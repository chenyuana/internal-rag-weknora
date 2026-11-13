"""Run the same EFB questions before/after enrichment; never print API keys."""
import argparse
import json
import subprocess
import urllib.request
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--phase', required=True)
parser.add_argument('--kb', default='b35a43d9-8477-4f7a-8edb-7311222ff61c')
parser.add_argument('--out', default='backups/pre-chunk-enrichment-20261013/evaluation')
args = parser.parse_args()
key_sql = "SELECT api_key FROM tenant_api_keys WHERE tenant_id=10000 AND revoked_at IS NULL AND capabilities::text LIKE '%chat%' ORDER BY created_at DESC LIMIT 1"
key = subprocess.check_output(['docker', 'exec', 'WeKnora-postgres', 'psql', '-U', 'weknora', '-d', 'WeKnora', '-Atc', key_sql], text=True).strip()
assert key, 'No chat API key available'
base = 'http://localhost:18080/api/v1'

def post(path, body):
    req = urllib.request.Request(base + path, json.dumps(body, ensure_ascii=False).encode(), headers={'Content-Type': 'application/json', 'X-API-Key': key}, method='POST')
    return urllib.request.urlopen(req, timeout=300)

questions = [
    '一台每天都留在驾驶舱的平板没有纳入型号设计，连接已安装电源和数据接口。另一显示器每天拆下但纳入型号设计。如何分类？谁负责说明哪些组件已安装？',
    '一台每天都留在驾驶舱的平板没有纳入型号设计，连接已安装电源和数据接口。另一显示器每天拆下但纳入型号设计。AC 20-173 如何分类？谁负责说明哪些组件已安装？',
]
out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)
for i, question in enumerate(questions, 1):
    with post('/sessions', {'title': f'现有chunk增强验证 {args.phase} Q{i}'}) as response:
        session_id = json.load(response)['data']['id']
    body = {'query': question, 'agent_enabled': False, 'knowledge_base_ids': [args.kb], 'agent_id': 'builtin-quick-answer', 'web_search_enabled': False, 'summary_model_id': 'e34d26a0-5882-4b14-bd73-0a11668bcfc6', 'mentioned_items': [{'id': args.kb, 'name': 'FAA-AC图片版', 'type': 'kb', 'kb_type': 'document'}], 'channel': 'web'}
    events = []
    with post('/knowledge-chat/' + session_id, body) as response:
        for raw in response:
            line = raw.decode('utf-8').strip()
            if line.startswith('data:'):
                try:
                    events.append(json.loads(line[5:].strip()))
                except json.JSONDecodeError:
                    pass
    answer = ''.join(str(e.get('content') or '') for e in events if e.get('response_type') in ('text', 'answer', 'content', 'message'))
    (out / f'{args.phase}-q{i}.json').write_text(json.dumps({'session_id': session_id, 'request': body, 'events': events}, ensure_ascii=False, indent=2), encoding='utf-8')
    (out / f'{args.phase}-q{i}.md').write_text(answer, encoding='utf-8')
    print(f'{args.phase} Q{i}: session={session_id}, answer_chars={len(answer)}', flush=True)
