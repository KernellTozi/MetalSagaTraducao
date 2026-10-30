"""Pinned compressed combat TIM2 labels; same slots, palette and dimensions.

FBS_DATA is a separate field atlas. Live battle uses entries 1589/1594 of
MMBATTLE.BIN. No generic TIM2 importer or expansion permission is provided.
"""
import copy
import hashlib
import json
import struct
from functools import lru_cache
from dialogue import ROOT, sha
from glyph_spacing import ORIGINAL_SHA
from discover_credits import decode, execute_decoder_loop
from credits_edit_pack import compress

POLICY = 'battle-compressed-tim2-fixed-labels-v001'
RESOURCE = 'DATA/MMBATTLE/MMBATTLE.BIN'
PARENT = 'translations/interface-v054.json'
MANIFEST = 'translations/batalha-grafica-v001.json'
STATUS = 'Menu real de batalha e cinco estados; nomes de armas somente para revisão.'
WINDOWS = ((0x10917c, 0x1091a4), (0x109244, 0x10926c),
           (0x19b780, 0x19b910))
# Only the lettering interiors are writable. Borders/icons/MAIN/SUB/SE/Item stay.
LABELS = {
    1589: [(6, 'Habil.', (38,139,80,157),136,164,16),
           (7, 'Equip.', (94,139,136,157),136,164,16),
           (8, 'Munição', (150,139,192,157),136,164,16),
           (10,'Fugir', (94,171,136,189),136,164,16),
           (11,'Dirigir',(150,171,192,189),136,164,16),
           (12,'Arma', (206,107,248,125),136,164,16),
           (13,'Passar',(206,139,248,157),136,164,16),
           (14,'Defesa',(206,171,248,189),136,164,16)],
    1594: [(0,'Fogo',(2,94,30,106),190,218,12),
           (1,'Ácido',(42,94,70,106),190,218,12),
           (2,'Veneno',(82,94,110,106),190,218,11),
           (3,'Atord.',(122,94,150,106),190,218,12),
           (4,'Caído',(162,94,190,106),190,218,12),
           (5,'Habil.',(1,66,21,77),124,226,10)]}


def instruction_bindings(elf):
    if sha(elf) != ORIGINAL_SHA:
        raise ValueError('Battle atlas ELF differs')
    # Actual loader IDs, not inferred solely from visual resemblance.
    for at, index in ((0x109180,1589),(0x109248,1594)):
        if struct.unpack_from('<I',elf,at)[0] != 0x24020000 | index:
            raise ValueError('Original combat texture selector differs')
    return [{'offset':a,'size':b-a,'sha256':sha(elf[a:b])} for a,b in WINDOWS]


def sources():
    path=ROOT/'JOGO/Metal Saga'/RESOURCE
    expected=next(r for r in json.loads((ROOT/'reports/inventory.json').read_bytes()) if r['path']==RESOURCE)
    with path.open('rb') as f:
        if hashlib.file_digest(f,'sha256').hexdigest()!=expected['sha256']:
            raise ValueError('Original MMBATTLE differs')
        f.seek(0);directory=f.read(0x3400);result={}
        for index in LABELS:
            size,offset=struct.unpack_from('<II',directory,index*8)
            if offset<0x3400 or offset+size>expected['size']:
                raise ValueError('Combat directory extent outside file')
            f.seek(offset);slot=f.read(size)
            if len(slot)!=size:raise ValueError('Truncated combat slot')
            result[index]=(offset,slot)
    return expected['sha256'],sha(directory),result


def tim2(raw):
    # Exactly this game's two single-picture, linear 8-bit 256x256 atlases.
    if len(raw)!=66624 or raw[:16]!=bytes.fromhex('54494d32040001000000000000000000'):
        raise ValueError('Unsupported combat TIM2 envelope')
    values=struct.unpack_from('<IIIHHBBBBHH',raw,16)
    if values!=(66608,1024,65536,48,256,0,1,3,5,256,256):
        raise ValueError('Unsupported TIM2 picture/palette layout')
    palette=[tuple(raw[65600+i*4:65604+i*4]) for i in range(256)]
    # CSM1 CLUT swaps groups of eight; indices themselves stay linear.
    palette=[palette[(i&231)|((i&8)<<1)|((i&16)>>1)] for i in range(256)]
    return raw[64:65600],palette


