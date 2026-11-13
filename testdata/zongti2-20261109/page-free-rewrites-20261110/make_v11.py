# -*- coding: utf-8 -*-
"""Produce page-free (章节版) revisions of both 总体2 sets.

Rewritten: ZT2-024, ZT2-025, ZT2H-011, ZT2H-012.
Alternative rewrites offered for ZT2-023 and ZT2H-010 (index entries keep pages as data).
"""
import json
from pathlib import Path

ROOT = Path('D:/weknora-evaluation/testdata/zongti2-20261109')
OUT = ROOT / 'page-free-rewrites-20261110'
OUT.mkdir(parents=True, exist_ok=True)

TOC = ('4052X_toc.pdf', 'e594c56a-96e1-497a-8af3-556f0bb14450')
HB = ('公开+第19册(直升机设计).pdf', '77f84b06-e93f-4ad6-9177-29a9e10ccca2')

REPLACE = {
    'ZT2-024': dict(
        question='按《Civil Jet Aircraft Design》的目录，起落架布局属于哪一章、哪一节？该节前后各是哪一节？',
        required_points=['第 3 章 Overall Configuration and Systems。',
                         '第 3.4 节 Landing Gear Layout。',
                         '前一节 3.3 System Considerations，后一节 3.5 Future Developments。'],
        evidence=[{'document': TOC[0], 'document_id': TOC[1], 'chunk_id': '857588ef-c50c-4684-aeb4-8de6327307bc',
                   'chunk_index': 0,
                   'quote': '3. Overall Configuration and Systems 29 3.1 Conventional Layouts 29 3.2 Novel Layouts 31 3.3 System Considerations 42 3.4 Landing Gear Layout 45 3.5 Future Developments 50 3.6 In Conclusion 52'}],
    ),
    'ZT2-025': dict(
        question='按《飞机设计手册》第 19 册的目录，直升机的纵向、横向、总距和航向操纵范围分别列在哪些小节？这四个小节共同属于哪一节？',
        required_points=['纵向 3.4.3.1、横向 3.4.3.2、总距 3.4.3.3、航向 3.4.3.4。',
                         '四项共同属于 3.4.3 操纵范围的确定（其上级为 3.4 配平特性）。'],
        evidence=[{'document': HB[0], 'document_id': HB[1], 'chunk_id': 'a30e1c69-178f-4504-a913-0c9818e81d5b',
                   'chunk_index': 8,
                   'quote': '3.4 配平特性……(188) 3.4.3 操纵范围的确定……(199) 3.4.3.1 纵向操纵……(200) 3.4.3.2 横向操纵……(200) 3.4.3.3 总距操纵……(200) 3.4.3.4 航向操纵……(201) 3.5 稳定性和操纵性……(201)'}],
    ),
    'ZT2H-011': dict(
        question='按目录，第 13 章 Parametric Studies 的前一章和后一章各是什么？本章自身包含哪两个小节？',
        required_points=['前一章为第 12 章 Aircraft Cost Estimations，后一章为第 14 章 Aircraft Type Specification。',
                         '本章两节：13.1 Introduction、13.2 Example。'],
        evidence=[{'document': TOC[0], 'document_id': TOC[1], 'chunk_id': '48c3fa26-d148-45cf-95ea-24a5f46bf38d',
                   'chunk_index': 2,
                   'quote': '12. Aircraft Cost Estimations 302 ... 13. Parametric Studies 326 13.1 Introduction 327 13.2 Example 329 14. Aircraft Type Specification 335'}],
    ),
    'ZT2H-012': dict(
        question='按目录，第 9 章的 9.10、9.11、9.12 分别是什么小节？三者的主题分别关于什么？',
        required_points=['9.10 Rules for Scaling an Engine（发动机缩放规则）。',
                         '9.11 Engine Price（发动机价格）。',
                         '9.12 Maintenance Costs（维护成本）。'],
        evidence=[{'document': TOC[0], 'document_id': TOC[1], 'chunk_id': '2df9edcf-4d22-44ee-953a-afdd3a895968',
                   'chunk_index': 1,
                   'quote': '9.9 Derivation of Pod Geometry 197 9.10 Rules for Scaling an Engine 201 9.11 Engine Price 201 9.12 Maintenance Costs 202 9.13 Engine Data 202'}],
    ),
}

