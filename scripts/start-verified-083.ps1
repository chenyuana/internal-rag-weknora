$ErrorActionPreference = 'Stop'
$env:DOCKER_API_VERSION = '1.43'
$deployRoot = 'C:/Users/Win11/.codex/worktrees/weknora-082-upgrade/weknora-evaluation'
$cutoverRoot = (Get-Content -LiteralPath 'D:/weknora-evaluation/notes/upgrade-083-cutover-path.txt' -Raw).Trim()
if (-not (Test-Path -LiteralPath "$cutoverRoot/CUTOVER_PASSED.json")) { throw 'Verified 0.8.3 cutover record is missing' }
$expected = Get-Content -LiteralPath "$cutoverRoot/expected-images.json" -Raw | ConvertFrom-Json
$actual = docker image inspect weknora-app:internal-rag-083-20261016 --format '{{.Id}}'
if ($LASTEXITCODE -ne 0 -or $actual -ne $expected.app) { throw 'Application image differs from the validated image' }
docker compose -p weknora-evaluation --project-directory $deployRoot -f "$deployRoot/docker-compose.yml" -f 'D:/weknora-evaluation/backups/pre-chunk-enrichment-20261013/compose.enrichment.json' -f "$cutoverRoot/production-083.json" up -d --no-deps --no-build --pull never app
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
docker exec WeKnora-frontend nginx -s reload
exit $LASTEXITCODE
