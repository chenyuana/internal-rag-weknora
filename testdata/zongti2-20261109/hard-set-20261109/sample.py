"""Run a sample of the hard set through the deployed production pipeline."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'production-run-20261109'))
import run  # noqa: E402

fx = {json.loads(l)['id']: json.loads(l)
      for l in (run.workspace / 'testdata/zongti2-20261109/hard-set-20261109/questions_hard.jsonl')
      .read_text(encoding='utf-8').splitlines()}
ids = ['ZT2H-001', 'ZT2H-002', 'ZT2H-010', 'ZT2H-013', 'ZT2H-019']
out = []
for qid in ids:
    r = run.safe_ask(fx[qid], True)
    out.append(r)
    print(qid, 'gold', len(r['gold_hit']), '/', len(fx[qid]['evidence']), 'lat', r['latency_s'], 'err', r['error'], flush=True)
path = run.out / 'hard-sample-results.jsonl'
with path.open('w', encoding='utf-8') as fh:
    for r in out:
        fh.write(json.dumps(r, ensure_ascii=False) + '\n')
print('wrote', path)
