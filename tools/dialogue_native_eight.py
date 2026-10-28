"""Exact eight source-bound fallback messages; no general native input release.

Compile the immutable v040 parent with the historical compiler, then apply a
separate ASCII-only overlay. Extraction fingerprints and legacy policies stay
unchanged. All eight sites are committed together or none is returned.
"""
import copy,json,struct
from pathlib import Path
from dialogue import ROOT,sha
from glyph_spacing import ORIGINAL_SHA
from gfi import Gfi,encode,sjis_to_jis

POLICY='eight-source-bound-native-fallbacks-ascii-slots-v001'
PARENT_MAP='translations/regiao-inicial-v040.json'
PARENT_UI='translations/interface-v047.json'
MANIFEST='translations/dialogos-nativos-oito-v001.json'
SOURCE_BODY=bytes.fromhex('82ce82ae815b8142')
TARGET='Erro.'
RECORDS={
 'map.msg.040ef0ec':'9871ce83d3685affc1cf09b3c65d09e65e8fd3049d1966e1c6cd4e89325375e0',
 'map.msg.1033e304':'75042a44fd6e1ee336ac01066cf3e3155dc96f17ca13fbc43e7ac888a2e72430',
 'map.msg.1df7ec14':'e8da0a08981af3309e4be2186639e843058cee0181e23a16e451f7a7ec451675',
 'map.msg.1df7ed3c':'be824bea1ddf60da02800cdcfc9f9349eb709879a1b766718b3a3092dfabc240',
 'map.msg.1df7ee6c':'be824bea1ddf60da02800cdcfc9f9349eb709879a1b766718b3a3092dfabc240',
 'map.msg.1df88cd4':'be824bea1ddf60da02800cdcfc9f9349eb709879a1b766718b3a3092dfabc240',
 'map.msg.1df88d9c':'7aafb7bdf62444b22e9e223ec1bb6e6458d6edc099f917f6c18a853b58a071ae',
 'map.msg.1df88e6c':'7aafb7bdf62444b22e9e223ec1bb6e6458d6edc099f917f6c18a853b58a071ae',
}
WINDOWS=((0x1be268,0x1be278),(0x1bf9a0,0x1bf9d4),(0x30b4d0,0x30b508),
         (0x1c54a8,0x1c54ec),(0x1bdd88,0x1bddf8),(0x1ccf80,0x1ccf88))

def source_record(data,key):
    if key not in RECORDS:raise ValueError('Unreviewed native occurrence')
    at=int(key.rsplit('.',1)[1],16);raw=bytes(data[at:at+44])
    if sha(raw)!=RECORDS[key] or raw[:4]!=b'msg\0' or struct.unpack_from('<H',raw,6)[0]!=44:
        raise ValueError('Native fallback record fingerprint differs')
    if raw[32:]!=SOURCE_BODY+bytes(4):raise ValueError('Native fallback body/padding differs')
    return at,raw

def patch_record(data,key,target):
    at,raw=source_record(data,key)
    # An exact editorial decision, not arbitrary authoring enabled by a hash.
    if target!=TARGET:raise ValueError('Native fallback target is not the reviewed ASCII message')
    value=encode(target)
    if value!=b'Erro.' or len(value)>len(SOURCE_BODY):raise ValueError('Native fallback codec/budget differs')
    after=raw[:32]+value+bytes(12-len(value))
    if len(after)!=44 or after[:32]!=raw[:32] or after[32:].split(b'\0',1)[0]!=value:
        raise ValueError('Native fallback header/length/readback differs')
    return {'id':key,'resource':'DATA/MAP/MAP.MCT','offset':at,'before':raw,'after':after}

def marker_cases(elf,marks):
    from speaker_labels import _run
    if len(marks)!=len(set(marks)) or any(not 0<=i<65535 for i in marks):raise ValueError('Ambiguous local marker IDs')
    result=[]
    for selected in marks+[65535]:
        context=bytearray(0x30);nodes=bytearray(12*len(marks))
        struct.pack_into('<I',context,0x20,0x630000 if marks else 0)
        for i,mark in enumerate(marks):
            struct.pack_into('<II',nodes,i*12+4,0x630000+(i+1)*12 if i+1<len(marks) else 0,mark)
        regs=[0]*32;regs[4]=0x620000;regs[3]=selected
        r=_run(elf,0x1bdd94,((0x1bdd94,0x1bdde4),(0x1bddf0,0x1bddf8)),regs,
            [(0x620000,context),(0x630000,nodes)],0x1bdde4)
        expected=0x630000+marks.index(selected)*12 if selected in marks else 0
        if r[2]!=int(bool(expected)) or struct.unpack_from('<I',context,0x18)[0]!=expected:
            raise ValueError('Original marker lookup/setter differs')
        result.append({'marker':selected,'found':bool(expected),'correct_target_node':True})
    return result

