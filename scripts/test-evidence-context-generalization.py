"""Read-only knowledge retrieval; creates isolated test conversations."""
import concurrent.futures
import json
import os
import runpy
from pathlib import Path

root = Path('testdata/evidence-context-20261029') / os.environ.get('EVIDENCE_PHASE','generalization')
root.mkdir(parents=True,exist_ok=True)
os.environ['EXACT_DATE_OUTPUT'] = str(root)
suite = runpy.run_path('scripts/verify-exact-date-deployment.py')
questions = [
 ('original-repeat-1','一套旅客座椅要分别通过哪两类彼此独立的适航试验？各自的判据与试验介质是什么？'),
 ('original-repeat-2','一套旅客座椅要分别通过哪两类彼此独立的适航试验？各自的判据与试验介质是什么？'),
 ('cross-part','比较 Part 23 与 Part 25 的座椅动态试验适用要求；分别列明依据，资料不足处明确说明，不要合并成统一要求。'),
 ('open','旅客座椅适航符合性涉及哪些方面？按检索证据概述，不预设只有两类。'),
 ('nonaviation','仅根据当前知识库，说明 PostgreSQL 的 MVCC 实现和 VACUUM 的作用；若没有对应资料请明确说明。'),
]
def run(item):
 record = suite['run'](item)
 (root/(item[0]+'.md')).write_text(record.get('answer',record.get('error','')),encoding='utf8')
 print(json.dumps({'case':item[0],'seconds':record['seconds'],'error':record.get('error'),'sources':len(record.get('references',[]))},ensure_ascii=False),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 list(pool.map(run,questions))
