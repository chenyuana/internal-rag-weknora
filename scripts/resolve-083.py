"""Resolve reviewed semantic overlaps after port-083.py (run once)."""
import pathlib
import re
import subprocess
import tempfile

r = pathlib.Path('/mnt/d/weknora-083-upgrade')
repo = '/mnt/d/weknora-evaluation/.git'

def upstream(file):
    return subprocess.check_output(['git', '--git-dir=' + repo, 'show', 'v0.8.3:' + file]).decode()

conflict_files = ['internal/types/chat_manage.go', 'internal/types/search.go',
                  'internal/application/service/knowledge_process.go',
                  'internal/application/service/knowledgebase_search.go']
with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    for file in conflict_files:
        tmp.joinpath('local').write_text(pathlib.Path('/mnt/c/Users/Win11/.codex/worktrees/weknora-082-upgrade/weknora-evaluation').joinpath(file).read_text())
        tmp.joinpath('base').write_bytes(subprocess.check_output(['git', '--git-dir=' + repo, 'show', 'v0.8.2:' + file]))
        tmp.joinpath('upstream').write_text(upstream(file))
        result = subprocess.run(['git', 'merge-file', '-p', str(tmp/'local'), str(tmp/'base'), str(tmp/'upstream')], capture_output=True)
        assert result.returncode in range(128)
        r.joinpath(file).write_bytes(result.stdout)

file = 'internal/types/chat_manage.go'
text = upstream(file)
local = pathlib.Path('/mnt/c/Users/Win11/.codex/worktrees/weknora-082-upgrade/weknora-evaluation').joinpath(file).read_text()
retrieved = local[local.index('// RetrievedImage is'):local.index('// PipelineState holds')]
text = text.replace('// PipelineState holds', retrieved + '// PipelineState holds', 1)
text = text.replace('type PipelineState struct {', 'type PipelineState struct {\n\tRetrievedImages []RetrievedImage `json:"-"`', 1)
text = text.replace('PipelineState: PipelineState{', 'PipelineState: PipelineState{\n\t\t\tRetrievedImages: slices.Clone(c.RetrievedImages),', 1)
r.joinpath(file).write_text(text)

file = 'internal/types/search.go'
text = r.joinpath(file).read_text()
text = re.sub(r'^<<<<<<<[^\n]*\n(.*?)^=======\n(.*?)^>>>>>>>[^\n]*\n', lambda m: m[1] + m[2], text, flags=re.M|re.S)
r.joinpath(file).write_text(text)

file = 'internal/application/service/knowledge_process.go'
text = r.joinpath(file).read_text()
text = re.sub(r'^<<<<<<<[^\n]*\n(.*?)^=======\n\tif options.EnableMultimodel[^\n]*\n(.*?)^>>>>>>>[^\n]*\n', lambda m: m[1] + m[2], text, flags=re.M|re.S)
r.joinpath(file).write_text(text)

file = 'internal/application/service/knowledgebase_search.go'
text = r.joinpath(file).read_text()
# Preserve upstream candidate construction and FAQ handling. Local numeric
# document pinning belongs after FAQ processing, before the wrapper truncates.
replacement = '''\tdeduplicatedChunks, err = s.applyFAQPostProcessing(
\t\tctx, kb, kbs, deduplicatedChunks, vectorLists, groups, params, matchCount)
\tif err != nil {
\t\treturn nil, err
\t}
\treturn deduplicatedChunks, nil
'''
text = re.sub(r'^<<<<<<<[^\n]*\n.*?^=======\n.*?^>>>>>>>[^\n]*\n', replacement, text, flags=re.M|re.S)
needle = '\trecordImageRecallDecision(ctx, "fusion.candidate_selection"'
pin = '''\tif recallNamedDocuments && len(mentionedACNumbers(params.OriginalQuery, params.QueryText)) > 0 {
\t\tids := params.KnowledgeBaseIDs
\t\tif len(ids) == 0 {
\t\t\tids = []string{id}
\t\t}
\t\tkbs, scopeErr := s.repo.GetKnowledgeBaseByIDs(ctx, ids)
\t\tif scopeErr != nil {
\t\t\treturn nil, scopeErr
\t\t}
\t\tif scopeErr = s.authorizeKBAccess(ctx, kbs); scopeErr != nil {
\t\t\treturn nil, scopeErr
\t\t}
\t\tchunks = s.pinNamedDocuments(ctx, chunks, kbs, params)
\t}

'''
assert needle in text
text = text.replace(needle, pin + needle, 1)
r.joinpath(file).write_text(text)
for file in conflict_files:
    assert not re.search(r'^(<<<<<<<|=======|>>>>>>>)', r.joinpath(file).read_text(), re.M), file
print('Four semantic merge conflicts resolved')
