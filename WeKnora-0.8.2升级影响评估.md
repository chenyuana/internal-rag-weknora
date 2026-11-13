# WeKnora 0.8.0 → 0.8.2 升级影响评估

**针对对象**：`D:\weknora-evaluation` 的本地改动 + `D:\internal-rag` 里正在跑的 WeKnora 部署
**方法**：本地已取到上游 `v0.8.0` 与 `v0.8.2` 两个 tag，所有结论来自**真实三方 diff**（你的检出 ≠ v0.8.0 tag，见 §1），不是读 changelog 推演
**限制**：本机**无 Go 工具链、前端未构建** → 所有"是否冲突/是否编译得过"的判断是**diff 层面的**，不是编译验证过的。标 `[未验证]` 的部分必须在升级窗口里实际跑一遍

---

## 0. 结论（先看）

**能升，而且建议升——但这不是"改个版本号"，因为你的部署现在处于一个版本错位状态，升级前必须先把这个错位理清。**

三句话：

1. **你的代码基线不是 v0.8.0**。你的检出（`17f8938`，2026-09-13）比官方 `v0.8.0` tag 已经**领先 91,532 行 / 996 个文件**，并且**已经包含 0.8.2 的迁移 000091–000095**。所以从"你的代码"到 0.8.2，迁移只差 **000096–000110（15 个）**，不是 changelog 里写的 000091–000110（20 个）。
2. **你正在跑的那个镜像和它自己的数据库是错位的**。运行镜像 = 官方 v0.8.0 + 你 09-13 的二进制（`Dockerfile.app.mirror` 就是这个构造），但底层 Postgres 的 `schema_migrations = 90`，而**这个二进制自带迁移 91–95**。也就是说：**镜像里的迁移目录（90）与二进制期望的（95）差 5 个**，`dirty=f` 只是因为 91–95 恰好没有必须跑的 DDL 才没炸。这个错位在升级窗口里会变成真实麻烦（见 §4）。

   > ✅ **这条已开箱验证**（`docker run --rm --entrypoint sh wechatopenai/weknora-app:internal-rag`）：容器内 `/app/migrations/versioned` 的**最高号 = `000090`，共 182 个文件**；同一个二进制里 `strings /app/WeKnora | grep -c 'internal-rag'` = **3**（确认自研 integration 代码确实编进了这个二进制）。两者合起来就是"新二进制 + 旧迁移目录"的直接证据，不再是推断。
3. **你的 9 处改动里，只有 1 处是真正的语义冲突**（`knowledge_process.go` 的 `SkipPostProcess` 与上游新增的 `CompleteProcessingWithoutSubtasks` 撞了同一个目的），其余都是**文本层面可解的局部冲突**。工作量的大头不在解冲突，而在两件配套的事：**补 `SYSTEM_SIGNING_KEY`**，以及**把 ParadeDB 镜像从 0.22.2 升到 0.22.6**（顺序做反会让 `pg_search` 静默停在旧版本）。

---

## 1. 先纠正一个前提：你的基线到底是什么

这是本次评估最重要的一条，之前的底账（包括我上一轮写的那份）都把它说成"0.8.0 检出"，这是**不准的**。

| | 提交 | 迁移最高号 | 说明 |
|---|---|---|---|
| 官方发布的镜像 `v0.8.0` | `1edcd54b`（tag `v0.8.0`，镜像 label 实测） | **90**（镜像内实测：`000090` 最高，182 个文件） | 你容器的**运行时基底** |
| **你的代码基线** | `17f8938`（2026-09-13，"fix(memory): rank memories by the query"） | **95** | 你的补丁全都基于它 |
| 官方 `v0.8.2` | `3e8b0bfc`（tag `v0.8.2`） | **110** | 目标 |

实测三方 diff：

```
基线 17f8938 → v0.8.2 ：1964 files changed, 175410 insertions(+), 76369 deletions(-)
v0.8.0  → 你的基线   ： 996 files changed,  91532 insertions(+), 16292 deletions(-)
```

