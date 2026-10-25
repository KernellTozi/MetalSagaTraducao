"""Read-only discovery of untranslated/uncertain resources; never compiles an ISO.

Original text and previews stay in work/. Public output is metadata only.
Candidates, address-like words and texture geometry are not edit permission.
"""
import argparse,collections,hashlib,json,mmap,re,struct
from pathlib import Path
from reinsertion import ROOT,SOURCE,local
from build_translation_pilot import load_draft,compile_draft
from interface_text import SOURCE as ELF,sections,compile_draft as compile_ui
from dialogue import sha
from gfi import encode,CHAR_TO_BYTES

SCOPE='Read-only consolidated remaining-catalogue discovery v001'
RUN=re.compile(rb'(?<![\x20-\x7e\r\n\t])[\x20-\x7e\r\n\t]{5,1024}\x00')
WORDS=re.compile(rb'[A-Za-z]{2,}')
PATH=re.compile(rb'[\\/]|\.(?:sda|dat|bin|gfi|h|cpp|irx)\b',re.I)

def ascii_stream(stream,chunk_size=1024*1024):
    """Bounded NUL strings, correct offsets across chunk boundaries, no duplicates."""
    if chunk_size<1:raise ValueError('Invalid discovery chunk size')
    carry=b'';position=0
    while True:
        chunk=stream.read(chunk_size)
        if not chunk:break
        raw=carry+chunk;base=position-len(carry)
        for match in RUN.finditer(raw):
            if base and match.start()==0 or base+match.end()<=position:continue
            yield base+match.start(),match.group()[:-1]
        position+=len(chunk);carry=raw[-1026:]

def phrase_candidate(raw):
    words=WORDS.findall(raw);letters=sum(map(len,words));compact=re.sub(rb'\s+',b'',raw)
    return len(words)>=2 and letters>=8 and letters/max(1,len(compact))>=0.72 and bool(re.search(rb'\S[ \r\n\t]+\S',raw)) and not PATH.search(raw)

def call_after(elf,start,limit=64):
    for at in range(start+4,min(start+limit,len(elf)-3),4):
        word=struct.unpack_from('<I',elf,at)[0]
        if word>>26==3:return {'offset':at,'target_file_offset':((word&0x3ffffff)<<2)-0xff000}
        if word>>26==2 or word==0x03e00008:break
    return None

def elf_discovery(elf,planning,patches):
    text=sections(elf)['.text'];lo=text['va'];hi=lo+text['size'];rows=[];counts=collections.Counter()
    changes=[p for p in patches if p['resource']=='SLUS_212.93']
    for row in planning['elf']:
        raw=bytes.fromhex(row['source_hex']);at=row['offset'];status=row['planning_status'];covered=[]
        for p in changes:
            if p['offset']<=at and at+len(raw)<=p['offset']+len(p['after']):
                actual=p['after'][at-p['offset']:at-p['offset']+len(raw)]
                covered.append({'patch_id':p['id'],'source_bytes_changed':actual!=raw})
        address_like=at%4==0 and len(raw)==3 and lo<=int.from_bytes(raw+b'\0','little')<hi and int.from_bytes(raw+b'\0','little')%4==0
        if covered:bucket='within-authored-patch'
        elif status in ('translated','restored-original','protected-term'):bucket='already-accounted-for'
        elif address_like:bucket='address-like-data-review'
        elif status=='technical-candidate' or PATH.search(raw) or b'::' in raw or re.search(rb'Q\d|tLink|tList|t5t',raw):bucket='technical-or-symbol-review'
        elif re.search(rb'[A-Za-z]{3}',raw):bucket='text-context-review'
        else:bucket='short-or-format-review'
        counts[bucket]+=1
        evidence=[]
        for ref in row.get('references',[]):
            pos=ref.get('immediate_offset',ref['offset'])
            if ref['kind']!='data-pointer':
                call=call_after(elf,pos)
                if call:evidence.append(call)
        rows.append({**row,'discovery_class':bucket,'authored_patch_overlap':covered,
            'first_following_calls':evidence,'direct_common_text_formatter':any(c['target_file_offset']==0x1977c8 for c in evidence),
            'editing_authorized':False})
    return {'classes':dict(counts),'catalogue_rows':len(rows),
        'uncovered_direct_formatter_candidates':sum(r['direct_common_text_formatter'] and r['discovery_class'] not in ('within-authored-patch','already-accounted-for') for r in rows),
        'limits':'Nearby calls are bounded address evidence, not a full use/visibility proof. Address-like bytes are not rejected as false positives automatically.'},rows

