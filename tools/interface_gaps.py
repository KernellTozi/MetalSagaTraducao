"""Narrow opt-in for a proven name-entry exit and four generic destinations."""
import copy,json,struct
from reinsertion import ROOT
from dialogue import sha
from glyph_spacing import ORIGINAL_SHA
from gfi import encode,decode

POLICY='small-interface-title-exit-and-generic-destinations-v001'
TITLE_POLICY='name-entry-title-exit-reviewed-v003'
LOCATION_POLICY='four-generic-destinations-existing-records-v001'
DESTINATIONS={14:'Pte. do lago L',16:'Ilha O',22:'Lab. médico',23:'Cáp. transp.'}
RESOURCE='DATA/S/S_PACK.SDA'
TITLE_WINDOWS=((0x10bf94,0x10bfac),(0x10bfc8,0x10bfd8),(0x10d650,0x10d668),
               (0x10d684,0x10d688),(0x10d6cc,0x10d6d0))
LOCATION_WINDOWS=((0x6ce70,0x6ce80),(0x11f35c,0x11f384),(0x11f3b0,0x11f3c8),
                  (0x1101a4,0x1101d8),(0x3f800,0x3f818))

def windows(elf,ranges):return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in ranges]

def title_proof(elf):
    from discover_remaining_catalogue import title_discovery
    from speaker_labels import _run
    legacy=title_discovery(elf)
    # Execute the original state-4 wrapper as far as the handler entry.
    r=[0]*32;r[16]=0x620000
    r=_run(elf,0x10d650,TITLE_WINDOWS,r,[],0x10bf18)
    if (r[4],r[31])!=(0x620000,0x10d658):raise ValueError('Name exit dispatch differs')
    memory=bytearray(0x31c0);struct.pack_into('<I',memory,0x3038,1)
    struct.pack_into('<I',memory,0x303c,0x12345678);struct.pack_into('<I',memory,0x88,1)
    before=bytes(memory);r=[0]*32;r[16]=0x620000
    _run(elf,0x10bf94,(*TITLE_WINDOWS,(0x10bfd4,0x10bfd8)),r,[(0x620000,memory)],0x10bfd8)
    if struct.unpack_from('<I',memory,0x303c)[0]!=0 or struct.unpack_from('<I',memory,0x88)[0]!=2:
        raise ValueError('Name exit does not clear commit flag/advance')
    if any(a!=b for i,(a,b) in enumerate(zip(before,memory)) if i not in set(range(0x88,0x8c))|set(range(0x303c,0x3040))):
        raise ValueError('Name exit changed other fields')
    cases=[]
    for condition in (0,1,65535):
        struct.pack_into('<H',memory,0x9e,condition);r=[0]*32;r[16]=0x620000
        r=_run(elf,0x10bfc8,TITLE_WINDOWS,r,[(0x620000,memory)],0x10bfd8)
        expected=int(condition==0)
        if r[2]!=expected:raise ValueError('Name exit terminal branch differs')
        # +303c=0 bypasses both committing calls, reaches the common update.
        r=_run(elf,0x10d658,TITLE_WINDOWS,r,[(0x620000,memory)],0x10d688)
        r=_run(elf,0x10d6cc,TITLE_WINDOWS,r,[],0x10d6d0)
        if r[2]!=expected:raise ValueError('Name exit completion not propagated')
        cases.append({'fade_field_9e':condition,'completion':expected,'name_commit_skipped':True})
    return {'policy':TITLE_POLICY,'instruction_windows':windows(elf,TITLE_WINDOWS),
        'legacy_request_evidence':legacy,'terminal_and_dispatch_cases':cases,'translation':'SAIR',
        'meaning':'Exit the name-entry operation without committing the name on the TITLE path.',
        'limits':'Original bounded integer paths in synthetic RAM. Fade setup, object update callbacks, external owner/destination, controller, GPU and PS2 not executed. Does not claim return-to-title destination.'}

def location_proof(elf,raw):
    from discover_remaining_catalogue import location_discovery
    from speaker_labels import _run
    meta,rows,_=location_discovery(elf,raw)
    if meta['maximum_original_name_bytes']!=14:raise ValueError('Destination observed ceiling differs')
    if struct.unpack_from('<I',elf,0x1101d0)[0]!=0x0c0c95b3:raise ValueError('Destination strlen call differs')
    cases=[]
    for row in rows:
        r=[0]*32;r[2]=0x630000;r[18]=0x600000+row['relative_offset']
        result=_run(elf,0x11f3b0,LOCATION_WINDOWS,r,[],0x110198)
        if (result[4],result[5],result[6],result[7],result[8])!=(0x630000,0x600000+row['relative_offset'],22,0,0):
            raise ValueError('Destination name forwarding differs')
        cases.append({'index':row['pointer_ids'][0],'name_offset':row['offset'],'font_size':22})
    return {'policy':LOCATION_POLICY,'table':meta,'instruction_windows':windows(elf,LOCATION_WINDOWS),
        'forwarding_cases':cases,'maximum_target_bytes':14,'name_field_bytes':32,
        'limits':'Original selection/forwarding integer windows; same observed 14-byte ceiling. No full text constructor, unlock/coordinate mutation, all-consumer census, GPU or PS2 execution.'}

