# WeKnora v0.8.0 检索链路深度分析（机制面 · 证据优先）

> 所有结论均以 `path:line` 为证。标注约定：**【代码】**=直接读到的事实；**【文档】**=仓库文档所述（可能与代码不一致）；**【推断】**=基于代码的分析判断。
> 代码基准：`D:\weknora-evaluation`（VERSION=v0.8.0）。

---

## 0. TL;DR — 与 RAGFlow 对比前必须先知道的 7 件事

| # | 事实 | 证据 |
|---|---|---|
| 1 | **存在两套互不相通的检索默认值**：会话/Agent 管线读 `config.yaml conversation.*`；独立的 `/knowledgebase/{id}/search` 与 Agent `knowledge_search` 工具读 `tenant.RetrievalConfig`（另一组默认值）。 | `internal/application/service/session_knowledge_qa.go:114-118`；`internal/application/service/session_knowledge_qa.go:853-857`；`internal/types/retrieval_config.go:44-109` |
| 2 | **关键词阈值（KeywordThreshold）在主引擎里基本不生效**：Postgres / SQLite / ES v8 / Qdrant / Milvus 的 `KeywordsRetrieve` 都不读 `params.Threshold`；Qdrant 与 Milvus 直接把关键词分数硬编码为 `1.0`。 | `postgres/repository.go:164-226`；`sqlite/repository.go:289-315`；`elasticsearch/v8/repository.go:485-506`；`qdrant/repository.go:694`；`milvus/repository.go:791` |
| 3 | **融合是加权 RRF**，k 默认 60，权重默认 vector 0.7 / keyword 0.3，可在租户级配置。 | `knowledgebase_search_fusion.go:84-128`；`retrieval_config.go:86-109` |
| 4 | **没有通用自适应 top-k**：唯一的"先少后多"是 FAQ 类型的迭代翻倍检索（最多 5 轮，上限 500）。 | `knowledgebase_search_faq.go:73-211` |
| 5 | **`config.yaml` 的 `enable_rerank` 是全代码库唯一出现处，从未被读取**。是否重排实际由 `RerankModelID` 是否为空决定。 | `config/config.go:105`（唯一定义）；`chat_pipeline/rerank.go:57-62`；全仓 grep `EnableRerank` 仅 1 处命中 |
| 6 | **上下文组装阶段没有 token 预算**。最终进入 LLM 的 chunk 数由 `RerankTopK` 与去重/合并决定，只有"扩展近邻"的单 chunk 850 rune 上限。 | `chat_pipeline/filter_top_k.go:41-51`；`chat_pipeline/merge_expand.go:16-19,254-267`；`chat_pipeline/into_chat_message.go:121-172` |
| 7 | **召回层没有文档级/用户级 ACL**。过滤维度只有 `knowledge_base_id` / `knowledge_id` / `tag_id` / `is_enabled`；ACL 在 KB 粒度事后校验。 | `postgres/repository.go:174-207,300-335`；`knowledgebase_search.go:170`；`knowledgebase_search_shared.go:45-55,83-95` |

---

## 1. 端到端管线（Plugin / Event 模型）

### 1.1 事件链组装（RAG 路径）

```
LOAD_HISTORY(可选) → MEMORY_RECALL → QUERY_UNDERSTAND → CHUNK_SEARCH_PARALLEL
   → CHUNK_RERANK → WEB_FETCH(可选) → CHUNK_MERGE → FILTER_TOP_K
   → DATA_ANALYSIS(可选) → INTO_CHAT_MESSAGE → CHAT_COMPLETION_STREAM
```

- 组装点：`internal/application/service/session_knowledge_qa.go:194-206`
  ```go
  pipeline = types.NewPipelineBuilder().
      AddIf(hasHistory, types.LOAD_HISTORY).
      Add(types.MEMORY_RECALL).
      Add(types.QUERY_UNDERSTAND).
      Add(types.CHUNK_SEARCH_PARALLEL).
      Add(types.CHUNK_RERANK).
      AddIf(req.WebSearchEnabled, types.WEB_FETCH).
      Add(types.CHUNK_MERGE).
      Add(types.FILTER_TOP_K).
      AddIf(chatManage.DataAnalysisEnabled, types.DATA_ANALYSIS).
      Add(types.INTO_CHAT_MESSAGE).
      Add(types.CHAT_COMPLETION_STREAM).
      Build()
  ```
- 纯聊天路径（无 KB 且未开 Web）：`LOAD_HISTORY? → MEMORY_RECALL → CHAT_COMPLETION_STREAM`（`:187-191`）。
- 判定 `needsRAG = hasKB || req.WebSearchEnabled`（`:167-168`）。

### 1.2 插件注册顺序 = 同事件内的执行顺序

关键在于 `EventManager.Register` 是 **append + 重建责任链**，因此同事件下先注册者在外层、先执行；`next()` 调用后者：

- `chat_pipeline/chat_pipeline.go:40-68`
  ```go
  e.listeners[eventType] = append(e.listeners[eventType], plugin)
  e.handlers[eventType] = e.buildHandler(e.listeners[eventType])
  // buildHandler 从后往前包裹，因此 listeners 顺序 = 执行顺序
  ```
- 容器注册顺序：`internal/container/container.go:379-396`

由此推出的**实际同事件顺序**：

| EventType | 插件（按注册=执行顺序） | 证据 |
|---|---|---|
| `CHUNK_RERANK` | `PluginRerank` → `PluginWikiBoost` → `PluginMemoryAffinity`（后两者都先 `next()` 再做事，所以"后置加工"顺序与注册顺序一致，**MemoryAffinity 的 stable sort 在最外层、是最后一次重排**） | `container.go:381,395,396`；`wiki_boost.go:48-51`；`memory_affinity.go:62-64` |
| `QUERY_UNDERSTAND` | `PluginQueryUnderstand` → `PluginExtractEntity`（ExtractEntity 不做前置，故在重写之后） | `container.go:389,392`；`extract_entity.go:51-53` |
| `CHUNK_SEARCH` | `PluginSearch`（`CHUNK_SEARCH_PARALLEL` 内部直调，不注册） | `search_parallel.go:49-59,120` |
| `ENTITY_SEARCH` | `PluginSearchEntity`（**注册了但永不被 Trigger**——不在任何组装出的 pipeline 里；实际调用是 `search_parallel.go:140` 直调内部未注册实例） | `container.go:393`；`search_parallel.go:140` |

> **【文档 vs 代码】** `website-docs/02-architecture/04-rag-pipeline.md:104` 把 `chunk_rerank` 写成 `PluginRerank → PluginWikiBoost`，**漏了 `PluginMemoryAffinity`**；`:76-93` 的注册清单也漏了 `NewPluginMemoryRecall` / `NewPluginMemoryAffinity`，且未说明 SearchEntity 注册后不被触发。

### 1.3 CHUNK_SEARCH_PARALLEL：检索的真正入口

`chat_pipeline/search_parallel.go:90-179`

1. 意图级短路：`if !chatManage.NeedsRetrieval() { return next() }`（`:94-100`）。`NeedsRetrieval` 依赖 `Intent`，空值视为需要检索（`types/chat_manage.go:102-109`）。
2. 两条任务**并行**执行（`RunParallel`，`:116-153`）：
   - `chunk_search` → `PluginSearch.OnEvent(CHUNK_SEARCH)`
   - `entity_search` → 仅当 `len(chatManage.Entity) > 0`（`:134-139`）
3. 合并：`append(chunkCM.SearchResult, entityCM.SearchResult...)` 后 `removeDuplicateResults`（`:156-157`），仅按 chunk ID + 内容签名去重，**不按 ParentChunkID 去重**（`search.go:183-207`）。
4. 全部为空 → `ErrSearchNothing`（`:171-176`）。

### 1.4 CHUNK_SEARCH 内部（`search.go`）

`chat_pipeline/search.go:62-163`

1. `hasKBTargets || WebSearchEnabled` 否则报 `kb_not_found`（`:66-76`）。
2. **两个 goroutine 并行**：KB 检索 + Web 检索（`:98-122`）。
3. **低召回触发的查询扩展**（`:141-146`）：
   ```go
   if chatManage.EnableQueryExpansion && len(chatManage.SearchResult) < max(1, chatManage.EmbeddingTopK) {
       expResults := p.runQueryExpansion(ctx, chatManage)
   ```
   即：召回数 < EmbeddingTopK（默认 30，见 §2）时，追加变体检索结果（**不是替换、不是重试更大 k**）。
4. 仍为空 → `ErrSearchNothing`（`:162`）。

---

## 2. Query→Params：完整参数集与默认值（问题 1）

### 2.1 三条入口，三套默认值 ⚠️

| 入口 | 参数来源 | Vector Threshold | Keyword Threshold | EmbeddingTopK | RerankTopK | RerankThreshold |
|---|---|---|---|---|---|---|
| **会话/Agent RAG 管线** | `config.yaml conversation.*` | **0.2** | **0.3** | **30** | **30** | **0.3** |
| **`/knowledgebase` search / message search** | `tenant.RetrievalConfig`（JSONB） | 0.15（nil 时） | 0.3 | 50（`DefaultRetrievalTopK`） | 10 | 0（nil 时 0.2） |
| **Agent 工具 `knowledge_search`** | 全局 config → 硬编码兜底 | 0.6（硬编码） | 0.5（硬编码） | 5（硬编码） | —（用 topK） | 0.3（agent 侧兜底） |
| **Custom Agent 默认值（`EnsureDefaults`）** | `types/custom_agent.go` | **0.5** | **0.3** | **10** | **5** | **0.5** |
| **DB 迁移历史默认（sessions 表）** | `migrations/versioned/000000_init.up.sql:139-144` | **0.5** | **0.5** | **10** | **10** | **0.65** |

证据：

- 会话管线（第一行）：
  - `internal/application/service/session_knowledge_qa.go:105-118`
    ```go
    VectorThreshold:  s.cfg.Conversation.VectorThreshold,
    KeywordThreshold: s.cfg.Conversation.KeywordThreshold,
    EmbeddingTopK:    s.cfg.Conversation.EmbeddingTopK,
    RerankTopK:       s.cfg.Conversation.RerankTopK,
    RerankThreshold:  s.cfg.Conversation.RerankThreshold,
    ```
  - 默认值定义：`config/config.yaml:9-21`
    ```yaml
    conversation:
      max_rounds: 5
      keyword_threshold: 0.3
      embedding_top_k: 30
      vector_threshold: 0.2
      rerank_threshold: 0.3
      rerank_top_k: 30
      enable_rewrite: true
      enable_query_expansion: true
      enable_rerank: true      # ← 从未被读取，见 §10
    ```
  - 结构体字段：`internal/config/config.go:96-105`
