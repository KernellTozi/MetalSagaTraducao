"""Read-only classification of the 12 remaining end-of-image consumers."""
import json,struct
from dialogue import ROOT,sha
from interface_text import SOURCE
from speaker_lookup_prototype import storage_evidence

RANGES={0x19d564:0x19d588,0x19d5c8:0x19d5e4,0x1a5b74:0x1a5ba4,
        0x1a5c6c:0x1a5c9c,0x1a6074:0x1a60ac,0x1a621c:0x1a6254}
CLASSIFICATIONS={0x2ff894:'Global data pointer to original end; writers and lifetime not fully proved',
 0x177b24:'Workspace size derived from RAM end minus original image end and reservations',
 0x180e70:'BSS clear bound; rounded write reaches 0x4B59A0',
 0x180ed0:'Startup syscall 0x3D receives original image end as lower bound',
 0x19b9d0:'Allocation and zero-fill size derived from original image end',
 0x19bcc0:'Temporary buffer size derived from original image end'}


def range_lower_bound(elf,start,call):
    regs={0:0}
    for at in range(start,call,4):
        w=struct.unpack_from('<I',elf,at)[0];op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31
        n=w&65535;n=n if n<32768 else n-65536
        if op==15:regs[rt]=(w&65535)<<16
        elif op==9:regs[rt]=regs[rs]+n if rs in regs else None
        elif op==13:regs[rt]=regs[rs]|(w&65535) if regs.get(rs) is not None else None
        elif op==0 and w&63 in (33,45,37):
            a,b=regs.get(rs),regs.get(rt)
            regs[rd]=(a|b if w&63==37 else a+b) if a is not None and b is not None else None
        elif op in (8,10,11,12,14,32,33,35,36,37,55):regs[rt]=None
        regs[0]=0
    instruction=struct.unpack_from('<I',elf,call)[0]
    if instruction>>26!=3 or (instruction&0x3ffffff)*4!=0x2a0130 or regs.get(6)!=0x4b599c:
        raise ValueError('Bounded allocator argument proof differs')
    return {'offset':start,'call_offset':call,'callee_va':0x2a0130,'lower_bound_a2':regs[6],
            'window_sha256':sha(elf[start:call+8])}


def classify(elf):
    evidence=storage_evidence(elf);rows=[]
    if {r['offset'] for r in evidence['end_address_references']}!=set(CLASSIFICATIONS)|set(RANGES):
        raise ValueError('End reference census differs')
    for row in evidence['end_address_references']:
        at=row['offset'];new=dict(row)
        if at in RANGES:
            new.update(classification='Original image end passed as lower bound to shared memory-range function',
                       argument_proof=range_lower_bound(elf,at,RANGES[at]))
        else:new['classification']=CLASSIFICATIONS[at]
        rows.append(new)
    return {'schema':1,'policy':'speaker-storage-consumer-classification-v002','elf_sha256':sha(elf),
            'references':rows,'total_references':12,'bounded_range_argument_proofs':6,
            'short_labels_remaining':13,'can_apply_to_iso':False,'originals_modified':False,
            'reason':'Classifying consumers is not a proof of reservation across all allocators, resets, loaders and kernel paths. No new segment or hook is promoted into the final candidate.',
            'alternatives':['Existing fixed slots and byte-tail packing already exhausted',
                            'Unloaded ELF header zeros are not a loaded code cave',
                            'A second segment needs heap reservation and separate runtime validation']}


if __name__=='__main__':
    result=classify(SOURCE.read_bytes());out=ROOT/'reports/falantes-memoria-v002.json'
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('12 consumers classified; 6 bounded argument proofs; ISO modification remains blocked')
