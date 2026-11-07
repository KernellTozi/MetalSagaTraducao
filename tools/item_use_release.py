"""Source-bound v071: item-use message pool, help prompt and mountain labels."""
import copy,json,mmap,struct
from dialogue import ROOT,sha
from gfi import encode,decode
from interface_text import SOURCE as ELF,references,sections,FORMAT
from glyph_spacing import ORIGINAL_SHA,DELTA
from reinsertion import SOURCE as MAP
from tank_drinking_gaps import metadata

PARENT='translations/interface-v070.json';CHILD='translations/interface-v071.json'
MANIFEST='translations/uso-itens-v001.json'
POLICY='item-use-aligned-same-pool-and-mountain-labels-v001'
STATUS='Uso de itens, montanhas e pergunta da ajuda em português; visual pendente.'
START=0x31a600;END=0x31a830
OFFSETS=(0x31a600,0x31a618,0x31a628,0x31a648,0x31a660,0x31a678,0x31a698,
         0x31a6b0,0x31a6c8,0x31a6e0,0x31a700,0x31a710,0x31a730,0x31a750,
         0x31a768,0x31a780,0x31a7b0,0x31a7d8,0x31a800,0x31a818)
TARGETS={
 0x31a600:'%s recuperou\n%dHP',
 0x31a628:'Pelo de %s\nbrilha mais (+%d)',
 0x31a648:'%s se curou\ndo veneno',0x31a660:'%s se livrou\ndo atordoamento',
 0x31a678:'%s não\nreviveu',0x31a698:'%s voltou\nà vida',
 0x31a6b0:'Recuperou %dSP\nem %s',0x31a6c8:'Removeu %s\nde %s',
 0x31a6e0:'Ácido em %s\nneutralizado',0x31a700:'Reparo: %s\nVeículo: %s',
 0x31a710:'%s não pode\nvirar\n%s',0x31a730:'%s em %s\nvirou\n%s',
 0x31a768:'%s virou\n%s',
 0x31a800:'Todos recuperaram\n%dHP'}
PRESERVED={0x31a618:'Ineficaz',0x31a750:'Nada a converter...',
           0x31a780:'Modo vigia: mais ataques preventivos',
           0x31a7b0:'Modo ameaça: afasta inimigos fracos',
           0x31a7d8:'Modo evasão: menos encontros',0x31a818:'Ouviu um som'}
LOCATIONS={'Junk Mountain':'Montanha de Sucata','Monkey Mountain':'Monte Macaco'}
WINDOWS=((0x70c40,0x70eb0),(0x70f60,0x71060),(0x71060,0x716b0),
         (0x12c3ec,0x12c3f8))


