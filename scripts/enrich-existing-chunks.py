"""Generate Wiki/graph from saved chunks. Defaults to validation only."""
import argparse
import json
import os
import urllib.error
import urllib.request

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--base', default='http://localhost:18080/api/v1')
parser.add_argument('--kb', required=True)
parser.add_argument('--knowledge-id', action='append', required=True)
parser.add_argument('--wiki', action='store_true')
parser.add_argument('--graph', action='store_true')
parser.add_argument('--apply', action='store_true', help='Schedule generation; omission only validates')
args = parser.parse_args()
key = os.environ.get('WEKNORA_API_KEY')
if not key:
    parser.error('Set WEKNORA_API_KEY to an ingest-capable API key')
body = {'knowledge_ids': args.knowledge_id, 'wiki': args.wiki, 'graph': args.graph, 'dry_run': not args.apply}
req = urllib.request.Request(f'{args.base}/knowledge-bases/{args.kb}/knowledge/enrich', json.dumps(body).encode(), headers={'X-API-Key': key, 'Content-Type': 'application/json'}, method='POST')
try:
    with urllib.request.urlopen(req, timeout=60) as response:
        print(json.dumps(json.load(response), ensure_ascii=False, indent=2))
except urllib.error.HTTPError as error:
    print(error.read().decode())
    raise SystemExit(1)