- 独立搜索/消息搜索（第二行）：
  - `internal/application/service/session_knowledge_qa.go:845-858`（`SearchKnowledge` 路径）
  - `internal/application/service/message.go:665`（`MatchCount: rc.GetEffectiveEmbeddingTopK()`）
  - 默认常量与取值函数：`internal/types/retrieval_config.go:14-38,40-109`
    - `DefaultRetrievalTopK = 50`（`:44`）
    - `GetEffectiveVectorThreshold()` → `0.15`（`:55-60`）
    - `GetEffectiveKeywordThreshold()` → `0.3`（`:63-68`）
    - `GetEffectiveRerankTopK()` → `10`（`:71-76`）
    - `GetEffectiveRerankThreshold()` → `0.2`，但**仅在 `c == nil` 时**；`c != nil && RerankThreshold == 0` 会原样返回 `0`（`:79-84`）
- Agent 工具（第三行）：
  - `internal/agent/tools/knowledge_search.go:238-260`
    ```go
    if topK == 0 { topK = 5 }
    if vectorThreshold == 0 { vectorThreshold = 0.6 }
    if keywordThreshold == 0 { keywordThreshold = 0.5 }
    if minScore == 0 { minScore = 0.3 }
    ```
  - `minScore` 随后被显式放弃：**"minScore filter is skipped because HybridSearch now uses RRF scores"**（`:345-347`）
  - Agent 侧 rerank 阈值兜底 `0.3`：`knowledge_search.go:700-705`

### 2.2 覆盖优先级链

```
config.yaml(系统默认)
  → tenant.RetrievalConfig（仅独立搜索/消息搜索路径；JSONB，UI: /tenants/kv/retrieval-config）
  → CustomAgent.Config（覆盖 EmbeddingTopK / VectorThreshold / KeywordThreshold / RerankTopK / RerankThreshold / RerankModelID）
  → SearchTarget（仅阈值：DisableRecallThresholds 可强制清零）
```

- Agent 覆盖：`internal/application/service/session_qa_helpers.go:211-227`
  ```go
  if customAgent.Config.EmbeddingTopK > 0  { cm.EmbeddingTopK = customAgent.Config.EmbeddingTopK }
  if customAgent.Config.KeywordThreshold > 0 { cm.KeywordThreshold = ... }
  if customAgent.Config.VectorThreshold > 0  { cm.VectorThreshold = ... }
  if customAgent.Config.RerankTopK > 0       { cm.RerankTopK = ... }
  cm.RerankThreshold = customAgent.Config.RerankThreshold   // ← 无 >0 判断，无条件覆盖
  if customAgent.Config.RerankModelID != ""  { cm.RerankModelID = ... }
  ```
  ⚠️ **`RerankThreshold` 是无条件覆盖**：若 agent 未配置该字段（Go 零值 0），会把系统默认 0.3 抹成 0 → 重排过滤完全失效。这是与其它四个参数不对称的行为。
- KB 级：**KB 上没有阈值/TPK 字段**。KB 只决定"走哪个索引"（FAQ 索引 vs 文档向量索引 vs 关键词索引），见 `knowledgebase_search.go:401-416`。
- Target 级覆盖：`types/search.go:52-58`
  ```go
  func (st *SearchTarget) RecallThresholds(vectorThreshold, keywordThreshold float64) (float64, float64) {
      if st != nil && st.DisableRecallThresholds { return 0, 0 }
      return vectorThreshold, keywordThreshold
  }
  ```

### 2.3 校验边界（决定合法区间）

| 参数 | 允许区间 | 证据 |
|---|---|---|
| `vector_threshold` | [0, 1] | `handler/tenant.go:1762-1765` |
| `keyword_threshold` | [0, 1] | `handler/tenant.go:1766-1769` |
| `rerank_threshold` | [-10, 10] | `handler/tenant.go:1770-1773` |
| `embedding_top_k` | [0, 200] | `handler/tenant.go:1774-1777` |
| `rerank_top_k` | [0, 200] | `handler/tenant.go:1778-1781` |

---

## 3. Top-k 处理（问题 2）

### 3.1 `filter_top_k.go` 到底做什么

`chat_pipeline/filter_top_k.go:27-71` —— **纯截断，无扩展**：

```go
filterTopK := func(searchResult []*types.SearchResult, topK int) []*types.SearchResult {
    sortSearchResultsDeterministically(searchResult)
    if topK > 0 && len(searchResult) > topK {
        searchResult = searchResult[:topK]
    }
    return searchResult
}

if len(chatManage.MergeResult) > 0 {
    chatManage.MergeResult = filterTopK(chatManage.MergeResult, chatManage.RerankTopK)
} else if len(chatManage.RerankResult) > 0 {
    chatManage.RerankResult = filterTopK(chatManage.RerankResult, chatManage.RerankTopK)
} else if len(chatManage.SearchResult) > 0 {
    chatManage.SearchResult = filterTopK(chatManage.SearchResult, chatManage.RerankTopK)
}
```

- 规则：**按 `RerankTopK` 截断**（不是 EmbeddingTopK），作用在 `MergeResult`（回退顺序 MergeResult → RerankResult → SearchResult）。
- 排序：`sortSearchResultsDeterministically`（`:76-96`）—— 分数降序，平局依次 `KnowledgeID` → `ChunkType` → `ChunkIndex` → `ID`，`SliceStable`，保证可复现。
- 输入来源：`RerankResult` 已被 MMR 截过一次（见 §5）。但**并非总是 no-op**：
  - 走 `MergeResult` 时，`CHUNK_MERGE` 会做"顺序块合并"（减量）**但也会注入历史引用、扩展近邻**（可能增量）；
  - **FAQ KB 走迭代检索时可达 500 个候选**（`knowledgebase_search_faq.go:78-84,210`），`MergeResult` 远大于 `RerankTopK` → 本步是真正的有效截断；
  - 未走重排的路径（`RerankResult` 为空、直接落回 `SearchResult`）会一次性截到 `RerankTopK`。
- `!chatManage.NeedsRetrieval()` 时直接跳过（`:30-32`）。

### 3.2 有没有"先少后多"？—— 有，但**只在 FAQ 类型 KB**

唯一的自适应扩召回实现在 `internal/application/service/knowledgebase_search_faq.go:73-211`：

```go
maxIterations := 5
currentTopK := min(matchCount*3, maxRetrievalPoolSize)     // :78-84
...
if len(uniqueChunks) >= matchCount { break }               // :193-196  够了就停
if totalRetrieved < currentTopK { break }                  // :199-202  取不满说明没更多了
if currentTopK >= maxRetrievalPoolSize { break }           // :206-209  到顶
currentTopK = min(currentTopK*2, maxRetrievalPoolSize)     // :210       翻倍
```

触发条件（`:40`）：

```go
needsIterativeRetrieval := len(chunks) < params.MatchCount && len(vectorResults) == matchCount
```

- 仅当 `kb.Type == types.KnowledgeBaseTypeFAQ` 才进入（`:33-35`）。
- 起点 `matchCount*3`，最多 5 轮，每轮 ×2，硬上限 `maxRetrievalPoolSize = 500`（`knowledgebase_search.go:20`）。
- 负样本问题过滤（`NegativeQuestions`）在每轮内生效（`:164-175`）。
- **这是"精确语义匹配"而非"通用召回不足"**。

### 3.3 其它"扩"的机制（都不是 top-k 自适应）

| 机制 | 触发 | 做法 | 证据 |
|---|---|---|---|
| 过召回池 | 每次都做 | `matchCount = max(MatchCount*5, 50) * len(KBs)`，上限 500 | `knowledgebase_search.go:190-196` |
| Postgres 候选扩张 | 每次都做 | 子查询 `LIMIT expandedTopK`（= min(max(TopK*2,100),200)），再按阈值过滤，再取 TopK | `postgres/repository.go:343-359` |
| 查询扩展 | `EnableQueryExpansion && len(results) < max(1, EmbeddingTopK)` | 追加 ≤5 个变体结果，`expTopK = max(EmbeddingTopK*2, RerankTopK*2)` | `search.go:141-146`；`query_expansion.go:29` |
| Query 变体（Agent） | LLM 自己给 1–5 个 query | 每个 query 都跑一遍 | `agent/tools/knowledge_search.go:80-88` |
| 重排阈值降级 | 重排后 0 条且原阈值 > 0.3 | 阈值 ×0.7（下限 0.3）重试一次 | `chat_pipeline/rerank.go:148-179` |

### 3.4 MatchCount 归一化

`knowledgebase_search.go:303-322`

```go
func normalizedMatchCount(requested int) int {
    if requested <= 0 { return types.DefaultRetrievalTopK }   // 50
    return requested
}
```
调用点在 `HybridSearch` 最开头（`:131`），保证"过召回下限 / FAQ 迭代触发 / 末尾截断"三处读到同一个值。末尾截断在 `:296-298`。

---

## 4. 融合（问题 3）

### 4.1 向量 + 关键词 = 加权 RRF

入口：`internal/application/service/knowledgebase_search_fusion.go:33-50`

```go
func fuseOrDeduplicate(ctx, vectorResults, keywordResults, retrievalCfg) []*types.IndexWithScore {
    if len(keywordResults) == 0 { return deduplicateByScore(vectorResults) }  // 向量单路：保留原始相似度分
    if len(vectorResults) == 0 { return deduplicateByScore(keywordResults) }  // 关键词单路：保留原始分
    return fuseWithRRF(ctx, vectorResults, keywordResults, retrievalCfg)      // 双路：RRF
}
```

核心函数 `fuseWithRRF`（`:80-142`）：

```go
rrfK := retrievalCfg.GetEffectiveRRFK()                      // 默认 60
vectorWeight, keywordWeight := retrievalCfg.GetEffectiveRRFWeights()  // 默认 0.7 / 0.3
...
rrfScore := 0.0
if rank, ok := vectorRanks[chunkID]; ok {
    rrfScore += vectorWeight / float64(rrfK+rank)
}
if rank, ok := keywordRanks[chunkID]; ok {
    rrfScore += keywordWeight / float64(rrfK+rank)
}
info.Score = rrfScore
```