def branch_cases(elf):
    """Original post-comparison if slice. Comparison and lookup are supplied.

    No script VM simulation: report precisely which two helpers are stubbed.
    """
    result=[]
    for condition,lookup in ((0,0),(1,0),(1,1)):
        regs=[0]*32;regs[2]=condition;regs[16]=0x620000;regs[17]=0x640000
        memory={0x620014:0x630000,0x630018:8};pc=0x1c54c0;pending=None;calls=[]
        for _ in range(40):
            if pc==0x1bdd88:
                calls.append(regs[5]);regs[2]=lookup;pc=regs[31];continue
            if pc==0x1c54ec:break
            if not 0x1c54c0<=pc<0x1c54ec:raise ValueError('If-slice probe escaped')
            w=struct.unpack_from('<I',elf,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31
            u=w&65535;n=u if u<32768 else u-65536;old=pending;pending=None
            if op==0:
                fn=w&63
                if fn in (33,45):regs[rd]=regs[rs]+regs[rt]
                elif fn==3:
                    value=regs[rt] if regs[rt]<0x80000000 else regs[rt]-0x100000000
                    regs[rd]=value>>((w>>6)&31)
                else:raise ValueError('Unexpected if-slice integer opcode')
            elif op in (4,5):pending=pc+4+n*4 if (regs[rs]==regs[rt])==(op==4) else pc+8
            elif op==9:regs[rt]=regs[rs]+n
            elif op==12:regs[rt]=regs[rs]&u
            elif op==35:regs[rt]=memory[(regs[rs]+n)&0xffffffff]
            elif op==3:regs[31]=pc+8;pending=((w&0x3ffffff)<<2)-0xff000
            else:raise ValueError('Unsupported if-slice instruction')
            regs=[r&0xffffffff for r in regs];regs[0]=0;pc=old if old is not None else pc+4
        else:raise ValueError('If-slice probe budget exceeded')
        if regs[2]!=(3 if condition and lookup else 2) or calls!=([4] if condition else []):raise ValueError('Original conditional lookup branch differs')
        result.append({'comparison_result_supplied':condition,'lookup_result_supplied':lookup,
                       'lookup_marker_arguments':calls,'return_code':regs[2]})
    return result

def evidence(data,elf,index=None):
    from dialogue_advanced import SsdIndex
    from interface_resources import original
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Fallback original ELF differs')
    if struct.unpack_from('<I',elf,0x30b4f4)[0]!=0x2c4490:raise ValueError('Original if virtual method differs')
    if struct.unpack_from('<II',elf,0x1ccf80)!=(0x03e00008,0x24020008):raise ValueError('Exit return path differs')
    index=SsdIndex(data) if index is None else index;rows=[]
    for key in RECORDS:
        at,raw=source_record(data,key);context=index.records[at]
        block=context['block_offset'];end=context['block_end']
        records=[v['instruction'] for v in index.records.values() if v['block_offset']==block]
        position=next(i for i,v in enumerate(records) if v['offset']==at)
        previous=records[position-1];ptag=bytes(data[previous['offset']:previous['offset']+4])
        if ptag not in (b'if\0\0',b'mark'):raise ValueError('Fallback predecessor structure differs')
        following=records[position+1:position+3]
        marks=[v['index'] for v in records if bytes(data[v['offset']:v['offset']+4])==b'mark']
        marker_probes=marker_cases(elf,marks)
        if ptag==b'mark' and (position!=len(records)-1 or bytes(data[records[position-2]['offset']:records[position-2]['offset']+4])!=b'exit' and bytes(data[records[position-2]['offset']:records[position-2]['offset']+4])!=b'scjp'):
            raise ValueError('Expected tail fallback after marker/exit-or-scjp')
        rows.append({'id':key,'offset':at,'size':44,'record_sha256':sha(raw),'body_sha256':sha(raw[32:40]),
            'original_body_bytes':8,'slot_capacity_bytes':11,'target_bytes':5,'translation':TARGET,
            'ssd_offset':block,'ssd_size':end-block,'ssd_sha256':sha(data[block:end]),
            'previous':{**previous,'tag_ascii':ptag.rstrip(b'\0').decode()},
            'following':following,'is_last_ssd_instruction':position==len(records)-1,
            'marker_ids':marks,'marker_lookup_cases':marker_probes})
    glyphs=[]
    for name in ('SUC20I22.GFI','SUC24I26.GFI'):
        raw=original('DATA/SYS/'+name);font=Gfi(raw)
        for pair in [SOURCE_BODY[i:i+2] for i in range(0,8,2)]:
            jis=sjis_to_jis(int.from_bytes(pair,'big'));at=font.glyph_offset(jis)
            if jis>>8==0x23 or not any(font.pixels(at)):raise ValueError('Native original glyph absent/collides')
            glyphs.append({'font':name,'jis':jis,'offset':at,'sha256':sha(raw[at:at+font.stride])})
        for char in set(TARGET):
            at=font.ascii_offset(char)
            if not any(font.pixels(at)):raise ValueError('Target ASCII glyph absent')
    return {'policy':POLICY,'records':rows,'elf_sha256':ORIGINAL_SHA,
        'instruction_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS],
        'original_if_postcomparison_cases':branch_cases(elf),'original_source_glyphs':glyphs,
        'distinct_bodies':1,'distinct_record_fingerprints':len(set(RECORDS.values())),
        'interpretation':'Short repeated error/fallback notices, supported by local battle/conditional and tail-marker contexts. Not declared unreachable or safe to remove.',
        'probe_limits':'Original marker lookup/setter and post-comparison branch slices in synthetic RAM; comparison/lookup supplied for the if slice. Full dispatch, battle outcomes, inter-script transitions, complete VM and PCSX2 not executed.'}

def load(binding):
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:raise ValueError('Native eight binding outside its single manifest')
    raw=(ROOT/MANIFEST).read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('Native eight manifest changed')
    m=json.loads(raw)
    fields={'schema','policy','parent_map','parent_map_sha256','parent_interface','parent_interface_sha256','translations','evidence'}
    if set(m)!=fields or m.get('schema')!=1 or m.get('policy')!=POLICY or m.get('parent_map')!=PARENT_MAP or m.get('parent_interface')!=PARENT_UI:raise ValueError('Native eight parent/policy differs')
    if sha((ROOT/PARENT_MAP).read_bytes())!=m['parent_map_sha256'] or sha((ROOT/PARENT_UI).read_bytes())!=m['parent_interface_sha256']:raise ValueError('Native eight parent fingerprint differs')
    if m['translations']!={key:TARGET for key in RECORDS}:raise ValueError('Native eight exact translations differ')
    return m

def validate_narrative(draft):
    from build_translation_pilot import load_draft
    binding=draft['native_fallback_review'];load(binding);expected,_=load_draft(ROOT/PARENT_MAP)
    expected=copy.deepcopy(expected)
    for key in RECORDS:
        if key not in expected['deferred'] or key in expected['translations']:raise ValueError('Native eight parent deferral differs')
        expected['deferred'].pop(key);expected['translations'][key]=TARGET
    expected.update(native_fallback_review=binding,name='regiao-inicial-v041',
        status='Oito avisos nativos de erro traduzidos; demais registros v040 preservados.',reviewed_changes=list(RECORDS))
    if draft!=expected:raise ValueError('Non-authorized native eight narrative change')

def validate_interface(recipe):
    if 'speaker_body_review' in recipe:
        from speaker_body_review import validate_interface as validate_speakers
        return validate_speakers(recipe)
    binding=recipe['native_fallback_review'];load(binding)
    expected=json.loads((ROOT/PARENT_UI).read_text(encoding='utf-8'))
    expected.update(native_fallback_review=binding,base_dialogue_draft='translations/regiao-inicial-v041.json',
        iso_name='MetalSaga-ptbr-interface-v048.iso',status='Oito avisos nativos traduzidos; interface v047 integralmente preservada.')
    if recipe!=expected:raise ValueError('Non-authorized native eight interface change')

def compile_overlay(data,draft):
    from build_translation_pilot import compile_draft,load_draft
    from interface_text import SOURCE
    validate_narrative(draft);m=load(draft['native_fallback_review']);proof=evidence(data,SOURCE.read_bytes())
    if proof!=m['evidence']:raise ValueError('Native eight source/control-flow/glyph evidence differs')
    parent,_=load_draft(ROOT/PARENT_MAP);document,patches,report=compile_draft(data,parent)
    if not report['valid'] or report['refused']:raise ValueError('Native eight parent compilation invalid')
    additional=[patch_record(data,key,draft['translations'][key]) for key in RECORDS]
    patches=sorted(patches+additional,key=lambda p:p['offset'])
    if any(a['offset']+len(a['before'])>b['offset'] for a,b in zip(patches,patches[1:])):raise ValueError('Native eight overlap')
    entries=[]
    for entry in document['entries']:
        if entry['id'] in RECORDS:
            entry=copy.deepcopy(entry)
            if len(entry['segments'])!=1 or entry['segments'][0]['source_hex']!=SOURCE_BODY.hex():raise ValueError('Native eight descriptor differs')
            entry['segments'][0]['translation']=TARGET
        entries.append(entry)
    # Historical extraction blocking stays unchanged in each descriptor;
    # opt-in approval is explicitly recorded in the compiled wrapper only.
    document={**document,'entries':entries,'compiled_native_fallback_overlay':proof}
    results=[];seen=set()
    for result in report['results']:
        if result['id'] in RECORDS:
            if result['status']!='unchanged':raise ValueError('Native eight parent unexpectedly edited')
            result={'id':result['id'],'status':'accepted','policy':POLICY,'warnings':[]};seen.add(result['id'])
        results.append(result)
    if seen!=set(RECORDS):raise ValueError('Native eight missing compiled parent record')
    report={**report,'results':results,'accepted':report['accepted']+8,'unchanged':report['unchanged']-8,
        'deferred':[r for r in report['deferred'] if r['id'] not in RECORDS],
        'native_fallback_overlay':proof,'runtime_visual_status':'pending_user_verification'}
    return document,patches,report
