"""Merge saved local 0.8.2 capabilities into the isolated 0.8.3 checkout."""
import json
import pathlib
import subprocess
import tempfile

source = pathlib.Path('/mnt/c/Users/Win11/.codex/worktrees/weknora-082-upgrade/weknora-evaluation')
target = pathlib.Path('/mnt/d/weknora-083-upgrade')
root = pathlib.Path('/mnt/d/weknora-evaluation')
backup = pathlib.Path(root.joinpath('notes/upgrade-083-backup-path.txt').read_text().strip().replace('D:\\', '/mnt/d/').replace('\\', '/'))
assert backup.joinpath('manifest-partial.json').exists(), 'Hash source baseline backup first'
assert backup.joinpath('deployment-source.tar.gz').stat().st_size > 50_000_000
assert backup.joinpath('evaluation-source.tar.gz').stat().st_size > 50_000_000
# Code changes stay isolated; database restore verification and complete runtime
# archives remain mandatory before touching production.

git_prefix = ['git', '--git-dir=/mnt/d/weknora-evaluation/.git/worktrees/weknora-evaluation', '--work-tree=' + str(source)]
def git(*args):
    return subprocess.check_output([*git_prefix, *args])

files = json.loads(root.joinpath('notes/upgrade-083-local-files.json').read_text(encoding='utf-8-sig'))
conflicts = []
with tempfile.TemporaryDirectory() as temp:
    temp = pathlib.Path(temp)
    for file in sorted(set(files)):
        local = source.joinpath(file).read_bytes().replace(b'\r\n', b'\n')
        dest = target.joinpath(file)
        dest.parent.mkdir(parents=True, exist_ok=True)
        base_result = subprocess.run([*git_prefix, 'show', 'v0.8.2:' + file], capture_output=True)
        if base_result.returncode:
            assert not dest.exists(), 'New upstream/local file collision: ' + file
            dest.write_bytes(local)
            continue
        assert dest.exists(), 'Upstream deleted local modified file: ' + file
        for name, data in [('local', local), ('base', base_result.stdout), ('upstream', dest.read_bytes().replace(b'\r\n', b'\n'))]:
            temp.joinpath(name).write_bytes(data)
        merged = subprocess.run(['git', 'merge-file', '-p', str(temp/'local'), str(temp/'base'), str(temp/'upstream')], capture_output=True)
        assert merged.returncode >= 0 and merged.returncode < 128, merged.stderr.decode()
        dest.write_bytes(merged.stdout)
        if merged.returncode:
            conflicts.append(file)

# These are the later table-image changes recorded in the evaluation checkout.
# They are local additions, not upstream files; keep their tests with them.
for file in ['internal/application/service/related_images.go',
             'internal/application/service/related_images_test.go',
             'internal/application/service/chat_pipeline/retrieved_images.go',
             'internal/application/service/chat_pipeline/retrieved_images_test.go',
             'frontend/src/utils/relatedReferenceImages.ts',
             'frontend/src/utils/relatedReferenceImages.test.mjs']:
    assert subprocess.run([*git_prefix, 'cat-file', '-e', 'v0.8.2:' + file], capture_output=True).returncode != 0
    target.joinpath(file).write_bytes(root.joinpath(file).read_bytes().replace(b'\r\n', b'\n'))
print(json.dumps({'files': len(set(files)), 'conflicts': conflicts}, indent=2))
