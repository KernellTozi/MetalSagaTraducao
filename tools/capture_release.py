"""v063: exact contextual revision, captured UI gaps and two fixed text pools."""
import copy,json,mmap,struct,hashlib
from pathlib import Path
from dialogue import ROOT,sha
from interface_text import SOURCE as ELF,FORMAT,references,sections
from interface_resources import original
from reinsertion import SOURCE as MAP
from gfi import encode,decode as text_decode
from glyph_spacing import ORIGINAL_SHA

POLICY='captured-gaps-context-and-approved-names-v001'
PARENT_UI='translations/interface-v062.json'
PARENT_MAP='translations/regiao-inicial-v044.json'
UI='translations/interface-v063.json'
NARRATIVE='translations/regiao-inicial-v045.json'
MANIFEST='translations/capturas-v001.json'
SPACK='DATA/S/S_PACK.SDA';MCT='DATA/MAP/MAP.MCT'
PUN_ID='map.msg.0be1a0e0'
PUN='...Dis...assembler...\nte... desmonta...!\tMwahahahaha!'
OLD_PUN='...Des...montar...\nem... pedaços...!\tMwahahahaha!'
STATUS='Capturas revisadas: montagem, minerais, locais, Renascimento e Primeiro golpe.'
NAMES={190:('Scrap Armor','Colete quebrado'),336:('Revitalizer','Renascimento'),
       665:('Unknown Ore','Minério ignoto'),666:('Medium Ore','Minério médio'),
       667:('Large Ore','Minério grande')}
LOCATIONS={'Iwasaki Medical Laboratory':'Laboratório Médico Iwasaki',
           'Mysterious Transport Pod':'Estranha cápsula de transporte',
           "Grand Master's Tent":'Tenda do Grand Master',
           'Lake Bridge East Gate':'Portão leste da Ponte do Lago'}
FIXED={0x3179b0:('Sem inimigos por perto.',None),
       0x349540:('Equipar',8),
       0x341ca8:('Escolha a peça %s.',None),
       0x349ea0:('1',8),0x349ea8:('2',8),0x349eb0:('3',8),0x349eb8:('4',8)}


def plain_patch(resource,at,before,value,key):
    if not value or len(value)>=len(before) or b'\0' in value:raise ValueError('Capture field exceeds proven cell')
    return {'id':key,'resource':resource,'offset':at,'before':before,'after':value+bytes(len(before)-len(value))}


def literals(elf):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Capture original ELF differs')
    refs=references(elf,sections(elf));out=[]
    if struct.unpack_from('<4I',elf,0x2fcb38)!=tuple(at+0xff000 for at in (0x349ea0,0x349ea8,0x349eb0,0x349eb8)):
        raise ValueError('Four assembly ordinal references differ')
    for at,(text,cell) in FIXED.items():
        end=elf.index(b'\0',at);size=cell or end-at+1;before=elf[at:at+size]
        if any(elf[end:at+size]) or (cell and any(at+0xff000+i in refs for i in range(1,size))):
            raise ValueError('Capture fixed cell padding/interior reference differs')
        value=encode(text)
        if FORMAT.findall(before)!=FORMAT.findall(value):raise ValueError('Capture printf arguments differ')
        out.append(plain_patch('SLUS_212.93',at,before,value,f'capture.elf.{at:08x}'))
    at=0x342dd0;before=elf[at:at+32]
    source=b'%-20s    %8dG\nWho will learn?'
    if not before.startswith(source+b'\0') or any(before[len(source):]) or any(at+0xff000+i in refs for i in range(1,32)):
        raise ValueError('Learning prompt source/cell differs')
    value=b'%-20s    %8dG\n'+encode('Quem aprenderá?')
    if FORMAT.findall(before)!=FORMAT.findall(value):raise ValueError('Learning format changed')
    out.append(plain_patch('SLUS_212.93',at,before,value,'capture.learn.prompt'))
    return out


