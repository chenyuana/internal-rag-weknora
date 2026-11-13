"""Execute the validated database-first production cutover."""
import json
import os
import pathlib
import subprocess
import time
import urllib.request

os.environ['DOCKER_API_VERSION']='1.43'
root=pathlib.Path('D:/weknora-evaluation')
b=pathlib.Path((root/'notes/upgrade-083-cutover-path.txt').read_text().strip())
assert (b/'BACKUP_READY.json').exists(),'Fresh stopped-writer backup required'
cfg=json.loads((b/'compose-files.json').read_text())
expected=json.loads((b/'expected-images.json').read_text())
def run(*args):
    p=subprocess.run(['docker',*args],capture_output=True,text=True)
    if p.returncode: raise RuntimeError('Docker '+args[0]+' failed: '+p.stderr)
    return p.stdout.strip()
compose=['compose','-p','weknora-evaluation','--project-directory',cfg['directory'],
         '-f',cfg['base'],'-f',cfg['old_override'],'-f',str(b/'production-083.json')]
run(*compose,'up','-d','--no-deps','--no-build','--pull','never','postgres')
for _ in range(60):
    p=subprocess.run(['docker','exec','WeKnora-postgres','pg_isready','-U','weknora'],capture_output=True)
    if p.returncode==0: break
    time.sleep(1)
else: raise RuntimeError('New database failed readiness')
run('cp',str(root/'scripts/upgrade-083-extensions.sql'),'WeKnora-postgres:/tmp/upgrade-083-extensions.sql')
dbs=json.loads((b/'BACKUP_READY.json').read_text())['databases']
for db in dbs:
    output=run('exec','WeKnora-postgres','psql','-U','weknora','-d',db,'-v','ON_ERROR_STOP=1','-f','/tmp/upgrade-083-extensions.sql')
    print('Upgraded extension catalog:',db,flush=True)
run(*compose,'up','-d','--no-deps','--no-build','--pull','never','docreader','app','frontend')
for _ in range(90):
    try:
        with urllib.request.urlopen('http://127.0.0.1:18081/health',timeout=3) as r:
            if r.status==200: break
    except Exception: pass
    time.sleep(2)
else: raise RuntimeError('New production application failed health; do not downgrade upgraded DB volume')
for service,name in [('app','WeKnora-app'),('frontend','WeKnora-frontend'),('docreader','WeKnora-docreader'),('postgres','WeKnora-postgres')]:
    actual=json.loads(run('inspect',name))[0]['Image']
    assert actual==expected[service],(service,actual,expected[service])
state=run('exec','WeKnora-postgres','psql','-U','weknora','-d','WeKnora','-Atc',"SELECT version,dirty FROM schema_migrations; SELECT extname,extversion FROM pg_extension WHERE extname IN ('pg_search','vector')")
assert '118|f' in state and 'pg_search|0.25.11' in state and 'vector|0.8.4' in state,state
(b/'production-state-after.txt').write_text(state,encoding='utf-8')
sql=(b/'evidence-snapshot.sql').read_text(encoding='utf-8')
after=run('exec','WeKnora-postgres','psql','-U','weknora','-d','WeKnora','-Atc',sql)
(b/'chunk-hashes-after.csv').write_text(after,encoding='utf-8')
assert after==(b/'chunk-hashes-before.csv').read_text(encoding='utf-8'),'Original evidence changed during cutover'
run('exec','WeKnora-frontend','nginx','-s','reload')
with urllib.request.urlopen('http://127.0.0.1:18080/health',timeout=10) as r: assert r.status==200
(b/'CUTOVER_PASSED.json').write_text(json.dumps({'state':state,'images':expected,'evidence_identical':True},indent=2),encoding='utf-8')
print('Production upgraded: 0.8.3 / migration118 / pg_search0.25.11 / vector0.8.4; original evidence unchanged.',flush=True)
