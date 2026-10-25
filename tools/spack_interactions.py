"""Proven counted pools for item reactions and bar text, bounded in original extents."""
import hashlib,re,struct
from item_descriptions import original,RESOURCE
from glyph_spacing import ORIGINAL_SHA
from plan_interface_menus import counted_strings
from spack_ui import execute_sda_pointer,_reader
from spack_battle import _run
from gfi import encode,decode

POLICY='spack-reactions-and-bar-original-counted-pools-v001'
REACTION_BASE,REACTION_SIZE,REACTION_COUNT=0x325d0,8864,179
BAR_BASE,BAR_SIZE,BAR_COUNT=0x11c820,3744,172
WINDOWS=((0x70bc4,0x70bd8),(0x709c8,0x70a64),(0x1e26ac,0x1e273c),
         (0x1e2ed4,0x1e2ef8),(0x1e33b4,0x1e33ec),(0x1e35e8,0x1e3664))
def sha(data):return hashlib.sha256(data).hexdigest()
def bindings(elf):return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]

def catalog(raw,kind):
    if kind=='bar':
        table=counted_strings(raw,BAR_BASE,BAR_SIZE,BAR_COUNT);result=[]
        for row in table['entries']:
            relative=row['text_offset']-BAR_BASE if 'text_offset' in row else row['offset']-BAR_BASE
            result.append({'id':f'bar.{row["pointer_ids"][0]:04d}','offset':BAR_BASE+relative,
                'source_hex':row['source_hex'],'source_sha256':row['source_sha256'],
                'references':[4+4*i for i in row['pointer_ids']]})
        base,size,header=BAR_BASE,BAR_SIZE,4+4*BAR_COUNT
    elif kind=='reaction':
        base,size,header=REACTION_BASE,REACTION_SIZE,4+16*REACTION_COUNT
        if struct.unpack_from('<I',raw,base)[0]!=REACTION_COUNT:raise ValueError('Reaction count changed')
        groups={}
        for i in range(REACTION_COUNT):
            for variant in range(3):
                field=4+i*16+4+variant*4;offset=struct.unpack_from('<I',raw,base+field)[0]
                if not header<=offset<size:raise ValueError('Reaction pointer outside original pool')
                groups.setdefault(offset,[]).append(field)
        result=[]
        for relative,refs in sorted(groups.items()):
            at=base+relative;end=raw.find(b'\0',at,base+size)
            if end<0:raise ValueError('Unterminated reaction')
            value=raw[at:end];result.append({'id':f'reaction.{relative:05x}','offset':at,
                'source_hex':value.hex(),'source_sha256':sha(value),'references':refs})
    else:raise ValueError('Unknown interaction pool')
    claimed=bytearray(size);claimed[:header]=bytes([1])*header
    for row in result:
        lo=row['offset']-base;n=len(bytes.fromhex(row['source_hex']))+1
        if any(claimed[lo:lo+n]):raise ValueError('Overlapping interaction strings')
        claimed[lo:lo+n]=bytes([1])*n
    end=max(row['offset']-base+len(bytes.fromhex(row['source_hex']))+1 for row in result)
    if any(raw[base+i] for i,v in enumerate(claimed[:end]) if not v):raise ValueError('Unclaimed interior interaction bytes are not zero')
    # Reaction tail has opaque nonzero words: preserve the entire original tail,
    # including zero bytes before those words. It is not translation capacity.
    limit=end if any(raw[base+i] for i in range(end,size)) else size
    return {'base':base,'size':size,'header':header,'pool_end':limit,'rows':result,'sha256':sha(raw[base:base+size])}

def execute_reaction(elf,table,index,variant):
    if not 0<=index<REACTION_COUNT or not 0<=variant<3:raise ValueError('Reaction probe index outside table')
    regs=[0]*32;regs[17]=0x600000;regs[6]=0x600004;regs[3]=index;regs[7]=variant;regs[29]=0x620000
    read=_reader([(0x600000,table),(0x620000,bytes(64))])
    out=_run(elf,0x70a38,0x70a58,regs,read,0x70a58)
    return out[2]-0x600000

def execute_bar(elf,table,index):
    if not 0<=index<BAR_COUNT:raise ValueError('Bar probe index outside table')
    regs=[0]*32;regs[2]=index;regs[17]=0x600000
    out=_run(elf,0x1e2edc,0x1e2ef0,regs,_reader([(0x600000,table)]),0x1e2ef0)
    return out[3]-0x600000

def rebuild(raw,table,targets):
    base,size,header=table['base'],table['size'],table['header'];limit=table['pool_end']
    out=bytearray(raw[base:base+header])+bytearray(limit-header)+bytearray(raw[base+limit:base+size]);cursor=header
    for row in table['rows']:
        value=targets.get(row['id'],bytes.fromhex(row['source_hex']))
        if cursor+len(value)+1>limit:raise ValueError('Interaction pool exceeds original text region')
        for ref in row['references']:struct.pack_into('<I',out,ref,cursor)
        out[cursor:cursor+len(value)]=value;cursor+=len(value)+1
    return bytes(out),cursor

