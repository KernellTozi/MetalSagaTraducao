"""Bounded v070 fixes reported by the user; preserves source structures."""
import copy,json,mmap,re,struct
from pathlib import Path
from collections import Counter
from dialogue import ROOT,sha
from gfi import encode
from interface_graphics import original
from interface_text import SOURCE as ELF,references,sections,FORMAT
from reinsertion import SOURCE as MAP
from interface_texture_pack import pillow,unpack_indices
from interface_textures import inspect_texture
from tank_drinking_gaps import display_palette,metadata
import category_pool

POLICY='reported-final-candidate-fixed-resources-v001'
PARENT='translations/interface-v069.json';CHILD='translations/interface-v070.json'
PARENT_MAP='translations/regiao-inicial-v047.json';CHILD_MAP='translations/regiao-inicial-v048.json'
MANIFEST='translations/candidata-final-v001.json'
FOLDER=ROOT/'work/final-v070'
SPACK='DATA/S/S_PACK.SDA';HMAP='DATA/MAP/HMAPAC.SDA';DIARY='DATA/FDATA/DIARY.DAT'
FONT=Path('C:/Windows/Fonts/arialbd.ttf')
ICON_FONT=Path('C:/Windows/Fonts/ariblk.ttf')
STATUS='Candidata final: relatos, categorias e revisão contextual; visual pendente.'
LOCATIONS={'Unknown Cave':'Caverna desconhecida','Trader Camp':'Acampamento de mercadores'}
NARRATIVE={
 'map.msg.040f10d4':'V-Você só pode\nestar brincando...\nNãããão!',
 'map.msg.01dee21c':'*gasp* Eddyyyyyyyyy!!\tV-Você... Meu Deus...\nNãããão!!',
}
LITERALS={0x341670:('%%I%02d%s\nSell price%11dG','%%I%02d%s\nVenda     %11dG',None),
          0x349a18:('Yes','Sim',8),0x349a20:('No','Não',8)}
WINDOWS=((0x1d5b80,0x1d5be0),(0x14c4f8,0x14c534))


def literal_patches(elf):
    refs=references(elf,sections(elf));patches=[]
    for at,(source,target,cell) in LITERALS.items():
        raw=source.encode();size=cell or len(raw)+1;before=elf[at:at+size];value=encode(target)
        if before!=raw+bytes(size-len(raw)) or len(value)>=size:
            raise ValueError('Final literal source/capacity differs')
        if any(refs.get(at+0xff000+i) for i in range(1,size)):
            raise ValueError('Final literal has interior references')
        if not refs.get(at+0xff000) and at!=0x349a18:
            raise ValueError('Final literal lacks a consumer')
        if FORMAT.findall(raw)!=FORMAT.findall(value) or raw.count(b'\n')!=value.count(b'\n'):
            raise ValueError('Final format controls changed')
        patches.append({'id':f'final.elf.{at:08x}','resource':'SLUS_212.93','offset':at,
                        'before':before,'after':value+bytes(size-len(value))})
    # Alternate Yes/No addresses passed as a2/a3 to the same constructor.
    expected={0x14c500:0x3c060045,0x14c518:0x3c070045,0x14c51c:0x24c68a18,
              0x14c520:0x24e78a20,0x14c52c:0x0c06ea96}
    for at,word in expected.items():
        if struct.unpack_from('<I',elf,at)[0]!=word:raise ValueError('Alternate choice call path differs')
    return patches


def diary_patch():
    from diary import fields
    from interface_resources import tokens
    raw=original(DIARY);row=next(f for f in fields(raw) if f['record']==16 and f['field']=='body')
    at=row['offset'];before=raw[at:at+row['capacity']+1];source=before.split(b'\0')[0]
    text='MC… sei lá o quê... Será|que é o MC Hamir?'
    value=b'\x81\x63'.join(encode(s) for s in text.split('…'))
    if source.count(b'\x81\x63')!=1 or any(c>=128 for c in source.replace(b'\x81\x63',b'')):
        raise ValueError('Binramen native character inventory differs')
    if tokens(source,True)!=tokens(value,True) or value.count(b'|')!=source.count(b'|') or len(value)>row['capacity']:
        raise ValueError('Binramen fixed slot/controls changed')
    return {'id':'final.diary.016.body','resource':DIARY,'offset':at,'before':before,
            'after':value+bytes(len(before)-len(value))}


