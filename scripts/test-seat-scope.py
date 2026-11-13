"""Controlled quick-answer scope tests; writes test sessions, never edits documents."""
import concurrent.futures
import json
import os
from pathlib import Path
import runpy

phase = os.environ.get('SEAT_SCOPE_PHASE', 'baseline')
root = Path('testdata/seat-scope-20261029') / phase
root.mkdir(parents=True, exist_ok=True)
os.environ['EXACT_DATE_OUTPUT'] = str(root)
suite = runpy.run_path('scripts/verify-exact-date-deployment.py')
questions = [
    ('original', '一套旅客座椅要分别通过哪两类彼此独立的适航试验？各自的判据与试验介质是什么？'),
    ('explicit', '针对运输类飞机旅客座椅的应急着陆合规，比较 §25.561 静强度与 §25.562 动态要求：各自的合格判据、关键数值及加载手段或人体模型是什么？为什么不能互相替代？'),
    ('fire', '仅依据运输类飞机资料，旅客座椅软垫油燃烧器可燃性试验的失重和烧损长度合格判据，以及试验燃料是什么？不要展开动态试验或旋翼机要求。'),
]
if os.environ.get('SEAT_SCOPE_REGRESSION') == 'true':
    questions += [('date', 'AC 25.853-1 的签发日期？')]

def run(item):
    record = suite['run'](item)
    (root / (item[0] + '.md')).write_text(record.get('answer', record.get('error', '')), encoding='utf8')
    refs = record.get('references', [])
    print(json.dumps({'case': item[0], 'seconds': record['seconds'], 'sources': [
        {'title': r.get('knowledge_title', r.get('title', '')), 'chars': len(r.get('content', ''))}
        for r in refs]}, ensure_ascii=False), flush=True)

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    list(pool.map(run, questions))
