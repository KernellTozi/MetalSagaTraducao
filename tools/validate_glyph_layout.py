"""Offline differential validation of native and PT-BR dialogue layout."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from glyph_layout import START,END,DELTA,BASES,elf_patch
from layout_probe import execute
ROOT=Path(__file__).resolve().parents[1]


def incoming(data):
    header=struct.unpack_from('<16sHHIIIIIHHHHHH',data);entries=[]
    for i in range(header[12]):
        sec=struct.unpack_from('<10I',data,header[6]+i*header[11])
        if sec[1]!=1 or sec[2]&6!=6:continue
        for off in range(sec[4],sec[4]+sec[5]-3,4):
            w=struct.unpack_from('<I',data,off)[0];op=w>>26;dest=None
            if op in (2,3):dest=(w&0x3ffffff)<<2
            elif op in (1,4,5,6,7,20,21,22,23):
                n=w&65535;n=n if n<32768 else n-65536
                dest=off+DELTA+4+n*4
            if dest is not None and START+DELTA<=dest<END+DELTA and not START<=off<END:
                entries.append({'offset':off,'destination':dest,'function_entry':dest==START+DELTA})
    return entries


def audit(data):
    patch=elf_patch(data);changed=[]
    for code in range(65536):
        raw=code.to_bytes(2,'big')
        old=execute(data,patch['before'],raw)
        new=execute(data,patch['after'],raw)
        if code in BASES:
            base=execute(data,patch['before'],bytes([BASES[code]]))
            expected={**base,'code':code,'consumed':2}
        else:expected=old
        if new!=expected:raise ValueError(f'Unexpected layout at {code:04x}: {new} != {expected}')
        if not new['callee_saved']:raise ValueError('ABI state changed')
        if old!=new:changed.append(f'{code:04x}')
    refs=incoming(data)
    if any(not r['function_entry'] for r in refs):raise ValueError('External entry inside function')
    return {'schema':1,'elf_sha256':hashlib.sha256(data).hexdigest(),
            'window_start':START,'window_end_exclusive':END,'same_size':True,
            'original_window_sha256':hashlib.sha256(patch['before']).hexdigest(),
            'replacement_window_sha256':hashlib.sha256(patch['after']).hexdigest(),
            'input_sequences_compared':65536,'changed_sequences':changed,
            'native_sequences_unchanged':65536-len(changed),'callee_saved_verified':True,
            'external_direct_references':refs,'runtime_validated':False,
            'mapping':[{'code':f'{k:04x}','ascii_base':chr(v)} for k,v in BASES.items()],
            'limitations':['Bounded interpreter, not a PS2 emulator','Classifier and soft-float helper calls are modeled ABI boundaries',
                          'Direct-reference scan does not exclude every indirect reference','Visual rendering and other text contexts still require PCSX2 validation']}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    output=parser.parse_args().output.resolve()
    if output.exists() or not any(output.is_relative_to(ROOT/d) for d in ('work','reports')):raise ValueError('Use a new report in work/ or reports/')
    report=audit((ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes())
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f"Compared 65536 sequences; {len(report['changed_sequences'])} PT-BR codes changed")

if __name__=='__main__':main()
