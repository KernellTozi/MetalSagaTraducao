"""Bound name-entry BACK navigation; TITLE stays outside the release."""
import struct
from interface_graphics import sha
from glyph_spacing import ORIGINAL_SHA

POLICY='name-entry-back-navigation-v002'
WINDOWS=((0x10ba5c,0x10ba94),(0x10cba8,0x10cbe0),
         (0x10d538,0x10d588),(0x10a974,0x10a9e8),(0x32a310,0x32a3b8))


def bindings(elf):
    return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]


def execute(elf,row,alphabet,*,legend=False,name_present=False,title_mode=False,flags=0):
    if not 0<=row<=6 or not 0<=alphabet<=2:raise ValueError('Name probe outside reviewed cursor/alphabet cases')
    regs=[0]*32;regs[4]=regs[16]=0x620000;memory=bytearray(0x3040);writes=[]
    name=b'\x82\x60\x82\x61\0' if name_present else b'\0'
    memory[0x1c:0x1c+len(name)]=name
    struct.pack_into('<I',memory,0x18,flags)
    struct.pack_into('<I',memory,0x2700,alphabet)
    struct.pack_into('<HH',memory,0x3020,row,4)
    struct.pack_into('<I',memory,0x3030,0x650000)
    struct.pack_into('<I',memory,0x3038,int(title_mode))
    initial=bytes(memory);pc=0x10d540 if legend else 0x10ba74;pending=None
    def read(at,size):
        if not 0x620000<=at<=0x620000+len(memory)-size:raise ValueError('Unexpected name-navigation read')
        return int.from_bytes(memory[at-0x620000:at-0x620000+size],'little')
    for _ in range(60):
        if pc in (0x10cba8,0x10ba94,0x10a930):
            return {'called_offset':pc,'legend_mode':regs[5] if legend else None,
                'row':struct.unpack_from('<H',memory,0x3020)[0],
                'column':struct.unpack_from('<H',memory,0x3022)[0],
                'name_unchanged':memory[0x1c:0x1c+len(name)]==name,
                'changed_offsets':[i for i,(a,b) in enumerate(zip(initial,memory)) if a!=b],
                'stores':writes}
        if not (0x10ba74<=pc<0x10ba94 or 0x10d540<=pc<0x10d588):
            raise ValueError('Name navigation probe escaped declared paths')
        w=struct.unpack_from('<I',elf,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31
        u=w&65535;n=u if u<32768 else u-65536;old=pending;pending=None;nextpc=pc+4
        if op==0:
            fn=w&63
            if fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            elif fn==0:regs[rd]=regs[rt]<<((w>>6)&31)
            else:raise ValueError('Unsupported name-navigation integer instruction')
        elif op==9:regs[rt]=regs[rs]+n
        elif op==12:regs[rt]=regs[rs]&u
        elif op in (32,33,35,37):
            size=1 if op==32 else 2 if op in (33,37) else 4;v=read((regs[rs]+n)&0xffffffff,size)
            if op in (32,33) and v>=(1<<(size*8-1)):v-=1<<(size*8)
            regs[rt]=v
        elif op==41:
            at=(regs[rs]+n)&0xffffffff
            if at not in (0x623020,0x623022):raise ValueError('Name BACK changed an unauthorized field')
            struct.pack_into('<H',memory,at-0x620000,regs[rt]&65535);writes.append(at-0x620000)
        elif op in (4,5,20,21):
            take=regs[rs]==regs[rt] if op in (4,20) else regs[rs]!=regs[rt]
            if op in (20,21) and not take:nextpc=pc+8
            else:pending=pc+4+n*4 if take else pc+8
        elif op==3:regs[31]=pc+8;pending=((w&0x3ffffff)<<2)-0xff000
        else:raise ValueError('Unsupported name-navigation opcode')
        regs=[r&0xffffffff for r in regs];regs[0]=0;pc=old if old is not None else nextpc
    raise ValueError('Name BACK probe step limit')


def proof(elf,config):
    if sha(elf)!=ORIGINAL_SHA or config!={'policy':POLICY,'instruction_windows':bindings(elf)}:
        raise ValueError('Name BACK evidence differs')
    cases=[]
    for row in range(7):
        for alphabet in range(3):
            for present in (False,True):
                r=execute(elf,row,alphabet,name_present=present)
                if (not r['name_unchanged'] or set(r['changed_offsets'])-{0x3020,0x3021,0x3022,0x3023}
                    or r['row']!=0 or r['column']!=(alphabet if row else 4)):
                    raise ValueError('BACK navigation changed name or wrong cursor fields')
                cases.append({'row':row,'alphabet':alphabet,'name_present':present,
                    'next_row':r['row'],'next_column':r['column'],'name_unchanged':True})
    legend_cases=[]
    for present in (False,True):
        for title in (False,True):
            for flags in (0,2):
                r=execute(elf,1,0,legend=True,name_present=present,title_mode=title,flags=flags)
                expected=3 if present or not title and not flags&2 else 1 if title else 2
                if r['called_offset']!=0x10a930 or r['legend_mode']!=expected:raise ValueError('Name legend selection differs')
                legend_cases.append({'name_present':present,'title_mode':title,'flags':flags,'legend_mode':expected})
    return {'policy':POLICY,'instruction_windows':bindings(elf),'navigation_cases':cases,
        'legend_cases':legend_cases,'translation':'VOL.','meaning':'Return cursor from the character grid to the alphabet/category selector; no deletion or exit',
        'title_status':'Still preserved; legend selection alone does not prove the caller returns to the title screen',
        'scope':'Original integer navigation and legend selection in synthetic RAM; callback rendering, input backend and PS2 not executed'}
