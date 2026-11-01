"""Local proof of bounded speaker indirection, NOT an ISO patch release.

Five short, reserved markers would occupy only the 13 approved label slots.
A setter hook would resolve complete names before the original strlen /
allocation / copy. The generated MIPS is executed in synthetic RAM only:
its test address is not a safe placement in the actual game executable.
"""
import argparse
import json
import mmap
from pathlib import Path
import struct

from dialogue import ROOT,sha
from gfi import encode,decode
from glyph_spacing import ORIGINAL_SHA,DELTA

BASE=0x6a0000  # Synthetic RAM ONLY: not a runtime allocation authorization.
CALLER=0x1c6550+DELTA
HOOK=0x1fd9d8
STRLEN=0x2266cc+DELTA
ROLES=[('Worker','Trabalhador'),('Man','Homem'),('Transporter','Transportador'),
       ('Cat','Gato'),('Dog','Cão')]
IDS={
    'map.msgn.057d67dc':0, 'map.msgn.0db14094':0,
    'map.msgn.0db140dc':0, 'map.msgn.0db147f8':0,
    'map.msgn.0db14898':0, 'map.msgn.0db148e0':0,
    'map.msgn.0e777edc':0, 'map.msgn.0e778354':0,
    'map.msgn.14aad804':0, 'map.msgn.0be1acd8':1,
    'map.msgn.0be25188':2, 'map.msgn.0be2d3a4':3,
    'map.msgn.19f55614':4,
}


def program(base=BASE):
    if base%16 or not 0x100000<=base<=0x1f00000:
        raise ValueError('Invalid synthetic program base')
    words=[];labels={};fixups=[]
    def emit(w):words.append(w)
    def imm(op,rs,rt,n):emit(op<<26|rs<<21|rt<<16|(n&65535))
    def reg(rs,rt,rd,fn,sa=0):emit(rs<<21|rt<<16|rd<<11|sa<<6|fn)
    def branch(op,rs,rt,target):
        fixups.append((len(words),'branch',target));imm(op,rs,rt,0)
    # Restrict markers to the original msgn label caller, saved by the setter.
    imm(35,29,3,0)
    imm(15,0,2,(CALLER+0x8000)>>16);imm(9,2,2,CALLER)
    branch(5,3,2,'fallback');emit(0)
    imm(36,4,2,0);imm(9,0,3,ord('~'))
    branch(5,2,3,'fallback');emit(0)
    imm(36,4,2,1);imm(9,2,2,-ord('0'));imm(11,2,3,5)
    branch(4,3,0,'fallback');emit(0)
    imm(36,4,3,2)
    branch(5,3,0,'fallback');emit(0)
    reg(0,2,2,0,2)
    fixups.append((len(words),'hi','table'));imm(15,0,3,0)
    fixups.append((len(words),'lo','table'));imm(9,3,3,0)
    reg(3,2,3,33);imm(35,3,4,0);reg(4,0,18,45)
    labels['fallback']=base+4*len(words)
    emit((2<<26)|((STRLEN>>2)&0x3ffffff));emit(0)
    code_size=4*len(words);labels['table']=base+code_size
    pool=bytearray(20);names=[]
    for index,(_,target) in enumerate(ROLES):
        # Force unaligned source for the already-proved scalar strcpy path.
        while (base+code_size+len(pool))%4!=1:pool.append(0)
        pointer=base+code_size+len(pool);raw=encode(target)
        struct.pack_into('<I',pool,index*4,pointer)
        names.append({'role_index':index,'pointer':pointer,'bytes':len(raw),
                      'encoded_hex':raw.hex(),'translation':target})
        pool.extend(raw+b'\0')
    for i,kind,target in fixups:
        dest=labels[target]
        if kind=='branch':
            delta=(dest-(base+4*i+4))//4
            if not -32768<=delta<=32767:raise ValueError('Lookup branch overflow')
            words[i]|=delta&65535
        elif kind=='hi':words[i]|=((dest+0x8000)>>16)&65535
        else:words[i]|=dest&65535
    blob=struct.pack('<'+'I'*len(words),*words)+pool
    return blob,{'base':base,'code_size':code_size,'table_address':labels['table'],
                 'size':len(blob),'names':names,'sha256':sha(blob)}


