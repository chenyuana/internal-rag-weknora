"""Start the upgrade candidate against cloned DB and a fresh task queue."""
import json
import os
import pathlib
import subprocess

os.environ['DOCKER_API_VERSION'] = '1.43'
root = pathlib.Path('D:/weknora-evaluation')
backup = pathlib.Path((root / 'notes/upgrade-083-backup-path.txt').read_text().strip())
def run(*args):
    return subprocess.check_output(['docker', *args], text=True).strip()
cfg = json.loads(run('inspect', 'WeKnora-app'))[0]
env = dict(x.split('=', 1) for x in cfg['Config']['Env'])
db_cfg = json.loads(run('inspect', 'weknora083-db'))[0]
db_env = dict(x.split('=', 1) for x in db_cfg['Config']['Env'])
env.update(DB_HOST='weknora083-db', DB_NAME='restore083_verified', DB_PORT='5432',
           DB_USER=db_env['POSTGRES_USER'], DB_PASSWORD=db_env['POSTGRES_PASSWORD'],
           REDIS_ADDR='weknora083-redis:6379', REDIS_PASSWORD='', REDIS_DB='0',
           WEKNORA_REDIS_NAMESPACE='upgrade083-validation', AUTO_MIGRATE='true',
           NEO4J_ENABLE='false', DOCREADER_ADDR='weknora083-docreader:50051',
           STORAGE_TYPE='local', LOCAL_STORAGE_BASE_DIR='/data/files',
           LOG_LEVEL='info', LANGFUSE_ENABLE='false')
# Keys are kept only in the already restricted backup directory.
env_path = backup / 'validation.env'
env_path.write_text(''.join(f'{k}={v}\n' for k,v in env.items() if '\n' not in v), encoding='utf-8')
networks = run('network', 'ls', '--format', '{{.Name}}').splitlines()
if 'weknora083-validation' not in networks:
    run('network', 'create', 'weknora083-validation')
db_networks = db_cfg['NetworkSettings']['Networks']
if db_cfg['HostConfig']['NetworkMode'] == 'none':
    db_env_path = backup / 'validation-db.env'
    db_env_path.write_text(''.join(f'{k}={v}\n' for k,v in db_env.items()), encoding='utf-8')
    run('stop', 'weknora083-db')
    run('rename', 'weknora083-db', 'weknora083-db-offline')
    run('run', '-d', '--name', 'weknora083-db', '--network', 'weknora083-validation', '--shm-size=1g',
        '--env-file', str(db_env_path), '-v', 'weknora083-restore-data:/var/lib/postgresql/data',
        'paradedb/paradedb:v0.25.11-pg17')
    db_networks = {'weknora083-validation': {}}
if 'weknora083-validation' not in db_networks:
    run('network', 'connect', 'weknora083-validation', 'weknora083-db')
run('exec', 'weknora083-db', 'psql', '-U', 'weknora', '-d', 'restore083_verified', '-v', 'ON_ERROR_STOP=1', '-c',
    "UPDATE data_sources SET sync_schedule=''; UPDATE im_channels SET enabled=false; UPDATE knowledge_bases SET is_temporary=false WHERE is_temporary=true;")
run('run', '-d', '--name', 'weknora083-redis', '--network', 'weknora083-validation', 'redis:7.0-alpine')
run('run', '-d', '--name', 'weknora083-app', '--network', 'weknora083-validation', '--env-file', str(env_path),
    '-p', '127.0.0.1:18083:8080', '-v', str(backup/'data-files')+':/data/files:ro',
    '-v', 'D:/weknora-083-upgrade/config/config.yaml:/app/config/config.yaml:ro',
    'weknora-app:internal-rag-083-20261016')
print('Validation app started on 127.0.0.1:18083; cloned DB, fresh Redis, disabled sync/IM and read-only file snapshot.')