def names(raw):
    from item_names import catalog
    by={r['index']:r for r in catalog(raw)};out=[]
    for index,(source,text) in NAMES.items():
        row=by[index];at=row['offset'];value=encode(text);before=raw[at:at+24]
        if bytes.fromhex(row['source_hex'])!=source.encode() or any(before[row['source_bytes']:]):raise ValueError('Capture item source/tail differs')
        if len(value)>16 or text_decode(value)!=text:raise ValueError('Capture item codec/ceiling differs')
        out.append(plain_patch(SPACK,at,before,value,row['id']))
    return out


def locations(data):
    from scene_name_fields import parse
    proof=parse(data)
    if (proof['map_count'],proof['name_fields'])!=(300,839):raise ValueError('Capture scene catalogue differs')
    rows=[]
    for index in range(300):
        tree,size,blob,script=struct.unpack_from('<4I',data,0x830+16*index)
        for node in range(0x800+tree,0x800+tree+size,16):
            typ,children,identity,offset,length=struct.unpack_from('<HHIII',data,node)
            if typ not in (2,7):continue
            at=0x800+blob+offset;field=bytes(data[at:at+32]);source=field.split(b'\0')[0]
            try:key=source.decode('ascii')
            except UnicodeDecodeError:continue
            if key not in LOCATIONS:continue
            value=encode(LOCATIONS[key]);span=max(len(source),len(value))+1
            if span>32 or any(field[len(source):span]) or (typ==7 and length!=216):raise ValueError('Capture location field/layout differs')
            rows.append({'patch':plain_patch(MCT,at,field[:span],value,f'capture.map.{index:03d}.{node-0x800-tree:06x}'),
                         'node_offset':node,'node_type':typ,'node_sha256':sha(data[node:node+16]),
                         'record_sha256':sha(data[at:at+length]),'translation':LOCATIONS[key]})
    if len(rows)!=7:raise ValueError('Capture location occurrence set differs')
    return rows


def pun_spec(data):
    from build_translation_pilot import load_draft
    from dialogue_formats import parse_msg,tokens
    draft,sources=load_draft(ROOT/PARENT_MAP)
    if draft['translations'][PUN_ID]!=OLD_PUN or PUN_ID in draft.get('aliases',{}) or PUN_ID in draft.get('aliases',{}).values():raise ValueError('Pun parent/alias differs')
    at=0xbe1a0e0;parsed,opaque=parse_msg(data,at);size=parsed['size'];raw=bytes(data[at:at+size])
    old=encode(OLD_PUN);new=encode(PUN)
    if opaque or size!=88 or parsed['capacity']!=55 or len(new)>55:raise ValueError('Pun source structure/capacity differs')
    if tokens(new)[0]!=tokens(bytes.fromhex(parsed['original_text_hex']))[0]:
        # Lexer spans include positions; compare control bytes, not positions.
        from reinsertion import control_check
        control_check(bytes.fromhex(parsed['original_text_hex']),new)
    parent=raw[:32]+old+bytes(size-32-len(old));after=raw[:32]+new+bytes(size-32-len(new))
    return {'id':PUN_ID,'offset':at,'size':size,'capacity':55,'source_sha256':sha(raw),
            'parent_sha256':sha(parent),'after_sha256':sha(after),'translation':PUN,
            'parent_draft_sources':sources}


