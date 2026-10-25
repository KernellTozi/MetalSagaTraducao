"""Reviewed character titles in bounded original cells; pointer tables immutable."""
import struct
from glyph_spacing import ORIGINAL_SHA
from interface_resources import sha
from gfi import encode,decode
from password_graphics import run,memory32

POLICY='character-title-original-cells-v001'
GROUPS=((0x264338,47),(0x2643f8,7),(0x264418,7),(0x264438,8),(0x264458,8),
        (0x348c38,1),(0x348c40,1),(0x348c48,1),(0x348c50,1),(0x348c58,1))
WINDOWS=((0x6bb60,0x6bb84),(0x118a18,0x118a34),(0x118a68,0x118a8c),
         (0x1b5d60,0x1b5d74),(0x1cd374,0x1cd388),(0x264338,0x2644a0),
         (0x348c38,0x348c60))
PRESERVED={0x348c20,0x3199c0,0x319a70,0x319b10,0x319d30}


def bindings(elf):return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]


def lookup(elf,group,index):
    if not 0<=group<len(GROUPS) or not 0<=index<GROUPS[group][1]:raise ValueError('Title lookup outside reviewed group')
    regs=[0]*32;regs[4]=group;regs[5]=index;regs[31]=0x5ff000
    return run(elf,0x6bb60,0x6bb84,0x500000,regs,{})[2]


def catalog(elf):
    rows={}
    for start,count,step in ((0x3198f0,71,16),(0x348bf8,8,8)):
        for at in range(start,start+count*step,step):
            cell=elf[at:at+step];end=cell.find(b'\0')
            if end<0 or any(cell[end:]) or any(not 32<=c<127 for c in cell[:end]):raise ValueError('Title cell layout differs')
            rows[at]={'id':f'character.title.{at:08x}','offset':at,'size':step,'capacity':step-1,
                'source':cell[:end].decode('ascii'),'source_sha256':sha(cell),'references':[]}
    for group,(base,count) in enumerate(GROUPS):
        if struct.unpack_from('<I',elf,0x264478+group*4)[0]!=base+0xff000:raise ValueError('Title group table differs')
        expected_boundary={3:0x418c90,4:0x363338}.get(group,0)
        if struct.unpack_from('<I',elf,base+count*4)[0]!=expected_boundary:raise ValueError('Title group boundary differs')
        for index in range(count):
            at=struct.unpack_from('<I',elf,base+index*4)[0]-0xff000
            if at not in rows:raise ValueError('Title pointer outside proved cells')
            rows[at]['references'].append({'group':group,'index':index,'pointer_offset':base+index*4})
    if any(not r['references'] for r in rows.values()):raise ValueError('Unreferenced title cell')
    return [r for r in rows.values() if r['source']]


def proof(elf):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Title ELF revision mismatch')
    rows=catalog(elf);cases=[]
    from interface_text import references,sections
    refs=references(elf,sections(elf))
    for row in rows:
        base=row['offset']+0xff000
        if any(base+i in refs for i in range(1,row['size'])):raise ValueError('Title interior reference not approved')
        known=refs.get(base,[]);expected={r['pointer_offset'] for r in row['references']}
        if (any(r['kind']!='data-pointer' for r in known)
            or {r['offset'] for r in known}!=expected):raise ValueError('Title references differ from proved tables')
    for r in rows:
        for ref in r['references']:
            group,index=ref['group'],ref['index'];pointer=lookup(elf,group,index)
            if pointer!=r['offset']+0xff000:raise ValueError('Original title lookup differs')
            # Original status caller passes class/title index, including the delay-slot load.
            regs=[0]*32;regs[16]=0x620000;regs[20]=0x630000
            mem=memory32(((0x62035c,0x640000),(0x63005c,index),(0x63002c,group),(0x640004,0x650000)))
            a=run(elf,0x118a18,0x118a34,0x6bb60,regs,mem)
            if (a[4],a[5],a[19])!=(group,index,0x650000):raise ValueError('Title status arguments differ')
            regs=[0]*32;regs[18]=pointer;regs[19]=0x650000;regs[16]=0x42a6a0
            regs[20]=0x630000;regs[29]=0x640000
            a=run(elf,0x118a68,0x118a8c,0x10e608,regs,memory32(((0x630054,123),)))
            if a[7]!=pointer or a[5]!=0x42a6a0:raise ValueError('Title string formatting argument differs')
            cases.append({'group':group,'index':index,'string_offset':r['offset']})
    return {'instruction_windows':bindings(elf),'unique_nonempty_titles':len(rows),'nonempty_lookup_cases':len(cases),
        'group_counts':[n for _,n in GROUPS],'original_maximum_title_bytes':max(len(r['source']) for r in rows),
        'cases':cases,'scope':'Original bounded lookup and status call arguments in synthetic RAM; formatter, input, drawing and PS2 not executed'}


def compile_titles(elf,config):
    evidence=proof(elf)
    if config.get('policy')!=POLICY or config.get('instruction_windows')!=bindings(elf):raise ValueError('Title policy/code evidence differs')
    if set(config)!= {'policy','instruction_windows','entries','preserved'}:raise ValueError('Unknown title configuration fields')
    rows={r['id']:r for r in catalog(elf)};entries=config['entries'];preserved=config['preserved']
    expected_preserved={f'character.title.{at:08x}' for at in PRESERVED}
    if set(preserved)!=expected_preserved or any(not isinstance(v,str) or not v.strip() for v in preserved.values()):raise ValueError('Title preservation decisions differ')
    ids=[r['id'] for r in entries]
    if len(ids)!=len(set(ids)) or set(ids)&set(preserved) or set(ids)|set(preserved)!=set(rows):raise ValueError('Incomplete/duplicate title review')
    patches=[];results=[]
    from translation_policy import validate
    for target in entries:
        if set(target)!={'id','source_sha256','translation'}:raise ValueError('Unknown title target fields')
        old=rows[target['id']];at=old['offset'];before=elf[at:at+old['size']]
        if target['source_sha256']!=old['source_sha256']:raise ValueError('Title source differs')
        text=target['translation'];after=encode(text)
        if (not after or len(after)>old['capacity'] or any(c in after for c in b'\0\n\t%')
            or decode(after)!=text or after==before.split(b'\0')[0]):raise ValueError('Title target/slot differs')
        issues=validate(old['source'],text)
        if issues:raise ValueError('Title terminology: '+'; '.join(issues))
        after=after+bytes(old['size']-len(after))
        patches.append({'id':old['id'],'resource':'SLUS_212.93','offset':at,'before':before,'after':after})
        results.append({'id':old['id'],'offset':at,'source_sha256':sha(before),'target_sha256':sha(after),
            'source_bytes':len(old['source']),'target_bytes':len(encode(text)),'slot_bytes':old['size'],
            'references':old['references']})
    return patches,{'policy':POLICY,'accepted':len(patches),'preserved':len(preserved),'results':results,
        'evidence':evidence,'pointers_code_frames_and_other_cells_unchanged':True,'runtime_visual_status':'pending_user_verification'}