**为什么这条重要**：`git diff v0.8.0 你的基线` 有 9 万行——你已经"免费"吃掉了 0.8.1/0.8.2 周期里相当一部分改动（迁移 91–95、BrowserSkill 的 release 清单等）。所以：

- **好消息**：0.8.2 的迁移里 91–95 你已经有了，而且**逐字节与上游相同**（我比过 5 个文件的 blob hash，全部 `相同`）→ **这部分零冲突**。
- **坏消息**：你的部署把"新代码"和"旧镜像基底"拼在了一起，`/app/migrations` 来自旧基底。这决定了升级步骤不能简单"pull 新镜像"。

---

## 2. 你的"改动"完整清单（15 项，分三类）

之前只知道有几个未跟踪文件；实际是**三类共 15 项**。全部实测来源：`git status --short` + `git diff --stat`。

### 一类：已提交的本地补丁（2 个 commit，14 个文件，约 2,178 行）

**`8e9b808` internal-rag 集成（1,254 行）**

| 文件 | 规模 | 性质 |
|---|---|---|
| `internal/application/service/knowledge_internal_rag.go` | +174 | **纯新增** |
| `internal/application/service/knowledge_internal_rag_test.go` | +34 | 纯新增 |
| `internal/types/internal_rag.go` | +46 | 纯新增 |
| `internal/application/service/knowledge_process.go` | +14/−1 | **改既有函数** |
| `internal/handler/knowledge.go` | +35 | 加 handler |
| `internal/router/routes_knowledge.go` | +1 | 加路由 |
| `RETRIEVAL_ANALYSIS.md`、`docs/api/knowledge.md` | +951 | 文档 |

**`3f930ab` 数字命名文档召回修复（924 行）**

| 文件 | 规模 | 性质 |
|---|---|---|
| `internal/application/service/knowledgebase_search_exact.go` | +303 | **纯新增** |
| `internal/application/service/knowledgebase_search_exact_test.go` | +363 | 纯新增 |
| `internal/application/service/knowledgebase_search.go` | +20 | **重构既有函数** |
| `internal/application/service/chat_pipeline/search.go` | +2 | 改既有 |
| `internal/types/search.go` | +7/−1 | 改既有 |
| `scripts/verify-ac-number-recall.ps1` | +230 | 脚本 |

### 二类：未提交的工作区改动（5 个文件，25 行）

| 文件 | 改动 |
|---|---|
| `config/config.yaml` | `max_completion_tokens: 2048 → 8192` + 注释（**这是运行时挂载的**，见 §4 风险） |
| `internal/types/search.go` | `+RelatedImages []RelatedImage` 字段、`gorm:"-"`（不落库） |
| `internal/application/service/session_knowledge_qa.go` | +1 行：`s.attachRelatedImages(ctx, chatManage.MergeResult)` |
| `frontend/.../AgentStreamDisplay.vue` | +6：插 `<RelatedReferenceImages>` + import |
| `frontend/.../botmsg.vue` | +5：同上 |

### 三类：未跟踪的新增文件（9 项）

`internal/application/service/related_images.go`（+100，含测试）、`frontend/src/components/RelatedReferenceImages.vue`、`frontend/src/utils/relatedReferenceImages.ts`（+测试）、`docker/Dockerfile.app.mirror`、`frontend/Dockerfile.mirror`、`backups/`、`notes/`。

**这三类里，真正有升级风险的只有 4 个文件**：`knowledge_process.go`、`knowledgebase_search.go`、`AgentStreamDisplay.vue`、`config/config.yaml`。其余都是纯新增或上游没碰。

---

## 3. 逐文件冲突判定（这是你要的核心表）

我跑了 `git diff 17f8938 upstream-v0.8.2 -- <你的每个改动文件>`。判定依据：**上游是否改了同一区域**。