| 项 | 值 | 证据 |
|---|---|---|
| 公式 | `w_v/(k+rank_v) + w_k/(k+rank_k)` | `knowledgebase_search_fusion.go:120-124` |
| RRF k | **60**（`RRFK <= 0` 时） | `retrieval_config.go:87-92` |
| 向量权重 | **0.7** | `retrieval_config.go:96-108` |
| 关键词权重 | **0.3** | 同上 |
| rank 基准 | 1-indexed，`i+1`，同 chunk 取首次出现 | `:90-100` |
| 分数上界 | `2/(60+1) ≈ 0.0328`（两路 rank=1 且权重都 1 时）；默认权重下 `(0.7+0.3)/61 ≈ 0.0164` | 由公式推出【推断】；Agent 侧注释确认量级 `knowledge_search.go:280-282` |

**权重是否可按 query 类型配置：否。** 权重来自 `tenant.RetrievalConfig`，是租户级全局值，没有任何"按 query 类型/意图"分支（`fusion.go:84-86` 无 query 入参）。

**RRF 的 `rrf_k` 与两个权重完全无输入校验**（`handler/tenant.go:1761-1781` 只校验 5 个阈值/topk）；`GetEffectiveRRFK` 只判 `<= 0`，正数一律原样使用 → `rrf_k = 10^9` 会让所有 RRF 分趋近 0。

### 4.2 RRF 前置的分数归一化

`internal/application/service/retriever/normalizer.go:112-159` + `knowledgebase_search_fanout.go:107-129`

- **只在 `len(groups) > 1` 且结果跨 >1 种 engine type 时才归一化**（`:110`）。单引擎时保留原生尺度（"raw scores produced by the same engine are directly comparable"，`:107-109`）。
- 只归一化**向量分**；关键词分原样透传：
  ```go
  if retrieverType != types.VectorRetrieverType { return score }   // :118-122
  ```
- Milvus 特例：`(score+1)/2`；其余引擎 `clamp01(score)`（`:124-158`）。
- `clamp01` 同时吞掉 NaN/±Inf（`:164-175`），保护下游排序的严格弱序。

> **【文档 vs 代码】** `website-docs/03-features/05-retrieval-engines.md:244` 说的"关键词分数不归一化"与代码一致。

### 4.3 `composite.go` 如何组合多个 engine —— **不是组合，是路由**

`internal/application/service/retriever/composite.go:32-60`

```go
for _, engineInfo := range c.engineInfos {
    if slices.Contains(engineInfo.retrieverType, param.RetrieverType) {
        result, err := engineInfo.retrieveEngine.Retrieve(ctx, param)
        ...
        found = true
        break        // ← 第一个匹配即返回，不做多引擎合并
    }
}
if !found { return fmt.Errorf("retriever type %s not found", param.RetrieverType) }
```

- **每个 `RetrieverType` 只解析到一个 engine**（`break`），不存在"多引擎分数加权合并"。
- 真正的多引擎合并发生在**上层**：`retrieveFromStores`（`knowledgebase_search_fanout.go:48-131`）按 `storeGroup` 并发 Retrieve，再由 `classifyRetrievalResults` + `fuseOrDeduplicate` 合并。
- 去重规则：
  - `deduplicateByScore`（`fusion.go:65-78`）：**按 `ChunkID` 取最高分**，然后降序。
  - `fuseWithRRF`（`fusion.go:103-113`）：先放向量侧结果（同 chunk 取高分），关键词侧的新 chunkID 才补入 → **同一个 chunk 在两路都命中时只保留一条**（分数换成 RRF 分），元数据取向量侧。
  - `classifyRetrievalResults`（`fusion.go:13-29`）：`RetrieverType == VectorRetrieverType` 归向量，**其余全部归关键词**（`else` 分支，含未来新增类型）。

### 4.4 StoreGroup 扇出（多向量库/多租户）

`knowledgebase_search_fanout.go:48-131`

| 项 | 值 | 证据 |
|---|---|---|
| 并发上限 | `defaultMultiStoreFanoutLimit = 4` | `:24,67` |
| 每组超时 | `defaultMultiStoreRetrieveTimeout = 30s`，可用 `MULTI_STORE_RETRIEVE_TIMEOUT_SEC` 覆盖 | `:23,193-206` |
| 快路径 | `len(groups) == 1` 直接单引擎 Retrieve，零扇出开销 | `:56-58` |
| 失败策略 | **全有或全无**（errgroup 取消兄弟组）→ `NewVectorStoreUnavailableError` | `:32-36,89-105` |

---

## 5. 阈值语义（问题 4）

### 5.1 各引擎实际如何使用阈值

| 引擎 | 向量阈值 | 关键词阈值 | 证据 |
|---|---|---|---|
| **Postgres** | ✅ `WHERE distance <= 1-threshold`，`score = 1-distance` | ❌ **完全未使用** | `postgres/repository.go:390-397`；`164-261` 全函数无 `params.Threshold` |
| **SQLite** | ✅ `if params.Threshold > 0 && score < params.Threshold { continue }` | ❌ 未使用 | `sqlite/repository.go:436-439`；`289-365` |
| **Elasticsearch v8** | ✅ `MinScore: &minScore` | ❌ 未使用 | `elasticsearch/v8/repository.go:425-434`；`485-506` |
| **Elasticsearch v7** | ✅ `min_score` | ❌ 未使用 | `elasticsearch/v7/repository.go:659`；`704-726` |
| **Qdrant** | ✅ 原生 `score_threshold` 下推 | ❌ 未使用，且**分数硬编码 `Score: 1.0`** | `qdrant/repository.go:694` |
| **Milvus** | ✅（阈值语义由驱动决定） | ❌ 未使用，**分数硬编码 `set.Score = 1.0`** | `milvus/repository.go:791` |
| **Weaviate** | ✅ `WithCertainty(threshold)` | ❌ 未使用（推断，`KeywordsRetrieve` 无 threshold 引用） | `weaviate/repository.go:605-673` |

> **【推断】结论**：`keyword_threshold` 在两个 UI 上可配、在三种入口都有默认值（0.3 / 0.3 / 0.5），但**在检索时几乎不产生任何过滤效果**。在 Qdrant/Milvus 上关键词分数恒为 1.0，阈值即使被使用也只会"全部通过或全部不通过"。真正决定关键词召回的是 `TopK` 与 `MATCH` 语句，以及下游 RRF 的 rank。

### 5.2 什么都没通过阈值时会怎样

| 层级 | 行为 | 证据 |
|---|---|---|
| 引擎层 | 返回空列表，**不报错**，交给上层 | `postgres/repository.go:446`（仅 Warn 日志） |
| `HybridSearch` | `len(vector)==0 && len(keyword)==0` → `return nil, nil`（空且无错） | `knowledgebase_search.go:267-270` |
| `PluginSearch` | 检查 `EnableQueryExpansion && 召回数 < max(1, EmbeddingTopK)` → 跑变体检索补救 | `search.go:141-146` |
| `PluginSearch` | 仍为空 → `ErrSearchNothing` | `search.go:162` |
| `PluginSearchParallel` | chunk 空 + entity 空 → `ErrSearchNothing` | `search_parallel.go:171-176` |
| `PluginRerank` | 空输入 → 直接 `next()`（不报错） | `rerank.go:51-56` |
| `PluginMerge` | 空输入 → `next()`（`MergeResult` 保持空） | `merge.go:68-74` |
| `PluginFilterTopK` | 空 → 仅 Warn | `filter_top_k.go:59-63` |
| 上层 | `SearchKnowledge` 见 `ErrSearchNothing` → 返回空结果集，**不报错** | `session_knowledge_qa.go:912-915` |
| 会话层 | 空结果走 `FallbackStrategy`（`model` 或固定寄语，config 默认 `model`） | `session_knowledge_qa.go:929-936`；`config/config.yaml:16-18` |

**唯一真正的"阈值放宽"是重排层**（不是召回层）：
- 重排后 0 条且原阈值 > 0.3 → 阈值 ×0.7（下限 0.3）重试一次（`rerank.go:148-179`）。
- 重排后 0 条但 Top1 分数 ≥ fallback 下限 → 保底保留 Top1（`rerank.go:395-401`）。
- fallback 下限：**默认 0.15**；若 `SearchTargets.HasRecallThresholdOverride()` 为真则 **0**（`rerank.go:413-421`）。

### 5.3 `DisableRecallThresholds` 是不是"自适应逃生舱"？—— 不是

它是一个**用户显式圈定范围时的静态标志**：置位后 `RecallThresholds` 直接返回 `(0, 0)`，即彻底关闭召回阈值。

```go
// types/search.go:52-58
func (st *SearchTarget) RecallThresholds(vectorThreshold, keywordThreshold float64) (float64, float64) {
    if st != nil && st.DisableRecallThresholds { return 0, 0 }
    return vectorThreshold, keywordThreshold
}
```

**全部调用点/置位点（穷举）**：

| 位置 | 角色 | 说明 |
|---|---|---|
| `types/search.go:43-46` | 定义 | 字段与注释 |
| `types/search.go:52-58` | 消费（取阈值） | `RecallThresholds` 清零 |
| `types/search.go:60-69` | 消费（判定） | `HasRecallThresholdOverride()` —— 任一 target 置位即 true |
| `types/chat_manage.go:192` | 传递 | `Clone()` 深拷贝时保留该标志 |
| `chat_pipeline/search.go:536-546` | 消费 | 命中时打 `explicit_scope_threshold_override` 日志；`params` 用清 0 后阈值 |
| `chat_pipeline/query_expansion.go:59-62` | 消费 | 变体检索同样走 `RecallThresholds` |
| `chat_pipeline/rerank.go:413-421` | 消费 | fallback 下限从 0.15 降到 0 |
| `agent/tools/knowledge_search.go:568-571` | 消费 | Agent 工具的同名路径 |
| `agent/tools/knowledge_search.go:641` | 消费 | `HasRecallThresholdOverride()` → `preserveTop=true` |
| `session_knowledge_qa.go:547-553` | **置位** | `@` 提到的具体文档（`SearchTargetTypeKnowledge`） |
| `session_knowledge_qa.go:584-591` | **置位** | 文档型 KB 的标签范围（tag scope，已解析为 KnowledgeIDs） |
| `session_knowledge_qa.go:595-607` | **置位** | FAQ KB 的标签范围 / 标签+显式文档 |

