"""Create a test agent, or apply a verified prompt to quick answer."""
import json
import sys
from pathlib import Path

exec(Path('scripts/test-ac25853-wiki.py').read_text(encoding='utf-8-sig').split('source=req(')[0])
root = Path('testdata/seat-scope-20261029')
original = json.loads((root/'agent-before.json').read_text(encoding='utf8'))['data']
config = dict(original['config'])
prompt = config['system_prompt']
prompt = prompt.replace(
    '4. Additional information from other documents may be included only when\n'
    '   it materially helps answer the question. Label it "Supplementary Reference"\n'
    '   in the response language and keep it separate from the main answer.',
    '4. Relevant documents within the adopted scope may be combined.\n'
    '   Do not add other aircraft categories or compliance domains as\n'
    '   supplementary references unless the user explicitly requests them.')
prompt = prompt.replace(
    '6. Keep the answer concise while preserving necessary completeness.',
    '6. If the question gives a number of categories but no classification basis,\n'
    '   do not claim that the retrieved categories are the only required ones.\n'
    '   Unless the question or a source establishes the classification basis,\n'
    '   ask one focused clarification and give only a brief orientation.\n'
    '   Do not produce a full comparison before this ambiguity is resolved.\n'
    '   Co-occurrence or prominence in retrieved sources does not establish\n'
    '   that those items form the requested exhaustive classification.\n'
    '7. When primary applicable sources lack a requested criterion, do not\n'
    '   substitute requirements from another aircraft category or scope.\n'
    '   Keep cross-scope text and images out of the main comparison. Include\n'
    '   a cross-scope supplement only if explicitly requested by the user.\n'
    '   Prioritize requested criteria over peripheral equipment details,\n'
    '   approval paperwork, unrelated exceptions, or supplementary categories.\n'
    '8. Keep the answer concise while preserving necessary completeness.')
# Renumber the remaining original rules without changing their meaning.
for old, new in [('11. Do not output', '13. Do not output'),
                 ('10. Give recommendations', '12. Give recommendations'),
                 ('9. Include images', '11. Include images'),
                 ('8. Do not add', '10. Do not add'),
                 ('7. After a table', '9. After a table')]:
    prompt = prompt.replace(old, new)
prompt = prompt.replace('8. Keep the answer concise while preserving necessary completeness.',
    '8. Keep the answer concise while preserving necessary completeness.\n'
    '   For complex technical comparisons in Chinese, allow roughly 1200-2000\n'
    '   Chinese characters excluding citation markup when the content needs it.\n'
    '   This is a flexible guide, not a minimum or hard cutoff. Never pad an\n'
    '   answer to reach it; exceed it when essential conditions require more.\n'
    '   For comparisons, normally use one table and up to three brief notes.\n'
    '   Add further detail only when explicitly requested or needed to preserve\n'
    '   an essential condition. Do not expand into adjacent compliance topics.')
config['system_prompt'] = prompt
(root/'system-prompt-after.txt').write_text(prompt, encoding='utf8')
if '--apply' in sys.argv:
    live = req('GET','/agents/builtin-quick-answer')['data']
    # Preserve concurrent changes to every other configuration field.
    live_config = dict(live['config']);live_config['system_prompt'] = prompt
    result = req('PUT','/agents/builtin-quick-answer',
        {'name':live['name'], 'description':live['description'], 'config':live_config})
    (root/'agent-applied.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print('Updated quick-answer system prompt; other settings preserved')
elif '--update-candidate' in sys.argv:
    candidate = json.loads((root/'candidate-agent.json').read_text(encoding='utf8'))['data']
    result = req('PUT','/agents/'+candidate['id'],{'name':candidate['name'], 'description':candidate['description'], 'config':config})
    (root/'candidate-agent.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print('Updated candidate prompt')
else:
    result = req('POST','/agents',{'name':'Scope validation 20261029',
        'description':'Temporary controlled scope regression agent', 'config':config})
    (root/'candidate-agent.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(result['data']['id'])
