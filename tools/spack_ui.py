"""Opt-in same-extent S_PACK UI repack; original logical IDs and alias graph preserved."""
import hashlib,json,re,struct
from reinsertion import ROOT
from plan_interface_menus import counted_strings,TABLE_BASE,TABLE_SIZE,COUNT,RESOURCE
from interface_resources import original
from interface_text import controls,FORMAT,references,sections
from gfi import encode,decode
from glyph_spacing import ORIGINAL_SHA
POLICY='spack-ui-counted-alias-preserving-repack-v001'
STATUS_POLICY='character-status-single-multiline-v001'
# Hand-inspected load/root selection, UI selection, dynamic text buffer and pipe conversion.
WINDOWS=((0x6cb94,0x6cbe8),(0x6cc24,0x6ccc8),(0x6ce04,0x6ce1c),
 (0x3ed10,0x3ed70),(0x1e8d14,0x1e8d34),(0x3dbac,0x3dc78),(0x2266cc,0x2266d8),(0x2267f0,0x226810))
LOCKED={2,3,4,9,13,14,17,20,37,38,39,45,48,49,142,143,144,159,
 161,162,163,165,166,167,169,170,216,261,370,371,372,373,374,375,376,377}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def proof(elf,binding):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('S_PACK ELF mismatch')
    expected=[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]
    if binding!=expected:raise ValueError('S_PACK loader/consumer binding mismatch')
    reads=[]
    for at in range(0x1000,0x25b108,4):
        w=struct.unpack_from('<I',elf,at)[0]
        if w>>26!=35 or w&65535!=0x5b18:continue
        reads.append(at);reg=w>>16&31
        for pos in range(at+4,min(at+52,0x25b108),4):
            q=struct.unpack_from('<I',elf,pos)[0];op=q>>26;rs=q>>21&31;rt=q>>16&31
            if op==9 and rs==reg and 0x5ec<=q&65535<0x2000:raise ValueError('Potential direct UI pool offset needs investigation')
            if ((op in (9,13,15,35,32,36) and rt==reg) or (op==0 and q>>11&31==reg) or (op==3 and reg in (2,3))):break
    return {'instruction_windows':expected,'ui_global_pointer_va':0x475b18,
        'bounded_pointer_read_census':{'reads':len(reads),'following_instructions_max':12,
            'direct_pool_addiu_candidates':0,'completeness':'local instruction scan, not full alias/control-flow proof'},
        'load':'S_PACK root entry 1, then nested SDA entry 0',
        'lookup':'base + u32(base + 4 + 4*id)',
        'text_buffer':'Observed common text path allocates (byte_length+32)&~3 and converts pipe to LF',
        'limits':'Proof is scoped to inspected paths; not a full-game execution or all consumers'}


def rebuild(before,table,values):
    output=bytearray(len(before));struct.pack_into('<I',output,0,table['count']);cursor=table['header_size']
    for row in table['entries']:
        value=values.get(row['pointer_ids'][0],bytes.fromhex(row['source_hex']))
        if cursor+len(value)+1>len(output):raise ValueError('S_PACK UI table exceeds original 8192 bytes')
        for index in row['pointer_ids']:struct.pack_into('<I',output,4+index*4,cursor)
        output[cursor:cursor+len(value)]=value;cursor+=len(value)+1
    return bytes(output),cursor


def validate_value(row,text,policy):
    raw=bytes.fromhex(row['source_hex']);index=row['pointer_ids'][0]
    if index in LOCKED or row['source_ascii'] is None:raise ValueError('Protected/native/composed S_PACK entry')
    value=encode(text)
    if not value or any(c in value for c in (0,9,10,13)):raise ValueError('Injected S_PACK delimiter')
    if decode(value)!=text:raise ValueError('S_PACK glyph round-trip mismatch')
    if value==raw:raise ValueError('S_PACK entry is not a translation')
    if len(value)>max(31,len(raw)):raise ValueError('S_PACK entry growth guard exceeded')
    if controls(raw)!=controls(value):raise ValueError('S_PACK printf/pipe sequence changed')
    # Preserve the literal native prefix produced by printf, not just the %% token.
    if re.findall(rb'%%I%02d%s',raw)!=re.findall(rb'%%I%02d%s',value):raise ValueError('S_PACK inline item prefix changed')
    if re.findall(rb'\d+',FORMAT.sub(b'',raw))!=re.findall(rb'\d+',FORMAT.sub(b'',value)):raise ValueError('S_PACK numeric facts changed')
    if re.match(rb' *',raw).group()!=re.match(rb' *',value).group() or re.search(rb' *$',raw).group()!=re.search(rb' *$',value).group():raise ValueError('S_PACK concatenation spaces changed')
    from translation_policy import validate
    issues=validate(raw.decode('ascii').replace('|',' '),text.replace('|',' '),policy)
    from weapon_terms import validate as weapons
    issues+=weapons(raw.decode('ascii'),text)
    for term in ('MAIN','SUB'):
        if len(re.findall(r'\b'+term+r'\b',raw.decode('ascii'),re.I))>len(re.findall(r'\b'+term+r'\b',text)):
            issues.append('Tank category must remain '+term)
    if issues:raise ValueError(f'S_PACK {index}: '+ '; '.join(issues))
    return value


