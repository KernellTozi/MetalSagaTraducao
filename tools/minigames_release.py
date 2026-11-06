"""Local, source-bound minigame localization using original indexed textures."""
import argparse
import copy
import json
import math
import re
import struct
from collections import Counter, deque
from pathlib import Path

from dialogue import ROOT, sha
from gfi import encode
from interface_graphics import original
from interface_text import SOURCE as ELF, references, sections
from interface_texture_pack import pillow, unpack_indices, replace_indices
from interface_textures import inspect_texture
from tank_drinking_gaps import display_palette, metadata

POLICY = 'all-minigames-source-bound-indexed-cells-v001'
PARENT = 'translations/interface-v067.json'
CHILD = 'translations/interface-v068.json'
CONTENT = 'translations/minigames-conteudo-v001.json'
MANIFEST = 'translations/minigames-v001.json'
FOLDER = ROOT / 'work/minigames-v068'
STATUS = 'Minigames: gráficos, instruções e comandos em português; visual pendente.'
FONTS = {name: Path('C:/Windows/Fonts') / file for name, file in
         [('impact','impact.ttf'),('arial','arialbd.ttf'),('times','timesbd.ttf')]}
COLORS = {'white':(240,240,230), 'gold':(245,190,40), 'red':(245,42,30),
          'green':(40,190,145), 'blue':(80,165,225), 'black':(20,20,20), 'brown':(107,61,48)}
ICON = re.compile(rb'\$(?:\x81.|[RL][12])|\x81\x46')


def palette(record, meta):
    if meta['bpp'] == 8:
        return display_palette(record)
    return [tuple(record[16+i*4:20+i*4]) for i in range(16)]


def image(record, meta):
    Image = pillow()
    return Image.frombytes('L', (meta['width'],meta['height']),unpack_indices(record,meta))


def background_index(canvas, rect, colors):
    used = Counter(canvas.crop(rect).tobytes())
    return used.most_common(1)[0][0]


def paint_mask(canvas, mask, x, y, color, colors):
    """Quantize coverage against the unchanged PS2 palette, including alpha."""
    alpha = max(c[3] for c in colors)
    lookup = {}
    for iy in range(mask.height):
        for ix in range(mask.width):
            coverage = mask.getpixel((ix,iy))
            if not coverage:
                continue
            old = canvas.getpixel((x+ix,y+iy))
            key = (coverage,old)
            if key not in lookup:
                fraction = coverage/255
                prior = colors[old]
                target = tuple(round(prior[k]+fraction*(color[k]-prior[k])) for k in range(3)) + (round(prior[3]+fraction*(alpha-prior[3])),)
                lookup[key] = min(range(len(colors)),key=lambda i: sum((a-b)**2 for a,b in zip(colors[i],target)))
            canvas.putpixel((x+ix,y+iy),lookup[key])


def font_mask(text, font_name, size, width, height, outline):
    Image = pillow()
    from PIL import ImageDraw, ImageFont
    # Rasterize at final size. Fitting chooses a point size, never resamples ink.
    for point in range(size,4,-1):
        font = ImageFont.truetype(str(FONTS[font_name]),point)
        scratch = Image.new('L',(1,1))
        box = ImageDraw.Draw(scratch).multiline_textbbox((0,0),text,font=font,spacing=1,align='center')
        w,h = math.ceil(box[2]-box[0]+outline*2+2),math.ceil(box[3]-box[1]+outline*2+2)
        if w <= width and h <= height:
            mask = Image.new('L',(w,h))
            ImageDraw.Draw(mask).multiline_text((outline+1-box[0],outline+1-box[1]),text,font=font,fill=255,spacing=1,align='center')
            return mask,point
    raise ValueError(f'Minigame word cannot fit original cell: {text!r}')


