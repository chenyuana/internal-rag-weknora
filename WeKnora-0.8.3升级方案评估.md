# WeKnora 0.8.3 升级方案评估

评估日期：2026-10-16（Asia/Shanghai）。范围：当前定制部署升级可行性、补丁移植、数据迁移、验收及回滚。此次未升级服务、修改配置或执行数据库写入。

## 结论

建议升级，但先在隔离环境验证，再安排停写切换。目标应为“0.8.3 + 已验证的本地能力”，不能直接拉官方镜像替换。当前主要风险是本地图片链路与上游新实现重叠、未提交的 Wiki/增强补丁，以及 ParadeDB 扩展升级后的回滚限制。

首轮保持现有 embedding 模型、切片和图谱开关，不全库重解析、不启用全库图片向量。图片画廊与原文引用可先验证；多模态 embedding 单独用小样本评估。当前没有必须当天切换的证据。

## 1. 现场实测与基线

实际部署工作区是 `C:\Users\Win11\.codex\worktrees\weknora-082-upgrade\weknora-evaluation`，并非当前评估目录。容器 Compose 标签确认使用该目录的 `docker-compose.yml` 和 `D:\weknora-evaluation\backups\pre-chunk-enrichment-20261013\compose.enrichment.json`。

| 项目 | 2026-10-16 实测 |
|---|---|
| 部署工作区 HEAD | `214ed452`，基于官方 v0.8.2，另有 9 个本地提交 |
| 应用镜像 | `weknora-app:auto-wiki-20261014`，health healthy |
| 前端 / docreader | `wechatopenai/weknora-ui:internal-rag-082` / `wechatopenai/weknora-docreader:internal-rag-082` |
| PostgreSQL 镜像 | `paradedb/paradedb:v0.22.6-pg17` |
| schema_migrations | `110`，dirty=false |
| 数据库扩展 | `pg_search=0.22.6`，`vector=0.8.1` |
| 官方目标 tag | `v0.8.3`，提交 `3e22822c1d2397be730c458c7539d0eb8c113a24` |
| 上游净变更 | v0.8.2 → v0.8.3：1576 文件，+142102 / -16333 行（含文档等） |

部署工作区相对 v0.8.2 的已跟踪差异为 47 个文件、+4330/-24 行；另有未跟踪的 Wiki 召回、已有 chunk 增强及测试文件。旧的 0.8.2 评估描述的是更早现场，不能直接拿它的“仍运行 0.8.0/迁移 90”作为此次前提。

重要待核验：10-12 的表格图片记录声称部署过专用前端，但当前前端 tag 为 internal-rag-082。tag 本身不能证明缺少该补丁，也不能证明包含；移植前需核对镜像 ID/静态资产与源码。Neo4j 容器当前运行，但既有记录表示业务图谱已关闭；不能把容器运行等同于图谱试验重新启用。

## 2. 升级收益与适用边界

| 能力 | 对当前知识库的价值 | 首轮策略 |
|---|---|---|
| 图片画廊 | 按图注/OCR/来源浏览图片，辅助核查图片关联 | 验证历史 image_info 投影及权限 |
| 原文引用定位 | 更容易回查 PDF/Office 等原文证据 | 旧文档先接受文本匹配回退，不强制重解析 |
| 图片向量与视觉上下文 | 有机会改善图表发现及看图回答 | 小库试验，保留现有图片关联，禁止直接换全库模型 |
| 检索修复及诊断 | 去重、重排、截断可见性有改进 | 用固定问题对照，不能由 changelog 推定质量提高 |
| Wiki 状态与并发修复 | 有望减少 processing/finalizing 滞留 | 保留接入台自动生成与原文证据召回的本地语义 |
| 用户管理、模型目录 | 内网管理更方便 | 需要时启用，核查注册及模型配置契约 |

官方说明：历史图片向量不会自动补齐；启用多模态与 image_vector_enabled 后需重解析选定文档，扫描 PDF 页面不在该功能范围。更换到不兼容的消息式 embedding 模板要重建相应向量。它不能作为保留现有清洗 chunk 的无损开关。

## 3. 本地补丁移植风险

对部署工作区“相对 v0.8.2 的本地改动”与上游 v0.8.3 做路径交集：21 个文件双方都修改。对交集中的已跟踪文件，以 v0.8.2 为共同基线，用临时文件执行 `git merge-file -p`，8 个文件产生文本冲突：

- `.env.example`
- `.github/workflows/docker-image.yml`
- `frontend/src/views/chat/components/AgentStreamDisplay.vue`
- `frontend/src/views/chat/components/botmsg.vue`
- `internal/application/service/knowledge_process.go`
- `internal/application/service/knowledgebase_search.go`
- `internal/types/chat_manage.go`
- `internal/types/search.go`

这是逐文件文本检查，不是完整 cherry-pick 演练或编译验证；其余文件文本能合并也不等于语义兼容。未跟踪文件尚须加入完整移植清单。