**结论**：置位条件全是"用户在本轮显式圈定了文档/标签"，与"召回太少"无关。**它不是自适应机制**。真正意义上的语义是：**"用户说了要这几篇，就别让全局阈值把它们全滤掉"**。

---

## 6. 重排（问题 5）

### 6.1 何时跑

`chat_pipeline/rerank.go:38-62`

```go
if !chatManage.NeedsRetrieval() { return next() }        // 意图不需要检索 → 跳过
if len(chatManage.SearchResult) == 0 { return next() }   // 无候选 → 跳过
if chatManage.RerankModelID == "" { return next() }      // 无模型 → 跳过（fail-open）
```

- **`CHUNK_RERANK` 事件无条件加入管线**（`session_knowledge_qa.go:199`），运行时靠上面 3 个条件短路。
- **`config.yaml` 的 `enable_rerank` 未被读取**（见 §10）。等价的控制手段 = 清空 `RerankModelID`。
- 模型解析失败 → **报错中止**：`return ErrGetRerankModel.WithError(err)`（`rerank.go:65-72`）。这是 fail-closed 的唯一分支。

### 6.2 重排多少候选、用什么阈值

| 项 | 值 | 证据 |
|---|---|---|
| 候选数 | `len(chatManage.SearchResult)` **全部**（过滤掉空 passage 后的） | `rerank.go:75-88,114-117` |
| 候选上限 | **无 pipeline 级上限**。候选来自 `EmbeddingTopK`(30) × 每个 KB/SearchTarget，聚合后可远超 30 | `search.go:469-478,547-557` |
| 单次 API 文档数 | 由驱动内部切批：LKEAP **60**/请求、Volcengine **50**/请求 | `models/rerank/lkeap_reranker.go:16-17,111-124`；`models/rerank/volcengine_reranker.go:23,112-114` |
| Query | 单条 `chatManage.RewriteQuery` | `rerank.go:128` |
| Passage | `getEnrichedPassage` = 清洗后的 `Content` + 全部 `ImageInfo.Caption/OCRText` + `ChunkMetadata.GeneratedQuestions` | `rerank.go:644-694` |
| Passage 清洗 | 剥离 markdown 图片/链接/URL/表格分隔/标题符/引用符/粗斜体/列表符/HTML/折叠空行 | `rerank.go:594-642` |
| 阈值 | `chatManage.RerankThreshold`（会话路径默认 **0.3**） | `rerank.go:385` |
| 打分明细 | `passages` 里 `TrimSpace()==""` 的被剔除，**索引会错位** → 见 §10 潜在缺陷 | `rerank.go:325-343` vs `:78-88` |

### 6.3 失败/未配置：fail-open 还是 fail-closed

| 情形 | 行为 | 判定 | 证据 |
|---|---|---|---|
| `RerankModelID` 为空 | 跳过重排，保留原始检索序 | **fail-open** | `rerank.go:57-62` |
| `SearchResult` 为空 | 跳过 | fail-open | `rerank.go:51-56` |
| 意图不需要检索 | 跳过 | fail-open | `rerank.go:41-43` |
| **模型解析失败** | `ErrGetRerankModel` 中止 | **fail-closed** | `rerank.go:65-72` |
| **重排 API 调用失败** | 回退到原始候选 `candidatesToRerank` | **fail-open** | `rerank.go:130-144`；降级重试分支 `:164-177` |
| 重排结果全被阈值滤掉 | Top1 ≥ fallback 下限则保留 Top1；否则返回 `ErrSearchNothing` | 半开 | `rerank.go:390-408`；`:237-251` |

### 6.4 复合打分 / FAQ / MMR

```go
// rerank.go:439-455
func compositeScore(sr *types.SearchResult, modelScore, baseScore float64) float64 {
    sourceWeight := 1.0
    if strings.ToLower(sr.KnowledgeSource) == "web_search" { sourceWeight = 0.95 }
    composite := 0.6*modelScore + 0.3*baseScore + 0.1*sourceWeight
    // clamp [0,1]
}
```
- 权重 **0.6 / 0.3 / 0.1**，web_search 源固定 0.95 分项。`base_score` 与 `model_score` 写进 Metadata（`:200-202`）。
- FAQ boost（仅当 `FAQPriorityEnabled && FAQScoreBoost > 1.0 && ChunkType == faq`）：`Score = min(Score * boost, 1.0)`（`:206-218`）。
- **MMR**（`:223`）：
  ```go
  final := applyMMR(ctx, reranked, chatManage, min(len(reranked), max(1, chatManage.RerankTopK)), 0.7)
  ```
  - **lambda = 0.7（硬编码）**，k = `min(候选数, max(1, RerankTopK))`（注意：**不是**文档说的纯 `RerankTopK`）。
  - 冗余度用 `searchutil.Jaccard` on `searchutil.TokenizeSimple(getEnrichedPassage(...))`，token 集并行预计算（`:475-477`），然后贪心 `mmr = 0.7*relevance - 0.3*maxJaccard`（`:503`）。
  - `k <= 0 || len(results) == 0` → 返回 **nil**（`:465-467`），调用方 `RerankResult = nil` → 后续 Merge 回退到 `SearchResult`。

### 6.5 是否按 query 类型/scope 跳过重排？—— 否

- 没有任何 query-type / intent 分支跳过重排。唯一相关的分支是 `!NeedsRetrieval()`（全局意图，不是 query 类型细分）。
- scope 只影响**阈值兜底**，不影响"是否重排"：

```go
// rerank.go:413-421
func rerankFallbackMinScore(searchTargets types.SearchTargets) float64 {
    if searchTargets.HasRecallThresholdOverride() {
        return 0     // 显式 scope：保底保留最佳候选
    }
    return 0.15
}
```

- `rerank_scope_test.go:9-18` 精确锁定这个语义：
  ```go
  if got := rerankFallbackMinScore(nil); got != 0.15 { ... }
  targets := types.SearchTargets{{DisableRecallThresholds: true}}
  if got := rerankFallbackMinScore(targets); got != 0 { ... }
  ```
  即：**`HasRecallThresholdOverride()==true` ⇔ fallback 下限 0 ⇔ "显式圈定的 scope 绝不能被阈值清空"**。Agent 工具侧同一语义：`preserveTop=true` 时即使 Top1 分数低于 `agentRerankFallbackMinScore`(0.15) 也保留（`agent/tools/knowledge_search.go:709-735`）。

### 6.6 后置加成（同为 CHUNK_RERANK 事件，在 Rerank 核心之后）

执行链 = `PluginRerank` → `PluginWikiBoost` → `PluginMemoryAffinity`（`container.go:381,395,396`）。两个加成插件都先 `next()` 再加工，因此顺序与注册顺序相同，**MemoryAffinity 的 `sort.SliceStable` 是最终顺序**。

| 加成 | 因子 | 条件 | 证据 |
|---|---|---|---|
| **WikiBoost** | **1.3×** 恒定 | 结果含 `ChunkType == "wiki_page"` **且** 至少一个 SearchTarget 的 KB `IsWikiEnabled()` | `wiki_boost.go:15,55-97`；`types/chunk.go:38-39`；`types/knowledgebase.go:822-827` |
| **MemoryAffinity** | `1 + 0.15 * min(1, ln(1+hits)/ln(9))` → 最大 **1.15×** | `hits >= types.MemoryDocAffinityMinHits`（=2）；最多查 200 个 KnowledgeID；需 memory 启用且 `RetrievalConditioningEnabled()` | `memory_affinity.go:20-25,89-110,119-128`；`types/memory.go:387-391,405-409` |

`affinityFactor` 实测值：hits=2 → **1.0750**；hits=3 → 1.0946；hits=5 → 1.1223；hits≥8 → **1.15（封顶）**（`memory_affinity.go:119-128`）。

> **重要边界**：两者都只作用于**已完成 MMR 选择的 `RerankResult`（≤ RerankTopK）**（`rerank.go:223-224`）。因此加成**只能在同一候选集内改变次序，无法把被 MMR 淘汰的块召回**。

---

## 7. 检索后扩展（问题 6）

### 7.1 CHUNK_MERGE 的 8 步（`chat_pipeline/merge.go:33-97`）

| 步 | 操作 | 函数 |
|---|---|---|
| 1 | 选输入：`RerankResult` 优先，空则 `SearchResult`（按分降序） | `selectInputResults` `:101-113` |
| 2 | 初去重（ID + 内容签名） | `dedup`/`removeDuplicateResults` `:116-126`；`search.go:183-211` |
| 3 | 注入历史引用并再去重 | `injectHistoryResults` `:130-145` |
| 4 | **父块解析** | `resolveParentChunks` `:218-401` |
| 5 | 按 `KnowledgeID + ChunkType` 分组、合并连续正文 | `groupAndMergeCurrentContent` `:149-212` → `mergeSequentialChunks` |
| 6 | 填充 FAQ 答案 | `populateFAQAnswers` `:83` |
| 7 | 近邻扩展短上下文 | `expandShortContextWithNeighbors` `merge_expand.go:11-246` |
| 7.5 | 再次合并（扩展可能引入新重叠） | `groupAndMergeCurrentContent` `:89` |
| 8 | 终去重：ID+签名 再 + 部分重叠 | `dedup` + `removePartialOverlaps` `:92-93` |

### 7.2 `resolveParentChunks` 细节（`:218-401`）
- 前置：`chunkRepo != nil`；`tenantID` 从 ctx 或 `chatManage.TenantID` 取，**取不到就整体跳过**（`:227-236`）。
- 收集所有 `ParentChunkID`，批量 `ListChunksByID` 一次取回（`:239-266`）。
- **祖父块（grandparent）只在 image 命中时取**（`:271-308`）：
  ```go
  for _, r := range results {
      if r.ChunkType == string(types.ChunkTypeImageOCR) || r.ChunkType == string(types.ChunkTypeImageCaption) {
          imageTextParentIDs[r.ParentChunkID] = struct{}{}
      }
  }
  // 父块必须是 text 类型，且父块的 ParentChunkID 指向未取过的块 → 取作祖父
  if parent.ParentChunkID == "" || parent.ChunkType != types.ChunkTypeText { continue }
  ```
  即链式为 **image_ocr/image_caption → text → parent_text**。
