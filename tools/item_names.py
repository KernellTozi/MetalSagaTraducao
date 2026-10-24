"""Opt-in generic item/skill names in original NUL slots, never item attributes."""
import json,re,struct
from item_descriptions import original,RESOURCE,ITEM_BASE,ITEM_COUNT,STRIDE,sha
from glyph_spacing import ORIGINAL_SHA
from gfi import encode,decode
from spack_ui import execute_sda_pointer,execute_byte_length,_execute,_reader

POLICY='spack-reviewed-generic-item-names-original-slots-v001'
WINDOWS=((0x70a68,0x70b9c),(0x6d938,0x6d950),(0x705a8,0x70610),
         (0x1b34d0,0x1b3530),(0x1977c8,0x197840),
         (0x2266cc,0x2266d8),(0x2267f0,0x226810))

def bindings(elf):return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]

def catalog(raw):
    if execute_table_bounds(raw)!=(ITEM_BASE,ITEM_COUNT*STRIDE):raise ValueError('Item name table boundary mismatch')
    rows=[]
    for index in range(ITEM_COUNT):
        at=ITEM_BASE+index*STRIDE;record=raw[at:at+STRIDE];field=record[:24]
        end=field.find(b'\0')
        if end<0:raise ValueError('Unterminated item name field')
        value=field[:end]
        rows.append({'id':f'item.name.{index:04d}','index':index,'offset':at,
            'source_hex':value.hex(),'source_sha256':sha(value),'record_sha256':sha(record),
            'source_bytes':len(value),'empty':not value,
            'native':any(c<32 or c>126 for c in value)})
    return rows

def execute_table_bounds(raw):
    if struct.unpack_from('<I',raw,0x808)[0]!=5:raise ValueError('Item SDA count mismatch')
    first,next_=struct.unpack_from('<II',raw,0x80c)
    return 0x800+first,next_-first

def protected(index):
    # All weapons, engines/C Units and named construction components remain
    # out of scope. Generic equipment, consumables, decor and skills are explicit
    # editorial selections, never automatic substring substitutions.
    return (index<100 or 190<=index<=318 or 463<=index<=618 or
            659<=index<=694 or index in (448,453,454,455,456,457,630,633,636,637,
              715,716,717,718,719,724,725,726,729,742,752,801,856,864,929,935,
              941,942,949,950,957,958,959,963,964,971,990,1002,1004,1022,1023,
              1025,1026,1027,1028,1029,1030,1031,1032,1033,1034,1046,1047,1048,1049)
            or index>1049)

def validate_value(row,text):
    if row['empty'] or row['native'] or protected(row['index']):raise ValueError('Protected, native or empty item name')
    value=encode(text);before=bytes.fromhex(row['source_hex'])
    if any(c in before for c in (37,124)):raise ValueError('Variable/control item name blocked')
    if (not value or value!=value.strip() or len(value)>len(before) or
        any(c in value for c in (0,9,10,13,37,124))):raise ValueError('Item name original slot/control budget exceeded')
    if decode(value)!=text:raise ValueError('Item name Unicode round-trip failed')
    if re.findall(rb'\d+',before)!=re.findall(rb'\d+',value):raise ValueError('Item name numbers changed')
    # An accent's second GFI byte may look like ASCII I. Level markers belong
    # to decoded text, not arbitrary bytes inside a multibyte character.
    if re.findall(r'\b(?:EX|I{1,3})\b',before.decode('ascii'))!=re.findall(r'\b(?:EX|I{1,3})\b',text):raise ValueError('Item name level markers changed')
    if value==before:raise ValueError('Unchanged item name must be omitted')
    from translation_policy import validate
    from weapon_terms import validate as weapons
    issues=validate(before.decode('ascii'),text)+weapons(before.decode('ascii'),text)
    if issues:raise ValueError('; '.join(issues))
    return value

