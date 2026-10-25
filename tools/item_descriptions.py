"""Bounded item description pool; immutable item names, stats and references."""
import json,re,struct,hashlib
from interface_resources import original
from glyph_spacing import ORIGINAL_SHA
from gfi import encode,decode
from reinsertion import ROOT
from spack_ui import execute_sda_pointer,execute_byte_length,_execute,_reader
RESOURCE='DATA/S/S_PACK.SDA'
POLICY='spack-item-description-original-slots-v001'
ITEM_BASE,ITEM_COUNT,STRIDE=0x820,1349,128
POOL,SIZE=0x2aaa0,0x4ec0
WINDOWS=((0x6cda0,0x6cdb0),(0x70a68,0x70b9c),(0x118cb4,0x118cd4),
         (0x2266cc,0x2266d8),(0x2267f0,0x226810))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bindings(elf):return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]

def catalog(raw):
    groups={}
    for index in range(ITEM_COUNT):
        at=ITEM_BASE+index*STRIDE;record=raw[at:at+STRIDE]
        offset=struct.unpack_from('<I',record,24)[0]
        if offset==0xffffffff:continue
        if not 0<=offset<SIZE:raise ValueError('Item description reference outside pool')
        name=record[:24].split(b'\0')[0]
        groups.setdefault(offset,[]).append({'id':index,'name_sha256':sha(name),'record_sha256':sha(record)})
    result=[]
    for offset,items in sorted(groups.items()):
        end=raw.find(b'\0',POOL+offset,POOL+SIZE)
        if end<0:raise ValueError('Unterminated item description')
        value=raw[POOL+offset:end]
        result.append({'id':f'item.description.{offset:05x}','offset':POOL+offset,'source_hex':value.hex(),
            'source_sha256':sha(value),'items':items,'native':any(c<32 or c>126 for c in value)})
    for a,b in zip(result,result[1:]):
        if a['offset']+len(bytes.fromhex(a['source_hex']))>=b['offset']:raise ValueError('Interior description alias needs separate policy')
    if len(result)!=567:raise ValueError('Item description topology changed')
    return result

def validate_value(before,text):
    value=encode(text)
    if not value or len(value)>len(before) or any(c in value for c in (0,9,10,13,37)):
        raise ValueError('Description slot/control budget exceeded')
    if any(c<32 or c>126 for c in before) or b'%' in before:raise ValueError('Native/variable description blocked')
    if decode(value)!=text:raise ValueError('Description Unicode round-trip failed')
    source=before.decode('ascii')
    if source.count('|')!=text.count('|'):raise ValueError('Description line count changed')
    if max(map(len,text.split('|')))>max(map(len,source.split('|'))):raise ValueError('Description column guard exceeded')
    if re.findall(rb'\d+',before)!=re.findall(rb'\d+',value):raise ValueError('Description numeric facts changed')
    from translation_policy import validate
    from weapon_terms import validate as weapons
    issues=validate(source.replace('|',' '),text.replace('|',' '))+weapons(source,text)
    if issues:raise ValueError('; '.join(issues))
    return value

def validate_names(source,target):
    """Explicit unique references for the broader component/memo lot; opt-in."""
    from translation_policy import occurrences
    names=('Defending Blade','Twin Fang','Jamadhar','Stirm Pistol','G3A3','Cement Gun',
        'Firebreather','USP','Magnum','Ingram','Drill Claw','Evil Sword','Evil Toy Sword',
        'Deathbringer','165mm Ghost','205mm Crimson','Crimson Vulcan','Priceless Map',
        'Legendary Map','Beam Claw','Bomb Claw','Spiked Fender','Iron Claw','Pilebunker',
        'Moocher','C Unit','Max Load')
    source=source.replace('|',' ');target=target.replace('|',' ')
    for name in names:
        if occurrences(source,name,True)>occurrences(target,name,True):raise ValueError('Unique item reference missing: '+name)

def compile_descriptions(elf,config):
    from description_pool import POLICY as REPACK_POLICY
    if config.get('policy')==REPACK_POLICY:
        from description_pool import compile_pool
        return compile_pool(elf,config)
    if sha(elf)!=ORIGINAL_SHA or config.get('policy')!=POLICY or config.get('instruction_windows')!=bindings(elf):
        raise ValueError('Item reader/source policy mismatch')
    if config.get('name_reference_policy') not in (None,'item-description-unique-name-references-v002'):
        raise ValueError('Unknown item name policy')
    raw=original(RESOURCE)
    if sha(raw)!=config['source_sha256'] or sha(raw[POOL:POOL+SIZE])!=config['pool_sha256']:
        raise ValueError('Item pool source mismatch')
    if execute_sda_pointer(elf,raw,0)!=0x800 or execute_sda_pointer(elf,raw[0x800:],0)!=0x20 or execute_sda_pointer(elf,raw[0x800:],1)!=POOL-0x800:
        raise ValueError('Item SDA source boundaries mismatch')
    rows={r['id']:r for r in catalog(raw)};seen=set();patches=[];results=[]
    for target in config['entries']:
        key=target['id']
        if key not in rows or key in seen:raise ValueError('Unknown/duplicate item description ID')
        seen.add(key);row=rows[key];before=bytes.fromhex(row['source_hex'])
        if target['source_sha256']!=row['source_sha256'] or target['item_records']!=row['items']:
            raise ValueError('Description source/item alias binding changed')
        after=validate_value(before,target['translation'])
        if config.get('name_reference_policy'):
            validate_names(before.decode('ascii'),target['translation'])
        if after==before:raise ValueError('Unchanged description must be omitted')
        patches.append({'id':key,'resource':RESOURCE,'offset':row['offset'],'before':before+b'\0',
            'after':after+bytes(len(before)+1-len(after))})
        results.append({'id':key,'offset':row['offset'],'source_bytes':len(before),'target_bytes':len(after),
            'item_ids':[e['id'] for e in row['items']]})
    return patches,{'policy':POLICY,'accepted':len(results),'item_occurrences':sum(len(r['item_ids']) for r in results),
        'catalog_unique_descriptions':len(rows),'names_and_item_records_unchanged':True,
        'pool_offsets_unchanged':True,'instruction_windows':bindings(elf),'results':results,
        'runtime_visual_status':'pending_user_verification'}

def execute_description_pointer(elf,pool,relative):
    """Original status-menu pointer forwarding, stopping at the text consumer."""
    if not 0<=relative<len(pool):raise ValueError('Description probe outside pool')
    regs=[0]*32;regs[3]=0x470000;regs[2]=0x620000;regs[6]=relative
    reader=_reader([(0x475aec,struct.pack('<I',0x600000)),(0x620004,struct.pack('<I',0x630000)),(0x600000,pool)])
    result=_execute(elf,0x118cc4,((0x118cc4,0x118cd4),),regs,reader,0x10e608)
    return result[5]-0x600000
