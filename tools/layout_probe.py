"""Bounded instruction probe for the original and patched layout function.

Models only this function and four external ABI boundaries; not a PS2 emulator.
The native metric tables are read directly from the immutable reference ELF.
"""
import struct
from glyph_layout import START,END,DELTA
MASK=(1<<64)-1


def execute(data,code,raw,side=22,mode=1):
    base=START+DELTA;end=END+DELTA
    regs=[(0x12340000+i)<<64|0x33440000+i for i in range(32)]
    regs[0]=0;regs[29]=0x700000;regs[31]=0xdeadf000
    regs[4]=0x600000;regs[5]=0x600010;regs[6]=0x600020;regs[7]=side
    regs[8]=0x600030;regs[9]=0x600040
    initial=regs.copy();mem={};calls=[]
    def put(at,val,size):
        val&=(1<<(size*8))-1
        for i in range(size):mem[at+i]=val>>(i*8)&255
    def get(at,size,signed=False):
        out=[]
        for i in range(size):
            p=at+i
            if p in mem:out.append(mem[p])
            elif 0x500000<=p<0x500000+len(raw):out.append(raw[p-0x500000])
            elif 0x4491d0<=p<0x4491d4:out.append((mode>>((p-0x4491d0)*8))&255)
            elif base<=p<end:out.append(code[p-base])
            elif DELTA<=p<DELTA+len(data):out.append(data[p-DELTA])
            else:raise ValueError(f'Unexpected read {p:x}')
        return int.from_bytes(bytes(out),'little',signed=signed)
    put(0x600000,0x500000,4)
    for ptr in (0x600010,0x600020,0x600030,0x600040):put(ptr,0xaaaaaaaa,4)
    def signed(v,bits=32):
        v&=(1<<bits)-1;return v if v<1<<(bits-1) else v-(1<<bits)
    def bits(d):return struct.unpack('<Q',struct.pack('<d',d))[0]
    def double(v):return struct.unpack('<d',struct.pack('<Q',v&MASK))[0]
    pc=base;pending=None
    for steps in range(600):
        if pc==initial[31]:
            return {'code':regs[2]&0xffffffff,'consumed':get(0x600000,4)-0x500000,
                    'metrics':[get(p,4,signed=True) for p in (0x600010,0x600020,0x600030,0x600040)],
                    'callee_saved':all(regs[r]==initial[r] for r in (*range(16,24),28,29,30,31)),
                    'float_calls':calls}
        if pc in (0x296080,0x281fe8,0x281a70,0x2820a0):
            if pc==0x296080:
                b=regs[4]&255
                result=0 if b<0x20 else 1 if b<=0x7f else 2 if 0xa0<=b<=0xdf else -2 if 0xf0<=b<=0xf9 else -1
            elif pc==0x281fe8:result=bits(float(signed(regs[4])));calls.append(('int',signed(regs[4])))
            elif pc==0x281a70:
                result=bits(double(regs[4])*double(regs[5]));calls.append(('mul',regs[4]&MASK,regs[5]&MASK))
            else:result=int(double(regs[4]));calls.append(('trunc',regs[4]&MASK))
            for r in range(2,16):regs[r]=0xfeed0000+r
            regs[24]=0xfeed0018;regs[25]=0xfeed0019
            regs[2]=result&MASK;pc=regs[31];continue
        if not base<=pc<end:raise ValueError(f'PC outside layout function: {pc:x}')
        w=struct.unpack_from('<I',code,pc-base)[0]
        op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;sa=w>>6&31;fn=w&63
        u=w&65535;n=signed(u,16)
        previous=pending;pending=None;nextpc=pc+4
        if op==0:
            if fn==0:regs[rd]=signed(regs[rt]<<sa)
            elif fn==3:regs[rd]=signed(regs[rt])>>sa
            elif fn==8:pending=regs[rs]
            elif fn==33:regs[rd]=signed(regs[rs]+regs[rt])
            elif fn==35:regs[rd]=signed(regs[rs]-regs[rt])
            elif fn==37:regs[rd]=regs[rs]|regs[rt]
            elif fn==45:regs[rd]=regs[rs]+regs[rt]
            elif fn==56:regs[rd]=regs[rt]<<sa
            else:raise ValueError(f'Unknown R instruction {fn:x} at {pc:x}')
        elif op in (1,4,5,20,21):
            if op==1:
                if rt not in (1,3):raise ValueError('Unsupported REGIMM')
                take=signed(regs[rs],64)>=0
            else:take=(regs[rs]==regs[rt]) if op in (4,20) else regs[rs]!=regs[rt]
            if (op in (20,21) or op==1 and rt==3) and not take:nextpc=pc+8
            else:pending=pc+4+n*4 if take else pc+8
        elif op in (2,3):
            if op==3:regs[31]=pc+8
            pending=(w&0x3ffffff)<<2
        elif op==9:regs[rt]=signed(regs[rs]+n)
        elif op==11:regs[rt]=int((regs[rs]&MASK)<(n&MASK))
        elif op==13:regs[rt]=regs[rs]|u
        elif op==15:regs[rt]=signed(u<<16)
        elif op in (30,32,35,36,55):
            size={30:16,32:1,35:4,36:1,55:8}[op]
            regs[rt]=get((regs[rs]+n)&MASK,size,signed=op in (32,35))
        elif op in (31,43,63):
            put((regs[rs]+n)&MASK,regs[rt],{31:16,43:4,63:8}[op])
        else:raise ValueError(f'Unknown opcode {op:x} at {pc:x}')
        regs=[r&MASK if i not in (*range(16,24),28,30) else r for i,r in enumerate(regs)]
        regs[0]=0;pc=previous if previous is not None else nextpc
    raise ValueError('Instruction budget exhausted')
