"""Opt-in recognition of one evidenced dynamic control; legacy lexer unchanged."""
import hashlib
import struct
from dialogue_formats import tokens
from glyph_spacing import ORIGINAL_SHA
B15=b'%B$15'
WINDOWS=((0x1b5a30,0x1b5ad0,'515375499c4437590c7351fb3fee25aa10c1b45bf295ac6d4cdf2723e7523791'),
         (0x1b5ce0,0x1b5d2c,'5bac25ea430efbf5944dd998473c946ad5b77740f291ad712b4ca360c7996c43'))


def verify(data):
    if hashlib.sha256(data).hexdigest()!=ORIGINAL_SHA:raise ValueError('ELF revision mismatch')
    for a,b,expected in WINDOWS:
        if hashlib.sha256(data[a:b]).hexdigest()!=expected:raise ValueError('B15 reader/handler mismatch')
    if struct.unpack_from('<I',data,0x33dd60+(ord('B')-0x24)*4)[0]!=0x2b4ce0:raise ValueError('B dispatch changed')
    return {'elf_sha256':ORIGINAL_SHA,'argument_reader':[0x1b5a30,0x1b5ad0],
        'b_handler':[0x1b5ce0,0x1b5d2c],'dispatch_table':0x33dd60,'allowed_token_hex':B15.hex(),
        'variable_index':15,'grammar':'B plus numeric argument reader: $15 loads uint32 at context+15*4',
        'growth_allowed':False,'mode':'slots','runtime_visual_status':'pending_manual_validation'}


def tokenize(raw):
    parts,_=tokens(raw);out=[]
    for part in parts:
        if part['kind']=='opaque-percent' and bytes.fromhex(part['hex'])==B15:
            part={**part,'kind':'preserved-b15-reference','semantics':'variable 15 -> B string lookup; immutable bytes'}
        out.append(part)
    return out,any(t['kind']=='opaque-percent' for t in out)


def execute_argument(data,raw,variables):
    """Execute the original leaf reader, including R5900 MULT rd and delay slots.

    This bounded probe models only code 0x1b5a30..1b5ad0, not the PS2 runtime.
    """
    regs=[0]*32;regs[4]=0x1000;regs[5]=0x2000;regs[6]=0x3000;regs[31]=0x5000
    memory={};pc=0x1b5a30;pending=None;reads=[]
    def signed(v):return v if v<0x80000000 else v-0x100000000
    def byte(at):
        if 0x1000<=at<0x1000+len(raw):return raw[at-0x1000]
        raise ValueError('Read outside parameter source')
    for _ in range(400):
        if pc==0x5000:return {'consumed':regs[2]-0x1000,'value':memory[0x2000],'variable_indices':reads}
        if not 0x1b5a30<=pc<0x1b5ad0:raise ValueError('Reader escaped its window')
        w=struct.unpack_from('<I',data,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;sa=w>>6&31;fn=w&63
        n=w&65535;n=n if n<32768 else n-65536
        old=pending;pending=None;nextpc=pc+4
        if op==0:
            if fn==0:regs[rd]=regs[rt]<<sa
            elif fn==3:regs[rd]=signed(regs[rt])>>sa
            elif fn==8:pending=regs[rs]
            elif fn==24:regs[rd]=signed(regs[rs])*signed(regs[rt])
            elif fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            else:raise ValueError(f'Unsupported R instruction {fn}')
        elif op in (4,5,21):
            take=regs[rs]==regs[rt] if op==4 else regs[rs]!=regs[rt]
            if op==21 and not take:nextpc=pc+8
            else:pending=pc+4+n*4 if take else pc+8
        elif op==9:regs[rt]=regs[rs]+n
        elif op==11:regs[rt]=int(regs[rs]<(n&0xffffffff))
        elif op in (32,36):
            value=byte((regs[rs]+n)&0xffffffff);regs[rt]=value-256 if op==32 and value>=128 else value
        elif op==35:
            at=(regs[rs]+n)&0xffffffff
            if at<0x3000 or (at-0x3000)%4:raise ValueError('Unexpected variable address')
            index=(at-0x3000)//4
            if index>=len(variables):raise ValueError('Variable index out of probe bounds')
            reads.append(index);regs[rt]=variables[index]
        elif op==43:memory[(regs[rs]+n)&0xffffffff]=regs[rt]
        else:raise ValueError(f'Unsupported instruction {op}')
        regs=[v&0xffffffff for v in regs];regs[0]=0;pc=old if old is not None else nextpc
    raise ValueError('Argument reader instruction budget exceeded')
