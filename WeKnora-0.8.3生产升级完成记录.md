# WeKnora 0.8.3 生产升级完成记录

2026-10-16（Asia/Shanghai）。生产已切换，系统接口实测 version=0.8.3、db_version=118。

## 运行版本

| 服务 | 已部署镜像 |
|---|---|
| 应用 | weknora-app:internal-rag-083-20261016 |
| 前端 | weknora-ui:internal-rag-083-20261016 |
| docreader | wechatopenai/weknora-docreader:v0.8.3 |
| PostgreSQL | paradedb/paradedb:v0.25.11-pg17 |

应用镜像ID：`sha256:1252fe9c40dc4b126c3e9f000c8fd46a64b5973c5f8cae241f4be5af995ee78a`。
前端镜像ID：`sha256:3c82729e710913c9ec46e6cae3db8c6b4b818b17ae5a8a780518f3936afbbe3c`。
真实运行镜像ID已与受限备份中的 expected-images.json 全部核对。

迁移118、dirty=false；pg_search=0.25.11、vector=0.8.4。生产WeKnora、paradedb、postgres、template1中的已安装扩展均按升级SQL处理。

## 数据保护与验证

- 切换前停止WeKnora应用和前端写入，制作全部可连接数据库的自定义格式dump、角色备份和文件副本；没有更换共享MinIO。
- 原始243,433个chunk的ID、序号、正文、原始内容、metadata、边界、类型、父/前/后关联、image_info、enabled和deleted_at证据哈希，在生产迁移前后完全相同。
- 保留现有embedding模型、AES/JWT/signing配置、token预算、图谱开关；没有全库重解析或生成历史图片向量。
- 隔离库实际恢复成功，迁移111–118通过，恢复及迁移后全部证据哈希一致。
- chat_pipeline全量及相关服务/仓库/检索/协议定向测试通过；AnyDoc0.2.4原生库、带anydoc标签的后端构建及镜像构建成功。
- 前端4项相关引用图片测试通过，生产构建成功（49.86秒）。本机将LESS预处理改为串行；并行构建期间Docker虚拟机曾失联，构建时临时停止RAGFlow应用后完成，RAGFlow已恢复。
- 隔离实际API验证：有/无文件号检索、流式问答、历史消息读取、自动Wiki入队/完成（pending=0）和重复导入skipped。实际问答日志确认加载并发送4张原图，读取失败数为0。
- 生产入口验证：主页、health、知识库列表、带AC20-173文件号的检索均返回200；检索包含目标原文；匿名知识库访问被401拒绝；system/info确认0.8.3与118。

这些验证覆盖升级关键路径和固定样本，不能替代全部资料/模型/连接器的穷尽测试。旧文档原文定位可能使用文本匹配回退；未为补定位而重解析。

## 备份与现场

- 初始完整现场：`D:\weknora-evaluation\backups\pre-083-20261016-091641`，包含源码、Git bundle、原运行配置、数据库、角色、文件/对象副本及旧镜像。
- **停写切换备份**：`D:\weknora-evaluation\backups\cutover-083-20261016-155054`。
- 后者含 BACKUP_READY.json、各库dump/目录、globals.sql、containers-before.json、production-083.json、expected-images.json、原始证据前后快照、CUTOVER_PASSED.json、production-api-verification.json及最终源码归档。
- 旧app、UI、postgres已有完整docker-save归档；docreader另有完整rootfs导出及原Config元数据，可按配置恢复。目录中早期 `.tmp-*` 为未完成归档，不能当备份加载。
- manifest-final.json记录完成文件的SHA256和目录库存；目录库存没有逐文件哈希。共享MinIO初始副本是在线副本，不声称为RAGFlow/MinIO全服务停写快照。
- 备份目录有受限ACL，配置及验证报告可能包含密钥或私有资料，禁止提交或公开分享。
- 新源码：`D:\weknora-083-upgrade`，分支codex/weknora-083-upgrade，官方基线3e22822c，加本地移植；仍为未提交工作，未推送。
- 原部署目录继续承载基础Compose，新override明确使用新镜像及 `D:\weknora-083-upgrade\config\config.yaml`。不能直接只运行基础Compose。

## 日常启动与回滚

日常启动：`D:\weknora-evaluation\scripts\start-verified-083.ps1`。
历史 `start-verified-enrichment.ps1` 已转发到新脚本，避免误启动旧app。新脚本检查已验收镜像ID，使用固定override及--no-build/--pull never；已实际执行通过。

升级验证容器已停止，保留其容器、网络和独立卷，不参与生产；原生产及同机RAGFlow/MinIO服务已恢复运行。

回滚不能只把PostgreSQL镜像换回0.22.6。须停写，使用切换前dump/角色/文件恢复到独立旧版卷，再配旧镜像和旧配置，并评估升级后新增写入。禁止将已升级扩展的数据卷直接交给旧镜像。

主要执行日志：notes/upgrade-083-production-cutover.log、upgrade-083-production-api.log、upgrade-083-frontend-serial-retry.log、upgrade-083-ui-image.log，以及受限备份中的验证JSON。

本次没有发布GitHub代码或PR，没有设置自动后台监控。