def label(canvas, spec, colors):
    Image = pillow()
    from PIL import ImageFilter
    x,y,right,bottom = spec['rect']
    if not (0 <= x < right <= canvas.width and 0 <= y < bottom <= canvas.height):
        raise ValueError('Minigame label outside texture')
    mode = spec.get('background','mode')
    source_ink=Counter(canvas.crop((x,y,right,bottom)).tobytes())
    if mode == 'row':
        # Wood-grain sign: a clean adjacent sample supplies each scanline.
        for row in range(y,bottom):
            index = canvas.getpixel((x-3,row))
            canvas.paste(index,(x,row,right,row+1))
    elif mode == 'mode':
        # Tight word cells can contain more ink than background. Sample their
        # perimeter instead of mistaking a thick letter's fill for the backdrop.
        edge=[canvas.getpixel((ix,iy)) for iy in (y,bottom-1) for ix in range(x,right)]
        edge += [canvas.getpixel((ix,iy)) for ix in (x,right-1) for iy in range(y,bottom)]
        canvas.paste(Counter(edge).most_common(1)[0][0],(x,y,right,bottom))
    elif mode == 'white':
        alpha=max(c[3] for c in colors)
        index=min(range(len(colors)),key=lambda i:sum((a-b)**2 for a,b in zip(colors[i],(255,255,255,alpha))))
        canvas.paste(index,(x,y,right,bottom))
    elif mode == 'sample':
        canvas.paste(canvas.getpixel(tuple(spec['sample'])),(x,y,right,bottom))
    elif mode == 'sample_rect':
        region=canvas.crop(spec['sample_rect'])
        canvas.paste(Counter(region.tobytes()).most_common(1)[0][0],(x,y,right,bottom))
    else:
        raise ValueError('Unknown minigame background policy')
    outline = spec.get('outline',1)
    rotated = spec.get('rotation',0)
    if rotated not in (0,90,180):
        raise ValueError('Unknown minigame label orientation')
    width,height = (bottom-y,right-x) if rotated==90 else (right-x,bottom-y)
    mask,point = font_mask(spec['text'],spec.get('font','impact'),spec['size'],width,height,outline)
    if rotated==90:
        mask=mask.transpose(Image.Transpose.ROTATE_90)
    elif rotated==180:
        mask=mask.transpose(Image.Transpose.ROTATE_180)
    left,top = x+(right-x-mask.width)//2,y+(bottom-y-mask.height)//2
    if outline:
        edge = mask.filter(ImageFilter.MaxFilter(2*outline+1))
        paint_mask(canvas,edge,left,top,(15,15,15),colors)
        if spec.get('font')=='impact' and spec['color'] not in ('white','black') and point>=16:
            paint_mask(canvas,edge,left,top,(235,228,207),colors)
    if spec['color']=='source':
        candidates=[i for i in source_ink if colors[i][3]>0 and sum(colors[i][:3])>400]
        if not candidates:
            raise ValueError('Source minigame ink not found')
        color=colors[max(candidates,key=source_ink.get)][:3]
    else:
        color=COLORS[spec['color']]
    paint_mask(canvas,mask,left,top,color,colors)
    return {'text':spec['text'],'rect':spec['rect'],'point_size':point,'mask_sha256':sha(mask.tobytes())}


