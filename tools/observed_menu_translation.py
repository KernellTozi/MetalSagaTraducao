"""Screenshot-driven fixed ELF labels and three pinned indexed atlas regions.

No string relocation, archive expansion, global font edit or save modification.
"""
import copy
import json
import struct
from dialogue import ROOT, sha
from interface_text import SOURCE as ELF, references, sections, FORMAT
from interface_resources import original
from interface_texture_pack import unpack_indices, replace_indices, pillow
from interface_textures import inspect_texture
from glyph_spacing import ORIGINAL_SHA
from gfi import encode,decode

POLICY = 'observed-save-vehicle-vending-and-headers-fixed-v001'
PARENT = 'translations/interface-v060.json'
MANIFEST = 'translations/menus-observados-v001.json'
CHILD = 'translations/interface-v061.json'
STATUS = 'Avisos de tanque, salvamento, equipamento, teletransporte e máquina de venda; visual pendente.'
SPACK = 'DATA/S/S_PACK.SDA'
NDATA = 'DATA/NDATA/NDATA.SDA'
LITERALS = {
    0x3211f0: 'Nome    ', 0x321200: 'Nível   ',
    0x321210: 'Tempo   ', 0x321240: 'Salvo   ',
    0x32ed10: '\nSobrepeso', 0x32ed20: '\nChassi falhou',
    0x32ed30: '\nSem motor', 0x32ed48: '\nMotor falhou',
    0x32ed58: '\nSem C Unit', 0x32ed70: '\nC Unit falhou',
    0x32ed80: '%s\nimóvel:%s', 0x32b110: 'Equipamento',
    0x32b250: 'Comparar', 0x348f78: 'Vazio',
    0x32ff38: 'Mover',
}
SAVE = frozenset((0x3211f0, 0x321200, 0x321210, 0x321240))
ICONS = (b'$\x81\x81', b'$\x81\x7e', b'$\x81\x9b')
HEADERS = ((108, 114, 'CIDADES'), (156, 146, 'FROTA'), (168, 144, 'MEMBROS'))
VENDING = ('Acenda o centro', 'e ganhe um prêmio!')
WINDOWS = ((0xcb098,0xcb0b4),(0xcb118,0xcb12c),(0xcb178,0xcb18c),
           (0xcb260,0xcb294),(0x13b058,0x13b1a0),(0x1432a4,0x1432b4),
           (0x6cb94,0x6ce04))


def bindings(elf):
    if sha(elf) != ORIGINAL_SHA:
        raise ValueError('Observed menu ELF source differs')
    return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]


def literal_rows(elf):
    refs = references(elf, sections(elf))
    out = []
    for at, text in LITERALS.items():
        end = elf.find(b'\0',at)
        before = elf[at:end]
        after = encode(text)
        if at in SAVE:
            if before[8:10] != b'\x81F' or len(text)!=8 or len(before)>=16:
                raise ValueError('Save native colon/alignment differs')
            # Four independently referenced format cells are 16 bytes apart.
            # The printf caller consumes until NUL, not a fixed byte offset.
            # This permits the one extra encoded byte of í while retaining
            # eight visible prefix characters. Bind every spare byte and
            # reject interior address evidence instead of assuming free space.
            if any(elf[end:at+16]) or any(at+0xff000+i in refs for i in range(1,16)):
                raise ValueError('Save cell tail/interior reference differs')
            after += before[8:]
            before=elf[at:at+15]
        elif at == 0x32ff38:
            expected = b'Select:'+ICONS[0]+b' Buy:'+ICONS[1]+b' Exit:'+ICONS[2]
            if before != expected:
                raise ValueError('Vending command/icon source differs')
            after = b'Mover'+ICONS[0]+b' Comprar'+ICONS[1]+b' Sair'+ICONS[2]
        if len(after)>len(before) or b'\0' in after:
            raise ValueError('Observed label exceeds original fixed slot')
        if FORMAT.findall(before)!=FORMAT.findall(after) or before.count(b'\n')!=after.count(b'\n'):
            raise ValueError('Observed label format/newline changed')
        if at==0x32ff38 and any(after.count(token)!=1 for token in ICONS):
            raise ValueError('Original controller icon changed')
        out.append({'id':f'observed.elf.{at:08x}','offset':at,'size':len(before)+1,
                    'source_sha256':sha(before+b'\0'),'translation':text,
                    'target_hex':after.hex(),'target_bytes':len(after),
                    'references':refs.get(at+0xff000,[])})
    return out