def label_deficit(entry,record,target):
    if bytes.fromhex(entry['tag'])!=b'msgn' or len(entry['segments'])!=2:raise ValueError('Deficit proof restricted to two-string msgn')
    body=entry['segments'][0]['offset']-entry['offset'];end=record.index(0,body)
    minimum=body+(end-body)+1+len(encode(target))+1
    return {'minimum_record_bytes':minimum,'original_record_bytes':len(record),
        'extra_bytes_required':max(0,minimum-len(record)),'body_bytes':end-body,'label_target_bytes':len(encode(target))}

def map_discovery(data,document,patches,report):
    from speaker_labels import ROLES
    from speaker_label_review import EXTRA
    from audit_dialogue_backlog import classify
    protected=json.loads((ROOT/'reports/n3-preservation-v001.json').read_text(encoding='utf-8'))['records']
    metadata,buckets=classify(document,report,protected);compiled={p['id']:p for p in patches}
    labels=[];remaining=collections.Counter();label_groups=collections.defaultdict(list);native=[]
    entries=document['entries']
    for number,e in enumerate(entries):
        label=next((s for s in e['segments'] if s['key']=='label'),None)
        if label and label['translation']==label['source']:
            source=label['source'];label_groups[source].append(e['id'])
            if source in ROLES or source in EXTRA:
                raw=compiled[e['id']]['after'] if e['id'] in compiled else bytes(data[e['offset']:e['offset']+e['size']])
                target=EXTRA.get(source,ROLES.get(source));budget=label_deficit(e,raw,target)
                if budget['extra_bytes_required']<=0:raise ValueError('Unexpected remaining label that fits; review classification')
                remaining[source]+=1;labels.append({'id':e['id'],'resource':'DATA/MAP/MAP.MCT','record_sha256':e['record_sha256'],
                    'record_offset':e['offset'],'block_offset':e['block_offset'],'label_offset':label['offset'],
                    'source':source,'existing_proposal':target,**budget,'status':'located-needs-storage-proof',
                    'context':[{ 'id':n['id'],'segments':n['segments']} for n in entries[max(0,number-1):number+2] if n['block_offset']==e['block_offset']]})
        if e['id'] in {n['id'] for n in buckets.get('native_pending_context',[])}:
            native.append({'id':e['id'],'offset':e['offset'],'block_offset':e['block_offset'],'record_sha256':e['record_sha256'],
                'segments':e['segments'],'nearby_same_block':[{'id':n['id'],'segments':n['segments']} for n in entries[max(0,number-2):number+3] if n['block_offset']==e['block_offset']],
                'status':'located-native-context-pending'})
    deficits=collections.Counter(str(r['extra_bytes_required']) for r in labels)
    editorial=buckets.get('editorial_review_not_automatic_translation',[])
    return {**metadata,'remaining_reviewed_labels':len(labels),'label_sources':dict(remaining),'label_deficit_distribution':dict(deficits),
        'editorial_review_by_family':dict(collections.Counter(bytes.fromhex(e['tag']).rstrip(b'\0').decode('ascii') for e in editorial)),
        'editorial_entries_with_asterisk_expressions':sum(any('*' in s['source'] for s in e['segments'] if s['editable']) for e in editorial),
        'unchanged_label_sources':len(label_groups),'unchanged_label_references':sum(map(len,label_groups.values()))}, {
        'labels':labels,'native':native,'unchanged_label_groups':[{'source':s,'ids':ids,'editing_authorized':False} for s,ids in label_groups.items()],
        'editorial_review':editorial}

