"""Fixed 32-byte default-model names in MCT root entry 2; no model expansion."""
import struct
from dialogue import sha
from gfi import encode,decode
from speaker_labels import ROLES
from glyph_spacing import ORIGINAL_SHA,DELTA

RESOURCE='DATA/MAP/MAP.MCT'
BASE=0x202b7000
COUNT=409
STRIDE=44
EXTRA={
 'Boy':'Menino','Mod Shop':'Oficina de tuning','Service Station':'Posto de serviço',
 'Shell Shop':'Loja de munição','Tank Wash ':'Lava-tanques ',
 'Memory Center':'Central de memória','Storage Room':'Depósito',
 'Employee':'Funcionário','Maid':'Empregada','Rail Maid':'Comissária',
 'Dancer':'Dançarina','Conductor':'Condutor','Rich Old Woman':'Idosa rica',
 'Rich Lady':'Senhora rica','Rich Girl':'Garota rica','Rich Mother':'Mãe rica',
 'Rich Dude':'Rapaz rico','Rich Guy':'Rapaz rico','Hostess':'Anfitriã',
 'Cowgirl':'Vaqueira','Craftsman':'Artesão','Craftswoman':'Artesã',
 'Waiter':'Garçom','Homeless Guy':'Sem-teto','Young Lady':'Jovem',
 'Hoodlum':'Arruaceiro','Hooligan':'Vândalo','Dead Guy':'Homem morto',
 'Muscle Man':'Musculoso','Muscle Woman':'Musculosa',
 'Muscle Guard':'Guarda musculoso','Masked Muscle':'Musculoso mascarado',
 'Marauder':'Saqueador','Mercenary':'Mercenário',
}
TARGETS=ROLES|EXTRA
WINDOWS=((0x328d0,0x32930),(0x3299c,0x32a28),(0x31e8c,0x31edc),
         (0x7d530,0x7d550),(0x23bfd0,0x23bffc),(0x1fdb00,0x1fdb68),
         (0x304f70,0x304f78))


def bindings(elf):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Default-name ELF differs')
    if struct.unpack_from('<II',elf,0x403f28-DELTA+0x48)!=(0,0x7d530+DELTA):
        raise ValueError('NPC default name virtual descriptor differs')
    return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]


def catalog(data):
    if bytes(data[:4])!=b'sda\0' or struct.unpack_from('<II',data,4)!=(len(data),5):
        raise ValueError('MCT root differs')
    bounds=struct.unpack_from('<5I',data,12)
    if bounds[2]!=BASE or bounds[3]!=0x26d25800 or struct.unpack_from('<I',data,BASE)[0]!=COUNT:
        raise ValueError('Default-model bank differs')
    rows=[]
    for i in range(COUNT):
        at=BASE+4+i*STRIDE;record=bytes(data[at:at+STRIDE]);field=record[12:44]
        zero=field.find(0)
        if zero<0 or any(field[zero:]):raise ValueError('Unproven default-name tail')
        rows.append({'id':f'map.model.name.{i:04d}','index':i,'offset':at+12,
                     'record_offset':at,'record_sha256':sha(record),
                     'field_sha256':sha(field),'field':field,'record':record,
                     'source':field[:zero].decode('ascii') if field[:zero].isascii() else None})
    if BASE+4+COUNT*STRIDE>BASE+struct.unpack_from('<I',data,BASE+4)[0]:
        raise ValueError('Name directory overlaps first model payload')
    return rows


def getter_probe(elf,record,explicit=None):
    """Original fallback getter + virtual NPC name getter, collection lookup stubbed."""
    bindings(elf)
    from name_source_paths import run
    dialog=bytearray(0x50);npc=bytearray(0x140);bridge=bytearray(0xd0);model=bytearray(0x480)
    stack=bytearray(0x300)
    struct.pack_into('<II',dialog,0x24,0x630000,7)
    struct.pack_into('<I',dialog,0x34,0x650000 if explicit is not None else 0)
    struct.pack_into('<I',npc,0x10,0x403f28);struct.pack_into('<I',npc,0x120,0x621000)
    struct.pack_into('<I',bridge,0xc8,0x622000);struct.pack_into('<I',model,0x470,0x640000)
    struct.pack_into('<Q',stack,0x100,0x7ff000)
    regions=[(0x600000,dialog,False),(0x620000,npc,False),(0x621000,bridge,False),
             (0x622000,model,False),(0x640000,record,False),(0x700000,stack,True),(DELTA,elf,False)]
    if explicit is not None:regions.append((0x650000,explicit+b'\0',False))
    calls=[]
    def handle(pc,regs,access):
        if pc==0x1c51f0+DELTA:
            if (regs[4],regs[5])!=(0x630000,7):raise ValueError('Actor collection arguments differ')
            calls.append('actor_collection_lookup');regs[2]=0x620000;return True
        return False
    regs=[0]*32;regs[4]=0x600000;regs[29]=0x700100;regs[31]=0x7ff000
    r=run(elf,0x1fdb00,((0x1fdb00,0x1fdb68),(0x7d530,0x7d550)),regs,regions,0x7ff000,handle)
    expected=0x650000 if explicit is not None else 0x64000c
    if r['registers'][2]!=expected or len(calls)!=(0 if explicit is not None else 1):
        raise ValueError('Original fallback getter returned another field')
    return {'returned_name_offset_in_record':None if explicit is not None else 12,
            'explicit_name_preserved':explicit is not None,'collection_lookup_stubbed':True,
            'original_virtual_getter_executed':True,'instructions':r['instructions'],
            'only_stack_writes':all(0x700000<=w['address']<0x700300 for w in r['writes'])}


def targets(data,elf):
    bindings(elf);rows=catalog(data);out=[]
    from translation_policy import validate
    for r in rows:
        source=r['source']
        if source not in TARGETS:continue
        text=TARGETS[source];value=encode(text)
        if value==r['field'].split(b'\0')[0]:continue
        if len(value)>31 or b'\0' in value or b'%' in value or decode(value)!=text:
            raise ValueError('Default name exceeds proven field/codec')
        if validate(source,text):raise ValueError('Default name terminology differs')
        out.append({k:r[k] for k in ('id','index','offset','record_offset','record_sha256','field_sha256')}|
                   {'translation':text,'target_bytes':len(value)})
    if sum(r['translation']=='Menino' for r in out)!=2:raise ValueError('Expected exactly two Boy fields')
    return out


def compile_names(data,elf,expected):
    if targets(data,elf)!=expected:raise ValueError('Default name manifest differs')
    rows={r['id']:r for r in catalog(data)};patches=[];results=[]
    for item in expected:
        row=rows[item['id']];encoded=encode(item['translation']);after=encoded+bytes(32-len(encoded))
        updated=row['record'][:12]+after
        proof=getter_probe(elf,updated)
        patches.append({'id':item['id'],'resource':RESOURCE,'offset':row['offset'],
                        'before':row['field'],'after':after})
        results.append({**item,'getter':proof})
    return patches,{'accepted':len(results),'source_model_records':COUNT,'results':results,
                    'model_attributes_offsets_ids_unchanged':True,
                    'explicit_dialogue_labels_unchanged':True,
                    'pcsx2_executed':False,'visual_status':'pending_user'}
