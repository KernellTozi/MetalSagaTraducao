"""Bounded original %I expansion and caller scratch-area evidence, read only."""
import argparse,json,re,struct
from pathlib import Path
from dialogue import ROOT,sha
from glyph_spacing import ORIGINAL_SHA
from interface_text import SOURCE,sections
from item_names import original,RESOURCE,ITEM_BASE,ITEM_COUNT,STRIDE,compile_names
from control_b15 import execute_argument
from gfi import encode,decode

SCOPE='item-name-expansion-buffers-read-only-v002'
RECIPE='translations/interface-v051.json'
IDS=(331,372,459,838,841,849)
CALLERS=((0x473c8,0x80,0x100,0x170),(0x549e8,0,0x80,0xf0),
         (0x1c6fe4,0,0x400,0x430),(0x1ccdb0,0,0x400,0x420))
WINDOWS=((0x47220,0x47228),(0x473a8,0x473d0),(0x54960,0x549f0),(0x1c6f90,0x1c6fec),
         (0x1ccd88,0x1ccdb8),(0x1cd248,0x1cd4f0),(0x1b5a30,0x1b5ad0),
         (0x1fd274,0x1fd2c4),(0x1b5e88,0x1b5ef8),(0x1b5f58,0x1b5f94))

def caller_evidence(elf):
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Buffer ELF revision differs')
    word=0x0c000000|(0x2cc248>>2);part=sections(elf)['.text']
    calls=[at for at in range(part['offset'],part['offset']+part['size'],4) if struct.unpack_from('<I',elf,at)[0]==word]
    if calls!=[r[0] for r in CALLERS]:raise ValueError('Expansion caller set differs')
    # Exact argument materializations: destination and next known live area.
    expected={0x47220:0x27bdfe90,0x473a8:0x27b00100,0x473b8:0x24060028,0x473bc:0x27b10080,
        0x473c0:0x0200302d,0x473c4:0x03a0282d,0x473cc:0x0220202d,
        0x54960:0x27bdff10,0x54980:0xffbf00b0,0x5498c:0x27b10080,
        0x549e0:0x03a0202d,0x549e4:0x0240282d,0x549ec:0x0220302d,
        0x1c6f90:0x27bdfbd0,0x1c6fa0:0xffbf0400,0x1c6fdc:0x8e050024,0x1c6fe0:0x03a0202d,
        0x1ccd88:0x27bdfbe0,0x1ccd94:0xffbf0400,0x1ccda8:0x8e050020,0x1ccdac:0x03a0202d,
        0x1fd284:0x24040320,0x1fd288:0x0c0a9478,0x1fd294:0x24060320,
        0x1fd2a0:0xae220030,0x1fd2ac:0x8e280030,0x1fd2bc:0x0c0ad2c8,
        0x1b5f88:0xa4430000}
    for at,w in expected.items():
        if struct.unpack_from('<I',elf,at)[0]!=w:raise ValueError(f'Caller instruction differs at {at:x}')
    literals=[]
    for name in ('.data','.rodata','.sdata'):
        p=sections(elf)[name]
        literals.extend(at for at in range(p['offset'],p['offset']+p['size']-3,4) if struct.unpack_from('<I',elf,at)[0]==0x2cc248)
    emitter_target=0x0c000000|(0x2b4b20>>2)
    emitter_calls=[at for at in range(part['offset'],part['offset']+part['size'],4) if struct.unpack_from('<I',elf,at)[0]==emitter_target]
    if emitter_calls!=[0x1fd2bc]:raise ValueError('Glyph emitter direct caller set differs')
    return {'direct_calls':calls,'aligned_function_pointer_literals':literals,
        'callers':[{'call_offset':at,'destination_stack_offset':a,'next_live_area_stack_offset':z,
            'bytes_before_next_live_area':z-a,'stack_frame_bytes':frame,
            'boundary_kind':'variable-context area' if z<0x400 else 'saved return address'} for at,a,z,frame in CALLERS],
        'instruction_windows':[{'offset':a,'size':z-a,'sha256':sha(elf[a:z])} for a,z in WINDOWS],
        'separate_glyph_emitter':{'function_offset':0x1b5b20,'direct_calls':emitter_calls,
            'observed_allocation_request_bytes':0x320,'glyph_cell_stride_bytes':8,
            'terminal_code':5,'terminal_store_offset':0x1b5f88,
            'maximum_cells_before_terminal_for_observed_allocation':99,
            'executed_in_this_probe':False,
            'limits':'Separate stream emitter, not the string-expansion function. Static allocation/store evidence only; real expanded cell counts, alternative allocation paths and runtime object lifecycle remain unproved.'},
        'limits':'Four exact direct callers and argument/frame evidence. No proof that computed indirect calls cannot exist or that all incoming runtime strings have bounded expanded lengths.'}

