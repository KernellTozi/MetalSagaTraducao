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


def normalize_description_transition(old_ui,new_ui,old_recipe,old_patches,new_patches):
    """Overlay a proved fixed-slot→pool migration before the usual delta check.

    No arbitrary patch deletion is authorized: all displaced patches must be
    the unchanged parent's description entries, inside the original pool.
    """
    from description_pool import POLICY,parent_config
    from item_descriptions import POLICY as FIXED,RESOURCE,POOL,SIZE,original
    before=old_ui.get('item_descriptions',{});after=new_ui.get('item_descriptions',{})
    if before.get('policy')!=FIXED or after.get('policy')!=POLICY:return
    if after['fixed_slot_parent']['recipe']!=old_recipe.relative_to(ROOT).as_posix():
        raise ValueError('Description migration parent is not the compared recipe')
    if parent_config(after)!=before:raise ValueError('Description migration parent configuration differs')
    expected={e['id'] for e in before['entries']};found=set();raw=original(RESOURCE)
    overlay=bytearray(raw[POOL:POOL+SIZE])
    for key,p in list(old_patches.items()):
        if p['id'] not in expected:continue
        at=p['offset']
        if p['resource']!=RESOURCE or not POOL<=at<at+len(p['before'])<=POOL+SIZE:
            raise ValueError('Historical description patch outside original pool')
        if p['before']!=raw[at:at+len(p['before'])]:raise ValueError('Historical description source differs')
        overlay[at-POOL:at-POOL+len(p['after'])]=p['after'];found.add(p['id']);del old_patches[key]
    if found!=expected:raise ValueError('Historical description patch missing from migration')
    key=(RESOURCE,POOL);patch=new_patches.get(key)
    if not patch or patch['id']!='spack.item.description.pool' or patch['before']!=raw[POOL:POOL+SIZE]:
        raise ValueError('Migration does not supply the exact original description pool')
    old_patches[key]={**patch,'after':bytes(overlay)}


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


