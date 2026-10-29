"""Exact six-name release, preserving legacy ceilings and historical recipes."""
import copy,json,re
from dialogue import ROOT,sha
from gfi import encode,decode
from glyph_spacing import ORIGINAL_SHA

POLICY='six-approved-item-names-bounded-release-v001'
PARENT='translations/interface-v052.json'
MANIFEST='translations/nomes-maiores-v001.json'
PROOF='reports/prova-seis-nomes-v007.json'
IDS=(331,372,459,838,841,849)
ACTIONS=(124,884,887,882,895)
STATUS='Seis revisões de nomes aprovadas e cinco ações correspondentes, com prova de limites vinculada.'


def load(binding):
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:raise ValueError('Unknown six-name binding')
    raw=(ROOT/MANIFEST).read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('Six-name manifest differs')
    m=json.loads(raw);parent_raw=(ROOT/PARENT).read_bytes();proof_raw=(ROOT/PROOF).read_bytes()
    if (m.get('schema'),m.get('policy'),m.get('parent_recipe'),m.get('proof'))!=(1,POLICY,PARENT,PROOF):raise ValueError('Unknown six-name profile')
    if sha(parent_raw)!=m['parent_sha256'] or sha(proof_raw)!=m['proof_sha256']:raise ValueError('Six-name parent/proof differs')
    decisions=(ROOT/'translations/revisao-humana-itens-v001.json').read_bytes()
    if sha(decisions)!=m['human_decisions_sha256']:raise ValueError('Approved human names changed')
    wanted={x['id']:x['desired_not_applied'] for x in json.loads(decisions)['blocked']}
    if [r['index'] for r in m['items']]!=list(IDS) or [r['id'] for r in m['actions']]!=[f'battle.action.{i:04d}' for i in ACTIONS]:raise ValueError('Six-name ID set differs')
    if any(r['translation']!=wanted.get(r['id']) for r in m['items']):raise ValueError('Six-name wording differs from human review')
    targets={r['id']:r['translation'] for r in m['items']}
    if any(r['translation']!=targets.get(r['item_id']) for r in m['actions']):raise ValueError('Action/item wording differs')
    p=json.loads(proof_raw);budgets=p['budgets']
    if (p['parent_recipe'],p['parent_sha256'])!=(PARENT,m['parent_sha256']):raise ValueError('Evidence parent mismatch')
    if (p['scene_trees'],p['scene_fields'],p['scene_I_references'],p['inherited_scene_names'],p['item_table_maximum_bytes'])!=(300,839,0,400,18):raise ValueError('Scene/table evidence differs')
    if (budgets['field_count'],budgets['page_count'],budgets['item_byte_bound'],budgets['N0_byte_bound_for_valid_field'])!=(34,35,18,31):raise ValueError('Message budget coverage differs')
    if budgets['maximum_page_content_cells']>99 or budgets['maximum_body_bytes']+1>1024:raise ValueError('Evidence exceeds caller allocations')
    if sha((ROOT/p['new_consumer_dependency_report']).read_bytes())!=p['new_consumer_dependency_sha256']:raise ValueError('Dependency evidence changed')
    if not p['scene_iso_verification']['image']['verified'] or p['scene_iso_verification']['fields_identical']!=839:raise ValueError('Scene ISO readback absent')
    return m,json.loads(parent_raw)


def changed_config(parent,key,changes,binding):
    expected=copy.deepcopy(parent[key])
    for change in changes:
        row=next(e for e in expected['entries'] if e['id']==change['id'])
        if row['translation']!=change['parent_translation']:raise ValueError('Six-name parent wording differs')
        row['translation']=change['translation']
    expected['large_name_release']=binding
    return expected


def parent_names(config):
    binding=config['large_name_release'];m,parent=load(binding)
    if config!=changed_config(parent,'item_names',m['items'],binding):raise ValueError('Unrelated name/config change in six-name profile')
    return parent['item_names']


def validate_interface(recipe):
    binding=recipe['large_name_release'];m,parent=load(binding);expected=copy.deepcopy(parent)
    expected['item_names']=changed_config(parent,'item_names',m['items'],binding)
    expected['spack_battle']=changed_config(parent,'spack_battle',m['actions'],binding)
    expected.update(large_name_release=binding,iso_name='MetalSaga-ptbr-interface-v053.iso',status=STATUS)
    if recipe!=expected:raise ValueError('Unrelated interface change in six-name release')
    return parent


