"""Read-only consolidated menu audit; one replaceable local JSON, no edit authority."""
import argparse,collections,hashlib,json,re,struct
from pathlib import Path
from reinsertion import ROOT,local
from interface_text import catalog,embedded_catalog,controls,FORMAT,SOURCE

RESOURCE='DATA/S/S_PACK.SDA'
TABLE_BASE=0x35070
TABLE_SIZE=0x2000
COUNT=378
PROTECTED={'Hunter','Soldier','MAIN','SUB','SE','Item','Satcom','Remote','C Unit','Drive'}
RANGES=((0x32b110,0x32c000,'character-equipment'),(0x33d700,0x33eaa0,'shops'),
        (0x341000,0x342a00,'shop-services'),(0x349540,0x3497c0,'compact-interface'))
KEYWORDS=re.compile(r'\b(buy|sell|equip|equipment|inventory|skill|attack|defense|quantity|money|price|discard|transfer|repair)\b',re.I)
TECHNICAL=re.compile(r'^(?:\d+[A-Za-z_]|Null|sShop|sScr|fShop|_shop)|[\\/].*\.(?:sda|imd|dat|bin)$|\.(?:sda|imd|gfi)$')


def digest(data):return hashlib.sha256(data).hexdigest()


def counted_strings(raw,base,size,expected_count=None):
    end=base+size
    if base<0 or size<4 or end>len(raw):raise ValueError('Table bounds invalid')
    count=struct.unpack_from('<I',raw,base)[0]
    if expected_count is not None and count!=expected_count:raise ValueError('Unexpected table count')
    header=4+count*4
    if not count or header>size:raise ValueError('Table header invalid')
    offsets=struct.unpack_from('<'+'I'*count,raw,base+4)
    aliases=collections.defaultdict(list)
    for index,offset in enumerate(offsets):
        if not header<=offset<size:raise ValueError('String pointer outside data area')
        aliases[offset].append(index)
    rows=[];prior_end=base+header
    for offset,ids in sorted(aliases.items()):
        start=base+offset;stop=raw.find(b'\0',start,end)
        if stop<0 or start<prior_end:raise ValueError('Unterminated or interior-overlapping strings')
        value=raw[start:stop];ascii_only=all(32<=c<127 or c in (9,10,13) for c in value)
        tokens=[];control_error=None
        if ascii_only:
            try:tokens=[c.hex() for c in controls(value)]
            except ValueError as exc:control_error=str(exc)
        rows.append({'id':f'spack.ui.{start:08x}','offset':start,'relative_offset':offset,
            'source_length':len(value),'terminator_offset':stop,'source_hex':value.hex(),
            'source_sha256':digest(value),'source_ascii':value.decode('ascii') if ascii_only else None,
            'pointer_ids':ids,'pointer_offsets':[base+4+i*4 for i in ids],
            'control_sequence_hex':tokens,'control_parse_issue':control_error,
            'repertoire':'ascii-bytes' if ascii_only else 'native-bytes-unmapped',
            'status':'identified-not-editable','reason':'Counted offsets and NUL bounds proved; runtime reader/buffers and reinsertion policy pending'})
        prior_end=stop+1
    occupied=header+sum(r['source_length']+1 for r in rows)
    return {'base':base,'size':size,'count':count,'header_size':header,
        'unique_payload_bytes':sum(r['source_length'] for r in rows),'unclaimed_bytes':size-occupied,
        'unclaimed_bytes_are_editable_capacity':False,
        'unique_strings':len(rows),'alias_references':count-len(rows),'offsets':list(offsets),
        'table_sha256':digest(raw[base:end]),'entries':rows}


def classify_elf(row,translated,restored):
    text=row['source'];key=row['id']
    if key in translated:return 'translated'
    if key in restored:return 'restored-original'
    if text in PROTECTED:return 'protected-term'
    if TECHNICAL.search(text) or re.search(r'\.(?:sda|imd|gfi)$',text,re.I) or re.fullmatch(r'[a-z_][A-Za-z0-9_]*[A-Z][A-Za-z0-9_]*',text):return 'technical-candidate'
    if 0x319000<=row['offset']<0x31a000:return 'named-content-review'
    residue=FORMAT.sub(b'',text.encode('ascii')).decode('ascii')
    if not re.search(r'[A-Za-z]',residue):return 'format-or-data-only'
    if len(text)<=3 and text not in {'Atk','Def','Dur','Wgt','Mnt','EXP','Dog','Bio','Old'}:return 'short-fragment-review'
    if any(a<=row['offset']<z for a,z,_ in RANGES) or KEYWORDS.search(text):
        return 'review-reference' if row['status']=='referenced-candidate' else 'blocked-reference'
    return 'outside-current-selection'