def normalize_item_name_review_transition(old_ui,new_ui,old_recipe,old_patches,new_patches):
    """Normalize bounded name-slot prefixes for the explicit human review only.

    Both builds originate at immutable source. Shorter translations may restore
    bytes beyond their own patch prefix; compare the union of the two prefixes.
    This does not resize the compiled patch or release other item fields.
    """
    if 'item_use_release' in new_ui:
        from item_use_release import validate,PARENT,normalize
        if old_ui!=validate(new_ui)[0] or old_recipe.relative_to(ROOT).as_posix()!=PARENT:
            raise ValueError('Item-use comparator parent differs')
        normalize(old_patches,new_patches)
        return
    if 'final_candidate_review' in new_ui:
        from final_candidate import validate,PARENT
        from category_pool import normalize
        if old_ui!=validate(new_ui)[0] or old_recipe.relative_to(ROOT).as_posix()!=PARENT:
            raise ValueError('Final candidate comparator parent differs')
        normalize(old_patches,new_patches)
        return
    if 'card_terms_review' in new_ui:
        from card_terms_review import validate,PARENT
        if old_ui!=validate(new_ui)[0] or old_recipe.relative_to(ROOT).as_posix()!=PARENT:
            raise ValueError('Card terminology comparator parent differs')
        return
    if 'all_minigames_release' in new_ui:
        from minigames_release import validate,PARENT
        if old_ui!=validate(new_ui)[0] or old_recipe.relative_to(ROOT).as_posix()!=PARENT:
            raise ValueError('All-minigames comparator parent differs')
        return
    if 'screenshot_backlog_release' in new_ui:
        from screenshot_backlog import validate,PARENT
        if old_ui!=validate(new_ui)[0] or old_recipe.relative_to(ROOT).as_posix()!=PARENT:
            raise ValueError('Reported backlog comparator parent differs')
        return
    if 'tank_drinking_release' in new_ui:
        from tank_drinking_gaps import validate,PARENT
        if old_ui!=validate(new_ui)[0] or old_recipe.relative_to(ROOT).as_posix()!=PARENT:
            raise ValueError('Tank/drinking comparator parent differs')
        return
    if 'credit_readability_release' in new_ui:
        from credit_readability import validate,PARENT
        if old_ui!=validate(new_ui)[0] or old_recipe.relative_to(ROOT).as_posix()!=PARENT:
            raise ValueError('Readability comparator parent differs')
        return
    if 'title_menu_release' in new_ui:
        from title_menu_revision import validate,PARENT
        if old_ui!=validate(new_ui)[0] or old_recipe.relative_to(ROOT).as_posix()!=PARENT:
            raise ValueError('Title menu comparator parent differs')
        return
    if 'capture_release' in new_ui:
        from capture_release import validate_interface,PARENT_UI,normalize_prefix
        if old_ui!=validate_interface(new_ui)[0] or old_recipe.relative_to(ROOT).as_posix()!=PARENT_UI:
            raise ValueError('Capture comparator parent differs')
        normalize_prefix(old_patches,new_patches)
        return
    if 'screen_followup_release' in new_ui:
        from screen_followup import validate_interface,PARENT,normalize_statistics
        if old_ui!=validate_interface(new_ui)[0] or old_recipe.relative_to(ROOT).as_posix()!=PARENT:
            raise ValueError('Follow-up comparator parent differs')
        normalize_statistics(old_patches,new_patches)
        return
    if 'observed_menu_release' in new_ui:
        from observed_menu_translation import validate_interface,PARENT
        if old_ui!=validate_interface(new_ui)[0] or old_recipe.relative_to(ROOT).as_posix()!=PARENT:
            raise ValueError('Observed menu comparator parent differs')
        return
    if 'npc_and_choice_release' in new_ui:
        from npc_menu_revision import validate_interface,PARENT
        if old_ui!=validate_interface(new_ui)[0] or old_recipe.relative_to(ROOT).as_posix()!=PARENT:
            raise ValueError('NPC/choice comparator parent differs')
        return
    if 'battle_effect_release' in new_ui:
        from battle_effect_atlas import validate_interface,PARENT
        if old_ui!=validate_interface(new_ui)[0] or old_recipe.relative_to(ROOT).as_posix()!=PARENT:
            raise ValueError('Effect atlas comparator parent differs')
        return
    if 'approved_weapons' in new_ui:
        from approved_weapon_names import validate_interface,PARENT
        if old_ui!=validate_interface(new_ui)[0] or old_recipe.relative_to(ROOT).as_posix()!=PARENT:
            raise ValueError('Approved weapon comparator parent differs')
        return
    if 'exit_wording_revision' in new_ui:
        from exit_wording_revision import validate_interface,PARENT
        if old_ui!=validate_interface(new_ui) or old_recipe.relative_to(ROOT).as_posix()!=PARENT:
            raise ValueError('Exit wording comparator parent differs')
        return
    if 'satcom_gap_release' in new_ui:
        from satcom_observed_gaps import validate_interface,PARENT
        if old_ui!=validate_interface(new_ui)[0] or old_recipe.relative_to(ROOT).as_posix()!=PARENT:
            raise ValueError('Observed gap comparator parent differs')
        return
    if 'battle_atlas_release' in new_ui:
        from battle_menu_atlas import validate_interface,PARENT
        if old_ui!=validate_interface(new_ui)[0] or old_recipe.relative_to(ROOT).as_posix()!=PARENT:
            raise ValueError('Combat atlas comparator parent differs')
        return
    if 'remaining_name_release' in new_ui:
        from remaining_item_name_release import normalize_transition
        return normalize_transition(old_ui,new_ui,old_recipe,old_patches,new_patches)
    if 'large_name_release' in new_ui:
        from large_item_name_release import normalize_transition
        return normalize_transition(old_ui,new_ui,old_recipe,old_patches,new_patches)
    if 'item_accent_fallback' in new_ui:
        from item_accent_fallback import validate_interface, PARENT
        if old_ui != validate_interface(new_ui) or old_recipe.relative_to(ROOT).as_posix() != PARENT:
            raise ValueError('Single-item accent comparison parent differs')
        # This profile keeps the complete old prefix size; no normalization.
        return
    from item_name_user_review import POLICY,load_manifest
    from item_names import CEILING_POLICY,catalog,original,RESOURCE
    before=old_ui.get('item_names',{});after=new_ui.get('item_names',{})
    if before==after:return
    if before.get('policy')==POLICY and after.get('policy')==POLICY and 'pending_resolution' in after:
        from pending_name_resolution import load
        m,_=load(after['pending_resolution'])
    elif before.get('policy')==POLICY and after.get('policy')==POLICY and 'approved_extension' in after:
        from item_name_approved_batch import load
        m,_=load(after['approved_extension'])
    elif before.get('policy')==CEILING_POLICY and after.get('policy')==POLICY:
        m=load_manifest(after['user_review'])
    else:return
    if m['parent_recipe']!=old_recipe.relative_to(ROOT).as_posix():
        raise ValueError('Reviewed item transition parent is not compared recipe')
    raw=original(RESOURCE);rows={r['id']:r for r in catalog(raw)}
    for target in m['approved']:
        row=rows[target['id']];key=(RESOURCE,row['offset'])
        old=old_patches.get(key);new=new_patches.get(key)
        if new is None or new['id']!=row['id']:raise ValueError('Reviewed item target patch missing')
        if old is None:continue
        if old['id']!=row['id']:raise ValueError('Reviewed item parent patch identity differs')
        sizes=[len(p['before']) for p in (old,new)]
        if not all(1<=n<=24 for n in sizes):raise ValueError('Reviewed item prefix escapes name field')
        width=max(sizes);source=raw[row['offset']:row['offset']+width]
        for patches,patch in ((old_patches,old),(new_patches,new)):
            n=len(patch['before'])
            if patch['before']!=source[:n] or len(patch['after'])!=n:
                raise ValueError('Reviewed item prefix source/size differs')
            patches[key]={**patch,'before':source,'after':patch['after']+source[n:]}


