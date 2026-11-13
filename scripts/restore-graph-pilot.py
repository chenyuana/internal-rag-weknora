"""Restore the proven Wiki-only runtime without restoring the entire database."""
import json
import subprocess
import urllib.request
from pathlib import Path

root = Path('backups/pre-chunk-enrichment-20261013')
kb = json.loads((root / 'kb-before-graph.json').read_bytes())
key = subprocess.check_output(['docker', 'exec', 'WeKnora-postgres', 'psql', '-U', 'weknora', '-d', 'WeKnora', '-Atc', "SELECT api_key FROM tenant_api_keys WHERE tenant_id=10000 AND revoked_at IS NULL AND capabilities::text LIKE '%ingest%' ORDER BY created_at DESC LIMIT 1"], text=True).strip()
req = urllib.request.Request('http://localhost:18080/api/v1/knowledge-bases/' + kb['id'], data=json.dumps({'name': kb['name'], 'config': {'indexing_strategy': kb['indexing_strategy']}}).encode(), headers={'X-API-Key': key, 'Content-Type': 'application/json'}, method='PUT')
with urllib.request.urlopen(req, timeout=60) as response:
    result = json.load(response)
assert result['data']['indexing_strategy']['graph_enabled'] is False
assert result['data']['extract_config']['enabled'] is False
(root / 'kb-restored-after-graph.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
config_path = root / 'compose.enrichment.json'
config = json.loads(config_path.read_bytes())
original = json.loads((root / 'app-inspect.json').read_bytes())
if isinstance(original, list):
    original = original[0]
env = dict(item.split('=', 1) for item in original['Config']['Env'])
for name in ('NEO4J_ENABLE', 'NEO4J_URI', 'NEO4J_USERNAME', 'NEO4J_PASSWORD'):
    config['services']['app']['environment'][name] = env.get(name, '').replace('$', '$$')
config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
print('Restored KB graph=false and original graph runtime environment; Wiki remains enabled.')