- 逐条改写（`:317-398`）：
  - **text 子块**：父块必须是 `ChunkTypeParentText` 且 `Content != ""`，否则 `continue`（不扩展）。扩展方式：
    ```go
    parentContent := searchutil.PruneMarkdownImagesByImageInfo(parent.Content, r.ImageInfo)
    r.Content = searchutil.JoinChunkContent(parentContent, r.Content, "\n\n")
    r.ContentRewritten = true
    r.SubChunkID = append(r.SubChunkID, r.ID)
    ```
    `ImageInfo` 按 text-child 作用域注入（`assignScopedImageInfo`，`:439-449`），避免图片密集的父块把整页 OCR/Caption 灌进上下文。
  - **image_ocr / image_caption 子块**：先保存 `childRecognizedContent`（命中块自身的 OCR/Caption 文本），把 `Content` 换成 text 父块，若 text 父块还有 `parent_text` 祖父则用祖父作为主体：
    ```go
    contentSource := textParent
    if textParent.ParentChunkID != "" {
        if gp, found := parentMap[textParent.ParentChunkID]; found &&
            gp.ChunkType == types.ChunkTypeParentText && gp.Content != "" {
            contentSource = gp
        }
    }
    r.Content = textParent.Content
    r.ChunkIndex = textParent.ChunkIndex
    ...
    r.Content = searchutil.JoinChunkContent(parentContent, textContent, "\n\n")
    r.Content = searchutil.JoinChunkContent(r.Content, childRecognizedContent, "\n\n")  // 重新贴回识别文本
    ```
    （`:351-384`）—— 显式修复"强制扫描 PDF 的父 markdown 只有图片占位符，丢子块正文会导致上下文为空"的 #3052。
- 扩展后 `SubChunkID` 记录被并入的子块 ID，`ContentRewritten = true`。

### 7.3 近邻扩展（`merge_expand.go`）

```go
const (
    minLen = 350      // 短于 350 rune 的 text chunk 才扩展
    maxLen = 850      // 扩展后硬截断到 850 rune
)
```

- 仅对 `ChunkType == text` 且 `runeLen(Content) < 350` 的块（`:47-52`）。
- 沿 `PreChunkID` / `NextChunkID` 两侧向外扩，**要求 `KnowledgeID` 相同**（`:143,153,179,197`）。
- 循环直到 `runeLen(merged) >= 350` 或两侧都取不到（`:163-210`）。
- 截断规则 `mergeOrderedContent`（`:254-267`）：
  ```go
  runes := []rune(content)
  if len(runes) > maxLen { return string(runes[:maxLen]) }
  ```
  → **单 chunk 上下文上限 850 rune**（runes，不是 bytes、不是 token）。

### 7.4 顺序块合并（`merge_overlap.go`）

- 分组内按 `ChunkIndex` 排序（`merge.go:183-188`），逐对分类（`classifyMerge` `:129-150`）：

| 分类 | 条件 | 动作 |
|---|---|---|
| `mergeSeparate` | 坐标可信且 `current.StartAt > last.EndAt`；或不可信且既非文本包含也非索引连续 | 新开一组 |
| `mergeExtend` | 坐标可信且 `current.EndAt > last.EndAt` | 按坐标重叠拼接（`AppendWithExactOverlap`，失败降级 `AppendWithOverlap`） |
| `mergeSubsume` | 坐标可信且 `last.Content` 包含 `current.Content` | 只记录子块，不动正文 |
| `mergeJoinDistinct` | 坐标可信、范围被包含但文本不同 | 文本拼接（破坏长度不变量） |
| `mergeJoinText` | 不可信但文本包含或 `ChunkIndex == lastIndex+1` | 纯文本拼接 |

- "坐标可信"定义（`:94-99`，非常关键）：
  ```go
  func chunkTrusted(chunk *types.SearchResult) bool {
      return chunk.ContentRevision == 0 && !chunk.ContentRewritten &&
             chunk.EndAt > chunk.StartAt && runeLen(chunk.Content) == chunk.EndAt-chunk.StartAt
  }
  ```
  即 **未编辑、未被管线改写、范围合法、且长度与切分器一致**。第 4 步父块扩展会把 `ContentRewritten` 置 true，因此**父块解析后的块会退化到文本匹配路径**——这是有意设计（注释 `:12-16`）。
- 组内保留**最高分**（`:58-60`）。

### 7.5 部分重叠去重

`search.go:226-303`（`removePartialOverlaps`）

```go
const overlapThreshold = 0.85
```
- 触发删除的条件：`IsContentContained(短, 长)` 为真，**或** `ContentOverlapRatio(...) >= 0.85`。
- 被删者是两者中**分数较低**的一个（`:278-282`）。
- `removeDuplicateResults` 明确**不**按 `ParentChunkID` 去重（`search.go:188-190` 注释）：
  > "Only deduplicate by exact chunk ID — do NOT treat shared ParentChunkID as duplicates, because different child chunks of the same parent carry different content segments that may all be relevant."

### 7.6 最终进 LLM 的 chunk 数 & 预算

**没有 token 预算。** 结论链：

1. `PluginFilterTopK` 把 `MergeResult` 截断到 `RerankTopK`（会话默认 30 / 租户默认 10）（`filter_top_k.go:41-51`）。
2. `IntoChatMessage` 遍历 `chatManage.MergeResult` **全部**拼进 `<context id="N">`，无长度检查、无计数检查：
   ```go
   // into_chat_message.go:156-162
   for i, result := range chatManage.MergeResult {
       passage := getEnrichedPassageForChat(ctx, result)
       ...
       contextsBuilder.WriteString(fmt.Sprintf("<context id=\"%d\">%s</context>", i+1, passage))
   }
   ```
3. 唯一存在的尺寸约束是：
   - 单 chunk 850 rune（近邻扩展上限，§7.3）；
   - `config/config.yaml:26` 的 `summary.max_input_chars: 16384` —— 但这是**摘要功能**的参数，不在检索管线里。
4. 因此**实际进上下文的 chunk 数 ≈ min(去重合并后的候选数, RerankTopK)**；上限数量级 = `RerankTopK`。

> `Merge` 阶段多数操作是"减量"（合并/去重），所以最终数通常 < `RerankTopK`；但**没有任何机制保证总字符数/token 数有界**。若父块 `parent_text` 极大（CHUNKING.md 推荐 4096），单条 context 就可能很大。

---

## 8. 查询变换（问题 7）

### 8.1 `query_understand.go` —— **LLM 驱动**

| 项 | 值 | 证据 |
|---|---|---|
| 触发 | `chatManage.EnableRewrite` 为真，**或** 有图片 | `query_understand.go:66-74` |
| 默认行为 | `RewriteQuery = Query`（先赋值，失败也不会变空） | `:64` |
| 输出结构 | `{"rewrite_query": "...", "intent": "...", "image_description": "..."}` | `:28-32` |
| 模型选择 | 优先 vision 模型（有图时）；否则 `QueryUnderstandModelID`，为空则 `ChatModelID`；解析失败回退 `ChatModelID` | `:230-284` |
| Temperature | **0.3** | `:125` |
| MaxCompletionTokens | **150**（无图）/ **500**（有图） | `:113-116` |
| Thinking | **显式关闭** `thinking := false` | `:119,127` |
| 历史 | 复用 `chatManage.History`，否则 `loadAndProcessHistory(..., maxRounds, 20)`；`MaxRounds <= 0` 直接返回 nil | `:196-226` |
| 记忆注入 | `MemoryService.RetrievalContextFor` 的背景/兴趣/常查资料，注入到**重写提示词**中（不是过滤条件） | `:335-374` |
| 解析容错 | `parseStructuredQueryOutput`：先严格 JSON，失败则截取首个 `{` 到末个 `}` 再解析；键名兼容 `rewrite_query`/`rewritten_query`/`query`/`question` | `:398-447` |
| LLM 失败 | `return next()`（**保留原始 query 与 intent，不中断管线**） | `:129-135` |
| 意图的用途 | `!NeedsRetrieval()` 时套用 `IntentSystemPrompts` 覆盖系统提示词；并让下游 3 个插件短路 | `:146-154`；`search_parallel.go:94-100`；`rerank.go:41-43`；`filter_top_k.go:30-32`；`merge.go:47-49` |

- 意图枚举：`kb_search` / `web_search` / `greeting` / `chitchat` / `follow_up` / `image_only` / `doc_only` / `summarize` / `clarification`（`types/chat_manage.go:86-96`）。
- `NeedsKBRetrieval`：`kb_search` / `clarification` / `summarize` / 空值 → true（`:102-109`）。
- **意图不参与任何阈值/权重计算**，只用于"要不要检索"和"用哪段系统提示词"。

### 8.2 `query_expansion.go` —— **纯规则，无 LLM**

`chat_pipeline/query_expansion.go:14-175`

| 项 | 值 | 证据 |
|---|---|---|
| 触发 | `EnableQueryExpansion && len(SearchResult) < max(1, EmbeddingTopK)` | `search.go:141` |
| 生成方式 | **本地规则**，注释明说 "generates query variants locally without LLM" | `:112-113` |
| 变体来源 | ①去停用词后的关键词 ②引号/「」『』短语 ③按 `,，;；、。！？!?\s` 切分的长段（>5 字）④去疑问词（什么/如何/怎么/为什么/哪个…） | `:140-164`；停用词表 `:178-188`；疑问词正则 `:191` |
| 上限 | **5 个变体** | `:120,166-169` |
| 去重 | 与原 query、`chatManage.Query` 去重；长度 < 3 丢弃 | `:121-138` |
| 分词 | `types.Jieba.CutForSearch`（中文），中英混排按脚本分段 | `:236-281` |
| 每个变体的检索参数 | `VectorThreshold`=target 阈值，`KeywordThreshold = KeywordThreshold*0.8`（放宽 20%），`MatchCount = max(EmbeddingTopK*2, RerankTopK*2)`，双路都开 | `:29-30,59-73` |
| 并发 | 信号量 `capSem = min(16, len(expansions) × len(SearchTargets))` | `:36-48` |
| 结果处理 | **直接 append** 到 `SearchResult`（不去重、不重排），随后由 rerank/merge 统一处理 | `search.go:142-146` |

