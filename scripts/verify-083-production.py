import base64
import json
import os
import pathlib
import subprocess
import urllib.request
import urllib.error
os.environ['DOCKER_API_VERSION']='1.43'
root=pathlib.Path('D:/weknora-evaluation')
b=pathlib.Path((root/'notes/upgrade-083-cutover-path.txt').read_text().strip())
raw=subprocess.check_output(['docker','exec','WeKnora-postgres','psql','-U','weknora','-d','WeKnora','-Atc',"SELECT api_key FROM tenant_api_keys WHERE tenant_id=10000 AND revoked_at IS NULL ORDER BY full_access DESC,id LIMIT 1"],text=True).strip()
if raw.startswith('enc:v1:'):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    cfg=json.loads((b/'containers-before.json').read_text(encoding='utf-8'))
    env=dict(v.split('=',1) for v in next(c for c in cfg if c['Name']=='/WeKnora-app')['Config']['Env'])
    data=base64.b64decode(raw[len('enc:v1:'):])
    raw=AESGCM(env['SYSTEM_AES_KEY'].encode()).decrypt(data[:12],data[12:],None).decode()
def request(path,body=None,key=True):
    h={'Content-Type':'application/json'}
    if key:h['X-API-Key']=raw
    req=urllib.request.Request('http://127.0.0.1:18080'+path,headers=h,data=None if body is None else json.dumps(body).encode())
    with urllib.request.urlopen(req,timeout=180) as r:return r.status,r.read().decode()
checks=[]
for path in ['/','/health','/api/v1/knowledge-bases']:
    code,text=request(path)
    assert code==200
    checks.append({'path':path,'status':code})
code,text=request('/api/v1/knowledge-search',{'query':'AC 20-173 平板与显示器的分类及申请人责任','knowledge_base_ids':['b35a43d9-8477-4f7a-8edb-7311222ff61c'],'match_count':10})
assert code==200 and 'AC_20-173' in text
checks.append({'path':'/api/v1/knowledge-search','status':code,'named_document_recalled':True})
try:
    request('/api/v1/knowledge-bases',key=False)
    raise AssertionError('Unauthenticated knowledge access unexpectedly allowed')
except urllib.error.HTTPError as e:
    assert e.code in (401,403)
    checks.append({'name':'unauthenticated access denied','status':e.code})
try:
    code,text=request('/api/v1/system/info')
    checks.append({'name':'system info','status':code,'response':json.loads(text)})
except urllib.error.HTTPError as e:checks.append({'name':'system info restricted','status':e.code})
(b/'production-api-verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print('Production UI/health/authenticated retrieval and unauthenticated access checks passed.')
