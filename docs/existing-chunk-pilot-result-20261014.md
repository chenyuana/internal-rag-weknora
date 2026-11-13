# 已有 chunk 增强试验记录

知识库：`b35a43d9-8477-4f7a-8edb-7311222ff61c`（FAA-AC图片版）。仅对 `AC_20-173.pdf` 的 23 个已有文本切片试运行；未批量生成 245 份资料。

## 已验证的结果

相同问题、相同回答模型、新会话、普通问答模式、关闭联网。问题是平板与显示器的分类及谁负责说明已安装组件；Q1 不带文件号，Q2 添加 AC 20-173。

| 条件 | Q1 原文召回 | Q2 原文召回 |
|---|---|---|
| 原有 RAG | 未找到相关依据 | 找到 AC 20-173 |
| 仅生成 Wiki 页面 | 未找到相关依据 | 找到 AC 20-173 |
| Wiki 发现文档，再检索已有 chunk | 找到 AC 20-173 | 找到 AC 20-173 |
| 图谱试验撤回后的复测 | 找到 AC 20-173 | 找到 AC 20-173 |

最终回答引用原始 chunk `8eebc026-4d44-4be6-8788-e3b7e50caa5d`，解释拆装频率不决定分类，并识别申请人的责任。这证明本题的检索缺口有所改善，不代表整个知识库准确率已经提升。模型正文保留了“正当改装”的例外，但结论表仍将未纳入型号设计的平板直接判为便携式，条件表达不够严谨，不能把这次答案认定为完全正确。

全库原始 24,472 个 chunk：无缺失、无正文或元数据变化、无新增 chunk。Wiki 新增的是页面，不是重新清洗或切分后的文本。普通问答使用页面标题/别名发现文档，然后召回原文、进入原有重排；Wiki 内容不直接取代原文证据。共享租户补充召回及同义表达仍有限制。

## 图谱试验已停止并恢复

图谱任务可从已有 chunk 提交，但本轮部分结果出现空输出或 JSON 解析失败。核查发现知识库 PUT 更新接口的 `KnowledgeBaseConfig` 不包含 `extract_config`，提交的关系类型、示例与提示词没有被保存；图谱开关通过 `indexing_strategy` 生效，而抽取配置只剩 `enabled=true`。因此本轮没有满足预定的图谱抽取条件，不能用节点数量或答案判断图谱价值。

按照“无效先恢复”的要求，未追加代码或重试提示词。已将知识库图谱开关和抽取 enabled 恢复为 false，应用 Neo4j 环境变量恢复原值，停止试验 Neo4j。保留已验证有效的 Wiki 检索版本；这不是撤回全部 Wiki 改动。失败记录及独立 Neo4j 试验卷留存，不参与当前召回。

## 运行与备份

完整备份目录：`D:\weknora-evaluation\backups\pre-chunk-enrichment-20261013`，含数据库 dump、源代码归档、原容器配置、原始 chunk 快照和镜像标签 `weknora-app:pre-chunk-enrichment-20261013`。不要用全库数据库恢复覆盖后续会话或其他用户数据。

当前有效镜像：`weknora-app:chunk-enrichment-20261013`，digest `sha256:a1c12d00f7fdad91cfe46a88fe25231b204f8a209278831e4f036d346f59c65f`。部署使用实际 0.8.2 checkout 和备份目录的 Compose 覆盖配置；日常重建使用 `scripts/start-verified-enrichment.ps1`，避免只运行基础 Compose 意外切回旧镜像。配置文件含本地凭据，不应分享。

原始记录见备份目录 `evaluation` 中的 `baseline`、`wiki-only`、`wiki-recall-final`、`restored-wiki` JSON 与 Markdown。接口用法见 `existing-chunk-enrichment.md`。图谱 pilot 脚本仅作本轮失败审计，不应重跑。