def name_table(elf,raw,recipe,decisions):
    if sha(elf)!=ORIGINAL_SHA or sha(raw)!=recipe['item_names']['source_sha256']:raise ValueError('Name table source differs')
    patches,report=compile_names(elf,recipe['item_names'])
    if report['accepted']!=541:raise ValueError('Name baseline differs')
    current=bytearray(raw)
    for p in patches:current[p['offset']:p['offset']+len(p['after'])]=p['after']
    table=current[ITEM_BASE:ITEM_BASE+ITEM_COUNT*STRIDE];targets={int(r['id'].rsplit('.',1)[1]):r['desired_not_applied'] for r in decisions['blocked']}
    for index in IDS:
        value=encode(targets[index]);at=index*STRIDE
        if len(value)>=24:raise ValueError('Synthetic target exceeds physical field')
        table[at:at+24]=value+bytes(24-len(value))
    # Synthetic name fields only; description repack and real runtime objects
    # are not materialized. The original non-name attributes remain untouched.
    for index in range(ITEM_COUNT):
        at=index*STRIDE
        if table[at+24:at+STRIDE]!=raw[ITEM_BASE+at+24:ITEM_BASE+at+STRIDE]:raise ValueError('Synthetic name table changed attributes')
    return bytes(table),{i:targets[i] for i in IDS}

def expand(elf,table,text,capacity,variables=()):
    """Execute the original expansion function; classify/argument ABI modeled.

    The argument reader itself executes through the existing original-code
    harness. Caller-provided variable values, heap/table address and byte
    classification are synthetic. No allocator, renderer or upstream caller.
    """
    if sha(elf)!=ORIGINAL_SHA or len(table)!=ITEM_COUNT*STRIDE:raise ValueError('Expansion source/table differs')
    if capacity not in (128,1024):raise ValueError('Use a witnessed caller scratch bound')
    source=encode(text)+b'\0';tokens=list(re.finditer(rb'%I(?:\$0|[0-9]+)',source))
    if b'%' in re.sub(rb'%I(?:\$0|[0-9]+)',b'',source):raise ValueError('Only explicit item tokens in this probe')
    regs=[0]*32;regs[4]=0x610000;regs[5]=0x600000;regs[6]=0x620000;regs[29]=0x700000;regs[31]=0x7ffff0
    initial=regs.copy();mem={};output=bytearray(b'\xa5'*capacity+b'GUARD');pc=0x1cd248;pending=None;lookups=[];writes=[];arguments=[];steps=0
    def read(at,size,signed=False):
        if 0x600000<=at and at+size<=0x600000+len(source):b=source[at-0x600000:at-0x600000+size]
        elif 0x640000<=at and at+size<=0x640000+len(table):b=table[at-0x640000:at-0x640000+size]
        elif at==0x475ae8 and size==4:b=(0x640000).to_bytes(4,'little')
        elif all(at+i in mem for i in range(size)):b=bytes(mem[at+i] for i in range(size))
        elif 0xff000<=at and at+size<=0xff000+len(elf):b=elf[at-0xff000:at-0xff000+size]
        else:raise ValueError(f'Expansion read outside bounded RAM {at:x}/{size}')
        return int.from_bytes(b,'little',signed=signed)
    def write(at,value,size):
        if 0x610000<=at<0x610000+capacity+len(b'GUARD'):
            if at+size>0x610000+capacity:raise ValueError('Original expansion reaches next live caller area')
            output[at-0x610000:at-0x610000+size]=(value&((1<<(8*size))-1)).to_bytes(size,'little');writes.append(at)
        elif 0x6fff00<=at and at+size<=0x700010:
            for i in range(size):mem[at+i]=value>>(8*i)&255
        else:raise ValueError(f'Expansion write outside bounded RAM {at:x}/{size}')
    for steps in range(200000):
        if pc==0x7ffff0:
            end=output.find(0,0,capacity)
            if end<0 or output[capacity:]!=b'GUARD':raise ValueError('Expansion terminator/guard differs')
            if any(regs[r]!=initial[r] for r in (*range(16,24),29,31)):raise ValueError('Expansion callee-saved registers differ')
            return {'output_hex':bytes(output[:end]).hex(),'output_text':decode(bytes(output[:end])),'input_bytes':len(source)-1,
                'output_bytes':end,'capacity_before_next_live_area':capacity,'nul_written':True,'guard_unchanged':True,
                'callee_saved':True,'lookup_item_ids':lookups,'variable_indices':arguments,'original_instructions':steps,
                'classification_modeled':True,'upstream_inputs_proven':False}
        if pc==0x197080:
            b=regs[4]&255
            if b==0x82:value=-1
            elif b<32:value=0
            elif b<=127:value=1
            else:raise ValueError('Unmodeled source classification byte')
            regs[2]=value&0xffffffff;pc=regs[31];continue
        if pc==0x1b5a30:
            if regs[6]!=0x620000:raise ValueError('Expansion variable context differs')
            pos=regs[4]-0x600000
            if not 0<=pos<len(source):raise ValueError('Argument source outside input')
            result=execute_argument(elf,source[pos:],list(variables));index=result['value']
            if not 0<=index<ITEM_COUNT:raise ValueError('Expansion item index outside table')
            write(regs[5],index,4);regs[2]=regs[4]+result['consumed'];lookups.append(index);arguments.extend(result['variable_indices']);pc=regs[31];continue
        if not 0x1cd248<=pc<0x1cd4f0:raise ValueError(f'Expansion escaped original function {pc:x}')
        w=struct.unpack_from('<I',elf,pc)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;fn=w&63
        u=w&65535;n=u if u<32768 else u-65536;old=pending;pending=None;nextpc=pc+4
        if op==0:
            if fn==0:regs[rd]=regs[rt]<<((w>>6)&31)
            elif fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            elif fn==35:regs[rd]=regs[rs]-regs[rt]
            elif fn==8:
                target=regs[rs];pending=target-0xff000 if 0xff000<=target<0xff000+len(elf) else target
            else:raise ValueError(f'Unsupported expansion R opcode {w:08x}')
        elif op==9:regs[rt]=regs[rs]+n
        elif op in (10,11):
            v=regs[rs]&0xffffffff;v=v if op==11 or v<0x80000000 else v-0x100000000
            regs[rt]=int(v<(n&0xffffffff if op==11 else n))
        elif op==15:regs[rt]=u<<16
        elif op in (30,32,35,36,55):regs[rt]=read((regs[rs]+n)&0xffffffff,{30:16,32:1,35:4,36:1,55:8}[op],signed=op==32)
        elif op in (31,40,43,63):write((regs[rs]+n)&0xffffffff,regs[rt],{31:16,40:1,43:4,63:8}[op])
        elif op in (4,5,20,21):
            take=regs[rs]==regs[rt] if op in (4,20) else regs[rs]!=regs[rt]
            if op in (20,21) and not take:nextpc=pc+8
            else:pending=pc+4+n*4 if take else pc+8
        elif op==3:regs[31]=pc+8;pending=((w&0x3ffffff)<<2)-0xff000
        else:raise ValueError(f'Unsupported expansion opcode {w:08x}')
        regs=[v&((1<<128)-1) for v in regs];regs[0]=0;pc=old if old is not None else nextpc
    raise ValueError('Expansion instruction budget exceeded')