def message_pool(elf,parents):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Item-use ELF revision differs')
    refs=references(elf,sections(elf));out=bytearray();rows=[];by={}
    targets=TARGETS|PRESERVED
    if set(targets)!=set(OFFSETS):raise ValueError('Item-use target census differs')
    parent_recipe=json.loads((ROOT/PARENT).read_bytes())
    entries={e['id']:e for e in parent_recipe['entries']}
    for at,text in PRESERVED.items():
        if entries[f'elf.ui.{at:08x}']['translation']!=text:raise ValueError('Existing mode message changed')
    for index,at in enumerate(OFFSETS):
        end=elf.index(b'\0',at);source=elf[at:end];target=encode(targets[at])
        next_at=OFFSETS[index+1] if index+1<len(OFFSETS) else END
        if end>=next_at or any(elf[end:next_at]):raise ValueError('Item message slot/source padding differs')
        if FORMAT.findall(source)!=FORMAT.findall(target) or source.count(b'\n')!=target.count(b'\n'):
            raise ValueError('Item message argument order or line controls changed')
        if decode(target)!=targets[at] or b'\0' in target:raise ValueError('Item message codec differs')
        if any(at+DELTA+i in refs for i in range(1,len(source)+1)):
            raise ValueError('Interior item message reference needs separate proof')
        # Fixed-copy paths must retain the old read span, alignment, early NUL.
        fixed=b'%' not in source
        if fixed and len(target)>len(source):raise ValueError('Fixed-copy item message would be truncated')
        while len(out)%8:out.append(0)
        pos=START+len(out);reserve=max(len(target)+1,len(source)+1 if fixed else 0)
        out.extend(target+bytes(reserve-len(target)));by[at]=pos+DELTA
        rows.append({'source_offset':at,'source_sha256':sha(source),'translation':targets[at],
                     'target_va':pos+DELTA,'target_bytes':len(target),'reserved_bytes':reserve,
                     'fixed_copy_read_bytes':len(source)+1 if fixed else None,
                     'printf_tokens':[s.decode() for s in FORMAT.findall(source)],
                     'new_translation':at in TARGETS})
    used=len(out)
    if used>END-START:raise ValueError('Item message pool overflow')
    out.extend(bytes(END-START-used))
    patches=[{'id':'item-use.message.pool','resource':'SLUS_212.93','offset':START,
              'before':elf[START:END],'after':bytes(out)}]
    absorbed=[p for p in parents if p['resource']=='SLUS_212.93' and
              max(START,p['offset'])<min(END,p['offset']+len(p['before']))]
    if {p['id'] for p in absorbed}!={f'elf.ui.{at:08x}' for at in PRESERVED}:
        raise ValueError('Unexpected inherited message patches')
    addresses={at+DELTA:[] for at in OFFSETS}
    for pos in range(0,len(elf)-3,4):
        address=struct.unpack_from('<I',elf,pos)[0]
        if address in addresses:addresses[address].append(pos)
    changes=[];seen=set()
    for at in OFFSETS:
        uses=refs.get(at+DELTA,[])
        if at==0x31a660:
            if uses:raise ValueError('Stun reference census changed')
            # Shared LUI in a branch delay slot; final ADDIU is in another block.
            if struct.unpack_from('<I',elf,0x70e44)[0]!=0x3c050042 or struct.unpack_from('<I',elf,0x70e70)[0]!=0x24a59660:
                raise ValueError('Shared stun format address differs')
            uses=[{'kind':'lui-immediate-candidate','offset':0x70e44,'immediate_offset':0x70e70}]
        if not uses or addresses[at+DELTA]:raise ValueError('Item message has missing or additional absolute references')
        for ref in uses:
            if ref['kind']!='lui-immediate-candidate':raise ValueError('Unproved item pointer consumer')
            hi=struct.unpack_from('<I',elf,ref['offset'])[0];pos=ref['immediate_offset'];lo=struct.unpack_from('<I',elf,pos)[0]
            target=by[at]
            if (hi>>26!=15 or lo>>26!=9 or lo>>21&31!=hi>>16&31
                or (target+0x8000)>>16!=hi&65535):raise ValueError('Item pointer instruction differs')
            oldlo=lo&65535;oldlo=oldlo if oldlo<32768 else oldlo-65536
            if ((hi&65535)<<16)+oldlo!=at+DELTA:raise ValueError('Original item pointer does not resolve')
            if pos in seen:raise ValueError('Duplicate item pointer patch')
            seen.add(pos);word=(lo&0xffff0000)|(target&65535)
            if word!=lo:patches.append({'id':f'item-use.pointer.{pos:08x}','resource':'SLUS_212.93','offset':pos,
                                       'before':elf[pos:pos+4],'after':struct.pack('<I',word)})
            changes.append({'source_offset':at,'high_offset':ref['offset'],'low_offset':pos,
                            'target_va':target,'changed':word!=lo})
    return patches,[p['id'] for p in absorbed],{'pool_start':START,'pool_bytes':END-START,
        'used_bytes':used,'messages':rows,'references':changes,'all_targets_8byte_aligned':True,
        'all_other_elf_data_unchanged':True}


def help_patch(elf):
    at=0x32d5e0;source=b'Select a category\0';target=encode('Qual categoria?')
    refs=references(elf,sections(elf))
    if elf[at:at+len(source)]!=source or elf[at-4:at]!=b'\xff'*4 or len(target)>=len(source):
        raise ValueError('Help prompt source/capacity differs')
    if not refs.get(at+DELTA) or any(at+DELTA+i in refs for i in range(1,len(source))):
        raise ValueError('Help prompt reference/alias differs')
    expected={0x12c3ec:0x3c050043,0x12c3f0:0x0c08aee0,0x12c3f4:0x24a5c5e0}
    for pos,word in expected.items():
        if struct.unpack_from('<I',elf,pos)[0]!=word:raise ValueError('Help prompt consumer differs')
    return {'id':'item-use.help.category','resource':'SLUS_212.93','offset':at,'before':source,
            'after':target+bytes(len(source)-len(target))}


def map_labels():
    from scene_name_fields import parse
    from build_translation_pilot import load_draft
    patches=[];rows=[]
    with MAP.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
        proof=parse(data)
        if (proof['map_count'],proof['name_fields'])!=(300,839):raise ValueError('Mountain scene census differs')
        for index in range(300):
            tree,size,blob,script=struct.unpack_from('<4I',data,0x830+16*index)
            for node in range(0x800+tree,0x800+tree+size,16):
                typ,children,identity,off,length=struct.unpack_from('<HHIII',data,node)
                if typ not in (2,7):continue
                pos=0x800+blob+off;field=bytes(data[pos:pos+32]);name=field.split(b'\0')[0].decode('ascii',errors='replace')
                if name not in LOCATIONS:continue
                target=encode(LOCATIONS[name]);span=max(len(name),len(target))+1
                if span>32 or any(field[len(name):]) or (typ==7 and length!=216):raise ValueError('Mountain name bounds differ')
                patches.append({'id':f'item-use.mountain.{pos:08x}','resource':'DATA/MAP/MAP.MCT','offset':pos,
                                'before':field[:span],'after':target+bytes(span-len(target))})
                rows.append({'map':index,'node_type':typ,'node_offset':node,'name_offset':pos,
                             'node_sha256':sha(data[node:node+16]),'translation':LOCATIONS[name]})
    if len(rows)!=5:raise ValueError('Mountain label occurrence count differs')
    draft,_=load_draft(ROOT/'translations/regiao-inicial-v048.json')
    if (draft['translations'].get('map.supr.1f3291d4')!='Montanha de Sucata' or
        draft['translations'].get('map.supr.0971eb74')!='- Monte Macaco -'):
        raise ValueError('Existing mountain entrance titles differ')
    return patches,rows


