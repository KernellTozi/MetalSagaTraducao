"""Opt-in authored body revisions plus proven same-record speaker tails.

The historical body compiler checks each revision before the existing original
label scanners/copy probes check its longer caption. No record/block growth.
"""
import copy,json
from dialogue import ROOT,sha
from gfi import encode,BYTES_TO_CHAR
from speaker_labels import ROLES,probe
from speaker_label_space import placement,locate,byte_copy_probe,bindings
from reinsertion import compile_entry

POLICY='map-reviewed-body-and-complete-speaker-tail-v005'
PARENT_MAP='translations/regiao-inicial-v041.json'
PARENT_UI='translations/interface-v048.json'
DECISIONS='translations/rotulos-redacao-v005.json'
MANIFEST='translations/rotulos-espaco-v005.json'
BODIES_SHA='6e1690336f769d74d27248839e41f9503aff2d7d607ed2965f646fd13b68bb08'

def bodies():
    raw=(ROOT/DECISIONS).read_bytes();value=json.loads(raw)
    if value.get('schema')!=1 or set(value)!= {'schema','note','bodies'}:raise ValueError('Speaker body decisions schema differs')
    result=value['bodies']
    canonical=json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
    if len(result)!=36 or sha(canonical)!=BODIES_SHA:raise ValueError('Speaker authored body decisions differ')
    return result

def construct(data,entry,base,body,elf):
    from translation_policy import validate
    if bytes.fromhex(entry['tag'])!=b'msgn' or entry['mode']!='slots' or entry['blocked_reasons']:
        raise ValueError('Speaker body review requires a proven unblocked msgn')
    if len(entry['segments'])!=2 or [s['key'] for s in entry['segments']]!=['body','label']:
        raise ValueError('Speaker body review segment roles differ')
    source,label=entry['segments']
    if label['editable'] or label['source']!=label['translation'] or label['source'] not in ROLES:
        raise ValueError('Speaker source role unreviewed or already edited')
    if source['offset']!=entry['offset']+32 or b'%' in bytes.fromhex(source['source_hex']):
        raise ValueError('Speaker body scope excludes dynamic commands/new layouts')
    if body!=bodies().get(entry['id']):raise ValueError('Unreviewed speaker body target')
    if validate(source['source'],body):raise ValueError('Speaker body violates terminology/preserved expression policy')
    parent_body=base[32:].split(b'\0',1)[0]
    if parent_body!=encode(source['translation']):raise ValueError('Speaker parent body/readback differs')
    revised=copy.deepcopy(entry);revised['segments'][0]['translation']=body
    # Keep label protected here: use the exact legacy body compiler first.
    body_patch,body_result=compile_entry(data,revised,entry,quirk_refs=True)
    if body_patch is None or body_patch['before']!=bytes(data[entry['offset']:entry['offset']+entry['size']]):
        raise ValueError('Speaker body compiler baseline differs')
    compact=body_patch['after'];target=ROLES[label['source']];raw=encode(target)
    start=entry['size']-len(raw)-1;alignment=4 if start%4==0 else 1
    start,raw,nul=placement(compact,entry,target,alignment=alignment)
    after=compact[:start]+raw+bytes(len(compact)-start-len(raw))
    old=label['offset']-entry['offset']
    if locate(elf,base,32,b'msgn')!=old or locate(elf,after,32,b'msgn')!=start:
        raise ValueError('Original revised-body label traversal differs')
    if after[:32]!=base[:32] or len(after)!=len(base) or after[32:nul+1]!=encode(body)+b'\0':
        raise ValueError('Speaker header/size/body/terminator changed')
    # Reparse independent of PT-BR glyph meanings, preserving every byte slot.
    shadow=bytearray(after)
    for at in (32,start):
        value=after[at:].split(b'\0',1)[0];i=0
        while i<len(value):
            if value[i:i+2] in BYTES_TO_CHAR:shadow[at+i:at+i+2]=b'aa';i+=2
            else:i+=1
    from dialogue_formats import parse_msgn,reconstruct
    parsed,opaque=parse_msgn(shadow,0)
    if opaque or parsed['text_offset']!=32 or parsed['display_label']['text_offset']!=start or reconstruct(parsed)!=shadow:
        raise ValueError('Speaker compact record structural round-trip differs')
    evidence=probe(elf,raw);residue=(entry['offset']+start)%4
    if residue:
        for a in (residue,residue+4):byte_copy_probe(elf,raw,a)
    result={'id':entry['id'],'record_sha256':entry['record_sha256'],'base_record_sha256':sha(base),
        'source_label_sha256':sha(bytes.fromhex(label['source_hex'])),
        'parent_body_sha256':sha(parent_body),'translation':target,'body_translation':body,
        'old_body_bytes':len(parent_body),'new_body_bytes':len(encode(body)),
        'old_label_offset':label['offset'],'target_label_offset':entry['offset']+start,
        'reclaimed_separator_bytes':old-start,'target_record_sha256':sha(after),
        'body_compiler_warnings':body_result['warnings'],**evidence}
    return after,result