def header(parent):
    from interface_texture_pack import unpack_indices
    from interface_textures import inspect_texture
    from observed_menu_translation import header_glyphs
    from screen_followup import header_revision
    raw=original(SPACK);expected=header_revision(raw)[0]
    if parent!=expected:raise ValueError('Capture parent header differs')
    record=raw[0x8c830:0x9cc40];meta,_=inspect_texture(record);pixels=unpack_indices(record,meta)
    glyphs=header_glyphs(record)
    for char,a,z in (('Q',19,30),('P',53,64)):
        glyphs[char]=(z-a,b''.join(pixels[(180+y)*256+a:(180+y)*256+z] for y in range(10)))
    text='EQUIPAMENTOS';width=sum(glyphs[c][0] for c in text)+3*(len(text)-1)
    if width>171:raise ValueError('Equipment title exceeds native cell')
    out=bytearray(parent['after'])
    for y in range(180,192):out[y*256+4:y*256+176]=bytes([241])*172
    cursor=5
    for char in text:
        w,glyph=glyphs[char]
        for y in range(10):out[(180+y)*256+cursor:(180+y)*256+cursor+w]=glyph[y*w:(y+1)*w]
        cursor+=w+3
    return {**parent,'after':bytes(out)},{'translation':text,'width':width,'height':10,'rect':[4,180,176,192],'resized':False}


def ui_pool(parent):
    from plan_interface_menus import counted_strings
    from spack_ui import rebuild,TABLE_BASE,TABLE_SIZE,COUNT
    if (parent['resource'],parent['offset'],len(parent['after']))!=(SPACK,TABLE_BASE,TABLE_SIZE):raise ValueError('Capture UI pool differs')
    before=parent['after'];table=counted_strings(before,0,TABLE_SIZE,COUNT)
    if rebuild(before,table,{})[0]!=before:raise ValueError('Parent UI pool is not canonical/reversible')
    row=next(r for r in table['entries'] if 318 in r['pointer_ids'])
    if bytes.fromhex(row['source_hex'])!=encode('Montar itens'):raise ValueError('Assembly title parent differs')
    after,used=rebuild(before,table,{row['pointer_ids'][0]:encode('Combinar peças')})
    checked=counted_strings(after,0,TABLE_SIZE,COUNT)
    expected={tuple(r['pointer_ids']):(encode('Combinar peças') if 318 in r['pointer_ids'] else bytes.fromhex(r['source_hex'])) for r in table['entries']}
    if {tuple(r['pointer_ids']):bytes.fromhex(r['source_hex']) for r in checked['entries']}!=expected:raise ValueError('Capture UI aliases/text changed')
    return {**parent,'after':after},{'canonical_id':row['pointer_ids'][0],'translation':'Combinar peças','used_bytes':used,'other_strings_preserved':True}


def reaction_pool(parent):
    from spack_interactions import catalog,rebuild,REACTION_BASE,REACTION_SIZE
    raw=original(SPACK);source=catalog(raw,'reaction')
    if (parent['offset'],len(parent['after']))!=(REACTION_BASE,REACTION_SIZE):raise ValueError('Capture reaction extent differs')
    original_row=next(r for r in source['rows'] if r['id']=='reaction.0203a')
    current=bytearray(raw);current[REACTION_BASE:REACTION_BASE+REACTION_SIZE]=parent['after'];table=catalog(current,'reaction')
    row=next(r for r in table['rows'] if r['references']==original_row['references'])
    old=encode('1. Evil Toy Sword  2. Revigorante|3. ?  4. ?')
    new=encode('1. Evil Toy Sword  2. Renascimento|3. ?  4. ?')
    if bytes.fromhex(row['source_hex'])!=old:raise ValueError('Revitalizer reaction parent differs')
    table['pool_end']=source['pool_end']
    baseline,_=rebuild(current,table,{})
    if baseline!=parent['after']:raise ValueError('Parent reaction pool is not canonical/reversible')
    after,used=rebuild(current,table,{row['id']:new});current[REACTION_BASE:REACTION_BASE+REACTION_SIZE]=after
    readback=catalog(current,'reaction')
    expect={tuple(r['references']):(new if r['id']==row['id'] else bytes.fromhex(r['source_hex'])) for r in table['rows']}
    if {tuple(r['references']):bytes.fromhex(r['source_hex']) for r in readback['rows']}!=expect:raise ValueError('Reaction text/aliases changed')
    if after[source['pool_end']:]!=parent['after'][source['pool_end']:]:raise ValueError('Reaction opaque tail changed')
    return {**parent,'after':after},{'logical_references':row['references'],'used_bytes':used,'text_limit':source['pool_end'],'opaque_tail_preserved':True,'other_strings_preserved':True}


