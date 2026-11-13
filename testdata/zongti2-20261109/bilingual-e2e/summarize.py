import json
import statistics
from pathlib import Path

p = Path(__file__).resolve().parent

def read(name):
    rows = [json.loads(line) for line in (p / name).read_text(encoding="utf8").splitlines()]
    assert len(rows) == len({r["id"] for r in rows})
    return sorted(rows, key=lambda r: r["id"])

original = read("results.jsonl")
independent = read("independent-results.jsonl")
reverse = read("reverse-results.jsonl")
assert len(original) == 32 and len(independent) == 24 and len(reverse) == 4

methods = ("original", "expanded")
datasets = [
    ("总体2可答题", [r for r in original if r["answerable"]]),
    ("适航知识库中文原题", [r for r in independent if not r["id"].endswith("-EN")]),
    ("适航知识库英文对照", [r for r in independent if r["id"].endswith("-EN")]),
    ("总体2英文问中文资料", reverse),
]
report = ["# 跨语言查询扩展端到端 A/B", "",
          "共 60 个测试输入。总体2原集 32 题，适航知识库旧题 20 道及其中 4 道的英文对照，总体2另有 4 道英文问中文资料的对照。英文对照与原题共用参考答案，单独统计。适航知识库的切片 ID 由旧评测原文节选与当前索引正文匹配。", "",
          "A 用原问取混合检索前 20 条。B 用同一模型自动生成另一种语言的等义查询，合并两路候选并按切片 ID 去重。两组都用现有 BGE 重排器按原问重排，取前 5 条交给同一个 DeepSeek 模型，用相同提示词中文作答。未固定语言配额。用同一生成模型对 A/B 随机换序盲评。", "",
          "| 测试组 | 全部标准切片进候选 A → B | 全部标准切片进最终上下文 A → B | 答案满分 A → B | 答中要点 A → B | 有据答案 A → B |",
          "|---|---:|---:|---:|---:|---:|"]
def has_all(row, ids):
    return set(row["expected"]).issubset(ids)

def stats(rows, method):
    scores = [r["scores"][method] for r in rows]
    return (
        sum(has_all(r,r["variants"][method]["candidate_ids"]) for r in rows),
        sum(has_all(r,{c["id"] for c in r["variants"][method]["context"]}) for r in rows),
        sum(all(s["points"]) for s in scores),
        sum(sum(s["points"]) for s in scores),
        sum(s["grounded"] and any(s["points"]) for s in scores),
    )

for name, rows in datasets:
    a, b = (stats(rows,m) for m in methods)
    denominators = [len(rows)]*5
    denominators[3] = sum(len(r["required_points"]) for r in rows)
    report.append(f"| {name} | " + " | ".join(f"{x}/{n} → {y}/{n}" for x,y,n in zip(a,b,denominators)) + " |")

report += ["", "有据答案要求至少答中一个标准要点且模型判定关键结论有证据支持。标准切片命中使用严格 ID 匹配，可能漏计等价出处。", "",
           "## 逐题变化与耗时", ""]
for name, rows in datasets:
    score=lambda r,m: sum(r["scores"][m]["points"])
    improved=[r["id"] for r in rows if score(r,"expanded")>score(r,"original")]
    declined=[r["id"] for r in rows if score(r,"expanded")<score(r,"original")]
    errors=[sum(r["scores"][m]["major_error"] for r in rows) for m in methods]
    medians=[statistics.median(r["variants"][m]["pipeline_s"] for r in rows) for m in methods]
    report.append(f"- {name}。要点增加 {len(improved)} 道（{', '.join(improved) or '无'}），下降 {len(declined)} 道（{', '.join(declined) or '无'}）。关键错误 {errors[0]} → {errors[1]}。流水线中位耗时 {medians[0]:.2f} → {medians[1]:.2f} 秒。")

negatives=[r for r in original if not r["answerable"]]
safe=[sum(all(r["scores"][m]["points"]) and r["scores"][m]["grounded"] and not r["scores"][m]["major_error"] for r in negatives) for m in methods]
report += [f"- 信息不足题通过 {safe[0]}/{len(negatives)} → {safe[1]}/{len(negatives)}。通过要求说明缺失资料且无编造。",
           "", "人工抽查发现 FAA-WIKI-10 的自动判分方向有误。扩展组明确说明额外黑白条纹是醒目性建议且有对应切片，基线只指出没有证据证明其为强制要求，自动盲评却只给了基线该要点。FAA-WIKI-12 两组最终上下文均未包含地面气象雷达的关键证据，扩展组同时失去了基线提供的运输类防雷来源。表中保留原始盲评结果。",
           "", "耗时根据并行检索关键路径加重排与生成计算，含自动改写，不含判分。此为独立脚本中的并发实测估算，线上原生会话还有额外开销。", "",
           "测试调用现有检索接口和配置的模型。上下文组装与生成由独立脚本执行，未测试生产界面的原生会话编排，也未改动生产配置或索引。样本集中于航空领域，反向跨语言、同语种英文及拒答样本较少。同一模型的盲评不等同于独立人工复核。", "",
           "[总体2逐题结果](results.jsonl) · [适航知识库逐题结果](independent-results.jsonl) · [反向语言逐题结果](reverse-results.jsonl) · [复跑脚本](run.py)", ""]
(p / "README.md").write_text("\n".join(report),encoding="utf8")
print("\n".join(report).encode("ascii","backslashreplace").decode("ascii"))
