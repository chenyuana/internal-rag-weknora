# 基于已有 chunk 生成 Wiki 和图谱

自 2026-10-14 的自动 Wiki 修复起，接入台调用 `POST /api/v1/knowledge-bases/:id/knowledge/internal-rag` 导入新资料或更新资料时，如果知识库开启 Wiki，完成已有 chunk 索引和外部元数据保存后，自动提交 Wiki 专用增强任务，响应包含 `wiki_status: "queued"`。页面异步生成，入队不等于生成已完成；不会同时启用图谱、摘要或问题生成。dry-run 和内容哈希相同的已完成资料跳过导入时，不触发重复生成。Wiki 入队失败会明确返回“文档已导入，但自动 Wiki 调度失败”及文档 ID，可使用下方手动接口补建。开启开关不会自动扫描历史资料。

接口：`POST /api/v1/knowledge-bases/:id/knowledge/enrich`。
使用与导入相同的知识库写权限和 API key 范围检查。

```json
{
  "knowledge_ids": ["4272c6b1-0113-4625-80a2-7b04a9fb30b0"],
  "wiki": true,
  "graph": false,
  "dry_run": true
}
```

一次明确选择 1–20 份已完成、没有后台任务的文档。先开启库的相应索引策略；图谱还需要启用 Neo4j 和抽取配置。`dry_run: true` 验证归属、文档状态和已有切片，返回切片数量；改为 false 才提交后台任务。批次提交途中失败时，响应 data 列出已提交文档，不盲目重发整批。

生成只读取已有文本/OCR/caption chunk，不运行解析、清洗、重新切分、向量重建、摘要重生成、问题生成或自动标签。原始 chunk ID、正文和元数据保持不变；新增 Wiki 页、图谱节点和关系。重复生成可更新增强内容，模型输出可能变化。

调用脚本 `scripts/enrich-existing-chunks.py` 默认只验证。API key 从 `WEKNORA_API_KEY` 环境变量读取，不放进命令参数或输出。

```powershell
python scripts/enrich-existing-chunks.py --kb b35a43d9-8477-4f7a-8edb-7311222ff61c --knowledge-id 4272c6b1-0113-4625-80a2-7b04a9fb30b0 --wiki
```

加 `--apply` 提交；加 `--graph` 同时选择图谱。大库应按主题分批，不在试运行中默认生成全库。

普通问答通过 Wiki 标题和别名发现相关文档，再在这些文档已有 chunk 中执行检索，并补充 Wiki 引用的原文片段，最后进入原有重排和回答流程。本部署版本不会创建 Wiki 向量切片。只使用已发布页面，保留文档范围限制；跨租户共享知识库暂不使用此补充召回。词面匹配可能遗漏同义表达。

效果验证使用同样的不带文件号/带文件号问题，新建会话并关闭联网，保存实际召回来源。生成前后按原始 chunk ID 核对正文、边界和元数据。生成成功不等于回答质量改善，必须检验相关原文召回和最终答案。
