"""Remove answer compression only; snapshot and preserve other live settings."""
import json
import re
from pathlib import Path
from datetime import datetime

exec(Path('scripts/test-ac25853-wiki.py').read_text(encoding='utf-8-sig').split('source=req(')[0])
root=Path('backups')/('answer-completeness-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
root.mkdir()
live=req('GET','/agents/builtin-quick-answer')['data']
(root/'agent-before.json').write_text(json.dumps(live,ensure_ascii=False,indent=2),encoding='utf8')
prompt=live['config']['system_prompt']
prompt=prompt.replace('Keep answers concise without omitting information\nneeded to answer the question correctly.', 'Prioritize a complete supported answer over brevity; preserve all requested criteria and necessary conditions.')
start=prompt.index('## Answer Construction')
end=prompt.index('## Final Check',start)
section=prompt[start:end]
section=re.sub(r'(?ms)^6\. If the question gives a number of categories.*?(?=^7\.)', '6. If classification is ambiguous, explain the supported interpretation and\n   relevant alternatives without forcing an exhaustive classification.\n',section)
section=re.sub(r'(?ms)^8\. Keep the answer concise.*?(?=^9\.)', '8. Prioritize completeness over brevity. Do not impose a target word count,\n   table count, or note count. Include all requested criteria, numerical\n   values, conditions, exceptions and supporting explanations available\n   in the evidence. Use tables or prose as appropriate.\n',section)
section=re.sub(r'(?ms)^9\. After a table,.*?(?=^10\.)', '9. Add explanations needed to understand the evidence and its limits.\n',section)
section=re.sub(r'(?ms)^10\. Do not add an unsolicited full workflow.*?(?=^11\.)', '10. Include background and procedures when they help interpret the requested\n    requirements; distinguish them from the main answer.\n',section)
prompt=prompt[:start]+section+prompt[end:]
if prompt==live['config']['system_prompt']: raise RuntimeError('No matching restrictions changed; inspect live prompt')
config=dict(live['config']);config['system_prompt']=prompt
(root/'system-prompt-after.txt').write_text(prompt,encoding='utf8')
req('PUT','/agents/builtin-quick-answer',{'name':live['name'],'description':live['description'],'config':config})
after=req('GET','/agents/builtin-quick-answer')['data']
assert after['config']['system_prompt']==prompt
assert {k:v for k,v in config.items() if k!='system_prompt'}=={k:v for k,v in after['config'].items() if k!='system_prompt'}
(root/'agent-after.json').write_text(json.dumps(after,ensure_ascii=False,indent=2),encoding='utf8')
print('Restored completeness preference. Other settings preserved. Backup:',root)
print('Rerank:',{k:v for k,v in after['config'].items() if 'rerank' in k})
