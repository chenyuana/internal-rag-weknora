package main

import ("strings"; "encoding/json"; "os"; "fmt")

// focusedParentContext limits expansion, never the retrieved child itself.
// Only a unique, literal anchor permits narrowing: edited children, repeated
// boilerplate and unstructured parents retain their original context.
func focusedParentContext(parent, child string) string {
	if runeLen(parent) <= 12000 || strings.TrimSpace(child) == "" {
		return parent
	}
	anchor := strings.TrimSpace(child)
	if len(anchor) < 32 || strings.Count(parent, anchor) != 1 {
		return parent
	}
	start := strings.Index(parent, anchor)
	end := start + len(anchor)
	// Keep complete paragraphs containing the hit plus two on either side.
	// A single giant paragraph is deliberately not cut mid-condition/table.
	for i := 0; i < 3; i++ {
		if start == 0 {
			break
		}
		boundary := strings.LastIndex(parent[:start], "\n\n")
		if boundary < 0 {
			start = 0
			break
		}
		start = boundary
	}
	for i := 0; i < 3; i++ {
		boundary := strings.Index(parent[end:], "\n\n")
		if boundary < 0 {
			end = len(parent)
			break
		}
		end += boundary + 2
	}
	return strings.TrimSpace(parent[start:end])
}

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