| 你的改动文件 | 上游 0.8.2 是否动过 | 上游改动规模 | 冲突判定 | 依据 |
|---|---|---|---|---|
| `internal/types/search.go` | ❌ **未动** | — | ✅ **零冲突** | 上游 0.8.2 完全没碰这个文件；你加的 `RelatedImages` 只有本地用 |
| `internal/application/service/chat_pipeline/search.go` | ❌ **未动** | — | ✅ **零冲突** | 同上 |
| `knowledgebase_search_exact.go`（新增） | ❌ 上游无此文件 | — | ✅ **零冲突** | 纯新增，`git ls-tree upstream-v0.8.2` 为空 |
| `knowledge_internal_rag.go`、`internal_rag.go`、`related_images.go`、组件与 utils（新增） | ❌ 上游无 | — | ✅ **零冲突** | 纯新增；且我检查过它们**没有调用** 0.8.2 改过签名的 API（无 `.Embed(`、无旧工具名） |
| `internal/router/routes_knowledge.go` | ✅ 动过 | +5 行 | ✅ **低**（同文件不同区域） | 你加的是 `kb.POST("/internal-rag", ...)`，插在既有 `kb` 组的一串 POST 中间；上游这 5 行加在别处 |
| `internal/handler/knowledge.go` | ✅ 动过 | +224/−9 | ⚠️ **中** | 同文件大改，但你的是新增 handler 方法 + 一个本地 `internalRAGImporter` 接口，不碰上游改的函数体 |
| `internal/application/service/knowledgebase_search.go` | ✅ 动过 | **+2/−2** | ⚠️ **中（唯一的真 API 变化）** | 上游把两处 `embeddingModel.Embed(ctx, ...)` 改成 `Embed(types.WithEmbedQuery(ctx), ...)`。你把这个函数**重构出了 `hybridSearch(ctx, id, params, recallNamedDocuments bool)` 包装**。上游没做这个重构（实测：上游只有 `HybridSearch`@L125 和 `resolveQueryEmbedding`@L480，**没有 `hybridSearch`**），所以你的 wrapper 会保留，但你 wrapper 内部调用的路径要跟着适配新签名 |
| `internal/application/service/knowledge_process.go` | ✅ 动过 | **+456/−80** | 🔴 **高（语义冲突）** | 见下 |
| `frontend/.../AgentStreamDisplay.vue` | ✅ 动过 | **+89/−343** | 🔴 **高（上游重写）** | 见下 |
| `frontend/.../botmsg.vue` | ✅ 动过 | +88/−13 | ⚠️ **中** | 你的插入点（`renderedHTML` 之后、`answer-toolbar` 之前）和 prop（`session.knowledge_references`）**上游都还在**（实测 `knowledge_references` 上游仍有 3 处），但文件有 88 行新增需要 rebase |

### 3.1 🔴 唯一的语义冲突：`SkipPostProcess` vs `CompleteProcessingWithoutSubtasks`

你的补丁在 `knowledge_process.go:694` 手动把文档直接标成完成：

```go
if options.SkipPostProcess {
    knowledge.ParseStatus = types.ParseStatusCompleted
    knowledge.PendingSubtasksCount = 0
    knowledge.SummaryStatus = types.SummaryStatusNone
    knowledge.ErrorMessage = ""
}
```

而 0.8.2 **在同一个问题上做了上游自己的解法**，而且更严谨：

- 新增仓库方法 `CompleteProcessingWithoutSubtasks(ctx, id)`，注释写明是"**原子地**完成一个仍在 processing、且没有 enrichment 任务的文档，**不覆盖 cancel/delete**"
- 并给 `KnowledgeService` 接口加了 `ReplaceKnowledgeFile`、`KnowledgeRepository` 加了 `ListKnowledgeProfileRows` 等新方法
- 上游同文件里已有 `knowledge.PendingSubtasksCount = 0`（L2911）和 `existing.PendingSubtasksCount = 0`（L2982）的正确路径

