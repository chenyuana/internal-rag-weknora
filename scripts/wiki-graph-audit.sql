-- Wiki 链接图谱体检脚本（只读）
--
-- 用途：判断某个知识库的 Wiki「图谱」是否正确。
-- 用法：
--   docker exec -i WeKnora-postgres psql -U weknora -d WeKnora -v kb=94e597b5-0142-454d-8919-be3b551bbec7 < scripts/wiki-graph-audit.sql
--   或： pwsh -File scripts/wiki-graph-audit.ps1 -Kb 94e597b5-0142-454d-8919-be3b551bbec7
--
-- 说明：
--   * out_links / in_links / source_refs / chunk_refs / aliases 都是 jsonb，且历史行可能存成
--     JSON 标量 null（jsonb_typeof = 'null'）。对 JSON null 调 jsonb_array_length /
--     jsonb_array_elements_text 会直接报错，所以本脚本一律先做 jsonb_typeof(...)='array' 守卫。
--   * 所有查询都只读，不会写入任何数据。

\pset pager off
\set ON_ERROR_STOP off

\echo '### 0. 页面清点（按类型 / 有出链 / 有入链）'
SELECT page_type,
       count(*) AS pages,
       count(*) FILTER (WHERE jsonb_typeof(out_links) = 'array' AND jsonb_array_length(out_links) > 0) AS has_out,
       count(*) FILTER (WHERE jsonb_typeof(in_links)  = 'array' AND jsonb_array_length(in_links)  > 0) AS has_in,
       count(*) FILTER (WHERE coalesce(jsonb_typeof(in_links),'null') <> 'array'
                          AND coalesce(jsonb_typeof(out_links),'null') <> 'array') AS isolated
FROM wiki_pages
WHERE knowledge_base_id = :'kb' AND deleted_at IS NULL
GROUP BY page_type ORDER BY pages DESC;

\echo '### 1. 悬空链接（out_links 指向不存在的页面）—— 期望 0 行'
SELECT src.slug AS source_slug, t.link AS missing_target
FROM wiki_pages src
CROSS JOIN LATERAL jsonb_array_elements_text(src.out_links) AS t(link)
LEFT JOIN wiki_pages tgt
       ON tgt.knowledge_base_id = src.knowledge_base_id
      AND tgt.slug = t.link AND tgt.deleted_at IS NULL
WHERE src.knowledge_base_id = :'kb' AND src.deleted_at IS NULL
  AND jsonb_typeof(src.out_links) = 'array'
  AND tgt.id IS NULL
ORDER BY 1;

\echo '### 2. in_links / out_links 互反性破坏 —— 期望 0 行'
SELECT src.slug AS source_slug, t.link AS target_slug
FROM wiki_pages src
CROSS JOIN LATERAL jsonb_array_elements_text(src.out_links) AS t(link)
JOIN wiki_pages tgt
  ON tgt.knowledge_base_id = src.knowledge_base_id
 AND tgt.slug = t.link AND tgt.deleted_at IS NULL
WHERE src.knowledge_base_id = :'kb' AND src.deleted_at IS NULL
  AND jsonb_typeof(src.out_links) = 'array'
  AND NOT (jsonb_typeof(tgt.in_links) = 'array' AND tgt.in_links ? src.slug)
ORDER BY 1;

\echo '### 3. 自链接 —— 期望 0 行'
SELECT src.slug AS self_linked_slug
FROM wiki_pages src
CROSS JOIN LATERAL jsonb_array_elements_text(src.out_links) AS t(link)
WHERE src.knowledge_base_id = :'kb' AND src.deleted_at IS NULL
  AND jsonb_typeof(src.out_links) = 'array' AND t.link = src.slug;

