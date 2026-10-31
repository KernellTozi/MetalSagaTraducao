"""Bounded effect word artwork in two original compressed combat TIM2 slots.

Draw whole words, using a locally installed font. No game fonts or palette
entries are changed. Each replacement stays inside the original ink bounds:
there is no inferred extra UV room, texture expansion or executable patch.
Ambiguous labels remain verbatim until their consumers are understood.
"""
import copy
from functools import lru_cache
import json
from pathlib import Path
import struct

from dialogue import ROOT, sha
from glyph_spacing import ORIGINAL_SHA
from battle_menu_atlas import RESOURCE, tim2, _recompress
from discover_credits import decode, execute_decoder_loop
from interface_texture_pack import pillow

POLICY = 'battle-effect-original-ink-bounds-v001'
PARENT = 'translations/interface-v058.json'
MANIFEST = 'translations/batalha-efeitos-v001.json'
STATUS = 'Efeitos de batalha em atlas originais; termos ambíguos preservados.'
FONT = Path('C:/Windows/Fonts/impact.ttf')
# Cells isolate the observed original words, not a release of unused space.
# The renderer further restricts writing to the nontransparent ink bounding box.
CELLS = {
    1587: [
        ('fire', 'Fogo', (8,6,50,30)),
        ('acid', 'Ácido', (58,6,88,30)),
        ('shutdown', 'Pane', (92,6,180,30)),
        ('dummy', None, (186,6,249,30)),
        ('venom', 'Veneno', (3,42,32,55)),
        ('stun', 'Atord.', (42,36,81,57)),
        ('hp', None, (92,34,128,61)),
        ('recovered', 'Recuperado', (132,38,187,56)),
        ('up', None, (190,32,234,62)),
        ('down', None, (3,63,83,92)),
        ('drive', 'Dirigir', (85,65,140,90)),
        ('turn-rate', 'Iniciativa', (143,65,232,90)),
        ('attack', 'Ataque', (10,95,77,120)),
        ('defense', 'Defesa', (84,95,166,120)),
        ('durability', 'Durab.', (168,99,220,117)),
        ('critical-rate', 'Taxa crítica', (5,127,101,149)),
        ('all-parts', 'Todas as peças', (102,124,186,150)),
        ('broken', 'Quebrado', (192,127,248,149)),
        ('main', None, (3,154,59,181)),
        ('sub', None, (64,154,107,181)),
        ('se', None, (117,154,153,182)),
        ('evade-rate', 'Esquiva', (158,159,239,180)),
        ('engine', 'Motor', (16,184,85,210)),
        ('chassis', None, (105,184,184,210)),
        ('sp', None, (196,183,234,211)),
        ('c-unit', None, (22,214,92,241)),
        ('hit-rate', 'Precisão', (112,216,188,241)),
        ('fastest', 'Mais rápido', (193,218,249,240)),
    ],
    1588: [
        ('recovery-2x', 'Recuperação 2x', (2,2,149,32)),
        ('hit-rate', 'Precisão', (151,2,230,32)),
        ('act-twice', 'Ação dupla', (5,36,94,58)),
        ('normal', None, (100,37,148,57)),
        ('out-of-range', 'Fora de alcance', (154,39,233,58)),
        ('melee-protection', 'Proteção corpo a corpo', (8,66,172,89)),
        ('airborne', 'No ar', (176,68,230,88)),
        ('ranged-protection', 'Proteção a distância', (9,96,170,120)),
        ('underground', 'Subsolo', (177,102,231,118)),
        ('damage-override', None, (14,121,191,153)),
        ('high-altitude', 'Alta altitude', (5,158,82,177)),
        ('underwater', 'Submerso', (87,161,139,177)),
        ('stealth', 'Furtivo', (151,155,225,179)),
        ('shelter', 'Abrigo', (20,184,94,211)),
        ('damaged', 'Danificado', (111,187,165,207)),
        ('broken', 'Quebrado', (167,187,220,207)),
        ('protector', 'Protetor', (21,215,121,241)),
        ('decoy', 'Isca', (141,215,208,241)),
    ],
}
PENDING = {1587: ['dummy', 'up', 'down'], 1588: ['damage-override']}


def instruction_bindings(elf):
    if sha(elf) != ORIGINAL_SHA:
        raise ValueError('Effect atlas original ELF differs')
    for at, index in ((0x109108,1587), (0x109130,1588)):
        if struct.unpack_from('<I',elf,at)[0] != (0x24020000 | index):
            raise ValueError('Effect atlas loader selector differs')
    return [{'offset':a, 'size':z-a, 'sha256':sha(elf[a:z])}
            for a,z in ((0x109104,0x109154),(0x19b780,0x19b910))]


