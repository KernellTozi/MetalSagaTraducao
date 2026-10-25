"""Exact T$0 lookup preservation; no inference of canonical entity identity."""
import hashlib
import struct
from control_numeric15 import tokenize as inherited_tokens, verify as inherited_verify
from control_b15 import execute_argument

TOKEN=b'%T$0'
WINDOWS=((0x1b5d2c,0x1b5d74,'d52e88d683ab08c287d43e547b69e463029ab9a6af4d10eef293d894d162f4f8'),
         (0x7f698,0x7f6a0,'f06d86d2158c0b83da5ac105b082b9811449614fe9c06af47266a1cacadcae68'),
         (0x6bb60,0x6bb84,'6fa08c8e897e93b9d5c8576345ac613ff3c99fe7b9bb25b429744b4181f04d3a'))


def verify(data):
    inherited=inherited_verify(data)
    for start,end,expected in WINDOWS:
        if hashlib.sha256(data[start:end]).hexdigest()!=expected:raise ValueError('T lookup code mismatch')
    if struct.unpack_from('<I',data,0x33dd60+(ord('T')-0x24)*4)[0]!=0x2b4d2c:
        raise ValueError('T dispatch mismatch')
    return {'elf_sha256':inherited['elf_sha256'],'windows':[{'start':a,'end':b,'sha256':h} for a,b,h in WINDOWS],
        'allowed_token_hex':TOKEN.hex(),'variable_index':0,'entity_stride':0x240,
        'entity_base_pointer_va':0x475570,'object_pointer_offset':0x228,'selector_offset':0x6c,
        'string_table_va':0x363478,'growth_allowed':False,'mode':'slots',
        'identity':'unresolved; do not infer canonical character ID from source text',
        'runtime_visual_status':'pending_manual_validation'}


def tokenize(raw):
    parts,_=inherited_tokens(raw)
    parts=[{**p,'kind':'preserved-t0-reference','semantics':'variable 0 -> T lookup; immutable bytes'}
           if p['kind']=='opaque-percent' and bytes.fromhex(p['hex'])==TOKEN else p for p in parts]
    return parts,any(p['kind']=='opaque-percent' for p in parts)


def execute_lookup(data,index,selector,*,literal=False):
    """Execute original T handler and both accessors against synthetic memory.

    Numeric-reader calls execute the original leaf via its existing probe.
    PCs/return addresses use file offsets; runtime data pointers retain their
    literal addresses. This is a bounded instruction test, not a PS2 emulator.
    """
    verify(data)
    if not 0<=index<=100 or not 0<=selector<=100:raise ValueError('Probe bounds')
    if literal and index!=0:raise ValueError('Only reviewed literal T0')
    raw=b'T0!\0' if literal else b'T$0!\0';regs=[0]*32;regs[18]=0x1000;regs[21]=0x3000;regs[29]=0x2000
    memory={0x475570:0x100000,0x100000+index*0x240+0x228:0x200000,
            0x200000+0x6c:selector,0x363478+index*4:0x300000,
            0x300000+selector*4:0x400000}
    reads=[];arguments=[];pc=0x1b5d2c;pending=None
    def signed(v):return v if v<0x80000000 else v-0x100000000
    for _ in range(100):
        if pc==0x1b5e88:
            return {'string_pointer':regs[17],'consumed_after_percent':regs[22]-0x1000,
                    'variable_indices':arguments,'memory_reads':reads}
        if pc==0x1b5a30:
            if regs[6]!=0x3000:raise ValueError('Unexpected context pointer')
            result=execute_argument(data,raw[regs[4]-0x1000:],[index])
            memory[regs[5]]=result['value'];arguments.extend(result['variable_indices'])
            regs[2]=regs[4]+result['consumed'];pc=regs[31];continue
        if not any(a<=pc<b for a,b,_ in WINDOWS):raise ValueError('T probe escaped verified windows')
        w=struct.unpack_from('<I',data,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;fn=w&63;sa=w>>6&31
        n=w&65535;n=n if n<32768 else n-65536
        old=pending;pending=None;nextpc=pc+4
        if op==0:
            if fn==0:regs[rd]=regs[rt]<<sa
            elif fn==8:pending=regs[rs]
            elif fn==24:regs[rd]=signed(regs[rs])*signed(regs[rt])
            elif fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            else:raise ValueError(f'Unsupported T instruction {fn}')
        elif op==3:regs[31]=pc+8;pending=((w&0x3ffffff)*4)-0xff000
        elif op==4:pending=pc+4+n*4 if regs[rs]==regs[rt] else pc+8
        elif op==9:regs[rt]=regs[rs]+n
        elif op==15:regs[rt]=(w&65535)<<16
        elif op==35:
            address=(regs[rs]+n)&0xffffffff;reads.append(address);regs[rt]=memory[address]
        else:raise ValueError(f'Unsupported T opcode {op}')
        regs=[v&0xffffffff for v in regs];regs[0]=0;pc=old if old is not None else nextpc
    raise ValueError('T instruction budget exceeded')
