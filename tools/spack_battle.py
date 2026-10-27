"""Opt-in battle text; attributes and protected identities stay intact."""
import hashlib,json,re,struct
from pathlib import Path
from item_descriptions import original,RESOURCE
from item_names import catalog as item_catalog
from glyph_spacing import ORIGINAL_SHA
from gfi import encode,decode
from spack_ui import execute_sda_pointer,_reader
from reinsertion import ROOT

POLICY='spack-battle-labels-and-analysis-hints-fixed-fields-v001'
ACTION_BASE,ACTION_STRIDE,ACTION_COUNT=0x37070,228,967
ENEMY_BASE,ENEMY_STRIDE,ENEMY_COUNT=0x6cdb0,276,261
WINDOWS=((0x6ce04,0x6ce70),(0x11d358,0x11d380),(0x12b45c,0x12b488),
         (0x12b4bc,0x12b4d4),(0x12b594,0x12b5a4),(0x12b648,0x12b664),(0x1977c8,0x197910))
# Editorial opt-in: descriptive creatures/roles only. Bosses, wanted names,
# characters, branded/punned identities and every ID outside this set stay locked.
GENERIC_ENEMY_IDS=frozenset((1,2,3,4,5,7,10,11,15,16,22,23,24,25,26,31,35,36,37,38,42,43,44,
    45,47,48,49,50,51,54,59,65,73,74,76,77,80,81,85,87,90,91,92,95,103,104,108,109,
    115,116,117,119,120,122,125,129,132,136,138,139,141,143,150,155,156,157,158,160,
    252,253,254,255,256))

def sha(data):return hashlib.sha256(data).hexdigest()
def bindings(elf):return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]

def catalog(raw):
    if raw[0x35000:0x35004]!=b'sda\0':raise ValueError('Battle SDA missing')
    offsets=struct.unpack_from('<22I',raw,0x3500c)
    if tuple(0x35000+v for v in offsets[:4])!=(0x35070,ACTION_BASE,ENEMY_BASE,0x7e720):
        raise ValueError('Battle SDA bounds differ')
    if (raw[ACTION_BASE+ACTION_COUNT*ACTION_STRIDE:ENEMY_BASE]!=bytes(4) or
        raw[ENEMY_BASE+ENEMY_COUNT*ENEMY_STRIDE:0x7e720]!=bytes.fromhex('000000000100000000007041')):
        raise ValueError('Unexpected battle record tail')
    result=[]
    for kind,base,stride,count,field,size in (('action',ACTION_BASE,ACTION_STRIDE,ACTION_COUNT,0,32),
                                              ('hint',ENEMY_BASE,ENEMY_STRIDE,ENEMY_COUNT,232,44),
                                              ('enemy_name',ENEMY_BASE,ENEMY_STRIDE,ENEMY_COUNT,0,24)):
        for i in range(count):
            start=base+i*stride;at=start+field;slot=raw[at:at+size];end=slot.find(b'\0')
            if end<0 or any(slot[end:]):raise ValueError('Unterminated/nonzero battle field padding')
            value=slot[:end]
            result.append({'id':f'battle.{kind}.{i:04d}','kind':kind,'index':i,'offset':at,
                'record_offset':start,'record_sha256':sha(raw[start:start+stride]),
                'source_sha256':sha(value),'source_hex':value.hex(),'source_bytes':len(value),
                'field_bytes':size,'native':any(c<32 or c>126 for c in value),'empty':not value})
    return result