def prepare(data,parent,elf,compiled=None):
    from build_translation_pilot import compile_draft
    document,patches,report=compile_draft(data,parent) if compiled is None else compiled
    if not report['valid']:raise ValueError('Speaker review parent compilation invalid')
    pending=json.loads((ROOT/'reports/rotulos-falantes-v037.json').read_text(encoding='utf-8'))['deferred']
    expected={r['id'] for r in pending};by={e['id']:e for e in document['entries']};compiled={p['id']:p for p in patches}
    selected=bodies();rows=[]
    if not set(selected)<expected or len(expected)!=49:raise ValueError('Speaker historical pending scope differs')
    for key,body in selected.items():
        e=by[key]
        if key in parent.get('preservation_decisions',{}) or key in document.get('compiled_speaker_label_offsets',{}):
            raise ValueError('Protected/already relocated speaker review record')
        if key not in compiled:raise ValueError('Speaker body must already be translated in parent')
        _,row=construct(data,e,compiled[key]['after'],body,elf);rows.append(row)
    remaining=[{'id':key,'record_sha256':by[key]['record_sha256'],
        'label_sha256':sha(bytes.fromhex(by[key]['segments'][-1]['source_hex'])),
        'reason':'Preserve complete expression/citation/sound/silence or idiomatic short line; no safe equivalent compact revision selected.'} for key in sorted(expected-set(selected))]
    return {'schema':1,'policy':POLICY,'parent_map':PARENT_MAP,'parent_map_sha256':sha((ROOT/PARENT_MAP).read_bytes()),
        'parent_interface':PARENT_UI,'parent_interface_sha256':sha((ROOT/PARENT_UI).read_bytes()),
        'body_decisions':{'recipe':DECISIONS,'sha256':sha((ROOT/DECISIONS).read_bytes())},
        'instruction_windows':bindings(elf),'entries':rows,'remaining':remaining}

def load(binding):
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:raise ValueError('Speaker body binding scope differs')
    raw=(ROOT/MANIFEST).read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('Speaker body manifest changed')
    m=json.loads(raw)
    if m.get('schema')!=1 or m.get('policy')!=POLICY or m.get('parent_map')!=PARENT_MAP or m.get('parent_interface')!=PARENT_UI:
        raise ValueError('Speaker body manifest parent/policy differs')
    for path,key in ((PARENT_MAP,'parent_map_sha256'),(PARENT_UI,'parent_interface_sha256')):
        if sha((ROOT/path).read_bytes())!=m[key]:raise ValueError('Speaker body parent fingerprint differs')
    if m['body_decisions']!={'recipe':DECISIONS,'sha256':sha((ROOT/DECISIONS).read_bytes())}:raise ValueError('Speaker body decisions binding differs')
    if len(m['entries'])!=36 or {r['id']:r['body_translation'] for r in m['entries']}!=bodies():raise ValueError('Speaker body authored entries differ')
    return m