# Optional all-page-free variants (index entries keep page numbers as their own data).
OPTIONAL = {
    'ZT2-023': dict(
        question='查书末索引：aileron sizing 与 baulked landing climb 两条索引项是否存在？各归在 A 段还是 B 段？相邻的操纵面尺寸条目还有哪些？',
        required_points=['两条都存在：aileron sizing 在 A 段，baulked landing climb 在 B 段。',
                         '相邻的操纵面尺寸条目有 tailplane sizing、fin/rudder sizing。'],
        evidence=[{'document': '4052X_indx.pdf', 'document_id': 'fde65e8a-2a7c-4b03-9bac-5b1824b38aa2',
                   'chunk_id': '02914eab-93cc-439b-aa85-cf72073c3240', 'chunk_index': 1,
                   'quote': 'A ... aileron sizing 122 ... B baggage allowance 142 baulked landing climb 273 biplane 37 block time 320'}],
    ),
    'ZT2H-010': dict(
        question='查书末索引，type record 这一条目下包含哪些子项？',
        required_points=['子项包括 aerodynamic and structural criteria、airframe description、general characteristics、general design requirements、illustrations、overview、passenger cabin layout、powerplant description、servicing and airport details、systems、weights and balance。'],
        evidence=[{'document': '4052X_indx.pdf', 'document_id': 'fde65e8a-2a7c-4b03-9bac-5b1824b38aa2',
                   'chunk_id': '662d50ee-739f-4c44-a9a6-86bdb7c84db9', 'chunk_index': 8,
                   'quote': 'type record aerodynamic and structural criteria 338 airframe description 339 general characteristics 337 general design requirements 337 illustrations 343 overview 336 passenger cabin layout 341 powerplant description 339 servicing and airport details 342 systems 340 341 weights and balance 338'}],
    ),
}


def revise(src, dst_stem, replace):
    rows = [json.loads(l) for l in src.read_text(encoding='utf-8').splitlines() if l.strip()]
    changed = 0
    for r in rows:
        if r['id'] in replace:
            r.update(replace[r['id']])
            r['revision'] = 'page-free-20261110'
            changed += 1
    with (OUT / f'{dst_stem}.jsonl').open('w', encoding='utf-8') as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + '\n')
    with (OUT / f'{dst_stem}_only.txt').open('w', encoding='utf-8') as fh:
        for r in rows:
            fh.write(r['question'] + '\n')
    md = [f'# {dst_stem} 参考答案（页码无关版）', '',
          f'共 {len(rows)} 题；标 `revision: page-free-20261110` 的为题面改写项。', '']
    for r in rows:
        md.append(f"## {r['id']} · {r['question']}")
        md.append('')
        md.append(f"**题型**　{r.get('category','')}　**可答**　{'是' if r['answerable'] else '否'}")
        md.append('')
        md.append('**参考答案要点**')
        md.append('')
        for p in r['required_points']:
            md.append(f'- {p}')
        md.append('')
        if r['evidence']:
            md.append('**原文证据**')
            md.append('')
            for e in r['evidence']:
                md.append(f"- **{e['document']}** · 切片序号 {e.get('chunk_index','')} · 切片 ID `{e['chunk_id']}`")
                md.append('')
                md.append(f"  > {e['quote']}")
                md.append('')
        md.append('')
    (OUT / f'{dst_stem}_with_answers.md').write_text('\n'.join(md), encoding='utf-8')
    return len(rows), changed


n1, c1 = revise(ROOT / 'questions.jsonl', 'v1_pagefree', REPLACE)
n2, c2 = revise(ROOT / 'hard-set-20261109/questions_hard.jsonl', 'hard_pagefree', REPLACE)

# optional variants
rows = [json.loads(l) for l in (ROOT / 'questions.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
for r in rows:
    if r['id'] in OPTIONAL:
        r.update(OPTIONAL[r['id']])
        r['revision'] = 'page-free-20261110-optional'
with (OUT / 'v1_pagefree_optional.jsonl').open('w', encoding='utf-8') as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + '\n')

rows = [json.loads(l) for l in (ROOT / 'hard-set-20261109/questions_hard.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
for r in rows:
    if r['id'] in OPTIONAL:
        r.update(OPTIONAL[r['id']])
        r['revision'] = 'page-free-20261110-optional'
with (OUT / 'hard_pagefree_optional.jsonl').open('w', encoding='utf-8') as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + '\n')

print('v1', n1, 'changed', c1, '| hard', n2, 'changed', c2)
