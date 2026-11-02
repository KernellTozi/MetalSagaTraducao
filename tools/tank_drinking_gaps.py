"""v066: observed tank headers, map labels and bounded drinking-contest UI."""
import copy,json,mmap,struct,re,math
from pathlib import Path
from collections import Counter
from dialogue import ROOT,sha
from interface_graphics import original
from interface_texture_pack import pillow,unpack_indices
from interface_textures import inspect_texture
from interface_text import SOURCE as ELF,references,sections
from reinsertion import SOURCE as MAP
from gfi import encode

POLICY='tank-headers-locations-and-drinking-ui-v001'
PARENT='translations/interface-v065.json';CHILD='translations/interface-v066.json'
PARENT_MAP='translations/regiao-inicial-v045.json';CHILD_MAP='translations/regiao-inicial-v046.json'
MANIFEST='translations/lacunas-tanque-bebida-v001.json'
FOLDER=ROOT/'work/interface-v066-investigacao'
NDATA='DATA/NDATA/NDATA.SDA';SPACK='DATA/S/S_PACK.SDA';MCT='DATA/MAP/MAP.MCT'
STATUS='Peças, Nome, Selecionados, locais e interface/instruções de bebida; visual pendente.'
LOCATIONS={'Abandoned Building':'Prédio abandonado','Abandoned Buildings':'Prédios abandonados','Sunken Ruins':'Ruínas submersas'}
TITLES={'map.supr.1b0bc77c':('- Prédios Vazios -','Prédios abandonados'),
        'map.supr.1857c10c':('Ruínas Submersas','Ruínas submersas')}
HEADERS=((118,120,256,132,'PEÇAS'),(4,192,158,204,'NOME'),(4,228,196,240,'SELECIONADOS'))
FONT=Path('C:/Windows/Fonts/arialbd.ttf')
HUD=(('Tempo',(37,37,85,57),'time',20),('Bebidas',(24,301,106,324),'drinks',20),
     ('BEBER',(218,88,289,105),'drink',19),('PERIGO',(208,72,301,87),'danger',19))
RULES=(('text',None,16,24,'Regras'),
       ('paragraph',48,60,18,'Beba todas as bebidas antes que o tempo acabe para vencer.'),
       ('icon',(171,98,220,127),48,115),
       ('paragraph',115,116,18,'Cada bebida faz a barra subir em um ritmo diferente.'),
       ('paragraph',48,178,18,'Se a barra na parte inferior da tela encher completamente, você vai engasgar.'),
       ('text',None,250,24,'Controles'),('icon',(95,291,120,316),64,295),
       ('text',100,299,18,'Aperte várias vezes para beber.'),
       ('icon',(230,370,288,392),230,370))


