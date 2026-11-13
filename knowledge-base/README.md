# 适航知识库（知识库文件不入库）

本目录只保存知识库的**清单与重建说明**，不保存任何 PDF 原件。

## 当前状态（2026-11-13 实测）

| 项 | 值 |
| --- | --- |
| 知识库 | 适航知识库 |
| Knowledge Base ID | `acdf013d-971b-42c3-b6ca-cf09157c9215` |
| 文档数 | 364（361 个不同文件名） |
| 原件体积 | 348,790,348 B（约 333 MiB） |
| 分块数 | 70,879 |
| 导入方式 | `internal_rag`（由 internal-rag 资料接入台解析后按分块导入） |
| Embedding 模型 ID | `cafe0214-cd51-4472-ad3b-f1f69a489a01` |
| 分块配置 | auto / 512 / overlap 80 / 子块 384 / 父块 4096（父子分块开启） |
| 内容构成 | FAA AC 245 份、Part 23 修正案与 DRS 等 117 份、Docket 2 份 |

`manifest.json` 逐份记录了 `file_name`、`title`、`size_bytes`、`sha256`、
`parser`、`source_document_id`，可用来核对一份外部副本是否完整。

## 为什么不入库

- 原件 333 MiB 且属于第三方文档（FAA AC / 修正案），进 git 历史后不可撤销；
- 这些文档的**权威副本**在 internal-rag 的摄取库里，仓库只需记录"有哪些、哈希是多少"；
- 评测与复现真正依赖的是分块文本、页码、章节路径等元数据，不在 PDF 字节本身。

## 重建方式

### 方式 1（推荐）：从既有实例分块级搬运

`scripts/weknora_kb_transfer.py` 按 `GET /api/v1/chunks/:knowledge_id` 导出源端分块，
再用 `POST /api/v1/knowledge-bases/:id/knowledge/internal-rag` 写入目标端，目标端重新做
embedding；按 `(source_document_id, normalized_text_sha256)` 幂等，可断点续跑。

```powershell
python scripts/weknora_kb_transfer.py `
  --src http://127.0.0.1:18081 --src-key sk-xxx `
  --dst http://127.0.0.1:18081 --dst-key sk-yyy `
  --kb 适航知识库 --execute --create-kb
```

### 方式 2：从 internal-rag 摄取库重新导入

原件在 `D:\internal-rag\data\ingestion\originals\<sha 前两位>\<sha256>\source.pdf`
（本机共 398 份 1.5 GiB，其中 361 份属于本知识库）。用资料接入台重新解析后，把结果
POST 到 WeKnora 的 internal-rag 导入接口即可，`manifest.json` 里的 `sha256` 就是原件目录名。

### 方式 3：整机恢复

知识库正文保存在容器 `WeKnora-postgres`（库 `WeKnora`，`knowledge_bases` / `knowledges` /
`chunks` 表），向量与原始上传在 MinIO 卷内。整体迁移可直接搬 Docker 卷。

## 说明

- 该库是 `internal_rag` 类型：WeKnora 侧没有原始文件，`GET /knowledge/:id/download`
  拿不到字节，所以"下载知识库导出 zip"这条路对本库不适用；
- 检索相关的调参结论（RRF 权重、编号类问句命中、rerank 空转等）见仓库根目录的
  `RETRIEVAL_ANALYSIS.md` 与 `docs/ragas-evaluation.md`。