def locations(data):
    from scene_name_fields import parse
    proof=parse(data)
    if (proof['map_count'],proof['name_fields'])!=(300,839):raise ValueError('Scene catalogue differs')
    rows=[];patches=[]
    for index in range(300):
        tree,size,blob,script=struct.unpack_from('<4I',data,0x830+index*16)
        for node in range(0x800+tree,0x800+tree+size,16):
            typ,children,identity,off,length=struct.unpack_from('<HHIII',data,node)
            if typ not in (2,7):continue
            at=0x800+blob+off;field=bytes(data[at:at+32]);source=field.split(b'\0')[0].decode('ascii',errors='replace')
            if source not in LOCATIONS:continue
            target=encode(LOCATIONS[source]);span=max(len(source),len(target))+1
            if span>32 or any(field[len(source):]) or (typ==7 and length!=216):raise ValueError('Final scene name bounds differ')
            patches.append({'id':f'final.map.{at:08x}','resource':'DATA/MAP/MAP.MCT',
                            'offset':at,'before':field[:span],'after':target+bytes(span-len(target))})
            rows.append({'map':index,'type':typ,'node_offset':node,'node_sha256':sha(data[node:node+16]),
                         'field_offset':at,'translation':LOCATIONS[source]})
    if len(rows)!=18:raise ValueError('Final location census differs')
    return patches,rows