def strike(elf):
    from battle_menu_atlas import RESOURCE,tim2,_recompress
    from battle_effect_atlas import ink_bounds,word_mask,FONT
    from discover_credits import decode,execute_decoder_loop
    from interface_texture_pack import pillow
    Image=pillow()
    from PIL import ImageFilter
    inv=next(r for r in json.loads((ROOT/'reports/inventory.json').read_bytes()) if r['path']==RESOURCE)
    with (ROOT/'JOGO/Metal Saga'/RESOURCE).open('rb') as f:
        if hashlib.file_digest(f,'sha256').hexdigest()!=inv['sha256']:raise ValueError('Strike original resource differs')
        f.seek(0);directory=f.read(0x3400);size,at=struct.unpack_from('<II',directory,1586*8);f.seek(at);slot=f.read(size)
    if struct.unpack_from('<I',elf,0x1090e0)[0]!=0x24020632:raise ValueError('Strike original atlas selector differs')
    raw,used,_=decode(slot,maximum=66624)
    if any(slot[used:]):raise ValueError('Strike compressed tail is opaque')
    pixels,pal=tim2(raw);out=bytearray(pixels);bg=next(i for i,p in enumerate(pal) if p[3]==0);labels=[]
    colors={v:min((i for i,p in enumerate(pal) if p[3]==128),key=lambda i:sum((pal[i][k]-v)**2 for k in range(3))) for v in (0,85,170,255)}
    for cell in ((27,200,125,220),(127,200,225,220)):
        x,y,z,w=ink_bounds(pixels,pal,cell);mask,layout=word_mask('Primeiro golpe',z-x,w-y);outline=mask.filter(ImageFilter.MaxFilter(3))
        for yy in range(w-y):
            for xx in range(z-x):
                v=mask.getpixel((xx,yy));out[(y+yy)*256+x+xx]=bg if outline.getpixel((xx,yy))<48 else colors[round(v/85)*85]
        labels.append({'translation':'Primeiro golpe','rect':[x,y,z,w],**layout})
    after=raw[:64]+bytes(out)+raw[65600:];packed=_recompress(after)
    if len(packed)>len(slot):raise ValueError('Strike compressed slot overflow')
    actual,consumed,steps=execute_decoder_loop(elf,packed,maximum=66624)
    if actual!=after or consumed!=len(packed):raise ValueError('Native strike decompression differs')
    p={'id':'capture.battle.first-strike','resource':RESOURCE,'offset':at,'before':slot,'after':packed+bytes(len(slot)-len(packed))}
    return p,{'index':1586,'source_sha256':inv['sha256'],'directory_sha256':sha(directory),'slot_size':len(slot),'packed_bytes':len(packed),
              'font_sha256':sha(FONT.read_bytes()),'labels':labels,'native_decoder_steps':steps,'palettes_headers_unchanged':True,'decoded_sha256':sha(after)}


