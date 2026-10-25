"""Borrow only trailing, compiled separator zeros for a longer generic label."""
import copy
from speaker_labels import ROLES,validate_label,probe,_run
from gfi import encode,BYTES_TO_CHAR
from dialogue import sha
POLICY='map-generic-speaker-label-same-record-tail-borrow-v002'
BYTE_POLICY='map-generic-speaker-label-byte-tail-borrow-v003'
WINDOWS=((0x1c649c,0x1c64b4),(0x1c6508,0x1c6550),(0x1c6d8c,0x1c6de8),
 (0x2262c8,0x2262d4),(0x22643c,0x226468))

def bindings(elf):
    from speaker_labels import bindings as original_bindings
    original_bindings(elf)
    return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]

def locate(elf,payload,previous,family):
    """Execute original scalar strchr and zero-skip with bounded synthetic RAM.

    Unaligned helper input selects scalar code. No SIMD/drawing/objects run.
    """
    address=0x640001-previous;regions=[(address,bytearray(payload))]
    regs=[0]*32;regs[4]=address+previous;regs[5]=0;regs[31]=0x700000
    found=_run(elf,0x2262c8,WINDOWS,regs,regions,0x700000)[2]
    if found!=address+payload.index(0,previous):raise ValueError('Speaker preceding terminator differs')
    regs=[0]*32;regions.append((0x660000,bytearray(16)));regs[29]=0x660000
    if family==b'msgn':
        regs[18]=found;start=0x1c6508;stop=0x1c653c;result_register=18
    elif family in (b'smnn',b'2snm'):
        regs[17]=found;start=0x1c6d9c;stop=0x1c6dd4;result_register=16
    else:raise ValueError('Unproved label traversal family')
    result=_run(elf,start,WINDOWS,regs,regions,stop)
    return result[result_register]-address

def placement(base,entry,target,*,alignment=4):
    if alignment not in (1,4):raise ValueError('Unsupported speaker-label alignment')
    if entry['mode']!='slots' or entry['blocked_reasons']:raise ValueError('Blocked/non-slot label relocation')
    if bytes.fromhex(entry['tag']) not in (b'msgn',b'smnn',b'2snm'):raise ValueError('Unproved label relocation family')
    label=entry['segments'][-1];previous=entry['segments'][-2]
    if label['key']!='label' or label['editable'] or label['translation']!=label['source']:raise ValueError('Previously edited/invalid label')
    raw=validate_label(label['source'],target,len(base));old=label['offset']-entry['offset']
    if len(raw)<=label['capacity']:raise ValueError('Use fixed-slot label policy when it fits')
    previous_start=previous['offset']-entry['offset'];nul=base.index(0,previous_start)
    start=(len(base)-len(raw)-1)&~(alignment-1)
    if not previous_start<=nul<start<old:raise ValueError('Insufficient separator zeros for label')
    if alignment==1 and start%4==0:raise ValueError('Use aligned label relocation policy')
    src=bytes.fromhex(label['source_hex'])
    if base[nul+1:old]!=bytes(old-nul-1) or base[old:]!=src+bytes(len(base)-old-len(src)):raise ValueError('Label tail/separator not pristine')
    return start,raw,nul

def byte_copy_probe(elf,raw,alignment):
    """Execute original scalar strcpy with aligned heap destination, unaligned source."""
    if alignment not in range(1,8) or not raw or b'\0' in raw:raise ValueError('Invalid byte-copy probe')
    source=0x690000+alignment;destination=0x680000
    original=bytearray(raw+b'\0');output=bytearray(b'\xa5'*(len(raw)+1)+b'GUARD')
    registers=[0]*32;registers[4]=destination;registers[5]=source;registers[31]=0x700000
    from speaker_labels import WINDOWS as COPY_WINDOWS
    result=_run(elf,0x2265b4,COPY_WINDOWS,registers,[(source,original),(destination,output)],0x700000)
    if result[2]!=destination or output!=raw+b'\0GUARD' or original!=raw+b'\0':raise ValueError('Byte-positioned label copy differs')
    return True

