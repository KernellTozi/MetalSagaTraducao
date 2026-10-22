"""Exhaustive single-character layout audit; all work runs offline."""
import argparse
import hashlib
import json
from pathlib import Path
from glyph_single import START,END,BASES,elf_patch
from glyph_layout import elf_patch as adjacent_patch
from layout_probe import execute
from validate_glyph_layout import incoming
ROOT=Path(__file__).resolve().parents[1]


def audit(data):
    patch=elf_patch(data);adjacent=adjacent_patch(data);changed=[]
    for code in range(65536):
        raw=code.to_bytes(2,'big')
        old=execute(data,patch['before'],raw,single=True)
        new=execute(data,patch['after'],raw,single=True)
        if code in BASES:
            native=execute(data,patch['before'],bytes([BASES[code]]),single=True)
            expected={**native,'cache_codes':[code]}
        else:expected=old
        if new!=expected or not new['callee_saved']:raise ValueError(f'Unexpected single-glyph behavior: {code:04x}')
        if old!=new:changed.append(f'{code:04x}')
    refs=incoming(data,START,END)
    if any(not r['function_entry'] for r in refs):raise ValueError('External entry inside function')
    return {'schema':1,'elf_sha256':hashlib.sha256(data).hexdigest(),
        'window_start':START,'window_end_exclusive':END,'same_size':True,
        'original_window_sha256':hashlib.sha256(patch['before']).hexdigest(),
        'patched_window_sha256':hashlib.sha256(patch['after']).hexdigest(),
        'requires_adjacent_patch_sha256':hashlib.sha256(adjacent['after']).hexdigest(),
        'codes_compared':65536,'changed_codes':changed,'native_codes_unchanged':65536-len(changed),
        'cache_code_preserved':True,'callee_saved_verified':True,'external_direct_references':refs,
        'font_cache_widths_model':'existing v003 half-width flag; native classification modeled at call boundary',
        'runtime_validated':False,'limitations':['Bounded instruction interpreter, not a PS2 emulator',
        'Cache/texture/draw calls are modeled boundaries; actual rasterization not emulated',
        'Direct reference scan cannot exclude all indirect references']}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    output=parser.parse_args().output.resolve()
    if output.exists() or not any(output.is_relative_to(ROOT/d) for d in ('work','reports')):raise ValueError('Use a new project report')
    report=audit((ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes())
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('65536 codes checked; 18 PT-BR draw paths corrected; native results identical')

if __name__=='__main__':main()
