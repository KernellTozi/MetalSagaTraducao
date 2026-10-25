"""Opt-in for three observed variable/100 tokens; no general float grammar."""
import re,struct
from control_variable_refs import tokenize as inherited_tokens,verify as inherited_verify
from control_b15 import execute_argument

TOKENS={b'%$0f100',b'%$2f100',b'%$13f100'}
MATCH=re.compile(rb'%\$(?:0|2|13)f100(?![A-Za-z0-9_$])')


def tokenize(raw):
    parts,_=inherited_tokens(raw);out=[]
    for p in parts:
        at=p['relative_offset'];m=MATCH.match(raw,at)
        if p['kind']=='opaque-percent' and m:
            p={**p,'hex':m.group().hex(),'kind':'preserved-scaled100-reference',
               'semantics':'Original signed variable divided by literal 100; complete token immutable'}
        out.append(p)
    return out,any(p['kind']=='opaque-percent' for p in out)


def execute(data,token,value):
    if token not in TOKENS or not 0<=value<=0xffffffff:raise ValueError('Unreviewed scaled token/value')
    selector=int(token[2:token.index(b'f')]);raw=token[1:]+b'!\0'
    regs=[0]*32;regs[18]=0x1000;regs[21]=0x3000;regs[29]=0x2000
    memory={};floats={};reads=[];args=[];converted=[];pc=0x1b5dec;pending=None
    f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
    for _ in range(100):
        if pc==0x227a28:
            if regs[5]!=0x448db8 or regs[6]!=0x12345678 or len(converted)!=1:raise ValueError('Scaled format forwarding differs')
            if args!=[value,100] or reads!=[selector] or regs[22]-0x1000!=len(token)-1:raise ValueError('Scaled argument consumption differs')
            return {'token_hex':token.hex(),'variable_index':selector,'value_bits':value,'divisor':100,
                'consumed_after_percent':regs[22]-0x1000,'ratio_f32':converted[0],
                'format_offset':0x349db8,'conversion_stub_result_forwarded':True}
        if pc==0x1b5a30:
            if regs[6]!=0x3000:raise ValueError('Scaled argument context differs')
            values=[0x5a5a5a5a]*(selector+1);values[selector]=value
            r=execute_argument(data,raw[regs[4]-0x1000:],values)
            memory[regs[5]]=r['value'];args.append(r['value']);reads.extend(r['variable_indices'])
            regs[2]=regs[4]+r['consumed'];pc=regs[31];continue
        if pc==0x183e38:
            converted.append(floats[12]);regs[2]=0x12345678;pc=regs[31];continue
        if not 0x1b5dec<=pc<0x1b5e84:raise ValueError('Scaled probe escaped original handler')
        w=struct.unpack_from('<I',data,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31
        u=w&65535;n=u if u<32768 else u-65536;old=pending;pending=None
        if op==0:
            fn=w&63
            if fn==0:regs[rd]=regs[rt]<<((w>>6)&31)
            elif fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            else:raise ValueError('Unexpected scaled integer instruction')
        elif op==3:regs[31]=pc+8;pending=((w&0x3ffffff)<<2)-0xff000
        elif op in (4,5):pending=pc+4+n*4 if (regs[rs]==regs[rt])==(op==4) else pc+8
        elif op==9:regs[rt]=regs[rs]+n
        elif op==15:regs[rt]=u<<16
        elif op==32:
            at=(regs[rs]+n)&0xffffffff
            if not 0x1000<=at<0x1000+len(raw):raise ValueError('Scaled suffix read outside token')
            regs[rt]=raw[at-0x1000]
        elif op==49:
            at=(regs[rs]+n)&0xffffffff
            if at not in memory:raise ValueError('Scaled FP load outside argument slots')
            floats[rt]=memory[at]
        elif op==17:
            fd=w>>6&31;fs=w>>11&31;ft=w>>16&31;fn=w&63
            if rs==20 and fn==32:
                v=floats[fs];floats[fd]=f32(v if v<0x80000000 else v-0x100000000)
            elif rs==16 and fn==3:floats[fd]=f32(floats[fs]/floats[ft])
            else:raise ValueError('Unexpected scaled FP instruction')
        else:raise ValueError('Unexpected scaled opcode')
        regs=[r&0xffffffff for r in regs];regs[0]=0;pc=old if old is not None else pc+4
    raise ValueError('Scaled handler step budget exceeded')


def verify(data):
    inherited=inherited_verify(data)
    if data[0x349db8:0x349dbd]!=b'%.2f\0':raise ValueError('Scaled format differs')
    cases=[execute(data,t,v) for t in sorted(TOKENS) for v in (0,1,99,100,101,12345,0x7fffffff,0xffffffff)]
    return {'elf_sha256':inherited['elf_sha256'],'allowed_token_hex':sorted(t.hex() for t in TOKENS),
        'handler':[0x1b5dec,0x1b5e84],'argument_reader':[0x1b5a30,0x1b5ad0],
        'format_offset':0x349db8,'format_hex':b'%.2f\0'.hex(),'case_count':len(cases),'cases':cases,
        'scope':'Original reader/handler instruction paths with synthetic RAM and finite FP32 model; float conversion helper stubbed, formatter/emitter/PS2 not executed',
        'mode':'slots','growth_allowed':False,'divisor_immutable':100}
