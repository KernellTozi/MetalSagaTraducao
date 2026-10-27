"""Single approved-scope loading label; original dimensions/palette/GANM.

Authored rectangular letter strokes match the original stencil proportions.
Only RLOADING entry 2 pixels are eligible. Posters/minigame titles untouched.
"""
import argparse,json,struct
from pathlib import Path
from reinsertion import ROOT,local
from interface_resources import original
from interface_text import SOURCE
from glyph_spacing import ORIGINAL_SHA
from dialogue import sha
from interface_texture_pack import pillow,unpack_indices,replace_indices
from interface_textures import inspect_texture
from speaker_labels import _run

POLICY='loading-carregando-original-palette-fixed-sprite-v001'
RESOURCE='DATA/RDATA/RLOADING.SDA'
START,SIZE,GANM=0x8d0,0x1050,0x1920
TEXT='Carregando'
TARGET_TEXTURE_SHA='bf027e233e710e714c05c0bc09640f303e9837509b699e550f65f8fabfdfb1a4'
INK=(6,7,8,11,12,13,14,15)
WINDOWS=((0x17524c,0x175254),(0x1752dc,0x17533c),
    (0x175650,0x17565c),(0x175678,0x17567c),(0x17571c,0x175720),
    (0x19af90,0x19afa4))
DATA_WINDOWS=((0x268788,0x2687f8),(0x33ada8,0x33adc8))


def bindings(elf):
    return [{'kind':'code' if (a,z) in WINDOWS else 'data','offset':a,'size':z-a,
        'sha256':sha(elf[a:z])} for a,z in WINDOWS+DATA_WINDOWS]


def proof(elf,raw):
    if sha(elf)!=ORIGINAL_SHA or sha(raw)!=sha(original(RESOURCE)):
        raise ValueError('Loading original source differs')
    if raw[:4]!=b'sda\0' or struct.unpack_from('<I',raw,8)[0]!=4:
        raise ValueError('Loading SDA header differs')
    if struct.unpack_from('<4I',raw,12)!=(0x20,0x870,START,GANM):raise ValueError('Loading entry boundaries differ')
    if struct.unpack_from('<4sIII',raw,GANM)!=(b'ganm',1,16,32):raise ValueError('Loading GANM header differs')
    if struct.unpack_from('<8h',raw,GANM+16)!=(0,0,256,32,128,16,0,0):raise ValueError('Loading full-word sprite differs')
    owner=bytearray(0xd30);struct.pack_into('<I',owner,0xcf0,0x600000);stack=bytearray(16)
    table=elf[0x268788:0x2687f8];regions=[(0x620000,owner),(0x640000,stack),(0x367788,table)]
    cases=[]
    for i,(texture,size,ganm) in enumerate(((0x20,0x850,0x870),(START,SIZE,GANM))):
        at=0x268788+i*56
        if struct.unpack_from('<4I',elf,at+32)!=(texture,size,ganm,0x60 if i==0 else 0x20):
            raise ValueError('Loading descriptor tuple differs')
        r=[0]*32;r[20]=0x620000;r[16]=at+0xff000;r[17]=0x620850+i*0x150
        r[18]=0x620af0+i*64;r[29]=0x640000
        r=_run(elf,0x1752dc,WINDOWS,r,regions,0x1acc58)
        if (r[4],r[5],r[7])!=(0x620850+i*0x150,0x600000+texture,size):
            raise ValueError('Loading texture upload arguments differ')
        r=_run(elf,0x17532c,WINDOWS,r,regions,0x19af80)
        if (r[4],r[5])!=(0x620af0+i*64,0x600000+ganm):raise ValueError('Loading GANM arguments differ')
        cases.append({'descriptor_offset':at,'texture_offset':texture,'texture_size':size,'ganm_offset':ganm})
    r=[0]*32;r[18]=0x620000;r[16]=0x650000;r[17]=0x620c60
    _run(elf,0x175650,WINDOWS,r,[(0x620000,owner)],0x17565c)
    if struct.unpack_from('<I',owner,0xc80)[0]!=0x6209a0:raise ValueError('Loading drawing texture owner differs')
    r=[0]*32;r[18]=0x620000
    r=_run(elf,0x175678,WINDOWS,r,[],0x17567c)
    if r[16]!=0x620b30:raise ValueError('Loading drawing GANM owner differs')
    struct.pack_into('<I',owner,0xb3c,0x600000+GANM+16)
    r=[0]*32;r[16]=0x620b30
    r=_run(elf,0x17571c,WINDOWS,r,[(0x620000,owner)],0x175720)
    if r[4]!=0x600000+GANM+16:raise ValueError('Loading first sprite pointer differs')
    filename=elf[0x33ada8:0x33adc8].split(b'\0',1)[0]
    if filename!=b'\\data\\rdata\\rLoading.sda':raise ValueError('Loading source path differs')
    r=[0]*32;r[5]=0x440000
    r=_run(elf,0x17524c,WINDOWS,r,[],0x78338)
    if r[5]!=0xff000+0x33ada8:raise ValueError('Loading source name forwarding differs')
    return {'source_path_data_verified':True,'descriptor_cases':cases,'original_scalar_forwarding_cases':8,
        'drawing_texture_owner_offset':0x9a0,'drawing_ganm_owner_offset':0xb30,
        'sprite_count':1,'sprite_rect':[0,0,256,32],'sprite_hotspot':[128,16],
        'limits':'Eight bounded original integer forwarding snippets; source/owner/stack and manager pointer supplied. Full file load, GPU, FPU animation and PCSX2 not executed.'}