def item_discovery(recipe,elf,raw):
    from item_names import catalog,ceiling_binding,STRIDE,ITEM_BASE
    from translation_policy import validate
    rows=catalog(raw);byid={r['id']:r for r in rows};groups=collections.defaultdict(list)
    for r in rows:
        if not r['empty']:groups[r['source_hex']].append(r['id'])
    pending=[];counts=collections.Counter()
    for proposal in recipe['item_name_review']['pending']:
        r=byid[proposal['id']];text=proposal['proposed'];encoded=None
        missing=sorted(set(c for c in text if c not in CHAR_TO_BYTES and not 0x20<=ord(c)<=0x7e))
        if not missing:encoded=encode(text)
        flags=[]
        if missing:flags.append('unmapped-glyph')
        if encoded is not None and len(encoded)>16:flags.append('exceeds-observed-16-byte-ceiling')
        if encoded is not None and len(encoded)>23:flags.append('exceeds-24-byte-field-with-nul')
        issues=validate(bytes.fromhex(r['source_hex']).decode('ascii'),text)
        if issues:flags.append('terminology-or-name-review')
        counts.update(flags)
        pending.append({**r,'existing_proposal':text,'proposal_bytes':len(encoded) if encoded is not None else None,
            'missing_glyphs':[f'U+{ord(c):04X}' for c in missing],'all_blockers':flags,'terminology_issues':issues,
            'alias_ids':groups[r['source_hex']],'name_field':[r['offset'],r['offset']+24],
            'description_pointer_offset':r['offset']+24,'attributes_begin':r['offset']+28,'editing_authorized':False})
    evidence=ceiling_binding(elf,raw)
    return {'pending_names':len(pending),'blockers_nonexclusive':dict(counts),'record_count':len(rows),'record_stride':STRIDE,
        'table_offset':ITEM_BASE,'name_field_bytes':24,'description_pointer_at':24,
        'original_maximum_bytes':evidence['maximum_original_name_bytes'],'original_maximum_witnesses':evidence['witness_item_ids'],
        'all_name_tails_zero_through_23':evidence['zero_name_tails'],
        'proposals_above_16_but_within_23':sum(r['proposal_bytes'] is not None and 16<r['proposal_bytes']<=23 for r in pending),
        'limits':'A 24-byte field and zero tail do not prove every consumer accepts 23 bytes; current compiler ceiling remains 16. No growth or new glyph authorized.'},pending