def verify(old_folder,new_folder,old_recipe,new_recipe):
    cache={}
    old_ui,old=compile_recipe(old_recipe,cache);new_ui,new=compile_recipe(new_recipe,cache)
    if old_ui['layout_profile']!=new_ui['layout_profile']:
        raise ValueError('This comparator requires an unchanged font/layout profile')
    old_patches={(p.get('resource','DATA/MAP/MAP.MCT'),p['offset']):p for p in old}
    new_patches={(p.get('resource','DATA/MAP/MAP.MCT'),p['offset']):p for p in new}
    if len(old_patches)!=len(old) or len(new_patches)!=len(new):raise ValueError('Duplicate patch')
    normalize_description_transition(old_ui,new_ui,old_recipe,old_patches,new_patches)
    normalize_item_name_review_transition(old_ui,new_ui,old_recipe,old_patches,new_patches)
    dropped=old_patches.keys()-new_patches.keys()
    restorations=new_ui.get('restored_originals',[])
    previous_restorations=set(old_ui.get('restored_originals',[]))
    if (len(restorations)!=len(set(restorations)) or not previous_restorations<=set(restorations)
        or {old_patches[k]['id'] for k in dropped}!=set(restorations)-previous_restorations):
        raise ValueError('Prior patch dropped without exact restoration ledger')
    for key in dropped:
        prior=old_patches[key]
        if key[0]!='SLUS_212.93' or not prior['id'].startswith('elf.ui.'):
            raise ValueError('Only fixed ELF UI strings can be restored')
        new_patches[key]={**prior,'after':prior['before']}

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