def derive(elf,parents):
    patches,absorbed,pool=message_pool(elf,parents)
    locations,evidence=map_labels();patches.extend([help_patch(elf)]+locations)
    occupied=[p for p in parents if p['id'] not in absorbed]
    for patch in patches:
        if any(patch['resource']==p['resource'] and max(patch['offset'],p['offset'])<min(patch['offset']+len(patch['before']),p['offset']+len(p['before'])) for p in occupied):
            raise ValueError('Item-use patch overlaps inherited data')
        occupied.append(patch)
    return patches,absorbed,{'messages':pool,'mountains':evidence,
        'existing_mountain_titles_preserved':True,'generic_you_used_message_preserved':'Usou %s!',
        'instruction_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]}


def validate(recipe):
    binding=recipe['item_use_release']
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:raise ValueError('Unknown item-use binding')
    raw=(ROOT/MANIFEST).read_bytes();m=json.loads(raw)
    if sha(raw)!=binding['sha256'] or m['policy']!=POLICY or m['parent_sha256']!=sha((ROOT/PARENT).read_bytes()):
        raise ValueError('Item-use manifest or parent differs')
    parent=json.loads((ROOT/PARENT).read_bytes());expected=copy.deepcopy(parent)
    expected.update(item_use_release=binding,iso_name='MetalSaga-ptbr-interface-v071.iso',status=STATUS)
    if recipe!=expected:raise ValueError('Unrelated item-use mutation')
    return parent,m


def compile_interface(elf,recipe):
    from interface_text import compile_draft
    parent,m=validate(recipe);parents,report=compile_draft(elf,parent)
    patches,absorbed,evidence=derive(elf,parents)
    if m['patches']!=[metadata(p) for p in patches] or m['absorbed']!=absorbed or m['evidence']!=evidence:
        raise ValueError('Item-use output drift')
    report=copy.deepcopy(report);report['accepted']+=20
    report['item_use_release']={'policy':POLICY,'new_units':20,'new_item_messages':14,
        'preserved_item_messages':6,'help_prompt':1,'mountain_name_fields':5,'pcsx2_executed':False,
        'visual_status':'pending_user','public_patch_updated':False}
    return [p for p in parents if p['id'] not in absorbed]+patches,report


def normalize(old_patches,new_patches):
    key=('SLUS_212.93',START);pool=new_patches[key];overlay=bytearray(pool['before'])
    keys=[k for k,p in old_patches.items() if k[0]=='SLUS_212.93' and
          max(START,p['offset'])<min(END,p['offset']+len(p['before']))]
    if {old_patches[k]['id'] for k in keys}!={f'elf.ui.{at:08x}' for at in PRESERVED}:
        raise ValueError('Item pool comparison baseline differs')
    for k in keys:
        p=old_patches.pop(k);at=p['offset']-START
        if p['before']!=pool['before'][at:at+len(p['before'])]:raise ValueError('Item pool comparison source differs')
        overlay[at:at+len(p['after'])]=p['after']
    old_patches[key]={**pool,'after':bytes(overlay)}


def prepare():
    from interface_text import compile_draft
    elf=ELF.read_bytes();parent=json.loads((ROOT/PARENT).read_bytes());parents,_=compile_draft(elf,parent)
    patches,absorbed,evidence=derive(elf,parents)
    manifest={'schema':1,'policy':POLICY,'parent':PARENT,'parent_sha256':sha((ROOT/PARENT).read_bytes()),
              'patches':[metadata(p) for p in patches],'absorbed':absorbed,'evidence':evidence}
    raw=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode();(ROOT/MANIFEST).write_bytes(raw)
    child=copy.deepcopy(parent);child.update(item_use_release={'recipe':MANIFEST,'sha256':sha(raw)},
                    iso_name='MetalSaga-ptbr-interface-v071.iso',status=STATUS)
    (ROOT/CHILD).write_bytes((json.dumps(child,ensure_ascii=False,indent=2)+'\n').encode());validate(child)
    print(f'Item use: {len(patches)} patches, {len(absorbed)} inherited messages preserved/repacked')


if __name__=='__main__':prepare()