def letter(char):
    """Integer rectangles; native 4px stems, 1px crossbars, 19px capitals."""
    Image=pillow();from PIL import ImageDraw
    widths={'C':18,'a':15,'r':13,'e':15,'g':15,'n':15,'d':15,'o':15}
    if char not in widths:raise ValueError('Unmapped loading raster character')
    out=Image.new('L',(widths[char],24));d=ImageDraw.Draw(out)
    def rect(x,y,z,w):d.rectangle((x,y,z-1,w-1),fill=255)
    if char=='C':
        rect(0,0,4,19);rect(4,0,18,1);rect(4,18,18,19)
    elif char=='a':
        rect(2,6,15,7);rect(11,6,15,19);rect(0,10,4,19);rect(4,10,11,11);rect(4,18,11,19)
    elif char=='r':
        rect(0,8,4,19);rect(4,8,13,9)
    elif char=='e':
        rect(0,8,4,19);rect(11,8,15,14);rect(4,8,11,9);rect(4,13,11,14);rect(4,18,15,19)
    elif char in ('g','o','d'):
        rect(0,8,4,19);rect(11,8,15,19);rect(4,8,11,9);rect(4,18,11,19)
        if char=='d':rect(11,0,15,8)
        if char=='g':rect(11,19,15,24);rect(3,23,11,24)
    elif char=='n':
        rect(0,8,4,19);rect(11,8,15,19);rect(4,8,11,9)
    return out