def emulate(raw,*,caller=CALLER,base=BASE,source_alignment=1):
    if b'\0' in raw or not 0<=source_alignment<=7:
        raise ValueError('Invalid bounded string fixture')
    blob,metadata=program(base)
    source=0x600000+source_alignment;stack=0x700000
    regions=[(base,blob),(source,raw+b'\0'),(stack,struct.pack('<Q',caller))]
    reads=[]
    def read(at,size):
        for address,data in regions:
            if address<=at and at+size<=address+len(data):
                reads.append((at,size));return int.from_bytes(data[at-address:at-address+size],'little')
        raise ValueError(f'Lookup probe escaped supplied memory {at:x}')
    regs=[0x1000+i for i in range(32)];regs[0]=0;regs[4]=regs[18]=source
    regs[29]=stack;regs[31]=HOOK+DELTA+8;original=regs.copy()
    pc=base;pending=None;steps=0
    while pc!=STRLEN:
        if steps>=128 or not base<=pc<base+metadata['code_size']:
            raise ValueError('Lookup code escaped / did not tail-call native strlen')
        steps+=1;w=struct.unpack_from('<I',blob,pc-base)[0]
        op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;u=w&65535
        n=u if u<32768 else u-65536;old=pending;pending=None
        if op==0:
            fn=w&63
            if fn==0:regs[rd]=regs[rt]<<((w>>6)&31)
            elif fn in (33,45):regs[rd]=regs[rs]+regs[rt]
            else:raise ValueError('Unsupported lookup register instruction')
        elif op==2:pending=((pc+4)&0xf0000000)|((w&0x3ffffff)<<2)
        elif op==9:regs[rt]=regs[rs]+n
        elif op==11:regs[rt]=int(regs[rs]<(n&0xffffffff))
        elif op==15:regs[rt]=u<<16
        elif op in (35,36):regs[rt]=read((regs[rs]+n)&0xffffffff,4 if op==35 else 1)
        elif op in (4,5):
            take=(regs[rs]==regs[rt]) if op==4 else (regs[rs]!=regs[rt])
            pending=pc+4+n*4 if take else pc+8
        else:raise ValueError('Unsupported lookup instruction')
        regs=[r&0xffffffff for r in regs];regs[0]=0
        pc=old if old is not None else pc+4
    pointer=regs[4];value=bytearray()
    for i in range(64):
        c=read(pointer+i,1)
        if not c:break
        value.append(c)
    else:raise ValueError('Unterminated lookup result')
    if any(regs[i]!=original[i] for i in range(32) if i not in (2,3,4,18)):
        raise ValueError('Lookup corrupted live registers')
    if regs[18]!=pointer:raise ValueError('Allocation and copy would use different sources')
    return {'raw':bytes(value),'source_pointer':pointer,'resolved':pointer!=source,
            'steps':steps,'return_address':regs[31],'live_registers_preserved':True,
            'source_and_stack_unchanged':True,'reads':reads}