def overlay(data,document,patches,report,config,elf,preserved=(),*,byte_packed=False):
    policy=BYTE_POLICY if byte_packed else POLICY
    if not report['valid'] or config.get('policy')!=policy or config.get('instruction_windows')!=bindings(elf):raise ValueError('Invalid label relocation binding/base')
    doc=copy.deepcopy(document);rep=copy.deepcopy(report);out={p['id']:dict(p) for p in patches}
    entries={e['id']:e for e in doc['entries']};results={r['id']:r for r in rep['results']}
    offsets=dict(document.get('compiled_speaker_label_offsets',{})) if byte_packed else {}
    rows=[];seen=set();new_records=0
    for item in config['entries']:
        key=item['id']
        if key in seen or key in preserved:raise ValueError('Duplicate/protected label relocation')
        seen.add(key);entry=entries[key];label=entry['segments'][-1];old=label['offset']-entry['offset']
        original=bytes(data[entry['offset']:entry['offset']+entry['size']]);src=bytes.fromhex(label['source_hex'])
        if (sha(original),sha(src))!=(item['record_sha256'],item['label_sha256']) or sha(original)!=entry['record_sha256']:raise ValueError('Label relocation source mismatch')
        prior=out.get(key);base=prior['after'] if prior else original
        if prior and prior['before']!=original:raise ValueError('Label relocation base differs')
        start,raw,nul=placement(base,entry,item['translation'],alignment=1 if byte_packed else 4)
        if item['target_offset']!=entry['offset']+start or item['base_record_sha256']!=sha(base):raise ValueError('Compiled label placement binding differs')
        after=base[:start]+raw+bytes(len(base)-start-len(raw))
        if after[:nul+1]!=base[:nul+1] or len(after)!=len(original):raise ValueError('Label relocation damaged preceding string')
        family=bytes.fromhex(entry['tag']);previous=entry['segments'][-2]['offset']-entry['offset']
        if locate(elf,base,previous,family)!=old or locate(elf,after,previous,family)!=start:raise ValueError('Original label traversal differs')
        evidence=probe(elf,raw)
        if byte_packed:
            # Either possible mod-8 class for a mod-4-aligned SSD allocation.
            residue=(entry['offset']+start)%4
            if residue==0:raise ValueError('Byte policy requires an unaligned label')
            for alignment in (residue,residue+4):byte_copy_probe(elf,raw,alignment)
            evidence['aligned_destination_scalar_copy']=True
        shadow=bytearray(after);expected=[s['offset']-entry['offset'] for s in entry['segments']];expected[-1]=start
        for at in expected:
            text=after[at:].split(b'\0',1)[0];i=0
            while i<len(text):
                if text[i:i+2] in BYTES_TO_CHAR:shadow[at+i:at+i+2]=b'aa';i+=2
                else:i+=1
        if family==b'msgn':
            from dialogue_formats import parse_msgn
            parsed,_=parse_msgn(shadow,0);found=[parsed['text_offset'],parsed['display_label']['text_offset']]
        else:
            from dialogue_advanced import parse
            _,parsed=parse(shadow,0);found=[s['text_offset'] for s in parsed['segments']]
        if found!=expected:raise ValueError('Relocated label structural parse differs')
        label['translation']=item['translation'];offsets[key]=entry['offset']+start
        out[key]={'resource':doc['resource'],'id':key,'offset':entry['offset'],'before':original,'after':after}
        row=results[key]
        if row['status']=='unchanged':
            new_records+=1;row.update(status='accepted',mode='slots',warnings=[],record_offset=entry['offset'],record_size=entry['size'],block_offset=entry['block_offset'],visual_status='pending_manual_validation')
        elif row['status']!='accepted':raise ValueError('Refused label relocation base')
        row.update(source_lengths=[len(bytes.fromhex(s['source_hex'])) for s in entry['segments']],
            target_lengths=[len(encode(s['translation'])) for s in entry['segments']],
            source_capacities=[s['capacity'] for s in entry['segments']],source_offsets=[s['offset'] for s in entry['segments']],
            target_offsets=[entry['offset']+i for i in expected],speaker_label_relocated=True)
        rows.append({'id':key,'source_offset':label['offset'],'target_offset':entry['offset']+start,
            'borrowed_separator_bytes':old-start,'preceding_nul_offset':entry['offset']+nul,
            'target_sha256':sha(raw),**evidence})
    if not rows:raise ValueError('Empty label relocation batch')
    compiled=sorted(out.values(),key=lambda p:p['offset'])
    if any(a['offset']+len(a['before'])>b['offset'] for a,b in zip(compiled,compiled[1:])):raise ValueError('Relocated label patches overlap')
    doc['compiled_speaker_label_offsets']=offsets
    doc['speaker_label_byte_policy' if byte_packed else 'speaker_label_relocation_policy']=policy
    rep.update(accepted=len(compiled),unchanged=len(doc['entries'])-len(compiled),requires_ptbr_fonts=True)
    rep['speaker_label_byte_packing' if byte_packed else 'speaker_label_relocations']={'policy':policy,'accepted':len(rows),'new_changed_records':new_records,
        'instruction_windows':bindings(elf),'results':rows,'bodies_choices_headers_and_record_boundaries_unchanged':True,
        'extraction_metadata_unchanged':True,'pcsx2_executed':False,'runtime_visual_status':'pending_user_verification',
        'limits':'Original scalar strchr and zero-skip scanners executed in synthetic memory for both old/new records; aligned SIMD, complete caller, objects, drawing and portraits not executed; original record/SSD/ISO extents preserved'}
    return doc,compiled,rep
