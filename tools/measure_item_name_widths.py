"""Static advance probes for reviewed names; never claims complete UI fitting."""
import argparse,json
from functools import lru_cache
from pathlib import Path
from reinsertion import ROOT
from dialogue import sha
from interface_text import SOURCE
from item_names import catalog,original,RESOURCE
from item_name_user_review import load_manifest
from glyph_layout import elf_patch
from layout_probe import execute
from gfi import encode


def measure(recipe_path):
    recipe_path=Path(recipe_path).resolve()
    if not recipe_path.is_relative_to(ROOT/'translations'):raise ValueError('Width recipe outside translations')
    recipe=json.loads(recipe_path.read_text(encoding='utf-8'))
    if 'approved_extension' in recipe['item_names']:
        from item_name_approved_batch import load
        m,_=load(recipe['item_names']['approved_extension'])
    else:m=load_manifest(recipe['item_names']['user_review'])
    elf=SOURCE.read_bytes();patch=elf_patch(elf)
    rows=[r for r in catalog(original(RESOURCE)) if not r['empty'] and not r['native']]
    @lru_cache(maxsize=None)
    def advance(char,side,mode):
        value=encode(char);r=execute(elf,patch['after'],value,side,mode)
        if r['consumed']!=len(value) or not r['callee_saved']:raise ValueError('Reviewed glyph metric probe differs')
        return r['metrics'][3]
    def width(text,side,mode):return sum(advance(c,side,mode) for c in text)
    profiles=[];results={r['id']:{'id':r['id'],'encoded_bytes':len(encode(r['translation'])),'profiles':[]} for r in m['approved']}
    for side in (22,26):
        for mode in (0,1,2):
            original_widths={r['index']:width(bytes.fromhex(r['source_hex']).decode('ascii'),side,mode) for r in rows}
            maximum=max(original_widths.values());witnesses=[i for i,w in original_widths.items() if w==maximum]
            for r in m['approved']:
                value=width(r['translation'],side,mode)
                results[r['id']]['profiles'].append({'side':side,'mode':mode,'advance':value,'within_original_maximum':value<=maximum})
            profiles.append({'side':side,'mode':mode,'maximum_original_name_advance':maximum,'witness_ids':witnesses})
    warnings=[r['id'] for r in results.values() if any(not p['within_original_maximum'] for p in r['profiles'])]
    return {'schema':1,'recipe':recipe_path.relative_to(ROOT).as_posix(),'recipe_sha256':sha(recipe_path.read_bytes()),
        'elf_sha256':sha(elf),'layout_function_offset':patch['offset'],'layout_function_sha256':sha(patch['after']),
        'original_nonempty_names_compared':len(rows),'reviewed_names_measured':len(results),
        'profiles':profiles,'results':list(results.values()),'names_above_observed_advance_envelope':warnings,
        'unique_glyph_profile_probes':advance.cache_info().currsize,
        'limits':'Bounded layout-v004 instruction harness used by layout-v005, native metrics in immutable ELF. Font size/mode supplied. Sum of advances only; no actual menu box, bearing/clipping, glyph drawing, FPU caller, GPU or PCSX2 verification. Not authorization to enlarge 16-byte ceiling.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description='Medir avanços dos nomes revistos sem executar o jogo')
    p.add_argument('--recipe',type=Path,default=ROOT/'translations/interface-v042.json')
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
    if not any(out.is_relative_to(ROOT/k) for k in ('reports','work')) or out.exists():raise ValueError('Use new metadata output under reports/ or work/')
    r=measure(a.recipe);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'names':r['reviewed_names_measured'],'probes':r['unique_glyph_profile_probes'],'warnings':r['names_above_observed_advance_envelope']},ensure_ascii=False))