def validate_narrative(draft):
    from build_translation_pilot import load_draft
    binding=draft['speaker_body_review'];load(binding);expected,_=load_draft(ROOT/PARENT_MAP);expected=copy.deepcopy(expected)
    for key,text in bodies().items():
        if key not in expected.get('aliases',{}):expected['translations'][key]=text
    targets=dict(expected['translations']);aliases=dict(expected['aliases'])
    while aliases:
        ready=[key for key,parent in aliases.items() if parent in targets]
        if not ready:raise ValueError('Unresolved speaker body aliases')
        for key in ready:targets[key]=targets[aliases.pop(key)]
    if any(targets.get(key)!=body for key,body in bodies().items()):raise ValueError('Speaker revised alias body differs')
    expected.update(speaker_body_review=binding,name='regiao-inicial-v042',
        status='Trinta e seis rótulos completos com revisão contextual das falas; treze preservados por limite de espaço.',reviewed_changes=list(bodies()))
    if draft!=expected:raise ValueError('Non-authorized speaker body narrative change')

def validate_interface(recipe):
    if 'speaker_faction_review' in recipe:
        from speaker_faction_review import validate_interface as validate_faction
        return validate_faction(recipe)
    binding=recipe['speaker_body_review'];load(binding)
    expected=json.loads((ROOT/PARENT_UI).read_text(encoding='utf-8'))
    expected.update(speaker_body_review=binding,base_dialogue_draft='translations/regiao-inicial-v042.json',
        iso_name='MetalSaga-ptbr-interface-v049.iso',status='Trinta e seis rótulos de falantes; demais recursos v048 preservados.')
    if recipe!=expected:raise ValueError('Non-authorized speaker body interface change')

def compile_overlay(data,draft):
    from build_translation_pilot import load_draft,compile_draft
    from interface_text import SOURCE
    validate_narrative(draft);m=load(draft['speaker_body_review']);parent,_=load_draft(ROOT/PARENT_MAP);elf=SOURCE.read_bytes()
    document,patches,report=compile_draft(data,parent)
    if not report['valid']:raise ValueError('Speaker body parent compilation invalid')
    if m!=prepare(data,parent,elf,compiled=(document,patches,report)):raise ValueError('Speaker body full manifest evidence differs')
    entries={e['id']:e for e in document['entries']};out={p['id']:p for p in patches}
    new_entries=dict(entries);results={r['id']:r for r in report['results']}
    label_offsets=dict(document.get('compiled_speaker_label_offsets',{}));segment_offsets=copy.deepcopy(document.get('compiled_dialogue_segment_offsets',{}))
    for item in m['entries']:
        key=item['id'];e=entries[key];after,actual=construct(data,e,out[key]['after'],item['body_translation'],elf)
        if item!=actual:raise ValueError('Speaker body compiled evidence differs')
        original=bytes(data[e['offset']:e['offset']+e['size']])
        out[key]={'id':key,'resource':document['resource'],'offset':e['offset'],'before':original,'after':after}
        e=copy.deepcopy(e);e['segments'][0]['translation']=item['body_translation'];e['segments'][-1]['translation']=item['translation'];new_entries[key]=e
        label_offsets[key]=item['target_label_offset'];segment_offsets[key]={'body':e['offset']+32,'label':item['target_label_offset']}
        result=copy.deepcopy(results[key]);result.update(speaker_body_review=True,
            target_offsets=[e['offset']+32,item['target_label_offset']],
            target_lengths=[len(encode(s['translation'])) for s in e['segments']],
            warnings=item['body_compiler_warnings']);results[key]=result
    compiled=sorted(out.values(),key=lambda p:p['offset'])
    if any(a['offset']+len(a['before'])>b['offset'] for a,b in zip(compiled,compiled[1:])):raise ValueError('Speaker body patches overlap')
    doc={**document,'entries':[new_entries[e['id']] for e in document['entries']],
        'compiled_speaker_label_offsets':label_offsets,'compiled_dialogue_segment_offsets':segment_offsets,
        'speaker_body_policy':POLICY}
    rep={**report,'results':[results[r['id']] for r in report['results']],
        'speaker_body_review':{'policy':POLICY,'accepted':36,'remaining_reviewed_role_references':13,
        'new_changed_records':0,'instruction_windows':m['instruction_windows'],'results':m['entries'],
        'runtime_visual_status':'pending_user_verification','pcsx2_executed':False,
        'limits':'Existing legacy body checks, source-bound complete labels and original scalar lookup/copy/getter probes; no record/SSD growth, full renderer, aligned SIMD or PCSX2 execution.'}}
    return doc,compiled,rep