def derive(elf,parents):
    raw=original(SPACK);byid={p['id']:p for p in parents};byat={(p['resource'],p['offset']):p for p in parents}
    new=[];revised=[];evidence={}
    for p in literals(elf)+names(raw):
        old=byat.get((p['resource'],p['offset']))
        if old:
            if p['id'].startswith('capture.elf.'):
                if old['id']!='elf.ui.00341ca8':raise ValueError('Unreviewed capture literal revision')
                p['id']=old['id']
            elif p['id'] not in ('item.name.0190','item.name.0336'):raise ValueError('Unreviewed capture item revision')
            if p['before'][:len(old['before'])]!=old['before']:raise ValueError('Capture revision source differs')
            revised.append(p)
        else:new.append(p)
    inv=next(r for r in json.loads((ROOT/'reports/inventory.json').read_bytes()) if r['path']==MCT)
    with MAP.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
        if sha(data)!=inv['sha256']:raise ValueError('Capture original MAP differs')
        loc=locations(data);evidence['locations']=[{k:v for k,v in r.items() if k!='patch'} for r in loc]
        new.extend(r['patch'] for r in loc);evidence['pun']=pun_spec(data)
    for name,fn in (('observed.headers',header),('spack.ui.table',ui_pool),('spack.reaction.pool',reaction_pool)):
        p,row=fn(byid[name]);revised.append(p);evidence[name]=row
    p,row=strike(elf);new.append(p);evidence['strike']=row
    evidence['source_hashes']={'elf':ORIGINAL_SHA,'spack':sha(raw),'map':inv['sha256']}
    return new,revised,evidence


def patch_meta(p):
    return {'id':p['id'],'resource':p['resource'],'offset':p['offset'],'size':len(p['before']),
            'source_sha256':sha(p['before']),'after_sha256':sha(p['after'])}


def template(elf,parents):
    new,rev,evidence=derive(elf,parents)
    return {'schema':1,'policy':POLICY,'parent_ui':PARENT_UI,'parent_ui_sha256':sha((ROOT/PARENT_UI).read_bytes()),
            'parent_map':PARENT_MAP,'parent_map_sha256':sha((ROOT/PARENT_MAP).read_bytes()),
            'new':[patch_meta(p) for p in new],'revised':[patch_meta(p) for p in rev],'evidence':evidence}


def binding_load(binding):
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:raise ValueError('Unknown capture binding')
    raw=(ROOT/MANIFEST).read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('Capture manifest differs')
    m=json.loads(raw)
    if m['policy']!=POLICY or m['parent_ui']!=PARENT_UI or m['parent_map']!=PARENT_MAP or m['parent_ui_sha256']!=sha((ROOT/PARENT_UI).read_bytes()) or m['parent_map_sha256']!=sha((ROOT/PARENT_MAP).read_bytes()):raise ValueError('Capture parents differ')
    return m


def validate_interface(recipe):
    m=binding_load(recipe['capture_release']);parent=json.loads((ROOT/PARENT_UI).read_bytes());expected=copy.deepcopy(parent)
    expected.update(capture_release=recipe['capture_release'],base_dialogue_draft=NARRATIVE,iso_name='MetalSaga-ptbr-interface-v063.iso',status=STATUS)
    if expected!=recipe:raise ValueError('Unrelated capture UI mutation')
    return parent,m


