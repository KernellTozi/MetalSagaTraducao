"""Explicit observed selectors, proved through the original argument/handlers.

No generic percent release, float syntax, N$3 tank-name editing or table edits.
"""
import struct
from control_n0 import tokenize as inherited_tokens,verify as inherited_verify
from control_b15 import execute_argument

SELECTORS={'decimal':(0,2,5,10,11,12,13,14,16,17,18),
           'item':(1,2,9,10,15,19),'name':(1,2,6,10)}
PREFIX={'decimal':b'%$','item':b'%I$','name':b'%N$'}
ALLOWED={PREFIX[k]+str(i).encode():(k,i) for k,ids in SELECTORS.items() for i in ids}
BOUNDS={'decimal':(0x1b5dec,0x1b5e84),'item':(0x1b5d74,0x1b5da4),'name':(0x1b5cac,0x1b5ce0)}


def tokenize(raw):
    parts,_=inherited_tokens(raw);out=[]
    for p in parts:
        token=bytes.fromhex(p['hex']);end=p['relative_offset']+len(token)
        if p['kind']=='opaque-percent' and token in ALLOWED:
            kind,index=ALLOWED[token]
            if kind!='decimal' or raw[end:end+1]!=b'f':
                p={**p,'kind':'preserved-reviewed-variable-reference',
                    'semantics':f'Original {kind} handler, variable {index}; immutable command bytes'}
        out.append(p)
    return out,any(p['kind']=='opaque-percent' for p in out)


def _execute(data,kind,selector,value):
    if kind not in SELECTORS or selector not in SELECTORS[kind]:raise ValueError('Selector not explicitly approved')
    if not 0<=value<=0xffffffff or kind!='decimal' and value>65535:raise ValueError('Value outside synthetic probe bounds')
    token=PREFIX[kind]+str(selector).encode();raw=token[1:]+b'!\0'
    regs=[0]*32;regs[18]=0x1000;regs[21]=0x3000;regs[29]=0x2000
    memory={0x475ae8:0x100000,0x47558c+value*4:0x100000+value*16}
    arguments=[];reads=[];start,end=BOUNDS[kind];pc=start;pending=None
    stop=0x227a28 if kind=='decimal' else 0x1b5e88
    for _ in range(90):
        if pc==stop:
            consumed=regs[22]-0x1000
            if arguments!=[selector] or consumed!=len(token)-1:raise ValueError('Variable reader selected/consumed a different argument')
            result={'kind':kind,'selector':selector,'value':value,'variable_indices':arguments,
                'consumed_after_percent':consumed,'memory_reads':reads}
            if kind=='decimal':
                if regs[5]!=0x448dc0 or regs[6]!=value:raise ValueError('Decimal signed format argument differs')
                result['format_offset']=regs[5]-0xff000;result['signed_value']=value if value<0x80000000 else value-0x100000000
            else:result['string_pointer']=regs[17]
            return result
        if pc==0x1b5a30:
            if regs[6]!=0x3000:raise ValueError('Variable context pointer differs')
            values=[0x5a5a5a5a]*(selector+1);values[selector]=value
            r=execute_argument(data,raw[regs[4]-0x1000:],values)
            memory[regs[5]]=r['value'];arguments.extend(r['variable_indices'])
            regs[2]=regs[4]+r['consumed'];pc=regs[31];continue
        if not start<=pc<end:raise ValueError('Variable probe escaped bound handler')
        w=struct.unpack_from('<I',data,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31
        n=w&65535;n=n if n<32768 else n-65536;old=pending;pending=None
        if op==0:
            fn=w&63
            if fn==0:regs[rd]=regs[rt]<<((w>>6)&31)
            elif fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            else:raise ValueError('Unsupported variable handler instruction')
        elif op==3:regs[31]=pc+8;pending=((w&0x3ffffff)<<2)-0xff000
        elif op in (4,5):pending=pc+4+n*4 if (regs[rs]==regs[rt])==(op==4) else pc+8
        elif op==9:regs[rt]=regs[rs]+n
        elif op==15:regs[rt]=(w&65535)<<16
        elif op==32:
            at=(regs[rs]+n)&0xffffffff
            if not 0x1000<=at<0x1000+len(raw):raise ValueError('Variable suffix read outside source')
            v=raw[at-0x1000];regs[rt]=v if v<128 else v-256
        elif op==35:
            at=(regs[rs]+n)&0xffffffff;reads.append(at)
            if at not in memory:raise ValueError('Variable lookup outside synthetic table')
            regs[rt]=memory[at]
        else:raise ValueError('Unsupported variable handler opcode')
        regs=[r&0xffffffff for r in regs];regs[0]=0;pc=old if old is not None else pc+4
    raise ValueError('Variable handler step limit')


def verify(data):
    inherited=inherited_verify(data);cases=[]
    for kind,selectors in SELECTORS.items():
        values=(0,1,999,0x7fffffff,0x80000000,0xffffffff) if kind=='decimal' else (0,1,1348,65535)
        for selector in selectors:
            for value in values:
                r=_execute(data,kind,selector,value)
                if kind=='item' and r['string_pointer']!=0x100000+value*128:raise ValueError('Item name stride differs')
                if kind=='name' and r['string_pointer']!=0x100000+value*16:raise ValueError('Indirect name pointer differs')
                cases.append(r)
    return {'elf_sha256':inherited['elf_sha256'],'approved_selectors':SELECTORS,
        'argument_reader':[0x1b5a30,0x1b5ad0],'handlers':BOUNDS,'probe_cases':cases,
        'case_count':len(cases),'allowed_token_hex':sorted(t.hex() for t in ALLOWED),
        'growth_allowed':False,'mode':'slots','float_suffix_blocked':True,
        'scope':'Original handlers and argument reader in synthetic RAM; no emitter, table initialization, canonical identity, runtime index limit or PS2 execution proved'}
