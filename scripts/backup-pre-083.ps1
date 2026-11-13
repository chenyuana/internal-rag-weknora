$ErrorActionPreference = 'Stop'
$deployRoot = 'C:\Users\Win11\.codex\worktrees\weknora-082-upgrade\weknora-evaluation'
$stamp = [TimeZoneInfo]::ConvertTimeBySystemTimeZoneId([DateTime]::UtcNow, 'China Standard Time').ToString('yyyyMMdd-HHmmss')
$backupRoot = "D:\weknora-evaluation\backups\pre-083-$stamp"
New-Item -ItemType Directory -Path $backupRoot | Out-Null
$identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
icacls $backupRoot /inheritance:r /grant:r "${identity}:(OI)(CI)F" 'SYSTEM:(OI)(CI)F' 'Administrators:(OI)(CI)F' | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Backup ACL failed' }
Set-Content -LiteralPath 'D:\weknora-evaluation\notes\upgrade-083-backup-path.txt' -Value $backupRoot
function Check($label) { if ($LASTEXITCODE -ne 0) { throw "$label failed: $LASTEXITCODE" } }
git -C $deployRoot bundle create "$backupRoot/repository.bundle" --all; Check 'git bundle'
git -C $deployRoot diff --binary --output="$backupRoot/deployment-working.patch"; Check 'working patch'
git -C $deployRoot status --porcelain=v1 --untracked-files=all | Set-Content "$backupRoot/deployment-status.txt"
git -C $deployRoot rev-parse HEAD | Set-Content "$backupRoot/deployment-head.txt"
tar -czf "$backupRoot/deployment-source.tar.gz" --exclude=.git --exclude=node_modules --exclude=dist --exclude=.venv -C $deployRoot .; Check 'source archive'
Copy-Item -LiteralPath "$deployRoot/.env" -Destination "$backupRoot/deployment.env"
Copy-Item -LiteralPath 'D:\weknora-evaluation\backups\pre-chunk-enrichment-20261013\compose.enrichment.json' -Destination "$backupRoot/compose.enrichment.json"
Copy-Item -LiteralPath 'D:\weknora-evaluation\scripts\start-verified-enrichment.ps1' -Destination "$backupRoot/start-before.ps1"
docker inspect WeKnora-app WeKnora-frontend WeKnora-docreader WeKnora-postgres WeKnora-redis docker-minio-1 | Set-Content "$backupRoot/containers.json"; Check 'container inspect'
docker exec WeKnora-postgres pg_dump -U weknora -d WeKnora -Fc -f /tmp/weknora-pre-083.dump; Check 'database dump'
docker cp WeKnora-postgres:/tmp/weknora-pre-083.dump "$backupRoot/database.dump"; Check 'database copy'
docker exec WeKnora-postgres sh -c 'pg_dumpall -U weknora --globals-only > /tmp/weknora-pre-083-globals.sql'; Check 'roles dump'
docker cp WeKnora-postgres:/tmp/weknora-pre-083-globals.sql "$backupRoot/globals.sql"; Check 'roles copy'
docker exec WeKnora-postgres pg_restore -l /tmp/weknora-pre-083.dump | Set-Content "$backupRoot/database-toc.txt"; Check 'dump TOC'
$sql = "COPY (SELECT id, md5(concat_ws('|',knowledge_id,knowledge_base_id,content,source_content,metadata::text,start_at::text,end_at::text,chunk_type,parent_chunk_id,pre_chunk_id,next_chunk_id,image_info,is_enabled::text,deleted_at::text)) AS evidence_hash FROM chunks ORDER BY id) TO STDOUT WITH CSV"
docker exec WeKnora-postgres psql -U weknora -d WeKnora -Atc $sql | Set-Content "$backupRoot/chunk-hashes.csv"; Check 'evidence snapshot'
docker exec WeKnora-postgres psql -U weknora -d WeKnora -Atc 'SELECT version,dirty FROM schema_migrations; SELECT extname,extversion FROM pg_extension; SELECT count(*) FROM chunks;' | Set-Content "$backupRoot/database-state.txt"; Check 'db state'
docker run --rm -v weknora-evaluation_data-files:/source:ro -v "${backupRoot}:/backup" alpine tar -czf /backup/data-files.tar.gz -C /source .; Check 'file archive'
docker run --rm -v docker_minio_data:/source:ro -v "${backupRoot}:/backup" alpine tar -czf /backup/minio-data.tar.gz -C /source .; Check 'object archive'
docker exec WeKnora-redis redis-cli SAVE | Set-Content "$backupRoot/redis-save.txt"; Check 'redis save'
docker cp WeKnora-redis:/data/dump.rdb "$backupRoot/redis-dump.rdb"; Check 'redis copy'
foreach ($item in @(@('WeKnora-app','app'),@('WeKnora-frontend','ui'),@('WeKnora-docreader','docreader'),@('WeKnora-postgres','postgres'))) {
    $id = docker inspect $item[0] --format '{{.Image}}'; Check 'image id'
    docker tag $id "weknora-rollback:$($item[1])-$stamp"; Check 'rollback tag'
}
docker save -o "$backupRoot/rollback-images.tar" "weknora-rollback:app-$stamp" "weknora-rollback:ui-$stamp" "weknora-rollback:docreader-$stamp" "weknora-rollback:postgres-$stamp"; Check 'image archive'
$manifest = Get-ChildItem -LiteralPath $backupRoot -File | ForEach-Object { @{name=$_.Name; bytes=$_.Length; sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash} }
$manifest | ConvertTo-Json -Depth 5 | Set-Content "$backupRoot/manifest.json"
Write-Output "BACKUP_COMPLETE=$backupRoot"
Write-Output 'Online baseline backup; a fresh stopped-writer backup is still required immediately before production migration.'
