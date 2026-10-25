"""Exact original quirks, preserved byte-for-byte; no typo or price repair."""
import re,struct
from control_scaled100 import tokenize as inherited_tokens,verify as inherited_verify
from control_b15 import execute_argument
from control_t0 import execute_lookup as title_lookup
from control_n0 import execute_lookup as name_lookup
from password_graphics import run,memory32

PATTERN=re.compile(rb'%(?:M_[14](?![0-9])|T0(?![0-9_$])|NO(?=[,!? .\t\n]|$)|(?:5000|8000|1000|500)(?= G(?:\t|$)))')


def tokenize(raw):
    parts,_=inherited_tokens(raw);out=[]
    for p in parts:
        at=p['relative_offset'];m=PATTERN.match(raw,at)
        if p['kind']=='opaque-percent' and m:
            value=m.group();tail=value[2:] if value[1:2].isdigit() else b'O' if value==b'%NO' else b''
            p={**p,'hex':value.hex(),'kind':'preserved-dialogue-quirk',
                'semantics':'Exact observed source lexeme including literal residue; not a correction',
                'literal_tail_hex':tail.hex()}
        out.append(p)
    return out,any(p['kind']=='opaque-percent' for p in out)


def execute_motion(data,value):
    if value not in (1,4):raise ValueError('Unreviewed omitted M argument')
    raw=b'M_'+str(value).encode()+b'!\0';regs=[0]*32;regs[18]=0x1000;regs[21]=0x3000;regs[23]=0x4000;regs[29]=0x2000
    memory={};pc=0x1b5c5c;pending=None;arguments=[]
    for _ in range(70):
        if pc==0x1b5e88:
            if memory.get(0x4000)!=8 or memory.get(0x4004)!=value or arguments!=[0,value]:raise ValueError('M packed command differs')
            return {'token_hex':(b'%'+raw[:-2]).hex(),'first_argument':0,'second_argument':value,
                'consumed_after_percent':regs[18]-0x1000,'output_kind':8,'packed_value':memory[0x4004]}
        if pc==0x1b5a30:
            if regs[6]!=0x3000:raise ValueError('M context differs')
            r=execute_argument(data,raw[regs[4]-0x1000:],[])
            if r['variable_indices']:raise ValueError('M unexpectedly read a variable')
            memory[regs[5]]=r['value'];arguments.append(r['value']);regs[2]=regs[4]+r['consumed'];pc=regs[31];continue
        if not 0x1b5c5c<=pc<0x1b5cac:raise ValueError('M probe escaped handler')
        w=struct.unpack_from('<I',data,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31
        u=w&65535;n=u if u<32768 else u-65536;old=pending;pending=None
        if op==0:
            fn=w&63
            if fn==0:regs[rd]=regs[rt]<<((w>>6)&31)
            elif fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            elif fn==37:regs[rd]=regs[rs]|regs[rt]
            else:raise ValueError('Unexpected M integer instruction')
        elif op==3:regs[31]=pc+8;pending=((w&0x3ffffff)<<2)-0xff000
        elif op==4:pending=pc+4+n*4 if regs[rs]==regs[rt] else pc+8
        elif op==9:regs[rt]=regs[rs]+n
        elif op==37:regs[rt]=memory[(regs[rs]+n)&0xffffffff]&65535
        elif op in (41,43):memory[(regs[rs]+n)&0xffffffff]=regs[rt]&(65535 if op==41 else 0xffffffff)
        else:raise ValueError('Unexpected M opcode')
        regs=[r&0xffffffff for r in regs];regs[0]=0;pc=old if old is not None else pc+4
    raise ValueError('M probe step limit')


def verify(data):
    inherited=inherited_verify(data);motion=[execute_motion(data,i) for i in (1,4)]
    title=[{'selector':s,**title_lookup(data,0,s,literal=True)} for s in (0,1,7,100)]
    if any(r['consumed_after_percent']!=2 or r['variable_indices'] for r in title):raise ValueError('Literal T0 differs')
    name=name_lookup(data,0,omitted=True)
    if name['consumed_after_percent']!=1 or name['variable_indices']:raise ValueError('NO omitted argument differs')
    defaults=[]
    for digit in (ord('1'),ord('5'),ord('8')):
        dispatch=struct.unpack_from('<I',data,0x33dd60+(digit-0x24)*4)[0]-0xff000
        if dispatch!=0x1b5e84:raise ValueError('Percent-digit dispatch differs')
        regs=[0]*32;regs[18]=0x1001;regs[17]=0;regs[22]=0
        out=run(data,0x1b5e84,0x1b5e90,0x1b5ef8,regs,{})
        if out[18]!=0x1002 or out[17]!=0:raise ValueError('Default skip differs')
        defaults.append({'first_digit':chr(digit),'dispatch':dispatch,'consumes_percent_and_first_digit':True,'emits_command_text':False})
    return {'elf_sha256':inherited['elf_sha256'],'motion_cases':motion,'literal_title_cases':title,
        'omitted_name_argument':name,'percent_digit_default_cases':defaults,
        'reader_zero_input_cases':[execute_argument(data,r,[]) for r in (b'_1!',b'O,')],
        'original_typos_preserved':True,'mode':'slots','growth_allowed':False,
        'scope':'Bound original reader/handlers and generic default skip in synthetic RAM; choice renderer and PS2 not executed; price lexemes/NO residue preserved, not repaired'}
