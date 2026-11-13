# 知识库评测（第一版）

入口：左侧“知识库评测”。支持历史对话导入、JSON 数组 / JSONL 导入、逐题评分和报告导出。历史导入最多读取最近 200 条消息，通过 request_id 匹配完整问答；缺少上下文的样本跳过评分。历史引用不等同于完整 Prompt 上下文，多轮问题应手动补全问题语义。

报告仅保留在当前页面内存中，离开前导出 JSON。导入报告时只恢复样本，重新评分，避免旧分数被误认为当前结果。尚未实现持久化任务、CSV、重新运行知识库问答、完整 Prompt 快照和版本对比。

## 启动 Worker

建议独立虚拟环境，Python 3.10+：

```powershell
python -m venv .venv-ragas
.venv-ragas/Scripts/python -m pip install -r scripts/ragas-worker/requirements.txt
$env:RAGAS_WORKER_TOKEN = '<随机长密钥>'
$env:RAGAS_MODEL = '<支持结构化输出的评判模型名>'
$env:OPENAI_API_KEY = '<模型密钥>'
$env:OPENAI_API_BASE = '<兼容 OpenAI 的 API 地址，包含 /v1>'
.venv-ragas/Scripts/python -m uvicorn app:app --app-dir scripts/ragas-worker --host 127.0.0.1 --port 8099
```

WeKnora 后端需设置 RAGAS_WORKER_URL=http://127.0.0.1:8099 与相同 RAGAS_WORKER_TOKEN，然后重启新构建的后端。若 Go 后端在 Docker 中，127.0.0.1 指容器自身，应按实际网络设置内部服务地址。Worker 不公开端口，不从浏览器接收评判模型密钥。Go API 复用现有 Admin 权限与 run_evaluations API key 能力。

Worker 无状态，不存储样本；最多同时评分两题，每个指标最多等待 50 秒。页面逐题请求，停止操作在当前题完成后生效。

## 指标

- faithfulness：回答是否得到所提供上下文支持。
- llm_context_precision_without_reference：以回答判断上下文相关性并计算排序精度；不能解释为完整问题证据的召回率。
- context_recall：仅在样本填写 reference 后运行。

失败指标单独返回 errors，不作为零分。模型版本与 Ragas 版本随结果返回。当前版本不提供评分理由，报告展示原始分数和错误。

## 样本

```json
[{"user_input":"问题","response":"实际回答","retrieved_contexts":["实际上下文"],"reference":"可选参考答案"}]
```

备份：backups/pre-ragas-verified-20261106-103058/source.zip，已执行 ZIP CRC 完整性校验；同目录包含 HEAD.txt 和 working-tree.patch。备份包含原有未提交修改，不要用 Git reset 覆盖既有工作。

## 2026-11-06 部署基线修正

实际运行源码位于 C:/Users/Win11/.codex/worktrees/weknora-082-upgrade/weknora-evaluation（HEAD 214ed452），包含产物库和工具箱。D:/weknora-evaluation 的 HEAD 3f930ab7 较旧，不能直接用于替换完整前后端，否则会丢失已有功能。当前 Ragas handler、路由、菜单和美化后的页面已移植到实际运行源码。

当前镜像：weknora-app:ragas-ui-fix-20261106 与 weknora-ui:ragas-ui-fix-20261106。部署和回滚脚本：backups/ragas-ui-fix-20261106/apply.py；--rollback 恢复原 Ragas 接入前的完整版本。构建、类型检查、Go handler 测试通过；独立无业务数据预览验证了布局与标签切换。生产页面登录态尚未人工验证；静态页面与产物/工具箱/评测资源返回 200，后端 healthy。

## 评判模型复用

评测页新增评判模型选择器，默认使用当前空间默认问答模型（无默认则首个可用问答模型）。浏览器仅发送 model_id；后端在当前租户内读取 API 地址、密钥和自定义请求头，并转发给受内部 token 保护的 Worker。当前 Worker 使用 OpenAI 兼容 Chat Completions 接口；原生 Anthropic/Gemini/Responses-only 模型暂不保证兼容。

Worker 当前在 Windows 本机运行，监听 127.0.0.1:8099。Docker 通过 host.docker.internal:8099 访问。Windows 重启后需运行 backups/ragas-model-config-20261106/start-worker.py。密钥不写入浏览器报告、不打印日志。

部署文件 backups/ragas-model-config-20261106/compose.ragas-model.json 含内部 token，请保密。实际评分可通过同目录 smoke.py 使用已有凭据执行合成样本验证，不创建知识库或对话。