\echo '### 4. 弱连通分量（只被 summary/index 连起来的图会退化成 1 个巨分量，别把这个当正确性证据）'
WITH RECURSIVE nodes AS (
  SELECT slug::text AS s, slug::text AS r FROM wiki_pages
   WHERE knowledge_base_id = :'kb' AND deleted_at IS NULL
), edges AS (
  SELECT src.slug::text AS a, t.link::text AS b
  FROM wiki_pages src
  CROSS JOIN LATERAL jsonb_array_elements_text(src.out_links) AS t(link)
  JOIN wiki_pages tgt ON tgt.knowledge_base_id = src.knowledge_base_id
                     AND tgt.slug = t.link AND tgt.deleted_at IS NULL
  WHERE src.knowledge_base_id = :'kb' AND src.deleted_at IS NULL
    AND jsonb_typeof(src.out_links) = 'array'
), und AS (
  SELECT a, b FROM edges UNION SELECT b, a FROM edges
), walk AS (
  SELECT n.r AS root, n.s AS node, 0 AS d FROM nodes n
  UNION
  SELECT w.root, u.b, w.d + 1 FROM walk w JOIN und u ON u.a = w.node WHERE w.d < 15
), assign AS (
  SELECT node, min(root) AS component FROM walk GROUP BY node
)
SELECT count(*) AS components, min(sz) AS min_size, max(sz) AS max_size,
       sum(CASE WHEN sz = 1 THEN 1 ELSE 0 END) AS singletons
FROM (SELECT component, count(*) AS sz FROM assign GROUP BY component) x;

\echo '### 5. 边质量分层：结构性边（summary/index 发出的）vs 语义边'
WITH edge AS (
  SELECT src.slug::text AS s, t.link::text AS tt
  FROM wiki_pages src
  CROSS JOIN LATERAL jsonb_array_elements_text(src.out_links) AS t(link)
  JOIN wiki_pages tgt ON tgt.knowledge_base_id = src.knowledge_base_id
                     AND tgt.slug = t.link AND tgt.deleted_at IS NULL
  WHERE src.knowledge_base_id = :'kb' AND src.deleted_at IS NULL
    AND jsonb_typeof(src.out_links) = 'array'
), j AS (
  SELECT a.page_type AS s_type, b.page_type AS t_type,
    CASE WHEN jsonb_typeof(a.source_refs) = 'array' AND jsonb_typeof(b.source_refs) = 'array'
              AND a.source_refs ?| ARRAY(SELECT jsonb_array_elements_text(b.source_refs))
         THEN 1 ELSE 0 END AS shares_doc,
    CASE WHEN jsonb_typeof(a.chunk_refs) = 'array' AND jsonb_typeof(b.chunk_refs) = 'array'
              AND jsonb_array_length(a.chunk_refs) > 0
              AND a.chunk_refs ?| ARRAY(SELECT jsonb_array_elements_text(b.chunk_refs))
         THEN 1 ELSE 0 END AS shares_chunk
  FROM edge e
  JOIN wiki_pages a ON a.knowledge_base_id = :'kb' AND a.slug = e.s
  JOIN wiki_pages b ON b.knowledge_base_id = :'kb' AND b.slug = e.tt
)
SELECT CASE WHEN s_type = 'summary' THEN 'structural: summary -> page'
            WHEN s_type = 'index'   THEN 'structural: index -> page'
            ELSE 'semantic: ' || s_type || ' -> ' || t_type END AS edge_class,
       count(*) AS edges, sum(shares_doc) AS share_doc, sum(shares_chunk) AS share_chunk
FROM j GROUP BY 1 ORDER BY edges DESC;

\echo '### 6. 同源却未连边（漏链候选）—— 只统计 concept/entity 之间'
SELECT count(*) AS missing_edges_between_pages_sharing_a_source_doc
FROM wiki_pages a JOIN wiki_pages b
  ON a.knowledge_base_id = b.knowledge_base_id AND a.slug < b.slug
 AND a.page_type IN ('concept','entity') AND b.page_type IN ('concept','entity')
 AND jsonb_typeof(a.source_refs) = 'array' AND jsonb_typeof(b.source_refs) = 'array'
 AND a.source_refs ?| ARRAY(SELECT jsonb_array_elements_text(b.source_refs))
WHERE a.knowledge_base_id = :'kb' AND a.deleted_at IS NULL AND b.deleted_at IS NULL
  AND NOT (coalesce(jsonb_typeof(a.out_links),'null') = 'array' AND a.out_links ? b.slug)
  AND NOT (coalesce(jsonb_typeof(b.out_links),'null') = 'array' AND b.out_links ? a.slug);

