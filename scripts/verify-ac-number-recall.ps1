# Read-only diagnostic: does a document named by its number reach the candidate
# list that HybridSearch returns?
#
# It answers the question the bug report is actually about. A question that only
# names a document ("AC_20-27G的主要内容是什么") carries no semantic signal for
# the vector channel and no rare token for the keyword channel, so the document
# can lose the ranking outright. Measuring only the final answer hides which
# stage dropped it, so this script reports each stage separately:
#
#   1. keyword (BM25) rank of the named document
#   2. vector rank of the named document
#   3. fused (RRF) rank, and the score cutoff at the MatchCount bound
#   4. what the named-document lookup contributes, and whether that survives
#
# Nothing here writes to the database, the application, or the index. It talks
# to PostgreSQL read-only and to the embedding model over HTTP.
#
# Keep this file ASCII-only: Windows PowerShell 5.1 reads a BOM-less script as
# ANSI and would mangle any non-ASCII character.
#
# Usage:
#   .\scripts\verify-ac-number-recall.ps1 -Query 'AC_20-27G query text' -ExpectedNumber '20-27G'

[CmdletBinding()]
param(
    # The user's verbatim question.
    [Parameter(Mandatory = $true)][string]$Query,
    # The document number that question names, normalised as "20-27G".
    [Parameter(Mandatory = $true)][string]$ExpectedNumber,
    # Knowledge base to search. Defaults to the FAA-AC base in this deployment.
    [string]$KnowledgeBaseId = 'cc7d315c-985e-4ae6-859a-db47393d63d0',
    # Mirrors conversation.embedding_top_k: the bound HybridSearch truncates to.
    [int]$MatchCount = 30,
    # Mirrors the tenant RRF configuration.
    [int]$RrfK = 60,
    [double]$VectorWeight = 0.7,
    [double]$KeywordWeight = 0.3,
    # Retrieval depth per channel, matching matchCount = max(MatchCount*5, 50).
    [int]$ChannelDepth = 150,
    # Mirrors exactDocumentChunkBudget: passages one resolved document may add.
    [int]$LookupBudget = 3,
    # Which embedding dimension to rank against. This deployment uses 1024.
    [int]$Dimension = 1024,
    [string]$PgContainer = 'WeKnora-postgres',
    [string]$PgUser = 'weknora',
    [string]$PgDatabase = 'WeKnora',
    [string]$OllamaUrl = 'http://127.0.0.1:11434',
    [string]$EmbeddingModel = 'qwen3-embedding:0.6b'
)

$ErrorActionPreference = 'Stop'

function Invoke-Psql {
    param([string]$Sql)
    $rows = $Sql | docker exec -i $PgContainer psql -U $PgUser -d $PgDatabase -A -F'|' -t
    if ($LASTEXITCODE -ne 0) { throw "psql failed" }
    return $rows
}