def build_proposal(data,document,patches,elf):
    if sha(elf)!=ORIGINAL_SHA or struct.unpack_from('<I',elf,HOOK)[0]!=0x0c0c95b3:
        raise ValueError('Original speaker setter differs')
    from speaker_labels import bindings
    bindings(elf)
    by_id={e['id']:e for e in document['entries']};compiled={p['id']:p for p in patches}
    markers={b'~'+bytes([ord('0')+i]) for i in range(5)}
    for entry in document['entries']:
        for segment in entry['segments']:
            if segment['key']=='label' and encode(segment['translation']) in markers:
                raise ValueError('Reserved speaker marker collides with existing label')
    proposals=[];rows=[]
    for key,index in IDS.items():
        entry=by_id[key];label=entry['segments'][-1];source,target=ROLES[index]
        if (bytes.fromhex(entry['tag'])!=b'msgn' or entry['mode']!='slots'
            or entry['blocked_reasons'] or label['key']!='label'
            or label['source']!=source or label['translation']!=source):
            raise ValueError('Pending speaker metadata differs')
        original=bytes(data[entry['offset']:entry['offset']+entry['size']])
        if sha(original)!=entry['record_sha256']:raise ValueError('Speaker source fingerprint differs')
        current=compiled.get(key,{'after':original})['after'];at=label['offset']-entry['offset']
        before=bytes.fromhex(label['source_hex']);end=at+label['capacity']+1
        if current[at:end]!=before+bytes(end-at-len(before)):
            raise ValueError('Pending speaker slot was changed')
        token=b'~'+bytes([ord('0')+index])
        if len(token)>label['capacity']:raise ValueError('Marker exceeds original label slot')
        after=current[:at]+token+bytes(end-at-len(token))+current[end:]
        if len(after)!=len(current) or after[:at]!=current[:at] or after[end:]!=current[end:]:
            raise ValueError('Marker changed body, controls or record boundary')
        # Existing body encoding may use PT-BR pairs; its already-compiled bytes
        # are not reparsed by the historical ASCII parser here. Label traversal
        # is separately executed on the complete compiled record below.
        from speaker_label_space import locate
        previous=entry['segments'][-2]['offset']-entry['offset']
        if locate(elf,current,previous,b'msgn')!=at or locate(elf,after,previous,b'msgn')!=at:
            raise ValueError('Original msgn traversal changed')
        from spack_ui import execute_byte_length
        from speaker_labels import probe
        from speaker_label_space import byte_copy_probe
        encoded=encode(target);observed=emulate(token)
        if observed['raw']!=encoded or decode(encoded)!=target or execute_byte_length(elf,encoded)!=len(encoded):
            raise ValueError('Resolved label codec/native length differs')
        proof=probe(elf,encoded)
        pointer=observed['source_pointer']
        byte_copy_probe(elf,encoded,pointer%8)
        row={'id':key,'offset':entry['offset'],'size':entry['size'],
             'record_sha256':entry['record_sha256'],'compiled_record_sha256':sha(current),
             'label_offset':label['offset'],'capacity':label['capacity'],
             'marker_hex':token.hex(),'translation':target,'target_bytes':len(encoded),
             'proposed_record_sha256':sha(after),'body_controls_and_metadata_unchanged':True,
             'native_label_traversal_unchanged':True,'original_copy_probe':proof}
        rows.append(row)
        proposals.append({'id':key,'offset':entry['offset'],'before_hex':current.hex(),'after_hex':after.hex()})
    if len(rows)!=13:raise ValueError('Incomplete speaker proposal')
    return rows,proposals


def storage_evidence(elf):
    """Census for a future declared ELF segment; never use zero runs as caves."""
    from interface_text import sections,references
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Storage census ELF differs')
    phoff=struct.unpack_from('<I',elf,28)[0]
    phsize,count=struct.unpack_from('<HH',elf,42)
    if (phoff,phsize,count)!=(0x34,32,1):raise ValueError('Unexpected program headers')
    header=struct.unpack_from('<8I',elf,phoff)
    if header!=(1,4096,1048576,1048576,3444848,3889564,7,4096):
        raise ValueError('Original load segment differs')
    parts=sections(elf);end=header[2]+header[5]
    clear_start=parts['.sbss']['va'];clear_stop=(end+15)&~15
    refs=references(elf,parts).get(end,[])
    expected={0x2ff894,0x177b24,0x180e70,0x180ed0,0x19b9d0,0x19bcc0,
              0x19d564,0x19d5c8,0x1a5b74,0x1a5c6c,0x1a6074,0x1a621c}
    if {r['offset'] for r in refs}!=expected:raise ValueError('End-of-image references differ')
    windows=[]
    for a,z in ((0x180e6c,0x180e98),(0x180ed0,0x180ee8)):
        windows.append({'offset':a,'size':z-a,'sha256':sha(elf[a:z])})
    rows=[]
    for ref in refs:
        a=ref['offset'];start=max(0,a-8);size=48 if ref['kind']!='data-pointer' else 4
        rows.append({**ref,'window_offset':start if size==48 else a,'window_size':size,
                     'window_sha256':sha(elf[start:start+size] if size==48 else elf[a:a+4]),
                     'classification':('BSS clearing end; must not move over injected code' if a==0x180e70
                         else 'Startup syscall 0x3d argument; heap reservation candidate' if a==0x180ed0
                         else 'End-of-image data/size/allocator reference; data flow still to prove')})
    blob,meta=program(clear_stop)
    return {'original_load_segment':{'file_offset':header[1],'va':header[2],
                'file_size':header[4],'memory_size':header[5],'flags':header[6]},
            'elf_size':len(elf),'original_memory_end':end,
            'startup_clear_start':clear_start,'startup_clear_stop_exclusive':clear_stop,
            'clearing_rounding_bytes_beyond_declared_end':clear_stop-end,
            'header_padding_interval':[0x54,0x1000],
            'header_padding_all_zero':elf[0x54:0x1000]==bytes(0x1000-0x54),
            'candidate_declared_segment':{'file_offset':0x100,'synthetic_va_after_bss_clear':clear_stop,
                'program_bytes':len(blob),'proposed_heap_start':(clear_stop+len(blob)+15)&~15,
                'requires_new_program_header':True,'can_apply':False},
            'end_address_references':rows,'startup_instruction_windows':windows,
            'limitations':'12 conservative address references, not a complete data-flow proof. Startup clears through the next 16-byte boundary. Adding PT_LOAD alone is unsafe: kernel/game allocator ranges and any reset paths must reserve the new program first. File padding is not currently loaded or executable storage.',
            'format_reference':'https://github.com/PCSX2/pcsx2/blob/master/pcsx2/Elfheader.h'}


