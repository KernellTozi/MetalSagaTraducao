"""Source-bound BB occupational captions; never rename factions or Soldier."""
import copy,json,re
from dialogue import ROOT,sha
from gfi import encode,decode
from speaker_labels import bindings,apply_fixed_slots
from speaker_label_space import locate

POLICY='map-reviewed-bb-occupation-original-slots-v006'
PARENT_MAP='translations/regiao-inicial-v042.json'
PARENT_UI='translations/interface-v049.json'
MANIFEST='translations/rotulos-bb-v006.json'
MAP='translations/regiao-inicial-v043.json'
UI='translations/interface-v050.json'
STATUS='Trinta e dois rótulos de função BB traduzidos nos slots originais; demais recursos preservados.'
TARGETS={'BB Trooper':'Soldado BB','Ex-BB Trooper':'Ex-soldado BB',
         **{f'BB Trooper #{i}':f'Soldado BB #{i}' for i in range(1,7)}}

def validate_label(source,target,capacity):
    if source not in TARGETS or target!=TARGETS[source]:raise ValueError('Unreviewed BB occupation')
    raw=encode(target)
    if len(raw)>capacity or decode(raw)!=target or any(c in raw for c in (0,9,10,13,37)):
        raise ValueError('BB label codec/slot/control mismatch')
    if re.findall(r'\d+',source)!=re.findall(r'\d+',target):raise ValueError('BB ordinal changed')
    from translation_policy import validate
    if validate(source,target):raise ValueError('BB label terminology mismatch')
    return raw

def prepare(document,elf):
    selected=[]
    for e in document['entries']:
        labels=[s for s in e['segments'] if s['key']=='label']
        if not labels or labels[0]['source'] not in TARGETS:continue
        s=labels[0];target=TARGETS[s['source']];validate_label(s['source'],target,s['capacity'])
        if s['translation']!=s['source'] or s['editable']:raise ValueError('BB caption already changed')
        selected.append({'id':e['id'],'record_sha256':e['record_sha256'],
            'label_sha256':sha(bytes.fromhex(s['source_hex'])),'translation':target})
    if len(selected)!=32:raise ValueError('BB source catalogue differs')
    return {'schema':1,'policy':POLICY,'parent_map':PARENT_MAP,
        'parent_map_sha256':sha((ROOT/PARENT_MAP).read_bytes()),'parent_interface':PARENT_UI,
        'parent_interface_sha256':sha((ROOT/PARENT_UI).read_bytes()),
        'instruction_windows':bindings(elf),'entries':selected}

def load(binding):
    if set(binding)!= {'recipe','sha256'} or binding['recipe']!=MANIFEST:raise ValueError('BB manifest binding differs')
    raw=(ROOT/MANIFEST).read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('BB manifest fingerprint differs')
    m=json.loads(raw)
    if set(m)!= {'schema','policy','parent_map','parent_map_sha256','parent_interface','parent_interface_sha256','instruction_windows','entries'}:
        raise ValueError('BB manifest fields differ')
    if (m['schema'],m['policy'],m['parent_map'],m['parent_interface'])!=(1,POLICY,PARENT_MAP,PARENT_UI):
        raise ValueError('BB manifest policy/parent differs')
    if sha((ROOT/PARENT_MAP).read_bytes())!=m['parent_map_sha256'] or sha((ROOT/PARENT_UI).read_bytes())!=m['parent_interface_sha256']:
        raise ValueError('BB parent fingerprint differs')
    return m

def validate_narrative(draft):
    from build_translation_pilot import load_draft
    binding=draft['speaker_faction_review'];load(binding);expected,_=load_draft(ROOT/PARENT_MAP)
    expected.update(speaker_faction_review=binding,name='regiao-inicial-v043',status=STATUS,reviewed_changes=[])
    if draft!=expected:raise ValueError('Non-authorized BB narrative change')

def validate_interface(recipe):
    if 'context_finish_review' in recipe:
        from dialogue_context_finish import validate_interface as validate_context
        return validate_context(recipe)
    binding=recipe['speaker_faction_review'];load(binding)
    expected=json.loads((ROOT/PARENT_UI).read_text(encoding='utf-8'))
    expected.update(speaker_faction_review=binding,base_dialogue_draft=MAP,
        iso_name='MetalSaga-ptbr-interface-v050.iso',status=STATUS)
    if recipe!=expected:raise ValueError('Non-authorized BB interface change')

def compile_overlay(data,draft):
    from build_translation_pilot import compile_draft,load_draft
    from interface_text import SOURCE
    validate_narrative(draft);m=load(draft['speaker_faction_review']);parent,_=load_draft(ROOT/PARENT_MAP)
    document,patches,report=compile_draft(data,parent);elf=SOURCE.read_bytes()
    if m!=prepare(document,elf):raise ValueError('BB selected source set differs')
    config={k:m[k] for k in ('policy','instruction_windows','entries')}
    doc,compiled,rep=apply_fixed_slots(data,document,patches,report,config,elf,parent.get('preservation_decisions',{}),
        policy=POLICY,validator=validate_label)
    before={p['id']:p for p in patches};after={p['id']:p for p in compiled};entries={e['id']:e for e in document['entries']}
    for row in m['entries']:
        e=entries[row['id']];base=before.get(e['id'],{'after':bytes(data[e['offset']:e['offset']+e['size']])})['after']
        previous=e['segments'][-2]['offset']-e['offset'];label=e['segments'][-1]['offset']-e['offset']
        if locate(elf,base,previous,bytes.fromhex(e['tag']))!=label or locate(elf,after[e['id']]['after'],previous,bytes.fromhex(e['tag']))!=label:
            raise ValueError('Original BB label traversal differs')
    # Retain every historical layer and its counts instead of replacing it.
    doc['speaker_label_policy']=document['speaker_label_policy'];doc['speaker_faction_policy']=POLICY
    rep['speaker_faction_review']=rep['speaker_labels'];rep['speaker_labels']=report['speaker_labels']
    return doc,compiled,rep