def audit(draft,output):
    if not draft.resolve().is_relative_to(ROOT/'translations'):raise ValueError('Recipe must be under translations')
    recipe=json.loads(draft.read_text(encoding='utf-8'));elf=SOURCE.read_bytes()
    inventory={r['path']:r for r in json.loads((ROOT/'reports/inventory.json').read_text(encoding='utf-8'))}
    pack=(ROOT/'JOGO/Metal Saga'/RESOURCE).read_bytes()
    if digest(pack)!=inventory[RESOURCE]['sha256']:raise ValueError('Original S_PACK source mismatch')
    from probe_resources import nested
    nodes=nested(pack);node=next((n for n in nodes if n['offset']==0x35000),None)
    if not node or node['count']!=22 or node['offsets'][:2]!=[0x70,0x2070]:raise ValueError('Original UI SDA bounds mismatch')
    table=counted_strings(pack,TABLE_BASE,TABLE_SIZE,COUNT)
    translated={r['id']:r for r in recipe['entries']};restored=set(recipe.get('restored_originals',[]))
    cat=catalog(elf);byid={r['id']:r for r in cat['entries']}
    if recipe.get('embedded_literal_profile'):byid.update({r['id']:r for r in embedded_catalog(elf)})
    for key,value in translated.items():
        if key not in byid or value['source_sha256']!=byid[key]['source_sha256']:raise ValueError('Existing translation binding mismatch')
    rows=[]
    for row in sorted(byid.values(),key=lambda e:e['offset']):
        row=dict(row)
        if 'source' not in row:row['source']=bytes.fromhex(row['source_hex']).decode('ascii')
        row['planning_status']=classify_elf(row,translated,restored)
        row['candidate_contexts']=[name for a,z,name in RANGES if a<=row['offset']<z]
        if row['id'] in translated:row['translation']=translated[row['id']]['translation']
        rows.append(row)
    spack_config=recipe.get('spack_ui')
    if spack_config:
        if spack_config.get('policy')!='spack-ui-counted-alias-preserving-repack-v001' or spack_config['source_sha256']!=digest(pack) or spack_config['table_sha256']!=table['table_sha256']:
            raise ValueError('S_PACK recipe planning binding mismatch')
        for row in table['entries']:
            target=spack_config['translations'].get(str(row['pointer_ids'][0]))
            if target:
                if target['source_sha256']!=row['source_sha256']:raise ValueError('S_PACK entry planning binding mismatch')
                row['translation']=target['translation'];row['status']='translated-in-recipe-pending-visual'
                row['reason']='Explicit alias-preserving UI policy; original source offsets retained in this audit'
            else:
                row['status']='preserved-in-recipe'
                row['reason']='Native bytes, protected names, stable symbols, unchanged Portuguese or blocked composition; consult current release'
    multiline=[];refs=None
    from interface_text import references,sections
    refs=references(elf,sections(elf))
    for start in (0x32b6a0,):
        stop=elf.find(b'\0',start);value=elf[start:stop]
        multiline.append({'id':f'elf.ui.{start:08x}','offset':start,'source_hex':value.hex(),
            'source_ascii':value.decode('ascii'),'source_length':len(value),'source_sha256':digest(value),
            'references':refs.get(start+0xff000,[]),'control_sequence_hex':[c.hex() for c in controls(value)],
            'status':'identified-not-editable','reason':'Multiline literal excluded by historical catalog; explicit consumer/alias policy needed'})
    if recipe.get('character_status'):
        target=recipe['character_status']
        if target['source_sha256']!=multiline[0]['source_sha256']:raise ValueError('Character status planning binding mismatch')
        multiline[0]['translation']=target['translation'];multiline[0]['status']='translated-in-recipe-pending-visual'
        multiline[0]['reason']='Explicit single multiline formatter policy'
    satcom=[]
    if recipe.get('satcom_records'):
        from spack_satcom import parse_table,TABLES as SATCOM_TABLES,sha as satcom_sha
        config=recipe['satcom_records'];targets={r['id']:r for r in config['entries']}
        if config['source_sha256']!=satcom_sha(pack):raise ValueError('Satcom planning source binding mismatch')
        for kind,(_,base,size,_) in SATCOM_TABLES.items():
            if config['table_sha256'][kind]!=satcom_sha(pack[base:base+size]):raise ValueError('Satcom planning table binding mismatch')
            for row in parse_table(pack,kind):
                for field,value in row['fields'].items():
                    key=f"spack.{kind}.{row['id']:03d}.{field}";target=targets.get(key)
                    item={'id':key,'offset':row['offset']+value['relative'],'record_offset':row['offset'],
                        'record_size':row['size'],'source':value['raw'].decode('ascii'),
                        'source_hex':value['raw'].hex(),'source_sha256':satcom_sha(value['raw']),
                        'status':'translated-in-recipe-pending-visual' if target else 'preserved-in-recipe'}
                    if target:
                        if target['source_sha256']!=item['source_sha256'] or target['record_sha256']!=satcom_sha(row['raw']):
                            raise ValueError('Satcom planning record/field binding mismatch')
                        item['translation']=target['translation']
                    satcom.append(item)
    item_rows=[]
    if recipe.get('item_descriptions'):
        from item_descriptions import catalog as item_catalog
        config=recipe['item_descriptions'];targets={r['id']:r for r in config['entries']}
        if config['source_sha256']!=digest(pack):raise ValueError('Item planning source binding mismatch')
        review=recipe.get('description_review',{})
        pending={r['id']:r for r in review.get('pending',[])}
        preserved={r['id'] for r in review.get('preserved',[])}
        item_sources=item_catalog(pack)
        if review.get('policy'):
            from prepare_item_batch import validate_review
            validate_review(review,config,item_sources)
        for row in item_sources:
            item=dict(row);target=targets.get(row['id'])
            deferred=pending.get(row['id'])
            item['status']=('translated-in-recipe-pending-visual' if target else
                ('preserved-reviewed-marker' if row['id'] in preserved else
                 (('deferred-control' if deferred.get('kind')=='technical-control' else 'deferred-space') if deferred else 'not-reviewed')))
            if target:
                if target['source_sha256']!=row['source_sha256'] or target['item_records']!=row['items']:raise ValueError('Item planning binding mismatch')
                item['translation']=target['translation']
            item_rows.append(item)
    # Counts are disjoint statuses, not percentages of all game screens.
    summary={'elf_catalog_rows':len(rows),'elf_statuses':dict(collections.Counter(r['planning_status'] for r in rows)),
        'spack_pointer_ids':table['count'],'spack_unique_strings':table['unique_strings'],
        'spack_alias_references':table['alias_references'],'spack_unique_payload_bytes':table['unique_payload_bytes'],
        'spack_unclaimed_bytes':table['unclaimed_bytes'],
        'spack_repertoires':dict(collections.Counter(r['repertoire'] for r in table['entries'])),
        'spack_statuses':dict(collections.Counter(r['status'] for r in table['entries'])),
        'spack_control_parse_issues':sum(bool(r['control_parse_issue']) for r in table['entries']),
        'additional_multiline_literals':len(multiline),
        **({'satcom_fields':len(satcom),'satcom_statuses':dict(collections.Counter(r['status'] for r in satcom))} if satcom else {}),
        **({'item_descriptions':len(item_rows),'item_statuses':dict(collections.Counter(r['status'] for r in item_rows))} if item_rows else {})}
    document={'schema':1,'scope':'Menu planning only; references/keyword matches do not approve editing or prove screen coverage',
        'recipe':draft.relative_to(ROOT).as_posix(),'recipe_sha256':digest(draft.read_bytes()),
        'source_elf_sha256':digest(elf),'source_spack_sha256':digest(pack),'summary':summary,
        'elf':rows,'additional_elf_literals':multiline,'spack_ui':table,
        'composition_review':[{'id':r['id'],'pointer_ids':r['pointer_ids'],'reason':'English word assembled with %screased; caller arguments and sentence structure need review'} for r in table['entries'] if r['source_ascii'] and '%screased' in r['source_ascii']],
        'next_work':(['Review blocked %screased composition and remaining interface contexts; retain native/name locks',
            'Collect consolidated visual test of character, inventory and shops'] if spack_config else
            ['Trace S_PACK UI reader/buffers; pin character formatter; review literal candidates']),
        'originals_modified':False,'iso_created':False,'translation_created':False}
    if satcom:document['satcom_records']=satcom
    if item_rows:document['item_descriptions']=item_rows
    output=local(output);output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():
        old=json.loads(output.read_text(encoding='utf-8'))
        if old.get('scope')!=document['scope']:raise ValueError('Refusing to replace unrelated file')
    temp=output.with_suffix('.json.tmp')
    if temp.exists():raise ValueError('Audit temporary output already exists')
    temp.write_text(json.dumps(document,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(output)
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser(description='Planejar menus em um JSON local consolidado, sem editar jogo')
    p.add_argument('--draft',type=Path,default=ROOT/'translations/interface-v018.json')
    p.add_argument('--output',type=Path,default=ROOT/'work/planejamento-interface.json');a=p.parse_args()
    print(json.dumps(audit(a.draft.resolve(),a.output),ensure_ascii=False,indent=2))
