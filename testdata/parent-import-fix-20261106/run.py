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
out=Path('testdata/parent-import-fix-20261106')
source=req('GET','/knowledge-bases/21271cb1-9067-4b8b-a9f7-2d582dc1422f')['data']
body={f:source[f] for f in ['type','embedding_model_id','summary_model_id','indexing_strategy','storage_provider_config','chunking_config'] if f in source}
body.update(name='父块修复导入对照-20261106',is_temporary=True)
body['indexing_strategy']=dict(body.get('indexing_strategy') or {},wiki_enabled=False,graph_enabled=False)
body['chunking_config']=dict(body.get('chunking_config') or {},parent_chunk_size=4096)
kb=json.loads((out/'kb.json').read_text())['id'] if (out/'kb.json').exists() else req('POST','/knowledge-bases',body)['data']['id'];save('kb.json',{'id':kb})
raw=json.loads(sql("SELECT json_agg(t ORDER BY chunk_index) FROM (SELECT chunk_index,content,metadata FROM chunks WHERE knowledge_id='33a46c79-c238-4957-aed1-27c48dbd0313' AND chunk_type='text' AND deleted_at IS NULL ORDER BY chunk_index) t"))
chunks=[]
for i,r in enumerate(raw):
 c=dict(r.get('metadata') or {});c.update(chunk_id=c.get('external_chunk_id') or str(i),parent_chunk_id=c.get('external_parent_chunk_id',''),text=r['content']);chunks.append(c)
payload={'source_document_id':'parent-import-fix-fixture','source_name':'直升机空气动力学-父块修复对照','normalized_text_sha256':'same-text-parent-fixture-v1','chunks':chunks}
save('payload.json',payload)
res=req('POST','/knowledge-bases/'+kb+'/knowledge/internal-rag',payload);save('import.json',res);kid=res['data']['knowledge_id'];print('Imported',kid,flush=True)
stored=json.loads(sql("SELECT json_agg(t ORDER BY chunk_index) FROM (SELECT chunk_index,content,metadata,parent_chunk_id FROM chunks WHERE knowledge_id='"+kid+"' AND chunk_type='text' AND deleted_at IS NULL ORDER BY chunk_index) t"))
assert len(stored)==len(chunks)
for a,b in zip(chunks,stored):
 assert a['text']==b['content']
 assert a['chunk_id']==b['metadata']['external_chunk_id']
 assert a.get('page_start',0)==b['metadata'].get('page_start',0)
parents=json.loads(sql("SELECT json_agg(t) FROM (SELECT id,content FROM chunks WHERE knowledge_id='"+kid+"' AND chunk_type='parent_text' AND deleted_at IS NULL) t"))
assert max(map(lambda r:len(r['content']),parents))<=4096
save('parent-stats.json',{'count':len(parents),'max_chars':max(len(p['content']) for p in parents),'child_count':len(stored),'text_and_metadata_preserved':True})
print('Max parent',max(len(p['content']) for p in parents),'children',len(stored),flush=True)
repeat=req('POST','/knowledge-bases/'+kb+'/knowledge/internal-rag',payload);save('repeat.json',repeat);assert repeat['data']['action']=='skipped'
# The following mutation touches only our new test document: simulate pre-fix metadata.
sql("UPDATE knowledges SET metadata=metadata::jsonb-'internal_rag_parent_version' WHERE id='"+kid+"'")
migrate=req('POST','/knowledge-bases/'+kb+'/knowledge/internal-rag',payload);save('migration.json',migrate);assert migrate['data']['action']=='updated'
count=int(sql("SELECT count(*) FROM chunks WHERE knowledge_id='"+kid+"' AND chunk_type='text' AND deleted_at IS NULL"));assert count==len(chunks)
print('Idempotency and legacy version reimport passed',flush=True)
questions=['前飞时旋翼尾迹在悬停、小速度平飞、大速度平飞下分别近似什么形状？','经典滑流理论有哪些基本假设？','旋翼实度是什么意思？']
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
