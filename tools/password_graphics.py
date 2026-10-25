"""Three password-panel labels in their proven original indexed texture.

The texture, palette, sprite records, numeric keys and password logic keep their
original bounds. Text is composed locally from the existing game GFI font.
"""
import argparse,json,struct
from pathlib import Path
from interface_graphics import original,sha,mask
from interface_texture_pack import unpack_indices,replace_indices,pillow
from interface_textures import inspect_texture
from glyph_spacing import ORIGINAL_SHA
from reinsertion import ROOT,local

POLICY='password-panel-three-native-labels-v001'
RESOURCE='DATA/FDATA/PASSWORD.SDA'
START,SIZE,GANM=0x618b0,0x10410,0x71d80
TARGET_SHA='60d7d56a31f7ac6e53fe9513daf931cf8d33737f24dc17954ee17eabffaf80cd'
LABELS=((18,'DESTRAVAR',(154,170,252,192)),
        (1,'TRAVAR',(154,200,252,222)),(0,'SAIR',(154,230,252,252)))
WINDOWS=((0x131950,0x131a94),(0x1329d8,0x132a9c),(0x132b40,0x132c44),
         (0x1321b4,0x1321e8),(0x132300,0x13232c),
         (0x32e120,0x32e130),(0x32e200,0x32e23c),(0x32e290,0x32e2ec))


def bindings(elf):
    return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]


