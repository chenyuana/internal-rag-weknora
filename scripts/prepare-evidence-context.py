import json
import shutil
from pathlib import Path

root = Path('backups/evidence-context-20261029').resolve()
build = root/'build'
build.mkdir(exist_ok=True)
shutil.copyfile('notes/WeKnora-evidence-context-20261029', build/'WeKnora')
(build/'Dockerfile').write_text('FROM weknora-app:seat-scope-20261029\nCOPY --chmod=755 WeKnora /app/WeKnora\n',encoding='utf8')
base = json.loads(Path('backups/seat-scope-20261029/runtime-before.json').read_text())['compose_base']
base += ['-f', str(Path('backups/seat-scope-20261029/compose.seat-scope.json').resolve())]
(root/'runtime-before.json').write_text(json.dumps({'compose_base':base},indent=2),encoding='utf8')
(root/'compose.evidence-context.json').write_text(json.dumps({'services':{'app':{'image':'weknora-app:evidence-context-20261029'}}},indent=2),encoding='utf8')
shutil.copyfile('backups/seat-scope-20261029/apply.py',root/'apply.py')
p=root/'apply.py'
p.write_text(p.read_text().replace('compose.seat-scope.json','compose.evidence-context.json'),encoding='utf8')
(root/'rollback.ps1').write_text("python '"+root.as_posix()+"/apply.py' --rollback\n",encoding='utf8')
candidate = Path('scripts/start-seat-scope-canary.py').read_text()
candidate = candidate.replace("'notes/WeKnora-seat-scope-20261029'", "'notes/WeKnora-evidence-context-20261029'")
Path('scripts/start-evidence-context-canary.py').write_text(candidate,encoding='utf8')
print('Prepared candidate and deployment; rollback uses retained seat-scope image')