- **不是 HyDE**（不生成假设文档）。
- **不是 decomposition / multi-hop**（不做子问题拆分、不做多轮迭代检索）。变体是**同一个问题的表层改写**。
- Agent 工具侧的"多 query"是另一条路：由 LLM 在工具调用里给 1–5 个 query，schema 硬限制 `maxItems: 5`（`agent/tools/knowledge_search.go:70-88`）。

---

## 9. 替代/附加检索路径（问题 8）

| 路径 | 激活条件 | 机制 | 关键数字 | 证据 |
|---|---|---|---|---|
| **MMR** | Pipeline：**无条件**（只要重排产生了结果）；Agent 工具：同样无条件（只要有候选） | 贪心 `λ*rel - (1-λ)*maxJaccard`，token 用 `TokenizeSimple` | Pipeline: **λ=0.7**, k=`min(n, max(1,RerankTopK))`；Agent: **λ=0.7**, k=`min(n, max(1,topK))` | `chat_pipeline/rerank.go:223,457-538`；`agent/tools/knowledge_search.go:318-343,1248-1330` |
| **GraphRAG / 实体检索** | `NEO4J_ENABLE=true` **且** 至少一个 KB 的 `ExtractConfig.Enabled` **且** 实体抽取产出非空 `chatManage.Entity` | LLM 抽实体 → 单跳 Neo4j 查询 → 节点携带的 chunkID → 加载 chunk（`Score=1.0`, `MatchType=MatchTypeGraph`） | **单跳**（Cypher `MATCH (n)-[r]-(m)`，无 hop 参数）；节点名 `CONTAINS` 匹配；无节点数上限 | `extract_entity.go:60-63,107-117,145-151`；`search_entity.go:45-59,131-135,209-232`；`neo4j/repository.go:176-182` |
| **Web 搜索** | `chatManage.WebSearchEnabled` **且** 有 `WebSearchProviderID` | 与 KB 检索**并行**（独立 goroutine），结果转成 `SearchResult` 直接 append | `MaxResults` 来自 `EffectiveWebSearchConfig`，可被 Agent 的 `WebSearchMaxResults` 覆盖 | `search.go:112-120,583-651` |
| **Web Fetch** | `req.WebSearchEnabled`（管线级）+ `WebFetchEnabled` | `WEB_FETCH` 事件，位于 RERANK 与 MERGE 之间，用完整页面替换 snippet | `WebFetchTopN` 默认 3 | `session_knowledge_qa.go:200`；`chat_pipeline/web_fetch.go:14`；`types/chat_manage.go:73-74` |
| **Wiki Boost** | 结果里有 `wiki_page` **且** 至少一个 target KB `IsWikiEnabled()` | `Score *= 1.3`，然后 stable sort | **1.3×** | `wiki_boost.go:15,53-97` |
| **Memory Affinity** | `memoryService != nil` 且结果非空且该用户对该文档有历史命中 | `Score *= 1 + 0.15*min(1, ln(1+hits)/ln(9))` | 最大 **1.15×**；门槛 `hits >= 2`；最多查 **200** 个 KnowledgeID | `memory_affinity.go:20-25,89-110,119-128`；`types/memory.go:391` |
| **FAQ 迭代检索** | KB 类型为 FAQ 且首次唯一 chunk 数 < MatchCount 且 `len(vectorResults)==matchCount` | TopK 从 `matchCount*3` 起翻倍，最多 5 轮 | 上限 **500** | `knowledgebase_search_faq.go:33-48,78-84,210` |
| **历史引用注入** | 前序轮次存在 `KnowledgeReferences` | 把上一轮引用标记 `MatchTypeHistory` 并合入 | 只取**最近一轮**有引用的 | `search.go:166-181`；`merge.go:130-145` |
| **父块/近邻/关系块富化** | `!SkipContextEnrichment` | 拉父块（`MatchTypeParentChunk`）、`PreChunkID/NextChunkID` 近邻（`MatchTypeNearByChunk`）、`RelationChunks`（`MatchTypeRelationChunk`） | — | `knowledgebase_search_results.go:127-173` |
| **数据源复合检索** | `DataAnalysisEnabled`（Agent 配置，默认关） | `DATA_ANALYSIS` 独立管线阶段 | — | `session_knowledge_qa.go:203`；`types/chat_manage.go:51-54` |
| **StoreGroup 多库扇出** | 多向量库/多租户分组 | 并发 Retrieve + 归一化 + RRF | 并发 **4**，每组超时 **30s**；store 解析总预算 **12s**（`storeResolveBudget`） | `knowledgebase_search_fanout.go:22-25,67,72`；`knowledgebase_search_storegroup.go:17-21,114-115` |

**其它需知的结构性事实**

| 事实 | 说明 | 证据 |
|---|---|---|
| `ENTITY_SEARCH` 链是死代码 | `PluginSearchEntity` 注册在 `ENTITY_SEARCH` 上，但任何组装出的 pipeline 都不含该事件；实际调用是 `search_parallel.go:140` 直调内部未注册实例。 | `container.go:393`；`search_parallel.go:140`；`session_knowledge_qa.go:187-206` |
| `chatManage.GraphResult` 无消费者 | 关系数据被写入但全仓无人读取，只有 `node.Chunks` 生效（图召回 = 节点→chunk，关系数据丢弃）。 | `search_entity.go:131-134`；`types/chat_manage.go:124` |
| 实体抽取是 LLM 调用且**不检查 intent** | 只要 `NEO4J_ENABLE=true` 且有 `ExtractConfig.Enabled` 的 KB，即使意图是 greeting 也会跑一次抽取（模型 = 会话同款 `ChatModelID`，T=0.3，maxTokens=4096）。 | `extract_entity.go:60-63,67,107-117,167-177` |
| 图召回 base score 最高 | `Score=1.0` → 复合分中拿满 0.3 基础分项。 | `search_entity.go:221`；`rerank.go:447` |
| FAQ 走迭代时 **RRF 结果被整体替换** | `applyFAQPostProcessing` 的迭代分支直接 `return iterativeRetrieveWithDeduplication(...)`，覆盖 `deduplicatedChunks`。因 FAQ 不参与关键词检索（`knowledgebase_search.go:413`），实际是"向量多轮合并"，未丢 RRF 语义。 | `knowledgebase_search_faq.go:40-48`；`knowledgebase_search.go:287-291,413` |
| `keywords_vector_hybrid_indexer.go` 不实现索引或打分 | 只是把 Repository 包装成 `RetrieveEngineService`，唯一实质职责是在 `Index`/`BatchIndex` 时按 retriever type 计算 embedding。关键词索引与打分完全取决于被包装的 Repository。 | `keywords_vector_hybrid_indexer.go:62-84,294-296` |

> **重要**：`chat_pipeline` 路径下所有 KB 检索都传 `SkipContextEnrichment: true`（`search.go:476,555`；`query_expansion.go:72`），因此 `collectEnrichmentChunkIDs` 那套块级富化**只在非 chat 路径（`/knowledgebase/search`）生效**；chat 路径的富化完全由 `CHUNK_MERGE` 承担（`merge.go`）。---

## 10. 可配置项清单（问题 9）

### 10.1 租户/工作区级（JSONB `tenants.retrieval_config`，UI `/tenants/kv/retrieval-config`）

API：`GET/PUT /tenants/retrieval-config`（`handler/tenant.go:1731-1806`）

| 字段 | 默认 | 合法区间 | 影响 |
|---|---|---|---|
| `embedding_top_k` | 50 | [0,200] | 过召回池基数、MatchCount、查询扩展触发阈值 |
| `vector_threshold` | 0.15 | [0,1] | 向量召回 |
| `keyword_threshold` | 0.3 | [0,1] | 关键词召回（**多数引擎不生效**，§5.1） |
| `rerank_top_k` | 10 | [0,200] | 重排后保留数、`filter_top_k` 截断值 |
| `rerank_threshold` | 0（显式 0 即不过滤） | [-10,10] | 重排过滤 |
| `rerank_model_id` | 空 | — | 空 = 禁用重排 |
| `rrf_k` | 60 | >0（无上限校验） | RRF 平滑常数 |
| `rrf_vector_weight` | 0.7 | >0 | RRF 向量权重 |
| `rrf_keyword_weight` | 0.3 | >0 | RRF 关键词权重 |

⚠️ 只有 `/knowledgebase/.../search`、消息搜索、评估（`service/evaluation.go:270-276`）走这套；**会话聊天默认走 `config.yaml`**（`session_knowledge_qa.go:114-118`）。

### 10.2 Agent 级（`CustomAgent.Config`）

`internal/application/service/session_qa_helpers.go:211-288`

| 字段 | 生效方式 |
|---|---|
| `embedding_top_k` | `> 0` 时覆盖 |
| `keyword_threshold` | `> 0` 时覆盖 |
| `vector_threshold` | `> 0` 时覆盖 |
| `rerank_top_k` | `> 0` 时覆盖 |
| `rerank_threshold` | **无条件覆盖**（零值会抹掉系统默认） |
| `rerank_model_id` | 非空时覆盖 |
| `enable_rewrite` / `enable_query_expansion` | 直接赋值 |
| `rewrite_prompt_system` / `rewrite_prompt_user` | 非空时覆盖 |
| `query_understand_model_id` | 非空时覆盖 |
| `faq_priority_enabled` / `faq_direct_answer_threshold` / `faq_score_boost` | 直接赋值 |
| `history_turns` / `multi_turn_enabled` | 覆盖 `MaxRounds`（`multi_turn_enabled=false` → `MaxRounds=0`） |
| `web_search_max_results` | `> 0` 时覆盖 |
| `intent_prompts` | 意图级系统提示词覆盖 |
| `data_analysis_enabled` | 开启 `DATA_ANALYSIS` 阶段 |
| `citation_enabled` | 引用开关 |
| `memory_enabled` | 长期记忆偏好 |

### 10.3 系统级 `config/config.yaml`

| 键 | 默认 | 位置 |
|---|---|---|
| `conversation.max_rounds` | 5 | `:10` |
| `conversation.keyword_threshold` | 0.3 | `:11` |
| `conversation.embedding_top_k` | **30** | `:12` |
| `conversation.vector_threshold` | 0.2 | `:13` |
| `conversation.rerank_threshold` | 0.3 | `:14` |
| `conversation.rerank_top_k` | **30** | `:15` |
| `conversation.fallback_strategy` | `model` | `:16` |
| `conversation.enable_rewrite` | true | `:19` |
| `conversation.enable_query_expansion` | true | `:20` |
| `conversation.enable_rerank` | true | `:21` — **未被读取** |
| `conversation.summary.max_input_chars` | 16384 | `:26`（摘要用，非检索） |
| `knowledge_base.chunk_size` | 512 | `:42` |
| `knowledge_base.chunk_overlap` | 50 | `:43` |