def cloth_lettering(canvas, spec, colors):
    """Remove small gold glyph components, retaining the long table-frame lines."""
    Image = pillow()
    from PIL import ImageFont
    x,y,right,bottom = spec['rect']
    source=canvas.copy()
    def gold(index):
        r,g,b,a=colors[index]
        return a>0 and r>90 and g>70 and b<220 and g*.92<=r<=g*1.2 and g*.55<=b<r*.94
    candidates={(ix,iy) for iy in range(y,bottom) for ix in range(x,right) if gold(source.getpixel((ix,iy)))}
    remaining=set(candidates);ink=set();components=[]
    while remaining:
        first=remaining.pop();queue=deque([first]);group=[first]
        while queue:
            ix,iy=queue.popleft()
            for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):
                point=(ix+dx,iy+dy)
                if point in remaining:
                    remaining.remove(point);queue.append(point);group.append(point)
        left=min(p[0] for p in group);top=min(p[1] for p in group)
        width=max(p[0] for p in group)-left+1;height=max(p[1] for p in group)-top+1
        if width<=48 and height<=42 and 2<=len(group)<=1200:
            ink.update(group);components.append([left,top,width,height,len(group)])
    expanded={(ix+dx,iy+dy) for ix,iy in ink for dx in (-1,0,1) for dy in (-1,0,1)
              if x<=ix+dx<right and y<=iy+dy<bottom}
    for ix,iy in sorted(expanded):
        found=[]
        for radius in (2,4,7,10,16,24):
            points=[(ix,iy-radius),(ix,iy+radius),(ix-radius,iy),(ix+radius,iy)]
            found=[source.getpixel(p) for p in points if 0<=p[0]<canvas.width and 0<=p[1]<canvas.height
                   and p not in expanded and not gold(source.getpixel(p))]
            if found:
                break
        if not found:
            raise ValueError(f'Table lettering has no clean neighboring sample: {(ix,iy)}')
        canvas.putpixel((ix,iy),Counter(found).most_common(1)[0][0])
    # The curved insurance strip has a painted brown substrate. Restore its
    # original outline, then replace only the inner substrate containing ink.
    for ix in range(x,right):
        brown=[]
        for iy in range(max(y,128),bottom):
            r,g,b,a=colors[source.getpixel((ix,iy))]
            if r>g*1.3 and r>b*1.6 and g>b*1.1:
                brown.append(iy)
        if len(brown)<10:
            continue
        first,last=min(brown),max(brown)
        a,b=max(y,first-3),min(bottom,last+4)
        canvas.paste(source.crop((ix,a,ix+1,b)),(ix,a))
        if last-first>8:
            substrate=Counter(source.getpixel((ix,iy)) for iy in brown).most_common(1)[0][0]
            canvas.paste(substrate,(ix,first+2,ix+1,last-1))
    arcs=[]
    for row in spec.get('arcs',[]):
        font=ImageFont.truetype(str(FONTS['times']),row['size'])
        advance=sum(font.getlength(c) for c in row['text'])
        position=row['center'][0]-advance/2
        for char in row['text']:
            step=font.getlength(char);cx=position+step/2;position+=step
            if char==' ':
                continue
            offset=cx-row['center'][0];cy=row['center'][1]-row['curve']*offset*offset
            mask,_=font_mask(char,'times',row['size'],64,64,0)
            angle=math.degrees(math.atan(2*row['curve']*offset))
            mask=mask.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
            left,top=round(cx-mask.width/2),round(cy-mask.height/2)
            if not (x<=left<left+mask.width<=right and y<=top<top+mask.height<=bottom):
                raise ValueError('Translated table lettering exceeds bound region')
            paint_mask(canvas,mask,left,top,COLORS['gold'],colors)
        arcs.append({'text':row['text'],'center':row['center'],'point_size':row['size']})
    return {'rect':spec['rect'],'removed_glyph_components':sorted(components),'arcs':arcs}


def native_mask(text,height):
    from interface_remainder_graphics import lettering
    try:
        return lettering(text,height)
    except ValueError as error:
        if 'Unsupported project glyph' not in str(error):
            raise
        return font_mask(text,'arial',height,10000,height+6,0)[0]