def compile_names(elf,config):
    from item_names import compile_names as base,original,RESOURCE,catalog,protected
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Six-name ELF differs')
    m,_=load(config['large_name_release']);old=parent_names(config)
    patches,report=base(elf,old);raw=original(RESOURCE);rows=catalog(raw);byid={r['id']:r for r in rows}
    out={p['id']:p for p in patches};report=copy.deepcopy(report);results={r['id']:r for r in report['results']}
    for change in m['items']:
        row=byid[change['id']];value=encode(change['translation'])
        if any(row[k]!=change[k] for k in ('index','offset','source_sha256','record_sha256')):raise ValueError('Six-name source identity differs')
        if row['empty'] or row['native'] or protected(row['index']) or not 17<=len(value)<=18:raise ValueError('Six-name field/encoding outside exact profile')
        if decode(value)!=change['translation'] or any(b in value for b in (0,9,10,13,37,124)):raise ValueError('Six-name control/Unicode mismatch')
        if sum(r['source_hex']==row['source_hex'] for r in rows)!=1:raise ValueError('Six-name source alias needs separate approval')
        from translation_policy import validate
        from weapon_terms import validate as weapons
        source=bytes.fromhex(row['source_hex']).decode('ascii')
        if validate(source,change['translation']) or weapons(source,change['translation']) or re.findall(r'\d+',source)!=re.findall(r'\d+',change['translation']):raise ValueError('Six-name terminology/numeric facts differ')
        prior=out[row['id']]
        if prior['after'].split(b'\0')[0]!=encode(change['parent_translation']):raise ValueError('Six-name compiled parent differs')
        span=max(len(prior['before']),len(value)+1);at=row['offset'];before=raw[at:at+span]
        if span>24 or any(raw[at+row['source_bytes']:at+24]):raise ValueError('Six-name field tail is not proved padding')
        out[row['id']]={**prior,'before':before,'after':value+bytes(span-len(value))}
        results[row['id']]['target_bytes']=len(value)
    report.update(policy=POLICY,maximum_target_bytes=18,
        unique_translated_labels=len({encode(e['translation']) for e in config['entries']}),
        large_name_release={'policy':POLICY,'binding':config['large_name_release'],'ids':[r['id'] for r in m['items']],
                            'legacy_global_ceiling_unchanged':True,'valid_existing_name_field_required':True,
                            'runtime_visual_status':'pending_user_verification'})
    return sorted(out.values(),key=lambda p:p['offset']),report


def validate_battle(config,item_config,rows,battle_rows):
    from item_name_user_review import validate_battle_config
    binding=config['large_name_release'];m,parent=load(binding)
    parent_names(item_config)
    if config!=changed_config(parent,'spack_battle',m['actions'],binding):raise ValueError('Unrelated battle changes in six-name release')
    old=validate_battle_config(parent['spack_battle'],parent['item_names'],rows,battle_rows)
    byid={r['id']:r for r in battle_rows}
    for c in m['actions']:
        row=byid[c['id']]
        if row['kind']!='action' or any(row[k]!=c[k] for k in ('offset','source_sha256','record_sha256')):raise ValueError('Action record identity differs')
    return old+[{'id':c['id'],'item_ids':[c['item_id']],'source_sha256':c['source_sha256'],'record_sha256':c['record_sha256']} for c in m['actions']]


def compile_interface(elf,recipe):
    from interface_text import compile_draft
    from spack_battle import compile_battle
    parent=validate_interface(recipe);patches,report=compile_draft(elf,parent)
    names,nreport=compile_names(elf,recipe['item_names'])
    battle,breport=compile_battle(elf,recipe['spack_battle'],recipe['item_names'])
    m,_=load(recipe['large_name_release']);ids={r['id'] for r in m['items']+m['actions']}
    replacements={p['id']:p for p in names+battle if p['id'] in ids}
    if set(replacements)!=ids or sum(p['id'] in ids for p in patches)!=11:raise ValueError('Release parent patch set differs')
    out=[replacements.get(p['id'],p) for p in patches]
    report=copy.deepcopy(report);report['item_names']=nreport;report['spack_battle']=breport
    report['large_name_release']={'policy':POLICY,'names_revised':6,'actions_revised':5,'remaining_reviewed_names':9}
    return out,report


def normalize_transition(old_ui,new_ui,old_recipe,old_patches,new_patches):
    from item_names import original,RESOURCE,catalog
    if old_ui!=validate_interface(new_ui) or old_recipe.relative_to(ROOT).as_posix()!=PARENT:raise ValueError('Six-name comparator parent differs')
    m,_=load(new_ui['large_name_release']);raw=original(RESOURCE);rows={r['id']:r for r in catalog(raw)}
    for c in m['items']:
        row=rows[c['id']];key=(RESOURCE,row['offset']);a,b=old_patches[key],new_patches[key]
        span=max(len(a['before']),len(b['before']))
        if span>24:raise ValueError('Release comparison escapes name field')
        source=raw[row['offset']:row['offset']+span]
        for patches,p in ((old_patches,a),(new_patches,b)):
            n=len(p['before'])
            if p['id']!=c['id'] or p['before']!=source[:n] or len(p['after'])!=n:raise ValueError('Release comparison prefix differs')
            patches[key]={**p,'before':source,'after':p['after']+source[n:]}