def compile_ui(elf,config):
    if config.get('policy')!=POLICY:raise ValueError('Unknown S_PACK UI policy')
    evidence=proof(elf,config['instruction_windows']);raw=original(RESOURCE)
    before=raw[TABLE_BASE:TABLE_BASE+TABLE_SIZE]
    if sha(raw)!=config['source_sha256'] or sha(before)!=config['table_sha256']:raise ValueError('S_PACK UI source mismatch')
    from probe_resources import nested
    node=next(n for n in nested(raw) if n['offset']==0x35000)
    if node['count']!=22 or node['offsets'][:2]!=[0x70,0x2070]:raise ValueError('S_PACK UI SDA boundary mismatch')
    table=counted_strings(raw,TABLE_BASE,TABLE_SIZE,COUNT);rows={r['pointer_ids'][0]:r for r in table['entries']}
    original_values={i:bytes.fromhex(r['source_hex']) for i,r in rows.items()}
    if rebuild(before,table,original_values)[0]!=before:raise ValueError('S_PACK original reverse round-trip mismatch')
    policy=json.loads((ROOT/'translations/politica.json').read_text(encoding='utf-8'));values={};result=[]
    for key,target in config['translations'].items():
        if not re.fullmatch(r'0|[1-9]\d*',key):raise ValueError('Noncanonical S_PACK ID')
        index=int(key)
        if index not in rows:raise ValueError('Use canonical ID for each shared string')
        row=rows[index]
        if target['source_sha256']!=row['source_sha256']:raise ValueError('S_PACK per-entry source mismatch')
        value=validate_value(row,target['translation'],policy);values[index]=value
        result.append({'id':row['id'],'pointer_ids':row['pointer_ids'],'old_offset':row['offset'],
            'source_length':row['source_length'],'target_length':len(value),'target_sha256':sha(value)})
    if not values:raise ValueError('Empty S_PACK translation batch')
    after,used=rebuild(before,table,values);parsed=counted_strings(after,0,TABLE_SIZE,COUNT)
    new_by_index={i:r for r in parsed['entries'] for i in r['pointer_ids']}
    for row in table['entries']:
        expected=values.get(row['pointer_ids'][0],bytes.fromhex(row['source_hex']))
        for index in row['pointer_ids']:
            found=new_by_index[index]
            if bytes.fromhex(found['source_hex'])!=expected or found['pointer_ids']!=row['pointer_ids']:raise ValueError('S_PACK readback/alias mismatch')
    for item in result:
        item['new_offset']=TABLE_BASE+new_by_index[item['pointer_ids'][0]]['offset']
    if len(after)!=len(before):raise ValueError('S_PACK size changed')
    return [{'resource':RESOURCE,'id':'spack.ui.table','offset':TABLE_BASE,'before':before,'after':after}],{
        'policy':POLICY,'accepted':len(values),'changed_pointer_occurrences':sum(len(rows[i]['pointer_ids']) for i in values),
        'total_unique_strings':len(rows),'preserved_unique_strings':len(rows)-len(values),
        'pointer_count':COUNT,'alias_references':COUNT-len(rows),'size':TABLE_SIZE,'used_bytes':used,
        'free_bytes':TABLE_SIZE-used,'offsets_changed_inside_table_only':True,'reverse_roundtrip':True,
        'source_sha256':sha(raw),'table_sha256':sha(after),'evidence':evidence,'results':result,
        'preserved_ids':[i for i in rows if i not in values],
        'growth_guard':'At most max(original byte length,31) per entry; conservative policy, not a universal runtime buffer bound',
        'runtime_visual_status':'pending_user_verification'}