| 补丁 | 风险及处理 |
|---|---|
| 数字文件名召回 | 保留 AC 文件号识别与候选扩展。上游 HybridSearch 增加 rerank 等行为，检查本地 wrapper 避免双重重排及放宽文档范围 |
| 图片进入远程视觉模型 | 上游已有 ContextImages/ContextImageChunkIDs，并在当前用户消息拼入召回图片。与本地 RetrievedImages 链路重叠，应收敛为一次注入，保留图片可达性、鉴权、预算及远程传输回归 |
| 图注、表格及续表关联 | 上游图片向量不能证明覆盖 metadata.asset_ids、描述性图注、跨页表格关联；保留或移植到上游路径，以样本证明可替代后再删除 |
| 引用 UI | RelatedImages 与上游 MatchedImages、SourceLocators、CitationSources 必须兼容；答案及历史消息不得丢图，也不能重复展示两份图片 |
| internal-rag 导入与自动 Wiki | 保留 SaveChunks 后仅调度 Wiki 的行为。上游 post-process 增加 attemptSuperseded 和 withAttempt；本地手动增强调度须遵守代次与取消/删除边界 |
| Wiki 发现文档再召回原 chunk | 上游跨库 Wiki 搜索不等价于此补丁；继续用原 chunk 作证据，检查权限、标签/指定文档范围及插件执行顺序 |
| 已有 chunk 增强 | 新增文件仍依赖上游接口及任务状态机，需定向编译和服务测试；不得因合并成功自动运行全库增强 |
| 图谱 | 既有试验无效且已撤回，首轮保持关闭。图谱方向修复不能证明旧配置保存问题已经解决 |

补充：本地新增的是 MatchTypeWiki；上游新增的是另一组枚举 SourceType 的 ImageSourceType，本次没有发现两者直接撞值。仍需保持历史 MatchType 数值稳定。

## 4. 数据库迁移与基础设施

从实测迁移 110 升到 118，新增 8 个 up 迁移：

| 迁移 | 内容与关注点 |
|---|---|
| 111 | 模型目录配置 |
| 112 | embeddings 的 knowledge_id / chunk_id 普通 B-tree 索引；可能阻塞写入，大库可预建同名并发索引 |
| 113 | chunk_images 表、索引、触发器及历史 image_info 回填；需测耗时、空间和图片一致性 |
| 114 | chunks.source_locators JSONB |
| 115 | pg_search → 0.25.11、vector → 0.8.4，在目标扩展包可用时执行 |
| 116 | smart-reasoning 的空工具列表写入显式默认；“所有知识库”范围可能排除 Wiki-only 库 |
| 117 | 消息附件查找索引 |
| 118 | MCP OAuth 时间戳时区；旧值按 UTC 处理，偏移过的 token 可能需要重新授权 |

上游也修改了 93/94/99 的历史迁移。当前已到 110，不会因 SQL 文件变化自动重跑它们；不要为此强制重置版本。

ParadeDB 升级必须按顺序：停所有写入方 → 做新鲜、可恢复的数据库及角色备份/卷快照 → 替换 PG17 镜像 → 更新每个已安装扩展的数据库 catalog → 检查 pg_search=0.25.11、vector=0.8.4 → 启动新 app 完成迁移 → 关键词/向量检索验证。在 catalog 更新完成前不要开放应用流量或调用版本诊断函数；新库上不要执行旧的 UPDATE TO '0.22.6' 命令。

不能只依赖 115：它仅处理 WeKnora 数据库，目标包缺失时可跳过，而且不处理其他库。数据库已经迁移后换镜像也不会重跑它。

回滚必须使用升级前备份/快照恢复到独立卷，配合旧镜像。不能把已升级数据卷交回 0.22.6：扩展不能靠 down 迁移降级，0.24 起的自定义 WAL 记录旧镜像不能重放。

上游 Compose 还改变了 MinIO 镜像；当前 MinIO 名称显示属于另一个 Compose 项目，可能与 RAGFlow 共用。必须先核对实际存储端点和卷归属，首轮避免连带替换共享存储。app/UI/docreader 使用一致目标源码/版本；禁止继续以旧镜像基底仅覆盖二进制，遗漏迁移、解析器或静态资源。

保留现有 SYSTEM_AES_KEY、JWT_SECRET、SYSTEM_SIGNING_KEY 及存储配置，不用新 .env.example 覆盖现有凭据。保留已验证的 completion token 预算，逐项合并配置。invite_only 现在禁止邀请密码注册，若需要邀请注册应选择 invite_register。工具列表 [] 与 missing/null 的语义不同，须核查实际 agent 配置。

## 5. 建议实施顺序