def wrap(text,width,height):
    lines = []
    line = ''
    for word in text.split():
        trial = (line+' '+word).strip()
        if native_mask(trial,height).width <= width:
            line = trial
        else:
            if not line or native_mask(word,height).width > width:
                raise ValueError('Unbreakable minigame instruction')
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def panel(canvas, spec, colors):
    x,y,right,bottom = spec['rect']
    source = canvas.copy()
    bg = background_index(source,(x,y,right,bottom),colors)
    canvas.paste(bg,(x,y,right,bottom))
    if spec.get('border'):
        from PIL import ImageDraw
        index=min(range(len(colors)),key=lambda i:sum((a-b)**2 for a,b in zip(colors[i][:3],(200,175,130))))
        ImageDraw.Draw(canvas).rectangle((x+4,y+4,right-5,bottom-5),outline=index,width=1)
    occupied = []
    rows = []
    def reserve(rect):
        a,b,c,d = rect
        if not (x <= a < c <= right and y <= b < d <= bottom):
            raise ValueError(f'Minigame instruction outside frame: {rect}')
        if any(a<q[2] and q[0]<c and b<q[3] and q[1]<d for q in occupied):
            raise ValueError(f'Minigame instruction/icon overlap: {rect}')
        occupied.append(rect)
    def write(text,left,top,height,width,color='white'):
        mask = native_mask(text,height)
        if mask.width > width:
            raise ValueError(f'Minigame instruction line too wide: {text!r}')
        left = (canvas.width-mask.width)//2 if left is None else left
        reserve((left,top,left+mask.width,top+mask.height))
        paint_mask(canvas,mask,left,top,COLORS[color],colors)
        rows.append({'text':text,'rect':[left,top,left+mask.width,top+mask.height]})
    if spec['title']:
        write(spec['title'],None,y+12,22,right-x)
    for part in spec['parts']:
        if part['kind'] == 'copy':
            crop = source.crop(part['rect'])
            rect = (part['x'],part['y'],part['x']+crop.width,part['y']+crop.height)
            reserve(rect)
            canvas.paste(crop,(part['x'],part['y']))
            continue
        lines = wrap(part['text'],part['width'],part['height']) if part['kind']=='paragraph' else [part['text']]
        for n,line in enumerate(lines):
            write(line,part['x'],part['y']+n*(part['height']+2),part['height'],part['width'],part.get('color','white'))
    if spec.get('page'):
        page,total = spec['page'],spec['total']
        write(f'{page} / {total}',None,375,16,130)
        if page > 1:
            write('Voltar',30,375,15,110)
            canvas.paste(source.crop((8,372,30,394)),(8,372))
        if page < total:
            write('Avançar',400,375,15,104)
            canvas.paste(source.crop((482,372,504,394)),(482,372))
    return rows


def render_texture(spec, parents):
    resource,at = spec['resource'],spec['offset']
    raw = original(resource)
    meta,_ = inspect_texture(raw[at:])
    end = meta['pixel_offset']+meta['pixel_bytes']
    record = raw[at:at+end]
    offset = at+meta['pixel_offset']
    before = record[meta['pixel_offset']:end]
    inherited = [p for p in parents if p['resource']==resource and
                 max(offset,p['offset']) < min(offset+len(before),p['offset']+len(p['before']))]
    if inherited and (len(inherited)!=1 or inherited[0]['offset']!=offset or len(inherited[0]['before'])!=len(before)):
        raise ValueError('Minigame texture inheritance requires one exact pixel plane')
    previous = inherited[0] if inherited else None
    current = record[:meta['pixel_offset']] + (previous['after'] if previous else before)
    canvas = image(current,meta)
    colors = palette(record,meta)
    instructions = panel(canvas,spec['panel'],colors) if 'panel' in spec else []
    for rect in spec.get('erase',[]):
        canvas.paste(background_index(canvas,rect,colors),rect)
    cloth=cloth_lettering(canvas,spec['cloth'],colors) if 'cloth' in spec else None
    words = [label(canvas,s,colors) for s in spec['labels']]
    output = replace_indices(record,canvas.tobytes())
    if output[:meta['pixel_offset']] != record[:meta['pixel_offset']]:
        raise ValueError('Minigame header or palette altered')
    if replace_indices(output,unpack_indices(record,meta)) != record:
        raise ValueError('Minigame indexed reverse round-trip failed')
    patch = {'id':previous['id'] if previous else f'minigame.texture.{Path(resource).stem}.{at:08x}',
             'resource':resource,'offset':offset,'before':before,'after':output[meta['pixel_offset']:]}
    if previous and previous['before'] != before:
        raise ValueError('Inherited minigame baseline differs')
    proof = {'resource':resource,'offset':at,'texture':meta | {'trailing_bytes':0},
             'source_sha256':sha(raw),'header_palette_sha256':sha(record[:meta['pixel_offset']]),
             'words':words,'instructions':instructions,'revised':previous is not None}
    if cloth is not None:
        proof['cloth']=cloth
    return patch,proof,current,output


