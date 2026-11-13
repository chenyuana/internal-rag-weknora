"""API regression against the isolated upgrade candidate only."""
import json
import base64
import os
import pathlib
import subprocess
import sys
import time
import urllib.request
import urllib.error

os.environ['DOCKER_API_VERSION'] = '1.43'
backup = pathlib.Path(pathlib.Path('D:/weknora-evaluation/notes/upgrade-083-backup-path.txt').read_text().strip())
report = {'base': 'http://127.0.0.1:18083', 'checks': []}
def sql(query):
    return subprocess.check_output(['docker','exec','weknora083-db','psql','-U','weknora','-d','restore083_verified','-Atc',query], text=True).strip()
key = sql("SELECT api_key FROM tenant_api_keys WHERE tenant_id=10000 AND revoked_at IS NULL ORDER BY full_access DESC,id LIMIT 1")
if key.startswith('enc:v1:'):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    env = dict(line.split('=',1) for line in (backup/'validation.env').read_text().splitlines() if '=' in line)
    raw = base64.b64decode(key[len('enc:v1:'):])
    key = AESGCM(env['SYSTEM_AES_KEY'].encode()).decrypt(raw[:12],raw[12:],None).decode()
assert key
def request(method, path, body=None, stream=False):
    req = urllib.request.Request(report['base'] + path,
        data=None if body is None else json.dumps(body,ensure_ascii=False).encode(),
        headers={'X-API-Key':key,'Content-Type':'application/json'},method=method)
    with urllib.request.urlopen(req, timeout=180) as response:
        raw = response.read().decode()
        return raw if stream else json.loads(raw)
def save():
    (backup/'validation-api-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')

if len(sys.argv)>1 and sys.argv[1]=='resume':
    report=json.loads((backup/'validation-api-report.json').read_text(encoding='utf-8'))
    session=next(c['session'] for c in report['checks'] if c['name']=='streaming QA')
    history=request('GET','/api/v1/messages/'+session+'/load')
    report['checks'].append({'name':'history','response':history})
    source=request('GET','/api/v1/knowledge-bases/6a114c40-1790-470f-b3e7-129227291699')['data']
    body={f:source[f] for f in ['type','embedding_model_id','summary_model_id','indexing_strategy','storage_provider_config'] if f in source}
    body.update(name='0.8.3隔离自动Wiki验收',is_temporary=False,wiki_config={'extraction_granularity':'focused','max_pages_per_ingest':1,'content_instructions':'使用中文，保留原文引用。'})
    testkb=request('POST','/api/v1/knowledge-bases',body)['data']['id']
    payload={'source_document_id':'upgrade083-api-verification','source_name':'升级验收流程','normalized_text_sha256':'upgrade083-fixture-v1',
        'chunks':[{'chunk_id':'upgrade083-1','text':'升级前应先备份数据库、角色、文件和当前运行镜像。先验证备份能够恢复到独立数据卷，再升级数据库扩展，最后切换应用。不得对新扩展数据卷直接换回旧数据库镜像。'},
                  {'chunk_id':'upgrade083-2','text':'升级验收应检查关键词检索、向量检索、图片问答和引用原文。接入台导入已经清洗的切片后自动生成Wiki，不应重新清洗或重新切分原始证据。重复导入相同内容应保持幂等。'}]}
    imported=request('POST','/api/v1/knowledge-bases/'+testkb+'/knowledge/internal-rag',payload)
    assert imported['data'].get('wiki_status')=='queued',imported
    report['checks'].append({'name':'automatic Wiki queued','kb':testkb,'response':imported})
    save()
    kn=imported['data']['knowledge_id']
    for _ in range(90):
        state=json.loads(sql("SELECT json_build_object('status',parse_status,'pending',pending_subtasks_count,'error',error_message) FROM knowledges WHERE id='"+kn+"'"))
        if state['status']=='completed' and state['pending']==0: break
        if state['status']=='failed': raise RuntimeError('Wiki generation failed: '+str(state))
        time.sleep(5)
    assert state['status']=='completed' and state['pending']==0,state
    repeat=request('POST','/api/v1/knowledge-bases/'+testkb+'/knowledge/internal-rag',payload)
    assert repeat['data']['action']=='skipped',repeat
    report['checks'].append({'name':'automatic Wiki completed and idempotent','state':state,'repeat':repeat})
    save()
    print('History, automatic Wiki completion and duplicate-import idempotency passed in isolated environment.')
    sys.exit(0)

health = request('GET','/health')
report['checks'].append({'name':'health','result':health})
kbs = request('GET','/api/v1/knowledge-bases')
data = kbs['data']
if isinstance(data,dict): data = data.get('data',data.get('knowledge_bases',[]))
assert data
report['checks'].append({'name':'list knowledge bases','count':len(data)})
kb = next((x for x in data if x['id']=='b35a43d9-8477-4f7a-8edb-7311222ff61c'),data[0])
for query in ['AC 20-173 平板与显示器的分类，以及申请人的责任','平板与显示器的分类，以及谁负责说明已安装组件']:
    res = request('POST','/api/v1/knowledge-search',{'query':query,'knowledge_base_ids':[kb['id']],'match_count':20})
    report['checks'].append({'name':'knowledge search','query':query,'response':res})
    save()
models = request('GET','/api/v1/models')['data']
if isinstance(models,dict): models=models.get('models',models.get('data',[]))
model = next((x for x in models if x.get('id')==kb.get('summary_model_id')),None)
if model is None: model=next(x for x in models if x.get('type')=='KnowledgeQA')
session = request('POST','/api/v1/sessions',{'title':'0.8.3隔离验收'})['data']['id']
answer = request('POST','/api/v1/knowledge-chat/'+session,{
    'query':'AC 20-173 中平板与显示器如何分类，谁负责说明已安装组件？请引用原文。',
    'knowledge_base_ids':[kb['id']],'summary_model_id':model['id'],
    'agent_enabled':False,'web_search_enabled':False,'disable_title':True},stream=True)
report['checks'].append({'name':'streaming QA','session':session,'stream':answer})
save()
history = request('GET','/api/v1/messages/'+session+'/load')
report['checks'].append({'name':'history','response':history})
save()
print(json.dumps({'checks':len(report['checks']),'report':str(backup/'validation-api-report.json')},ensure_ascii=False))
