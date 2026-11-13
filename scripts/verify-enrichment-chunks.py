"""Compare original chunk IDs and all saved evidence fields after enrichment."""
import argparse
import json
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--snapshot', default='backups/pre-chunk-enrichment-20261013/target-chunks.json')
parser.add_argument('--kb', default='b35a43d9-8477-4f7a-8edb-7311222ff61c')
args = parser.parse_args()
# Validate before interpolating into read-only SQL.
import uuid
kb = str(uuid.UUID(args.kb))
before = json.loads(Path(args.snapshot).read_bytes())
sql = f"SELECT json_agg(t) FROM (SELECT id,knowledge_id,chunk_index,content,source_content,metadata,start_at,end_at,chunk_type,parent_chunk_id,pre_chunk_id,next_chunk_id,image_info FROM chunks WHERE deleted_at IS NULL AND knowledge_base_id='{kb}' ORDER BY id) t"
raw = subprocess.check_output(['docker', 'exec', 'WeKnora-postgres', 'psql', '-U', 'weknora', '-d', 'WeKnora', '-Atc', sql])
after = {x['id']: x for x in json.loads(raw) or []}
missing = [x['id'] for x in before if x['id'] not in after]
changed = [x['id'] for x in before if x['id'] in after and x != after[x['id']]]
report = {'original_chunks': len(before), 'missing': missing, 'changed': changed, 'new_chunks': len(set(after) - {x['id'] for x in before})}
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(1 if missing or changed else 0)
