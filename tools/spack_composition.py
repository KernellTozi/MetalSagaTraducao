"""One proved upgrade preview; keep shared in/de arguments unchanged."""
import struct
from item_descriptions import sha
from glyph_spacing import ORIGINAL_SHA
from spack_ui import _reader
POLICY='spack-in-de-cremento-preview-v001'
TEXT='%%I%02d%s|%s: %scremento. OK?'
SOURCE=b'%%I%02d%s|%s will be %screased. OK?'
WINDOWS=((0x1f0320,0x1f040c),(0x349fb8,0x349fc8))

def binding(elf):return {'policy':POLICY,'windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]}

def proof(elf,config):
    if sha(elf)!=ORIGINAL_SHA or config!=binding(elf):raise ValueError('Upgrade composition reader binding mismatch')
    if struct.unpack_from('<4h',elf,0x349fb8)!=(22,29,28,31) or struct.unpack_from('<4h',elf,0x349fc0)!=(143,144,145,146):
        raise ValueError('Upgrade argument ID arrays changed')
    return {'policy':POLICY,'windows':config['windows'],'format_id':142,
        'attribute_ids':[22,29,28,31],'prefix_ids':[143,144,145,146],
        'shared_prefixes_unchanged':True,'code_unchanged':True,
        'limits':'Original argument forwarding only, stopping before sprintf; no formatter or PCSX2 execution'}

def execute_arguments(elf,table,attribute_state,prefix_state):
    """Original branch-free argument forwarding with synthetic memory."""
    if not 0<=attribute_state<4 or not 0<=prefix_state<4:raise ValueError('Upgrade probe state out of bounds')
    regs=[0]*32;regs[30]=attribute_state;regs[20]=prefix_state
    regs[18]=0x470000;regs[16]=0x610000;regs[17]=7;regs[2]=0x620000;regs[29]=0x700000
    read=_reader([(0x448fb8,elf[0x349fb8:0x349fc8]),(0x475b18,struct.pack('<I',0x600000)),(0x600000,table)])
    for pc in range(0x1f038c,0x1f03ec,4):
        w=struct.unpack_from('<I',elf,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31
        n=w&65535;n=n if n<32768 else n-65536
        if op==15:regs[rt]=(w&65535)<<16
        elif op==9:regs[rt]=(regs[rs]+n)&0xffffffff
        elif op==0 and w&63==0:regs[rd]=(regs[rt]<<((w>>6)&31))&0xffffffff
        elif op==0 and w&63 in (33,45):regs[rd]=(regs[rs]+regs[rt])&0xffffffff
        elif op in (33,35):
            value=read((regs[rs]+n)&0xffffffff,2 if op==33 else 4)
            regs[rt]=value-65536 if op==33 and value>=32768 else value
        elif op==3 and pc==0x1f03e4 and (w&0x3ffffff)<<2==0x326a28:
            pass # Stop after the bound delay slot, before invoking sprintf.
        else:raise ValueError('Unsupported upgrade probe instruction')
        regs[0]=0
    return {'attribute_pointer':regs[8]-0x600000,'prefix_pointer':regs[9]-0x600000,
        'format_pointer':regs[5],'item_number':regs[6],'item_name_pointer':regs[7]}