def sources():
    expected = next(r for r in json.loads((ROOT/'reports/inventory.json').read_bytes())
                    if r['path'] == RESOURCE)
    import hashlib
    with (ROOT/'JOGO/Metal Saga'/RESOURCE).open('rb') as f:
        if hashlib.file_digest(f,'sha256').hexdigest() != expected['sha256']:
            raise ValueError('Effect atlas resource differs')
        f.seek(0);directory = f.read(0x3400)
        result = {}
        for index in CELLS:
            size,offset = struct.unpack_from('<II',directory,index*8)
            if offset < len(directory) or offset+size > expected['size']:
                raise ValueError('Invalid effect extent')
            f.seek(offset);slot=f.read(size)
            if len(slot)!=size:
                raise ValueError('Truncated effect extent')
            result[index]=(offset,slot)
    return expected['sha256'],sha(directory),result


def ink_bounds(pixels,palette,cell):
    x,y,z,w=cell
    coords=[(xx,yy) for yy in range(y,w) for xx in range(x,z)
            if palette[pixels[yy*256+xx]][3]]
    if not coords:
        raise ValueError('Empty original label')
    bounds=(min(p[0] for p in coords),min(p[1] for p in coords),
            max(p[0] for p in coords)+1,max(p[1] for p in coords)+1)
    # An opaque edge may mean an adjacent word or a clipped original.
    if any(a==b for a,b in zip(bounds,cell)):
        raise ValueError('Original lettering touches isolation cell edge')
    return bounds


