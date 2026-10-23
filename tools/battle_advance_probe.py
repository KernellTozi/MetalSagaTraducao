"""Bounded integer/FPU probe of one character path, with declared draw/map ABIs.

Executes actual original/rebuilt instructions between the entry to lead-byte
classification and pointer increment. Does not emulate PS2 rendering or prologue.
"""
import struct
from battle_font_advance import START,END,DELTA,replacement


def run(elf,raw,patched=False,size=22,scale=1.0,advance=0.0):
    before=elf[START:END]
    code,labels=replacement(before) if patched else (before,{a:a+DELTA for a in range(START,END,4)})
    pc=labels[0x8c114];end=labels[0x8c2ac];base=START+DELTA
    regs=[0]*32;fp=[0]*32;pending=None;mem={};draws=[];maps=[]
    def put(a,v,n=4):
        for i in range(n):mem[a+i]=(v>>(i*8))&255
    def get(a,n=4):
        try:return sum(mem[a+i]<<(i*8) for i in range(n))
        except KeyError:raise ValueError(f'Unexpected battle probe read {a:x}')
    def bits(v):return struct.unpack('<I',struct.pack('<f',v))[0]
    def number(v):return struct.unpack('<f',struct.pack('<I',v&0xffffffff))[0]
    def signed(v):return v if v<0x80000000 else v-0x100000000
    regs[16]=0x600000;regs[18]=0x610000;regs[20]=0x620000;regs[29]=0x630000
    regs[7]=128;regs[19]=128
    for i,b in enumerate(raw+b'\0\0'):put(0x610000+i,b,1)
    put(0x600088,size);put(0x6000a0,bits(scale));put(0x6000a4,bits(scale))
    put(0x600080,bits(advance));put(0x600084,0);put(0x630000,bits(advance));put(0x630004,0)
    fp[20]=bits(0.5) if patched else bits(-999.0)
    for steps in range(300):
        if pc==end:
            return {'consumed':regs[18]-0x610000+1,'advance':number(get(0x600080)),
                    'draws':draws,'maps':maps}
        if pc in (0x18c0a0,0x18b908):
            if pc==0x18c0a0:maps.append(regs[5]&65535);value=regs[5]&65535
            else:draws.append({'code':regs[5]&65535,'x':number(get(regs[6])),'color':regs[7]});value=0
            for r in list(range(2,16))+[24,25]:regs[r]=0xfeed0000+r
            for r in range(20):fp[r]=bits(-777.0)
            regs[2]=value;pc=regs[31];continue
        if not base<=pc<base+len(code):raise ValueError(f'Unexpected battle PC {pc:x}')
        w=struct.unpack_from('<I',code,pc-base)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31
        fn=w&63;u=w&65535;n=u if u<32768 else u-65536
        previous=pending;pending=None;nextpc=pc+4
        if op==0:
            if fn==0:regs[rd]=regs[rt]<<((w>>6)&31)
            elif fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            elif fn in (37,):regs[rd]=regs[rs]|regs[rt]
            elif fn==43:regs[rd]=int(regs[rs]<regs[rt])
            else:raise ValueError(f'Unknown battle R opcode {fn}')
        elif op==9:regs[rt]=regs[rs]+n
        elif op==11:regs[rt]=int(regs[rs]<(n&0xffffffff))
        elif op==12:regs[rt]=regs[rs]&u
        elif op==14:regs[rt]=regs[rs]^u
        elif op==15:regs[rt]=u<<16
        elif op==36:regs[rt]=get((regs[rs]+n)&0xffffffff,1)
        elif op==43:put((regs[rs]+n)&0xffffffff,regs[rt])
        elif op==49:fp[rt]=get((regs[rs]+n)&0xffffffff)
        elif op==57:put((regs[rs]+n)&0xffffffff,fp[rt])
        elif op in (4,5):
            take=(regs[rs]==regs[rt]) if op==4 else (regs[rs]!=regs[rt])
            pending=pc+4+n*4 if take else pc+8
        elif op==3:regs[31]=pc+8;pending=(w&0x3ffffff)<<2
        elif op==17:
            fs=w>>11&31;ft=w>>16&31;fd=w>>6&31;fmt=w>>21&31
            if fmt==4:fp[fs]=regs[rt]
            elif fmt==20 and fn==32:fp[fd]=bits(float(signed(fp[fs])))
            elif fmt==16 and fn==0:fp[fd]=bits(number(fp[fs])+number(fp[ft]))
            elif fmt==16 and fn==2:fp[fd]=bits(number(fp[fs])*number(fp[ft]))
            else:raise ValueError(f'Unknown battle COP1 {w:08x}')
        else:raise ValueError(f'Unknown battle opcode {op} at {pc:x}')
        regs=[r&0xffffffff for r in regs];regs[0]=0
        pc=previous if previous is not None else nextpc
    raise ValueError('Battle probe instruction limit exceeded')
