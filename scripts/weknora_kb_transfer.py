#!/usr/bin/env python3
"""WeKnora 知识库跨实例迁移（源 -> 目标），分块级搬运。

适用场景：源库里的文档是 `internal_rag` 类型（由 internal-rag 解析后经
POST /knowledge-bases/:id/knowledge/internal-rag 导入），WeKnora 侧没有原始文件，
`GET /knowledge/:id/download` 拿不到字节。这类内容只能按分块导出、再按分块导入：

    源: GET /api/v1/chunks/:knowledge_id      (分页，只含 chunk_type=text)
    目标: POST /api/v1/knowledge-bases/:id/knowledge/internal-rag
          {schema_version, source_document_id, source_name, ..., chunks:[...]}

目标实例会复用 `processChunks` 重新做 embedding（SkipPostProcess），分块文本、
页码、章节路径、表格 HTML、公式、原文块 ID 等元数据原样保存；向量不搬迁。

幂等：目标端按 (source_document_id, normalized_text_sha256) 判重，重复执行返回
action=skipped，可安全重跑 / 断点续跑。

用法示例：

    # 只看清单，不写目标（默认就是 dry-run）
    python scripts/weknora_kb_transfer.py \
        --src http://127.0.0.1:18081 --src-key sk-xxx \
        --dst http://10.0.0.9:18081 --dst-key sk-yyy \
        --kb 适航知识库 --limit 3

    # 真跑：目标端没有同名库时自动建库（沿用源库分块/模型配置）
    python scripts/weknora_kb_transfer.py ... --execute --create-kb

    # 只迁指定文档
    python scripts/weknora_kb_transfer.py ... --docs AC_25.785-1B.pdf,AC_25.773-1.pdf --execute

图片：源分块正文里的图片是绝对 URL（指向 internal-rag，如
http://localhost:8080/api/v1/ingestion/jobs/<job>/assets/<asset>）。目标机器上
这个地址通常不可达，用 --asset-base 改写成源机可达地址，或先用 --asset-mode keep
原样搬迁（正文检索不受影响，图片会裂）。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
from datetime import datetime

import requests

DEFAULT_TIMEOUT = 60
IMPORT_TIMEOUT = 1800  # 导入同步做 embedding，大文档可能几分钟


class WeKnora:
    def __init__(self, base: str, key: str, name: str):
        self.name = name
        self.base = base.rstrip("/") + "/api/v1"
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": key})

    # ---- 基础请求 -------------------------------------------------------
    def get(self, path: str, params: dict | None = None, timeout: int = DEFAULT_TIMEOUT):
        r = self.session.get(self.base + path, params=params, timeout=timeout)
        self._raise(r)
        return r.json()

    def post(self, path: str, body: dict, timeout: int = DEFAULT_TIMEOUT):
        r = self.session.post(self.base + path, json=body, timeout=timeout)
        self._raise(r)
        return r.json()

    def put(self, path: str, body: dict, timeout: int = DEFAULT_TIMEOUT):
        r = self.session.put(self.base + path, json=body, timeout=timeout)
        self._raise(r)
        return r.json()

    def delete(self, path: str, timeout: int = DEFAULT_TIMEOUT):
        r = self.session.delete(self.base + path, timeout=timeout)
        self._raise(r)
        return r.json() if r.content else {}

    @staticmethod
    def _raise(r: requests.Response):
        if r.status_code >= 400:
            raise RuntimeError(f"HTTP {r.status_code} {r.request.method} {r.url}: {r.text[:600]}")

    # ---- 资源 -----------------------------------------------------------
    def list_kbs(self) -> list[dict]:
        out, page = [], 1
        while True:
            j = self.get("/knowledge-bases", {"page": page, "page_size": 100})
            batch = j.get("data") or []
            out.extend(batch)
            if len(batch) < 100:
                return out
            page += 1

    def kb_detail(self, kb_id: str) -> dict:
        return self.get(f"/knowledge-bases/{kb_id}")["data"]

    def create_kb(self, payload: dict) -> dict:
        return self.post("/knowledge-bases", payload)["data"]

    def list_models(self) -> dict[str, str]:
        j = self.get("/models")
        models = j.get("data") or []
        return {m.get("name"): m.get("id") for m in models if m.get("name") and m.get("id")}

    def list_knowledge(self, kb_id: str) -> list[dict]:
        out, page = [], 1
        while True:
            j = self.get(f"/knowledge-bases/{kb_id}/knowledge", {"page": page, "page_size": 100})
            batch = j.get("data") or []
            out.extend(batch)
            if len(batch) < 100:
                return out
            page += 1

    def list_chunks(self, knowledge_id: str) -> list[dict]:
        out, page, total = [], 1, None
        while True:
            j = self.get(f"/chunks/{knowledge_id}", {"page": page, "page_size": 1000})
            batch = j.get("data") or []
            total = j.get("total", total)
            out.extend([c for c in batch if c.get("chunk_type") == "text"])
            if not batch or (total is not None and len(out) >= total) or len(batch) < 1000:
                return out
            page += 1

    def import_internal_rag(self, kb_id: str, payload: dict, dry_run: bool):
        payload = dict(payload)
        payload["dry_run"] = dry_run
        return self.post(f"/knowledge-bases/{kb_id}/knowledge/internal-rag", payload, timeout=IMPORT_TIMEOUT)

    def list_tags(self, kb_id: str) -> list[dict]:
        try:
            return self.get(f"/knowledge-bases/{kb_id}/tags").get("data") or []
        except RuntimeError:
            return []

    def create_tag(self, kb_id: str, name: str) -> str | None:
        j = self.post(f"/knowledge-bases/{kb_id}/tags", {"name": name})
        return (j.get("data") or {}).get("id")

    def move_to_folder(self, kb_id: str, knowledge_ids: list[str], folder_path: str):
        self.post("/knowledge/folder", {"kb_id": kb_id, "knowledge_ids": knowledge_ids, "folder_path": folder_path})

    def batch_tags(self, knowledge_ids: list[str], tag_ids: list[str]):
        self.put("/knowledge/tags", {"knowledge_ids": knowledge_ids, "tag_ids": tag_ids})


# ---------------------------------------------------------------------------
def parse_args(argv=None):
    p = argparse.ArgumentParser(description="WeKnora 知识库跨实例迁移（分块级）")
    p.add_argument("--src", required=True, help="源实例地址，如 http://127.0.0.1:18081")
    p.add_argument("--src-key", required=True, help="源实例 X-API-Key（需 retrieve）")
    p.add_argument("--dst", required=True, help="目标实例地址")
    p.add_argument("--dst-key", required=True, help="目标实例 X-API-Key（需 retrieve+ingest+manage_kbs）")

    p.add_argument("--kb", help="源知识库名称（与 --kb-id 二选一）")
    p.add_argument("--kb-id", help="源知识库 ID")
    p.add_argument("--dst-kb", help="目标知识库名称（默认与源同名）")
    p.add_argument("--dst-kb-id", help="目标知识库 ID（指定后不再查找/创建）")
    p.add_argument("--create-kb", action="store_true", help="目标端无同名库时自动建库（沿用源库配置）")
    p.add_argument("--dst-embedding-model", help="目标端 embedding 模型 ID（默认按模型名从源库映射）")
    p.add_argument("--dst-summary-model", help="目标端摘要模型 ID（默认按模型名映射）")
    p.add_argument("--dst-parent-chunk-size", type=int, default=16384,
                   help="新建目标库时的 parent_chunk_size（默认 16384）。导入时父块正文会按该值"
                        "重新切分，源库的长父块（本库最长约 11.7k 字符）只有在目标值更大时才能原样保留")
    p.add_argument("--restore-config", action="store_true",
                   help="迁移结束后把目标库 chunking_config 改回源库配置（父块已落库，不受影响）")

    p.add_argument("--docs", help="只处理这些文档（逗号分隔的 file_name/title）")
    p.add_argument("--limit", type=int, help="最多处理多少篇（按源库顺序）")
    p.add_argument("--offset", type=int, default=0, help="跳过前 N 篇")
    p.add_argument("--sleep", type=float, default=0.0, help="每篇之间休眠秒数")

    p.add_argument("--asset-mode", choices=["rewrite", "keep"], default="keep",
                   help="图片 URL 处理：rewrite 改写到 --asset-base，keep 原样")
    p.add_argument("--asset-base", default="", help="改写用的源机可达地址，如 http://192.168.15.16:8080")

    p.add_argument("--copy-folders", action="store_true", help="迁移文档所在文件夹路径")
    p.add_argument("--copy-tags", action="store_true", help="迁移文档标签（按名称映射，缺失则新建）")

    p.add_argument("--execute", action="store_true", help="真正写入目标（默认 dry-run）")
    p.add_argument("--yes", action="store_true", help="跳过确认")
    p.add_argument("--report", help="报告输出路径（JSON）")
    p.add_argument("--log", help="逐篇日志（JSONL）路径，用于断点审计")
    return p.parse_args(argv)


def rewrite_assets(text: str, src_prefix: str, dst_base: str) -> str:
    if not text or not dst_base:
        return text
    return text.replace(src_prefix, dst_base.rstrip("/"))


def detect_asset_prefix(chunks: list[dict]) -> str | None:
    """从正文里推断图片 URL 前缀（host:port + /api/v1/ingestion/jobs/...）。"""
    for c in chunks:
        content = c.get("content") or ""
        idx = content.find("](/api/v1/ingestion/")
        if idx > 0:
            return content[:idx].rsplit("](", 1)[-1]
        idx = content.find("](http")
        if idx >= 0:
            url = content[idx + 2:].split(")", 1)[0]
            parsed = urllib.parse.urlsplit(url)
            if parsed.scheme and parsed.netloc:
                return f"{parsed.scheme}://{parsed.netloc}"
    return None


def build_import_payload(kb_item: dict, chunks: list[dict], asset_base: str) -> dict:
    meta = kb_item.get("metadata") or {}
    payload_chunks = []
    for c in chunks:
        cm = c.get("metadata") or {}
        text = c.get("content") or ""
        if asset_base:
            prefix = detect_asset_prefix([c])
            if prefix:
                text = rewrite_assets(text, prefix, asset_base)
        payload_chunks.append({
            "chunk_id": cm.get("external_chunk_id") or c.get("id"),
            "parent_chunk_id": cm.get("external_parent_chunk_id") or "",
            "title": kb_item.get("title") or kb_item.get("file_name") or "",
            "text": text,
            "page_start": cm.get("page_start") or 0,
            "page_end": cm.get("page_end") or 0,
            "section_path": cm.get("section_path") or [],
            "block_ids": cm.get("block_ids") or [],
            "article_id_raw": cm.get("article_id_raw") or "",
            "article_id_normalized": cm.get("article_id_normalized") or "",
            "article_parent_id": cm.get("article_parent_id") or "",
            "article_aliases": cm.get("article_aliases") or [],
            "keywords": cm.get("keywords") or [],
            "question_aliases": cm.get("question_aliases") or [],
            "asset_ids": cm.get("asset_ids") or [],
            "table_html": cm.get("table_html") or [],
            "table_rows": cm.get("table_rows") or [],
            "formula_latex": cm.get("formula_latex") or [],
            "related_chunks": cm.get("related_chunks") or [],
            "content_type": cm.get("content_type") or "text",
        })
    return {
        "schema_version": meta.get("internal_rag_schema_version") or "document-ir/0.2",
        "source_document_id": meta.get("internal_rag_source_document_id") or kb_item["id"],
        "source_name": kb_item.get("file_name") or kb_item.get("title") or kb_item["id"],
        "source_path": meta.get("internal_rag_source_path") or "",
        "source_sha256": meta.get("internal_rag_source_sha256") or kb_item.get("file_hash") or "",
        "normalized_text_sha256": meta.get("internal_rag_normalized_text_sha256") or "",
        "parser_name": meta.get("internal_rag_parser_name") or "",
        "parser_version": meta.get("internal_rag_parser_version") or "",
        "chunks": payload_chunks,
    }


def resolve_kb(client: WeKnora, kb_id: str | None, name: str | None) -> dict:
    if kb_id:
        return client.kb_detail(kb_id)
    for kb in client.list_kbs():
        if kb.get("name") == name:
            return client.kb_detail(kb["id"])
    raise SystemExit(f"[{client.name}] 找不到知识库: {name}")


def build_kb_payload(src_kb: dict, name: str, embedding_id: str, summary_id: str | None,
                     parent_chunk_size: int | None = None) -> dict:
    keep = ("type", "chunking_config", "image_processing_config", "vlm_config", "asr_config",
            "question_generation_config", "auto_tag_config", "extract_config", "indexing_strategy")
    payload = {"name": name, "description": src_kb.get("description") or ""}
    for k in keep:
        if src_kb.get(k) is not None:
            payload[k] = src_kb[k]
    payload["embedding_model_id"] = embedding_id
    if summary_id:
        payload["summary_model_id"] = summary_id
    if parent_chunk_size:
        cfg = dict(payload.get("chunking_config") or {})
        cfg["parent_chunk_size"] = parent_chunk_size
        payload["chunking_config"] = cfg
    # 目标端 storage_provider 用默认即可，不照搬源端绑定
    return payload


def map_model(src_client: WeKnora, dst_client: WeKnora, model_id: str, label: str,
              override: str | None) -> str:
    if override:
        return override
    src_models = src_client.list_models()
    dst_models = dst_client.list_models()
    name = next((n for n, i in src_models.items() if i == model_id), None)
    if name and name in dst_models:
        print(f"  模型映射 {label}: {model_id} -> {dst_models[name]} (按名称 {name})")
        return dst_models[name]
    if not name:
        raise SystemExit(f"  源端模型 {model_id} 不在 /models 列表中，无法按名称映射 {label}；请用参数显式指定")
    raise SystemExit(
        f"  目标端没有同名 {label} 模型 {name!r}。请先在目标端注册同名模型，"
        f"或用 --dst-{label.replace('_', '-')} 指定目标 ID"
    )


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.asset_mode == "rewrite" and not args.asset_base:
        raise SystemExit("--asset-mode rewrite 需要同时给 --asset-base")

    src = WeKnora(args.src, args.src_key, "src")
    dst = WeKnora(args.dst, args.dst_key, "dst")

    src_kb = resolve_kb(src, args.kb_id, args.kb)
    print(f"源知识库: {src_kb['name']}  id={src_kb['id']}  docs={src_kb.get('knowledge_count')}")

    # ---- 目标库 ----------------------------------------------------------
    dst_kb = None
    if args.dst_kb_id:
        dst_kb = dst.kb_detail(args.dst_kb_id)
    else:
        dst_name = args.dst_kb or src_kb["name"]
        for kb in dst.list_kbs():
            if kb.get("name") == dst_name:
                dst_kb = dst.kb_detail(kb["id"])
                print(f"目标知识库已存在: {dst_name}  id={dst_kb['id']}")
                break

    embed_id = None
    if dst_kb is None:
        print("目标端无同名知识库。")
        if not args.execute or not args.create_kb:
            print("  dry-run：真跑时加 --execute --create-kb 才会建库。")
        else:
            embed_id = map_model(src, dst, src_kb["embedding_model_id"], "embedding_model",
                                 args.dst_embedding_model)
            summary_id = None
            if src_kb.get("summary_model_id"):
                summary_id = map_model(src, dst, src_kb["summary_model_id"], "summary_model",
                                       args.dst_summary_model)
            payload = build_kb_payload(src_kb, args.dst_kb or src_kb["name"], embed_id, summary_id,
                                       args.dst_parent_chunk_size)
            dst_kb = dst.create_kb(payload)
            print(f"已在目标端建库: {dst_kb['name']}  id={dst_kb['id']}  embedding={embed_id}")
    else:
        if dst_kb.get("embedding_model_id") != src_kb.get("embedding_model_id"):
            print(f"  注意: 目标库 embedding 模型 {dst_kb.get('embedding_model_id')} "
                  f"与源库 {src_kb.get('embedding_model_id')} 不同，检索结果会有差异。")

    # ---- 文档清单 --------------------------------------------------------
    docs = src.list_knowledge(src_kb["id"])
    if args.docs:
        wanted = {d.strip() for d in args.docs.split(",") if d.strip()}
        docs = [d for d in docs if (d.get("file_name") or d.get("title")) in wanted]
    docs = [d for d in docs if (d.get("parse_status") or "completed") == "completed"]
    docs = docs[args.offset:]
    if args.limit:
        docs = docs[:args.limit]
    print(f"待迁移文档: {len(docs)} 篇（已跳过非 completed / offset）")

    if not args.execute:
        print("\n== dry-run：只读源端并检查目标库，不写入 ==")

    # ---- 标签映射 --------------------------------------------------------
    tag_map: dict[str, str] = {}
    if args.copy_tags and dst_kb:
        dst_tags = {t.get("name"): t.get("id") for t in dst.list_tags(dst_kb["id"])}
        src_tags = {t.get("id"): t.get("name") for t in src.list_tags(src_kb["id"])}
        for tid, tname in src_tags.items():
            if tname in dst_tags:
                tag_map[tid] = dst_tags[tname]

    report_path = args.report or f"kb-transfer-{datetime.now():%Y%m%d-%H%M%S}.json"
    log_path = args.log or report_path.replace(".json", ".jsonl")
    log = open(log_path, "w", encoding="utf-8")

    stats = {"created": 0, "updated": 0, "skipped": 0, "failed": 0,
             "chunks_sent": 0, "docs": 0}
    started = time.time()
    failures = []

    for i, doc in enumerate(docs, 1):
        label = doc.get("file_name") or doc.get("title") or doc["id"]
        prefix = f"[{i}/{len(docs)}] {label}"
        t0 = time.time()
        try:
            chunks = src.list_chunks(doc["id"])
            if not chunks:
                raise RuntimeError("源端没有 text 分块")
            payload = build_import_payload(doc, chunks, args.asset_base if args.asset_mode == "rewrite" else "")
            if args.execute and dst_kb is not None:
                res = dst.import_internal_rag(dst_kb["id"], payload, dry_run=False)
                data = res.get("data") or {}
                action = data.get("action") or "?"
                new_id = data.get("knowledge_id")

                # 文件夹 / 标签（导入后补，失败不算迁移失败）
                if args.copy_folders and new_id and doc.get("folder_path"):
                    try:
                        dst.move_to_folder(dst_kb["id"], [new_id], doc["folder_path"])
                    except RuntimeError as exc:
                        print(f"    ! 文件夹设置失败: {exc}")
                if args.copy_tags and new_id:
                    names = [tag_map.get(t.get("id")) for t in (doc.get("tags") or [])]
                    ids = [n for n in names if n]
                    if ids:
                        try:
                            dst.batch_tags([new_id], ids)
                        except RuntimeError as exc:
                            print(f"    ! 标签设置失败: {exc}")
                stats[action if action in stats else "created"] = stats.get(action, 0) + 1
                stats["chunks_sent"] += len(chunks)
                print(f"{prefix}  chunks={len(chunks)} -> {action} ({time.time()-t0:.1f}s)")
            else:
                res = dst.import_internal_rag(dst_kb["id"], payload, dry_run=True) if dst_kb else {}
                data = res.get("data") or {}
                print(f"{prefix}  chunks={len(chunks)}  validated={data.get('action', 'no-target-kb')}")
            stats["docs"] += 1
            log.write(json.dumps({"doc": doc["id"], "label": label, "chunks": len(chunks),
                                  "result": data, "elapsed": round(time.time() - t0, 2)},
                                 ensure_ascii=False) + "\n")
        except Exception as exc:  # noqa: BLE001 - 单篇失败不中断整体
            stats["failed"] += 1
            failures.append({"doc": doc["id"], "label": label, "error": str(exc)[:500]})
            print(f"{prefix}  FAILED: {str(exc)[:300]}")
            log.write(json.dumps({"doc": doc["id"], "label": label, "error": str(exc)[:800]},
                                 ensure_ascii=False) + "\n")
        log.flush()
        if args.sleep:
            time.sleep(args.sleep)

    log.close()

    # 迁移时为了保住源库的长父块，临时把 parent_chunk_size 放大；这里可选改回源库配置。
    restored = False
    if args.restore_config and args.execute and dst_kb and src_kb.get("chunking_config"):
        try:
            dst.put(f"/knowledge-bases/{dst_kb['id']}",
                    {"name": dst_kb["name"],
                     "config": {"chunking_config": src_kb["chunking_config"]}})
            restored = True
            print(f"\n已把目标库 chunking_config 改回源库配置（parent_chunk_size="
                  f"{src_kb['chunking_config'].get('parent_chunk_size')}）")
        except RuntimeError as exc:
            print(f"\n! 还原目标库 chunking_config 失败: {exc}")

    summary = {"source": {"url": args.src, "kb_id": src_kb["id"], "kb_name": src_kb["name"]},
               "target": {"url": args.dst, "kb_id": dst_kb["id"] if dst_kb else None,
                          "kb_name": dst_kb.get("name") if dst_kb else None},
               "execute": args.execute, "stats": stats, "config_restored": restored,
               "elapsed_seconds": round(time.time() - started, 1),
               "failures": failures}
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)

    print("\n== 汇总 ==")
    print(json.dumps(stats, ensure_ascii=False))
    print(f"耗时 {summary['elapsed_seconds']}s，报告: {os.path.abspath(report_path)}")
    if failures:
        print(f"失败 {len(failures)} 篇，详见报告 failures 字段。")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