@lru_cache(maxsize=128)
def word_mask(text,width,height):
    Image=pillow()
    from PIL import ImageDraw,ImageFont
    font=ImageFont.truetype(str(FONT),96)
    box=font.getbbox(text)
    mask=Image.new('L',(box[2]-box[0]+48,box[3]-box[1]+16))
    ImageDraw.Draw(mask).text((24-box[0],8-box[1]),text,font=font,fill=255)
    # Original effect words are bold and right-slanted. Build complete words,
    # rather than assembling fragments of the old texture.
    mask=mask.transform((mask.width+32,mask.height),Image.Transform.AFFINE,
                        (1,0.20,-0.20*mask.height,0,1,0),Image.Resampling.BICUBIC)
    mask=mask.crop(mask.getbbox())
    for target_height in range(height-2,max(1,height-5),-1):
        natural=max(1,round(mask.width*target_height/mask.height))
        target_width=min(width-2,natural)
        if target_width/natural>=0.70:
            break
    if target_width/natural < 0.70:
        raise ValueError(f'Effect word excessively compressed: {text}')
    mask=mask.resize((target_width,target_height),Image.Resampling.LANCZOS)
    out=Image.new('L',(width,height))
    out.paste(mask,((width-target_width)//2,height-1-target_height))
    return out,{'natural_width':natural,'rendered_width':target_width,
                'height':target_height,'height_reduction':height-2-target_height,
                'horizontal_scale':target_width/natural,
                'mask_sha256':sha(out.tobytes())}


def render(raw,index):
    Image=pillow()
    from PIL import ImageFilter
    pixels,palette=tim2(raw);out=bytearray(pixels);labels=[]
    transparent=[i for i,p in enumerate(palette) if p[3]==0]
    if not transparent:
        raise ValueError('No original transparent palette entry')
    bg=transparent[0]
    shades={v:min((i for i,p in enumerate(palette) if p[3]==128),
                  key=lambda i:sum((palette[i][k]-v)**2 for k in range(3)))
            for v in (0,85,170,255)}
    for key,text,cell in CELLS[index]:
        rect=ink_bounds(pixels,palette,cell)
        if text is None:
            continue
        x,y,z,w=rect;mask,layout=word_mask(text,z-x,w-y)
        outline=mask.filter(ImageFilter.MaxFilter(3))
        for yy in range(w-y):
            for xx in range(z-x):
                value=mask.getpixel((xx,yy))
                # Use only existing opaque grayscale entries and transparent
                # background. Four levels limit noise and compressed growth.
                color=bg if outline.getpixel((xx,yy))<48 else shades[round(value/85)*85]
                out[(y+yy)*256+x+xx]=color
        labels.append({'id':f'battle.effect.{index}.{key}', 'translation':text,
                       'isolation_cell':list(cell),'original_ink_rect':list(rect),**layout})
    permitted=[r['original_ink_rect'] for r in labels]
    for at,(a,b) in enumerate(zip(pixels,out)):
        if a!=b and not any(x<=at%256<z and y<=at//256<w for x,y,z,w in permitted):
            raise ValueError('Effect artwork escaped original ink bounds')
    return raw[:64]+bytes(out)+raw[65600:],labels


def template(elf):
    source_hash,directory_hash,slots=sources();entries=[]
    for index,(offset,slot) in slots.items():
        raw,used,_=decode(slot,maximum=66624)
        if any(slot[used:]):raise ValueError('Unknown effect slot tail')
        _,labels=render(raw,index)
        entries.append({'index':index,'offset':offset,'size':len(slot),
                        'slot_sha256':sha(slot),'decoded_sha256':sha(raw),'labels':labels})
    return {'schema':1,'policy':POLICY,'resource':RESOURCE,'source_sha256':source_hash,
            'directory_sha256':directory_hash,'parent_recipe':PARENT,
            'parent_sha256':sha((ROOT/PARENT).read_bytes()),
            'font':{'file':FONT.name,'sha256':sha(FONT.read_bytes()),
                    'use':'local whole-word rasterization; not an original game font'},
            'instruction_windows':instruction_bindings(elf),'entries':entries,
            'semantic_pending':{str(k):v for k,v in PENDING.items()}}


def validate_interface(recipe):
    binding=recipe['battle_effect_release']
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:
        raise ValueError('Unknown effect atlas binding')
    raw=(ROOT/MANIFEST).read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('Effect manifest differs')
    manifest=json.loads(raw);parent_raw=(ROOT/PARENT).read_bytes();parent=json.loads(parent_raw)
    if manifest.get('parent_recipe')!=PARENT or manifest.get('parent_sha256')!=sha(parent_raw):
        raise ValueError('Effect parent differs')
    expected=copy.deepcopy(parent)
    expected.update(battle_effect_release=binding,iso_name='MetalSaga-ptbr-interface-v059.iso',status=STATUS)
    if recipe!=expected:raise ValueError('Unrelated effect child change')
    return parent,manifest


def compile_slots(elf,manifest):
    if manifest!=template(elf):raise ValueError('Effect source/artwork binding differs')
    _,_,slots=sources();patches=[];results=[]
    for index,(offset,slot) in slots.items():
        before,used,_=decode(slot,maximum=66624);after,labels=render(before,index)
        packed=_recompress(after)
        if len(packed)>len(slot):raise ValueError('Compressed effect atlas exceeds original slot')
        checked,consumed,_=decode(packed,maximum=66624)
        actual,actual_used,steps=execute_decoder_loop(elf,packed,maximum=66624)
        if checked!=after or actual!=after or consumed!=len(packed) or actual_used!=consumed:
            raise ValueError('Original decoder effect roundtrip differs')
        patches.append({'id':f'battle.tim2.{index}','resource':RESOURCE,'offset':offset,
                        'before':slot,'after':packed+bytes(len(slot)-len(packed))})
        results.append({'index':index,'offset':offset,'slot_size':len(slot),
                        'original_consumed':used,'packed_size':len(packed),
                        'remaining_slot_bytes':len(slot)-len(packed),'decoded_size':len(after),
                        'decoded_sha256':sha(after),'original_decoder_steps':steps,'labels':labels})
    return patches,{'policy':POLICY,'accepted':sum(len(r['labels']) for r in results),
                    'results':results,'original_decoder_roundtrip':True,
                    'headers_palettes_dimensions_directory_unchanged':True,
                    'semantic_pending':manifest['semantic_pending'],
                    'pcsx2_executed':False,'visual_validation':'pending_user'}


def compile_interface(elf,recipe):
    from interface_text import compile_draft
    parent,manifest=validate_interface(recipe);patches,report=compile_draft(elf,parent)
    additions,evidence=compile_slots(elf,manifest);report=copy.deepcopy(report)
    report['battle_effect_release']=evidence;report['accepted']+=evidence['accepted']
    return patches+additions,report


def export_comparison(elf,manifest,output):
    Image=pillow()
    from PIL import ImageDraw
    patches,report=compile_slots(elf,manifest);output.mkdir(parents=True,exist_ok=True)
    for patch in patches:
        index=int(patch['id'].rsplit('.',1)[1]);images=[]
        for key in ('before','after'):
            raw,_,_=decode(patch[key]);pixels,palette=tim2(raw)
            im=Image.frombytes('RGBA',(256,256),bytes(c for i in pixels for c in
                (*palette[i][:3],min(255,palette[i][3]*2))))
            bg=Image.new('RGBA',im.size,'#77765a');bg.alpha_composite(im)
            bg=bg.convert('RGB').resize((512,512),Image.Resampling.NEAREST)
            bg.save(output/f'{index}-{key}.png');images.append(bg)
        sheet=Image.new('RGB',(1024,536),'#303030');draw=ImageDraw.Draw(sheet)
        draw.text((4,4),'Original',fill='white');draw.text((516,4),'Proposta PT-BR',fill='white')
        sheet.paste(images[0],(0,24));sheet.paste(images[1],(512,24))
        sheet.save(output/f'comparacao-{index}.png')
    return report


def prepare():
    from interface_text import SOURCE
    elf=SOURCE.read_bytes();manifest=template(elf)
    patches,report=compile_slots(elf,manifest)
    payload=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
    (ROOT/MANIFEST).write_bytes(payload)
    child=json.loads((ROOT/PARENT).read_bytes())
    child.update(battle_effect_release={'recipe':MANIFEST,'sha256':sha(payload)},
                 iso_name='MetalSaga-ptbr-interface-v059.iso',status=STATUS)
    (ROOT/'translations/interface-v059.json').write_bytes((json.dumps(child,ensure_ascii=False,indent=2)+'\n').encode())
    validate_interface(child)
    export_comparison(elf,manifest,ROOT/'work/batalha-atributos-v001')
    return report


if __name__=='__main__':
    print(json.dumps(prepare(),ensure_ascii=True,indent=2))