**这条是好事**：上游 0.8.2 恰好修了**嵌入式收文档最痛的那个问题**——changelog 的 Bug Fixes 第一条就是 *"Documents no longer get stranded in `processing` or `deleting`"*。你的 `SkipPostProcess` 是在绕开这个 bug。

**升级动作**：不要机械合并。应该**用上游的原子语义重写你的 `SkipPostProcess`**（调用 `CompleteProcessingWithoutSubtasks`），否则你会保留一个绕过 cancel/delete 的竞态。这需要读懂那 456 行新增，是本次升级**唯一需要真正动脑的地方**。

> 附带澄清：0.8.2 给 `KnowledgeService` 接口加了方法，**不会**导致你编译失败——你的 `knowledge_internal_rag.go` 实现的是**具体类型** `*knowledgeService` 的方法（实测无 `var _ KnowledgeService =` 断言），handler 侧用的是本地小接口 `internalRAGImporter`。上游自己补了实现。✅

### 3.2 🔴 前端：一个 213 行的"消失"

`AgentStreamDisplay.vue`：上游 0.8.2 是 **3573 行**，你的是 **3786 行**——**你的比上游多 213 行**。

我一开始以为是你自己加的，实测不是：**本地 HEAD 相对基线对该文件零改动**，那 213 行差**全部来自上游 0.8.2 的删减**（该文件 `−343/+89`）。也就是说上游重构时**从你这份文件里移走了 213 行**（很可能拆到新的 tool-results 组件里——上游同时新增/改动了 40+ 个 `chat/components/**` 文件）。

- **好消息**：你的插入点上下文**幸存**——上游在 L385 仍有 `answerFullyRendered && event.done …` + `class="answer-toolbar"`，与你插入点前的位置一模一样。所以 `<RelatedReferenceImages>` 那个 hunk 大概率能文本干净地落下去。
- **坏消息**：你不止插了一处。`botmsg.vue` 也插了；而上游 0.8.2 新增了 **`ChatReferencesDrawer.vue`** + `css/chat-citations.less` + 配套测试——**你要评估"相关引用图"是否应该改为挂进这个新的引用抽屉，而不是继续贴在答案下方**。否则升完级你会发现引用有两套 UI 入口。
- 你的组件没有撞名（上游 `frontend/src/components/` 下无 `RelatedReferenceImages.vue`）。✅

---

## 4. 升级窗口里必须处理的 6 个具体事项

### ① `SYSTEM_SIGNING_KEY` 缺失 —— 必须补

0.8.2 的 BREAKING 明确：`.env.example` 不再提供默认密钥，新增 `SYSTEM_SIGNING_KEY`。实测：

| 变量 | 你的 `.env` | 结论 |
|---|---|---|
| `JWT_SECRET` | 已设，长度 31 | ⚠️ 偏短，官方示例要求 32 字节（`openssl rand -hex 32` 是 64 个 hex 字符）。**不要动它**——动了所有人重新登录 |
| `SYSTEM_AES_KEY` | 已设，长度 31 | 🔴 **绝对不能改**。changelog 原文：*"existing deployments must keep their current `SYSTEM_AES_KEY`, or stored credentials cannot be decrypted"* → 改了模型 API Key、MCP 凭据、数据源凭据**全部解不开** |
| `SYSTEM_SIGNING_KEY` | ❌ **缺失** | 🔴 **必须补**。用途实测在 `cmd/desktop/signing_key.go` 与 `internal/application/service/embed_session*`（嵌入挂件会话签名）。缺失不一定会启动失败，但嵌入相关功能会退化 `[未验证]` |

### ② `WEKNORA_VERSION` 必须改

