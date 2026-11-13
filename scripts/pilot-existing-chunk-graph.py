"""Bounded graph pilot; credentials remain local and never enter output."""
import json
import subprocess
import urllib.request
from pathlib import Path

out = Path('backups/pre-chunk-enrichment-20261013')
kb_id = 'b35a43d9-8477-4f7a-8edb-7311222ff61c'
knowledge_id = '4272c6b1-0113-4625-80a2-7b04a9fb30b0'
key = subprocess.check_output(['docker', 'exec', 'WeKnora-postgres', 'psql', '-U', 'weknora', '-d', 'WeKnora', '-Atc', "SELECT api_key FROM tenant_api_keys WHERE tenant_id=10000 AND revoked_at IS NULL AND capabilities::text LIKE '%ingest%' ORDER BY created_at DESC LIMIT 1"], text=True).strip()

def request(method, suffix, body=None):
    req = urllib.request.Request('http://localhost:18080/api/v1/knowledge-bases/' + kb_id + suffix, data=None if body is None else json.dumps(body, ensure_ascii=False).encode(), headers={'X-API-Key': key, 'Content-Type': 'application/json'}, method=method)
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.load(response)

kb = request('GET', '')['data']
(out / 'kb-before-graph.json').write_text(json.dumps(kb, ensure_ascii=False, indent=2), encoding='utf-8')
strategy = dict(kb['indexing_strategy'], graph_enabled=True)
extract = {'enabled': True, 'text': 'AC 20-47: A colored band continuously outlines the emergency exit.', 'tags': ['适用于', '组成', '连接', '负责', '分类为', '引用', '限制', '标识'], 'nodes': [{'name': '应急出口 (emergency exit)'}, {'name': '彩色带 (colored band)'}], 'relations': [{'node1': '彩色带 (colored band)', 'node2': '应急出口 (emergency exit)', 'type': '标识'}], 'custom_instructions': '仅抽取原文明确支持的实体和关系，使用中英文实体名，保留适用条件和例外。区分硬件、安装接口与责任主体；不得根据常识补全关系。'}
result = request('PUT', '', {'name': kb['name'], 'config': {'indexing_strategy': strategy, 'extract_config': extract}})
(out / 'kb-graph-config.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
for dry in (True, False):
    result = request('POST', '/knowledge/enrich', {'knowledge_ids': [knowledge_id], 'wiki': False, 'graph': True, 'dry_run': dry})
    (out / ('graph-dry-run.json' if dry else 'graph-queued.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False), flush=True)
