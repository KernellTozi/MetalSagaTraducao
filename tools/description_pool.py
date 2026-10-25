"""Opt-in item description repack inside the original loaded pool.

Only item record +24 offsets may change. All logical aliases, earlier Unicode
translations, native/control strings and the original SDA extents are retained.
"""
import json,re,struct
from item_descriptions import (RESOURCE,POOL,SIZE,ITEM_BASE,ITEM_COUNT,STRIDE,
    catalog,original,sha,validate_value as validate_fixed,validate_names)
from glyph_spacing import ORIGINAL_SHA
from reinsertion import ROOT
from gfi import encode,decode
from spack_ui import execute_sda_pointer,_reader
from spack_battle import _run

POLICY='spack-item-description-original-pool-repack-v002'
READS=(0x4a85c,0x4ef44,0xe1c3c,0xe1f8c,0x118cc4,0x11de8c,
       0x123430,0x1ce180,0x1d4bdc,0x1d922c,0x1dad64,0x1db1c0,
       0x1e126c,0x1eac88,0x1ec038,0x1f5080,0x1f50ac)
WINDOWS=((0x6cda0,0x6cdb0),(0x70a98,0x70b9c),(0x6d938,0x6d950),
         (0x1b1890,0x1b19e0),(0x10e608,0x10e7a0),
         (0x2266cc,0x2266d8),(0x2267f0,0x226810)) + tuple((p-12,p+28) for p in READS)


def bindings(elf):
    return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]


def parent_config(config):
    binding=config['fixed_slot_parent'];path=(ROOT/binding['recipe']).absolute()
    if (not path.is_relative_to(ROOT/'translations') or path.suffix!='.json'
        or path.is_symlink() or path.resolve()!=path):
        raise ValueError('Description parent must be an ordinary translations recipe')
    data=path.read_bytes()
    if sha(data)!=binding['sha256']:raise ValueError('Description parent recipe hash differs')
    document=json.loads(data);parent=document['item_descriptions']
    from item_descriptions import POLICY as FIXED_POLICY
    if parent['policy']!=FIXED_POLICY:raise ValueError('Expected immutable fixed-slot parent')
    pending={r['id'] for r in document['description_review']['pending']}
    if not set(config['resumed_ids'])<=pending:raise ValueError('Only explicitly deferred space descriptions may resume')
    for key,value in parent.items():
        if key not in ('policy','entries') and config.get(key)!=value:
            raise ValueError('Historical description source/name binding changed')
    return parent


def topology(raw):
    rows=catalog(raw);cursor=0
    for row in rows:
        value=bytes.fromhex(row['source_hex'])
        if row['offset']!=POOL+cursor:raise ValueError('Description pool contains a gap/interior alias')
        cursor+=len(value)+1
    if cursor!=20155 or any(raw[POOL+cursor:POOL+SIZE]):raise ValueError('Unexpected description pool tail')
    return rows


def proof(elf,raw,config):
    if sha(elf)!=ORIGINAL_SHA or config.get('pool_repack_windows')!=bindings(elf):
        raise ValueError('Description pool reader evidence differs')
    if (execute_sda_pointer(elf,raw,0)!=0x800
        or execute_sda_pointer(elf,raw[0x800:],0)!=ITEM_BASE-0x800
        or execute_sda_pointer(elf,raw[0x800:],1)!=POOL-0x800
        or execute_sda_pointer(elf,raw[0x800:],2)!=POOL+SIZE-0x800):
        raise ValueError('Description SDA load boundary differs')
    reads=tuple(p for p in range(0x1000,0x25b108,4)
        if struct.unpack_from('<I',elf,p)[0]>>26==35
        and struct.unpack_from('<I',elf,p)[0]&65535==0x5aec)
    if reads!=READS:raise ValueError('Description pointer read census changed')
    rows=topology(raw)
    return {'instruction_windows':bindings(elf),'pool_size':SIZE,
        'source_used_bytes':20155,'source_zero_tail_bytes':5,
        'global_pointer_va':0x475aec,'bounded_lw_immediate_census':list(READS),
        'unique_descriptions':len(rows),'item_references':sum(len(r['items']) for r in rows),
        'maximum_original_bytes':59,'maximum_original_columns':29,
        'proof_scope':'17 bound forwarding paths; original integer instructions with synthetic RAM. No exhaustive indirect-alias proof, formatter, allocation, rendering or PS2 execution.'}


