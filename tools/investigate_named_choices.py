"""Read-only evidence for named choices. Does not enable a reinsertion policy."""
import argparse
from collections import Counter
import hashlib
import json
import mmap
from pathlib import Path
import struct
from dialogue_advanced import SsdIndex
from dialogue_formats import tokens
from glyph_spacing import ORIGINAL_SHA
from reinsertion import ROOT,SOURCE,descriptor,source_hash

DELTA=0xff000
# Exact R5900 words, including delay slots. Do not interpret these using a
# generic MIPS32 disassembler: several R5900 instructions alias other ISAs.
WORDS={0x2c14bc:0x2463a718,0x2c20cc:0x2463a6e0,
       0x40a72c:0x2c5c20,0x40a734:0x2c5920,
       0x40a6f4:0x2c5e58,0x40a6fc:0x2c5e30,
       0x2c5928:0x0c0b1492,0x2c592c:0x24050004,
       0x2c5e3c:0x24050005,0x2c5e40:0x0c0b1492,
       0x2c5e90:0x0c0b1708,0x2c5d68:0x0c0b15e2,
       0x2c5d90:0x0c0c94b2,0x2c5d94:0x0000282d,
       0x2c5da0:0x0220802d,0x2c5db8:0x82020000,
       0x2c5dc8:0x5040fffb,0x2c5dcc:0x26100001,
       0x2c5dd4:0x0c0bf6c0,0x2c5dd8:0x02c0282d,
       0x2c5de0:0x0c0bf25a,0x2c5de4:0x0200282d}


def verify_elf(elf):
    if hashlib.sha256(elf).hexdigest()!=ORIGINAL_SHA:raise ValueError('ELF revision mismatch')
    for va,expected in WORDS.items():
        if struct.unpack_from('<I',elf,va-DELTA)[0]!=expected:
            raise ValueError(f'Instruction mismatch at {va:08x}')
    return [{'va':f'{va:08x}','file_offset':va-DELTA,'word':f'{word:08x}'} for va,word in WORDS.items()]


def investigate(elf,data):
    instructions=verify_elf(elf);checksum=source_hash(data);index=SsdIndex(data)
    entries=[];tags=Counter();reasons=Counter();potential=0
    for at in sorted(index.records):
        if bytes(data[at:at+4]) not in (b'smnn',b'2snm'):continue
        entry=descriptor(data,at,index);parts=entry['segments']
        if [s['key'] for s in parts]!=['body','choices','label'] or parts[2]['editable']:
            raise ValueError('Named-choice segmentation changed')
        tags[entry['id'].split('.')[1]]+=1;reasons.update(entry['blocked_reasons'])
        has_opaque=any(tokens(bytes.fromhex(s['source_hex']))[1] for s in parts)
        native=any(any(c not in (9,10) and not 32<=c<=126 for c in bytes.fromhex(s['source_hex'])) for s in parts)
        potential+=not has_opaque and not native
        label=parts[2];start=label['offset'];raw=bytes.fromhex(label['source_hex'])
        if bytes(data[start:start+len(raw)])!=raw or data[start+len(raw)]!=0:
            raise ValueError('Label source mismatch')
        entries.append({'id':entry['id'],'offset':at,'record_sha256':entry['record_sha256'],
                        'label_offset':start,'label_sha256':hashlib.sha256(raw).hexdigest(),
                        'label_size':len(raw),'opaque_controls':has_opaque,'native_bytes':native})
    return {'schema':1,'elf_sha256':ORIGINAL_SHA,'map_sha256':checksum,
            'instruction_assertions':instructions,'records':len(entries),'by_tag':dict(tags),
            'blocking_reasons':dict(reasons),'without_other_known_blockers':potential,
            'third_string_role':'display-label argument through UI method 0x2FC968; not a canonical speaker ID',
            'path':'0x2C5C20 walks question and choices; 0x2C5D90 finds choices NUL; 0x2C5DB8 skips zeros; 0x2C5DE0 forwards third string',
            'editing_enabled':False,'repack_enabled':False,'pcsx2_executed':False,
            'next_requirement':'Implement a separate opt-in fixed-slot policy with preserved label and bound metadata; opaque/native controls remain blocked',
            'entries':entries}


def main():
    parser=argparse.ArgumentParser(description='Conferir evidencias de escolhas nomeadas sem editar o jogo')
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();output=args.output.resolve()
    if not any(output.is_relative_to(ROOT/p) for p in ('work','reports')) or output.exists():
        raise ValueError('Use new output under work/ or reports/')
    elf=(ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes()
    with SOURCE.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
        result=investigate(elf,data)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(f"Registros: {result['records']}; sem outros bloqueios conhecidos: {result['without_other_known_blockers']}; edicao continua bloqueada.")


if __name__=='__main__':main()
