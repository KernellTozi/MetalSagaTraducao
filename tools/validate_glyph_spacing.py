"""Reproducible, offline instruction-window differential audit on the real ELF."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from glyph_spacing import elf_patch,execute_window,PAIRS,START,END,DELTA

ROOT=Path(__file__).resolve().parents[1]


def native_class(code):
    if code<256:
        if code<0x20:return 0
        if code<=0x7f:return 1
        if 0xa0<=code<=0xdf:return 2
        if 0xf0<=code<=0xf9:return -2
        return -1
    if 0xf000<=code<0xfa00:return -2
    if 0x876f<=code<0x889f:return -3
    return -1


def audit():
    data=(ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes()
    patch=elf_patch(data);changed=[]
    for code in range(65536):
        kind=native_class(code)
        old=execute_window(patch['before'],code,kind)
        new=execute_window(patch['after'],code,kind)
        expected={**old,'flags':old['flags']|1} if code in PAIRS else old
        if new!=expected:raise ValueError(f'Unexpected behavior at {code:04x}')
        if old!=new:changed.append(code)
    if set(changed)!=PAIRS:raise ValueError('Pair set differs from project codec')
    # Static direct incoming control flow: none may land inside rewritten code.
    # Scan only the two allocated executable sections, not raw data/debug bytes.
    header=struct.unpack_from('<16sHHIIIIIHHHHHH',data)
    incoming=[]
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
                incoming.append({'offset':off,'destination':dest})
    if incoming:raise ValueError('External direct entry into replaced dispatch')
    # The replaced dispatch used the six-entry jump table; it is left intact,
    # but this function no longer branches through it. Other indirect control
    # flow cannot be ruled out with a direct-branch scan alone.
    return {'schema':1,'elf_sha256':hashlib.sha256(data).hexdigest(),
            'window_start':START,'window_end_exclusive':END,
            'original_window_sha256':hashlib.sha256(patch['before']).hexdigest(),
            'replacement_window_sha256':hashlib.sha256(patch['after']).hexdigest(),
            'codes_compared':65536,'changed_codes':[f'{v:04x}' for v in changed],
            'native_codes_unchanged':65536-len(changed),
            'lookup_arguments_identical':True,'other_cache_bits_identical':True,
            'external_direct_entries':incoming,'runtime_validated':False,
            'limitations':['Instruction-window interpreter with stubbed glyph lookup, not a PS2 emulator',
                           'Existing indirect jump-table entries remain; direct scan is not proof against all indirect references',
                           'No claim about all higher-level line measuring, dynamic controls or fonts'],
            'reproduce':'python tools/validate_glyph_spacing.py --output NEW_PROJECT_REPORT.json'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    output=parser.parse_args().output.resolve()
    if not any(output.is_relative_to(ROOT/d) for d in ('reports','work')) or output.exists():
        raise ValueError('Use a new report under reports/ or work/')
    report=audit();output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    print(f'Compared 65536 codes; only {len(report["changed_codes"])} PT-BR pairs changed')


if __name__=='__main__':main()
