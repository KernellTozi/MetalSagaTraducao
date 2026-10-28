"""Opt-in generic item/skill names in original NUL slots, never item attributes."""
import json,re,struct
from item_descriptions import original,RESOURCE,ITEM_BASE,ITEM_COUNT,STRIDE,sha
from glyph_spacing import ORIGINAL_SHA
from gfi import encode,decode
from spack_ui import execute_sda_pointer,execute_byte_length,_execute,_reader

POLICY='spack-reviewed-generic-item-names-original-slots-v001'
CEILING_POLICY='spack-reviewed-generic-names-observed-ceiling-v002'
USER_REVIEW_POLICY='spack-user-reviewed-item-names-observed-ceiling-v003'
CEILING_WINDOWS=((0x1b34ec,0x1b3504),(0x1977c8,0x197910))
WINDOWS=((0x70a68,0x70b9c),(0x6d938,0x6d950),(0x705a8,0x70610),
         (0x1b34d0,0x1b3530),(0x1977c8,0x197840),
         (0x2266cc,0x2266d8),(0x2267f0,0x226810))

def bindings(elf):return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]

def ceiling_binding(elf,raw):
    rows=catalog(raw)
    return {'maximum_original_name_bytes':max(r['source_bytes'] for r in rows),
        'witness_item_ids':[r['index'] for r in rows if r['source_bytes']==16],
        'zero_name_tails':all(not any(raw[r['offset']+r['source_bytes']:r['offset']+24]) for r in rows),
        'instruction_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in CEILING_WINDOWS]}

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

def validate_value(row,text,*,ceiling=None,remote_review=False,repair_review=False,pending_review=False):
    if row['empty'] or row['native'] or protected(row['index']):raise ValueError('Protected, native or empty item name')
    value=encode(text);before=bytes.fromhex(row['source_hex'])
    if any(c in before for c in (37,124)):raise ValueError('Variable/control item name blocked')
    if ceiling is not None and ceiling!=16:raise ValueError('Unsupported observed name ceiling')
    limit=len(before) if ceiling is None else ceiling
    if (not value or value!=value.strip() or len(value)>limit or
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
    if remote_review:
        from item_name_user_review import remote_exception
        if not remote_exception(row,text):raise ValueError('Unreviewed per-record Remote exception')
        issues=[issue for issue in issues if issue!='Termo/nome protegido ausente: Remote']
    if repair_review:
        from item_name_approved_batch import repair_exception
        if not repair_exception(row,text):raise ValueError('Unreviewed Repair Kit exception')
        issues=[issue for issue in issues if issue!='Termo/nome protegido ausente: Repair Kit']
    if pending_review:
        from pending_name_resolution import term_exception
        term=term_exception(row,text)
        if not term:raise ValueError('Unreviewed pending-name terminology exception')
        issues=[issue for issue in issues if issue!='Termo/nome protegido ausente: '+term]
    if issues:raise ValueError('; '.join(issues))
    return value

def compile_names(elf,config):
    if (sha(elf)!=ORIGINAL_SHA or config.get('policy') not in (POLICY,CEILING_POLICY,USER_REVIEW_POLICY) or
        config.get('instruction_windows')!=bindings(elf)):raise ValueError('Item name policy/reader mismatch')
    raw=original(RESOURCE)
    if config.get('source_sha256')!=sha(raw) or config.get('table_sha256')!=sha(raw[ITEM_BASE:ITEM_BASE+ITEM_COUNT*STRIDE]):
        raise ValueError('Item name source/table mismatch')
    if execute_sda_pointer(elf,raw,0)!=0x800 or execute_sda_pointer(elf,raw[0x800:],0)!=0x20:
        raise ValueError('Item name SDA lookup mismatch')
    ceiling=None
    if config['policy'] in (CEILING_POLICY,USER_REVIEW_POLICY):
        expected=ceiling_binding(elf,raw)
        if (config.get('ceiling_evidence')!=expected or expected['maximum_original_name_bytes']!=16 or
            expected['witness_item_ids']!=[954] or not expected['zero_name_tails']):
            raise ValueError('Observed name ceiling evidence mismatch')
        ceiling=16
    elif 'ceiling_evidence' in config:raise ValueError('Historic name policy cannot opt into growth')
    rows=catalog(raw);byid={r['id']:r for r in rows};values={};patches=[];results=[]
    user_review=None
    if config['policy']==USER_REVIEW_POLICY:
        from item_name_user_review import validate_config
        user_review=validate_config(config,rows)
    elif any(k in config for k in ('user_review','approved_extension','pending_resolution')):raise ValueError('Legacy policy cannot consume human-review exceptions')
    for target in config['entries']:
        if set(target)!={'id','source_sha256','record_sha256','translation','group'}:raise ValueError('Unknown item name metadata')
        key=target['id']
        if key not in byid or key in values:raise ValueError('Unknown/duplicate item name ID')
        row=byid[key]
        if target['source_sha256']!=row['source_sha256'] or target['record_sha256']!=row['record_sha256']:
            raise ValueError('Item name record binding mismatch')
        if target['group'] not in ('generic-equipment','consumables-materials','furniture-accessories','skills','generic-key-items'):
            raise ValueError('Item name editorial context missing')
        remote_review=bool(user_review and row['index'] in user_review['remote_term_exception_ids'])
        value=validate_value(row,target['translation'],ceiling=ceiling,remote_review=remote_review,
            repair_review=bool(user_review and 'approved_extension' in config and row['index']==342),
            pending_review=bool(user_review and 'pending_resolution' in config and row['index'] in (625,631,695)));values[key]=value
        span=max(row['source_bytes'],len(value))+1
        before=raw[row['offset']:row['offset']+span]
        if before!=bytes.fromhex(row['source_hex'])+bytes(span-row['source_bytes']):raise ValueError('Nonzero item name tail is not editable padding')
        after=value+bytes(span-len(value))
        if execute_record_pointer(elf,row['index'])!=row['index']*STRIDE:raise ValueError('Original item record getter mismatch')
        if ceiling and execute_name_forwarding(elf,row['index'])!=(row['index']*STRIDE,0x630000):raise ValueError('Common item name forwarding mismatch')
        if execute_byte_length(elf,value)!=len(value):raise ValueError('Original item name byte count mismatch')
        patches.append({'id':key,'resource':RESOURCE,'offset':row['offset'],'before':before,'after':after})
        results.append({'id':key,'item_id':row['index'],'offset':row['offset'],
            'source_bytes':row['source_bytes'],'target_bytes':len(value),'group':target['group']})
    # Duplicate labels in this same table keep the same translation everywhere,
    # including IDs outside the first item/skill category reviewed by an author.
    aliases={}
    for row in rows:
        if not row['empty']:
            source=bytes.fromhex(row['source_hex'])
            aliases.setdefault(source,[]).append(row)
    exceptions=[]
    for source,group in aliases.items():
        if len({values.get(r['id'],source) for r in group})==1:continue
        from item_name_user_review import alias_allowed
        if not user_review or not alias_allowed(source,group,values):raise ValueError('Shared item name translated inconsistently')
        exceptions.append([r['index'] for r in group])
    if not patches:raise ValueError('Empty item name batch')
    return patches,{'policy':config['policy'],'accepted':len(patches),'catalog_records':len(rows),
        'nonempty_records':sum(not r['empty'] for r in rows),
        'unique_translated_labels':len({v for v in values.values()}),
        'instruction_windows':bindings(elf),'record_stride':STRIDE,'name_field_bytes':24,
        'per_name_growth':bool(ceiling),'maximum_target_bytes':max(r['target_bytes'] for r in results),
        **({'ceiling_evidence':config['ceiling_evidence']} if ceiling else {}),
        'attributes_description_offsets_and_ids_unchanged':True,
        'shared_labels_consistent':not bool(exceptions),
        **({'approved_extension':config['approved_extension']} if 'approved_extension' in config else {}),
        **({'pending_resolution':config['pending_resolution']} if 'pending_resolution' in config else {}),
        **({'human_review':{'binding':config['user_review'],'approved_ids':[r['id'] for r in user_review['approved']],
            'remote_term_exception_ids':user_review['remote_term_exception_ids'],
            'record_specific_alias_groups':exceptions,'all_other_shared_labels_consistent':True}} if user_review else {}),
        'runtime_visual_status':'pending_user_verification','results':results,
        'limits':('Observed 16-byte ceiling and original zero tails; no growth beyond the largest original name. '
            if ceiling else 'Fixed original name budgets; ')+
            'Sort order may change. No full consumer census, formatter or PS2 execution claimed'}

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

def execute_name_forwarding(elf,index):
    """Original generic name path, stopping before the formatting routine."""
    if not 0<=index<ITEM_COUNT:raise ValueError('Item name forwarding index outside table')
    regs=[0]*32;regs[3]=index;regs[16]=0x620000
    read=_reader([(0x475ae8,struct.pack('<I',0x600000)),(0x620080,struct.pack('<I',0x630000))])
    result=_execute(elf,0x1b34ec,((0x1b34ec,0x1b3504),),regs,read,0x1977c8)
    return result[5]-0x600000,result[4]