def compile_locations(elf,config):
    from item_descriptions import original
    from discover_remaining_catalogue import location_discovery
    from spack_ui import execute_byte_length
    from translation_policy import validate
    raw=original(RESOURCE)
    if sha(elf)!=ORIGINAL_SHA or config['source_sha256']!=sha(raw) or config['evidence']!=location_proof(elf,raw):
        raise ValueError('Destination source/consumer proof differs')
    if config['policy']!=LOCATION_POLICY or [(r['index'],r['translation']) for r in config['entries']]!=list(DESTINATIONS.items()):
        raise ValueError('Destination editorial scope differs')
    _,rows,_=location_discovery(elf,raw);by={r['pointer_ids'][0]:r for r in rows};patches=[]
    for target in config['entries']:
        row=by[target['index']]
        if any(target[k]!=row[k] for k in ('id','record_sha256','source_sha256')):raise ValueError('Destination record differs')
        value=encode(target['translation']);source=bytes.fromhex(row['source_hex']).decode()
        if not 1<=len(value)<=14 or decode(value)!=target['translation'] or any(c in value for c in (0,9,10,13,37,124)):
            raise ValueError('Destination codec/ceiling differs')
        if validate(source,target['translation']):raise ValueError('Protected destination name')
        if execute_byte_length(elf,value)!=len(value):raise ValueError('Destination original byte count differs')
        at=row['offset'];before=raw[at:at+32];after=value+bytes(32-len(value))
        patches.append({'id':row['id'],'resource':RESOURCE,'offset':at,'before':before,'after':after})
    return patches,{'policy':LOCATION_POLICY,'accepted':4,'catalog_records':25,'preserved_records':21,
        'same_record_name_slots':True,'pointer_table_flags_coordinates_and_tails_unchanged':True,
        'source_evidence':config['evidence'],'runtime_visual_status':'pending_user_verification'}

def width_proof(elf,raw):
    from functools import lru_cache
    from glyph_layout import elf_patch
    from layout_probe import execute
    from discover_remaining_catalogue import location_discovery
    _,rows,_=location_discovery(elf,raw);patch=elf_patch(elf)
    @lru_cache(maxsize=None)
    def advance(char,side,mode):
        value=encode(char);r=execute(elf,patch['after'],value,side,mode)
        if r['consumed']!=len(value) or not r['callee_saved']:raise ValueError('Interface width probe differs')
        return r['metrics'][3]
    def width(text,side,mode):return sum(advance(c,side,mode) for c in text)
    cases=[]
    for mode in (0,1,2):
        maximum=max(width(bytes.fromhex(r['source_hex']).decode(),22,mode) for r in rows)
        for index,text in DESTINATIONS.items():
            target=width(text,22,mode)
            cases.append({'index':index,'side':22,'mode':mode,'advance':target,'original_maximum':maximum,
                          'within_original_envelope':target<=maximum})
    title=[]
    for side in (22,26):
        for mode in (0,1,2):
            old=width('TITLE',side,mode);new=width('SAIR',side,mode)
            title.append({'side':side,'mode':mode,'before_advance':old,'after_advance':new,'not_wider':new<=old})
    return {'destination_cases':cases,'title_cases':title,'unique_glyph_probes':advance.cache_info().currsize,
        'limits':'Sum of advances using existing layout-v005 metrics. Not a real menu clip/line-height/GPU/PCSX2 test.'}

def load(binding):
    if set(binding)!={'recipe','sha256'}:raise ValueError('Unknown interface gap binding')
    path=(ROOT/binding['recipe']).resolve()
    if not path.is_relative_to(ROOT/'translations'):raise ValueError('Interface gap manifest outside translations')
    raw=path.read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('Interface gap manifest changed')
    m=json.loads(raw)
    if m.get('policy')!=POLICY or m.get('parent_recipe')!='translations/interface-v045.json':raise ValueError('Interface gap parent/policy differs')
    raw=(ROOT/m['parent_recipe']).read_bytes()
    if sha(raw)!=m['parent_recipe_sha256']:raise ValueError('Interface gap parent changed')
    return m,json.loads(raw)

def expected_interface(binding):
    m,parent=load(binding);result=copy.deepcopy(parent)
    result['generic_destination_names']=m['destinations']
    result['name_entry']['policy']=TITLE_POLICY;result['name_entry']['title_evidence']=m['title_evidence']
    matches=0
    for row in result['name_entry']['entries']:
        for slot in row.get('slots',[]):
            if slot['translation']=='TITLE':slot['translation']='SAIR';matches+=1
    if matches!=1:raise ValueError('Expected one exact TITLE slot')
    result.update(interface_gap_review=binding,iso_name='MetalSaga-ptbr-interface-v046.iso',
                  status='Lacunas de interface: saída da nomeação e quatro destinos genéricos; demais recursos preservados.')
    return result

def validate_interface(recipe):
    if recipe!=expected_interface(recipe['interface_gap_review']):raise ValueError('Non-authorized interface gap change')
