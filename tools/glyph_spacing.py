"""Experimental fixed-size R5900 cache-width patch; no code cave or relocation.

Only the 18 project pairs gain the existing half-width cache flag. The original
bitmap lookup still receives the two-byte code. Runtime validation is separate.
"""
import hashlib
import struct
from gfi import CHAR_TO_BYTES

START=0x19797c
END=0x1979fc
DELTA=0xff000
BASE=START+DELTA
ORIGINAL_SHA='25756885a1a01a4ddd82045fd78e1928c09873f810cf182b99b248914fb1ea71'
WINDOW_SHA='f767e2885d654c47501d9477398b5bdb011afdb7912ea89403547e0f35d99760'
LOOKUP=0x296218
RETURN_ZERO=0x29694c
CONTINUE=END+DELTA
PAIRS={int.from_bytes(b,'big') for b in CHAR_TO_BYTES.values()}


def replacement():
    # Registers follow the surrounding original function: s0 font, s1 code,
    # s2 cache, s3 bitmap. s4 is saved by the original prologue and assigned
    # again at file 0x197ab4 before its next original use.
    # Every branch delay slot is explicit; there are no branch-likely opcodes.
    words=[];labels={};fixups=[]
    def emit(word):words.append(word)
    def imm(op,rs,rt,value):emit(op<<26|rs<<21|rt<<16|(value&65535))
    def reg(rs,rt,rd,fn,shift=0):emit(rs<<21|rt<<16|rd<<11|shift<<6|fn)
    def branch(rs,rt,target):
        fixups.append((len(words),target));imm(4,rs,rt,0)
    branch(2,0,RETURN_ZERO);imm(9,2,3,3)       # class 0: original early return
    imm(11,3,3,6);branch(3,0,CONTINUE)        # unsupported class: no lookup
    reg(0,2,20,42)                           # s4 = class > 0
    imm(13,0,3,0x8240);imm(12,17,5,65535)
    reg(5,3,5,35);imm(11,5,3,15)             # 8240..824e
    fixups.append((len(words),'half'));imm(5,3,0,0)
    imm(9,5,5,-25)                           # delay: second range starts 8259
    imm(11,5,3,3);reg(20,3,20,37)            # 8259..825b
    branch(0,0,'lookup');emit(0)
    labels['half']=BASE+len(words)*4
    imm(13,0,20,1)
    labels['lookup']=BASE+len(words)*4
    reg(16,0,4,37);emit(3<<26|LOOKUP>>2)
    imm(12,17,5,65535)                       # lookup delay: original code
    reg(2,0,19,37)
    imm(35,18,3,0);imm(35,18,4,0x18)
    reg(0,3,3,0,2);reg(3,4,3,33)
    imm(37,3,2,2);imm(12,2,2,0xfffe)
    reg(2,20,2,37);imm(41,3,2,2)             # preserve other cache bits
    for at,target in fixups:
        dest=labels[target] if isinstance(target,str) else target
        displacement=(dest-(BASE+at*4+4))//4
        if not -32768<=displacement<=32767:raise ValueError('Branch range')
        words[at]=(words[at]&0xffff0000)|(displacement&65535)
    if len(words)>32:raise ValueError('Patch exceeds original instruction window')
    words.extend([0]*(32-len(words)))
    return struct.pack('<32I',*words)


def elf_patch(data):
    if hashlib.sha256(data).hexdigest()!=ORIGINAL_SHA:
        raise ValueError('ELF revision does not match original')
    before=data[START:END]
    if hashlib.sha256(before).hexdigest()!=WINDOW_SHA:raise ValueError('Code window changed')
    return dict(offset=START,before=before,after=replacement())


def execute_window(code,character,classification,flags=0xa55a,lookup_clobbers=True):
    """Small deterministic interpreter for ONLY this straight MIPS code window.

    It models integer operations, branches/delay slots, memory and a lookup call
    boundary. It is not a PS2 emulator and cannot prove in-game rendering.
    """
    regs=[0]*32;regs[2]=classification&0xffffffff
    regs[16]=0x100000;regs[17]=character;regs[18]=0x110000
    regs[19]=0;regs[20]=0x77777777
    mem={0x110000:7,0x110018:0x120000,0x12001e:flags}
    table=[0x2969d0]*3+[RETURN_ZERO]+[0x2969a4]*2
    mem.update({0x43b320+i*4:v for i,v in enumerate(table)})
    pc=BASE;pending=None;calls=[]
    def signed(v):return v if v<0x80000000 else v-0x100000000
    for steps in range(100):
        if pc in (RETURN_ZERO,CONTINUE):
            return dict(exit=pc,flags=mem[0x12001e],calls=calls,bitmap=regs[19])
        if pc==LOOKUP:
            calls.append((regs[4],regs[5]))
            if lookup_clobbers:
                for r in (3,4,5,6,7,8,9,10,11,12,13,14,15):regs[r]=0xdeadbeef
            regs[2]=0x130000;pc=regs[31];continue
        if not BASE<=pc<CONTINUE:raise ValueError(f'Unexpected PC {pc:x}')
        w=struct.unpack_from('<I',code,pc-BASE)[0]
        op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31
        shift=w>>6&31;fn=w&63;u=w&65535;n=u if u<32768 else u-65536
        previous=pending;pending=None;nextpc=pc+4
        if op==0:
            if fn==0:regs[rd]=regs[rt]<<shift
            elif fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            elif fn==35:regs[rd]=regs[rs]-regs[rt]
            elif fn==37:regs[rd]=regs[rs]|regs[rt]
            elif fn==42:regs[rd]=int(signed(regs[rs])<signed(regs[rt]))
            elif fn==8:pending=regs[rs]
            else:raise ValueError(f'Unsupported R opcode {fn}')
        elif op==9:regs[rt]=regs[rs]+n
        elif op==11:regs[rt]=int(regs[rs]<(n&0xffffffff))
        elif op==12:regs[rt]=regs[rs]&u
        elif op==13:regs[rt]=regs[rs]|u
        elif op==15:regs[rt]=u<<16
        elif op in (4,5):
            take=(regs[rs]==regs[rt]) if op==4 else (regs[rs]!=regs[rt])
            pending=pc+4+n*4 if take else pc+8
        elif op==3:regs[31]=pc+8;pending=(w&0x3ffffff)<<2
        elif op in (35,37):
            value=mem[(regs[rs]+n)&0xffffffff]
            regs[rt]=value if op==35 else value&65535
        elif op==41:mem[(regs[rs]+n)&0xffffffff]=regs[rt]&65535
        else:raise ValueError(f'Unsupported opcode {op}')
        regs=[r&0xffffffff for r in regs];regs[0]=0
        pc=previous if previous is not None else nextpc
    raise ValueError('Instruction budget exhausted')
