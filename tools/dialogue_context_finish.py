"""Exact contextual body revisions and descriptive captions, fixed records."""
import copy,json
from dialogue import ROOT,sha
from gfi import encode,decode
from speaker_labels import bindings,apply_fixed_slots
from speaker_label_space import locate
from reinsertion import compile_entry

POLICY='map-contextual-final-dialogue-review-v007'
PARENT_MAP='translations/regiao-inicial-v043.json'
PARENT_UI='translations/interface-v050.json'
MAP='translations/regiao-inicial-v044.json'
UI='translations/interface-v051.json'
MANIFEST='translations/revisao-contextual-v007.json'
STATUS='Onze rótulos descritivos e cinco revisões contextuais; demais traduções preservadas.'
ROLES={**{f'Barbarian {c}':f'Bárbaro {c}' for c in 'ABCD'},
       'Ex-Barbarian':'Ex-bárbaro','Ex-Burglar':'Ex-ladrão','Capsule (Binramen)':'Cápsula (Binramen)'}
BODIES={
 'map.msgn.1282e1d0':'Minha pontaria é ruim.\nProvavelmente erraria\ntodos os alvos.\tE esta arma também\nestá sem balas.',
 'map.smsg.0e77864c':'Levo cargas, sobretudo,\npara o oeste.\tCostumo levar grãos\ne álcool.\tO frete dessas cargas\npaga bem, mas menos\nque o de verduras.',
 'map.msgn.0be22c78':'A nordeste, há\numa ponte para\nTorikami.\tO leste está cheio de\nScorpions, mas é onde\nse ganha mais dinheiro.',
 'map.msgn.0e7781f4':'Fui à casa dele contar\nà esposa e aos filhos\no que aconteceu.\tNão esqueço a\nexpressão deles...',
 'map.msgn.0e76d6c4':'O que faz aqui\ncom uma ferida dessas!?\nVá se tratar!',
}

def validate_role(source,target,capacity):
    if source not in ROLES or target!=ROLES[source]:raise ValueError('Unreviewed descriptive caption')
    raw=encode(target)
    if len(raw)>capacity or decode(raw)!=target or any(c in raw for c in (0,9,10,13,37)):
        raise ValueError('Descriptive caption codec/budget differs')
    from translation_policy import validate
    if validate(source,target):raise ValueError('Descriptive caption terminology differs')
    return raw

def revised_body(data,entry,base,target,document):
    if target!=BODIES.get(entry['id']) or entry['blocked_reasons'] or entry['mode']!='slots':
        raise ValueError('Unreviewed or blocked contextual body')
    if bytes.fromhex(entry['tag']) not in (b'msg\0',b'msgn',b'smsg'):
        raise ValueError('Unproved contextual body family')
    segments=entry['segments'];body=segments[0]
    if body['key']!='body' or '%' in body['source']:raise ValueError('Context scope excludes dynamic commands')
    if target==body['translation']:raise ValueError('Context body is unchanged from parent')
    from translation_policy import validate
    if validate(body['source'],target):raise ValueError('Context body violates protected terminology')
    original=bytes(data[entry['offset']:entry['offset']+entry['size']]);start=body['offset']-entry['offset']
    source=bytes.fromhex(body['source_hex']);header=bytes.fromhex(entry['header_hex'])
    if (sha(original)!=entry['record_sha256'] or original[start:start+len(source)+1]!=source+b'\0'
        or len(base)!=entry['size'] or base[:len(header)]!=header):
        raise ValueError('Context original fingerprint/header differs')
    check=copy.deepcopy(entry)
    for s in check['segments']:
        if not s['editable']:s['translation']=s['source']
    check['segments'][0]['translation']=target
    # Use the historical compiler against original fingerprints first; merge
    # only its body delta, keeping every previously translated/moved caption.
    p,result=compile_entry(data,check,check,quirk_refs=True)
    if p is None:raise ValueError('Contextual body must change the original')
    old=encode(body['translation']);new=encode(target)
    if base[start:start+len(old)+1]!=old+b'\0':raise ValueError('Context parent body readback differs')
    end=start+max(len(old),len(new))+1
    offsets=document.get('compiled_dialogue_segment_offsets',{}).get(entry['id'],{})
    next_at=entry['offset']+entry['size']
    for s in segments[1:]:
        at=offsets.get(s['key'],document.get('compiled_speaker_label_offsets',{}).get(entry['id'],s['offset']) if s['key']=='label' else s['offset'])
        value=encode(s['translation']);relative=at-entry['offset']
        if base[relative:relative+len(value)+1]!=value+b'\0':raise ValueError('Context parent adjoining segment differs')
        next_at=min(next_at,at)
    if end>next_at-entry['offset']:raise ValueError('Context revision would reach another compiled segment')
    if end>start+len(old)+1 and any(base[start+len(old)+1:end]):raise ValueError('Context growth crosses nonzero bytes')
    after=base[:start]+new+bytes(end-start-len(new))+base[end:]
    if len(after)!=len(base) or after[:start]!=base[:start] or after[end:]!=base[end:]:raise ValueError('Context body escaped its interval')
    if p['after'][start:start+len(new)+1]!=after[start:start+len(new)+1]:raise ValueError('Context compiler/readback differs')
    return after,result,{'id':entry['id'],'record_sha256':entry['record_sha256'],
        'parent_record_sha256':sha(base),'parent_body_sha256':sha(old),'target_body_sha256':sha(new),
        'target_record_sha256':sha(after),'offset':entry['offset']+start,'span':end-start,
        'compiled_next_segment_offset':next_at,'old_body_bytes':len(old),'new_body_bytes':len(new),
        'translation':target,'warnings':result['warnings']}