def title_discovery(elf):
    from speaker_labels import _run
    from glyph_spacing import ORIGINAL_SHA
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('TITLE ELF differs')
    windows=((0x10ba2c,0x10ba54),(0x10b7d0,0x10b7dc),(0x10bfc8,0x10bfd8),(0x10b210,0x10b248))
    if struct.unpack_from('<I',elf,0x10b210)[0]!=0x24030001:raise ValueError('TITLE initializer constant differs')
    initialization=[]
    for flags in (0,1,2,3):
        for index in (0,1):
            memory=bytearray(0x3040);r=[0]*32;r[16]=0x620000;r[3]=1;r[5]=flags;r[6]=index
            stop=0x10b248 if flags&3==1 and index else 0x10b244
            _run(elf,0x10b21c,windows,r,[(0x620000,memory)],stop)
            mode=struct.unpack_from('<I',memory,0x3038)[0]
            if mode!=int(flags&3==1 and index==0):raise ValueError('TITLE mode initialization differs')
            initialization.append({'flags':flags,'index':index,'title_mode':mode})
    cases=[]
    for title,flags in ((0,0),(0,2),(1,0),(1,2)):
        memory=bytearray(0x3040);struct.pack_into('<I',memory,0x3038,title);struct.pack_into('<I',memory,0x18,flags)
        regs=[0]*32;regs[16]=0x620000
        stop=0x10b7d0 if title or flags&2 else 0x10ba94
        result=_run(elf,0x10ba2c,windows,regs,[(0x620000,memory)],stop)
        if stop==0x10b7d0 and result[5]!=4:raise ValueError('TITLE does not request state 4')
        cases.append({'title_mode':title,'flags':flags,'stop_offset':stop,'requested_state':result[5] if stop==0x10b7d0 else None})
    memory=bytearray(b'\xa5'*0x100);initial=bytes(memory);regs=[0]*32;regs[4]=0x620000;regs[5]=4;regs[31]=0x700000
    _run(elf,0x10b7d0,windows,regs,[(0x620000,memory)],0x700000)
    if struct.unpack_from('<II',memory,0x84)!=(4,0) or any(a!=b for i,(a,b) in enumerate(zip(initial,memory)) if not 0x84<=i<0x8c):raise ValueError('TITLE state setter writes outside fields')
    outcomes=[]
    if struct.unpack_from('<I',elf,0x10bfc8)[0]!=0x8603009e:raise ValueError('TITLE terminal field load differs')
    for condition in (0,1):
        m=bytearray(0xa0);struct.pack_into('<H',m,0x9e,condition);r=[0]*32;r[16]=0x620000
        # The bound LH is mapped by the harness; execute its following original
        # branch/delay-slot/return-value code, not a claimed whole handler.
        r[3]=struct.unpack_from('<h',m,0x9e)[0]
        result=_run(elf,0x10bfcc,windows,r,[(0x620000,m)],0x10bfd8)
        if result[2]!=(condition==0):raise ValueError('TITLE completion branch differs')
        outcomes.append({'field_9e':condition,'return_value':result[2]})
    table=list(struct.unpack_from('<5I',elf,0x32a540))
    if table!=[0x20c610,0x20c620,0x20c630,0x20c640,0x20c650]:raise ValueError('Name state dispatcher differs')
    return {'resource':'SLUS_212.93','legend_offsets':[0x32a310,0x32a348,0x32a380],
        'title_slots':[{'offset':at+elf[at:elf.index(0,at)].index(b'TITLE'),'capacity':5} for at in (0x32a310,0x32a348,0x32a380) if b'TITLE' in elf[at:elf.index(0,at)]],
        'instruction_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in windows],
        'state_table_offset':0x32a540,'state_table_targets_va':table,'request_cases':cases,'completion_cases':outcomes,
        'title_initialization_cases':initialization,'config_call_sites':[0x177808,0x1c76c8,0x1e0010,0x1e4cf8],
        'observed':'Input requests state 4; setter writes +0x84=4/+0x88=0; state 4 dispatches to 0x10BF18; bounded terminal branch returns boolean',
        'terminal_lh_simulated_by_harness':True,
        'pending':'External owner/destination still requires proof; return-to-title meaning not approved',
        'editing_authorized':False,'pcsx2_executed':False}

def scan_resources(inventory,patches):
    groups=collections.defaultdict(list)
    for p in patches:groups[p.get('resource','DATA/MAP/MAP.MCT')].append((p['offset'],p['offset']+len(p['before'])))
    summaries=[];candidates=[]
    for row in inventory:
        resource=row['path'];path=(ROOT/'JOGO/Metal Saga'/resource)
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT/'JOGO/Metal Saga'):raise ValueError('Inventory path escapes original root')
        selected=resource.startswith('DATA/') and not resource.startswith('DATA/SOUND/') and resource!='DATA/MAP/MAP.MCT' and not resource.endswith('.GFI')
        digest=hashlib.sha256();found=0
        with path.open('rb') as stream:
            before=path.stat()
            if selected:
                # Hash in a separate streaming pass; regex state stays bounded.
                for at,raw in ascii_stream(stream):
                    if not phrase_candidate(raw):continue
                    overlaps=any(a<at+len(raw)+1 and at<b for a,b in groups[resource])
                    candidates.append({'resource':resource,'offset':at,'size':len(raw)+1,'source_sha256':sha(raw),'source':raw.decode('ascii'),
                        'authored_patch_overlap':overlaps,'classification':'phrase-shape-only','editing_authorized':False});found+=1
                stream.seek(0)
            while chunk:=stream.read(1024*1024):digest.update(chunk)
        after=path.stat()
        if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns) or digest.hexdigest()!=row['sha256']:raise ValueError('Original resource changed/differs: '+resource)
        summaries.append({'resource':resource,'size':before.st_size,'sha256':digest.hexdigest(),'phrase_scan':selected,'phrase_candidates':found})
    return summaries,candidates