def compile_names(elf,config):
    if (sha(elf)!=ORIGINAL_SHA or config.get('policy')!=POLICY or
        config.get('instruction_windows')!=bindings(elf)):raise ValueError('Item name policy/reader mismatch')
    raw=original(RESOURCE)
    if config.get('source_sha256')!=sha(raw) or config.get('table_sha256')!=sha(raw[ITEM_BASE:ITEM_BASE+ITEM_COUNT*STRIDE]):
        raise ValueError('Item name source/table mismatch')
    if execute_sda_pointer(elf,raw,0)!=0x800 or execute_sda_pointer(elf,raw[0x800:],0)!=0x20:
        raise ValueError('Item name SDA lookup mismatch')
    rows=catalog(raw);byid={r['id']:r for r in rows};values={};patches=[];results=[]
    for target in config['entries']:
        if set(target)!={'id','source_sha256','record_sha256','translation','group'}:raise ValueError('Unknown item name metadata')
        key=target['id']
        if key not in byid or key in values:raise ValueError('Unknown/duplicate item name ID')
        row=byid[key]
        if target['source_sha256']!=row['source_sha256'] or target['record_sha256']!=row['record_sha256']:
            raise ValueError('Item name record binding mismatch')
        if target['group'] not in ('generic-equipment','consumables-materials','furniture-accessories','skills','generic-key-items'):
            raise ValueError('Item name editorial context missing')
        value=validate_value(row,target['translation']);values[key]=value
        before=bytes.fromhex(row['source_hex'])+b'\0';after=value+bytes(len(before)-len(value))
        if execute_record_pointer(elf,row['index'])!=row['index']*STRIDE:raise ValueError('Original item record getter mismatch')
        if execute_byte_length(elf,value)!=len(value):raise ValueError('Original item name byte count mismatch')
        patches.append({'id':key,'resource':RESOURCE,'offset':row['offset'],'before':before,'after':after})
        results.append({'id':key,'item_id':row['index'],'offset':row['offset'],
            'source_bytes':len(before)-1,'target_bytes':len(value),'group':target['group']})
    # Duplicate labels in this same table keep the same translation everywhere,
    # including IDs outside the first item/skill category reviewed by an author.
    aliases={}
    for row in rows:
        if not row['empty']:
            source=bytes.fromhex(row['source_hex'])
            aliases.setdefault(source,[]).append(values.get(row['id'],source))
    if any(len(set(group))!=1 for group in aliases.values()):raise ValueError('Shared item name translated inconsistently')
    if not patches:raise ValueError('Empty item name batch')
    return patches,{'policy':POLICY,'accepted':len(patches),'catalog_records':len(rows),
        'nonempty_records':sum(not r['empty'] for r in rows),
        'unique_translated_labels':len({v for v in values.values()}),
        'instruction_windows':bindings(elf),'record_stride':STRIDE,'name_field_bytes':24,
        'per_name_growth':False,'attributes_description_offsets_and_ids_unchanged':True,
        'shared_labels_consistent':True,'runtime_visual_status':'pending_user_verification','results':results,
        'limits':'Fixed original name budgets; sort order may change. No full consumer census, formatter or PS2 execution claimed'}

def validate_review(review,config,rows):
    byid={r['id']:r for r in rows};accepted=[r['id'] for r in config['entries']]
    pending=[r['id'] for r in review['pending']];preserved=[r['id'] for r in review.get('preserved',[])];ids=accepted+pending+preserved
    if (len(ids)!=len(set(ids)) or set(ids)-byid.keys() or review['selected']!=len(ids)
        or review['accepted']!=len(accepted)):raise ValueError('Item name review accounting mismatch')
    for target in review['pending']+review.get('preserved',[]):
        if target['source_sha256']!=byid[target['id']]['source_sha256']:raise ValueError('Deferred item name source mismatch')

def execute_record_pointer(elf,index):
    if not 0<=index<ITEM_COUNT:raise ValueError('Item getter index out of bounds')
    regs=[0]*32;regs[4]=0x620000;regs[31]=0x700000
    read=_reader([(0x620008,struct.pack('<I',index)),(0x475ae8,struct.pack('<I',0x600000))])
    result=_execute(elf,0x6d938,((0x6d938,0x6d950),),regs,read,0x700000)
    return result[2]-0x600000
