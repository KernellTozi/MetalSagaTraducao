"""Context-reviewed generic labels and bounded named-choice separator reuse."""
import copy
from dialogue import sha
from gfi import encode,decode,BYTES_TO_CHAR
from speaker_labels import ROLES,probe,_run
from speaker_label_space import locate,byte_copy_probe,WINDOWS as TAIL_WINDOWS,bindings as tail_bindings
POLICY='map-context-reviewed-speaker-layout-v004'
# Role captions reviewed with their adjacent dialogue, never a name heuristic.
EXTRA={'Muscle Man':'Musculoso','Executive Believer':'Fiel dirigente',
       'Bus Maniac':'Fã de ônibus','Hunter Office employee':'Agente do Hunter Office'}
WINDOWS=TAIL_WINDOWS+((0x1c6cc0,0x1c6cd4),(0x1c6d2c,0x1c6d68))

def bindings(elf):
    tail_bindings(elf)
    return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]

def locate_choices(elf,payload,body):
    address=0x640001-body;regions=[(address,bytearray(payload))]
    regs=[0]*32;regs[4]=address+body;regs[5]=0;regs[31]=0x700000
    found=_run(elf,0x2262c8,WINDOWS,regs,regions,0x700000)[2]
    if found!=address+payload.index(0,body):raise ValueError('Named-choice body terminator mismatch')
    regs=[0]*32;regs[23]=found
    result=_run(elf,0x1c6d2c,WINDOWS,regs,regions,0x1c6d68)
    return result[6]-address

def construct(base,entry,target):
    family=bytes.fromhex(entry['tag']);segments=entry['segments'];label=segments[-1]
    if family not in (b'msgn',b'smnn',b'2snm') or entry['mode']!='slots' or entry['blocked_reasons']:raise ValueError('Blocked/unproved reviewed speaker record')
    if label['key']!='label' or label['editable'] or label['translation']!=label['source']:raise ValueError('Reviewed speaker label already edited')
    source=label['source'];extra=source in EXTRA
    if target!=(EXTRA if extra else ROLES).get(source):raise ValueError('Unreviewed contextual role/target')
    from translation_policy import validate
    if validate(source,target):raise ValueError('Reviewed role violates terminology')
    raw=encode(target)
    if decode(raw)!=target or not raw or any(c in raw for c in (0,9,10,13,37)):raise ValueError('Reviewed role codec/control mismatch')
    offsets=[s['offset']-entry['offset'] for s in segments]
    values=[base[at:].split(b'\0',1)[0] for at in offsets]
    old=offsets[-1];previous=offsets[-2];nul=base.index(0,previous)
    src=bytes.fromhex(label['source_hex'])
    if base[old:]!=src+bytes(len(base)-old-len(src)) or base[nul+1:old]!=bytes(old-nul-1):raise ValueError('Reviewed label tail/separator differs')
    if extra:
        start=min(old,len(base)-len(raw)-1)
        if start<=nul:raise ValueError('Reviewed role does not fit proven tail')
        after=base[:start]+raw+bytes(len(base)-start-len(raw));offsets[-1]=start
        layout='fixed-label-slot' if start==old else 'label-tail-bytes'
    else:
        if family not in (b'smnn',b'2snm') or len(segments)!=3 or [s['key'] for s in segments]!=['body','choices','label']:raise ValueError('Choice packing only for existing reviewed roles')
        # This policy is only for leftovers that cannot fit after current choices.
        start=len(base)-len(raw)-1
        if start>nul:raise ValueError('Use existing tail-only profile')
        choices=(start-len(values[1])-1)&~3;body_end=offsets[0]+len(values[0])
        if not body_end<choices<offsets[1] or start<=choices+len(values[1]):raise ValueError('Insufficient question/choice separator space')
        if base[body_end+1:offsets[1]]!=bytes(offsets[1]-body_end-1):raise ValueError('Question separator contains data')
        after=base[:body_end+1]+bytes(choices-body_end-1)+values[1]+b'\0'
        after+=bytes(start-len(after))+raw+bytes(len(base)-start-len(raw))
        offsets[1:]=[choices,start];layout='named-choice-separator-pack'
    if len(after)!=len(base) or after[:len(bytes.fromhex(entry['header_hex']))]!=bytes.fromhex(entry['header_hex']):raise ValueError('Reviewed role resized record/header')
    for at,value in zip(offsets[:-1],values[:-1]):
        if after[at:at+len(value)+1]!=value+b'\0':raise ValueError('Reviewed role changed preceding text/controls')
    return after,offsets,layout