你的 `.env` 里 `WEKNORA_VERSION=internal-rag`，而 `docker-compose.yml` 有 **4 处**引用它拼镜像名（`wechatopenai/weknora-app:${WEKNORA_VERSION}` / `weknora-ui:${WEKNORA_VERSION}`）。不改这个，`docker compose pull` 会去拉一个不存在的 tag。应改为新 tag（例如 `0.8.2` 或你自己的 `internal-rag-082`）。

### ③ ParadeDB 镜像从 `v0.22.2` 升到 `v0.22.6` —— 一个"静默漏掉"的坑

当前真实状态（实测，**两边是一致的**，所以现在没问题）：

| | 值 |
|---|---|
| 你的 `docker-compose.yml:522,800` | `paradedb/paradedb:v0.22.2-pg17` |
| 运行中的 postgres 扩展 | `pg_search = 0.22.2` |
| 你的 tree 里最新迁移 | `000095`（**没有** 000099） |

升级后会引入一组新东西：**迁移 `000099_pg_search_0226.up.sql` + compose 把镜像钉到 `v0.22.6-pg17`**。而那条迁移**设计得很保守**：只在 `installed_version ∈ {0.22.2…0.22.5}` **且服务器提供 0.22.6** 时才执行 `ALTER EXTENSION`；否则 **`RAISE NOTICE` 然后 `RETURN`**。

**这意味着什么**（本次升级最容易踩的坑）：

> 如果你在升级窗口里**只换了 app 镜像、没换 postgres 镜像**：迁移 000099 在 0.22.2 服务器上找不到 0.22.6，于是**打印一条 NOTICE 就返回**——迁移算作**成功**，`schema_migrations` 推进到 110。**等你过几天换镜像再重启，AUTO_MIGRATE 看到 110 已应用，不会再跑它** → `pg_search` **永远停在 0.22.2**，而且没有任何报错。迁移注释原话就在描述这个操作：*"update the server image and run `ALTER EXTENSION pg_search UPDATE TO '0.22.6'` manually"*。

**正确顺序**：先 `docker compose pull postgres` 并重启 postgres → 确认 `pg_available_extension_versions` 里有 0.22.6 → **再**上新的 app 镜像（让 000099 在正确的服务器上跑）；若已经做反了，手动补 `ALTER EXTENSION pg_search UPDATE TO '0.22.6'`。

### ④ `config/config.yaml` 是你唯一的 bind-mount 配置文件，而它**和上游 0.8.2 在相邻位置改了相反的值**

实测两边都改了这一段：

```
上游 0.8.2：  max_input_chars: 16384 → 8192      max_completion_tokens: 2048 → 1024
你的改动：    （未动 max_input_chars）            max_completion_tokens: 2048 → 8192
```

你的注释写明原因（值得保留）：*"2048 was too small once retrieval context grew: with a reasoning model the whole budget went to reasoning_content and the answer came back empty (observed prompt_tokens=46260 / completion_tokens=2048 / empty message)"*。

**必须做的判断**：上游把 `max_completion_tokens` **往下调到 1024**，理由是文档 profile 生成只需要摘要；而你是**往上调到 8192**，理由是答案生成为空。这**不是同一个用途吗？** 需要你确认——上游这段在 `conversation.summary` 下（摘要用途），如果确实只是摘要，那**你的 8192 注释可能挂错了配置块**，而真正管答案长度的是另一处。`[未验证]`，但这值得在升级前花 10 分钟确认，因为它直接关系到你"答案返回空"那个 bug 到底修在哪一层。

**注意**：这个文件是 `./config/config.yaml:/app/config/config.yaml` **bind-mount 进容器**的。所以升级镜像**不会**覆盖它——你的改动会保留，但你也**不会自动拿到上游对新配置项的期望值**。升级后建议对着 0.8.2 的 `config.yaml` 做一次逐项 diff。

### ⑤ 迁移 `000106` 有一个运维要求