def render(raw,index):
    from interface_graphics import mask
    pixels,palette=tim2(raw);out=bytearray(pixels);layouts=[]
    for key,text,rect,bg,fg,height in LABELS[index]:
        x,y,z,w=rect;glyph,layout=mask(text,height,z-x)
        if height>w-y:raise ValueError('Battle label height overflow')
        if palette[bg][3]!=palette[fg][3]:raise ValueError('Battle opacity differs')
        colors=[]
        for coverage in range(256):
            # Four coverage levels suit the original small pixel lettering and
            # avoid inventing hundreds of slightly different palette choices.
            coverage=round(coverage/85)*85
            rgb=[round(palette[bg][k]+(palette[fg][k]-palette[bg][k])*coverage/255) for k in range(3)]
            colors.append(min((i for i,p in enumerate(palette) if p[3]==palette[bg][3]),
                              key=lambda i:sum((palette[i][k]-rgb[k])**2 for k in range(3))))
        for yy in range(y,w):out[yy*256+x:yy*256+z]=bytes([bg])*(z-x)
        ox=x+(z-x-glyph.width)//2;oy=y+(w-y-height)//2
        for yy in range(height):
            for xx in range(glyph.width):out[(oy+yy)*256+ox+xx]=colors[glyph.getpixel((xx,yy))]
        layouts.append({'id':f'battle.atlas.{index}.{key:02d}','translation':text,
                        'rect':list(rect),**layout})
    for at,(a,b) in enumerate(zip(pixels,out)):
        if a!=b and not any(x<=at%256<z and y<=at//256<w for _,_,(x,y,z,w),_,_,_ in LABELS[index]):
            raise ValueError('Combat edit outside lettering rectangles')
    after=raw[:64]+bytes(out)+raw[65600:]
    if after[:64]!=raw[:64] or after[65600:]!=raw[65600:]:
        raise ValueError('TIM2 header/palette altered')
    return after,layouts


def template(elf):
    source_hash,directory_hash,slots=sources();entries=[]
    for index,(offset,slot) in slots.items():
        raw,used,_=decode(slot,maximum=66624)
        if any(slot[used:]):raise ValueError('Unknown nonzero compressed tail')
        _,labels=render(raw,index)
        entries.append({'index':index,'offset':offset,'size':len(slot),'slot_sha256':sha(slot),
                        'decoded_sha256':sha(raw),'labels':labels})
    return {'schema':1,'policy':POLICY,'resource':RESOURCE,'source_sha256':source_hash,
            'directory_sha256':directory_hash,'parent_recipe':PARENT,
            'parent_sha256':sha((ROOT/PARENT).read_bytes()),
            'instruction_windows':instruction_bindings(elf),'entries':entries}


def validate_interface(recipe):
    binding=recipe['battle_atlas_release']
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:
        raise ValueError('Unknown combat atlas binding')
    raw=(ROOT/MANIFEST).read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('Combat manifest differs')
    manifest=json.loads(raw);parent_raw=(ROOT/PARENT).read_bytes();parent=json.loads(parent_raw)
    if manifest.get('parent_recipe')!=PARENT or manifest.get('parent_sha256')!=sha(parent_raw):
        raise ValueError('Combat parent differs')
    expected=copy.deepcopy(parent)
    expected.update(battle_atlas_release=binding,iso_name='MetalSaga-ptbr-interface-v055.iso',status=STATUS)
    if recipe!=expected:raise ValueError('Unrelated change in combat atlas child')
    return parent,manifest


@lru_cache(maxsize=4)
def _recompress(raw):
    return compress(raw,maximum=66624)


def compile_slots(elf,manifest):
    if manifest!=template(elf):raise ValueError('Combat source/layout/masks differ')
    _,_,slots=sources();patches=[];results=[]
    for index,(offset,slot) in slots.items():
        before,used,_=decode(slot,maximum=66624);after,labels=render(before,index)
        packed=_recompress(after)
        if len(packed)>len(slot):raise ValueError('Compressed combat atlas exceeds original slot')
        checked,consumed,_=decode(packed,maximum=66624)
        actual,actual_used,steps=execute_decoder_loop(elf,packed,maximum=66624)
        if checked!=after or actual!=after or consumed!=len(packed) or actual_used!=consumed:
            raise ValueError('Original decoder combat roundtrip differs')
        patches.append({'id':f'battle.tim2.{index}','resource':RESOURCE,'offset':offset,
                        'before':slot,'after':packed+bytes(len(slot)-len(packed))})
        results.append({'index':index,'offset':offset,'slot_size':len(slot),
                        'original_consumed':used,'packed_size':len(packed),
                        'remaining_slot_bytes':len(slot)-len(packed),'decoded_size':len(after),
                        'decoded_sha256':sha(after),'original_decoder_steps':steps,'labels':labels})
    return patches,{'policy':POLICY,'accepted':sum(len(r['labels']) for r in results),
                    'source_sha256':manifest['source_sha256'],'results':results,
                    'headers_palettes_dimensions_directory_unchanged':True,
                    'original_decoder_roundtrip':True,'pcsx2_executed':False,
                    'visual_validation':'pending_user'}


def compile_interface(elf,recipe):
    from interface_text import compile_draft
    parent,manifest=validate_interface(recipe);patches,report=compile_draft(elf,parent)
    additions,evidence=compile_slots(elf,manifest);report=copy.deepcopy(report)
    report['battle_atlas_release']=evidence
    report['accepted']+=evidence['accepted']
    return patches+additions,report


def export_comparison(elf,recipe,output):
    from interface_texture_pack import pillow
    Image=pillow()
    from PIL import ImageDraw
    _,manifest=validate_interface(recipe);patches,report=compile_slots(elf,manifest)
    output.mkdir(parents=True,exist_ok=True)
    for patch in patches:
        index=int(patch['id'].rsplit('.',1)[1]);images=[]
        for key in ('before','after'):
            raw,_,_=decode(patch[key]);pixels,palette=tim2(raw)
            image=Image.frombytes('RGB',(256,256),bytes(c for i in pixels for c in palette[i][:3]))
            image.save(output/f'{index}-{key}.png')
            crop=image.crop((32,100,256,194) if index==1589 else (0,90,192,110))
            images.append(crop.resize((crop.width*3,crop.height*3),Image.Resampling.NEAREST))
        sheet=Image.new('RGB',(max(i.width for i in images),sum(i.height for i in images)+48),'#303030')
        y=0
        for label,image in zip(('Original','Proposta aplicada'),images):
            ImageDraw.Draw(sheet).text((4,y+3),label,fill='white');sheet.paste(image,(0,y+22));y+=image.height+24
        sheet.save(output/f'comparacao-{index}.png')
    return report