def overlay(data,document,patches,report,config,elf,preserved=()):
    if not report['valid'] or config.get('policy')!=POLICY or config.get('instruction_windows')!=bindings(elf):raise ValueError('Reviewed speaker policy/source mismatch')
    doc=copy.deepcopy(document);rep=copy.deepcopy(report);out={p['id']:dict(p) for p in patches}
    entries={e['id']:e for e in doc['entries']};results={r['id']:r for r in rep['results']}
    label_offsets=dict(doc.get('compiled_speaker_label_offsets',{}));segment_offsets=copy.deepcopy(doc.get('compiled_dialogue_segment_offsets',{}))
    seen=set();rows=[];new_records=0
    for item in config['entries']:
        key=item['id']
        if key in seen or key in preserved:raise ValueError('Duplicate/protected reviewed speaker ID')
        seen.add(key);e=entries[key];label=e['segments'][-1]
        original=bytes(data[e['offset']:e['offset']+e['size']]);prior=out.get(key);base=prior['after'] if prior else original
        if prior and prior['before']!=original:raise ValueError('Reviewed role patch baseline mismatch')
        if (sha(original),sha(bytes.fromhex(label['source_hex'])),sha(base))!=(item['record_sha256'],item['label_sha256'],item['base_record_sha256']) or sha(original)!=e['record_sha256']:raise ValueError('Reviewed role hashes differ')
        after,positions,layout=construct(base,e,item['translation'])
        expected=[e['offset']+at for at in positions]
        if item['target_offsets']!=expected or item['layout']!=layout:raise ValueError('Reviewed role placement binding differs')
        family=bytes.fromhex(e['tag']);old=[s['offset']-e['offset'] for s in e['segments']]
        if len(positions)==3:
            if locate_choices(elf,base,old[0])!=old[1] or locate_choices(elf,after,positions[0])!=positions[1]:raise ValueError('Original question-to-choice traversal differs')
        if locate(elf,base,old[-2],family)!=old[-1] or locate(elf,after,positions[-2],family)!=positions[-1]:raise ValueError('Original reviewed label traversal differs')
        raw=encode(item['translation']);evidence=probe(elf,raw);residue=expected[-1]%4
        if residue:
            for a in (residue,residue+4):byte_copy_probe(elf,raw,a)
        shadow=bytearray(after)
        for at in positions:
            value=after[at:].split(b'\0',1)[0];i=0
            while i<len(value):
                if value[i:i+2] in BYTES_TO_CHAR:shadow[at+i:at+i+2]=b'aa';i+=2
                else:i+=1
        if family==b'msgn':
            from dialogue_formats import parse_msgn
            parsed,_=parse_msgn(shadow,0);found=[parsed['text_offset'],parsed['display_label']['text_offset']]
        else:
            from dialogue_advanced import parse
            _,parsed=parse(shadow,0);found=[s['text_offset'] for s in parsed['segments']]
        if found!=positions:raise ValueError('Reviewed role structural round-trip differs')
        label['translation']=item['translation'];label_offsets[key]=expected[-1]
        segment_offsets[key]={s['key']:at for s,at in zip(e['segments'],expected)}
        out[key]={'id':key,'resource':doc['resource'],'offset':e['offset'],'before':original,'after':after}
        result=results[key]
        if result['status']=='unchanged':
            new_records+=1;result.update(status='accepted',mode='slots',warnings=[],record_offset=e['offset'],record_size=e['size'],block_offset=e['block_offset'],visual_status='pending_manual_validation')
        elif result['status']!='accepted':raise ValueError('Refused reviewed speaker base')
        result.update(source_offsets=[s['offset'] for s in e['segments']],target_offsets=expected,
            source_lengths=[len(bytes.fromhex(s['source_hex'])) for s in e['segments']],
            target_lengths=[len(encode(s['translation'])) for s in e['segments']],source_capacities=[s['capacity'] for s in e['segments']],speaker_context_review=True)
        rows.append({'id':key,'layout':layout,'target_offsets':expected,'target_sha256':sha(raw),**evidence})
    if not rows:raise ValueError('Empty reviewed speaker batch')
    compiled=sorted(out.values(),key=lambda p:p['offset'])
    if any(a['offset']+len(a['before'])>b['offset'] for a,b in zip(compiled,compiled[1:])):raise ValueError('Reviewed speaker patches overlap')
    doc.update(compiled_speaker_label_offsets=label_offsets,compiled_dialogue_segment_offsets=segment_offsets,speaker_context_policy=POLICY)
    rep.update(accepted=len(compiled),unchanged=len(doc['entries'])-len(compiled),requires_ptbr_fonts=True)
    rep['speaker_context_review']={'policy':POLICY,'accepted':len(rows),'new_changed_records':new_records,
        'instruction_windows':bindings(elf),'results':rows,'pcsx2_executed':False,
        'runtime_visual_status':'pending_user_verification','limits':'Original scalar searches, zero scanners and label copy probes only; complete choice helper, aligned SIMD, objects, allocator and drawing not executed; body/options bytes preserved exactly'}
    return doc,compiled,rep