def elf_specs():
    # Controller placeholders are replaced by the exact original byte tokens.
    return [
        (0x31dc38,'Cima/baixo para apostar\n(até 999G).',None),
        (0x31dc88,'Aposta:{0} OK:{1} Sair:{2} Ajuda:{3}',None),
        (0x31dcb0,'Nível:{0} Jogar:{1} Sair:{2} Ajuda:{3}',None),
        (0x31dd40,'Mover:{0} Número:{1} OK:{2} Ajuda:{3} (Sem repetir algarismos)',None),
        (0x31e0b0,'Cima/baixo para apostar.\nAperte X para\nconfirmar a aposta.',None),
        (0x31e118,'Mover:{0} Manter:{1} Trocar:{2}',None),
        (0x31e140,'Dobrar:{0} Receber:{1}',None),
        (0x31e160,'Aposta:{0} Jogar:{1} Sair:{2} Ajuda:{3}',40),
        (0x31e6e0,'Cima/baixo para apostar.\nAperte X para\nconfirmar a aposta.',None),
        (0x31e7c8,'Aposta:{0} Jogar:{1} Ajuda:{2} Sair:{3}',40),
        (0x31eb98,'Cima para apostar;\nbaixo para girar\nos rolos.',None),
        (0x31ec08,'Aposta:{0} Jogar:{1} Sair:{2} Ajuda:{3}',40),
        (0x31ec30,'Esq.:{0} Centro:{1} Dir.:{2}',None),
        (0x31f0b0,'Aposte nos números\ndesejados e escolha "OK".',None),
        (0x31f100,'Mover:{0} Apostar/aumentar:{1} Reduzir:{2} Histórico:{3} Ajuda:{4} Sair:{5}',None),
        (0x338b38,'Pose:{0} Sair:{1} Ajuda{2}{3}',32),
        (0x31fd38,'Vinte e um',16),(0x31fd48,'Caça-níqueis',16),
        (0x31fd68,'Caça-números',16),(0x31fd78,'Corrida de sapo',16),
        (0x31fd88,'Rali de tanques',16),(0x31fd98,'Fogo cruzado',16),
        (0x31fda8,'Aula de dança',16),(0x31fdd8,'Vitrola',16),
        (0x31fde8,'Venda de itens',16),(0x31fe20,'Jogo do cão',16),
        (0x348e00,'Pôquer',8),
    ]


def elf_patches(elf, parents):
    refs = references(elf,sections(elf))
    patches = []
    for at,text,cell in elf_specs():
        end = elf.find(b'\0',at)
        if end < at or end-at > 256:
            raise ValueError('Minigame ELF literal is not bounded')
        source = elf[at:end]
        tokens = ICON.findall(source)
        # Source may contain icons and the native colon, but no other native bytes.
        if any(b>=128 for b in ICON.sub(b'',source)):
            raise ValueError(f'Unrecognized native minigame literal: {at:x}')
        pieces = re.split(r'(\{\d+\})',text)
        output = b''.join(tokens[int(p[1:-1])] if re.fullmatch(r'\{\d+\}',p) else encode(p) for p in pieces)
        size = cell or len(source)+1
        before = source+bytes(size-len(source))
        if len(output)>=size or elf[at:at+size]!=before:
            raise ValueError(f'Minigame ELF capacity/source differs: {at:x}, {len(output)}/{size-1}')
        if not refs.get(at+0xff000) or any(at+0xff000+i in refs for i in range(1,size)):
            raise ValueError(f'Minigame ELF reference/alias needs investigation: {at:x}')
        if ICON.findall(output)!=tokens or output.count(b'\n')>source.count(b'\n'):
            raise ValueError('Minigame literal controls/line budget changed')
        patch = {'id':f'minigame.elf.{at:08x}','resource':'SLUS_212.93','offset':at,
                 'before':before,'after':output+bytes(size-len(output))}
        if any(p['resource']==patch['resource'] and max(at,p['offset'])<min(at+size,p['offset']+len(p['before'])) for p in parents):
            raise ValueError(f'Minigame ELF overlaps inherited translation: {at:x}')
        patches.append(patch)
    return patches