def atlas_discovery(inventory,patches):
    from explore_interface_atlases import inspect
    resources=[];local_rows=[]
    for row in inventory:
        resource=row['path']
        if not resource.endswith('.SDA') or not (resource.startswith(('DATA/FDATA/','DATA/RDATA/')) or resource=='DATA/S/S_PAINT.SDA'):continue
        raw=(ROOT/'JOGO/Metal Saga'/resource).read_bytes()
        if sha(raw)!=row['sha256']:raise ValueError('Atlas source differs')
        try:records=inspect(raw)
        except ValueError as error:
            resources.append({'resource':resource,'discovery_error':str(error),'editing_authorized':False})
            local_rows.append({'resource':resource,'entries':[],'discovery_error':str(error)})
            continue
        for r in records:
            if r['kind']!='texture':continue
            r['recipe_patch_overlap']=any(p['resource']==resource and p['offset']<r['offset']+r['size'] and r['offset']<p['offset']+len(p['before']) for p in patches)
        resources.append({'resource':resource,'entries':len(records),'kinds':dict(collections.Counter(r['kind'] for r in records)),
            'textures_without_recipe_patch':sum(r['kind']=='texture' and not r['recipe_patch_overlap'] for r in records),
            'limits':'Recognized texture/GANM structures only; patch intersection does not prove every word translated; absence does not prove text exists'})
        local_rows.append({'resource':resource,'entries':records})
    return resources,local_rows

def phrase_triage(rows,planning,atlas_rows):
    """Separate existing catalogues and raster/compressed bytes from new review."""
    spans=collections.defaultdict(list)
    for r in planning['item_names']:spans['DATA/S/S_PACK.SDA'].append((r['offset'],r['offset']+24,'known-item-name-field'))
    for r in planning['item_descriptions']:
        at=r.get('original_offset',r['offset']);spans['DATA/S/S_PACK.SDA'].append((at,at+len(bytes.fromhex(r['source_hex']))+1,'known-description-field'))
    for r in planning['spack_ui']['entries']:spans['DATA/S/S_PACK.SDA'].append((r['offset'],r['terminator_offset']+1,'known-ui-table-field'))
    for r in planning.get('battle_fields',[]):spans['DATA/S/S_PACK.SDA'].append((r['offset'],r['offset']+r['field_bytes'],'known-battle-field-or-adjacent-bytes'))
    for key in ('satcom_records','interaction_fields'):
        for r in planning.get(key,[]):spans['DATA/S/S_PACK.SDA'].append((r['offset'],r['offset']+len(bytes.fromhex(r['source_hex']))+1,'known-'+key))
    spans['DATA/S/S_PACK.SDA'].append((0x320f0,0x325d0,'engine-variant-region-preserve-review'))
    spans['DATA/S/S_PACK.SDA'].append((0x7e720,0x7ed60,'new-location-record-table'))
    spans['DATA/S/S_PACK.SDA'].append((0xf5260,0xf5800,'opaque-child-container-tail-review'))
    spans['DATA/FDATA/DIARY.DAT'].append((0,11252,'known-diary-resource'))
    spans['DATA/S/S_PAINT.SDA'].append((0xae6a0,0xb06b0,'new-paint-caption-table'))
    spans['DATA/FDATA/FD_END.SDA'].append((0x800,0x1800,'compressed-credits-bytes'))
    for resource in atlas_rows:
        for r in resource['entries']:
            if r['kind']=='texture':spans[resource['resource']].append((r['offset'],r['offset']+r['size'],'recognized-raster-bytes'))
    counts=collections.Counter()
    for row in rows:
        at=row['offset'];kind=next((kind for a,b,kind in spans[row['resource']] if (a<=at or kind=='known-battle-field-or-adjacent-bytes' and 0<a-at<=3) and at+row['size']<=b),None)
        if kind is None:
            if row['authored_patch_overlap']:kind='inside-existing-authored-patch'
            elif len(re.findall(r'\b[A-Z]?[a-z]{2,}\b',row['source']))>=2:kind='unresolved-sentence-case-shape'
            else:kind='unresolved-binary-or-text-shape'
        row['catalogue_relation']=kind;counts[kind]+=1
    return dict(counts)

