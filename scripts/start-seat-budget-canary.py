import json,subprocess
cfg=json.loads(subprocess.check_output(['docker','inspect','WeKnora-app'],text=True))[0]
env=dict(x.split('=',1) for x in cfg['Config']['Env']);net=next(iter(cfg['NetworkSettings']['Networks']))
def run(args):
 p=subprocess.run(['docker',*args],capture_output=True,text=True)
 if p.returncode:raise RuntimeError('Docker '+args[0]+' failed: '+p.stderr[-1000:])
 return p.stdout.strip()
run(['run','-d','--name','weknora-seat-budget-redis','--network',net,'redis:7.0-alpine'])
env.update(REDIS_ADDR='weknora-seat-budget-redis:6379',REDIS_PASSWORD='',REDIS_DB='0',AUTO_MIGRATE='false',WEKNORA_REDIS_NAMESPACE='seat-budget-canary',LANGFUSE_ENABLE='false')
args=['run','-d','--name','weknora-seat-budget-canary','--network',net,'-p','127.0.0.1:18084:8080']
for k,v in env.items():args+=['-e',k+'='+v]
for m in cfg['Mounts']:
 src=m['Name'] if m['Type']=='volume' else m['Source'];args+=['-v',src+':'+m['Destination']+('' if m['RW'] else ':ro')]
args+=['weknora-app:seat-budget-20261028'];run(args)
print('Seat-budget candidate running on 18084 with independent Redis')