### 10.4 环境变量

| 变量 | 默认 | 作用 | 证据 |
|---|---|---|---|
| `RETRIEVE_DRIVER` | `postgres`（`.env.example:271`） | 决定默认 retriever engine 映射 | `types/tenant.go:17-83` |
| `MULTI_STORE_RETRIEVE_TIMEOUT_SEC` | 30 | 多库扇出每组超时 | `knowledgebase_search_fanout.go:22-25,196-206` |
| `NEO4J_ENABLE` | false | 实体抽取/GraphRAG 总开关 | `extract_entity.go:60`；`.env.example:329-335` |
| `ENABLE_GRAPH_RAG` | — | 已弃用（v0.1.6 起由 `NEO4J_ENABLE` 取代，Go 端不再读取） | `.env.example:329` |
| `RERANK_MODEL_NAME` / `RERANK_BASE_URL` / `RERANK_API_KEY` / `RERANK_PROVIDER` | — | 重排模型接入 | `.env.example:373-376` |
| `EMBEDDING_MODEL_NAME` / `EMBEDDING_BASE_URL` / `EMBEDDING_API_KEY` / `EMBEDDING_PROVIDER` | — | 嵌入模型接入 | `.env.example:367-370` |

### 10.5 KB 级

- **没有任何检索参数**（无阈值、无 top-k）可直接配置在 KB 上。
- KB 只决定**索引路由**：`IsVectorEnabled()` / `IsKeywordEnabled()` / `Type == FAQ` / `VectorStoreID` 绑定（`knowledgebase_search.go:401-416,419-469`；`retriever/factory.go:147-165`）。
- KB 类型（document / FAQ / wiki / graph-only）间接决定走哪条检索逻辑。
- 绑定 `VectorStoreID` 会**绕过租户级 effective-engines 过滤**，使用该 store 支持的全部 retriever 类型（`factory.go:249-258`）。

### 10.6 请求级

- `SearchTarget` 的 `TagIDs` / `ScopeTagIDs` / `KnowledgeIDs` / `DisableRecallThresholds`（由 `@` 提及与 tag scope 派生，非用户直接输入）。
- `WebSearchEnabled` / `WebSearchProviderID`。

### 10.7 代码级（不可配置）

| 硬编码常量 | 值 | 位置 |
|---|---|---|
| MMR λ | **0.7** | `chat_pipeline/rerank.go:223`；`agent/tools/knowledge_search.go:336` |
| 复合打分权重 | **0.6 / 0.3 / 0.1** | `rerank.go:447` |
| web_search 源分项 | **0.95** | `rerank.go:443` |
| 重排 fallback 下限 | **0.15** | `rerank.go:420` |
| 重排阈值降级系数 / 下限 | **0.7 / 0.3** | `rerank.go:148-153` |
| Wiki boost | **1.3×** | `wiki_boost.go:15` |
| Memory affinity 上限 / 饱和点 / 门槛 / 查询上限 | **1.15 / 8.0 / 2 / 200** | `memory_affinity.go:20-25` |
| 查询扩展变体数 | **5** | `query_expansion.go:166-169` |
| 查询扩展关键词阈值放宽 | **×0.8** | `query_expansion.go:30` |
| 查询扩展并发上限 | **16** | `query_expansion.go:37` |
| 过召回倍数 / 下限 / 上限 | **×5 / 50 / 500** | `knowledgebase_search.go:20,193-196` |
| FAQ 迭代轮数 / 起点 / 上限 | **5 / ×3 / 500** | `knowledgebase_search_faq.go:78,84,210` |
| 近邻扩展 min/max | **350 / 850 rune** | `merge_expand.go:16-19` |
| 部分重叠阈值 | **0.85** | `search.go:227` |
| 多库扇出并发 / 超时 | **4 / 30s** | `knowledgebase_search_fanout.go:22-25` |
| 单引擎候选扩张（PG） | `min(max(TopK*2,100),200)` | `postgres/repository.go:350-356` |
| HNSW `ef_search` | `expandedTopK`，≥40 | `postgres/repository.go:405-408` |
| query_understand temperature / max tokens | **0.3 / 150(500)** | `query_understand.go:113-127` |
| 实体抽取 temperature / max tokens | **0.3 / 4096** | `extract_entity.go:172-176` |
| Custom Agent 检索默认值 | EmbeddingTopK **10** / KeywordThreshold **0.3** / VectorThreshold **0.5** / RerankTopK **5** / RerankThreshold **0.5** | `types/custom_agent.go:515-527` |
| 引擎注册表：构建超时 / 失败冷却 | **10s / 30s** | `retriever/registry.go:24,30,113` |
| store 解析总预算 | **12s** | `knowledgebase_search_storegroup.go:17-21` |
| embedding 输入安全上限 / 重试 / 退避 / 批大小 / 写并发 | **20000 char / 5 次 / 200ms 指数 / 40 / 5** | `retriever/keywords_vector_hybrid_indexer.go:25,30-31,105,110,129-153,170-175` |
| OpenSearch TopK 兜底 / 上限 / 响应体上限 | **10 / 10000 / 16MB** | `opensearch/retrieve.go:106-119,135-136` |
| 分页默认 / 上限 | **20 / 1000** | `types/search.go:287-296` |
| FAQ 搜索接口 MatchCount 兜底 / 上限 | **10 / 200** | `handler/faq.go:392-397` |
| Agent `knowledge_search` 查询数上限 | **5**（schema `maxItems:5`），KB 数上限 **10** | `agent/tools/knowledge_search.go:80-97` |

---

## 11. 诚实的局限（问题 10）

### 11.1 明确的"不做"

| # | 局限 | 证据 |
|---|---|---|
| 1 | **通用自适应 top-k 不存在**。只有 FAQ KB 有"取不满就翻倍"的迭代（最多 5 轮 / 500）。非 FAQ 的召回不足只靠"查询扩展追加"补偿，不做 top-k 提升。 | `knowledgebase_search_faq.go:40,78-210`；`search.go:141-146` |
| 2 | **`keyword_threshold` 在检索层几乎不生效**。Postgres / SQLite / ES v7+v8 / Qdrant / Milvus 的 `KeywordsRetrieve` 都不读 `params.Threshold`；Qdrant/Milvus 关键词分硬编码 1.0。这是**配置项与行为不一致**的实质性缺陷。 | §5.1 全部引用 |
| 3 | **`config.yaml:21` 的 `enable_rerank` 是死配置**。全仓 grep 仅 1 处命中（定义处）。想关重排只能把 Agent 的 `rerank_model_id` 清空。 | `config/config.go:105`；`chat_pipeline/rerank.go:57-62` |
| 4 | **没有 per-document / per-user ACL 下推到检索**。过滤维度只有 `knowledge_base_id` / `knowledge_id` / `tag_id` / `is_enabled`。ACL 是 KB 粒度的**事后**校验（`authorizeKBAccess` + `permissions.Check`）。 | `postgres/repository.go:174-207,300-335`；`knowledgebase_search.go:170`；`knowledgebase_search_shared.go:45-55,83-95` |
| 5 | **没有 query-type-aware 权重**。RRF 权重是租户级常量，函数签名里根本没有 query。意图（intent）只用于"是否检索"和提示词选择，不参与打分。 | `knowledgebase_search_fusion.go:84-86`；`types/chat_manage.go:102-109` |
| 6 | **没有上下文 token 预算/截断**。进 LLM 的 chunk 数由 `RerankTopK` 和去重决定；仅单 chunk 有 850 rune 上限。长父块（推荐 4096）会原样进入。 | `into_chat_message.go:156-162`；`merge_expand.go:16-19,254-267` |
| 7 | **没有 query decomposition / multi-hop / HyDE**。查询变换 = LLM 改写 + 规则变体；实体路径是**单跳** Neo4j。 | `query_expansion.go:112-113`；`neo4j/repository.go:176-182` |
| 8 | **没有 cross-encoder 之外的召回控制**：pipeline 把**全部候选**丢给 reranker，没有"先取 top-N 再 rerank"的应用层控制（只有驱动内部按 50/60 切批）。 | `rerank.go:75-88,124-128`；`lkeap_reranker.go:16-17`；`volcengine_reranker.go:23` |
| 9 | **没有 per-KB 阈值**。KB 只能选索引，不能调阈值/TPK。租户一套、Agent 一套，颗粒度止步于此。 | `knowledgebase_search.go:401-416`；§10.5 |
| 10 | **两套默认值互不相通**（30/0.2/0.3/30/0.3 vs 50/0.15/0.3/10/0.2）。在 UI 改租户检索配置**不会**影响会话聊天。 | §2.1 |
| 11 | **`RerankThreshold` 在 Agent 覆盖链上无条件下推**，零值会静默禁用重排阈值。与 `EmbeddingTopK` 等四个参数的 `> 0` 判断不对称。 | `session_qa_helpers.go:212-224` |
| 12 | **多库检索失败是 all-or-nothing**，没有部分结果策略（注释自称是已知待改进项）。 | `knowledgebase_search_fanout.go:32-36,89-105` |
| 13 | **无 rerank passage 长度控制**。passage 只做 markdown 清洗，不截断；超长 passage 会整体送往 reranker。 | `rerank.go:594-694` |
| 14 | **自建 Agent 默认关闭改写与查询扩展**。`CustomAgent.EnsureDefaults()` 未给 `EnableRewrite` / `EnableQueryExpansion` 兜底，而 `applyAgentOverridesToChatManage` 是**无条件赋值**（bool 零值 false）→ 自建 Agent 若未显式勾选，改写与扩展都关；内置 Agent 靠 `builtin_agents.yaml:45-46` 显式设 true。副作用：改写关闭 ⇒ 意图分类也关闭 ⇒ 所有 `NeedsRetrieval()` 的意图短路失效。 | `types/custom_agent.go:515-544`；`session_qa_helpers.go:230-231`；`builtin_agents.yaml:45-46`；`query_understand.go:67-74` |
| 15 | **`ENTITY_SEARCH` 注册后从不被 Trigger**（死链）。图检索只能经 `search_parallel.go:140` 的内部直调触发，`EventManager` 上那条监听永不执行。 | `container.go:393`；`search_parallel.go:140`；`session_knowledge_qa.go:187-206` |
| 16 | **图检索的关系数据被丢弃**。`chatManage.GraphResult` 写入后无任何消费者，只有 `node.Chunks` 转成结果。 | `search_entity.go:131-134,188-207`；`types/chat_manage.go:124` |
| 17 | **`ExcludeKnowledgeIDs` / `ExcludeChunkIDs` 在主检索路径上是死字段**：各引擎已实现，但 `buildRetrievalParams` 从不传参。 | `types/retriever.go:51-54`；`knowledgebase_search.go:429-439,459-467` |
| 18 | **RRF 参数无输入校验**。`handler/tenant.go:1761-1781` 只校验 5 个阈值/topk，`rrf_k` 与两个权重完全无校验；`rrf_k` 只判 `<=0`，正数（含 10^9）原样使用 → RRF 分趋近 0。 | `handler/tenant.go:1761-1781`；`retrieval_config.go:87-92` |
| 19 | **多 env 驱动下检索不分流且非确定**。`composite.go` 命中第一个支持该 `RetrieverType` 的引擎即 `break`，而 `engineInfos` 由 map 值收集（顺序随机）→ 配 `RETRIEVE_DRIVER=postgres,qdrant` 时同一次检索落到哪个驱动不确定，也不会双读。 | `composite.go:42-52,87` |
| 20 | **关键词分在部分引擎被硬编码为 1.0**（Qdrant `qdrant/repository.go:694`；Milvus `milvus/repository.go:791`；Doris `doris/repository.go:401,608`）→ 这些引擎上"关键词相关性"完全不存在，只有命中/未命中。 | 同左 |