def validate_value(row,text,table):
    before=bytes.fromhex(row['source_hex']);value=encode(text)
    if (not before or any(c<32 or c>126 for c in before) or b'%' in before or before.startswith(b'*')
        or not value or value==before or any(c in value for c in (0,9,10,13,37)) or decode(value)!=text):
        raise ValueError('Interaction source/control/glyph blocked')
    if re.findall(rb'\d+',before)!=re.findall(rb'\d+',value):raise ValueError('Interaction numeric facts changed')
    if before.count(b'|')!=value.count(b'|'):raise ValueError('Interaction line count changed')
    if re.match(rb' *',before).group()!=re.match(rb' *',value).group() or re.search(rb' *$',before).group()!=re.search(rb' *$',value).group():
        raise ValueError('Interaction edge spacing changed')
    maxbytes=max(len(bytes.fromhex(r['source_hex'])) for r in table['rows'])
    maxcols=max(max(map(len,bytes.fromhex(r['source_hex']).split(b'|'))) for r in table['rows'])
    if len(value)>maxbytes or max(map(len,text.split('|')))>maxcols:raise ValueError('Interaction observed line/byte bound exceeded')
    prefix=lambda b:re.match(rb'\[\d+\]',b).group() if re.match(rb'\[\d+\]',b) else b''
    if prefix(before)!=prefix(value) or value.count(b'[')!=before.count(b'[') or value.count(b']')!=before.count(b']'):
        raise ValueError('Bar numeric prefix changed')
    from translation_policy import validate
    from weapon_terms import validate as weapons
    issues=validate(before.decode().replace('|',' '),text.replace('|',' '))+weapons(before.decode(),text)
    if issues:raise ValueError('; '.join(issues))
    return value

def compile_interactions(elf,config):
    raw=original(RESOURCE)
    if sha(elf)!=ORIGINAL_SHA or config.get('policy')!=POLICY or config.get('source_sha256')!=sha(raw) or config.get('instruction_windows')!=bindings(elf):
        raise ValueError('Interaction source/reader binding differs')
    if execute_sda_pointer(elf,raw,6)!=0x11c800 or execute_sda_pointer(elf,raw[0x11c800:],0)!=0x20:
        raise ValueError('Bar SDA selectors differ')
    if execute_sda_pointer(elf,raw[0x800:],4)!=REACTION_BASE-0x800:raise ValueError('Reaction SDA selector differs')
    patches=[];results=[];counts={}
    for kind in ('reaction','bar'):
        table=catalog(raw,kind);cfg=config[kind]
        if cfg['table_sha256']!=table['sha256']:raise ValueError('Interaction table binding differs')
        byid={r['id']:r for r in table['rows']};targets={}
        for entry in cfg['entries']:
            if set(entry)!={'id','source_sha256','translation'}:raise ValueError('Unknown interaction metadata')
            key=entry['id']
            if key not in byid or key in targets or entry['source_sha256']!=byid[key]['source_sha256']:raise ValueError('Interaction ID/hash mismatch')
            targets[key]=validate_value(byid[key],entry['translation'],table)
            results.append({'id':key,'kind':kind,'source_bytes':len(bytes.fromhex(byid[key]['source_hex'])),'target_bytes':len(targets[key])})
        output,used=rebuild(raw,table,targets);base,size=table['base'],table['size'];roundtrip_raw=bytearray(raw);roundtrip_raw[base:base+size]=output
        decoded=catalog(roundtrip_raw,kind)
        # Compare logical references, not relocated offset-derived reaction IDs.
        logical={tuple(r['references']):bytes.fromhex(r['source_hex']) for r in decoded['rows']}
        for row in table['rows']:
            if logical.get(tuple(row['references']))!=targets.get(row['id'],bytes.fromhex(row['source_hex'])):raise ValueError('Interaction alias/readback mismatch')
        if kind=='reaction':
            if output[:4]!=raw[base:base+4]:raise ValueError('Reaction count modified')
            for i in range(REACTION_COUNT):
                if output[4+i*16:8+i*16]!=raw[base+4+i*16:base+8+i*16]:raise ValueError('Reaction key modified')
                for variant in range(3):
                    at=execute_reaction(elf,output,i,variant)
                    if at!=struct.unpack_from('<I',output,8+i*16+variant*4)[0]:raise ValueError('Reaction original forwarding differs')
        else:
            for i in range(BAR_COUNT):
                if execute_bar(elf,output,i)!=struct.unpack_from('<I',output,4+i*4)[0]:raise ValueError('Bar original forwarding differs')
        patches.append({'id':f'spack.{kind}.pool','resource':RESOURCE,'offset':base,'before':raw[base:base+size],'after':output})
        counts[kind]={'accepted':len(targets),'unique_source_strings':len(table['rows']),'used_bytes':used,
            'text_limit':table['pool_end'],'extent_size':size,'opaque_tail_bytes':size-table['pool_end']}
    return patches,{'policy':POLICY,'accepted':len(results),'tables':counts,'results':results,'source_extents_and_alias_graph_preserved':True,
        'runtime_visual_status':'pending_user_verification','proof_scope':'Bound original lookup/forwarding instructions in synthetic RAM; no full reader, prefix parser, formatter or PS2 execution'}
