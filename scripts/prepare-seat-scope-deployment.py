import json
import shutil
from pathlib import Path

root = Path('backups/seat-scope-20261029').resolve()
prior = Path('backups/seat-budget-20261028').resolve()
base = json.loads((prior/'runtime-before.json').read_text(encoding='utf8'))['compose_base']
base += ['-f',str(prior/'compose.seat-prompt.json')]
(root/'runtime-before.json').write_text(json.dumps({'tag':'weknora-app:seat-prompt-20261028','compose_base':base},indent=2),encoding='utf8')
override = {'services':{'app':{'image':'weknora-app:seat-scope-20261029',
    'environment':{'AUTO_MIGRATE':'false','WEKNORA_EVIDENCE_BUDGET_ENABLED':'false'}}}}
(root/'compose.seat-scope.json').write_text(json.dumps(override,indent=2),encoding='utf8')
build = root/'build';build.mkdir(exist_ok=True)
shutil.copyfile('notes/WeKnora-seat-scope-final-20261029',build/'WeKnora')
(build/'Dockerfile').write_text('FROM weknora-app:seat-prompt-20261028\nCOPY --chmod=755 WeKnora /app/WeKnora\n',encoding='utf8')
apply = '''import json,subprocess,sys
from pathlib import Path
p=Path(__file__).resolve().parent
base=json.loads((p/'runtime-before.json').read_text(encoding='utf8'))['compose_base']
if '--rollback' not in sys.argv:base+=['-f',str(p/'compose.seat-scope.json')]
subprocess.run(base+['up','-d','--no-deps','--no-build','--pull','never','app'],check=True)
subprocess.run(['docker','exec','WeKnora-frontend','nginx','-s','reload'],check=True)
'''
(root/'apply.py').write_text(apply,encoding='utf8')
(root/'rollback.ps1').write_text("$ErrorActionPreference='Stop'\npython '"+root.as_posix()+"/apply.py' --rollback\nexit $LASTEXITCODE\n",encoding='utf8')
Path('scripts/start-seat-scope-20261029.ps1').write_text("$ErrorActionPreference='Stop'\npython '"+root.as_posix()+"/apply.py'\nexit $LASTEXITCODE\n",encoding='utf8')
print('Prepared image build, startup and backend rollback files; deployment not executed')
