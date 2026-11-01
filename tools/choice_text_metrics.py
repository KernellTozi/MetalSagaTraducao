"""Choice-row width from the native glyph measure, within its old wrapper.

The original row update used 22 * (strlen/2), while drawing uses the native
glyph advances. Tail-call the existing measurement routine instead. No new
segment, heap reserve, code cave, font bitmap or hardcoded X correction.
"""
from functools import lru_cache
import struct
from dialogue import sha
from glyph_spacing import ORIGINAL_SHA,DELTA
from glyph_layout import elf_patch as layout_patch
from layout_probe import execute as glyph_execute
from gfi import encode

START=0x99f78
END=0x99fa8
MEASURE=0x3dd60
WINDOWS=((0xc4af0,0xc4b64),(0xc75e4,0xc7670),(0x99380,0x994a0),
         (0x99ea8,0x99fa8),(0x4f810,0x4f8d0),(0x3dd60,0x3de68))


def replacement():
    words=[0x8c820064,       # lw v0,0x64(a0): original row style
           0xa4820056,       # sh v0,0x56(a0)
           0x3c013f66,0x34216666,0xac810020,  # retain scale bits 0.9f
           0x84870054,       # lh a3,0x54(a0): actual draw font size
           0x2485002c,0x24860030,            # width/height output fields
           0x0000402d,0x0000482d,            # zero char/line gaps
           (2<<26)|((MEASURE+DELTA)>>2),
           0x24840044]       # delay: native string object at row+0x44
    result=struct.pack('<12I',*words)
    if len(result)!=END-START:raise ValueError('Choice wrapper size differs')
    return result


def bindings(elf):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Choice metrics ELF differs')
    return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]


def elf_patch(elf):
    bindings(elf)
    return {'id':'choice.row.native-width','resource':'SLUS_212.93','offset':START,
            'before':elf[START:END],'after':replacement()}


@lru_cache(maxsize=4096)
def metric(elf,char,side,mode):
    return glyph_execute(elf,layout_patch(elf)['after'],char,side,mode)