def investigate():
    elf=SOURCE.read_bytes();raw=original(RESOURCE);recipe=json.loads((ROOT/RECIPE).read_bytes());decisions=json.loads((ROOT/'translations/revisao-humana-itens-v001.json').read_bytes())
    proof=caller_evidence(elf);table,targets=name_table(elf,raw,recipe,decisions);cases=[]
    for at,a,z,frame in CALLERS:
        for index,target in targets.items():
            for token,variables in ((f'%I{index}',()),('%I$0',(index,))):
                text='Recebeu '+token+'!';result=expand(elf,table,text,z-a,variables)
                if result['output_text']!='Recebeu '+target+'!':raise ValueError('Full original expansion output differs')
                cases.append({'caller_offset':at,'item_id':index,'indirect':bool(variables),**result})
    repeated=' '.join(['%I331']*7);failure=None
    try:expand(elf,table,repeated,128)
    except ValueError as e:failure=str(e)
    if failure!='Original expansion reaches next live caller area':raise ValueError('Expected bounded expansion overflow was not caught')
    return {'schema':1,'scope':SCOPE,'recipe':RECIPE,'recipe_sha256':sha((ROOT/RECIPE).read_bytes()),
        'elf_sha256':sha(elf),'spack_sha256':sha(raw),'caller_evidence':proof,'synthetic_name_ids':list(IDS),
        'cases':cases,'case_count':len(cases),'negative_case':{'token_occurrences':7,'input_bytes':len(encode(repeated)),
            'expected_output_bytes':7*len(encode(targets[331]))+6,'scratch_bytes':128,'caught':failure,
            'observed_in_game':False,'meaning':'Synthetic counterexample only; not evidence of an existing game bug.'},
        'full_expansion_function_executed':True,'argument_reader_original_code_executed':True,
        'upstream_runtime_input_lengths_proven':False,'editing_authorized':False,'new_translations_applied':0,
        'originals_modified':False,'iso_created':False,'pcsx2_executed':False,
        'limits':'Exact expansion body with modeled classification/table address and supplied context values. Four direct caller scratch separations proved by instructions, not every incoming string or whole-game call graph. No name growth authorized.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description='Conferir buffers e expansão original dos seis nomes, sem aplicar alterações')
    p.add_argument('--output',type=Path,default=ROOT/'work/buffers-nomes-atual.json');a=p.parse_args();out=a.output.resolve()
    if not out.is_relative_to(ROOT/'work'):raise ValueError('Keep detailed buffer output under work/')
    if out.exists() and json.loads(out.read_bytes()).get('scope')!=SCOPE:raise ValueError('Refuse unrelated buffer output')
    result=investigate();out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'cases':result['case_count'],'scratch_bytes':[r['bytes_before_next_live_area'] for r in result['caller_evidence']['callers']],'editing_authorized':False}))