def compile_status(elf,config):
    if config.get('policy')!=STATUS_POLICY or sha(elf)!=ORIGINAL_SHA:raise ValueError('Character status policy/source mismatch')
    a,z=0x118a20,0x118a8c;at=0x32b6a0;end=elf.find(b'\0',at);raw=elf[at:end]
    if config['consumer_sha256']!=sha(elf[a:z]) or config['source_sha256']!=sha(raw) or len(raw)!=51:raise ValueError('Character status binding mismatch')
    refs=references(elf,sections(elf));aliases=[i for i in range(1,len(raw)) if at+0xff000+i in refs]
    if aliases:raise ValueError('Character status interior aliases detected')
    after=encode(config['translation'])
    if not after or len(after)>len(raw) or b'\0' in after or controls(raw)!=controls(after):raise ValueError('Character status format/slot changed')
    if decode(after)!=config['translation']:raise ValueError('Character status encoding mismatch')
    return [{'resource':'SLUS_212.93','id':'elf.ui.0032b6a0','offset':at,'before':raw+b'\0','after':after+bytes(len(raw)+1-len(after))}],{
        'accepted':1,'policy':STATUS_POLICY,'offset':at,'consumer':[a,z],'source_length':len(raw),
        'target_length':len(after),'consumer_sha256':sha(elf[a:z]),'runtime_visual_status':'pending_user_verification'}


# Bounded original-instruction probes; no drawing, allocator or emulator is run.
def _execute(elf,start,windows,regs,read,stop):
    pc=start;pending=None
    for _ in range(10000):
        if pc==stop:return regs
        if not any(a<=pc<z for a,z in windows):raise ValueError(f'Probe escaped bound code: {pc:x}')
        w=struct.unpack_from('<I',elf,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;fn=w&63
        u=w&65535;n=u if u<32768 else u-65536;old=pending;pending=None;nextpc=pc+4
        if op==0:
            if fn==0:regs[rd]=regs[rt]<<((w>>6)&31)
            elif fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            elif fn==35:regs[rd]=regs[rs]-regs[rt]
            elif fn==37:regs[rd]=regs[rs]|regs[rt]
            elif fn==8:pending=regs[rs]
            else:raise ValueError('Unsupported probe integer opcode')
        elif op==9:regs[rt]=regs[rs]+n
        elif op==12:regs[rt]=regs[rs]&u
        elif op==15:regs[rt]=u<<16
        elif op in (32,35):
            value=read((regs[rs]+n)&0xffffffff,1 if op==32 else 4)
            regs[rt]=value-256 if op==32 and value>=128 else value
        elif op in (5,21):
            take=regs[rs]!=regs[rt]
            if op==21 and not take:nextpc=pc+8
            else:pending=pc+4+n*4 if take else pc+8
        elif op==3:regs[31]=pc+8;pending=((w&0x3ffffff)<<2)-0xff000
        else:raise ValueError('Unsupported probe opcode')
        regs=[r&0xffffffff for r in regs];regs[0]=0;pc=old if old is not None else nextpc
    raise ValueError('Probe step limit')


def _reader(regions):
    def read(at,size):
        for base,data in regions:
            if base<=at and at+size<=base+len(data):return int.from_bytes(data[at-base:at-base+size],'little')
        raise ValueError(f'Probe read outside supplied memory {at:x}')
    return read


def execute_sda_pointer(elf,record,index):
    regs=[0]*32;regs[4]=0x600000;regs[5]=index;regs[31]=0x700000
    result=_execute(elf,0x3ed10,((0x3ed10,0x3ed24),),regs,_reader([(0x600000,record)]),0x700000)
    return result[2]-0x600000


def execute_ui_pointer(elf,table,index):
    regs=[0]*32;regs[17]=index;regs[16]=0x620000
    read=_reader([(0x600000,table),(0x475b18,struct.pack('<I',0x600000)),(0x6201b4,struct.pack('<I',0x630000))])
    result=_execute(elf,0x1e8d14,((0x1e8d14,0x1e8d34),),regs,read,0x50cc0)
    return result[5]-0x600000


def execute_byte_length(elf,raw):
    regs=[0]*32;regs[4]=0x600001;regs[31]=0x700000
    result=_execute(elf,0x2266cc,((0x2266cc,0x2266d8),(0x2267f0,0x226810)),regs,_reader([(0x600001,raw+b'\0')]),0x700000)
    return result[2]
