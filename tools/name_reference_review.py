"""Hash-bound contextual revisions; never a global terminology replacement."""
import copy,json
from reinsertion import ROOT
from dialogue import sha

POLICY='context-reviewed-canonical-name-references-v001'

def load(binding):
    if set(binding)!={'recipe','sha256'}:raise ValueError('Unknown name consistency binding')
    path=(ROOT/binding['recipe']).resolve()
    if not path.is_relative_to(ROOT/'translations'):raise ValueError('Consistency manifest outside translations')
    raw=path.read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('Consistency manifest hash differs')
    m=json.loads(raw)
    if m.get('schema')!=1 or m.get('policy')!=POLICY:raise ValueError('Unknown consistency policy')
    if m['parent_interface']!='translations/interface-v043.json':raise ValueError('Consistency parent differs')
    parent_raw=(ROOT/m['parent_interface']).read_bytes()
    if sha(parent_raw)!=m['parent_interface_sha256']:raise ValueError('Consistency parent changed')
    return m,json.loads(parent_raw)

def revise(parent,changes):
    result=copy.deepcopy(parent);seen=set()
    for change in changes:
        path=change['path'];key=tuple(path)
        if not path or path[-1]!='translation' or key in seen:raise ValueError('Invalid/duplicate consistency text path')
        seen.add(key);node=result
        for part in path[:-1]:node=node[part]
        if sha(node[path[-1]].encode('utf-8'))!=change['parent_text_sha256']:
            raise ValueError('Consistency old text changed')
        node[path[-1]]=change['translation']
    return result

def expected_interface(binding):
    m,parent=load(binding);result=revise(parent,m['interface_changes'])
    result['item_descriptions']['name_reference_review']=binding
    result.update(name_reference_review=binding,base_dialogue_draft=m['new_dialogue'],
                  iso_name=m['iso_name'],status=m['interface_status'])
    return result

def validate_interface(recipe):
    binding=recipe['name_reference_review']
    if recipe!=expected_interface(binding):raise ValueError('Non-authorized interface consistency change')

def revised_descriptions(config):
    binding=config['name_reference_review'];m,parent=load(binding)
    expected=expected_interface(binding)['item_descriptions']
    if config!=expected:raise ValueError('Non-authorized description consistency change')
    old={r['id']:r for r in parent['item_descriptions']['entries']}
    return {r['id'] for r in config['entries'] if r!=old.get(r['id'])}

def validate_narrative(draft):
    from build_translation_pilot import load_draft
    binding=draft['name_reference_review'];m,parent=load(binding)
    p=ROOT/parent['base_dialogue_draft']
    if sha(p.read_bytes())!=m['parent_dialogue_file_sha256']:raise ValueError('Consistency narrative parent changed')
    expected,_=load_draft(p)
    for change in m['dialogue_changes']:
        key=change['id']
        if sha(json.dumps(expected['translations'][key],ensure_ascii=False,sort_keys=True).encode('utf-8'))!=change['parent_value_sha256']:
            raise ValueError('Consistency narrative old value differs')
        expected['translations'][key]=change['translation']
    expected.update(name_reference_review=binding,name=m['dialogue_name'],status=m['dialogue_status'],
                    reviewed_changes=[r['id'] for r in m['dialogue_changes']])
    if draft!=expected:raise ValueError('Non-authorized dialogue consistency change')

def filter_terminology(binding,key,segment,source,target,issues):
    if key not in ('map.msg.084ab3fc','map.msg.084ac950'):return issues
    m,_=load(binding)
    changes={r['id']:r for r in m['dialogue_changes']}
    if key not in changes:return issues
    change=changes[key];value=change['translation']
    expected=value[segment] if isinstance(value,dict) else value
    if target!=expected:raise ValueError('Consistency terminology target differs')
    if segment!='body' or sha(source.encode('utf-8'))!=change['source_body_sha256']:
        raise ValueError('Consistency Repair Kit source differs')
    from translation_policy import occurrences
    if occurrences(source,'Repair Kit')!=1 or occurrences(target,'Kit de reparo')!=1:
        raise ValueError('Consistency Repair Kit identity missing')
    return [i for i in issues if i!='Termo/nome protegido ausente: Repair Kit']