function Get-QueryEmbeddingLiteral {
    param([string]$Text)
    $payload = @{
        model    = $EmbeddingModel
        input    = @($Text)
        options  = @{ num_ctx = 511 }
        truncate = $true
    } | ConvertTo-Json -Depth 6 -Compress
    $body = [System.Text.Encoding]::UTF8.GetBytes($payload)
    $response = Invoke-RestMethod -Uri "$OllamaUrl/api/embed" -Method Post `
        -Body $body -ContentType 'application/json; charset=utf-8'
    $culture = [System.Globalization.CultureInfo]::InvariantCulture
    $values = $response.embeddings[0] | ForEach-Object { ([double]$_).ToString($culture) }
    return '[' + ($values -join ',') + ']'
}

$escapedQuery = $Query.Replace("'", "''")
$escapedNumber = $ExpectedNumber.Replace("'", "''")

Write-Host "query    : $Query"
Write-Host "document : AC_$ExpectedNumber"
Write-Host "kb       : $KnowledgeBaseId"
Write-Host ""

# --- Which document is being tracked? Without this the run would silently
# --- measure nothing when the name does not resolve.
$documentRow = Invoke-Psql @"
select k.id, k.file_name
from knowledges k
where k.knowledge_base_id = '$KnowledgeBaseId'
  and k.parse_status = 'completed'
  and k.enable_status = 'enabled'
  and (upper(k.file_name) like 'AC_$escapedNumber%'
       or upper(k.file_name) like 'AC $escapedNumber%'
       or upper(k.file_name) like 'AC$escapedNumber%')
order by k.file_name
limit 5;
"@
if (-not $documentRow) { throw "no document named AC_$ExpectedNumber in knowledge base $KnowledgeBaseId" }
Write-Host "resolved documents:"
$documentRow | ForEach-Object { Write-Host "  $_" }
$KnowledgeIds = ($documentRow | ForEach-Object { ($_ -split '\|')[0] }) -join "','"
Write-Host ""

# The embedding must be computed before the SQL fragments below interpolate it.
$vectorLiteral = Get-QueryEmbeddingLiteral -Text $Query

$rankExpr = "coalesce($VectorWeight / ($RrfK + v.vr), 0) + coalesce($KeywordWeight / ($RrfK + k.kr), 0)"
$vectorPool = @"
vpool as (
  select e.id, e.knowledge_id,
         row_number() over (order by e.embedding::halfvec($Dimension) <=> '$vectorLiteral'::halfvec($Dimension)) as vr
  from embeddings e
  where e.knowledge_base_id = '$KnowledgeBaseId' and e.dimension = $Dimension
  order by e.embedding::halfvec($Dimension) <=> '$vectorLiteral'::halfvec($Dimension)
  limit $ChannelDepth
)
"@
$keywordPool = @"
kpool as (
  select e.id, e.knowledge_id,
         row_number() over (order by paradedb.score(e.id) desc) as kr
  from embeddings e
  where e.knowledge_base_id = '$KnowledgeBaseId' and e.content ||| '$escapedQuery'
  order by paradedb.score(e.id) desc
  limit $ChannelDepth
)
"@

# --- Stage 1: keyword channel ------------------------------------------------
$keywordRank = Invoke-Psql @"
with pool as (
  select e.knowledge_id,
         row_number() over (order by paradedb.score(e.id) desc) as rank
  from embeddings e
  where e.knowledge_base_id = '$KnowledgeBaseId'
    and e.content ||| '$escapedQuery'
  order by paradedb.score(e.id) desc
  limit $ChannelDepth
)
select coalesce(min(rank)::text, 'not in top $ChannelDepth')
from pool where knowledge_id in ('$KnowledgeIds');
"@
Write-Host "1. keyword (BM25) best rank : $keywordRank"

# --- Stage 2: vector channel -------------------------------------------------
$vectorRank = Invoke-Psql @"
with $vectorPool
select coalesce(min(vr)::text, 'not in top $ChannelDepth')
from vpool where knowledge_id in ('$KnowledgeIds');
"@
Write-Host "2. vector best rank         : $vectorRank"

# --- Stage 3: fusion, and the bound HybridSearch truncates to ----------------
$fused = Invoke-Psql @"
with $vectorPool, $keywordPool, fused as (
  select coalesce(v.knowledge_id, k.knowledge_id) as knowledge_id,
         $rankExpr as rrf
  from vpool v full outer join kpool k on k.id = v.id
)
select
  coalesce((select min(rank)::text from (
      select row_number() over (order by rrf desc) as rank, knowledge_id from fused
  ) t where knowledge_id in ('$KnowledgeIds')), 'not in top ' || $MatchCount) as target_rank,
  (select round(min(rrf)::numeric, 6)::text from (
      select rrf from fused order by rrf desc limit $MatchCount
  ) t) as cutoff,
  (select count(*)::text from (
      select knowledge_id from fused order by rrf desc limit $MatchCount
  ) t where knowledge_id in ('$KnowledgeIds')) as target_chunks_in_bound,
  (select count(distinct knowledge_id)::text from (
      select knowledge_id from fused order by rrf desc limit $MatchCount
  ) t) as documents_in_bound;
"@
$fusedParts = ($fused -split '\|')
Write-Host "3. fused (RRF) best rank    : $($fusedParts[0])"
Write-Host "   score at bound $MatchCount       : $($fusedParts[1])"
Write-Host "   target chunks within bound: $($fusedParts[2])"
Write-Host "   documents within bound    : $($fusedParts[3])"

# --- Stage 4: what the named-document lookup adds ---------------------------
# The lookup runs the ordinary hybrid retrieval scoped to the resolved document
# and prepends its top LookupBudget passages, so the document contributes the
# best of its own ranking instead of the rank it lost corpus-wide.
$scopedVectorPool = @"
svpool as (
  select e.id,
         row_number() over (order by e.embedding::halfvec($Dimension) <=> '$vectorLiteral'::halfvec($Dimension)) as vr
  from embeddings e
  where e.knowledge_base_id = '$KnowledgeBaseId' and e.dimension = $Dimension
    and e.knowledge_id in ('$KnowledgeIds')
  order by e.embedding::halfvec($Dimension) <=> '$vectorLiteral'::halfvec($Dimension)
  limit $ChannelDepth
)
"@
$scopedKeywordPool = @"
skpool as (
  select e.id,
         row_number() over (order by paradedb.score(e.id) desc) as kr
  from embeddings e
  where e.knowledge_base_id = '$KnowledgeBaseId'
    and e.knowledge_id in ('$KnowledgeIds')
    and e.content ||| '$escapedQuery'
  order by paradedb.score(e.id) desc
  limit $ChannelDepth
)
"@
$scoped = Invoke-Psql @"
with $scopedVectorPool, $scopedKeywordPool, scoped as (
  select $rankExpr as rrf
  from svpool v full outer join skpool k on k.id = v.id
)
select (select count(*)::text from (select rrf from scoped order by rrf desc limit $LookupBudget) t),
       coalesce((select round(max(rrf)::numeric, 6)::text from scoped), '0'),
       coalesce((select round(min(rrf)::numeric, 6)::text from (select rrf from scoped order by rrf desc limit $LookupBudget) t), '0');
"@
$scopedParts = ($scoped -split '\|')
Write-Host "4. lookup adds              : $($scopedParts[0]) passage(s), RRF $($scopedParts[2]) .. $($scopedParts[1])"
Write-Host ""

if ([int]$fusedParts[2] -gt 0) {
    Write-Host "RESULT: AC_$ExpectedNumber reaches the candidate list on ranking alone."
} else {
    Write-Host "RESULT: AC_$ExpectedNumber is absent from the candidate list on ranking alone."
    if ([int]$scopedParts[0] -gt 0) {
        Write-Host "        The named-document lookup supplies $($scopedParts[0]) passage(s); its weakest"
        Write-Host "        supplied score $($scopedParts[2]) vs the bound cutoff $($fusedParts[1])."
    } else {
        Write-Host "        The lookup found no passages either; the document contributes nothing."
    }
}