def engine_variants(raw):
    """Structural extraction only; these engine names follow the user's keep rule."""
    from item_names import catalog,protected
    items={r['index']:r for r in catalog(raw)};rows=[]
    if struct.unpack_from('<II',raw,0x800+12+3*4)!=(0x318f0,0x31dd0) or raw[0x325c8:0x325d0]!=struct.pack('<II',20,20):raise ValueError('Engine variant region/tail differs')
    for i in range(10):
        at=0x320f0+i*124;item_id=struct.unpack_from('<I',raw,at)[0]
        if item_id!=299+i or not protected(item_id):raise ValueError('Engine variant anchor differs')
        for j in range(5):
            pos=at+4+j*24;field=raw[pos:pos+24];end=field.find(b'\0')
            if end<0 or any(field[end:]) or any(not 32<=v<127 for v in field[:end]):raise ValueError('Engine variant string field differs')
            rows.append({'id':f'engine.variant.{i:02d}.{j}','item_id':item_id,'offset':pos,'source_hex':field[:end].hex(),
                'source_sha256':sha(field[:end]),'empty':end==0,'field_bytes':24,'decision':'preserve-user-engine-name-rule','editing_authorized':False})
    return {'resource':'DATA/S/S_PACK.SDA','offset':0x320f0,'slot_size':0x4e0,'record_stride':124,'records':10,
        'name_fields':50,'nonempty_names':sum(not r['empty'] for r in rows),'item_ids':list(range(299,309)),
        'opaque_tail_bytes':8,'consumer_proven':False,'editing_authorized':False,
        'decision':'Preserve engine names per user; structural extraction does not establish every consumer'},rows

def font_discovery():
    from gfi import Gfi,sjis_to_jis
    used={int.from_bytes(v,'big') for v in CHAR_TO_BYTES.values()};common=None;fonts=[]
    for name in ('SUC20I22.GFI','SUC24I26.GFI'):
        path=ROOT/'JOGO/Metal Saga/DATA/SYS'/name;raw=path.read_bytes();font=Gfi(raw);blank=set(font.blank_columns())
        pairs={code for code in range(0x8240,0x829f) if code&255!=127 and sjis_to_jis(code)&255 in blank and code not in used}
        common=pairs if common is None else common&pairs
        fonts.append({'resource':'DATA/SYS/'+name,'source_sha256':sha(raw),'cell_side':font.side,'unassigned_blank_pairs':len(pairs)})
    needed='çáàãâéêíóôõúüÇÁÀÃÂÉÊÍÓÔÕÚÜ'
    return {'current_project_mapping_count':len(CHAR_TO_BYTES),'unmapped_ptbr_codepoints':[f'U+{ord(c):04X}' for c in needed if c not in CHAR_TO_BYTES],
        'common_blank_unassigned_pairs':[f'{code:04x}' for code in sorted(common)],'fonts':fonts,
        'editing_authorized':False,'font_or_codec_changed':False,
        'pending':'Blank cells are storage candidates only; audit usage and extend codec, cache, both layout paths, metrics and regression profiles together; preserve accepted 18 mappings and ASCII banks'}

