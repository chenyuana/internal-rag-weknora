import json,os,subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
# Reuse credential loader only; do not execute its KB creation section.
exec(Path('scripts/test-ac25853-wiki.py').read_text(encoding='utf-8-sig').split("source=req(")[0].replace('http://localhost:18080', os.environ.get('EXACT_DATE_API_BASE', 'http://localhost:18080')))
out=Path(os.environ.get('EXACT_DATE_OUTPUT', 'testdata/exact-date-deploy-20261028'));out.mkdir(exist_ok=True)
import time,urllib.error
items=[json.loads(l) for l in Path('tmp/wk50.jsonl').read_text(encoding='utf8').splitlines()]
selected={'001','002','003','007','010','011','014','017','018','019','024','026','027','029','031','039','040','045','048','049','050'}
questions=[(r['num'],r.get('query_sent') or r['question']) for r in items if r['num'] in selected]
questions += [('date853','AC 25.853-1 的签发日期？'),('date853-repeat','AC 25.853-1 的签发日期？'),('014-repeat',next(r.get('query_sent') or r['question'] for r in items if r['num']=='014'))]
def run(item):
 num,q=item;t=time.monotonic()
 try:
  sid=req('POST','/sessions',{'title':'exact-date-deploy-'+num})['data']['id']
  body={'query':q,'agent_enabled':False,'knowledge_base_ids':['acdf013d-971b-42c3-b6ca-cf09157c9215'],'agent_id':'builtin-quick-answer','web_search_enabled':False,'summary_model_id':'e34d26a0-5882-4b14-bd73-0a11668bcfc6','mentioned_items':[{'id':'acdf013d-971b-42c3-b6ca-cf09157c9215','name':'适航知识库','type':'kb','kb_type':'document'}],'channel':'web'}
  body['agent_id']=os.environ.get('EXACT_DATE_AGENT_ID',body['agent_id'])
  r=urllib.request.Request(os.environ.get('EXACT_DATE_API_BASE', 'http://localhost:18080')+'/api/v1/knowledge-chat/'+sid,data=json.dumps(body,ensure_ascii=False).encode(),headers={'X-API-Key':key,'Content-Type':'application/json'},method='POST');events=[]
  with urllib.request.urlopen(r,timeout=240) as response:
   for raw in response:
    line=raw.decode('utf8').strip()
    if line.startswith('data:'):
     try:events.append(json.loads(line[5:].strip()))
     except ValueError:pass
  answer=''.join(e.get('content','') for e in events if e.get('response_type')=='answer' and not e.get('done'))
  refs=[r for e in events if e.get('response_type')=='references' for r in e.get('knowledge_references',[])]
  record={'num':num,'query':q,'session':sid,'answer':answer,'references':refs,'events':events,'seconds':round(time.monotonic()-t,2)}
 except Exception as e:record={'num':num,'query':q,'error':str(e),'seconds':round(time.monotonic()-t,2)}
 (out/(num+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
 print(num,'answer_chars',len(record.get('answer','')),'error',record.get('error',''),flush=True)
 return record
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=2) as pool:
  for f in as_completed([pool.submit(run,x) for x in questions]):f.result()
