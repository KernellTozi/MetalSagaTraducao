"""Only the two live END/FIM category sprites; native banks and frames preserved."""
import struct
from interface_graphics import original,sha,mask
from interface_texture_pack import unpack_indices,replace_indices,pillow
from interface_textures import inspect_texture
from password_graphics import run,memory32
from glyph_spacing import ORIGINAL_SHA
from reinsertion import local

POLICY='name-entry-two-finish-sprites-v001'
RESOURCE='DATA/FDATA/FNAME_DT.SDA'
START,SIZE,GANM=0x4cc0,0x40440,0x86980
WINDOWS=((0x10c248,0x10c274),(0x10c420,0x10c478),(0x10c5b8,0x10c5fc),
         (0x10c8f4,0x10c918),(0x19af90,0x19afa4),(0x10b974,0x10b9b0),
         (0x32a4d0,0x32a4f0))
TARGET_SHA='8fb48e5c4e6c965826885bd4555b45f42de8860f1433f326938195d0a38c3ab9'


def bindings(elf):return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]


def probes(elf,raw):
    regs=[0]*32;regs[2]=0x600000;regs[17]=0x620000;regs[21]=0x620dd0;regs[16]=0x430000
    r=run(elf,0x10c254,0x10c274,0x1acc58,regs,{})
    if (r[4],r[5],r[7])!=(0x620dd0,0x600000+START,0x40410):raise ValueError('Name texture upload differs')
    # The manager stores source+u32(source+8), i.e. GANM data after its 16-byte header.
    regs=[0]*32;regs[16]=0x620d90;regs[5]=0x600000+GANM
    mem=memory32(((0x600000+GANM+8,struct.unpack_from('<I',raw,GANM+8)[0]),))
    r=run(elf,0x19af90,0x19afa4,0x19afa4,regs,mem)
    if r[2]!=0x600000+GANM+16:raise ValueError('Name GANM manager base differs')
    cases=[]
    for category in range(3):
        regs=[0]*32;regs[20]=category;regs[16]=0x622710+category*0x1d0;regs[21]=0x620dd0;regs[29]=0x640000
        r=run(elf,0x10c5b8,0x10c5cc,0x111540,regs,memory32(((0x640000,0x600000+GANM),)))
        if r[7]!=category+32 or r[6]!=0x600000+GANM or r[5]!=0x620dd0:raise ValueError('Name default category sprite differs')
        regs=[0]*32;regs[18]=category;regs[16]=0x1d0;regs[17]=0x620d90;regs[19]=0x620000
        r=run(elf,0x10c8f4,0x10c918,0x111680,regs,memory32(((0x620d9c,0x600000+GANM+16),)))
        expected=0x600000+GANM+16+(category+12)*16
        if r[5]!=expected or r[4]!=0x620000+0x2710+category*0x1d0:raise ValueError('Name selected category sprite differs')
        cases.append({'category':category,'default_sprite':category+32,'selected_sprite':category+12})
    return {'texture_offset':START,'upload_bytes':0x40410,'record_bytes':SIZE,'ganm_offset':GANM,
        'category_cases':cases,'scope':'Original bounded upload, GANM pointer arithmetic and category argument forwarding; no GPU or PS2 execution'}


def render(raw):
    rec=raw[START:START+SIZE];meta,_=inspect_texture(rec)
    if (meta['width'],meta['height'],meta['bpp'],meta['trailing_bytes'])!=(512,512,8,48):raise ValueError('Name atlas layout differs')
    pal=[tuple(rec[16+4*i:20+4*i]) for i in range(256)];indices=bytearray(unpack_indices(rec,meta))
    if pal[17]!=(26,26,25,127) or pal[218]!=(51,237,61,127) or pal[237]!=(203,203,203,127):
        raise ValueError('Name label palette differs')
    glyph,layout=mask('FIM',24,47)
    if layout['horizontal_scale']!=1:raise ValueError('Name FIM must retain native width')
    results=[]
    for sprite,y,fg in ((14,216,218),(34,440,237)):
        if struct.unpack_from('<4h',raw,GANM+16+sprite*16)!=(384,y-4,505,y+28):raise ValueError('Name END sprite differs')
        rect=(426,y,475,y+24);left=426+(49-glyph.width)//2
        ramp=[min((i for i,p in enumerate(pal) if p[3]==127),
            key=lambda i:sum((pal[i][c]-round(pal[17][c]+(pal[fg][c]-pal[17][c])*a/255))**2 for c in range(3))) for a in range(256)]
        for yy in range(y,y+24):indices[yy*512+426:yy*512+475]=bytes([17])*49
        for yy in range(24):
            for xx in range(glyph.width):indices[(y+yy)*512+left+xx]=ramp[glyph.getpixel((xx,yy))]
        results.append({'id':f'name.finish.{sprite:02d}','translation':'FIM','sprite':sprite,'inner_rect':list(rect),'layout':layout})
    after=replace_indices(rec,indices)
    if after[:meta['pixel_offset']]!=rec[:meta['pixel_offset']] or after[-48:]!=rec[-48:]:raise ValueError('Name palette/header/tail changed')
    old=unpack_indices(rec,meta);new=unpack_indices(after,meta)
    if any(a!=b and not any(x<=i%512<z and y<=i//512<w for x,y,z,w in (r['inner_rect'] for r in results)) for i,(a,b) in enumerate(zip(old,new))):
        raise ValueError('Name artwork changed outside END interiors')
    return after,results


def compile_graphics(elf,config):
    raw=original(RESOURCE)
    if sha(elf)!=ORIGINAL_SHA or config!={'policy':POLICY,'source_sha256':sha(raw),'instruction_windows':bindings(elf)}:
        raise ValueError('Name finish source/evidence differs')
    evidence=probes(elf,raw);after,rows=render(raw)
    if TARGET_SHA is None or sha(after)!=TARGET_SHA:raise ValueError('Name finish raster differs from pinned output')
    return [{'id':'name.finish.texture','resource':RESOURCE,'offset':START,'before':raw[START:START+SIZE],'after':after}],{
        'policy':POLICY,'accepted':2,'results':rows,'evidence':evidence,'target_texture_sha256':sha(after),
        'palette_alpha_frames_other_labels_and_tail_unchanged':True,'runtime_visual_status':'pending_user_verification'}


def preview(path):
    path=local(path,True);path.parent.mkdir(parents=True,exist_ok=True)
    raw=original(RESOURCE);after,rows=render(raw);Image=pillow();rec=raw[START:START+SIZE];meta,_=inspect_texture(rec)
    canvas=Image.new('RGB',(512,160),(30,30,30))
    for side,data in enumerate((rec,after)):
        im=Image.frombytes('P',(512,512),unpack_indices(data,meta));im.putpalette(bytes(c for i in range(256) for c in data[16+4*i:19+4*i]))
        for variant,y in enumerate((212,436)):canvas.paste(im.crop((384,y,505,y+32)).resize((242,64),Image.Resampling.NEAREST).convert('RGB'),(side*256,variant*80))
    canvas.save(path);return sha(after)
