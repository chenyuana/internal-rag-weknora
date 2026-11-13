# Wiki 链接图谱体检（只读）—— scripts/wiki-graph-audit.sql 的调用包装
#
# 用法：
#   # 1) 列出所有开启了 Wiki 的知识库，拿到 kb id
#   pwsh -File scripts/wiki-graph-audit.ps1 -List
#
#   # 2) 体检指定知识库
#   pwsh -File scripts/wiki-graph-audit.ps1 -Kb 94e597b5-0142-454d-8919-be3b551bbec7
#
#   # 3) 导出到文件（便于归档 / diff 两次体检结果）
#   pwsh -File scripts/wiki-graph-audit.ps1 -Kb <kbID> -Out notes\wiki-graph-audit.md
#
# 说明：默认连本机 docker 容器 WeKnora-postgres 里的 WeKnora 库，
#       与仓库根目录 .env 中 DB_* 的默认部署一致。不做任何写操作。

[CmdletBinding()]
param(
    [string]$Kb = '',
    [switch]$List,
    [string]$Container = 'WeKnora-postgres',
    [string]$DbUser = 'weknora',
    [string]$DbName = 'WeKnora',
    [string]$Out = ''
)

$ErrorActionPreference = 'Stop'
$env:PGCLIENTENCODING = 'UTF8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$repoRoot = Split-Path -Parent $PSScriptRoot
$sqlFile = Join-Path $PSScriptRoot 'wiki-graph-audit.sql'
if (-not (Test-Path $sqlFile)) { throw "找不到 $sqlFile" }

function Invoke-Psql {
    param([string]$Sql)
    # 走 stdin，避免 PowerShell 二次解析 SQL 里的 $ / 引号
    $Sql | docker exec -i $Container psql -U $DbUser -d $DbName
}

if ($List) {
    $sql = @'
SELECT id, name, (indexing_strategy->>'wiki_enabled') AS wiki_enabled,
       (SELECT count(*) FROM wiki_pages p
         WHERE p.knowledge_base_id = kb.id AND p.deleted_at IS NULL) AS pages
FROM knowledge_bases kb
WHERE indexing_strategy->>'wiki_enabled' = 'true'
ORDER BY pages DESC;
'@
    Invoke-Psql $sql
    return
}

if (-not $Kb) {
    Write-Host '缺少 -Kb <kbID>；先运行 -List 查看可选知识库。' -ForegroundColor Yellow
    exit 2
}

# 脚本里用 :'kb' 引用变量，这里通过 psql -v 注入
$sql = Get-Content $sqlFile -Raw -Encoding UTF8
$result = $sql | docker exec -i $Container psql -U $DbUser -d $DbName -v "kb=$Kb" 2>&1 |
    ForEach-Object { $_.ToString() }

if ($Out) {
    $outPath = if ([System.IO.Path]::IsPathRooted($Out)) { $Out } else { Join-Path $repoRoot $Out }
    $header = @(
        "# Wiki 链接图谱体检报告",
        "",
        "- 知识库: ``$Kb``",
        "- 生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
        "- 脚本: ``scripts/wiki-graph-audit.sql``",
        "",
        '```'
    )
    ($header + $result + @('```')) | Set-Content -Path $outPath -Encoding UTF8
    Write-Host "已写入 $outPath" -ForegroundColor Green
}

$result
