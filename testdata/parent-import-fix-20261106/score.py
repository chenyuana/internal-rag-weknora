import json,subprocess,urllib.request,base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
key=subprocess.check_output(['docker','exec','WeKnora-postgres','psql','-U','weknora','-d','WeKnora','-Atc',"SELECT api_key FROM tenant_api_keys WHERE tenant_id=10000 AND revoked_at IS NULL ORDER BY full_access DESC,id LIMIT 1"],text=True).strip()
if key.startswith('enc:v1:'):
 env=dict(x.split('=',1) for x in json.loads(subprocess.check_output(['docker','inspect','WeKnora-app'],text=True))[0]['Config']['Env']); raw=base64.b64decode(key[7:]); key=AESGCM(env['SYSTEM_AES_KEY'].encode()).decrypt(raw[:12],raw[12:],None).decode()
def req(path,body=None):
 r=urllib.request.Request('http://localhost:18085/api/v1'+path,data=None if body is None else json.dumps(body).encode(),headers={'X-API-Key':key,'Content-Type':'application/json'})
 with urllib.request.urlopen(r,timeout=180) as res:return json.load(res)

from pathlib import Path
r=json.loads(Path('testdata/parent-import-fix-20261106/question-0.json').read_text(encoding='utf-8'))
result=req('/evaluation/ragas',{'model_id':'e34d26a0-5882-4b14-bd73-0a11668bcfc6','user_input':r['question'],'response':r['answer'],'retrieved_contexts':[x['content'] for x in r['references']]})
Path('testdata/parent-import-fix-20261106/ragas.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=True))