def run(elf,start,end,stop,regs,memory):
    """Narrow original integer upload/draw windows; store only to synthetic RAM."""
    mem=dict(memory)
    def read(at,size):
        out=[]
        for p in range(at,at+size):
            if p in mem:out.append(mem[p])
            elif 0xff000<=p<0xff000+len(elf):out.append(elf[p-0xff000])
            else:raise ValueError('Password forwarding probe read outside declared memory')
        return int.from_bytes(bytes(out),'little')
    pc=start;pending=None
    for _ in range(80):
        if pc==stop:return regs
        if not start<=pc<end:raise ValueError('Password probe escaped bound code')
        w=struct.unpack_from('<I',elf,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31
        u=w&65535;n=u if u<32768 else u-65536;old=pending;pending=None
        if op==0:
            fn=w&63
            if fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            elif fn==0:regs[rd]=regs[rt]<<((w>>6)&31)
            elif fn==8:pending=regs[rs]-0xff000
            else:raise ValueError('Unsupported password integer opcode')
        elif op==9:regs[rt]=regs[rs]+n
        elif op==11:regs[rt]=int(regs[rs]<(n&0xffffffff))
        elif op==13:regs[rt]=regs[rs]|u
        elif op==15:regs[rt]=u<<16
        elif op==35:regs[rt]=read((regs[rs]+n)&0xffffffff,4)
        elif op==43:
            at=(regs[rs]+n)&0xffffffff
            if not 0x620000<=at<=0x640100-4:raise ValueError('Password probe store outside synthetic context')
            for i in range(4):mem[at+i]=(regs[rt]>>(8*i))&255
        elif op==4:pending=pc+4+n*4 if regs[rs]==regs[rt] else pc+8
        elif op==3:regs[31]=pc+8;pending=((w&0x3ffffff)<<2)-0xff000
        else:raise ValueError('Unsupported password forwarding opcode')
        regs=[r&0xffffffff for r in regs];regs[0]=0;pc=old if old is not None else pc+4
    raise ValueError('Password probe step limit')


def memory32(pairs):
    return {at+i:(value>>(8*i))&255 for at,value in pairs for i in range(4)}


def probes(elf):
    regs=[0]*32;regs[18]=0x620000;regs[16]=0x620820
    r=run(elf,0x131a68,0x131a94,0x1acc58,regs,memory32(((0x620034,0x600000),)))
    if (r[4],r[5],r[7])!=(0x620820,0x600000+START,SIZE):raise ValueError('Password texture upload binding differs')
    mapping=[]
    for key in range(15):
        regs=[0]*32;regs[2]=0x630000;regs[18]=0x620000;regs[19]=0x6209c4
        regs[20]=0xff000+0x32e2b0+key*4;regs[22]=0x620820;regs[29]=0x640000
        r=run(elf,0x132c20,0x132c44,0x111540,regs,
            memory32(((0x640018,GANM),(0x620034,0x600000))))
        if r[5]!=0x620820 or r[6]!=0x600000+GANM:raise ValueError('Password sprite pairing differs')
        mapping.append(r[7])
    if mapping!=list(range(4,16))+[18,1,0]:raise ValueError('Password key/sprite order differs')
    # Original action switch: key 12 forwards mode 0, key 13 mode 1, key 14 exits.
    if struct.unpack_from('<3I',elf,0x32e200+12*4)!=(0x231300,0x231314,0x231328):
        raise ValueError('Password action switch differs')
    return {'texture_offset':START,'texture_bytes':SIZE,'ganm_offset':GANM,
        'logical_key_to_sprite':mapping,'texture_upload_cases':1,'label_draw_cases':15,
        'action_keys':{'unlock':12,'lock':13,'exit':14},
        'scope':'Original integer argument forwarding in synthetic RAM; no renderer, resource loader, password validation or PS2 execution'}


def render(raw):
    record=raw[START:START+SIZE];meta,_=inspect_texture(record)
    if (meta['width'],meta['height'],meta['bpp'])!=(256,256,8):raise ValueError('Password atlas geometry differs')
    pixels=bytearray(unpack_indices(record,meta));palette=[tuple(record[16+i*4:20+i*4]) for i in range(256)]
    if palette[0]!=(0,0,0,0) or any(p[3]!=127 for p in palette[1:]):raise ValueError('Password palette/alpha differs')
    tag,count,stride,size=struct.unpack_from('<4sIII',raw,GANM)
    if (tag,count,stride,size)!=(b'ganm',19,16,320):raise ValueError('Password GANM differs')
    rows=[]
    for index,text,rect in LABELS:
        sprite=struct.unpack_from('<8h',raw,GANM+16+index*16)
        if sprite!=(*rect,49,11,0,0):raise ValueError('Password label sprite bounds differ')
        x,y,z,w=rect;glyph,layout=mask(text,20,z-x-4)
        if layout['horizontal_scale']<.94:raise ValueError('Password word would need excessive compression')
        left=x+(z-x-glyph.width)//2;top=y+(w-y-glyph.height)//2
        for py in range(y,w):
            for px in range(x,z):pixels[py*256+px]=0
        # Keep the original raw palette and alpha. Dark antialias pixels use
        # original opaque shades; fully empty pixels use transparent index zero.
        ramp=[0]+[min(range(1,256),key=lambda i:sum((palette[i][c]-round(225*a/255))**2 for c in range(3))) for a in range(1,256)]
        for gy in range(glyph.height):
            for gx in range(glyph.width):pixels[(top+gy)*256+left+gx]=ramp[glyph.getpixel((gx,gy))]
        rows.append({'id':f'password.graphic.{index:02d}','translation':text,'sprite_index':index,
            'rect':list(rect),'layout':layout})
    out=replace_indices(record,bytes(pixels))
    if len(out)!=len(record) or out[:meta['pixel_offset']]!=record[:meta['pixel_offset']]:
        raise ValueError('Password palette/header/size changed')
    before=unpack_indices(record,meta);after=unpack_indices(out,meta)
    for i,(a,b) in enumerate(zip(before,after)):
        if a!=b and not any(x<=i%256<z and y<=i//256<w for _,_,(x,y,z,w) in LABELS):
            raise ValueError('Password pixel changed outside approved labels')
    return out,rows


def compile_graphics(elf,config):
    raw=original(RESOURCE)
    if (sha(elf)!=ORIGINAL_SHA or config!={'policy':POLICY,'source_sha256':sha(raw),
        'instruction_windows':bindings(elf)}):raise ValueError('Password graphics source/evidence differs')
    if struct.unpack_from('<14I',raw,12)[6]!=START or struct.unpack_from('<14I',raw,12)[13]!=GANM:
        raise ValueError('Password SDA entry pairing differs')
    evidence=probes(elf);after,rows=render(raw)
    if sha(after)!=TARGET_SHA:raise ValueError('Password v001 raster differs from pinned output; check rendering dependencies')
    return [{'id':'password.three-labels','resource':RESOURCE,'offset':START,
        'before':raw[START:START+SIZE],'after':after}],{'policy':POLICY,'accepted':3,
        'results':rows,'evidence':evidence,'instruction_windows':bindings(elf),
        'palette_alpha_ganm_numbers_controls_unchanged':True,'target_texture_sha256':sha(after),
        'runtime_visual_status':'pending_user_verification'}


def preview(output):
    from interface_text import SOURCE
    raw=original(RESOURCE);elf=SOURCE.read_bytes()
    config={'policy':POLICY,'source_sha256':sha(raw),'instruction_windows':bindings(elf)}
    patches,report=compile_graphics(elf,config);Image=pillow();meta,_=inspect_texture(patches[0]['before'])
    output=local(output,True);output.parent.mkdir(parents=True,exist_ok=True)
    canvas=Image.new('RGB',(512,256),(24,24,24))
    for side,data in enumerate((patches[0]['before'],patches[0]['after'])):
        image=Image.frombytes('P',(256,256),unpack_indices(data,meta))
        image.putpalette(bytes(c for i in range(256) for c in data[16+4*i:19+4*i]))
        canvas.paste(image.convert('RGB'),(side*256,0))
    canvas.resize((1024,512),Image.Resampling.NEAREST).save(output)
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description='Comparar três rótulos de senha, sem ISO ou APIs')
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(json.dumps(preview(a.output),ensure_ascii=True,indent=2))