1. **固定现场**：以真实部署工作区为源，保存已提交和未提交/未跟踪补丁、配置引用、镜像 digest、前端资产版本及数据库版本；敏感配置放受限备份，不放普通报告。
2. **建立隔离升级分支**：从固定 v0.8.3 tag 建立 codex/ 前缀分支，移植本地能力；原目录有大量未提交改动，禁止直接 reset/pull 覆盖。先处理类型/模型适配，再检索与图片，再导入/Wiki/增强，最后前端与配置。
3. **构建一致镜像**：官方 go.mod 为 Go 1.26.0，Windows PATH 未发现 go；使用匹配工具链或容器构建。跑定向 Go 测试、前端回归和生产构建，固定镜像 digest。
4. **克隆数据演练**：恢复新备份到独立卷，使用独立 Compose 项目/端口/队列/存储。隔离 Redis 后台任务，禁用自动数据源同步、webhook 和生产写入，避免复制任务作用到生产。图片读取可使用受控只读副本，不让测试清理影响生产对象。
5. **迁移与回滚演练**：按数据库指南升库，记录每条迁移耗时、空间和锁等待；恢复旧备份到另一个独立旧版卷并验证检索，证明回滚可用。
6. **生产切换**：演练验收通过后，在维护窗口停接入台/同步/上传和后台写入，等待或安全停止在途任务，重新备份；依已验证流程升库、迁移、切换一致镜像及实际 Compose override。重建 app 后刷新前端 Nginx 的地址缓存。
7. **分批验证新能力**：首轮稳定后，另建小样本库评估图片 embedding；只有证明收益并确认切片变化可接受，才讨论重解析范围。

工作量粗估：熟悉现有补丁的开发者约 3–5 个工作日完成移植、构建和演练；不含额外模型部署与大规模重解析。未实测迁移和恢复时间，因此不承诺停机时长，维护窗口以演练数据决定。

## 6. 上线验收门槛

- schema_migrations=118、dirty=false；目标扩展版本一致；app/docreader health 正常，关键词与向量索引可读写。
- 原始 chunk ID、正文、边界、关键 metadata、enabled 状态与升级前快照一致；允许新增投影表/定位字段，不允许意外重切片。旧记录的 24,472 是历史数量，应在演练前重新采集当前快照。
- AC 20-173 固定 Q1/Q2：有/无文件号都检查原文召回及引文。旧 Wiki 试验仅证明个例改善，不能以该例替代全库评估。
- 描述性图注、普通图片及跨页 Table I–IV：正确关联、权限可达、视觉模型真正收到图片、无重复注入、文本模型不发送图片；复核历史 7 张表图样本及 12 张/15MB 预算。
- 新 internal-rag 导入自动 Wiki 入队；最终 completed 且 pending=0；相同内容重复导入 skipped、不重复入队。失败、取消、删除、重试和新旧 attempt 不留下悬挂状态。
- 已有 chunk 增强不改变原文；Wiki 只用于发现原文证据，不绕过租户/共享权限、标签及指定文档限制。
- 流式/非流式、历史会话、图片引用与原文定位正常；旧文档文本匹配回退可接受。
- 核查 smart-reasoning 默认工具、Wiki-only 库范围、邀请注册与 MCP OAuth；测试明确列出通过/失败，不把旧记录的通过结果当本次通过。
- 回滚已演练，备份位于数据卷之外；旧镜像、配置、静态资源及对象文件备份完整。

任一数据完整性、权限、检索或自动 Wiki 核心回归失败即不切换。升级后故障采用停写、保存故障现场、恢复独立旧卷和旧镜像的流程；评估回滚会丢失的升级后写入，不直接用历史全库 dump 覆盖新数据。

## 7. 证据和未验证项

已执行：官方 tag 获取、v0.8.2/v0.8.3 diff、真实部署工作区状态/提交/文件差异、逐文件三方文本检查、Docker 容器与 Compose 标签读取、数据库迁移及扩展只读查询、既有图片/Wiki试验记录读取。

未执行：新镜像构建、Go/前端测试、升级后的真实 API 回归、数据库迁移/备份恢复、迁移耗时测试、共享 MinIO 归属及完整运行源码一致性核对。此前文档记载的测试不是此次新验证。

额度检查：开始时 5 小时窗口剩余 96%、周窗口 85%；阶段复查剩余 92%/84%，未触发 quota-handoff 的 ≤10% 停止阈值。该技能仅在执行检查点检查，不是后台监控。

官方来源（同时以本地 v0.8.3 tag 源码核对关键实现）：

- [v0.8.3 Release](https://github.com/Tencent/WeKnora/releases/tag/v0.8.3)
- [固定 tag 的 CHANGELOG](https://github.com/Tencent/WeKnora/blob/v0.8.3/CHANGELOG.md)
- [ParadeDB 升级与回滚指南](https://github.com/Tencent/WeKnora/blob/v0.8.3/website-docs/01-getting-started/06-paradedb-upgrade.md)
- [官方版本差异](https://github.com/Tencent/WeKnora/compare/v0.8.2...v0.8.3)