def header_glyphs(record):
    """The native uppercase atlas is a raster font; retain each glyph's pixels."""
    meta,_=inspect_texture(record)
    pixels=unpack_indices(record,meta)
    # These original rows supply every letter of the three new complete labels.
    samples=((60,'NAMESTATUS',0,151),(96,'WANTEDNOTE',0,140),
             (156,'VEHICLELIST',0,147),(168,'MEMBERLIST',0,145),
             (240,'TARGETMONSTER',0,193))
    glyphs={}
    for y,letters,left,right in samples:
        groups=[]
        for x in range(left,right):
            if not any(pixels[yy*256+x]==253 for yy in range(y,y+10)):
                continue
            if not groups or x>groups[-1][-1]+1:groups.append([x])
            else:groups[-1].append(x)
        if len(groups)!=len(letters):
            raise ValueError('Native uppercase glyph segmentation differs')
        for char,cols in zip(letters,groups):
            if char not in glyphs:
                a,z=cols[0],cols[-1]+1
                glyphs[char]=(z-a,b''.join(pixels[(y+dy)*256+a:(y+dy)*256+z] for dy in range(10)))
    # F shares the native E's top/stem/middle; remove only its bottom bar.
    width,source=glyphs['E'];glyph=bytearray(source)
    glyph[9*width+3:10*width]=bytes([241])*(width-3)
    glyphs['F']=(width,bytes(glyph))
    return glyphs


def render_headers(raw):
    if struct.unpack_from('<I',raw,12+2*4)[0]!=0x8c800 or struct.unpack_from('<I',raw,0x8c80c)[0]!=48:
        raise ValueError('Header atlas SDA selector differs')
    start,end=0x8c830,0x9cc40
    record=raw[start:end];meta,_=inspect_texture(record)
    if (meta['width'],meta['height'],meta['bpp'])!=(256,256,8):
        raise ValueError('Header atlas geometry differs')
    glyphs=header_glyphs(record);pixels=bytearray(unpack_indices(record,meta));results=[]
    for y,right,text in HEADERS:
        width=sum(glyphs[c][0] for c in text)+3*(len(text)-1)
        if width>right-5:
            raise ValueError('Full native header exceeds original UV cell')
        for yy in range(y,y+12):pixels[yy*256+4:yy*256+right]=bytes([241])*(right-4)
        x=5
        for char in text:
            w,glyph=glyphs[char]
            for yy in range(10):pixels[(y+yy)*256+x:(y+yy)*256+x+w]=glyph[yy*w:(yy+1)*w]
            x+=w+3
        results.append({'translation':text,'rect':[4,y,right,y+12],'rendered_width':width,
                        'source_font':'Original S_PACK uppercase raster glyphs','scaling':False})
    rebuilt=replace_indices(record,pixels)
    return [{'id':'observed.headers','resource':SPACK,'offset':start+meta['pixel_offset'],
             'before':record[meta['pixel_offset']:meta['pixel_offset']+meta['pixel_bytes']],
             'after':rebuilt[meta['pixel_offset']:meta['pixel_offset']+meta['pixel_bytes']]}],results


