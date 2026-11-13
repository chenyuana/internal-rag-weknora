import json,subprocess,urllib.request,base64
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
def sql(q):return subprocess.check_output(['docker','exec','WeKnora-postgres','psql','-U','weknora','-d','WeKnora','-Atc',q],text=True,encoding='utf8').strip()
key=sql("SELECT api_key FROM tenant_api_keys WHERE tenant_id=10000 AND revoked_at IS NULL ORDER BY full_access DESC,id LIMIT 1")
if key.startswith('enc:v1:'):
 env=dict(x.split('=',1) for x in json.loads(subprocess.check_output(['docker','inspect','WeKnora-app'],text=True))[0]['Config']['Env']); raw=base64.b64decode(key[7:]); key=AESGCM(env['SYSTEM_AES_KEY'].encode()).decrypt(raw[:12],raw[12:],None).decode()
def curl(path,body=None):
 r=urllib.request.Request('http://localhost:18085/api/v1'+path,data=None if body is None else json.dumps(body,ensure_ascii=False).encode(),headers={'X-API-Key':key,'Content-Type':'application/json'})
 with urllib.request.urlopen(r,timeout=300) as response:return response.read().decode('utf-8')

def req(method,path,body=None):return json.loads(curl(path,body))

def save(name,obj):(out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')

import time
out=Path('testdata/parent-import-fix-20261106/legacy-retrieval');out.mkdir(exist_ok=True)
kb='21271cb1-9067-4b8b-a9f7-2d582dc1422f'
body={'name':'适航原始文档父块回退验证'}
questions=['前飞时旋翼尾迹在悬停、小速度平飞、大速度平飞下分别近似什么形状？']
for i,q in enumerate(questions):
 sid=req('POST','/sessions',{'title':'父块修复测试-'+str(i)})['data']['id']
 data={'query':q,'agent_enabled':False,'knowledge_base_ids':[kb],'agent_id':'builtin-quick-answer','web_search_enabled':False,'summary_model_id':'e34d26a0-5882-4b14-bd73-0a11668bcfc6','mentioned_items':[{'id':kb,'name':body['name'],'type':'kb','kb_type':'document'}],'channel':'web'}
 events=[]
 for line in curl('/knowledge-chat/'+sid,data).splitlines():
  if line.startswith('data:'):
   try:events.append(json.loads(line[5:].strip()))
   except ValueError:pass

 refs=[r for e in events if e.get('response_type')=='references' for r in e.get('knowledge_references',[])]
 answer=''.join(e.get('content','') for e in events if e.get('response_type')=='answer' and not e.get('done'))
 result={'question':q,'answer':answer,'session':sid,'references':refs,'reference_chars':[len(r.get('content','')) for r in refs]};save('question-'+str(i)+'.json',result)
 print('Question',i,'answer chars',len(answer),'reference chars',result['reference_chars'],flush=True)
 assert refs and answer
 assert sum(result['reference_chars'])<60000