def _run(elf,start,end,regs,read,stop):
    """Only bound integer windows; R5900 MULT rd,rs,rt writes low 32 bits to rd.

    No DSP aliases, formatter, allocator, renderer or complete PS2 execution.
    """
    pc=start;pending=None
    for _ in range(100):
        if pc==stop:return regs
        if not start<=pc<end:raise ValueError('Battle probe escaped verified window')
        w=struct.unpack_from('<I',elf,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;fn=w&63
        n=w&65535;n=n if n<32768 else n-65536;old=pending;pending=None
        if op==0:
            if fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            elif fn==37:regs[rd]=regs[rs]|regs[rt]
            elif fn==24:regs[rd]=(regs[rs]*regs[rt])&0xffffffff
            elif fn==0:regs[rd]=regs[rt]<<((w>>6)&31)
            else:raise ValueError('Unsupported battle probe integer instruction')
        elif op==9:regs[rt]=regs[rs]+n
        elif op==15:regs[rt]=(w&65535)<<16
        elif op==35:regs[rt]=read((regs[rs]+n)&0xffffffff,4)
        elif op in (30,55):regs[rt]=read((regs[rs]+n)&0xffffffff,16 if op==30 else 8)&0xffffffff
        elif op==4:pending=pc+4+n*4 if regs[rs]==regs[rt] else pc+8
        elif op==3:regs[31]=pc+8;pending=((w&0x3ffffff)<<2)-0xff000
        else:raise ValueError('Unsupported battle probe opcode')
        regs=[v&0xffffffff for v in regs];regs[0]=0;pc=old if old is not None else pc+4
    raise ValueError('Battle probe step limit')

def execute_action(elf,index):
    if not 0<=index<ACTION_COUNT:raise ValueError('Action index outside source table')
    regs=[0]*32;regs[18]=0x620000;regs[29]=0x640000
    read=_reader([(0x620000,struct.pack('<I',index)),(0x475b10,struct.pack('<I',0x600000))])
    out=_run(elf,0x11d358,0x11d380,regs,read,0x227a28)
    if out[5]!=0x4485d0:raise ValueError('Action formatter is not the bound %s literal')
    return out[6]-0x600000

def execute_enemy(elf,index):
    if not 0<=index<ENEMY_COUNT:raise ValueError('Enemy index outside source table')
    regs=[0]*32;regs[23]=index
    out=_run(elf,0x12b45c,0x12b488,regs,_reader([(0x475b08,struct.pack('<I',0x600000))]),0x12b488)
    return out[20]-0x600000

def execute_hint(elf,index):
    regs=[0]*32;regs[20]=0x600000+execute_enemy(elf,index);regs[17]=0x620000
    read=_reader([(0x6201f0,struct.pack('<I',0x630000)),(0x630008,struct.pack('<I',0x640000))])
    out=_run(elf,0x12b648,0x12b664,regs,read,0x10e608)
    return out[6]-0x600000

def execute_enemy_name(elf,index):
    regs=[0]*32;regs[20]=0x600000+execute_enemy(elf,index);regs[17]=0x620000
    read=_reader([(0x6201ec,struct.pack('<I',0x630000)),(0x630004,struct.pack('<I',0x640000))])
    out=_run(elf,0x12b594,0x12b5a4,regs,read,0x10e608)
    return out[5]-0x600000

def verify(elf,raw,config):
    from item_name_user_review import BATTLE_POLICY
    if sha(elf)!=ORIGINAL_SHA or config.get('policy') not in (POLICY,BATTLE_POLICY) or config.get('instruction_windows')!=bindings(elf):
        raise ValueError('Battle reader/profile evidence differs')
    if config.get('source_sha256')!=sha(raw) or elf[0x3495d0:0x3495d3]!=b'%s\0' or elf[0x349870:0x349878]!=b'INFO\n%s\0':
        raise ValueError('Battle source or formatter binding differs')
    if execute_sda_pointer(elf,raw[0x35000:],1)!=ACTION_BASE-0x35000 or execute_sda_pointer(elf,raw[0x35000:],2)!=ENEMY_BASE-0x35000:
        raise ValueError('Battle SDA selector differs')

def validate_value(row,text,*,reviewed_remote=False):
    before=bytes.fromhex(row['source_hex'])
    if row['native'] or row['empty'] or '%' in before.decode('ascii',errors='replace'):raise ValueError('Native/empty/variable battle field blocked')
    value=encode(text)
    if (not value or value==before or value!=value.strip() or any(c in value for c in (0,9,10,13,37))
        or decode(value)!=text):raise ValueError('Invalid battle field/control/glyph')
    if row['kind']=='action':
        if len(value)>18 or '|' in text:raise ValueError('Action exceeds observed 18-byte bound')
    elif row['kind']=='enemy_name':
        if row['index'] not in GENERIC_ENEMY_IDS or len(value)>16 or '|' in text:
            raise ValueError('Protected enemy identity or observed 16-byte bound')
        for term in ('BB','AT','Gamma','Blocko','T1','Nitro','Gatling'):
            if term in before.decode('ascii').split() and term not in text.split():raise ValueError('Enemy identifier lost: '+term)
    elif len(value)>43 or len(text.split('|'))>2 or max(map(len,text.split('|')))>19:
        raise ValueError('Hint exceeds fixed field/two-line observed column guard')
    if re.findall(rb'\d+',before)!=re.findall(rb'\d+',value):raise ValueError('Battle numeric facts changed')
    from translation_policy import validate
    from weapon_terms import validate as weapons
    issues=validate(before.decode('ascii').replace('|',' '),text.replace('|',' '))+weapons(before.decode('ascii'),text)
    if reviewed_remote:
        from item_name_user_review import remote_action_exception
        if not remote_action_exception(row,text):raise ValueError('Unreviewed Remote action exception')
        issues=[issue for issue in issues if issue!='Termo/nome protegido ausente: Remote']
    if issues:raise ValueError('; '.join(issues))
    return value

def compile_battle(elf,config,item_config):
    raw=original(RESOURCE);verify(elf,raw,config);rows=catalog(raw);byid={r['id']:r for r in rows}
    from item_names import compile_names
    compile_names(elf,item_config)
    if max(r['source_bytes'] for r in rows if r['kind']=='action')!=18:
        raise ValueError('Observed action label ceiling differs')
    if max(r['source_bytes'] for r in rows if r['kind']=='enemy_name')!=16:
        raise ValueError('Observed enemy name ceiling differs')
    items=item_catalog(raw);targets={r['id']:r['translation'] for r in item_config['entries']};approved={};all_names=set()
    from item_name_user_review import BATTLE_POLICY,REMOTE_ACTION,validate_battle_config
    human_aliases=[]
    if config['policy']==BATTLE_POLICY:human_aliases=validate_battle_config(config,item_config,items,rows)
    elif 'item_review' in config:raise ValueError('Legacy battle policy cannot consume human exceptions')
    from spack_satcom import parse_table
    wanted_names={r['fields']['name']['raw'].decode('ascii') for r in parse_table(raw,'wanted')}
    for row in items:
        if row['empty'] or row['native']:continue
        source=bytes.fromhex(row['source_hex']).decode('ascii');all_names.add(source)
        if row['id'] in targets:approved[source]=targets[row['id']]
    seen={};patches=[];results=[]
    for target in config['entries']:
        if set(target)!={'id','source_sha256','record_sha256','translation'}:raise ValueError('Unknown battle metadata')
        key=target['id']
        if key not in byid or key in seen:raise ValueError('Unknown/duplicate battle ID')
        row=byid[key];source=bytes.fromhex(row['source_hex']).decode('ascii',errors='replace');text=target['translation']
        if any(target[k]!=row[k] for k in ('source_sha256','record_sha256')):raise ValueError('Battle source/record binding differs')
        if row['kind']=='enemy_name' and source in wanted_names:raise ValueError('Wanted identity cannot be translated')
        if row['kind']=='action' and source in all_names:
            if source not in approved or text!=approved[source]:raise ValueError('Battle name must preserve protected names or match approved item wording')
        value=validate_value(row,text,reviewed_remote=bool(human_aliases and row['kind']=='action' and row['index'] in REMOTE_ACTION));size=row['field_bytes'];at=row['offset'];before=raw[at:at+size];after=value+bytes(size-len(value))
        pointer={'action':execute_action,'hint':execute_hint,'enemy_name':execute_enemy_name}[row['kind']](elf,row['index'])
        expected=row['index']*(ACTION_STRIDE if row['kind']=='action' else ENEMY_STRIDE)+(232 if row['kind']=='hint' else 0)
        if pointer!=expected:raise ValueError('Original battle pointer forwarding differs')
        seen[key]=value;patches.append({'id':key,'resource':RESOURCE,'offset':at,'before':before,'after':after})
        results.append({k:row[k] for k in ('id','kind','index','offset','source_bytes')}|{'target_bytes':len(value)})
    # Every repeated label within a table keeps the same wording, including untouched occurrences.
    for kind in ('action','hint','enemy_name'):
        aliases={}
        for row in rows:
            if row['kind']==kind:aliases.setdefault(row['source_hex'],set()).add(seen.get(row['id'],bytes.fromhex(row['source_hex'])))
        if any(len(v)>1 for v in aliases.values()):raise ValueError('Repeated battle label translated inconsistently')
    return patches,{'policy':config['policy'],'accepted':len(patches),'actions':sum(r['kind']=='action' for r in results),
        **({'reviewed_item_counterparts':human_aliases,'human_item_review':config['item_review']} if human_aliases else {}),
        'hints':sum(r['kind']=='hint' for r in results),'generic_enemy_names':sum(r['kind']=='enemy_name' for r in results),
        'source_action_records':ACTION_COUNT,'source_enemy_records':ENEMY_COUNT,
        'enemy_attributes_and_protected_names_unchanged':True,'instruction_windows':bindings(elf),'results':results,
        'runtime_visual_status':'pending_user_verification','proof_scope':'Original pointer and forwarding windows in synthetic RAM; no formatter, GPU or complete PS2 execution'}
