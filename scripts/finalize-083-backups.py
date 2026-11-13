import hashlib
import json
import pathlib
root=pathlib.Path('D:/weknora-evaluation')
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda:f.read(4*1024*1024),b''):h.update(data)
    return h.hexdigest()
for pointer in ['upgrade-083-backup-path.txt','upgrade-083-cutover-path.txt']:
    b=pathlib.Path((root/'notes'/pointer).read_text().strip())
    files=[]
    for p in b.iterdir():
        if p.is_file() and not p.name.startswith('.tmp') and not p.name.startswith('manifest'):
            files.append({'name':p.name,'bytes':p.stat().st_size,'sha256':digest(p)})
    directories=[]
    for name in ['data-files','minio-data','build-083','ui-083']:
        d=b/name
        if d.is_dir():
            members=[p for p in d.rglob('*') if p.is_file()]
            directories.append({'name':name,'files':len(members),'bytes':sum(p.stat().st_size for p in members),'note':'directory inventory; per-file hashes not included'})
    (b/'manifest-final.json').write_text(json.dumps({'files':files,'directories':directories,'excluded':'Incomplete .tmp archives are not usable backups.'},indent=2),encoding='utf-8')
    print('Final manifest:',b,flush=True)
