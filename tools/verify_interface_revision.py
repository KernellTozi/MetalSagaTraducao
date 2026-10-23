"""Independent whole-image comparison of two consolidated interface recipes."""
import argparse
import hashlib
import json
import mmap
from pathlib import Path
from reinsertion import ROOT,local
from build_translation_pilot import load_draft,compile_draft,SOURCE as MAP
from interface_text import compile_draft as compile_ui,SOURCE as ELF
from build_dialogue_iso import compare_streams
from disc import entries,SECTOR


def compile_recipe(ui_path,dialogue_cache=None):
    ui=json.loads(ui_path.read_text(encoding='utf-8'))
    draft,_=load_draft(ROOT/ui['base_dialogue_draft'])
    if draft.get('layout_profile')!=ui.get('layout_profile'):
        raise ValueError('Recipe layout mismatch')
    key=hashlib.sha256(json.dumps(draft,sort_keys=True,ensure_ascii=False).encode('utf-8')).hexdigest()
    cache={} if dialogue_cache is None else dialogue_cache
    if key not in cache:
        with MAP.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
            _,patches,report=compile_draft(data,draft)
        if not report['valid']:raise ValueError('Invalid dialogue recipe')
        cache[key]=patches
    patches=cache[key]
    additions,_=compile_ui(ELF.read_bytes(),ui)
    return ui,patches+additions


def verify(old_folder,new_folder,old_recipe,new_recipe):
    cache={}
    old_ui,old=compile_recipe(old_recipe,cache);new_ui,new=compile_recipe(new_recipe,cache)
    if old_ui['layout_profile']!=new_ui['layout_profile']:
        raise ValueError('This comparator requires an unchanged font/layout profile')
    old_patches={(p.get('resource','DATA/MAP/MAP.MCT'),p['offset']):p for p in old}
    new_patches={(p.get('resource','DATA/MAP/MAP.MCT'),p['offset']):p for p in new}
    if len(old_patches)!=len(old) or len(new_patches)!=len(new):raise ValueError('Duplicate patch')
    if old_patches.keys()-new_patches.keys():raise ValueError('Prior patch dropped')
    reports=[json.loads((folder/'relatorio.json').read_text(encoding='utf-8')) for folder in (old_folder,new_folder)]
    if not all(r['valid'] and 'iso' in r for r in reports):raise ValueError('Incomplete build')
    images=[folder/r['iso']['image_name'] for folder,r in zip((old_folder,new_folder),reports)]
    with images[0].open('rb') as stream:directory=entries(stream)
    extents={e['path']:e['lba']*SECTOR for e in directory}
    changes=[]
    for key,p in new_patches.items():
        resource,at=key;prior=old_patches.get(key)
        if prior and prior['before']!=p['before']:raise ValueError('Patch source changed')
        before=prior['after'] if prior else p['before']
        if len(before)!=len(p['after']):raise ValueError('Patch resized')
        if before!=p['after']:
            changes.append({'id':p['id'],'resource':resource,'offset':extents[resource]+at,
                            'before':before,'after':p['after']})
    changes.sort(key=lambda p:p['offset'])
    if any(a['offset']+len(a['before'])>b['offset'] for a,b in zip(changes,changes[1:])):
        raise ValueError('Delta overlaps')
    with images[0].open('rb') as before,images[1].open('rb') as after:
        result=compare_streams(before,after,changes)
        after.seek(0)
        if entries(after)!=directory:raise ValueError('ISO directory changed')
    for key,r in zip(('source_iso_sha256','output_iso_sha256'),reports):
        if result[key]!=r['iso']['output_iso_sha256']:raise ValueError('Build hash mismatch')
    return {'old_recipe':old_recipe.relative_to(ROOT).as_posix(),'new_recipe':new_recipe.relative_to(ROOT).as_posix(),
            'source_iso_sha256':result['source_iso_sha256'],'output_iso_sha256':result['output_iso_sha256'],
            'iso_size':result['iso_size'],'changed_bytes':len(result['changed_iso_offsets']),
            'all_bytes_match_expected_delta':True,'directory_unchanged':True,'font_and_layout_profile_unchanged':True,
            'changed_patches':[{'id':p['id'],'resource':p['resource'],'iso_offset':p['offset'],'size':len(p['after'])} for p in changes],
            'pcsx2_executed':False}


def main():
    p=argparse.ArgumentParser(description='Conferir delta integral entre duas interfaces com o mesmo perfil de fonte')
    for name in ('old-build','new-build','old-recipe','new-recipe','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();output=a.output.resolve()
    if not output.is_relative_to(ROOT/'reports') or output.exists():raise ValueError('Use a new metadata report under reports/')
    old_recipe=a.old_recipe.resolve();new_recipe=a.new_recipe.resolve()
    if not all(p.is_relative_to(ROOT/'translations') for p in (old_recipe,new_recipe)):
        raise ValueError('Recipes must be under translations/')
    result=verify(local(a.old_build),local(a.new_build),old_recipe,new_recipe)
    with output.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(f"Delta integral conferido: {result['changed_bytes']} bytes em {len(result['changed_patches'])} patches")


if __name__=='__main__':main()