def location_discovery(elf,raw):
    from plan_interface_menus import counted_strings
    from speaker_labels import _run
    from glyph_spacing import ORIGINAL_SHA
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Location ELF source differs')
    table=counted_strings(raw,0x7e720,0x640,25);records=[];positions=table['offsets']+[0x640]
    windows=((0x6ce70,0x6ce80),(0x11f35c,0x11f384))
    if struct.unpack_from('<I',elf,0x11f378)[0]!=0x8e420020:raise ValueError('Location flag field boundary differs')
    for row in table['entries']:
        index=row['pointer_ids'][0];at=row['offset'];end=0x7e720+positions[index+1]
        field=raw[at:at+32];nul=field.find(b'\0')
        if nul<1 or any(field[nul:]) or end<at+44:raise ValueError('Location name/metadata bounds differ')
        regs=[0]*32;regs[22]=0x470000;regs[20]=index;regs[21]=0x620000
        result=_run(elf,0x11f35c,windows,regs,[(0x475b28,bytearray(struct.pack('<I',0x600000))),
            (0x6201d0,bytearray(4)),(0x600000,bytearray(raw[0x7e720:0x7ed60]))],0x11f378)
        if result[18]!=0x600000+row['relative_offset']:raise ValueError('Location original pointer lookup differs')
        records.append({**row,'id':f'location.name.{index:03d}','record_end':end,'record_sha256':sha(raw[at:end]),
            'name_field_bytes':32,'flags_offset':at+32,'runtime_write_offsets':[at+36,at+40],'editing_authorized':False})
    metadata={'resource':'DATA/S/S_PACK.SDA','sda_node_offset':0x35000,'sda_entry':3,'offset':0x7e720,'size':0x640,
        'records':25,'unique_names':len(records),'name_field_bytes':32,'maximum_original_name_bytes':max(r['source_length'] for r in records),
        'original_pointer_cases':25,'original_pointer_lookup_executed':True,'global_pointer_va':0x475b28,
        'instruction_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in windows],
        'editing_authorized':False,'pending':'Review generic destinations versus protected cities; pin name consumers and preserve flags/coordinates/variable record tails. Do not repack as a plain string pool.',
        'limits':'Original pointer selection executed; complete menu, unlock flags, writes, formatting and PS2 not executed'}
    tail={'resource':'DATA/S/S_PACK.SDA','child_offset':0xb4000,'declared_end':0xf5260,'slot_end':0xf5800,
        'tail_size':0x5a0,'nonzero_bytes_in_tail':sum(v!=0 for v in raw[0xf5260:0xf5800]),'matching_known_enemy_record':{'tail_offset':0xf5278,'known_offset':0x76278,
            'record_size':276,'byte_identical':raw[0xf5278:0xf5278+276]==raw[0x76278:0x76278+276]},
        'editing_authorized':False,'status':'Text outside child declared size; copied battle bytes observed; read extent/consumers unresolved. Do not promote English remnants as live untranslated dialogue.'}
    if not tail['matching_known_enemy_record']['byte_identical']:raise ValueError('Observed opaque-tail duplicate differs')
    return metadata,records,tail

