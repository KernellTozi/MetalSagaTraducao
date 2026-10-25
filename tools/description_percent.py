"""The single original 80%% description, with unchanged percent syntax.

This does not release printf arguments, MAP commands or other percent strings.
"""
import struct
from item_descriptions import POOL,sha
from glyph_spacing import ORIGINAL_SHA
from gfi import encode

POLICY='single-80-double-percent-description-v001'
ID='item.description.03226'
SOURCE=b'Prevents enemies from|fleeing 80%% of the time.'
WINDOWS=((0x10e6a8,0x10e6c0),(0x227c18,0x227c6c),(0x228930,0x2289fc),
         (0x229e90,0x229ed4),(0x22a3f4,0x22a418),(0x347cb4,0x347cb8),
         (0x1b18ec,0x1b19bc),(0x323bb0,0x323bbb))


def bindings(elf):
    return [{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]


def execute_percent_case(elf):
    """Execute original integer dispatch/emission prefix for '%' after '%'.

    Stops before width/padding/output. No C formatter or string routine is
    replaced by a model; this is a bounded proof of one switch case only.
    """
    regs=[0]*32;regs[23]=0x600000;regs[19]=0x650000;regs[29]=0x640000
    memory={0x600000:37,0x600001:0};reads=[];writes=[]
    def read(at,size):
        reads.append((at,size));out=[]
        for p in range(at,at+size):
            if p in memory:out.append(memory[p])
            elif 0xff000<=p<0xff000+len(elf):out.append(elf[p-0xff000])
            else:raise ValueError('Unexpected read in percent dispatch probe')
        return int.from_bytes(bytes(out),'little')
    pc=0x229ea4;pending=None
    for _ in range(50):
        if pc==0x22a418:
            return {'emitted_byte':memory[0x640000],
                'emitted_length':int.from_bytes(bytes(memory[0x64004c+i] for i in range(4)),'little'),
                'format_bytes_consumed':regs[23]-0x600000,
                'argument_pointer_unchanged':regs[19]==0x650000,
                'argument_memory_reads':sum(0x650000<=a<0x650100 for a,n in reads),
                'stores':writes}
        if not (0x229ea4<=pc<0x229ed4 or 0x22a3f4<=pc<0x22a418):
            raise ValueError('Percent probe left bound case')
        w=struct.unpack_from('<I',elf,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31
        u=w&65535;n=u if u<32768 else u-65536;previous=pending;pending=None
        if op==0:
            fn=w&63
            if fn==0:regs[rd]=regs[rt]<<((w>>6)&31)
            elif fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            elif fn==8:pending=regs[rs]-0xff000
            else:raise ValueError('Unsupported percent integer opcode')
        elif op==9:regs[rt]=regs[rs]+n
        elif op==11:regs[rt]=int(regs[rs]<(n&0xffffffff))
        elif op==12:regs[rt]=regs[rs]&u
        elif op==15:regs[rt]=u<<16
        elif op in (32,35):
            size=1 if op==32 else 4;v=read((regs[rs]+n)&0xffffffff,size)
            regs[rt]=v-256 if op==32 and v>=128 else v
        elif op in (40,43):
            size=1 if op==40 else 4;at=(regs[rs]+n)&0xffffffff
            if not 0x640000<=at<=0x640100-size:raise ValueError('Percent store outside scratch')
            for i in range(size):memory[at+i]=(regs[rt]>>(8*i))&255
            writes.append({'address':at,'bytes':size})
        elif op==4:pending=pc+4+n*4 if regs[rs]==regs[rt] else pc+8
        else:raise ValueError('Unsupported percent dispatch opcode')
        regs=[r&0xffffffff for r in regs];regs[0]=0;pc=previous if previous is not None else pc+4
    raise ValueError('Percent probe step limit')


def proof(elf,raw,config):
    if (sha(elf)!=ORIGINAL_SHA or config!={'policy':POLICY,'id':ID,
        'source_sha256':sha(SOURCE),'instruction_windows':bindings(elf)}):
        raise ValueError('Single percent description evidence differs')
    at=POOL+0x3226
    if raw[at:at+len(SOURCE)+1]!=SOURCE+b'\0':raise ValueError('Unexpected percent description source')
    probe=execute_percent_case(elf)
    if (probe['emitted_byte']!=37 or probe['emitted_length']!=1
        or probe['format_bytes_consumed']!=1 or not probe['argument_pointer_unchanged']
        or probe['argument_memory_reads']):raise ValueError('Percent literal case consumed an argument')
    return {'policy':POLICY,'instruction_windows':bindings(elf),'literal_case_probe':probe,
        'consumer_difference':'Format consumer collapses %% to %. Raw-copy and %s-wrapper consumers retain both original percent bytes; their existing behavior is preserved.',
        'limits':'One original description only; no full formatter/PS2 execution or general percent release'}


def validate_value(before,text):
    if before!=SOURCE or text.count('%%')!=1 or text.count('%')!=2 or '80%%' not in text:
        raise ValueError('The exact original 80%% token must be preserved')
    from description_pool import validate_value as ordinary
    # Same-length placeholders reuse all ordinary bounds/facts/terminology checks.
    # The bytes returned are the real unchanged %% sequence, never placeholders.
    ordinary(before.replace(b'%%',b'pp'),text.replace('%%','pp'))
    return encode(text)