changelog 原文：*"Migration `000106` builds an index `CONCURRENTLY`; if interrupted, drop the invalid index and rerun."* 你之前遇到过 RAGFlow 僵死要重启整机的情况——**如果这个索引构建中途被打断，你会得到一个 invalid index，且迁移会卡住**。升级窗口要留出时间，不要在急着交付的当天做。

### ⑥ 0.8.2 顺手修了三处**与你已知痛点直接相关**的东西

| 0.8.2 修的 | 为什么对你有用 |
|---|---|
| *"inline HTML tables no longer produce oversized chunks"* | 我在上一轮评估里指出过：WeKnora 从 MinerU 取回 HTML `<table>` 后，`<table>` **不在分片保护模式里**，大表会被切开且不补表头。**0.8.2 修了这个**（虽然只是表格问题的一部分——PDF 表格恢复、合并单元格、人工复核门禁仍然没有） |
| *"Documents no longer get stranded in `processing` or `deleting`"* | 正好是你 `SkipPostProcess` 在绕的那个 bug（见 §3.1） |
| *"timed-out converter process groups are killed"* + `WEKNORA_PADDLEOCR_VL_TIMEOUT` | 解析器挂死会留僵尸进程——对你的批处理场景有用 |

**外加一个对"数据不出内网"直接有用、但你现在没开的功能**：`SSRF_DNS_WHITELIST_ONLY`（实测存在于 `internal/container/container.go:1276,1290`、`internal/infrastructure/web_fetch/fetcher.go:270,315`、`internal/utils`）。它要求**任何不在 `SSRF_WHITELIST` 里的主机在 DNS 解析之前就被拒绝**，changelog 明确说这是为了 *"closing DNS-based exfiltration from offline deployments"*。你的 `.env` 里没有这个变量（`.env.example` 也没有）→ **需要手动加**。对一个要做内网隔离的无人机公司，这是本次升级**最值得拿的一个新能力**。

**注意**：它**不会**顺便解决你的重排注册问题——`host.docker.internal` 仍然要显式写进 `SSRF_WHITELIST_EXTRA`（这是升级之外的独立动作，别指望升级帮你修好那个 25% 页码命中率）。

---

## 5. ⚠️ 会打到你评测结论上的影响（这条容易被忽略）

0.8.2 把**智能体检索工具整套重命名并重构**了：

| 0.8.0 / 你的版本 | 0.8.2 |
|---|---|
| `knowledge_search`、`grep_chunks` | → 合并为 **`search_knowledge`**（候选池默认 10、上限 30；keyword 模式改走 BM25 索引，不再全表正则） |
| `list_knowledge_chunks`、`get_document_info`、`wiki_read_source_doc` | → 合并为 **`read_document`** |
| 新增 | `list_documents`、`discover_mcp_tools` / `call_mcp_tool` |

对本项目的具体后果：

1. **你的 `weknora-eval` 那 71 题基线，是在旧工具名下跑的。** 0.8.2 有**向后兼容别名**（`legacyToolSuccessors` / `NormalizeAllowedTools`，我实测本地版本**没有**这两个符号 → 属 0.8.2 新增），所以 `builtin_agents.yaml` 不会炸、历史会话仍能渲染。但这意味着**升级后检索工具的实际行为变了**。
2. **升级会再次移动基线**：0.8.2 还改了 *"history is sized by the model's context window with calibrated token estimates"*、*"`search_knowledge` reranks with document titles and allows a keyword retry after a rerank rejection"*——**这两条都直接作用在检索/上下文组装上**，也就是你那个 25% 页码命中率的测量对象。
3. **所以：升级后必须重跑那 71 题，并且把 `agent_id` 记进 manifest。** 我上一轮指出的问题在这里变成硬要求——你的 `runs/baseline/manifest.json` **没有记录 `agent_id`**，而 `run_eval.py` 默认 `builtin-quick-answer`（`vector_threshold 0.5` / `embedding_top_k 10` / 改写+扩展全开），**与租户默认值差别很大**。升级前后两次测量如果连 agent 都不一样，任何对比都是假的。

