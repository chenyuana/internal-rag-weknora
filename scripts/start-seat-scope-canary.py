import json
import subprocess

def run(args):
    p = subprocess.run(['docker', *args], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError('Docker ' + args[0] + ' failed: ' + p.stderr[-1000:])
    return p.stdout.strip()

cfg = json.loads(run(['inspect','WeKnora-app']))[0]
env = dict(x.split('=',1) for x in cfg['Config']['Env'])
network = next(iter(cfg['NetworkSettings']['Networks']))
# Use a checked-empty logical database; avoid waiting on an unrelated Docker
# anonymous-volume initialization while leaving production Redis DB untouched.
redis_env = ['-e','REDISCLI_AUTH='+env.get('REDIS_PASSWORD','')]
count = run(['exec',*redis_env,'WeKnora-redis','redis-cli','-n','15','DBSIZE'])
if count != '0': raise RuntimeError('Redis DB15 is not empty; refusing to share candidate state')
env.update(REDIS_DB='15',
           AUTO_MIGRATE='false', LANGFUSE_ENABLE='false', WEKNORA_EVIDENCE_BUDGET_ENABLED='false',
           WEKNORA_REDIS_NAMESPACE='seat-scope-canary')
args = ['create','--name','weknora-seat-scope-canary','--network',network,'-p','127.0.0.1:18085:8080']
for k,v in env.items():args += ['-e',k+'='+v]
for m in cfg['Mounts']:
    src = m['Name'] if m['Type']=='volume' else m['Source']
    args += ['-v',src+':'+m['Destination']+('' if m['RW'] else ':ro')]
args += [cfg['Config']['Image']]
run(args)
run(['cp','notes/WeKnora-seat-scope-20261029','weknora-seat-scope-canary:/app/WeKnora'])
run(['start','weknora-seat-scope-canary'])
print('Scope candidate started on 18085; isolated Redis DB15, shared existing DB; migrations disabled')
