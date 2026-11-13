import json,time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

loader=Path('scripts/test-ac25853-wiki.py').read_text(encoding='utf-8-sig').split("source=req(")[0]
exec(loader)
kb='4f216fce-1f63-4392-8e90-85ac1b6c7e8a'
out=Path('testdata/zongti2-20261109/bilingual-pilot')
rows=[json.loads(s) for s in (out.parent/'questions.jsonl').read_text(encoding='utf8').splitlines()]
english=(out/'queries-en.txt').read_text(encoding='utf8').splitlines()
assert len(rows)==len(english)==32

def retrieve(query):
    start=time.monotonic()
    for attempt in range(2):
        try:
            result=req('POST',f'/knowledge-bases/{kb}/hybrid-search',{'query_text':query,'match_count':20,'vector_threshold':0,'keyword_threshold':0})
            return [{k:r.get(k) for k in ('id','knowledge_title','score')} for r in result['data']], round(time.monotonic()-start,3)
        except Exception:
            if attempt: raise
            time.sleep(1)

def assess(row, queries, calls):
    zh,en=calls
    scores=defaultdict(float)
    for results,_ in calls:
        for rank,item in enumerate(results,1):
            scores[item['id']]+=1/(60+rank)
    z=[r['id'] for r in zh[0]]
    e=[r['id'] for r in en[0]]
    fused=sorted(scores,key=scores.get,reverse=True)
    balanced=list(dict.fromkeys([item for pair in zip(z[:3],e[:3]) for item in pair]+fused))
    expected=[item['chunk_id'] for item in row['evidence']]
    rankings={'zh':z,'en':e,'rrf':fused,'balanced':balanced}
    return dict(id=row['id'],queries=queries,expected=expected,ranks={name:[rank.index(i)+1 if i in rank else None for i in expected] for name,rank in rankings.items()},seconds={'zh':zh[1],'en':en[1]},results={'zh':zh[0],'en':en[0]},fused_ids=fused,balanced_ids=balanced)

with ThreadPoolExecutor(max_workers=4) as pool, (out/'results.jsonl').open('w',encoding='utf8') as f:
    pending=[]
    for row,translation in zip(rows,english):
        queries=[row['question'],translation]
        pending.append((row,queries,[pool.submit(retrieve,q) for q in queries]))
    for row,queries,futures in pending:
        result=assess(row,queries,[future.result() for future in futures])
        f.write(json.dumps(result,ensure_ascii=False)+'\n')
        f.flush()
        print(result['id'],result['ranks'],flush=True)
