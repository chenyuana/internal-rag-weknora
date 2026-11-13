import json,subprocess,urllib.request,base64
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
def sql(q):return subprocess.check_output(['docker','exec','WeKnora-postgres','psql','-U','weknora','-d','WeKnora','-Atc',q],text=True,encoding='utf8').strip()
key=sql("SELECT api_key FROM tenant_api_keys WHERE tenant_id=10000 AND revoked_at IS NULL ORDER BY full_access DESC,id LIMIT 1")
if key.startswith('enc:v1:'):
 env=dict(x.split('=',1) for x in json.loads(subprocess.check_output(['docker','inspect','WeKnora-app'],text=True))[0]['Config']['Env']); raw=base64.b64decode(key[7:]); key=AESGCM(env['SYSTEM_AES_KEY'].encode()).decrypt(raw[:12],raw[12:],None).decode()
def req(method,path,body=None):
 r=urllib.request.Request('http://localhost:18080/api/v1'+path,data=None if body is None else json.dumps(body,ensure_ascii=False).encode(),headers={'X-API-Key':key,'Content-Type':'application/json'},method=method)
 with urllib.request.urlopen(r,timeout=300) as response:return json.load(response)
def save(name,obj):(out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')

import requests,time
out=Path('testdata/native-parser-comparison-20261106/text-control');out.mkdir(exist_ok=True)
source=req('GET','/knowledge-bases/21271cb1-9067-4b8b-a9f7-2d582dc1422f')['data']
body={f:source[f] for f in ['type','embedding_model_id','summary_model_id','indexing_strategy','storage_provider_config','chunking_config'] if f in source}
body.update(name='原生切块正文对照-直升机空气动力学-20261106',is_temporary=True)
body['indexing_strategy']=dict(body.get('indexing_strategy') or {},wiki_enabled=False,graph_enabled=False)
# Pin documented native splitter sizes, enable parent-child expansion for a meaningful comparison.
body['chunking_config']=dict(body.get('chunking_config') or {},chunk_size=512,chunk_overlap=50,enable_parent_child=True,parent_chunk_size=4096,child_chunk_size=384,parser_engine_rules=[])
created=req('POST','/knowledge-bases',body);kb=created['data']['id'];save('created.json',created)
print('Created isolated KB',kb,'chunking',body['chunking_config'],flush=True)
file=Path('testdata/native-parser-comparison-20261106/same-extracted-text.md')
with file.open('rb') as f:
 r=requests.post('http://localhost:18080/api/v1/knowledge-bases/'+kb+'/knowledge/file',headers={'X-API-Key':key},files={'file':('helicopter-native-text.md',f,'text/markdown')},timeout=300)
r.raise_for_status();uploaded=r.json();save('uploaded.json',uploaded);kid=uploaded['data']['id'];print('Uploaded',kid,flush=True)
for i in range(180):
 record=req('GET','/knowledge/'+kid)['data'];state=record['parse_status'];print('Parse',state,flush=True)
 if state in ['completed','failed']:break
 time.sleep(10)
save('parsed.json',record)
assert state=='completed',record.get('error_message','Parsing incomplete')
stats=sql("SELECT json_agg(t) FROM (SELECT chunk_type,count(*) AS count,min(char_length(content)) AS min_chars,max(char_length(content)) AS max_chars,round(avg(char_length(content))) AS mean_chars FROM chunks WHERE knowledge_id='"+kid+"' AND deleted_at IS NULL GROUP BY chunk_type) t")
save('chunk-stats.json',json.loads(stats));print('Chunk stats',stats,flush=True)
session=req('POST','/sessions',{'title':'原生解析问答对照-20261106'})['data']['id']
q='前飞时旋翼尾迹在悬停、小速度平飞、大速度平飞下分别近似什么形状？'
request=urllib.request.Request('http://localhost:18080/api/v1/knowledge-chat/'+session,data=json.dumps({'query':q,'agent_enabled':False,'knowledge_base_ids':[kb],'agent_id':'builtin-quick-answer','web_search_enabled':False,'summary_model_id':'e34d26a0-5882-4b14-bd73-0a11668bcfc6','mentioned_items':[{'id':kb,'name':body['name'],'type':'kb','kb_type':'document'}],'channel':'web'},ensure_ascii=False).encode(),headers={'X-API-Key':key,'Content-Type':'application/json'})
events=[]
with urllib.request.urlopen(request,timeout=300) as response:
 for raw in response:
  line=raw.decode('utf-8').strip()
  if line.startswith('data:'):
   try:events.append(json.loads(line[5:].strip()))
   except ValueError:pass
save('events.json',events)
answer=''.join(e.get('content','') for e in events if e.get('response_type')=='answer' and not e.get('done'))
refs=[r for e in events if e.get('response_type')=='references' for r in e.get('knowledge_references',[])]
save('result.json',{'kb':kb,'knowledge':kid,'session':session,'answer':answer,'references':refs,'reference_chars':[len(r.get('content','')) for r in refs]})
print('Answer chars',len(answer),'Reference chars',[len(r.get('content','')) for r in refs],flush=True)