def compile_interface(elf,recipe):
    from interface_text import compile_draft
    parent,m=validate_interface(recipe);parents,report=compile_draft(elf,parent)
    if template(elf,parents)!=m:raise ValueError('Capture output/evidence differs')
    new,rev,evidence=derive(elf,parents);revisions={p['id']:p for p in rev};out=[revisions.get(p['id'],p) for p in parents]
    for p in new:
        if any(p['resource']==q['resource'] and max(p['offset'],q['offset'])<min(p['offset']+len(p['before']),q['offset']+len(q['before'])) for q in out):raise ValueError('Capture addition overlaps parent')
        out.append(p)
    report=copy.deepcopy(report);report['accepted']+=len(new)+2
    report['item_names']['accepted']+=3
    for idx in (665,666,667):report['item_names']['results'].append({'id':f'item.name.{idx:04d}','index':idx,'target_bytes':len(encode(NAMES[idx][1])),'group':'user-requested-ore'})
    current={p['id']:p for p in out};report['item_names']['unique_translated_labels']=len({current[r['id']]['after'].split(b'\0')[0] for r in report['item_names']['results']})
    for row in report['item_names']['results']:
        if row['id'] in ('item.name.0190','item.name.0336'):row['target_bytes']=len(current[row['id']]['after'].split(b'\0')[0])
    for row in report['results']:
        if row['id']=='elf.ui.00341ca8':
            value=current[row['id']]['after'].split(b'\0')[0];row.update(target_bytes=len(value),target_sha256=sha(value))
    from plan_interface_menus import counted_strings
    from spack_ui import TABLE_BASE,TABLE_SIZE,COUNT
    table=current['spack.ui.table']['after'];parsed=counted_strings(table,0,TABLE_SIZE,COUNT)
    logical={i:r for r in parsed['entries'] for i in r['pointer_ids']}
    for row in report['spack_ui']['results']:
        r=logical[row['pointer_ids'][0]];value=bytes.fromhex(r['source_hex'])
        row.update(new_offset=TABLE_BASE+r['offset'],target_length=len(value),target_sha256=sha(value))
    used=evidence['spack.ui.table']['used_bytes']
    report['spack_ui'].update(table_sha256=sha(table),used_bytes=used,free_bytes=TABLE_SIZE-used)
    report['spack_interactions']['tables']['reaction']['used_bytes']=evidence['spack.reaction.pool']['used_bytes']
    for row in report['spack_interactions']['results']:
        if row['id']=='reaction.0203a':row['target_bytes']=len(encode('1. Evil Toy Sword  2. Renascimento|3. ?  4. ?'))
    report['capture_release']={'policy':POLICY,'new_units':len(new)+2,'new_item_names':3,'new_map_labels':len(evidence['locations']),
                               'revised_items':2,'revised_reaction_references':1,'revised_dialogue_bodies':1,
                               'first_strike_variants':2,'pcsx2_executed':False,'visual_status':'pending_user'}
    return out,report


def validate_narrative(draft):
    from build_translation_pilot import load_draft
    m=binding_load(draft['capture_context_review']);expected,_=load_draft(ROOT/PARENT_MAP)
    expected['translations'][PUN_ID]=PUN
    expected.update(capture_context_review=draft['capture_context_review'],name='regiao-inicial-v045',status=STATUS,reviewed_changes=[PUN_ID])
    if expected!=draft:raise ValueError('Unrelated capture narrative mutation')
    return m


def compile_narrative(data,draft):
    from build_translation_pilot import load_draft,compile_draft
    from reinsertion import compile_entry
    m=validate_narrative(draft);parent,_=load_draft(ROOT/PARENT_MAP);doc,patches,report=compile_draft(data,parent)
    spec=pun_spec(data)
    if spec!=m['evidence']['pun']:raise ValueError('Capture dialogue proof differs')
    entry=next(e for e in doc['entries'] if e['id']==PUN_ID);previous=next(p for p in patches if p['id']==PUN_ID)
    if sha(previous['after'])!=spec['parent_sha256'] or len(entry['segments'])!=1 or entry['blocked_reasons'] or entry['mode']!='slots':raise ValueError('Capture dialogue parent differs')
    check=copy.deepcopy(entry);check['segments'][0]['translation']=PUN
    p,info=compile_entry(data,check,check,quirk_refs=True)
    if p is None or sha(p['after'])!=spec['after_sha256']:raise ValueError('Capture dialogue compiler differs')
    entry['segments'][0]['translation']=PUN;report=copy.deepcopy(report)
    for r in report['results']:
        if r['id']==PUN_ID:r.update(target_lengths=[len(encode(PUN))],warnings=info['warnings'])
    report['capture_context_review']={'policy':POLICY,'revised_bodies':1,'warnings':info['warnings'],'pcsx2_executed':False}
    return doc,[p if q['id']==PUN_ID else q for q in patches],report


def normalize_prefix(old,new):
    raw=original(SPACK)
    for key,p in list(new.items()):
        if p['id']!='item.name.0336':continue
        q=old[key];n=max(len(p['before']),len(q['before']));before=raw[p['offset']:p['offset']+n]
        if n!=24 or p['before']!=before or q['before']!=before[:len(q['before'])]:raise ValueError('Revitalizer prefix comparison differs')
        old[key]={**q,'before':before,'after':q['after']+before[len(q['after']):]}


