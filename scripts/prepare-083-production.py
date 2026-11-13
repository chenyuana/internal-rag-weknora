"""Capture the running deployment and take a fresh stopped-writer backup."""
import datetime
import hashlib
import json
import os
import pathlib
import subprocess

os.environ['DOCKER_API_VERSION']='1.43'
root=pathlib.Path('D:/weknora-evaluation')
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
backup=root/'backups'/('cutover-083-'+stamp)
backup.mkdir()
identity=subprocess.check_output(['whoami'],text=True).strip()
subprocess.run(['icacls',str(backup),'/inheritance:r','/grant:r',identity+':(OI)(CI)F','SYSTEM:(OI)(CI)F','Administrators:(OI)(CI)F'],check=True,capture_output=True)
def run(*args):
    p=subprocess.run(['docker',*args],capture_output=True,text=True)
    if p.returncode: raise RuntimeError('Docker '+args[0]+' failed: '+p.stderr)
    return p.stdout.strip()
containers=json.loads(run('inspect','WeKnora-app','WeKnora-frontend','WeKnora-docreader','WeKnora-postgres'))
(backup/'containers-before.json').write_text(json.dumps(containers,indent=2),encoding='utf-8')
original=pathlib.Path('C:/Users/Win11/.codex/worktrees/weknora-082-upgrade/weknora-evaluation')
base=str(original/'docker-compose.yml')
old_override='D:/weknora-evaluation/backups/pre-chunk-enrichment-20261013/compose.enrichment.json'
services={}
images={'app':'weknora-app:internal-rag-083-20261016','frontend':'weknora-ui:internal-rag-083-20261016','docreader':'wechatopenai/weknora-docreader:v0.8.3','postgres':'paradedb/paradedb:v0.25.11-pg17'}
expected={}
for c in containers:
    service=c['Config']['Labels']['com.docker.compose.service']
    env=dict(v.split('=',1) for v in c['Config']['Env'])
    services[service]={'image':images[service], 'environment':{k:v.replace('$','$$') for k,v in env.items()}}
    expected[service]=json.loads(run('image','inspect',images[service]))[0]['Id']
services['app']['volumes']=['D:/weknora-083-upgrade/config/config.yaml:/app/config/config.yaml']
(backup/'production-083.json').write_text(json.dumps({'services':services},indent=2),encoding='utf-8')
(backup/'expected-images.json').write_text(json.dumps(expected,indent=2),encoding='utf-8')
(root/'notes/upgrade-083-cutover-path.txt').write_text(str(backup),encoding='utf-8')
(backup/'compose-files.json').write_text(json.dumps({'directory':str(original),'base':base,'old_override':old_override},indent=2),encoding='utf-8')
# Stop only WeKnora writers. Shared MinIO/RAGFlow remain available; the existing
# snapshot remains their baseline backup, not a claimed all-service snapshot.
run('stop','--timeout','60','WeKnora-app','WeKnora-frontend')
try:
    dbs=run('exec','WeKnora-postgres','psql','-U','weknora','-d','postgres','-Atc',"SELECT datname FROM pg_database WHERE datallowconn ORDER BY datname").splitlines()
    for i,db in enumerate(dbs):
        remote='/tmp/cutover-083-'+str(i)+'.dump'
        run('exec','WeKnora-postgres','pg_dump','-U','weknora','-d',db,'-Fc','-f',remote)
        dest=backup/('database-'+db+'.dump')
        run('cp','WeKnora-postgres:'+remote,str(dest))
        toc=run('exec','WeKnora-postgres','pg_restore','-l',remote)
        (backup/('database-'+db+'-toc.txt')).write_text(toc,encoding='utf-8')
        print('Backed up database:',db,flush=True)
    run('exec','WeKnora-postgres','sh','-c','pg_dumpall -U weknora --globals-only > /tmp/cutover-083-globals.sql')
    run('cp','WeKnora-postgres:/tmp/cutover-083-globals.sql',str(backup/'globals.sql'))
    sql="COPY (SELECT id, md5(concat_ws('|',knowledge_id,knowledge_base_id,chunk_index::text,content,source_content,metadata::text,start_at::text,end_at::text,chunk_type,parent_chunk_id,pre_chunk_id,next_chunk_id,image_info,is_enabled::text,deleted_at::text)) FROM chunks ORDER BY id) TO STDOUT WITH CSV"
    (backup/'evidence-snapshot.sql').write_text(sql,encoding='utf-8')
    data=run('exec','WeKnora-postgres','psql','-U','weknora','-d','WeKnora','-Atc',sql)
    (backup/'chunk-hashes-before.csv').write_text(data,encoding='utf-8')
    run('cp','WeKnora-app:/data/files',str(backup/'data-files'))
    (backup/'BACKUP_READY.json').write_text(json.dumps({'databases':dbs,'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in backup.glob('*.dump')}},indent=2),encoding='utf-8')
    print('CUTOVER_BACKUP_READY='+str(backup),flush=True)
except Exception:
    run('start','WeKnora-app','WeKnora-frontend')
    raise