def write_local(path,value):
    path=local(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and json.loads(path.read_text(encoding='utf-8')).get('scope')!=SCOPE:raise ValueError('Refuse unrelated discovery output')
    temp=path.with_suffix('.json.tmp')
    with temp.open('x',encoding='utf-8') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
    temp.replace(path)

def run(recipe_path,output,summary=None):
    from verify_test_iso import verify_image
    from plan_interface_menus import audit as menu_audit
    recipe_path=recipe_path.resolve();summary=summary.resolve() if summary is not None else None;output=local(output)
    if not recipe_path.is_relative_to(ROOT/'translations') or summary is not None and (not summary.is_relative_to(ROOT/'reports') or summary.exists()):raise ValueError('Use existing project recipe and optional new metadata report')
    recipes={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in (ROOT/'translations').glob('*.json')}
    ui=json.loads(recipe_path.read_text(encoding='utf-8'));build=ROOT/'work'/recipe_path.stem;image=build/ui['iso_name']
    image_before=verify_image(image);draft,_=load_draft(ROOT/ui['base_dialogue_draft']);elf=ELF.read_bytes()
    menu_summary=menu_audit(recipe_path,ROOT/'work/planejamento-interface.json');planning=json.loads((ROOT/'work/planejamento-interface.json').read_text(encoding='utf-8'))
    with SOURCE.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        document,map_patches,map_report=compile_draft(data,draft)
        if not map_report['valid']:raise ValueError('Invalid discovery baseline')
        map_summary,map_rows=map_discovery(data,document,map_patches,map_report)
    ui_patches,ui_report=compile_ui(elf,ui);patches=map_patches+ui_patches
    elf_summary,elf_rows=elf_discovery(elf,planning,ui_patches)
    pack=(ROOT/'JOGO/Metal Saga/DATA/S/S_PACK.SDA').read_bytes();item_summary,item_rows=item_discovery(ui,elf,pack)
    title=title_discovery(elf);inventory=json.loads((ROOT/'reports/inventory.json').read_text(encoding='utf-8'))
    scanned,phrases=scan_resources(inventory,patches);atlases,atlas_rows=atlas_discovery(inventory,ui_patches)
    from discover_credits import analyse as credits_analyse
    from discover_paint import analyse as paint_analyse
    credits,credits_rows=credits_analyse(elf,(ROOT/'JOGO/Metal Saga/DATA/FDATA/FD_END.SDA').read_bytes())
    paint,paint_rows=paint_analyse(elf,(ROOT/'JOGO/Metal Saga/DATA/S/S_PAINT.SDA').read_bytes())
    engines,engine_rows=engine_variants(pack)
    locations,location_rows,opaque_tail=location_discovery(elf,pack)
    phrase_classes=phrase_triage(phrases,planning,atlas_rows)
    visual_review=[
        {'resource':'DATA/S/S_PAINT.SDA','texture_offset':0x34360,'observation':'Latin menu labels visible in decoded atlas','observed_labels':10,'editing_authorized':False},
        {'resource':'DATA/S/S_PAINT.SDA','texture_offset':0xcce0,'observation':'Three component captions visible in decoded atlas; tank category preservation applies','observed_labels':3,'editing_authorized':False},
        {'resource':'DATA/FDATA/FNP_VIEW.SDA','texture_offset':0x20,'observation':'Frame/background elements; no readable words observed in this preview','editing_authorized':False},
        {'resource':'DATA/FDATA/FNP_VIEW.SDA','texture_offset':0x10430,'observation':'Frame/background elements; no readable words observed in this preview','editing_authorized':False}]
    image_after=verify_image(image)
    if image_before!=image_after or recipes!={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in (ROOT/'translations').glob('*.json')}:raise ValueError('Discovery changed ISO/translation recipes')
    report={'schema':1,'scope':SCOPE,'recipe':recipe_path.relative_to(ROOT).as_posix(),'recipe_sha256':sha(recipe_path.read_bytes()),
        'baseline_iso':image_after,'map':map_summary,'menu_catalogue':menu_summary,'elf':elf_summary,'items':item_summary,'title':title,
        'resources':scanned,'atlases':atlases,'phrase_candidates':len(phrases),'phrase_catalogue_relations':phrase_classes,
        'credits_discovery':credits,'paint_discovery':paint,'engine_variant_discovery':engines,'font_discovery':font_discovery(),
        'location_discovery':locations,'opaque_tail_discovery':opaque_tail,
        'atlas_visual_review':visual_review,
        'phrase_candidates_outside_recipe_patches':sum(not r['authored_patch_overlap'] for r in phrases),
        'source_files_verified':len(scanned),'recipes_verified_unchanged':len(recipes),
        'originals_modified':False,'translation_created':False,'iso_created':False,'pcsx2_executed':False,
        'completeness':'Known catalogues plus bounded ASCII/recognized-atlas discovery; no complete-game coverage or edit approval'}
    write_local(output,{**report,'map_contexts':map_rows,'elf_candidates':elf_rows,'item_candidates':item_rows,'phrase_rows':phrases,'atlas_rows':atlas_rows,'credits_catalogue':credits_rows,'paint_catalogue':paint_rows,'engine_variants':engine_rows,'location_records':location_rows})
    if summary is not None:
        with summary.open('x',encoding='utf-8') as stream:json.dump(report,stream,ensure_ascii=False,indent=2);stream.write('\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description='Descoberta local consolidada, sem traduzir ou construir ISO')
    p.add_argument('--interface-draft',type=Path,default=ROOT/'translations/interface-v037.json')
    p.add_argument('--output',type=Path,default=ROOT/'work/descoberta-catalogo.json')
    p.add_argument('--summary',type=Path,help='Optional new public metadata snapshot; local catalogue is always replaceable');a=p.parse_args();r=run(a.interface_draft,a.output,a.summary)
    print(f"Descoberta: {r['source_files_verified']} arquivos verificados; {r['phrase_candidates']} candidatos por forma ASCII; tradução/ISO inalteradas.")