def render_vending(raw):
    from interface_graphics import mask
    pillow();masks=[]
    for text in VENDING:
        image,layout=mask(text,16,182)
        masks.append((image,layout))
    # This instruction crosses the seam of the machine's two original textures.
    patches=[];results=[]
    root_count=struct.unpack_from('<I',raw,8)[0]
    if root_count<=15 or struct.unpack_from('<2I',raw,12+13*4)!=(0x97000,0xd7800):
        raise ValueError('Vending NDATA entry boundaries differ')
    for index,start,end,global_x in ((13,0x97000,0xd7800,0),(14,0xd7800,0xe8000,512)):
        record=raw[start:end];meta,_=inspect_texture(record)
        if (meta['width'],meta['height'],meta['bpp'])!=((512 if index==13 else 128),512,8):
            raise ValueError('Vending source geometry differs')
        palette=[tuple(record[16+4*i:20+4*i]) for i in range(256)]
        pixels=bytearray(unpack_indices(record,meta));width=meta['width']
        left=max(453-global_x,0);right=min(606-global_x,width)
        # Keep transparent black for the background and the original opaque
        # ink alpha for nonzero coverage. The wall to the right stays untouched.
        bg=min(range(256),key=lambda i:sum(palette[i][:3]))
        alpha=128
        colors=[min((i for i,p in enumerate(palette) if p[3]==alpha),
                    key=lambda i:sum((palette[i][k]-v)**2 for k in range(3))) for v in range(256)]
        colors[0]=bg
        for y in range(312,348):pixels[y*width+left:y*width+right]=bytes([bg])*(right-left)
        for line,(image,layout) in enumerate(masks):
            for yy in range(image.height):
                for xx in range(image.width):
                    x=453+xx-global_x;y=312+line*18+yy
                    if left<=x<right:pixels[y*width+x]=colors[image.getpixel((xx,yy))]
        rebuilt=replace_indices(record,pixels)
        patches.append({'id':f'observed.vending.{index}','resource':NDATA,
                        'offset':start+meta['pixel_offset'],
                        'before':record[meta['pixel_offset']:meta['pixel_offset']+meta['pixel_bytes']],
                        'after':rebuilt[meta['pixel_offset']:meta['pixel_offset']+meta['pixel_bytes']]})
        results.append({'entry':index,'rect':[left,312,right,348],'background_index':bg,
                        'alpha':alpha,'lines':list(VENDING),'layout':[v for _,v in masks]})
    return patches,results


def compile_additions(elf):
    bindings(elf);rows=literal_rows(elf);patches=[]
    for row in rows:
        at=row['offset'];before=elf[at:at+row['size']];value=bytes.fromhex(row['target_hex'])
        patches.append({'id':row['id'],'resource':'SLUS_212.93','offset':at,
                        'before':before,'after':value+bytes(len(before)-len(value))})
    header_patches,headers=render_headers(original(SPACK));patches+=header_patches
    vending_patches,vending=render_vending(original(NDATA));patches+=vending_patches
    return patches,{'literal_rows':rows,'headers':headers,'vending':vending}


def template(elf):
    patches,report=compile_additions(elf)
    return {'schema':1,'policy':POLICY,'parent_recipe':PARENT,
            'parent_sha256':sha((ROOT/PARENT).read_bytes()),'elf_sha256':ORIGINAL_SHA,
            'instruction_windows':bindings(elf),
            'resources':{r:sha(original(r)) for r in (SPACK,NDATA)},'evidence':report,
            'patches':[{'id':p['id'],'resource':p['resource'],'offset':p['offset'],
                        'size':len(p['before']),'before_sha256':sha(p['before']),
                        'after_sha256':sha(p['after'])} for p in patches]}


def validate_interface(recipe):
    binding=recipe['observed_menu_release']
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:
        raise ValueError('Unknown observed menu manifest')
    raw=(ROOT/MANIFEST).read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('Observed menu manifest differs')
    manifest=json.loads(raw);parent=json.loads((ROOT/PARENT).read_bytes())
    expected=copy.deepcopy(parent)
    expected.update(observed_menu_release=binding,iso_name='MetalSaga-ptbr-interface-v061.iso',status=STATUS)
    if recipe!=expected or manifest['parent_recipe']!=PARENT or manifest['parent_sha256']!=sha((ROOT/PARENT).read_bytes()):
        raise ValueError('Unrelated observed menu child/parent mutation')
    return parent,manifest


