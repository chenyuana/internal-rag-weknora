"""Same four rewritten questions with cross-language search OFF (A/B)."""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / 'production-run-20261109'))
import run  # noqa: E402

ids = {'ZT2-024', 'ZT2-025', 'ZT2H-011', 'ZT2H-012'}
fixtures = []
for name in ('v1_pagefree.jsonl', 'hard_pagefree.jsonl'):
    for line in (HERE / name).read_text(encoding='utf-8').splitlines():
        r = json.loads(line)
        if r['id'] in ids:
            fixtures.append(r)

with ThreadPoolExecutor(max_workers=2) as pool:
    results = list(pool.map(lambda f: run.safe_ask(f, False), fixtures))

for r in results:
    print(r['id'], 'gold', len(r['gold_hit']), '/', len(r['gold_chunks']), 'lat', r['latency_s'], 'err', r['error'], flush=True)

path = HERE / 'rewrite-run-results-off.jsonl'
with path.open('w', encoding='utf-8') as fh:
    for r in results:
        fh.write(json.dumps(r, ensure_ascii=False) + '\n')
print('wrote', path)