def header_patch(parent):
    from observed_menu_translation import header_glyphs
    raw=original(SPACK);record=raw[0x8c830:0x9cc40];meta,_=inspect_texture(record)
    pixels=unpack_indices(record,meta);g=header_glyphs(record)
    g['P']=(11,b''.join(pixels[(180+y)*256+53:(180+y)*256+64] for y in range(10)))
    out=bytearray(parent['after']);review=[]
    for left,top,right,bottom,text in HEADERS:
        width=sum(g['C' if c=='Ç' else c][0] for c in text)+3*(len(text)-1)
        if width>right-left-2:raise ValueError('Tank header overflow')
        for y in range(top,bottom):out[y*256+left:y*256+right]=bytes([241])*(right-left)
        x=left+1
        for c in text:
            w,b=g['C' if c=='Ç' else c]
            for y in range(10):out[(top+y)*256+x:(top+y)*256+x+w]=b[y*w:(y+1)*w]
            if c=='Ç':out[(top+10)*256+x+w//2]=253;out[(top+11)*256+x+w//2-1]=253
            x+=w+3
        review.append({'translation':text,'rect':[left,top,right,bottom],'width':width,'cap_height':10,'cedilla_descender':2 if 'Ç' in text else 0})
    return {**parent,'after':bytes(out)},review


def map_names(data):
    from scene_name_fields import parse
    proof=parse(data)
    if (proof['map_count'],proof['name_fields'])!=(300,839):raise ValueError('Map source catalogue differs')
    patches=[];review=[]
    for index in range(300):
        tree,size,blob,script=struct.unpack_from('<4I',data,0x830+16*index)
        for node in range(0x800+tree,0x800+tree+size,16):
            typ,children,identity,offset,length=struct.unpack_from('<HHIII',data,node);at=0x800+blob+offset
            if typ not in (2,6,7):continue
            field=bytes(data[at:at+32]);name=field.split(b'\0')[0]
            try:source=name.decode('ascii')
            except UnicodeDecodeError:continue
            if source not in LOCATIONS:continue
            text=LOCATIONS[source];value=encode(text);span=max(len(name),len(value))+1
            if span>32 or any(field[len(name):span]) or (typ in (6,7) and length!={6:204,7:216}[typ]):raise ValueError('Map label extent or padding differs')
            if typ==6 and len(value)!=len(name):raise ValueError('Portal label must keep NUL position')
            p={'id':f'tank-gaps.map.{index:03d}.{node-0x800-tree:06x}','resource':MCT,'offset':at,
               'before':field[:span],'after':value+bytes(span-len(value))};patches.append(p)
            review.append({'id':p['id'],'map':index,'node_offset':node,'type':typ,'record_size':length,
                           'node_sha256':sha(data[node:node+16]),'record_sha256':sha(data[at:at+length]),'translation':text})
    if len(patches)!=7:raise ValueError('Map label occurrence census differs')
    return patches,review


def title_specs(data):
    from dialogue_advanced import parse
    from build_translation_pilot import load_draft
    draft,_=load_draft(ROOT/PARENT_MAP);rows=[]
    for key,(old,target) in TITLES.items():
        if draft['translations'][key]!=old:raise ValueError('Location title parent differs')
        at=int(key.rsplit('.',1)[1],16);kind,p=parse(data,at);size=p['size'];header=p['header_size'];capacity=size-header-1
        if kind!='validated' or header!=48 or len(p['segments'])!=1 or len(encode(target))>capacity:raise ValueError('Location title source layout differs')
        raw=bytes(data[at:at+size]);value=encode(target);previous=encode(old)
        before=raw[:header]+previous+bytes(size-header-len(previous));after=raw[:header]+value+bytes(size-header-len(value))
        rows.append({'id':key,'offset':at,'size':size,'capacity':capacity,'source_sha256':sha(raw),
                     'parent_sha256':sha(before),'after_sha256':sha(after),'translation':target})
    return rows


def elf_help(elf):
    at=0x31f7b0;source=b'Drink:$\x81~ Exit:$\x81\x9b Help:$\x81\xa2';value=b'Beber:$\x81~ Sair:$\x81\x9b Ajuda:$\x81\xa2'
    before=elf[at:at+32];refs=references(elf,sections(elf))
    if before!=source+bytes(32-len(source)) or any(at+0xff000+i in refs for i in range(1,32)):
        raise ValueError('Drinking input literal/cell/interior reference differs')
    if re.findall(rb'\$\x81.',source)!=re.findall(rb'\$\x81.',value):raise ValueError('Controller token changed')
    return {'id':'tank-gaps.drink-input','resource':'SLUS_212.93','offset':at,'before':before,'after':value+bytes(32-len(value))}


def ndata_texture(raw,index,offset):
    count=struct.unpack_from('<I',raw,8)[0];offsets=struct.unpack_from('<'+str(count)+'I',raw,12)
    if count!=203 or offsets[index]!=offset:raise ValueError('Drinking NDATA index changed')
    record=raw[offset:offset+263184];meta,_=inspect_texture(record)
    if (meta['width'],meta['height'],meta['bpp'])!=(512,512,8) or offset+263184>offsets[index+1]:raise ValueError('Drinking texture size differs')
    return record,meta


def display_palette(record):
    """CSM1 8-bit CLUT address mapping, for color lookup/preview only."""
    palette=[tuple(record[16+i*4:20+i*4]) for i in range(256)]
    return [palette[(i&~24)|((i&8)<<1)|((i&16)>>1)] for i in range(256)]


def hud(raw):
    Image=pillow()
    from PIL import ImageDraw,ImageFont
    record,meta=ndata_texture(raw,96,0xb6a800);pixels=unpack_indices(record,meta);out=bytearray(pixels)
    pal=display_palette(record);rows=[]
    for text,(left,top,right,bottom),kind,size in HUD:
        used=Counter(pixels[y*512+x] for y in range(top,bottom) for x in range(left,right));bg=used.most_common(1)[0][0]
        if kind in ('drink','danger'):
            bg=pixels[69*512+205]
            if bg!=241:raise ValueError('Drinking word-box original background differs')
        choices=[i for i in used if i!=bg]
        if kind=='drink' or kind=='drinks':choices=[i for i in choices if pal[i][0]<100 and pal[i][2]>pal[i][0]+20 and pal[i][1]<160]
        elif kind=='danger':choices=[i for i in choices if pal[i][0]>170 and pal[i][1]<100]
        else:choices=[i for i in choices if min(pal[i][:3])>120]
        if not choices:raise ValueError('HUD original ink color not found')
        fg=max(choices,key=lambda i:used[i]);layout={'horizontal_scale':1}
        if kind=='time':
            from interface_graphics import mask
            ink,layout=mask(text,bottom-top,right-left)
        else:
            font=ImageFont.truetype(str(FONT),size);box=font.getbbox(text)
            if box[2]-box[0]>right-left or box[3]-box[1]>bottom-top:raise ValueError('HUD word exceeds original cell')
            ink=Image.new('L',(right-left,bottom-top));ImageDraw.Draw(ink).text(((ink.width-(box[2]-box[0]))//2-box[0],(ink.height-(box[3]-box[1]))//2-box[1]),text,font=font,fill=255)
        clear={'time':(33,33,92,63),'drink':(205,88,307,107),'danger':(205,70,307,88)}.get(kind,(left,top,right,bottom))
        for yy in range(clear[1],clear[3]):out[yy*512+clear[0]:yy*512+clear[2]]=bytes([bg])*(clear[2]-clear[0])
        for y in range(ink.height):
            for x in range(ink.width):out[(top+y)*512+left+x]=fg if ink.getpixel((x,y))>=128 else bg
        rows.append({'text':text,'rect':[left,top,right,bottom],'clear_rect':list(clear),'font_size':size,
                     'background_index':bg,'foreground_index':fg,'mask_sha256':sha(ink.tobytes()),'horizontal_scale':layout['horizontal_scale']})
    return {'id':'tank-gaps.drinking-hud','resource':NDATA,'offset':0xb6a800+meta['pixel_offset'],'before':pixels,'after':bytes(out)},rows


def rules(raw):
    Image=pillow()
    from interface_remainder_graphics import lettering,paragraph
    record,meta=ndata_texture(raw,69,0x7b1000);pixels=unpack_indices(record,meta)
    source=Image.frombytes('L',(512,512),pixels);out=source.copy();bg=Counter(source.crop((4,4,508,396)).tobytes()).most_common(1)[0][0]
    pal=display_palette(record)
    inks=Counter(source.crop((240,35,285,57)).tobytes());choices=[i for i in inks if i!=bg and min(pal[i][:3])>110]
    if not choices:raise ValueError('Original rules ink color not found')
    fg=max(choices,key=lambda i:inks[i]);out.paste(bg,(4,4,508,396));occupied=[];rows=[];icons=[]
    def reserve(box):
        if not (4<=box[0]<box[2]<=508 and 4<=box[1]<box[3]<=396) or any(box[0]<b[2] and b[0]<box[2] and box[1]<b[3] and b[1]<box[3] for b in occupied):raise ValueError('Drinking rules overlap/overflow')
        occupied.append(box)
    for op in RULES:
        if op[0]=='icon':
            _,rect,x,y=op;icon=source.crop(rect);box=[x,y,x+icon.width,y+icon.height];reserve(box);out.paste(icon,(x,y))
            icons.append({'source_rect':list(rect),'target_rect':box,'sha256':sha(icon.tobytes())});continue
        kind,x,y,height,text=op;lines=paragraph(text,474-x,height) if kind=='paragraph' else [text]
        for n,line in enumerate(lines):
            glyph=lettering(line,height);left=(512-glyph.width)//2 if x is None else x;top=y+n*(height+2)
            box=[left,top,left+glyph.width,top+glyph.height];reserve(box)
            for yy in range(glyph.height):
                for xx in range(glyph.width):
                    if glyph.getpixel((xx,yy))>=128:out.putpixel((left+xx,top+yy),fg)
            rows.append({'text':line,'rect':box,'height':height,'resized_horizontally':False})
    return {'id':'tank-gaps.drinking-rules','resource':NDATA,'offset':0x7b1000+meta['pixel_offset'],'before':pixels,'after':out.tobytes()}, {'rows':rows,'icons':icons,'background_index':bg,'foreground_index':fg}


def derive(elf,parents):
    old=next(p for p in parents if p['id']=='observed.headers');header,h=header_patch(old)
    raw=original(NDATA);hp,hr=hud(raw);rp,rr=rules(raw)
    with MAP.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
        mp,mr=map_names(data);titles=title_specs(data)
    return [header],mp+[elf_help(elf),hp,rp],{'headers':h,'map_labels':mr,'titles':titles,'hud':hr,'rules':rr,
        'font_sha256':sha(FONT.read_bytes()),'ndata_source_sha256':sha(raw)}


def metadata(p):return {k:p[k] for k in ('id','resource','offset')}|{'size':len(p['before']),'source_sha256':sha(p['before']),'after_sha256':sha(p['after'])}


def binding_load(binding):
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:raise ValueError('Unknown tank/drinking binding')
    raw=(ROOT/MANIFEST).read_bytes();m=json.loads(raw)
    if sha(raw)!=binding['sha256'] or m['policy']!=POLICY or m['parent_sha256']!=sha((ROOT/PARENT).read_bytes()) or m['parent_map_sha256']!=sha((ROOT/PARENT_MAP).read_bytes()):raise ValueError('Tank/drinking manifest/parent differs')
    return m


def validate(recipe):
    m=binding_load(recipe['tank_drinking_release']);parent=json.loads((ROOT/PARENT).read_bytes());expected=copy.deepcopy(parent)
    expected.update(tank_drinking_release=recipe['tank_drinking_release'],base_dialogue_draft=CHILD_MAP,iso_name='MetalSaga-ptbr-interface-v066.iso',status=STATUS)
    if expected!=recipe:raise ValueError('Unrelated tank/drinking UI mutation')
    return parent,m


def compile_interface(elf,recipe):
    from interface_text import compile_draft
    parent,m=validate(recipe);patches,report=compile_draft(elf,parent);rev,new,evidence=derive(elf,patches)
    if m['revised']!=[metadata(p) for p in rev] or m['new']!=[metadata(p) for p in new] or m['evidence']!=evidence:raise ValueError('Tank/drinking output differs')
    by={p['id']:p for p in rev};out=[by.get(p['id'],p) for p in patches]
    for p in new:
        if any(q['resource']==p['resource'] and max(q['offset'],p['offset'])<min(q['offset']+len(q['before']),p['offset']+len(p['before'])) for q in out):raise ValueError('Tank/drinking new patch overlaps inherited data')
        out.append(p)
    report=copy.deepcopy(report);report['accepted']+=16
    report['tank_drinking_release']={'policy':POLICY,'new_units':16,'native_headers':3,'map_label_occurrences':7,'elf_input_legend':1,'hud_labels':4,'instruction_panels':1,
                                    'revised_location_titles':2,'pcsx2_executed':False,'visual_status':'pending_user'}
    return out,report


def validate_narrative(draft):
    from build_translation_pilot import load_draft
    m=binding_load(draft['minigame_context_review']);expected,_=load_draft(ROOT/PARENT_MAP)
    expected['translations'].update({k:v[1] for k,v in TITLES.items()})
    expected.update(minigame_context_review=draft['minigame_context_review'],name='regiao-inicial-v046',status=STATUS,reviewed_changes=list(TITLES))
    if expected!=draft:raise ValueError('Unrelated location narrative mutation')
    return m


def compile_narrative(data,draft):
    from build_translation_pilot import load_draft,compile_draft
    from reinsertion import compile_entry
    m=validate_narrative(draft);parent,_=load_draft(ROOT/PARENT_MAP);doc,patches,report=compile_draft(data,parent)
    specs=title_specs(data)
    if specs!=m['evidence']['titles']:raise ValueError('Location title evidence differs')
    replacements={};report=copy.deepcopy(report)
    for spec in specs:
        key=spec['id'];entry=next(e for e in doc['entries'] if e['id']==key);old=next(p for p in patches if p['id']==key)
        if sha(old['after'])!=spec['parent_sha256'] or len(entry['segments'])!=1 or entry['mode']!='slots' or entry['blocked_reasons']:raise ValueError('Location title compiler parent differs')
        check=copy.deepcopy(entry);check['segments'][0]['translation']=spec['translation'];p,info=compile_entry(data,check,check,quirk_refs=True)
        if not p or sha(p['after'])!=spec['after_sha256']:raise ValueError('Location title compiler differs')
        replacements[key]=p;entry['segments'][0]['translation']=spec['translation']
        next(r for r in report['results'] if r['id']==key).update(target_lengths=info['target_lengths'],warnings=info['warnings'])
    report['minigame_context_review']={'policy':POLICY,'revised_location_titles':2,'pcsx2_executed':False}
    return doc,[replacements.get(p['id'],p) for p in patches],report


def previews(revised,new):
    Image=pillow()
    from PIL import ImageDraw
    FOLDER.mkdir(exist_ok=True)
    for name,key,offset,rect,scale in (('bebidas','tank-gaps.drinking-hud',0xb6a800,(0,0,512,330),1),('tutorial','tank-gaps.drinking-rules',0x7b1000,(0,0,512,400),1)):
        raw=original(NDATA);p=next(p for p in new if p['id']==key);changed=bytearray(raw);changed[p['offset']:p['offset']+len(p['after'])]=p['after']
        board=Image.new('RGB',(1024,rect[3]+24),(35,35,35));d=ImageDraw.Draw(board)
        for col,blob in enumerate((raw,changed)):
            rec=blob[offset:offset+263184];meta,_=inspect_texture(rec);pal=display_palette(rec)
            rgb=bytes(v for i in unpack_indices(rec,meta) for v in pal[i][:3]);im=Image.frombytes('RGB',(512,512),rgb).crop(rect)
            board.paste(im,(col*512,24));d.text((col*512+5,3),'Original' if col==0 else 'PT-BR',fill='white')
        board.save(FOLDER/(name+'-comparacao.png'))
    raw=original(SPACK);p=revised[0];changed=bytearray(raw);changed[p['offset']:p['offset']+len(p['after'])]=p['after']
    board=Image.new('RGB',(840,150),(35,35,35));d=ImageDraw.Draw(board)
    for col,blob in enumerate((raw,changed)):
        _,rgb=inspect_texture(blob[0x8c830:0x9cc40]);im=Image.frombytes('RGB',(256,256),rgb)
        d.text((col*420+5,3),'Original' if col==0 else 'PT-BR',fill='white')
        for row,(x,y,z,w,_) in enumerate(HEADERS):
            crop=im.crop((x,y,z,w));crop=crop.resize((crop.width*2,24),Image.Resampling.NEAREST);board.paste(crop,(col*420+5,25+row*38))
    board.save(FOLDER/'cabecalhos-comparacao.png')


def prepare():
    from interface_text import compile_draft
    from build_translation_pilot import load_draft
    parent=json.loads((ROOT/PARENT).read_bytes());patches,_=compile_draft(ELF.read_bytes(),parent);rev,new,evidence=derive(ELF.read_bytes(),patches)
    m={'schema':1,'policy':POLICY,'parent':PARENT,'parent_sha256':sha((ROOT/PARENT).read_bytes()),'parent_map':PARENT_MAP,
       'parent_map_sha256':sha((ROOT/PARENT_MAP).read_bytes()),'revised':[metadata(p) for p in rev],'new':[metadata(p) for p in new],'evidence':evidence}
    raw=(json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode();(ROOT/MANIFEST).write_bytes(raw);binding={'recipe':MANIFEST,'sha256':sha(raw)}
    child=copy.deepcopy(parent);child.update(tank_drinking_release=binding,base_dialogue_draft=CHILD_MAP,iso_name='MetalSaga-ptbr-interface-v066.iso',status=STATUS)
    (ROOT/CHILD).write_bytes((json.dumps(child,ensure_ascii=False,indent=2)+'\n').encode())
    narrative={'schema':1,'extends':Path(PARENT_MAP).name,'name':'regiao-inicial-v046','status':STATUS,
               'translations':{k:v[1] for k,v in TITLES.items()},'reviewed_changes':list(TITLES),'minigame_context_review':binding}
    (ROOT/CHILD_MAP).write_bytes((json.dumps(narrative,ensure_ascii=False,indent=2)+'\n').encode());validate(child);validate_narrative(load_draft(ROOT/CHILD_MAP)[0]);previews(rev,new)
    print(json.dumps({'new_physical_patches':len(new),'revised_header_patches':len(rev),'revised_location_titles':2,'new_units':16}))


if __name__=='__main__':prepare()