**建议**：升级、修 SSRF、注册重排器、钉死 `agent_id` 这四件事**放在同一个窗口里做完，然后只跑一次评测**。分两次做等于浪费一次评测预算。

---

## 6. 0.8.2 的"大功能"里，哪些跟你有关

changelog 里 0.8.2 篇幅最大的是 BrowserSkill（本地浏览器）、Sandbox 终端/图形桌面、Artifacts 库、Lite 宿主沙箱、模型目录（27 家厂商）——**这些对一个内网知识库基本无关，而且它们大多是把攻击面和资源占用往上加的**（app 镜像要打包 `bsk` daemon、Sandbox 默认以 root 运行）。真正的 BREAKING 清单里，与你相关的只有两条：

| BREAKING | 对你的实际影响 |
|---|---|
| `.env` 密钥变更（不再提供默认值、新增 `SYSTEM_SIGNING_KEY`） | 🔴 **相关**，见 §4① |
| **钉钉渠道只支持 Stream 模式**（迁移 `000096` 会把现有 webhook 渠道改成 `websocket`） | 🟡 **看情况**：如果你没用钉钉，000096 对你无害；如果用了，升级后必须去钉钉开发者后台启用 Stream，否则渠道**静默失效** |
| Sandbox 命令默认以 `root` 运行 | 🟢 你的 `.env` 没开 Docker 沙箱 → 无关 |
| 组织邀请改为按精确 workspace ID 解析（按名字搜索被移除） | 🟡 多空间协作体验变化，需在 UI 上确认 |
| Go SDK `UpdateAgentRequest.Avatar` 变 `*string` | 🟢 你不用 SDK 就无关 |

---

## 7. 建议的升级路线（含回滚点）

**不要走"fork 出 0.8.2 再手补我的改动"这条路**——上游 0.8.2 是在 `main` 上的大幅重构（175,410 行插入），你的 9 处改动散落在 5 个被大改的文件里，手补容易漏。

**推荐：把补丁 rebase 到官方 v0.8.2 上，保持"薄补丁"姿态。**

| 步骤 | 动作 | 验收 |
|---|---|---|
| **0. 冻结与备份** | 备份 Postgres（`pg_dump`）、`config/config.yaml`、`.env`、`/data/files` 卷、`wechatopenai/weknora-app:internal-rag` 镜像（`docker save`） | 有可回滚镜像 tag + dump 文件 |
| **1. 建分支 rebase** | 从 `upstream-v0.8.2` 建分支，`git cherry-pick 8e9b808 3f930ab`，再单独提交工作区那 5 个文件的改动 | `git status` 干净；**记录每一处人工解的冲突** |
| **2. 先修语义冲突** | 用上游 `CompleteProcessingWithoutSubtasks` 重写 `SkipPostProcess`（§3.1）；确认 `config.yaml` 的 `max_completion_tokens` 归属（§4④） | 代码审阅通过 |
| **3. 前端 rebase** | `AgentStreamDisplay.vue` / `botmsg.vue` 按上游新结构重挂；**决定**相关引用图是留在答案下方还是并入新的 `ChatReferencesDrawer` | 前端能构建、引用图正常显示 |
| **4. 补密钥与变量** | `.env`：加 `SYSTEM_SIGNING_KEY`（`openssl rand -hex 32`）；**确认 `SYSTEM_AES_KEY` 一个字符都不动**；`WEKNORA_VERSION` 改新 tag；加 `SSRF_DNS_WHITELIST_ONLY=true` 并把内网主机写进白名单 | 容器启动、凭据仍可解密（能调通一个已存的模型连接） |
| **5. 换 ParadeDB 镜像** | 先 `docker compose pull postgres` 到 v0.22.6-pg17，**再**上新的 app 镜像；若顺序做反，手动补 `ALTER EXTENSION pg_search UPDATE TO '0.22.6'` | `select extversion from pg_extension where extname='pg_search'` = **0.22.6** |
| **6. 迁移与观察** | 起服务，盯着迁移跑到 110；留意 000106 的 CONCURRENTLY 索引 | `schema_migrations = 110, dirty=f`；`docker logs` 不再只打印 `json`（顺手修掉那个日志编码器 bug） |
| **7. 修重排 + 钉 agent** | `SSRF_WHITELIST_EXTRA` 加 `host.docker.internal` → 注册 `qwen3-reranker-0.6b` → 在 `run_eval.py` 里固定 `agent_id` | 重排真的跑了（日志可见） |
| **8. 重跑 71 题** | 一次跑完，记进 `CHANGELOG-params.md` | 与 09-23 基线可比（前提是 agent_id 一致） |
| **9. 更新 `.mirror` 构建** | `Dockerfile.app.mirror` 的基底 tag 与新版本对齐；注意 0.8.2 的 `docker/Dockerfile.app` 已改用 `scripts/copy-licenses.sh` 且**删掉了 `patches/browserskill`** | 镜像能构建成功 |

