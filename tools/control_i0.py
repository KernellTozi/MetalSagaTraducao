"""Exact I$0 table reference; original name data remains immutable."""
import hashlib
import struct
from control_t0 import tokenize as inherited_tokens, verify as inherited_verify
from control_b15 import execute_argument

TOKEN=b'%I$0'
START,END=0x1b5d74,0x1b5da4
HANDLER_SHA='e7173459777850dc32449a40f72148b044dcaab01098f53c3fdb5fc355ecdb46'


def verify(data):
    inherited=inherited_verify(data)
    if hashlib.sha256(data[START:END]).hexdigest()!=HANDLER_SHA:raise ValueError('I lookup code mismatch')
    if struct.unpack_from('<I',data,0x33dd60+(ord('I')-0x24)*4)[0]!=0x2b4d74:
        raise ValueError('I dispatch mismatch')
    return {'elf_sha256':inherited['elf_sha256'],'handler':[START,END],'handler_sha256':HANDLER_SHA,
        'allowed_token_hex':TOKEN.hex(),'variable_index':0,'table_base_pointer_va':0x475ae8,'record_stride':128,
        'growth_allowed':False,'mode':'slots','runtime_table_binding':'not fully traced to source resource',
        'runtime_visual_status':'pending_manual_validation'}


def tokenize(raw):
    parts,_=inherited_tokens(raw)
    parts=[{**p,'kind':'preserved-i0-reference','semantics':'variable 0 -> I table entry; immutable bytes'}
           if p['kind']=='opaque-percent' and bytes.fromhex(p['hex'])==TOKEN else p for p in parts]
    return parts,any(p['kind']=='opaque-percent' for p in parts)


def execute_lookup(data,index):
    """Execute the original I handler with synthetic memory and original reader.

    File-offset PCs, original delay slots, synthetic table pointer. Does not
    emulate the string emitter, resource initialization or a full PS2 runtime.
    """
    verify(data)
    if not 0<=index<=65535:raise ValueError('Probe bounds, not proven runtime index bounds')
    raw=b'I$0!\0';regs=[0]*32;regs[18]=0x1000;regs[21]=0x3000;regs[29]=0x2000
    memory={0x475ae8:0x100000};reads=[];arguments=[];pc=START;pending=None
    for _ in range(50):
        if pc==0x1b5e88:
            return {'string_pointer':regs[17],'consumed_after_percent':regs[22]-0x1000,
                    'variable_indices':arguments,'memory_reads':reads}
        if pc==0x1b5a30:
            if regs[6]!=0x3000:raise ValueError('Unexpected I context pointer')
            result=execute_argument(data,raw[regs[4]-0x1000:],[index])
            memory[regs[5]]=result['value'];arguments.extend(result['variable_indices'])
            regs[2]=regs[4]+result['consumed'];pc=regs[31];continue
        if not START<=pc<END:raise ValueError('I probe escaped verified handler')
        w=struct.unpack_from('<I',data,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;fn=w&63;sa=w>>6&31
        n=w&65535;n=n if n<32768 else n-65536
        old=pending;pending=None;nextpc=pc+4
        if op==0:
            if fn==0:regs[rd]=regs[rt]<<sa
            elif fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            else:raise ValueError(f'Unsupported I instruction {fn}')
        elif op==3:regs[31]=pc+8;pending=((w&0x3ffffff)*4)-0xff000
        elif op==4:pending=pc+4+n*4 if regs[rs]==regs[rt] else pc+8
        elif op==9:regs[rt]=regs[rs]+n
        elif op==15:regs[rt]=(w&65535)<<16
        elif op==35:
            address=(regs[rs]+n)&0xffffffff;reads.append(address);regs[rt]=memory[address]
        else:raise ValueError(f'Unsupported I opcode {op}')
        regs=[v&0xffffffff for v in regs];regs[0]=0;pc=old if old is not None else nextpc
    raise ValueError('I instruction budget exceeded')
