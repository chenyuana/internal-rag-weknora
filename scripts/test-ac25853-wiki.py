import json,subprocess,urllib.request,base64
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
out=Path('testdata/ac25853-wiki-20261028');out.mkdir(parents=True,exist_ok=True)
def sql(q):return subprocess.check_output(['docker','exec','WeKnora-postgres','psql','-U','weknora','-d','WeKnora','-Atc',q],text=True,encoding='utf8').strip()
key=sql("SELECT api_key FROM tenant_api_keys WHERE tenant_id=10000 AND revoked_at IS NULL ORDER BY full_access DESC,id LIMIT 1")
if key.startswith('enc:v1:'):
 env=dict(x.split('=',1) for x in json.loads(subprocess.check_output(['docker','inspect','WeKnora-app'],text=True))[0]['Config']['Env']); raw=base64.b64decode(key[7:]); key=AESGCM(env['SYSTEM_AES_KEY'].encode()).decrypt(raw[:12],raw[12:],None).decode()
def req(method,path,body=None):
 r=urllib.request.Request('http://localhost:18080/api/v1'+path,data=None if body is None else json.dumps(body,ensure_ascii=False).encode(),headers={'X-API-Key':key,'Content-Type':'application/json'},method=method)
 with urllib.request.urlopen(r,timeout=300) as response:return json.load(response)
def save(name,obj):(out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
source=req('GET','/knowledge-bases/acdf013d-971b-42c3-b6ca-cf09157c9215')['data']
body={f:source[f] for f in ['type','embedding_model_id','summary_model_id','indexing_strategy','storage_provider_config'] if f in source}; body.update(name='测试 AC25.853-1 日期 Wiki 对照 20261028',is_temporary=False)
body['indexing_strategy']=dict(body['indexing_strategy'],wiki_enabled=False,graph_enabled=False)
created=req('POST','/knowledge-bases',body);save('created-kb.json',created);kb=created['data']['id']
rows=json.loads(sql("SELECT json_agg(t ORDER BY chunk_index) FROM (SELECT id,chunk_index,content,metadata FROM chunks WHERE knowledge_id='78138020-8044-4d74-9e02-be579e00fb41' AND deleted_at IS NULL AND chunk_type='text') t"));save('original-chunks.json',rows)
chunks=[dict(chunk_id=r['id'],parent_chunk_id=(r['metadata'] or {}).get('external_parent_chunk_id',''),text=r['content'],page_start=int((r['metadata'] or {}).get('page_start',0)),page_end=int((r['metadata'] or {}).get('page_end',0))) for r in rows]
payload=dict(source_document_id='ac25853-wiki-controlled-test',source_name='AC_25.853-1.pdf',normalized_text_sha256='controlled-source-v1',chunks=chunks)
result=req('POST',f'/knowledge-bases/{kb}/knowledge/internal-rag',payload);save('import.json',result)
save('state.json',{'kb':kb,'knowledge':result['data']['knowledge_id'],'source_kb':source['id'],'summary_model':source['summary_model_id']})
print('Created isolated KB',kb,'chunks',len(rows),flush=True)