**回滚**：第 5 步之前都是可逆的（换回旧镜像 tag + 让 Postgres 回到旧镜像）。**第 5 步之后 ParadeDB 镜像升级是不可逆的**（扩展版本不能降级），所以第 5 步要留足时间窗。

---

## 8. 一句话答复

> **值得升，而且这次升级能白拿三样对你直接有用的东西**：`SSRF_DNS_WHITELIST_ONLY`（内网出站白名单，DNS 解析前拒绝）、"文档卡在 processing/deleting"的修复（正好替掉你那个 `SkipPostProcess` 绕法）、以及 HTML 大表被切碎的修复。
> **但代价不是"改版本号"**：你的部署正处在"新二进制 + 旧镜像基底"的错位状态（镜像里迁移到 90，二进制要到 95），升级要先把这件事理平；真正的语义冲突只有 1 处；**最容易踩的坑是 ParadeDB 0.22.2→0.22.6 的升级顺序**——顺序做反，`pg_search` 会静默停在 0.22.2；**最容易漏的是 `SYSTEM_SIGNING_KEY`**。
> **另外记住**：0.8.2 重构了智能体检索工具（`knowledge_search` → `search_knowledge`）并改了上下文/重排行为——**升级会移动你那次 71 题评测的基线**，所以升级后必须重跑，并且先把你 manifest 里缺失的 `agent_id` 钉死。

---

## 附：本次评估用到的权威来源

| 来源 | 用途 |
|---|---|
| `git diff 17f8938 upstream-v0.8.2`（本地已 fetch 到 `v0.8.0` / `v0.8.2` tag） | 三方 diff、逐文件冲突判定 |
| `git show upstream-v0.8.2:migrations/versioned/000099_pg_search_0226.up.sql` | ParadeDB 顺序陷阱 |
| `docker image inspect wechatopenai/weknora-app:internal-rag` | 实跑镜像 = v0.8.0（revision `1edcd54b`）+ 09-13 二进制 |
| `docker exec WeKnora-postgres psql ... select version,dirty from schema_migrations` | 运行时 schema = **90** |
| `docker run --rm --entrypoint sh wechatopenai/weknora-app:internal-rag`（开箱实测） | 镜像内迁移最高 = **`000090`**（182 文件）；二进制含 `internal-rag` 字符串 3 处 → 证实"新二进制 + 旧迁移目录"错位 |
| `docker ps` / `docker images` | 运行状态、镜像代际、ParadeDB 版本 |
| `D:\weknora-evaluation\CHANGELOG.md` + 在线 `CHANGELOG.md` | 0.8.2 变更清单（本地 CHANGELOG 只到 0.8.0） |
| `D:\internal-rag\weknora-eval\runs\baseline\manifest.json` | `agent_id` 缺失 → 评测基线不可比 |