def tail_storage_survey(data,document,patches):
    """Restricted final-padding census; never authorizes moving SSD records."""
    import collections
    from dialogue_advanced import SsdIndex
    pending=json.loads((ROOT/'reports/rotulos-falantes-v037.json').read_text(encoding='utf-8'))['deferred']
    index=SsdIndex(data);blocks=collections.defaultdict(list)
    for row in index.records.values():blocks[row['block_offset']].append(row['instruction'])
    compiled={p['offset']:p['after'] for p in patches};text={e['offset']:e for e in document['entries']};rows=[]
    for key in [r['id'] for r in pending]:
        at=int(key.rsplit('.',1)[1],16);block=index.records[at]['block_offset'];stream=blocks[block];donors=[]
        target_pos=next(i for i,r in enumerate(stream) if r['offset']==at)
        for i,record in enumerate(stream):
            pos=record['offset'];entry=text.get(pos)
            if pos==at or entry is None or bytes.fromhex(entry['tag']) not in (b'msg\0',b'msgn'):continue
            raw=compiled.get(pos,bytes(data[pos:pos+record['size']]));spare=len(raw)-len(raw.rstrip(b'\0'))-1
            if spare<4:continue
            a,z=sorted((target_pos,i))
            donors.append({'id':entry['id'],'offset':pos,'final_padding_beyond_nul':spare,
                'instruction_distance':abs(target_pos-i),
                'intermediate_tags':[bytes(data[r['offset']:r['offset']+4]).rstrip(b'\0').decode('ascii') for r in stream[a+1:z]]})
        rows.append({'id':key,'ssd_offset':block,'instruction_count':len(stream),'tail_candidates':donors})
    return {'schema':1,'policy':'restricted-final-padding-survey-v001','parent':PARENT_MAP,
        'parent_sha256':sha((ROOT/PARENT_MAP).read_bytes()),'records':rows,
        'pending_examined':49,'distinct_ssd_blocks':len({r['ssd_offset'] for r in rows}),
        'with_final_padding_candidate':sum(bool(r['tail_candidates']) for r in rows),
        'single_record_blocks':sum(r['instruction_count']==1 for r in rows),
        'editing_authorized':False,'iso_created':False,
        'limits':'Only final zeros in other msg/msgn records after parent compilation. Not a census of interior separators or other layouts; does not prove movable commands, free container padding or safe growth/repacking.'}

if __name__=='__main__':
    import argparse,mmap
    from pathlib import Path
    from build_translation_pilot import load_draft,compile_draft
    from reinsertion import SOURCE
    p=argparse.ArgumentParser(description='Reproduzir o levantamento restrito de padding dos 49 rótulos, sem alterar jogo ou ISO')
    p.add_argument('--survey-output',type=Path,required=True);a=p.parse_args();output=a.survey_output.resolve()
    if output.exists() or not any(output.is_relative_to(ROOT/n) for n in ('work','reports')):
        raise ValueError('Use a new metadata file under work/ or reports/')
    draft,_=load_draft(ROOT/PARENT_MAP)
    with SOURCE.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        document,patches,_=compile_draft(data,draft);value=tail_storage_survey(data,document,patches)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(f"49 rótulos examinados; {value['with_final_padding_candidate']} com candidato restrito de padding final. Nenhuma edição autorizada pelo levantamento.")