def prepare(data,document,patches,elf):
    selected=[];by={e['id']:e for e in document['entries']};out={p['id']:p for p in patches}
    for e in document['entries']:
        label=e['segments'][-1]
        if label['key']!='label' or label['source'] not in ROLES:continue
        if label['translation']!=label['source']:raise ValueError('Caption already revised')
        validate_role(label['source'],ROLES[label['source']],label['capacity'])
        selected.append({'id':e['id'],'record_sha256':e['record_sha256'],
            'label_sha256':sha(bytes.fromhex(label['source_hex'])),'translation':ROLES[label['source']]})
    if len(selected)!=11:raise ValueError('Context caption source scope differs')
    bodies=[]
    for key,target in BODIES.items():
        if key not in out:raise ValueError('Context body must already be translated')
        _,_,row=revised_body(data,by[key],out[key]['after'],target,document);bodies.append(row)
    if {r['id'] for r in selected}&set(BODIES):raise ValueError('Separate contextual body/caption scopes overlap')
    return {'schema':1,'policy':POLICY,'parent_map':PARENT_MAP,'parent_map_sha256':sha((ROOT/PARENT_MAP).read_bytes()),
        'parent_interface':PARENT_UI,'parent_interface_sha256':sha((ROOT/PARENT_UI).read_bytes()),
        'instruction_windows':bindings(elf),'captions':selected,'bodies':bodies}

def load(binding):
    if set(binding)!= {'recipe','sha256'} or binding['recipe']!=MANIFEST:raise ValueError('Context manifest binding differs')
    raw=(ROOT/MANIFEST).read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('Context manifest fingerprint differs')
    m=json.loads(raw)
    if set(m)!={'schema','policy','parent_map','parent_map_sha256','parent_interface','parent_interface_sha256','instruction_windows','captions','bodies'}:
        raise ValueError('Context manifest fields differ')
    if (m['schema'],m['policy'],m['parent_map'],m['parent_interface'])!=(1,POLICY,PARENT_MAP,PARENT_UI):raise ValueError('Context policy/parent differs')
    if any(sha((ROOT/m[k]).read_bytes())!=m[k+'_sha256'] for k in ('parent_map','parent_interface')):raise ValueError('Context parent fingerprint differs')
    return m

def validate_narrative(draft):
    from build_translation_pilot import load_draft
    binding=draft['context_finish_review'];load(binding);expected,_=load_draft(ROOT/PARENT_MAP)
    if any(k in BODIES or p in BODIES for k,p in expected.get('aliases',{}).items()):
        raise ValueError('Context revisions must not alter alias parents or children')
    for key,text in BODIES.items():
        if key in expected.get('aliases',{}):raise ValueError('Context alias revision needs separate proof')
        value=expected['translations'][key]
        expected['translations'][key]=text if isinstance(value,str) else {**value,'body':text}
    expected.update(context_finish_review=binding,name='regiao-inicial-v044',status=STATUS,reviewed_changes=list(BODIES))
    if draft!=expected:raise ValueError('Non-authorized contextual narrative change')

def validate_interface(recipe):
    binding=recipe['context_finish_review'];load(binding);expected=json.loads((ROOT/PARENT_UI).read_bytes())
    expected.update(context_finish_review=binding,base_dialogue_draft=MAP,iso_name='MetalSaga-ptbr-interface-v051.iso',status=STATUS)
    if recipe!=expected:raise ValueError('Non-authorized contextual interface change')

def compile_overlay(data,draft):
    from build_translation_pilot import compile_draft,load_draft
    from interface_text import SOURCE
    validate_narrative(draft);m=load(draft['context_finish_review']);parent,_=load_draft(ROOT/PARENT_MAP)
    document,patches,report=compile_draft(data,parent);elf=SOURCE.read_bytes()
    if m!=prepare(data,document,patches,elf):raise ValueError('Context source scope/evidence differs')
    config={'policy':POLICY,'instruction_windows':m['instruction_windows'],'entries':m['captions']}
    doc,out,rep=apply_fixed_slots(data,document,patches,report,config,elf,parent.get('preservation_decisions',{}),policy=POLICY,validator=validate_role)
    entries={e['id']:e for e in doc['entries']};out={p['id']:p for p in out};results={r['id']:r for r in rep['results']}
    for row in m['captions']:
        e=entries[row['id']];label=e['segments'][-1];prev=e['segments'][-2]['offset']-e['offset']
        if locate(elf,out[e['id']]['after'],prev,bytes.fromhex(e['tag']))!=label['offset']-e['offset']:raise ValueError('Context caption original traversal differs')
    for row in m['bodies']:
        key=row['id'];e=entries[key];after,result,actual=revised_body(data,e,out[key]['after'],row['translation'],doc)
        if actual!=row:raise ValueError('Context revised body binding differs')
        out[key]={**out[key],'after':after};e['segments'][0]['translation']=row['translation']
        r=results[key];r['target_lengths']=[len(encode(s['translation'])) for s in e['segments']]
        r['warnings']=result['warnings'];r['context_finish_review']=True
    doc['speaker_label_policy']=document['speaker_label_policy'];doc['context_finish_policy']=POLICY
    rep['context_finish_review']={**rep['speaker_labels'],'reviewed_bodies':len(m['bodies']),'body_results':m['bodies']}
    rep['speaker_labels']=report['speaker_labels']
    return doc,sorted(out.values(),key=lambda p:p['offset']),rep