def validate_value(before,text):
    value=encode(text)
    if (not before or any(c<32 or c>126 for c in before) or b'%' in before
        or not value or any(c in value for c in (0,9,10,13,37)) or decode(value)!=text):
        raise ValueError('Description native/control/glyph blocked')
    source=before.decode('ascii')
    if (len(value)>59 or source.count('|')!=text.count('|')
        or max(map(len,text.split('|')))>29 or any(not line for line in text.split('|'))):
        raise ValueError('Description observed byte/line bounds exceeded')
    if re.findall(r'\d+',source)!=re.findall(r'\d+',text):raise ValueError('Description numeric facts changed')
    from translation_policy import validate
    from weapon_terms import validate as weapons
    issues=validate(source.replace('|',' '),text.replace('|',' '))+weapons(source,text)
    if issues:raise ValueError('; '.join(issues))
    validate_names(source,text)
    return value


def rebuild(raw,rows,targets):
    result=bytearray(SIZE);cursor=0;offsets={}
    for row in rows:
        value=targets.get(row['id'],bytes.fromhex(row['source_hex']))
        if cursor+len(value)+1>SIZE:raise ValueError('Description pool exceeds original loaded extent')
        offsets[row['id']]=cursor
        result[cursor:cursor+len(value)]=value;cursor+=len(value)+1
    return bytes(result),offsets,cursor


def execute_forwarding(elf,record,site):
    """Actual integer forwarding up to the original called text/format routine."""
    rel=struct.unpack_from('<I',record,24)[0]
    if rel==0xffffffff or rel>=SIZE:raise ValueError('Invalid description probe offset')
    regs=[0]*32;regs[29]=0x640000
    obj=bytearray(0x400)
    for field in (4,0x1c,0x2c,0xc4,0x1b8,0x1c4):struct.pack_into('<I',obj,field,0x630000)
    struct.pack_into('<I',obj,24,0x620000)
    blocks=[(0x475aec,struct.pack('<I',0x600000)),(0x620000,record),(0x630000,bytes(obj))]
    start=site;end=site+28;stop=0x1b1890;target=5
    if site==0x4a85c:regs[3]=0x470000;regs[16]=0x620000;regs[18]=0x630000
    elif site==0x4ef44:regs[2]=0x470000;regs[3]=rel;regs[4]=0x630000
    elif site in (0xe1c3c,0xe1f8c):
        regs[3]=0x470000;regs[7]=rel;stop=0x227a28;target=6
    elif site in (0x118cc4,0x11de8c,0x123430):
        regs[3]=0x470000;regs[6]=rel;regs[2]=0x630000;stop=0x10e608
    elif site==0x1ce180:regs[2]=0x470000;regs[3]=rel
    elif site in (0x1d4bdc,0x1d922c,0x1e126c,0x1eac88,0x1f5080):
        regs[2]=0x470000;regs[3]=0x620000;regs[16]=regs[17]=0x630000
    elif site in (0x1dad64,0x1db1c0,0x1f50ac):
        regs[3]=0x470000;regs[6]=rel;regs[16]=0x630000
    elif site==0x1ec038:regs[2]=0x470000;regs[6]=0x620000
    else:raise ValueError('Unknown description forwarding site')
    out=_run(elf,start,end,regs,_reader(blocks),stop)
    return out[target]-0x600000