def compile_interface(elf,recipe):
    from interface_text import compile_draft
    parent,manifest=validate_interface(recipe)
    if manifest!=template(elf):raise ValueError('Observed menu source/render/proof differs')
    patches,report=compile_draft(elf,parent);additions,evidence=compile_additions(elf)
    for p in additions:
        if any(q['resource']==p['resource'] and max(p['offset'],q['offset'])<min(p['offset']+len(p['before']),q['offset']+len(q['before'])) for q in patches):
            raise ValueError('Observed menu overlaps previous translation')
    report=copy.deepcopy(report);report['accepted']+=20
    report['observed_menu_release']={'policy':POLICY,'new_units':20,'elf_literals':15,
        'native_headers':3,'vending_lines':2,'evidence':evidence,
        'category_expansion_applied':False,'pcsx2_executed':False,'visual_status':'pending_user'}
    return patches+additions,report


def prepare():
    elf=ELF.read_bytes();manifest=template(elf)
    raw=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
    (ROOT/MANIFEST).write_bytes(raw)
    child=json.loads((ROOT/PARENT).read_bytes())
    child.update(observed_menu_release={'recipe':MANIFEST,'sha256':sha(raw)},
                 iso_name='MetalSaga-ptbr-interface-v061.iso',status=STATUS)
    (ROOT/CHILD).write_bytes((json.dumps(child,ensure_ascii=False,indent=2)+'\n').encode())
    validate_interface(child)
    return {'new_units':20,'fixed_literals':15,'headers':3,'vending_lines':2}


def previews():
    Image=pillow()
    from PIL import ImageDraw
    folder=ROOT/'work/interface-v061-previews';folder.mkdir(exist_ok=True)
    additions,_=compile_additions(ELF.read_bytes())
    rebuilt={r:bytearray(original(r)) for r in (SPACK,NDATA)}
    for p in additions:
        if p['resource'] in rebuilt:
            rebuilt[p['resource']][p['offset']:p['offset']+len(p['after'])]=p['after']
    def rgb(raw,start,end):
        meta,pixels=inspect_texture(raw[start:end])
        return Image.frombytes('RGB',(meta['width'],meta['height']),pixels)
    headers=Image.new('RGB',(900,155),(30,30,30));draw=ImageDraw.Draw(headers)
    for column,raw in enumerate((original(SPACK),rebuilt[SPACK])):
        image=rgb(raw,0x8c830,0x9cc40)
        draw.text((column*450+8,5),'Original' if column==0 else 'PT-BR',fill='white')
        for i,(top,right,_) in enumerate(HEADERS):
            crop=image.crop((4,top,right,top+12))
            headers.paste(crop.resize(((right-4)*3,36),Image.Resampling.NEAREST),(column*450+8,25+i*42))
    headers.save(folder/'cabecalhos.png')
    vending=Image.new('RGB',(640,240),(30,30,30));draw=ImageDraw.Draw(vending)
    for line,raw in enumerate((original(NDATA),rebuilt[NDATA])):
        image=Image.new('RGB',(640,512))
        image.paste(rgb(raw,0x97000,0xd7800),(0,0))
        image.paste(rgb(raw,0xd7800,0xe8000),(512,0))
        crop=image.crop((355,305,640,355)).resize((570,100),Image.Resampling.NEAREST)
        vending.paste(crop,(5,20+line*120))
        draw.text((5,line*120),'Original' if line==0 else 'PT-BR',fill='white')
    vending.save(folder/'maquina.png')
    return {'previews':folder.relative_to(ROOT).as_posix(),'gpu_render':False}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description='Preparar lote observado ou comparações locais, sem alterar ISO')
    parser.add_argument('--previews',action='store_true')
    args=parser.parse_args()
    print(json.dumps(previews() if args.previews else prepare()))
