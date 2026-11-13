# 接入台自动 Wiki 修复

行为：创建知识库时选择 Wiki，随后从资料接入台导入已经清洗的 chunk，WeKnora 在保存 chunk 和外部元数据之后，自动提交 Wiki 生成任务。无需再次点击手动生成，也不重新清洗或切分。

修复位置：`knowledge_internal_rag.go`。继续保留 `SkipPostProcess: true`，避免默认摘要和问题生成；改为在 `SaveChunks` 之后调用已有 Wiki 专用增强调度，保留原有权限、归属与状态检查，以及队列失败回滚。入队成功响应增加兼容性字段 `wiki_status: queued`。后续 Wiki 生成仍是异步的，文档可能暂处于 `processing` 或 `finalizing`。

部署镜像：`weknora-app:auto-wiki-20261014`。使用 `scripts/start-verified-enrichment.ps1` 重建应用。重建后已刷新前端 Nginx 的旧容器地址缓存，页面访问恢复正常。

备份：`backups/pre-auto-wiki-20261014`，包含新的数据库完整 dump、原有源码、Compose 配置、原始 300 个 chunk 快照；原应用镜像保存为 `weknora-app:pre-auto-wiki-20261014`。原始 Wiki 检索改动保留，图谱继续关闭。

验证：服务层相关测试通过；通过真实 API 创建临时 Wiki 知识库，再调用与接入台相同的 internal-rag 接口导入 3 个已有清洗 chunk，返回 `created` 和 `wiki_status: queued`，自动生成并发布 7 个内容页面及 Index 页面。文档最终为 `completed`，待处理任务为 0。完成后相同内容重复导入返回 `skipped`，未再次生成。生成结果与状态记录保存在备份目录，临时验证库已删除。未修改接入台页面或重新解析 PDF。

用户测试库 `6a114c40-1790-470f-b3e7-129227291699` 在修复前已有的 5 份资料，另行提交了 Wiki 补建任务。新的自动触发只影响此后实际导入/更新；不会在应用启动时重跑所有历史资料。

截至本次验证结束，5 份资料仍在后台生成，不能视为已经生成完毕。原有 300 个 chunk 的 ID、正文、边界和元数据再次核对均未改变。

限制：重复导入内容哈希相同的已完成资料保持原有跳过行为；如需补建 Wiki，请使用手动增强接口。Wiki 的模型错误、生成耗时及主题质量依然需根据后台任务和页面判断，不能只根据入队响应认定完成。
