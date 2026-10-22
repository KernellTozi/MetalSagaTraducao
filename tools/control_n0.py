"""Exact indirect N$0 name lookup; N$3 and other variants remain blocked."""
import hashlib
import struct
from control_i0 import tokenize as inherited_tokens, verify as inherited_verify
from control_b15 import execute_argument

TOKEN=b'%N$0'
START,END=0x1b5cac,0x1b5ce0
HANDLER_SHA='ad4b84a4542c7b5a456286ba5cb796ceaa155374e24940d6f3e1eee62431cd1e'


def verify(data):
    inherited=inherited_verify(data)
    if hashlib.sha256(data[START:END]).hexdigest()!=HANDLER_SHA:raise ValueError('N lookup code mismatch')
    if struct.unpack_from('<I',data,0x33dd60+(ord('N')-0x24)*4)[0]!=0x2b4cac:
        raise ValueError('N dispatch mismatch')
    return {'elf_sha256':inherited['elf_sha256'],'handler':[START,END],'handler_sha256':HANDLER_SHA,
        'allowed_token_hex':TOKEN.hex(),'variable_index':0,'name_pointer_table_va':0x47558c,'pointer_stride':4,
        'growth_allowed':False,'mode':'slots','runtime_identity':'context-dependent; no canonical actor or vehicle ID inferred',
        'runtime_visual_status':'pending_manual_validation'}


def tokenize(raw):
    parts,_=inherited_tokens(raw)
    parts=[{**p,'kind':'preserved-n0-reference','semantics':'variable 0 -> N name pointer; immutable bytes'}
           if p['kind']=='opaque-percent' and bytes.fromhex(p['hex'])==TOKEN else p for p in parts]
    return parts,any(p['kind']=='opaque-percent' for p in parts)


def execute_lookup(data,index):
    """Run original N handler and numeric reader against synthetic memory.

    File-offset PCs, original delay slots, synthetic pointer-table entry.
    Does not execute name initialization, emitter or the complete PS2 runtime.
    """
    verify(data)
    if not 0<=index<=65535:raise ValueError('Probe bounds, not proven runtime table bounds')
    raw=b'N$0!\0';regs=[0]*32;regs[18]=0x1000;regs[21]=0x3000;regs[29]=0x2000
    memory={0x47558c+index*4:0x100000+index*16};reads=[];arguments=[];pc=START;pending=None
    for _ in range(50):
        if pc==0x1b5e88:
            return {'string_pointer':regs[17],'consumed_after_percent':regs[22]-0x1000,
                    'variable_indices':arguments,'memory_reads':reads}
        if pc==0x1b5a30:
            if regs[6]!=0x3000:raise ValueError('Unexpected N context pointer')
            result=execute_argument(data,raw[regs[4]-0x1000:],[index])
            memory[regs[5]]=result['value'];arguments.extend(result['variable_indices'])
            regs[2]=regs[4]+result['consumed'];pc=regs[31];continue
        if not START<=pc<END:raise ValueError('N probe escaped verified handler')
        w=struct.unpack_from('<I',data,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;fn=w&63;sa=w>>6&31
        n=w&65535;n=n if n<32768 else n-65536
        old=pending;pending=None;nextpc=pc+4
        if op==0:
            if fn==0:regs[rd]=regs[rt]<<sa
            elif fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            else:raise ValueError(f'Unsupported N instruction {fn}')
        elif op==3:regs[31]=pc+8;pending=((w&0x3ffffff)*4)-0xff000
        elif op==4:pending=pc+4+n*4 if regs[rs]==regs[rt] else pc+8
        elif op==9:regs[rt]=regs[rs]+n
        elif op==15:regs[rt]=(w&65535)<<16
        elif op==35:
            address=(regs[rs]+n)&0xffffffff;reads.append(address);regs[rt]=memory[address]
        else:raise ValueError(f'Unsupported N opcode {op}')
        regs=[v&0xffffffff for v in regs];regs[0]=0;pc=old if old is not None else nextpc
    raise ValueError('N instruction budget exceeded')