### 11.2 值得注意的潜在缺陷【推断】

| # | 现象 | 分析 | 证据 |
|---|---|---|---|
| A | **重排驱动的分批与 `Index` 语义值得实测** | 调用方用模型返回的 `rr.Index` 去索引 `candidatesToRerank`（`rerank.go:194-204`），而 `rerank()` 内部还有一次对空 passage 的过滤并基于局部切片 `candidates` 做越界判断（`:325-343,382-384`）。代码中**未见跨批次索引重映射**，而 LKEAP/Volcengine 驱动会按 50/60 分多次请求（`lkeap_reranker.go:111-124`；`volcengine_reranker.go:112-114`）——因此"驱动是否把每批的 index 还原成全局序号"是一个需要实测确认的点。 | `rerank.go:75-88,194-204,316-343`；`lkeap_reranker.go:111-124`；`volcengine_reranker.go:112-114` |
| A2 | **空 passage 过滤可能导致候选被静默丢弃** | `OnEvent` 在构建 passages 时就把空 passage 的候选 `continue` 掉（`rerank.go:78-88`），这些候选**不会进入 `reranked`**，即"内容为空但 score 很高"的块不会被重排也不会被保留。 | `rerank.go:78-88,191-221` |
| A3 | **重复 ChunkID 会占用 rank 编号** | `vectorRanks` 用切片下标 `i+1` 作 rank（`fusion.go:89-94`），融合前没有先 `deduplicateByScore`；若同一 ChunkID 在 `vectorResults` 出现两次，第二个副本仍占一个 rank，使后续 chunk 的 rank 整体后移。引擎侧通常已去重，但融合层没有防御。 | `fusion.go:89-113` |
| B | **租户 `RerankThreshold` 显式 0 时不回退默认 0.2** | `GetEffectiveRerankThreshold` 只在 `c == nil` 时返回 0.2；`c != nil && c.RerankThreshold == 0` 原样返回 0 → 重排阈值过滤被静默禁用。相比 `GetEffectiveVectorThreshold`（`<= 0` 回退 0.15）语义不一致。 | `retrieval_config.go:55-60` vs `:79-84` |
| C | **`minScore` 在 Agent 工具里算了但被弃用** | 打印了 `min_score=%.2f` 却跳过过滤（RRF 分数区间不在 [0,1]）。属历史残留。 | `agent/tools/knowledge_search.go:258-269,345-347` |
| D | **`deduplicateByScore` 在单路时保留原始分，双路时被 RRF 分覆盖** | 意味着 FAQ 的 `FAQDirectAnswerThreshold`（直接比对 embedding 相似度）在"双路都有结果"时比较的是 RRF 分（量级 ~0.016），语义与"相似度"完全不同。FAQ 目前不参与关键词检索（`knowledgebase_search.go:413`），所以该阈值仍与 embedding 相似度可比——但这依赖一个**隐式不变量**：一旦 FAQ 库被允许关键词检索，直答阈值立即失效。 | `fusion.go:34-49`；`into_chat_message.go:51`；`knowledgebase_search.go:413`；docs 注释 `website-docs/03-features/05-retrieval-engines.md:257` |
| E | **FAQ 迭代分支会丢弃 RRF 融合结果** | `applyFAQPostProcessing` 直接 `return iterativeRetrieveWithDeduplication(...)`，把 `HybridSearch` 里的 `deduplicatedChunks`（含 RRF 结果）整体替换为"逐轮向量检索 + 按 ChunkID 取最高分"。因为 FAQ 不参与关键词检索，实际未损失 RRF 增益，但这是**隐式耦合**：fusion 的行为与 FAQ 的索引路由必须保持一致。 | `knowledgebase_search_faq.go:40-48`；`knowledgebase_search.go:287-291,413` |
| F | **`OwnerTenantID` 路径不做所属校验** | KB 未绑定 `VectorStoreID` 时**完全跳过** store 属主校验，直接回退到 env store（进程内共享）——此路径的隔离依赖检索参数上的 `KnowledgeBaseIDs` 过滤，而非存储属主。 | `factory.go:156-162,194-240` |

### 11.3 文档与代码不一致汇总

| 文档 | 文档说 | 代码实际 |
|---|---|---|
| `website-docs/02-architecture/04-rag-pipeline.md:217` | MMR `k=RerankTopK` | `min(len(reranked), max(1, RerankTopK))`（`rerank.go:223`） |
| `website-docs/02-architecture/04-rag-pipeline.md:205-217` | CHUNK_RERANK = 重排→复合→MMR→Wiki 加权 | 中间还有 `MemoryAffinity`（`container.go:396`） |
| `config/config.yaml:21` | `enable_rerank: true` | 该开关无任何读取点 |
| `website-docs/02-architecture/04-rag-pipeline.md:203` | 查询扩展 TopK 放大为 `max(EmbeddingTopK, RerankTopK) * 2` | 等价形式 `max(EmbeddingTopK*2, RerankTopK*2)`（`query_expansion.go:29`）✅ 一致 |
| `website-docs/02-architecture/04-rag-pipeline.md:203` | 触发条件"召回数少于 `EmbeddingTopK`" | 实为 `< max(1, EmbeddingTopK)`（`search.go:141`） |
| `query_expansion.go:112-114` 注释 | "word reordering" 词序调整 | 四类规则里**没有**词序重排（`:140-164`） |
| `website-docs/02-architecture/04-rag-pipeline.md:179` | JSON 解析失败"默认 `kb_search`" | `Intent` 留在**空串**（`query_understand.go:380-396`）；行为等价（`chat_manage.go:104` 的 `""` 分支）但字段值不同 |
| `website-docs/02-architecture/04-rag-pipeline.md:185,505` | 实体抽取用 `graph_extraction.yaml` | 运行时用 `config/config.yaml:91-102` 的 `extract.extract_entity`（`extract_entity.go:41,135-138`；`config.go:465`） |
| `website-docs/02-architecture/04-rag-pipeline.md:104` | `chunk_rerank` = Rerank → WikiBoost | 实为 Rerank → WikiBoost → **MemoryAffinity**（`container.go:396`） |
| `website-docs/03-features/05-retrieval-engines.md:83` | 方法名 `GetRetrieverEngines()` | 实际是 `GetEffectiveEngines()`（`types/tenant.go:137`） |
| `website-docs/03-features/05-retrieval-engines.md:227` | `validateSameEmbeddingModel` 在 `knowledgebase_search_shared.go` | 实际在 `knowledgebase_search_storegroup.go:252` |
| 迁移文件 `migrations/versioned/000000_init.up.sql:139-144` | sessions 表默认 0.5 / 0.5 / 10 / 10 / 0.65 | 与 `config.yaml`（0.3/0.2/30/30/0.3）和 `RetrievalConfig`（0.3/0.15/50/10/0.2）构成**三套并存默认值** |
| 文档未记载 | 图检索跳数/深度 | **单跳硬编码**、无 depth/hop 参数、无 LIMIT；**无任何配置项**（`neo4j/repository.go:176-182`；全仓 grep `MaxHops/GraphDepth` 仅命中无关的 `tenant_skill_source.go:30`） |

---

## 12. 与 RAGFlow 对比时的"提问清单"

若要对齐比较，以下问题在 WeKnora 侧已有明确答案（可直接引用上方条目）：

1. 融合算法是什么、k 和权重是多少？→ 加权 RRF，k=60，0.7/0.3，租户级可配（§4.1）
2. 关键词阈值是否真的生效？→ **基本不生效**（§5.1）
3. top-k 是否自适应？→ 仅 FAQ 类型有迭代翻倍（§3.2）
4. 重排失败是 fail-open 还是 fail-closed？→ 大部分 fail-open，唯一 fail-closed 是模型解析失败（§6.3）
5. 重排是否有候选上限？→ 应用层无，仅驱动内部分批 50/60（§6.2）
6. MMR 的 λ？→ 硬编码 0.7（§6.4）
7. 父块扩展的链式规则？→ text→parent_text；image→text→parent_text，且 image 保留自身识别文本（§7.2）
8. 上下文有 token 预算吗？→ **没有**（§7.6）
9. 查询改写是 LLM 还是规则？→ 改写是 LLM（T=0.3, 150/500 tokens），扩展是规则（≤5 变体）（§8）
10. HyDE / decomposition / multi-hop？→ **都没有**（§11.1 #7）
11. 有文档级 ACL 吗？→ **没有**，只有 KB 级事后校验（§11.1 #4）
12. 阈值被卡死时能不能放宽？→ 只有"用户显式圈定 scope"的静态开关 `DisableRecallThresholds` + 重排层 ×0.7 降级；召回层无自适应放宽（§5.2-5.3）
