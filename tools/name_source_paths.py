"""Read-only, source-bound name pointer provenance. No growth authorization."""
import argparse
import json
import struct
from pathlib import Path
from dialogue import ROOT, sha
from interface_text import SOURCE, sections
from glyph_spacing import ORIGINAL_SHA

SCOPE = 'name-pointer-source-paths-read-only-v005'
DELTA = 0xff000
TABLE = 0x47558c
WINDOWS = ((0x798b8,0x798f8),(0x79ec8,0x79f08),(0x799a8,0x79a20),
           (0x79fb8,0x7a030),(0x79eb8,0x79ec8),(0x7a3b0,0x7a3c0),
           (0x1780d4,0x178174),(0x1784ac,0x178520),
           (0x7eed8,0x7ef34),(0x82388,0x823dc),
           (0x7f6c0,0x7f6cc),(0x827c8,0x827d0),
           (0x7ef90,0x7efac),(0x82438,0x82454),
           (0x10e11c,0x10e21c),(0x305198,0x305248),
           (0x304c80,0x304da0))


def verify(elf):
    if sha(elf) != ORIGINAL_SHA:
        raise ValueError('Name source ELF revision differs')
    tables = []
    for va, target in ((0x4041f0,0x79eb8),(0x404198,0x7a3b0),
                       (0x403d50,0x7f6c0),(0x403c80,0x827c8)):
        adjust = struct.unpack_from('<h',elf,va-DELTA+0x48)[0]
        function = struct.unpack_from('<I',elf,va-DELTA+0x4c)[0]-DELTA
        if (adjust,function) != (0,target):
            raise ValueError('Name getter virtual descriptor differs')
        tables.append({'vtable_va':va,'adjustment':adjust,'getter_offset':target})
    return {'elf_sha256':sha(elf),'virtual_descriptors':tables,
            'instruction_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS]}


def run(elf,start,windows,regs,regions,stop,handlers=None):
    """Small original integer runner using virtual PCs, including real jalr.

    Region tuples are (base, bytearray/bytes, writable). Unmapped reads and all
    writes outside supplied writable memory fail. It is not a PS2 emulator.
    """
    writes, visited = [], set()
    def access(at,size,value=None):
        for base,data,writable in regions:
            if base <= at and at+size <= base+len(data):
                off = at-base
                if value is None:
                    return int.from_bytes(data[off:off+size],'little')
                if not writable:
                    raise ValueError('Name probe attempted write to read-only source')
                data[off:off+size] = (value&((1<<(8*size))-1)).to_bytes(size,'little')
                writes.append({'address':at,'size':size})
                return
        raise ValueError(f'Name source access outside supplied memory {at:x}/{size}')
    pc, pending = start+DELTA, None
    for steps in range(10000):
        if pc == stop:
            return {'registers':regs,'writes':writes,'instruction_offsets':sorted(visited),'instructions':steps}
        if handlers is not None and handlers(pc,regs,access):
            pc=regs[31]
            continue
        at = pc-DELTA
        if not any(a <= at < z for a,z in windows):
            raise ValueError(f'Name source execution escaped bounded code {at:x}')
        visited.add(at)
        w = struct.unpack_from('<I',elf,at)[0]
        op,rs,rt,rd,fn = w>>26,w>>21&31,w>>16&31,w>>11&31,w&63
        u = w&65535; n = u if u<32768 else u-65536
        old,pending,nextpc = pending,None,pc+4
        if op == 0:
            if fn in (33,45): regs[rd] = regs[rs]+regs[rt]
            elif fn == 0: regs[rd] = regs[rt] << (w>>6&31)
            elif fn in (8,9):
                target = regs[rs]
                if fn == 9: regs[rd] = pc+8
                pending = target
            else: raise ValueError(f'Unsupported name source opcode {w:08x}')
        elif op == 9: regs[rt] = regs[rs]+n
        elif op == 10:
            value=regs[rs] if regs[rs]<0x80000000 else regs[rs]-0x100000000
            regs[rt]=int(value<n)
        elif op == 11: regs[rt] = int(regs[rs] < (n&0xffffffff))
        elif op == 12: regs[rt] = regs[rs]&u
        elif op == 15: regs[rt] = u<<16
        elif op in (30,32,33,35,36,55):
            value = access((regs[rs]+n)&0xffffffff,{30:16,32:1,33:2,35:4,36:1,55:8}[op])
            regs[rt] = value-256 if op==32 and value>=128 else value-65536 if op==33 and value>=32768 else value
        elif op in (31,40,43,63): access((regs[rs]+n)&0xffffffff,{31:16,40:1,43:4,63:8}[op],regs[rt])
        elif op in (4,5,20,21):
            take = regs[rs]==regs[rt] if op in (4,20) else regs[rs]!=regs[rt]
            if op in (20,21) and not take: nextpc = pc+8
            else: pending = pc+4+n*4 if take else pc+8
        elif op == 1 and rt in (1,3):
            take = not(regs[rs]&0x80000000)
            if rt==3 and not take: nextpc=pc+8
            else: pending=pc+4+n*4 if take else pc+8
        elif op == 3:
            regs[31]=pc+8;pending=(w&0x3ffffff)<<2
        else: raise ValueError(f'Unsupported name source opcode {w:08x}')
        regs = [v&0xffffffff for v in regs]; regs[0]=0
        pc = old if old is not None else nextpc
    raise ValueError('Name source instruction budget exceeded')


def initialize_table(elf):
    verify(elf)
    globals_ = bytearray(b'\xa5'*0x400)
    actors = bytearray(b'\xa5'*(10*0x240))
    tanks = bytearray(b'\xa5'*(29*0x2a0))
    struct.pack_into('<II',globals_,0x2f0,0x600000,0x620000)
    for i in range(10):
        struct.pack_into('<I',actors,i*0x240+0x10,0x403d50)
        struct.pack_into('<I',actors,i*0x240+0x228,0x600000+i*0x240+0x120)
    for i in range(29):
        struct.pack_into('<I',tanks,i*0x2a0+0x10,0x403c80)
        struct.pack_into('<I',tanks,i*0x2a0+0x290,0x620000+i*0x2a0+0x120)
    before = bytes(globals_)
    result = run(elf,0x1784ac,((0x1784ac,0x178520),(0x7f6c0,0x7f6cc),(0x827c8,0x827d0)),[0]*32,
                 [(0x475280,globals_,True),(0x600000,actors,False),
                  (0x620000,tanks,False),(DELTA,elf,False)],0x178520+DELTA)
    pointers = list(struct.unpack_from('<39I',globals_,0x30c))
    expected = [0x600000+i*0x240+0x130 for i in range(10)] + [0x620000+i*0x2a0+0x120 for i in range(29)]
    if pointers != expected or globals_[:0x30c] != before[:0x30c] or globals_[0x3a8:] != before[0x3a8:]:
        raise ValueError('Name table pointers or surrounding memory differ')
    if result['writes'] != [{'address':TABLE+i*4,'size':4} for i in range(39)]:
        raise ValueError('Name table stores differ')
    return {'table_va':TABLE,'entries':39,'actor_entries':10,'tank_entries':29,
            'actor_stride':0x240,'tank_stride':0x2a0,'synthetic_pointers':pointers,
            'N0_source':'actor object 0 -> field +0x228 -> record +0x10; default observed record is object+0x120',
            'N0_default_offset_in_actor':0x130,'name_lengths_proven':False,
            'memory_modeled':True,'original_virtual_getters_executed':True,
            'writes':result['writes'],'original_instructions':result['instructions'],
            'instruction_offsets':result['instruction_offsets'],'surrounding_guards_unchanged':True}


def terminate_scene_name(elf,kind):
    verify(elf)
    start = {2:0x79a18,3:0x7a028}.get(kind)
    if start is None: raise ValueError('Only observed scene types 2 and 3')
    obj = bytearray(b'\xa5'*0x50); payload = bytearray(b'X'*0x50)
    regs = [0]*32; regs[17]=0x600000; regs[18]=0x620000
    r = run(elf,start,((start,start+8),),regs,
            [(0x600000,obj,True),(0x620000,payload,True)],start+8+DELTA)
    if int.from_bytes(obj[0x3c:0x40],'little')!=0x620000 or payload!=b'X'*33+b'\0'+b'X'*(0x50-34):
        raise ValueError('Scene payload terminator differs')
    getter = 0x79eb8 if kind==2 else 0x7a3b0
    regs=[0]*32; regs[4]=0x600000; regs[31]=0x7ffff0
    g=run(elf,getter,((getter,getter+8),),regs,[(0x600000,obj,False)],0x7ffff0)
    if g['registers'][2] != 0x620000: raise ValueError('Scene getter returned a different field')
    return {'scene_type':kind,'setter_tail_offset':start,'getter_offset':getter,
            'payload_terminator_offset':33,'maximum_bytes_before_forced_terminator':33,
            'tail_instructions_executed':r['instructions'],'getter_instructions_executed':g['instructions'],
            'other_payload_bytes_unchanged':True,'full_setter_or_lifecycle_executed':False,
            'not_the_N0_actor_source':True}


def investigate():
    elf=SOURCE.read_bytes()
    text=sections(elf)['.text']
    call_word=0x0c000000|((0x10e0e8+DELTA)>>2)
    calls=[at for at in range(text['offset'],text['offset']+text['size'],4)
           if struct.unpack_from('<I',elf,at)[0]==call_word]
    if calls != [0x123f50,0x123f60,0x124310,0x1243bc,0x1243dc,0x129474,0x129684,0x129754,0x12c1f8]:
        raise ValueError('Additional formatter direct callers differ')
    return {'schema':1,'scope':SCOPE,'proof':verify(elf),'N_table_initialization':initialize_table(elf),
            'scene_name_paths':[terminate_scene_name(elf,k) for k in (2,3)],
            'additional_I_consumer':{'function_offset':0x10e0e8,'function_window_offset':0x10e11c,
                'item_handler_offset':0x10e1e8,'name_handler_offset':0x10e19c,
                'item_pointer':'global 0x475280+0x868, index * 128',
                'copier_call_offset':0x10e200,'strlen_call_offset':0x10e20c,
                'destination_capacity_proven':False,'executed':False,
                'direct_calls':calls,
                'caller_windows':[{'offset':at-24,'size':32,'sha256':sha(elf[at-24:at+8])} for at in calls],
                'status':'Original static instructions establish another I/N expansion path; destination callers need tracing.'},
            'editing_authorized':False,'new_translations_applied':0,'iso_created':False,'pcsx2_executed':False,
            'limits':'Actual name table initializer and getters executed with synthetic object pools and records. No constructor, allocator, save loading or complete setter lifecycle. The 33-byte scene bound does not establish the N0 actor-name bound, and other virtual classes are not enumerated.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description='Rastrear fontes de nomes com instruções originais, sem editar o jogo')
    p.add_argument('--output',type=Path,default=ROOT/'work/fontes-nomes-atual.json')
    out=p.parse_args().output.resolve()
    if not out.is_relative_to(ROOT/'work'):raise ValueError('Keep name source output under work/')
    if out.exists() and json.loads(out.read_bytes()).get('scope')!=SCOPE:raise ValueError('Refuse unrelated name source output')
    r=investigate();out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'name_table_entries':r['N_table_initialization']['entries'],
                      'N0_length_proven':False,'scene_bound_bytes':33,'editing_authorized':False}))
