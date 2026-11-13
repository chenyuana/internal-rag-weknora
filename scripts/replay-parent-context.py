"""Replay stored retrieval through the real Go context selector; no model calls."""
import json
import subprocess
from pathlib import Path

root = Path('testdata/parent-context-replay-20261029')
root.mkdir(parents=True, exist_ok=True)
sql = """SELECT json_agg(row_to_json(t)) FROM (
 SELECT c.id,c.content AS child,p.content AS parent,k.file_name
 FROM chunks c JOIN chunks p ON p.id=c.parent_chunk_id
 JOIN knowledges k ON k.id=c.knowledge_id
 WHERE c.id IN ('fc9b5c7c-d9d6-4a17-af82-96d27c717208','c8184bf5-a20c-4576-936b-8c2282b57859','9412a368-61df-49c5-9c6a-6cb49ed42469','73d20307-6048-4aa9-a306-963c7b8f0174','10ae867e-9cc7-446f-864b-a54a68b9c40e','c6254232-6473-4e7d-8bbd-bb8dd208b297','e5340508-3042-47a5-ab95-c29b5f61852b','f5d45f7e-b769-45df-a670-3cf0685917bc','11a60e78-5f63-4d8e-8b47-33981454f982')
) t"""
raw = subprocess.check_output(['docker','exec','WeKnora-postgres','psql','-U','weknora','-d','WeKnora','-Atc',sql],text=True,encoding='utf8')
(root/'input.json').write_text(raw,encoding='utf8')
source = Path('D:/weknora-083-upgrade/internal/application/service/chat_pipeline/parent_context.go').read_text()
source = source.replace('package chatpipeline','package main',1).replace('import "strings"','import ("strings"; "encoding/json"; "os"; "fmt")',1)
source += '''
func runeLen(s string) int { return len([]rune(s)) }
func main() {
 var rows []struct {ID,Child,Parent,File_name string}
 data,_:=os.ReadFile("input.json"); if err:=json.Unmarshal(data,&rows);err!=nil{panic(err)}
 out:=[]map[string]interface{}{}
 for _,r:=range rows {
  selected:=focusedParentContext(r.Parent,r.Child)
  retained:=strings.Contains(selected,strings.TrimSpace(r.Child))
  if strings.Contains(r.Parent,strings.TrimSpace(r.Child)) && !retained {panic("lost anchor: "+r.ID)}
  out=append(out,map[string]interface{}{"id":r.ID,"document":r.File_name,"before":runeLen(r.Parent),"after":runeLen(selected),"anchor_retained":retained,"selected":selected})
 }
 b,_:=json.MarshalIndent(out,"","  ");os.WriteFile("output.json",b,0644)
 fmt.Println("Replayed",len(rows),"actual parent/child pairs")
}
'''
(root/'replay.go').write_text(source,encoding='utf8')
subprocess.run(['wsl','bash','-lc','cd /mnt/d/weknora-evaluation/testdata/parent-context-replay-20261029 && /tmp/weknora-go126/go/bin/go run replay.go'],check=True)
for row in json.loads((root/'output.json').read_text(encoding='utf8')):
 print(row['document'],row['id'],row['before'],'->',row['after'],'anchor',row['anchor_retained'])
