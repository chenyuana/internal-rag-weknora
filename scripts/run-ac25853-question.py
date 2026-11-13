import sys
exec(open('scripts/test-ac25853-wiki.py',encoding='utf-8-sig').read().split("source=req(")[0])
state=json.loads((out/'state.json').read_text(encoding='utf8'))
phase=sys.argv[1]
question='AC 25.853-1 的签发日期？'
kb=state['source_kb'] if phase=='production' else state['kb']
session=req('POST','/sessions',{'title':f'AC25.853-1 Wiki 日期对照 {phase}'})['data']['id']
body={'query':question,'agent_enabled':phase=='wiki-agent','knowledge_base_ids':[kb],'agent_id':'builtin-wiki-researcher' if phase=='wiki-agent' else 'builtin-quick-answer','web_search_enabled':False,'summary_model_id':state['summary_model'],'mentioned_items':[{'id':kb,'name':'AC25.853日期测试','type':'kb','kb_type':'document'}],'channel':'web'}
r=urllib.request.Request('http://localhost:18080/api/v1/knowledge-chat/'+session,data=json.dumps(body,ensure_ascii=False).encode(),headers={'X-API-Key':key,'Content-Type':'application/json'},method='POST')
events=[]
with urllib.request.urlopen(r,timeout=300) as response:
 for raw in response:
  line=raw.decode('utf8').strip()
  if line.startswith('data:'):
   try:events.append(json.loads(line[5:].strip()))
   except ValueError:pass
save(phase+'-events.json',{'session':session,'request':body,'events':events})
print(phase,'session',session,'events',len(events),flush=True)
print(json.dumps(events,ensure_ascii=True)[-6500:])