\echo '### 7. 证据强度最弱的页面（chunk_refs 少且正文短 = 空壳页候选）'
SELECT slug, page_type, jsonb_array_length(chunk_refs) AS chunk_refs, length(content) AS content_len
FROM wiki_pages
WHERE knowledge_base_id = :'kb' AND deleted_at IS NULL
  AND page_type IN ('concept','entity') AND jsonb_typeof(chunk_refs) = 'array'
ORDER BY 3 ASC, 4 ASC LIMIT 15;

\echo '### 8. 同义重复页候选：alias 撞车'
SELECT lower(al.value) AS alias, count(*) AS n, string_agg(w.slug, ' | ') AS slugs
FROM wiki_pages w CROSS JOIN LATERAL jsonb_array_elements_text(w.aliases) AS al(value)
WHERE w.knowledge_base_id = :'kb' AND w.deleted_at IS NULL AND jsonb_typeof(w.aliases) = 'array'
GROUP BY lower(al.value) HAVING count(*) > 1 ORDER BY n DESC, alias;

\echo '### 9. 同一源文档产生多张 summary 页（口径/版本遗留）'
SELECT k.title AS source_doc, string_agg(w.slug, ' | ' ORDER BY w.slug) AS summary_slugs, count(*) AS n
FROM wiki_pages w
CROSS JOIN LATERAL jsonb_array_elements_text(w.source_refs) AS s(ref)
JOIN knowledges k ON k.id = s.ref
WHERE w.knowledge_base_id = :'kb' AND w.deleted_at IS NULL AND w.page_type = 'summary'
  AND jsonb_typeof(w.source_refs) = 'array'
GROUP BY 1 HAVING count(*) > 1 ORDER BY 3 DESC;

\echo '### 10. 死链清洗留痕：正文里仍存在的 [[...]] 链接目标全集（对比第 1 节的悬空清单）'
SELECT g.link AS bracket_target, count(*) AS occurrences
FROM wiki_pages src
CROSS JOIN LATERAL (
  SELECT (regexp_matches(src.content, '\[\[([^\]|]+)(?:\|[^\]]*)?\]\]', 'g'))[1] AS link
) AS g
WHERE src.knowledge_base_id = :'kb' AND src.deleted_at IS NULL
GROUP BY g.link ORDER BY occurrences DESC LIMIT 30;

\echo '### 11. 审计与版本水位'
SELECT 'pages' AS metric, count(*)::text AS value FROM wiki_pages
 WHERE knowledge_base_id = :'kb' AND deleted_at IS NULL
UNION ALL SELECT 'revisions', count(*)::text FROM wiki_page_revisions WHERE knowledge_base_id = :'kb'
UNION ALL SELECT 'issues_open', count(*)::text FROM wiki_page_issues
 WHERE knowledge_base_id = :'kb' AND deleted_at IS NULL AND status = 'pending'
UNION ALL SELECT 'pending_wiki_ops', count(*)::text FROM task_pending_ops
 WHERE scope_id = :'kb' AND task_type IN ('wiki:ingest','wiki:finalize');

\echo '### 12. 出/入度榜（找枢纽页与孤岛页；孤岛 = 只被 summary 链接）'
SELECT slug, page_type,
       coalesce(jsonb_array_length(out_links), 0) AS outl,
       coalesce(jsonb_array_length(in_links), 0) AS inl
FROM wiki_pages
WHERE knowledge_base_id = :'kb' AND deleted_at IS NULL
  AND jsonb_typeof(out_links) = 'array'
ORDER BY jsonb_array_length(out_links) DESC LIMIT 10;

SELECT slug, page_type, coalesce(jsonb_array_length(in_links),0) AS inl
FROM wiki_pages
WHERE knowledge_base_id = :'kb' AND deleted_at IS NULL
  AND jsonb_typeof(in_links) = 'array'
ORDER BY jsonb_array_length(in_links) DESC LIMIT 10;