def headers(parent):
    from observed_menu_translation import header_glyphs
    raw=original(SPACK);record=raw[0x8c830:0x9cc40];meta,_=inspect_texture(record)
    glyphs=header_glyphs(record);out=bytearray(parent['after']);rows=[]
    pixels=unpack_indices(record,meta)
    # U from EQUIPMENT LIST; J keeps U's lower hook and right-hand stem.
    columns=[]
    for x in range(4,180):
        if any(pixels[(180+y)*256+x]==253 for y in range(10)):
            if not columns or x>columns[-1][-1]+1:columns.append([x])
            else:columns[-1].append(x)
    if len(columns)!=13:raise ValueError('Equipment native glyph census differs')
    cols=columns[2];a,z=cols[0],cols[-1]+1;w=z-a
    u=b''.join(pixels[(180+y)*256+a:(180+y)*256+z] for y in range(10))
    j=bytearray(u)
    for y in range(7):j[y*w:y*w+w//2]=bytes([241])*(w//2)
    glyphs['J']=(w,bytes(j))
    for left,top,right,bottom,text in ((4,60,62,72,'NOME'),(4,216,156,228,'AJUSTES')):
        width=sum(glyphs[c][0] for c in text)+3*(len(text)-1)
        if width>right-left-2:raise ValueError('Native final header overflow')
        for y in range(top,bottom):out[y*256+left:y*256+right]=bytes([241])*(right-left)
        x=left+1
        for c in text:
            w,glyph=glyphs[c]
            for y in range(10):out[(top+y)*256+x:(top+y)*256+x+w]=glyph[y*w:(y+1)*w]
            x+=w+3
        rows.append({'rect':[left,top,right,bottom],'text':text,'width':width})
    patch={**parent,'after':bytes(out)}
    return patch,rows


def transport_icons(parent,previews=False):
    Image=pillow()
    from PIL import ImageDraw,ImageFont,ImageFilter
    raw=original(HMAP);record=raw[0x80:];meta,_=inspect_texture(record);palette=display_palette(record)
    original_pixels=unpack_indices(record,meta);canvas=Image.frombytes('L',(256,256),original_pixels)
    grayscale=[i for i,p in enumerate(palette) if p[3]==127 and len(set(p[:3]))==1]
    black=[i for i,c in enumerate(palette) if c[:3]==(0,0,0)]
    fade={}
    for x in range(90,192):
        samples=[original_pixels[y*256+x] for y in (*range(45,70),*range(119,144))
                 if palette[original_pixels[y*256+x]][:3]==(0,0,0)]
        opaque=[i for i in samples if palette[i][3]>0]
        if samples:fade[x]=Counter(opaque or samples).most_common(1)[0][0]
    for x in range(90,192):
        if x in fade:continue
        left=max(k for k in fade if k<x);right=min(k for k in fade if k>x)
        alpha=palette[fade[left]][3]+(palette[fade[right]][3]-palette[fade[left]][3])*(x-left)/(right-left)
        fade[x]=min(black,key=lambda i:abs(palette[i][3]-alpha))
    proofs=[]
    for index,top,bottom,sample,text in ((0,44,70,68,'Sem tanques'),(2,118,144,140,'Sem navios')):
        sprite=raw[0x10510+16*index:0x10520+16*index]
        if struct.unpack('<8h',sprite)[:4]!=(4,4 if index==0 else 78,196,70 if index==0 else 144):
            raise ValueError('Transport sprite source differs')
        rect=(90,top,192,bottom)
        # Both original labels share a column-constant black alpha fade.
        # Recover its mode only from black background pixels, excluding glyph ink.
        for x in range(90,192):
            i=fade[x]
            for y in range(top,bottom):canvas.putpixel((x,y),i if y>top else 0)
        point=16
        while True:
            font=ImageFont.truetype(str(ICON_FONT),point);box=font.getbbox(text,stroke_width=0)
            mask=Image.new('L',(box[2]-box[0]+2,box[3]-box[1]+2))
            ImageDraw.Draw(mask).text((1-box[0],1-box[1]),text,font=font,fill=255,stroke_width=0)
            if mask.width+2<=102 and mask.height+2<=26:break
            point-=1
            if point<12:raise ValueError('Transport word would be too small')
        outline=mask.filter(ImageFilter.MaxFilter(3));x0=90+(102-mask.width)//2;y0=top+(26-mask.height)//2
        for y in range(mask.height):
            for x in range(mask.width):
                ink=mask.getpixel((x,y));edge=outline.getpixel((x,y))
                if edge<48:continue
                shade=35+round(220*ink/255)
                canvas.putpixel((x0+x,y0+y),min(grayscale,key=lambda i:abs(palette[i][0]-shade)))
        proofs.append({'text':text,'rect':list(rect),'fade_source':'original black column mode, two label regions','point_size':point,
                       'glyph_dilation_pixels':0,'sprite_sha256':sha(sprite),'mask_sha256':sha(mask.tobytes())})
    patch={**parent,'after':canvas.tobytes()}
    if previews:
        FOLDER.mkdir(parents=True,exist_ok=True)
        bg=(100,115,90);board=Image.new('RGB',(1152,460),(25,25,25))
        for col,pixels in enumerate((original_pixels,parent['after'],patch['after'])):
            rgba=Image.frombytes('RGBA',(256,256),bytes(v for i in pixels for v in (*palette[i][:3],min(255,palette[i][3]*2))))
            image=Image.new('RGBA',(256,256),(*bg,255));image.alpha_composite(rgba)
            crop=image.crop((4,4,196,144)).resize((384,280),Image.Resampling.NEAREST)
            board.paste(crop.convert('RGB'),(col*384,30))
            ImageDraw.Draw(board).text((col*384+5,5),('Original','v069','v070')[col],fill='white')
        board.crop((0,0,1152,320)).save(FOLDER/'avisos-comparacao.png')
    return patch,proofs


def derive(elf,parents,previews=False):
    new=literal_patches(elf)+[diary_patch()];revised=[]
    with MAP.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
        loc,locproof=locations(data)
    new.extend(loc)
    header,hproof=headers(next(p for p in parents if p['id']=='observed.headers'));revised.append(header)
    icon,iproof=transport_icons(next(p for p in parents if p['id']=='reported.raster.tank'),previews);revised.append(icon)
    item=next(p for p in parents if p['id']=='item.name.0665');target=encode('Minério pequeno')
    if len(target)>16 or len(item['before'])!=24:raise ValueError('Ore fixed item capacity differs')
    revised.append({**item,'after':target+bytes(24-len(target))})
    cp,removed,category=category_pool.derive(elf,parents);new.extend(cp)
    # Repack replaces only exact historic label cells in the original 72 bytes.
    ignored=set(removed)|{p['id'] for p in revised}
    occupied=[p for p in parents if p['id'] not in ignored]
    for p in new:
        if any(p['resource']==q['resource'] and max(p['offset'],q['offset'])<min(p['offset']+len(p['before']),q['offset']+len(q['before'])) for q in occupied):
            raise ValueError('Final patch overlaps unrelated resource')
        occupied.append(p)
    return new,revised,removed,{'locations':locproof,'headers':hproof,'transport':iproof,'categories':category,
        'elf_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS],
        'font_sha256':sha(FONT.read_bytes()),'icon_font_sha256':sha(ICON_FONT.read_bytes()),'diary_sha256':sha(original(DIARY))}


def binding_load(binding):
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:raise ValueError('Final binding differs')
    raw=(ROOT/MANIFEST).read_bytes();m=json.loads(raw)
    if sha(raw)!=binding['sha256'] or m['policy']!=POLICY or m['parent_sha256']!=sha((ROOT/PARENT).read_bytes()) or m['parent_map_sha256']!=sha((ROOT/PARENT_MAP).read_bytes()):
        raise ValueError('Final manifest/parent differs')
    return m


def validate(recipe):
    m=binding_load(recipe['final_candidate_review']);parent=json.loads((ROOT/PARENT).read_bytes())
    expected=copy.deepcopy(parent);expected.update(final_candidate_review=recipe['final_candidate_review'],
        base_dialogue_draft=CHILD_MAP,iso_name='MetalSaga-ptbr-interface-v070.iso',status=STATUS)
    if recipe!=expected:raise ValueError('Unrelated final recipe mutation')
    return parent,m


def compile_interface(elf,recipe):
    from interface_text import compile_draft
    parent,m=validate(recipe);parents,report=compile_draft(elf,parent)
    new,revised,removed,evidence=derive(elf,parents)
    if m['new']!=[metadata(p) for p in new] or m['revised']!=[metadata(p) for p in revised] or m['removed']!=removed or m['evidence']!=evidence:
        raise ValueError('Final outputs differ from approved manifest')
    by={p['id']:p for p in revised}
    patches=[by.get(p['id'],p) for p in parents if p['id'] not in removed]+new
    report=copy.deepcopy(report);report['accepted']+=26
    report['final_candidate_review']={'policy':POLICY,'reviewed_units':26,'location_fields':18,
        'new_literals':3,'diary_fields':1,'headers':2,'transport_labels':2,
        'ore_name_revised':True,'category_pool':True,'short_speakers_remaining':13,
        'pcsx2_executed':False,'visual_status':'pending_user'}
    return patches,report


def validate_narrative(draft):
    from build_translation_pilot import load_draft
    m=binding_load(draft['final_candidate_review']);expected,_=load_draft(ROOT/PARENT_MAP)
    expected['translations'].update(NARRATIVE)
    expected.update(final_candidate_review=draft['final_candidate_review'],name='regiao-inicial-v048',
                    status=STATUS,reviewed_changes=list(NARRATIVE))
    if expected!=draft:raise ValueError('Unrelated final narrative mutation')
    return m


def compile_narrative(data,draft):
    from build_translation_pilot import load_draft,compile_draft
    from reinsertion import compile_entry
    validate_narrative(draft);parent,_=load_draft(ROOT/PARENT_MAP)
    doc,patches,report=compile_draft(data,parent);by={};report=copy.deepcopy(report)
    for key,target in NARRATIVE.items():
        entry=next(e for e in doc['entries'] if e['id']==key)
        editable=[s for s in entry['segments'] if s['editable']]
        if len(editable)!=1:raise ValueError('Final narrative target segment differs')
        changed=copy.deepcopy(entry);next(s for s in changed['segments'] if s['editable'])['translation']=target
        patch,info=compile_entry(data,changed,changed,quirk_refs=True)
        if not patch:raise ValueError('Final narrative patch missing')
        by[key]=patch;editable[0]['translation']=target
        next(r for r in report['results'] if r['id']==key).update(target_lengths=info['target_lengths'],warnings=info['warnings'])
    report['final_candidate_review']={'revised_dialogues':2,'pcsx2_executed':False}
    return doc,[by.get(p['id'],p) for p in patches],report


def prepare():
    from interface_text import compile_draft
    elf=ELF.read_bytes();parent=json.loads((ROOT/PARENT).read_bytes())
    parents,_=compile_draft(elf,parent)
    # Own, local scratch cache only: never used by the production compiler.
    import pickle
    FOLDER.mkdir(parents=True,exist_ok=True)
    (FOLDER/'parent-patches.pickle').write_bytes(pickle.dumps(parents))
    new,revised,removed,evidence=derive(elf,parents,previews=True)
    m={'schema':1,'policy':POLICY,'parent':PARENT,'parent_sha256':sha((ROOT/PARENT).read_bytes()),
       'parent_map':PARENT_MAP,'parent_map_sha256':sha((ROOT/PARENT_MAP).read_bytes()),
       'new':[metadata(p) for p in new],'revised':[metadata(p) for p in revised],
       'removed':removed,'evidence':evidence}
    raw=(json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode();(ROOT/MANIFEST).write_bytes(raw)
    binding={'recipe':MANIFEST,'sha256':sha(raw)};child=copy.deepcopy(parent)
    child.update(final_candidate_review=binding,base_dialogue_draft=CHILD_MAP,
                 iso_name='MetalSaga-ptbr-interface-v070.iso',status=STATUS)
    (ROOT/CHILD).write_bytes((json.dumps(child,ensure_ascii=False,indent=2)+'\n').encode())
    narrative={'schema':1,'extends':PARENT_MAP.rsplit('/',1)[1],'name':'regiao-inicial-v048',
        'status':STATUS,'translations':NARRATIVE,'reviewed_changes':list(NARRATIVE),'final_candidate_review':binding}
    (ROOT/CHILD_MAP).write_bytes((json.dumps(narrative,ensure_ascii=False,indent=2)+'\n').encode())
    validate(child)
    print(f'Final candidate: {len(new)} new patches, {len(revised)} revised, {len(removed)} coalesced')


if __name__=='__main__':prepare()
