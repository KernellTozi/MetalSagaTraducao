"""Bounded instruction probes for two original/patched layout functions.

Models these functions and declared ABI boundaries; not a PS2 emulator.
The native metric tables are read directly from the immutable reference ELF.
"""
import struct
from functools import lru_cache
from glyph_layout import START,END,DELTA
MASK=(1<<64)-1


@lru_cache(maxsize=2)
def adjacent_table(data):
    from glyph_layout import elf_patch
    return elf_patch(data)


def execute(data,code,raw,side=22,mode=1,*,single=False):
    if single:
        from glyph_single import START as start,END as end_offset
    else:start,end_offset=START,END
    base=start+DELTA;end=end_offset+DELTA
    regs=[(0x12340000+i)<<64|0x33440000+i for i in range(32)]
    regs[0]=0;regs[29]=0x700000;regs[31]=0xdeadf000
    regs[4]=0x600000;regs[5]=0x600010;regs[6]=0x600020;regs[7]=side
    regs[8]=0x600030;regs[9]=0x600040
    if single:
        regs[4]=0x610000;regs[5]=int.from_bytes(raw,'big');regs[6]=100;regs[7]=200
        regs[8]=side;regs[9]=4;regs[10]=128
    initial=regs.copy();mem={};calls=[];draws=[];cache_codes=[]
    from glyph_layout import BASES
    adjacent=adjacent_table(data) if single else None
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
            elif adjacent and adjacent['offset']+DELTA<=p<adjacent['offset']+DELTA+len(adjacent['after']):out.append(adjacent['after'][p-adjacent['offset']-DELTA])
            elif DELTA<=p<DELTA+len(data):out.append(data[p-DELTA])
            else:raise ValueError(f'Unexpected read {p:x}')
        return int.from_bytes(bytes(out),'little',signed=signed)
    put(0x600000,0x500000,4)
    if single:
        put(0x610010,0x620000,4);put(0x620008,0x630000,4)
        put(0x630018,0,2);put(0x63001c,0x640000,4)
    for ptr in (0x600010,0x600020,0x600030,0x600040):put(ptr,0xaaaaaaaa,4)
    def signed(v,bits=32):
        v&=(1<<bits)-1;return v if v<1<<(bits-1) else v-(1<<bits)
    def bits(d):return struct.unpack('<Q',struct.pack('<d',d))[0]
    def double(v):return struct.unpack('<d',struct.pack('<Q',v&MASK))[0]
    pc=base;pending=None
    for steps in range(600):
        if pc==initial[31]:
            if single:
                return {'next_x':regs[2]&0xffffffff,'draws':draws,'cache_codes':cache_codes,
                        'callee_saved':all(regs[r]==initial[r] for r in (*range(16,24),28,29,30,31))}
            return {'code':regs[2]&0xffffffff,'consumed':get(0x600000,4)-0x500000,
                    'metrics':[get(p,4,signed=True) for p in (0x600010,0x600020,0x600030,0x600040)],
                    'callee_saved':all(regs[r]==initial[r] for r in (*range(16,24),28,29,30,31)),
                    'float_calls':calls}
        if pc in (0x296080,0x281fe8,0x281a70,0x2820a0,0x297420,0x2aca38,0x640000,0x296e10,0x13d858):
            if pc==0x296080:
                b=regs[4]&255
                result=0 if b<0x20 else 1 if b<=0x7f else 2 if 0xa0<=b<=0xdf else -2 if 0xf0<=b<=0xf9 else -1
            elif pc==0x281fe8:result=bits(float(signed(regs[4])));calls.append(('int',signed(regs[4])))
            elif pc==0x281a70:
                result=bits(double(regs[4])*double(regs[5]));calls.append(('mul',regs[4]&MASK,regs[5]&MASK))
            elif pc==0x2820a0:result=int(double(regs[4]));calls.append(('trunc',regs[4]&MASK))
            elif pc==0x297420:result=0x620000
            elif pc==0x296e10:
                c=regs[5]&65535;cache_codes.append(c)
                cell=26 if side==26 else 22
                half=c in BASES or c<256 and (0x20<=c<=0x7f or 0xa0<=c<=0xdf)
                width=cell//2+2 if half else cell
                for r,v in zip((6,7,8,9),(width,cell,64,32)):put(regs[r],v,4)
                result=0
            elif pc==0x13d858:
                draws.append({'x':regs[4],'y':regs[5],'width':regs[6],'height':regs[7],
                    'color':regs[9],'texture_rect':[get(regs[8]+i*4,4,signed=True) for i in range(4)]})
                result=0
            else:result=0
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
            elif fn==9:regs[rd]=pc+8;pending=regs[rs]
            elif fn==10:
                if regs[rt]==0:regs[rd]=regs[rs]
            elif fn==33:regs[rd]=signed(regs[rs]+regs[rt])
            elif fn==35:regs[rd]=signed(regs[rs]-regs[rt])
            elif fn==37:regs[rd]=regs[rs]|regs[rt]
            elif fn==45:regs[rd]=regs[rs]+regs[rt]
            elif fn==42:regs[rd]=int(signed(regs[rs])<signed(regs[rt]))
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
        elif op==12:regs[rt]=regs[rs]&u
        elif op==13:regs[rt]=regs[rs]|u
        elif op==14:regs[rt]=regs[rs]^u
        elif op==15:regs[rt]=signed(u<<16)
        elif op in (30,32,33,35,36,37,55):
            size={30:16,32:1,33:2,35:4,36:1,37:2,55:8}[op]
            regs[rt]=get((regs[rs]+n)&MASK,size,signed=op in (32,33,35))
        elif op in (31,43,63):
            put((regs[rs]+n)&MASK,regs[rt],{31:16,43:4,63:8}[op])
        else:raise ValueError(f'Unknown opcode {op:x} at {pc:x}')
        regs=[r&MASK if i not in (*range(16,24),28,30) else r for i,r in enumerate(regs)]
        regs[0]=0;pc=previous if previous is not None else nextpc
    raise ValueError('Instruction budget exhausted')
