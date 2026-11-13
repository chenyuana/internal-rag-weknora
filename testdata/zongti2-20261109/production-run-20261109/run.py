"""Run the 总体2 test set through the deployed production pipeline.

Usage:
  python run.py --ids ZT2-011          # single question smoke
  python run.py                        # all 32 questions
Options:
  --cross-language on|off  (default on)
  --workers N              (default 3)
"""
import argparse
import concurrent.futures
import json
import time
import urllib.request
from pathlib import Path

workspace = Path('D:/weknora-evaluation')
out = workspace / 'testdata/zongti2-20261109/production-run-20261109'
out.mkdir(parents=True, exist_ok=True)

loader = (workspace / 'scripts/test-ac25853-wiki.py').read_text(encoding='utf-8-sig').split('source=req(')[0]
exec(loader)  # noqa: F821  -> key, req, sql
out = workspace / 'testdata/zongti2-20261109/production-run-20261109'
out.mkdir(parents=True, exist_ok=True)

base = 'http://127.0.0.1:18080'
kb = '4f216fce-1f63-4392-8e90-85ac1b6c7e8a'
model = 'e34d26a0-5882-4b14-bd73-0a11668bcfc6'


def ask(fixture, cross_language):
    sid = req('POST', '/sessions', {'title': f"总体2回归 {fixture['id']}"})['data']['id']
    body = {
        'query': fixture['question'],
        'agent_enabled': False,
        'agent_id': 'builtin-quick-answer',
        'knowledge_base_ids': [kb],
        'summary_model_id': model,
        'web_search_enabled': False,
        'mentioned_items': [{'id': kb, 'name': '总体2', 'type': 'kb', 'kb_type': 'document'}],
        'channel': 'web',
    }
    if cross_language:
        body['cross_language_search'] = True
    request = urllib.request.Request(
        base + '/api/v1/knowledge-chat/' + sid,
        data=json.dumps(body, ensure_ascii=False).encode(),
        method='POST',
        headers={'X-API-Key': key, 'Content-Type': 'application/json'},
    )
    started = time.time()
    events = []
    with urllib.request.urlopen(request, timeout=300) as response:
        for raw in response:
            line = raw.decode('utf8').strip()
            if line.startswith('data:'):
                try:
                    events.append(json.loads(line[5:]))
                except ValueError:
                    pass
    elapsed = round(time.time() - started, 2)
    answer = ''.join(e.get('content', '') for e in events
                     if e.get('response_type') == 'answer' and not e.get('done'))
    refs = [r for e in events if e.get('response_type') == 'references'
            for r in e.get('knowledge_references', [])]
    gold = [e['chunk_id'] for e in fixture['evidence']]
    ref_ids = {r.get('id') for r in refs}
    hit = [g for g in gold if g in ref_ids]
    return {
        'id': fixture['id'],
        'question': fixture['question'],
        'answerable': fixture['answerable'],
        'required_points': fixture['required_points'],
        'gold_chunks': gold,
        'gold_docs': [e['document'] for e in fixture['evidence']],
        'answer': answer,
        'references': [{'id': r.get('id'), 'doc': r.get('knowledge_title') or r.get('knowledge_filename') or r.get('title')} for r in refs],
        'reference_count': len(refs),
        'gold_hit': hit,
        'all_gold_hit': len(hit) == len(gold),
        'latency_s': elapsed,
        'error': None,
    }


def safe_ask(fixture, cross_language):
    try:
        return ask(fixture, cross_language)
    except Exception as exc:  # noqa: BLE001
        return {'id': fixture['id'], 'question': fixture['question'],
                'answerable': fixture['answerable'], 'answer': '', 'references': [],
                'reference_count': 0, 'gold_hit': [], 'all_gold_hit': False,
                'latency_s': None, 'error': f'{type(exc).__name__}: {exc}'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', nargs='*')
    ap.add_argument('--cross-language', choices=['on', 'off'], default='on')
    ap.add_argument('--workers', type=int, default=3)
    args = ap.parse_args()

    fixtures = [json.loads(line) for line in
                (workspace / 'testdata/zongti2-20261109/questions.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    if args.ids:
        wanted = set(args.ids)
        fixtures = [f for f in fixtures if f['id'] in wanted]
    fixtures.sort(key=lambda f: f['id'])

    suffix = 'single' if args.ids else 'all'
    result_path = out / f'results-{args.cross_language}-{suffix}.jsonl'
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(safe_ask, f, args.cross_language == 'on'): f for f in fixtures}
        for future in concurrent.futures.as_completed(futures):
            r = future.result()
            results.append(r)
            print(f"{r['id']} refs={r['reference_count']} gold={len(r['gold_hit'])} "
                  f"lat={r['latency_s']} err={r['error']}", flush=True)
    results.sort(key=lambda r: r['id'])
    with result_path.open('w', encoding='utf-8') as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('wrote', result_path, 'rows', len(results), flush=True)


if __name__ == '__main__':
    main()