def investigate():
    from build_translation_pilot import load_draft,compile_draft,SOURCE
    from interface_text import SOURCE as ELF
    from preserve_v059 import WORKING,EXPECTED
    from verify_test_iso import verify_image
    working=verify_image(ROOT/WORKING)
    if working['sha256']!=EXPECTED:raise ValueError('New working base differs from v059')
    elf=ELF.read_bytes();draft,_=load_draft(ROOT/'translations/regiao-inicial-v044.json')
    with SOURCE.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
        document,patches,report=compile_draft(data,draft)
        if not report['valid']:raise ValueError('Dialogue baseline invalid')
        rows,proposals=build_proposal(data,document,patches,elf)
    blob,metadata=program()
    # No callable apply/build operation: test RAM cannot authorize real storage.
    public={'schema':1,'scope':'Prototype only; 13 speaker labels still pending in playable ISO',
            'base_iso':working,'parent_interface_recipe':'translations/interface-v059.json',
            'parent_recipe_sha256':sha((ROOT/'translations/interface-v059.json').read_bytes()),
            'map_recipe':'translations/regiao-inicial-v044.json','elf_sha256':sha(elf),
            'hook_file_offset':HOOK,'original_hook_word':'0c0c95b3',
            'required_caller_va':CALLER,'native_strlen_va':STRLEN,
            'synthetic_program':metadata,'instruction_windows':__import__('speaker_labels').bindings(elf),
            'storage_investigation':storage_evidence(elf),
            'census_records':len(document['entries']),'existing_label_marker_collisions':0,
            'proposed_records':rows,'iso_modified':False,'can_apply_to_iso':False,
            'storage_status':'No safe real-game storage allocated; synthetic base must never be injected',
            'pcsx2_executed':False,'limits':'Lookup instructions executed in bounded synthetic RAM. Original scalar traversal/length/allocation arguments/copy/getter probes composed; allocator and lifetime, cleanup, full caller, GPU and drawing not executed.'}
    folder=ROOT/'work/falantes-lookup-v001'
    (folder/'lookup-somente-sonda.bin').write_bytes(blob)
    (folder/'proposta-local.json').write_bytes((json.dumps({'can_apply_to_iso':False,'patches_not_applied':proposals},indent=2)+'\n').encode())
    (ROOT/'reports/falantes-lookup-v001.json').write_bytes((json.dumps(public,ensure_ascii=False,indent=2)+'\n').encode())
    return public


if __name__=='__main__':
    p=argparse.ArgumentParser(description='Investigar lookup de falantes sem modificar ISO');p.parse_args()
    r=investigate()
    print(json.dumps({'proposed_labels':len(r['proposed_records']),'synthetic_program_bytes':r['synthetic_program']['size'],
                      'iso_modified':False,'can_apply_to_iso':False,'report':'reports/falantes-lookup-v001.json'}))
