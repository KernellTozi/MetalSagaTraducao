"""Bound original character-class branch identifying the canine Coat label."""
import struct
from item_descriptions import sha
from glyph_spacing import ORIGINAL_SHA

POLICY='canine-coat-status-label-v001'
WINDOWS=((0x118934,0x118a18),(0x32b648,0x32b69a),(0x3495a0,0x3495a4))


def bindings(elf):
    return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]


def execute(elf,character_class):
    if not 0<=character_class<10:raise ValueError('Class probe outside original ten labels')
    regs=[0]*32;regs[20]=0x620000;regs[29]=0x640000;regs[16]=0x630000
    mem={}
    def put(at,value):
        for i in range(4):mem[at+i]=(value>>(i*8))&255
    put(0x62002c,character_class);put(0x62004c,456);put(0x620058,123)
    for i,v in enumerate(elf[0x32b648:0x32b670]):mem[0x640040+i]=v
    def read(at):
        if any(at+i not in mem for i in range(4)):raise ValueError('Unknown canine status probe read')
        return int.from_bytes(bytes(mem[at+i] for i in range(4)),'little')
    calls=[];pc=0x118990;pending=None
    for _ in range(100):
        if pc==0x227a28:
            calls.append({'format_offset':regs[5]-0xff000,'argument':regs[6]})
            if len(calls)==2:return calls
            pc=regs[31];continue
        if not 0x118990<=pc<0x118a18:raise ValueError('Status probe escaped original class branches')
        w=struct.unpack_from('<I',elf,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31
        u=w&65535;n=u if u<32768 else u-65536;old=pending;pending=None
        if op==0:
            fn=w&63
            if fn==0:regs[rd]=regs[rt]<<((w>>6)&31)
            elif fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            else:raise ValueError('Unsupported status probe integer instruction')
        elif op==9:regs[rt]=regs[rs]+n
        elif op==10:regs[rt]=int(regs[rs]<n)
        elif op==15:regs[rt]=u<<16
        elif op==35:regs[rt]=read((regs[rs]+n)&0xffffffff)
        elif op==4:pending=pc+4+n*4 if regs[rs]==regs[rt] else pc+8
        elif op==3:regs[31]=pc+8;pending=((w&0x3ffffff)<<2)-0xff000
        else:raise ValueError('Unsupported status probe opcode')
        regs=[r&0xffffffff for r in regs];regs[0]=0;pc=old if old is not None else pc+4
    raise ValueError('Status probe step limit')


def proof(elf,config):
    if sha(elf)!=ORIGINAL_SHA or config!={'policy':POLICY,'instruction_windows':bindings(elf)}:
        raise ValueError('Canine status context binding differs')
    rows=[]
    for i in range(10):
        calls=execute(elf,i)
        if i>=6:
            if calls[0]['argument']!=0x4485a0 or elf[0x3495a0:0x3495a4]!=b'Dog\0':
                raise ValueError('Coat branch is not the bound canine class')
            if calls[1]!={'format_offset':0x32b690,'argument':123}:raise ValueError('Canine Coat field differs')
        elif calls[1]!={'format_offset':0x32b680,'argument':456}:raise ValueError('Human driving branch differs')
        rows.append({'class_index':i,'label_offset':calls[1]['format_offset'],'argument':calls[1]['argument']})
    return {'policy':POLICY,'instruction_windows':bindings(elf),'class_cases':rows,
        'canine_class_indexes':[6,7,8,9],'field':'Original character data +0x58; value and mechanics unchanged',
        'scope':'Original class branches and argument forwarding in synthetic RAM; no formatter, rendering or PS2 execution'}
