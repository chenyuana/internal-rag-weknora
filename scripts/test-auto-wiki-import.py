"""Exercise KB creation plus the ingestion desk's pre-cleaned-chunk API."""
import json
import subprocess
import urllib.request
from pathlib import Path

root = Path('backups/pre-auto-wiki-20261014')
key = subprocess.check_output(['docker', 'exec', 'WeKnora-postgres', 'psql', '-U', 'weknora', '-d', 'WeKnora', '-Atc', "SELECT api_key FROM tenant_api_keys WHERE tenant_id=10000 AND revoked_at IS NULL AND capabilities::text LIKE '%ingest%' ORDER BY created_at DESC LIMIT 1"], text=True).strip()

def request(method, path, body=None):
    req = urllib.request.Request('http://localhost:18080/api/v1' + path, data=None if body is None else json.dumps(body, ensure_ascii=False).encode(), headers={'X-API-Key': key, 'Content-Type': 'application/json'}, method=method)
    with urllib.request.urlopen(req, timeout=180) as response:
        return json.load(response)

kb = request('GET', '/knowledge-bases/6a114c40-1790-470f-b3e7-129227291699')['data']
(root / 'user-kb-before.json').write_text(json.dumps(kb, ensure_ascii=False, indent=2), encoding='utf-8')
body = {field: kb[field] for field in ['type', 'embedding_model_id', 'summary_model_id', 'indexing_strategy', 'storage_provider_config'] if field in kb}
body.update(name='自动Wiki导入验证（临时）', is_temporary=True, wiki_config={'extraction_granularity': 'focused', 'max_pages_per_ingest': 2, 'content_instructions': '使用中文，保留原文条件和原文引用。'})
created = request('POST', '/knowledge-bases', body)
test_kb = created['data']['id']
(root / 'auto-wiki-created-kb.json').write_text(json.dumps(created, ensure_ascii=False, indent=2), encoding='utf-8')
chunks = json.loads((root / 'target-chunks.json').read_bytes())
selected = [chunk for chunk in chunks if chunk['chunk_type'] == 'text' and len(chunk['content']) > 700][:3]
assert selected
payload = {'source_document_id': 'auto-wiki-import-verification-20261014', 'source_name': '已有清洗chunk自动Wiki验证', 'normalized_text_sha256': 'auto-wiki-verification-20261014', 'chunks': [{'chunk_id': c['id'], 'text': c['content'], 'page_start': (c.get('metadata') or {}).get('page_start', 0)} for c in selected]}
(root / 'auto-wiki-import-request.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
result = request('POST', '/knowledge-bases/' + test_kb + '/knowledge/internal-rag', payload)
(root / 'auto-wiki-import-response.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
assert result['data']['wiki_status'] == 'queued', result
print(json.dumps({'kb': test_kb, 'import': result}, ensure_ascii=False), flush=True)
# Same source and hash must remain idempotent after generation has completed.
