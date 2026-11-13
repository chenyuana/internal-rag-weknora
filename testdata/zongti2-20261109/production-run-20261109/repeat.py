"""Repeat the weak questions a few times to measure retrieval stability."""
import json
import run

fx = {json.loads(l)['id']: json.loads(l)
      for l in (run.workspace / 'testdata/zongti2-20261109/questions.jsonl').read_text(encoding='utf-8').splitlines()}
ids = ['ZT2-010', 'ZT2-024', 'ZT2-025', 'ZT2-029']
out = []
for i in range(2):
    for qid in ids:
        r = run.safe_ask(fx[qid], True)
        out.append(r)
        print(i, qid, 'gold', len(r['gold_hit']), '/', len(fx[qid]['evidence']), 'lat', r['latency_s'], 'err', r['error'], flush=True)
path = run.out / 'results-repeat.jsonl'
with path.open('w', encoding='utf-8') as fh:
    for r in out:
        fh.write(json.dumps(r, ensure_ascii=False) + '\n')
print('wrote', path)