def derive(elf, parents, previews=False):
    literals = elf_patches(elf,parents)
    content = json.loads((ROOT/CONTENT).read_bytes())
    if content['schema'] != 1:
        raise ValueError('Unknown minigame content schema')
    seen = set()
    revised,new,evidence,images = [],[],[],[]
    for spec in content['textures']:
        key = (spec['resource'],spec['offset'])
        if key in seen:
            raise ValueError('Duplicated minigame texture')
        seen.add(key)
        patch,proof,before,after = render_texture(spec,parents)
        (revised if proof['revised'] else new).append(patch)
        evidence.append(proof)
        if previews:
            images.append((spec,proof,before,after))
    new.extend(literals)
    if previews:
        export_previews(images)
    return revised,new,evidence


def export_previews(images):
    Image = pillow()
    from PIL import ImageDraw
    FOLDER.mkdir(exist_ok=True)
    panels,words = [],[]
    for spec,proof,before,after in images:
        meta = proof['texture']
        colors = palette(before,meta)
        def rgb(record):
            pixels = unpack_indices(record,meta)
            return Image.frombytes('RGB',(meta['width'],meta['height']),bytes(v for i in pixels for v in colors[i][:3]))
        old,current = rgb(before),rgb(after)
        if 'panel' in spec:
            tile = Image.new('RGB',(1024,420),(25,25,25))
            tile.paste(old.crop((0,0,512,400)),(0,20))
            tile.paste(current.crop((0,0,512,400)),(512,20))
            ImageDraw.Draw(tile).text((4,3),f"{Path(spec['resource']).stem} @{spec['offset']:x}: Original / PT-BR",fill='white')
            panels.append(tile)
        if 'cloth' in spec:
            tile = Image.new('RGB',(1024,300),(25,25,25))
            tile.paste(old.crop((0,40,512,320)),(0,20))
            tile.paste(current.crop((0,40,512,320)),(512,20))
            ImageDraw.Draw(tile).text((4,3),f"Mesa @{spec['offset']:x}: Original / PT-BR",fill='white')
            words.append(tile)
        for label_spec in spec['labels']:
            rect = label_spec['rect']
            a,b = old.crop(rect),current.crop(rect)
            scale = min(2,max(1,200//max(a.width,1)))
            a=a.resize((a.width*scale,a.height*scale),Image.Resampling.NEAREST)
            b=b.resize(a.size,Image.Resampling.NEAREST)
            tile = Image.new('RGB',(1024,max(a.height+22,58)),(30,30,30))
            tile.paste(a,(4,20));tile.paste(b,(516,20))
            ImageDraw.Draw(tile).text((4,2),f"{Path(spec['resource']).stem} @{spec['offset']:x} {label_spec['text']!r}",fill='white')
            words.append(tile)
    for kind,tiles,batch in [('regras',panels,3),('rotulos',words,12)]:
        for page in range(0,len(tiles),batch):
            selected = tiles[page:page+batch]
            board = Image.new('RGB',(1024,sum(t.height for t in selected)),(30,30,30))
            y = 0
            for tile in selected:
                board.paste(tile,(0,y));y+=tile.height
            board.save(FOLDER/f'{kind}-{page//batch:02}.png')


def binding_load(binding):
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:
        raise ValueError('Unknown all-minigames binding')
    raw=(ROOT/MANIFEST).read_bytes();manifest=json.loads(raw)
    if (sha(raw)!=binding['sha256'] or manifest['policy']!=POLICY
        or manifest['parent_sha256']!=sha((ROOT/PARENT).read_bytes())
        or manifest['content_sha256']!=sha((ROOT/CONTENT).read_bytes())
        or manifest['fonts']!={k:sha(p.read_bytes()) for k,p in FONTS.items()}):
        raise ValueError('All-minigames manifest/source/font mismatch')
    return manifest


def validate(recipe):
    manifest=binding_load(recipe['all_minigames_release'])
    parent=json.loads((ROOT/PARENT).read_bytes());expected=copy.deepcopy(parent)
    expected.update(all_minigames_release=recipe['all_minigames_release'],iso_name='MetalSaga-ptbr-interface-v068.iso',status=STATUS)
    if expected!=recipe:
        raise ValueError('Unrelated all-minigames recipe mutation')
    return parent,manifest


def compile_interface(elf,recipe):
    from interface_text import compile_draft
    parent,manifest=validate(recipe)
    parents,report=compile_draft(elf,parent)
    revised,new,evidence=derive(elf,parents)
    if (manifest['revised']!=[metadata(p) for p in revised] or manifest['new']!=[metadata(p) for p in new]
        or manifest['evidence']!=evidence):
        raise ValueError('All-minigames output drift')
    replacements={p['id']:p for p in revised}
    patches=[replacements.get(p['id'],p) for p in parents]
    for patch in new:
        if any(p['resource']==patch['resource'] and max(p['offset'],patch['offset']) < min(p['offset']+len(p['before']),patch['offset']+len(patch['before'])) for p in patches):
            raise ValueError('New minigame patch overlaps inherited data')
        patches.append(patch)
    captions=sum(len(e.get('cloth',{}).get('arcs',[])) for e in evidence)
    units=sum(len(e['words'])+bool(e['instructions']) for e in evidence)+len(elf_specs())+captions
    report=copy.deepcopy(report)
    report['accepted']+=units
    report['all_minigames_release']={'policy':POLICY,'authored_units':units,
        'texture_planes':len(evidence),'word_cells':sum(len(e['words']) for e in evidence),
        'instruction_panels':sum(bool(e['instructions']) for e in evidence),'elf_literals':len(elf_specs()),
        'table_captions':captions,
        'pcsx2_executed':False,'visual_status':'pending_user'}
    return patches,report


def prepare():
    from interface_text import compile_draft
    elf=ELF.read_bytes();parent=json.loads((ROOT/PARENT).read_bytes())
    parents,_=compile_draft(elf,parent)
    revised,new,evidence=derive(elf,parents,previews=True)
    manifest={'schema':1,'policy':POLICY,'parent':PARENT,'parent_sha256':sha((ROOT/PARENT).read_bytes()),
              'content':CONTENT,'content_sha256':sha((ROOT/CONTENT).read_bytes()),
              'fonts':{k:sha(p.read_bytes()) for k,p in FONTS.items()},
              'revised':[metadata(p) for p in revised],'new':[metadata(p) for p in new],'evidence':evidence}
    raw=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
    (ROOT/MANIFEST).write_bytes(raw)
    child=copy.deepcopy(parent)
    child.update(all_minigames_release={'recipe':MANIFEST,'sha256':sha(raw)},iso_name='MetalSaga-ptbr-interface-v068.iso',status=STATUS)
    (ROOT/CHILD).write_bytes((json.dumps(child,ensure_ascii=False,indent=2)+'\n').encode())
    validate(child)
    print(json.dumps({'texture_planes':len(evidence),'words':sum(len(e['words']) for e in evidence),
                      'panels':sum(bool(e['instructions']) for e in evidence),'elf_literals':len(elf_specs())}))


if __name__=='__main__':
    prepare()