def compile_pool(elf,config):
    raw=original(RESOURCE)
    if (config.get('policy')!=POLICY or config.get('source_sha256')!=sha(raw)
        or config.get('pool_sha256')!=sha(raw[POOL:POOL+SIZE])):
        raise ValueError('Description repack source/policy differs')
    evidence=proof(elf,raw,config);rows=topology(raw);byid={r['id']:r for r in rows}
    percent=None
    if config.get('literal_percent'):
        from description_percent import proof as percent_proof
        percent=percent_proof(elf,raw,config['literal_percent'])
    parent=parent_config(config);old={r['id']:r for r in parent['entries']}
    resumed=config['resumed_ids']
    if len(resumed)!=len(set(resumed)) or set(resumed)&old.keys():raise ValueError('Invalid explicit description resumption')
    targets={};results=[]
    for entry in config['entries']:
        key=entry['id']
        if key not in byid or key in targets:raise ValueError('Unknown/duplicate description ID')
        row=byid[key];before=bytes.fromhex(row['source_hex'])
        if entry['source_sha256']!=row['source_sha256'] or entry['item_records']!=row['items']:
            raise ValueError('Description source/alias binding differs')
        if key in old:
            if entry!=old[key]:raise ValueError('Earlier description translation changed')
            value=validate_fixed(before,entry['translation']);validate_names(before.decode(),entry['translation'])
        elif key in resumed:
            if percent and key==config['literal_percent']['id']:
                from description_percent import validate_value as percent_value
                value=percent_value(before,entry['translation'])
            else:value=validate_value(before,entry['translation'])
        else:raise ValueError('Description added without explicit resumption')
        if value==before:raise ValueError('Unchanged description counted as translation')
        targets[key]=value
        results.append({'id':key,'source_bytes':len(before),'target_bytes':len(value),
            'item_ids':[i['id'] for i in row['items']]})
    if set(targets)!=set(old)|set(resumed):raise ValueError('Description parent or resumed entry missing')
    if percent and config['literal_percent']['id'] not in targets:
        raise ValueError('Literal percent evidence requires its explicit translation')
    # Pure original reconstruction must be byte-identical, before any translation.
    if rebuild(raw,rows,{})[0]!=raw[POOL:POOL+SIZE]:raise ValueError('Description original round-trip differs')
    after,offsets,used=rebuild(raw,rows,targets)
    patches=[{'id':'spack.item.description.pool','resource':RESOURCE,'offset':POOL,
        'before':raw[POOL:POOL+SIZE],'after':after}]
    source_items=raw[ITEM_BASE:ITEM_BASE+ITEM_COUNT*STRIDE];items=bytearray(source_items)
    for row in rows:
        for item in row['items']:
            at=ITEM_BASE+item['id']*STRIDE+24
            oldref=raw[at:at+4];newref=struct.pack('<I',offsets[row['id']])
            struct.pack_into('<I',items,item['id']*STRIDE+24,offsets[row['id']])
            if oldref!=newref:patches.append({'id':f'item.description-ref.{item["id"]:04d}',
                'resource':RESOURCE,'offset':at,'before':oldref,'after':newref})
            found=after[offsets[row['id']]:].split(b'\0',1)[0]
            if found!=targets.get(row['id'],bytes.fromhex(row['source_hex'])):raise ValueError('Description alias readback differs')
    # Names, gameplay attributes and absent-description sentinels are immutable.
    for index in range(ITEM_COUNT):
        before=source_items[index*STRIDE:(index+1)*STRIDE];record=bytes(items[index*STRIDE:(index+1)*STRIDE])
        if record[:24]!=before[:24] or record[28:]!=before[28:]:raise ValueError('Item data changed outside description pointer')
        rel=struct.unpack_from('<I',record,24)[0]
        if struct.unpack_from('<I',before,24)[0]==0xffffffff:
            if record!=before:raise ValueError('Absent description sentinel changed')
            continue
        for site in READS:
            if execute_forwarding(elf,record,site)!=rel:raise ValueError('Original description forwarding differs')
    return patches,{'policy':POLICY,'accepted':len(targets),'new_descriptions':len(resumed),
        'item_occurrences':sum(len(byid[k]['items']) for k in targets),
        'catalog_unique_descriptions':len(rows),'used_bytes':used,'free_bytes':SIZE-used,
        'description_pointer_patches':len(patches)-1,'names_and_gameplay_attributes_unchanged':True,
        'logical_aliases_preserved':True,'pool_extent_unchanged':True,
        'original_roundtrip':True,'forwarding_cases':927*len(READS),'evidence':evidence,
        'results':results,**({'literal_percent':percent} if percent else {}),
        'runtime_visual_status':'pending_user_verification'}