def render(raw):
    record=raw[START:START+SIZE];meta,_=inspect_texture(record)
    if (meta['width'],meta['height'],meta['bpp'],meta['pixel_offset'])!=(256,32,4,80):
        raise ValueError('Loading texture geometry differs')
    Image=pillow();glyphs=[letter(c) for c in TEXT]
    width=sum(g.width for g in glyphs)+3*(len(glyphs)-1)
    if width>232:raise ValueError('Loading label overflow; resizing prohibited')
    mask=Image.new('L',(width,24));x=0
    for glyph in glyphs:mask.paste(glyph,(x,0));x+=glyph.width+3
    old=unpack_indices(record,meta);ink=[(i%256,i//256) for i,v in enumerate(old) if v in INK]
    if not ink:raise ValueError('Loading source ink absent')
    left=min(x for x,y in ink);right=max(x for x,y in ink)+1
    ox=(left+right-width)//2;oy=5
    # Preserve the source mottled ink field. Newly occupied pixels take the
    # nearest original ink sample on their own row; no new colors or alpha.
    by_row={y:[x for x,yy in ink if yy==y] for y in range(32)}
    result=bytearray(8192)
    for y in range(mask.height):
        source_y=oy+y
        if not by_row[source_y]:raise ValueError('Loading ink row has no source sample')
        for x in range(mask.width):
            if not mask.getpixel((x,y)):continue
            px=ox+x
            if not 0<=px<256:raise ValueError('Loading raster outside texture')
            sample=min(by_row[source_y],key=lambda v:(abs(v-px),v))
            result[source_y*256+px]=old[source_y*256+sample]
    after=replace_indices(record,result)
    if after[:80]!=record[:80] or len(after)!=len(record):raise ValueError('Loading palette/header changed')
    if replace_indices(after,old)!=record:raise ValueError('Loading reverse round-trip differs')
    return after,{'translation':TEXT,'capital_body_pixels':19,'lowercase_body_pixels':11,
        'stem_width':4,'crossbar_height':1,'letter_gap':3,'baseline':23,'descender_bottom':28,
        'rendered_width':width,'origin':[ox,oy],'mask_sha256':sha(mask.tobytes()),
        'target_indices_sha256':sha(result),'target_texture_sha256':sha(after),
        'horizontal_scale':1,'palette_alpha_header_ganm_unchanged':True}


def compile_graphics(elf,config):
    raw=original(RESOURCE)
    expected={'policy':POLICY,'source_sha256':sha(raw),'bound_windows':bindings(elf),
        'translation':TEXT,'target_texture_sha256':TARGET_TEXTURE_SHA}
    if config!=expected:raise ValueError('Loading policy/source/recipe differs')
    evidence=proof(elf,raw);after,layout=render(raw)
    if sha(after)!=TARGET_TEXTURE_SHA:raise ValueError('Loading raster differs from bound output')
    return [{'id':'loading.carregando.texture-pixels','resource':RESOURCE,'offset':START+80,
        'before':raw[START+80:START+SIZE],'after':after[80:]}],{
        'policy':POLICY,'accepted':1,'evidence':evidence,'layout':layout,
        'source_sha256':sha(raw),'bound_windows':bindings(elf),'reverse_roundtrip':True,
        'runtime_visual_status':'pending_user_verification',
        'protected_other_resources_untouched':['wanted posters','casino/minigame title artwork']}


def preview(output):
    output=local(output,True)
    if output.suffix.lower()!='.png':raise ValueError('Loading preview must be a PNG')
    raw=original(RESOURCE);after,layout=render(raw);Image=pillow()
    from PIL import ImageDraw
    canvas=Image.new('RGB',(820,280),(35,38,40));draw=ImageDraw.Draw(canvas)
    for i,(label,record) in enumerate((('ORIGINAL',raw[START:START+SIZE]),('CARREGANDO - PROPOSTA',after))):
        meta,_=inspect_texture(record);im=Image.frombytes('P',(256,32),unpack_indices(record,meta))
        im.putpalette(bytes(c for j in range(16) for c in record[16+4*j:19+4*j])+bytes(720))
        draw.text((26,15+i*135),label,fill='white')
        canvas.paste(im.convert('RGB').resize((768,96),Image.Resampling.NEAREST),(26,36+i*135))
    output.parent.mkdir(parents=True,exist_ok=True);canvas.save(output)
    return layout


if __name__=='__main__':
    p=argparse.ArgumentParser(description='Comparar a arte de Carregando com a textura original')
    p.add_argument('--preview',type=Path,required=True);a=p.parse_args();print(json.dumps(preview(a.preview),indent=2))