def prepare():
    from interface_text import compile_draft
    elf=ELF.read_bytes();parent=json.loads((ROOT/PARENT_UI).read_bytes());patches,report=compile_draft(elf,parent)
    m=template(elf,patches);raw=(json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode();(ROOT/MANIFEST).write_bytes(raw)
    binding={'recipe':MANIFEST,'sha256':sha(raw)}
    child=copy.deepcopy(parent);child.update(capture_release=binding,base_dialogue_draft=NARRATIVE,iso_name='MetalSaga-ptbr-interface-v063.iso',status=STATUS)
    (ROOT/UI).write_bytes((json.dumps(child,ensure_ascii=False,indent=2)+'\n').encode())
    narrative={'schema':1,'extends':Path(PARENT_MAP).name,'name':'regiao-inicial-v045','status':STATUS,
               'translations':{PUN_ID:PUN},'reviewed_changes':[PUN_ID],'capture_context_review':binding}
    (ROOT/NARRATIVE).write_bytes((json.dumps(narrative,ensure_ascii=False,indent=2)+'\n').encode())
    validate_interface(child)
    from build_translation_pilot import load_draft
    validate_narrative(load_draft(ROOT/NARRATIVE)[0])
    return {'new_physical_patches':len(m['new']),'revised_ui_patches':len(m['revised']),'new_units':len(m['new'])+2,'revised_dialogue':1}


def previews():
    from interface_texture_pack import pillow
    from interface_textures import inspect_texture
    from screen_followup import header_revision
    from battle_menu_atlas import tim2
    from discover_credits import decode
    Image=pillow()
    from PIL import ImageDraw
    folder=ROOT/'work/interface-v063-previews';folder.mkdir(exist_ok=True)
    raw=original(SPACK);parent=header_revision(raw)[0];p,_=header(parent)
    changed=bytearray(raw);changed[p['offset']:p['offset']+len(p['after'])]=p['after']
    canvas=Image.new('RGB',(1060,76),(30,30,30));draw=ImageDraw.Draw(canvas)
    for column,source in enumerate((raw,changed)):
        _,rgb=inspect_texture(source[0x8c830:0x9cc40])
        crop=Image.frombytes('RGB',(256,256),rgb).crop((4,180,176,192))
        draw.text((column*530+5,3),'Original' if column==0 else 'PT-BR',fill='white')
        canvas.paste(crop.resize((516,36),Image.Resampling.NEAREST),(column*530+5,25))
    canvas.save(folder/'equipamentos.png')
    p,evidence=strike(ELF.read_bytes())
    canvas=Image.new('RGB',(640,172),(30,30,30));draw=ImageDraw.Draw(canvas)
    for column,blob in enumerate((p['before'],p['after'])):
        decoded,_,_=decode(blob,maximum=66624);pixels,palette=tim2(decoded)
        rgba=bytes(v for i in pixels for v in (*palette[i][:3],min(255,palette[i][3]*2)))
        image=Image.frombytes('RGBA',(256,256),rgba)
        draw.text((column*320+5,3),'Original' if column==0 else 'PT-BR',fill='white')
        for row,rect in enumerate(((27,200,125,220),(127,200,225,220))):
            crop=image.crop(rect).resize((294,60),Image.Resampling.NEAREST)
            canvas.paste(crop,(column*320+5,25+row*70),crop)
    canvas.save(folder/'primeiro-golpe.png')
    return {'previews':folder.relative_to(ROOT).as_posix(),'gpu_render':False}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description='Preparar lote contextual ou comparações locais, sem alterar ISO')
    parser.add_argument('--previews',action='store_true')
    args=parser.parse_args()
    print(json.dumps(previews() if args.previews else prepare()))