def execute(elf,text,*,patched=True,mode=1,side=22,style=0xffff):
    """Bounded original measure/update instructions, native glyph ABI composed.

    Glyph metric function is executed by layout_probe; allocator/cache/drawing
    inside that probe remain its declared stubs. No PS2 or GPU execution.
    """
    bindings(elf);raw=text if isinstance(text,bytes) else encode(text)
    row=bytearray(b'\xa5'*0x100);stack=bytearray(b'\xcc'*0x400)
    struct.pack_into('<I',row,0x48,0x640000)
    struct.pack_into('<HH',row,0x54,side,0)
    struct.pack_into('<III',row,0x58,side,len(raw)//2,0xffffffff)
    struct.pack_into('<II',row,0x38,0,0)
    struct.pack_into('<I',row,0x64,style)
    regs=[((0x12340000+i)<<64)|0x3000+i for i in range(32)]
    regs[0]=0;regs[4]=0x620000;regs[29]=0x700300;regs[31]=0x7ff000
    original=regs.copy();fregs={};pc=START;pending=None;steps=0;glyphs=[]
    regions=[(0x620000,row,True),(0x640000,raw+b'\0',False),(0x700000,stack,True)]
    def read(at,size):
        for base,data,_ in regions:
            if base<=at and at+size<=base+len(data):return int.from_bytes(data[at-base:at-base+size],'little')
        raise ValueError(f'Choice probe read outside memory {at:x}/{size}')
    writes=[]
    def write(at,size,value):
        for base,data,allowed in regions:
            if allowed and base<=at and at+size<=base+len(data):
                data[at-base:at-base+size]=(value&((1<<(8*size))-1)).to_bytes(size,'little')
                if base==0x620000:writes.append([at-base,size])
                return
        raise ValueError('Choice probe escaped writable memory')
    def signed(value,bits=32):
        value&=(1<<bits)-1
        return value if value<(1<<(bits-1)) else value-(1<<bits)
    while pc!=0x7ff000:
        if steps>=20000:raise ValueError('Choice probe instruction bound exceeded')
        steps+=1
        if pc==0x3e520:
            ptr=read(regs[4],4);offset=ptr-0x640000
            char=raw[offset:offset+(2 if raw[offset]>127 else 1)]
            m=metric(elf,char,regs[7],mode)
            write(regs[4],4,ptr+m['consumed'])
            for out,value in zip((5,6,8,9),m['metrics']):write(regs[out],4,value)
            glyphs.append(m);regs[2]=m['code'];pc=regs[31];continue
        if not any(a<=pc<z for a,z in [(START,END),(0x4f898,0x4f8d0),(MEASURE,0x3de68)]):
            raise ValueError(f'Choice probe escaped instruction windows {pc:x}')
        code=replacement() if patched and START<=pc<END else elf
        w=struct.unpack_from('<I',code,pc-START if code is not elf else pc)[0]
        op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;fn=w&63
        u=w&65535;n=signed(u,16);old=pending;pending=None;nextpc=pc+4
        if op==0:
            if fn==0:regs[rd]=signed(regs[rt]<<((w>>6)&31))
            elif fn==3:regs[rd]=signed(regs[rt])>>((w>>6)&31)
            elif fn in (33,45):regs[rd]=(regs[rs]+regs[rt])&0xffffffffffffffff
            elif fn==8:pending=regs[rs]
            elif fn==11:
                if regs[rt]!=0:regs[rd]=regs[rs]
            elif fn==24:
                # R5900 MULT rd,rs,rt also writes the low result to rd.
                if rd:regs[rd]=signed(signed(regs[rs])*signed(regs[rt]))
            elif fn==42:regs[rd]=int(signed(regs[rs],64)<signed(regs[rt],64))
            else:raise ValueError(f'Unsupported choice arithmetic {w:08x}')
        elif op in (2,3):
            if op==3:regs[31]=pc+8
            pending=((w&0x3ffffff)<<2)-DELTA
        elif op==9:regs[rt]=(regs[rs]+n)&0xffffffffffffffff
        elif op==12:regs[rt]=regs[rs]&u
        elif op==13:regs[rt]=regs[rs]|u
        elif op==15:regs[rt]=u<<16
        elif op in (30,33,35,36,37,55):
            value=read((regs[rs]+n)&0xffffffff,{30:16,33:2,35:4,36:1,37:2,55:8}[op])
            regs[rt]=signed(value,16) if op==33 else value
        elif op in (31,41,43,63):write((regs[rs]+n)&0xffffffff,{31:16,41:2,43:4,63:8}[op],regs[rt])
        elif op==17:
            if rs!=4:raise ValueError('Unsupported choice FPU operation')
            fregs[rd]=regs[rt]&0xffffffff
        elif op==57:write((regs[rs]+n)&0xffffffff,4,fregs[rt])
        elif op in (4,5):pending=pc+4+n*4 if ((regs[rs]==regs[rt]) if op==4 else regs[rs]!=regs[rt]) else pc+8
        else:raise ValueError(f'Unsupported choice instruction {w:08x}')
        regs[0]=0;pc=old if old is not None else nextpc
    if regs[29]!=original[29] or any(regs[i]!=original[i] for i in range(16,24)) or regs[30]!=original[30]:
        raise ValueError('Choice measurement corrupted ABI state')
    width,height=struct.unpack_from('<II',row,0x2c)
    return {'encoded_bytes':len(raw),'width':width,'height':height,'steps':steps,
            'glyphs':len(glyphs),'glyph_advances':[m['metrics'][3] for m in glyphs],
            'style':struct.unpack_from('<H',row,0x56)[0],
            'scale_bits':struct.unpack_from('<I',row,0x20)[0],
            'callee_saved_and_stack_preserved':True,'row_write_intervals':writes,
            'probe_limits':'Bounded native update/measure instructions; glyph metric ABI composed with existing layout probe; no allocator, cache lifecycle, GPU or PCSX2.'}
