"""Exact nine-name release, preserving legacy ceilings and historical recipes."""
import copy,json,re
from dialogue import ROOT,sha
from gfi import encode,decode
from glyph_spacing import ORIGINAL_SHA

POLICY='nine-approved-item-names-bounded-release-v002'
PARENT='translations/interface-v053.json'
MANIFEST='translations/nomes-restantes-v002.json'
PROOF='reports/prova-nove-nomes-v002.json'
IDS=(354,373,431,647,711,798,826,836,840)
ACTIONS=(106,881,886)
STATUS='Nove revisões restantes e três ações correspondentes; limites vinculados, conferência visual pendente.'


def load(binding):
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:raise ValueError('Unknown nine-name binding')
    raw=(ROOT/MANIFEST).read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('Nine-name manifest differs')
    m=json.loads(raw);parent_raw=(ROOT/PARENT).read_bytes();proof_raw=(ROOT/PROOF).read_bytes()
    if (m.get('schema'),m.get('policy'),m.get('parent_recipe'),m.get('proof'))!=(1,POLICY,PARENT,PROOF):raise ValueError('Unknown nine-name profile')
    if sha(parent_raw)!=m['parent_sha256'] or sha(proof_raw)!=m['proof_sha256']:raise ValueError('Nine-name parent/proof differs')
    decisions=(ROOT/'translations/revisao-humana-itens-v001.json').read_bytes()
    if sha(decisions)!=m['human_decisions_sha256']:raise ValueError('Approved human names changed')
    wanted={x['id']:x['desired_not_applied'] for x in json.loads(decisions)['blocked']}
    if [r['index'] for r in m['items']]!=list(IDS) or [r['id'] for r in m['actions']]!=[f'battle.action.{i:04d}' for i in ACTIONS]:raise ValueError('Nine-name ID set differs')
    if any(r['translation']!=wanted.get(r['id']) for r in m['items']):raise ValueError('Nine-name wording differs from human review')
    targets={r['id']:r['translation'] for r in m['items']}
    if any(r['translation']!=targets.get(r['item_id']) for r in m['actions']):raise ValueError('Action/item wording differs')
    p=json.loads(proof_raw);budgets=p['budgets']
    if (p['parent_recipe'],p['parent_sha256'])!=(PARENT,m['parent_sha256']):raise ValueError('Evidence parent mismatch')
    if p['scope']!='nine-approved-item-names-ui-evidence-v002' or p['elf_sha256']!=ORIGINAL_SHA:raise ValueError('UI evidence source differs')
    if [int(r['id'].rsplit('.',1)[1]) for r in p['items']]!=list(IDS):raise ValueError('UI evidence item scope differs')
    if (p['shop']['logical_row_width'],p['shop']['name_budget_before_price'])!=(374,242):raise ValueError('Shop geometry differs')
    if any(r['shop_name_margin_before_price']<22 for r in p['items']):raise ValueError('Shop price margin absent')
    if len(p['panel_cases'])!=4 or p['panel_cases'][0]['requested_and_returned']!=[80,144,272,208]:raise ValueError('Panel roundtrip absent')
    if (budgets['field_count'],budgets['page_count'],budgets['item_byte_bound'],budgets['N0_byte_bound_for_valid_field'])!=(34,35,19,31):raise ValueError('Message budget coverage differs')
    if budgets['maximum_page_content_cells']>99 or budgets['maximum_body_bytes']+1>1024:raise ValueError('Evidence exceeds allocations')
    if sha((ROOT/p['legacy_scene_dependency_proof']).read_bytes())!=p['legacy_scene_dependency_sha256']:raise ValueError('Prior dependencies changed')
    return m,json.loads(parent_raw)


def changed_config(parent,key,changes,binding):
    expected=copy.deepcopy(parent[key])
    for change in changes:
        row=next(e for e in expected['entries'] if e['id']==change['id'])
        if row['translation']!=change['parent_translation']:raise ValueError('Nine-name parent wording differs')
        row['translation']=change['translation']
    expected['remaining_name_release']=binding
    return expected


def parent_names(config):
    binding=config['remaining_name_release'];m,parent=load(binding)
    if config!=changed_config(parent,'item_names',m['items'],binding):raise ValueError('Unrelated name/config change in nine-name profile')
    return parent['item_names']


def validate_interface(recipe):
    binding=recipe['remaining_name_release'];m,parent=load(binding);expected=copy.deepcopy(parent)
    expected['item_names']=changed_config(parent,'item_names',m['items'],binding)
    expected['spack_battle']=changed_config(parent,'spack_battle',m['actions'],binding)
    expected.update(remaining_name_release=binding,iso_name='MetalSaga-ptbr-interface-v054.iso',status=STATUS)
    if recipe!=expected:raise ValueError('Unrelated interface change in nine-name release')
    return parent


def compile_names(elf,config):
    from item_names import compile_names as base,original,RESOURCE,catalog,protected
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Nine-name ELF differs')
    m,_=load(config['remaining_name_release']);old=parent_names(config)
    patches,report=base(elf,old);raw=original(RESOURCE);rows=catalog(raw);byid={r['id']:r for r in rows}
    out={p['id']:p for p in patches};report=copy.deepcopy(report);results={r['id']:r for r in report['results']}
    for change in m['items']:
        row=byid[change['id']];value=encode(change['translation'])
        if any(row[k]!=change[k] for k in ('index','offset','source_sha256','record_sha256')):raise ValueError('Nine-name source identity differs')
        if row['empty'] or row['native'] or protected(row['index']) or not 17<=len(value)<=19:raise ValueError('Nine-name field/encoding outside exact profile')
        if decode(value)!=change['translation'] or any(b in value for b in (0,9,10,13,37,124)):raise ValueError('Nine-name control/Unicode mismatch')
        aliases=[r['index'] for r in rows if r['source_hex']==row['source_hex']]
        if aliases!=change['source_alias_indices'] or any(i not in IDS for i in aliases):raise ValueError('Unreviewed name alias')
        from translation_policy import validate
        from weapon_terms import validate as weapons
        source=bytes.fromhex(row['source_hex']).decode('ascii')
        if validate(source,change['translation']) or weapons(source,change['translation']) or re.findall(r'\d+',source)!=re.findall(r'\d+',change['translation']):raise ValueError('Nine-name terminology/numeric facts differ')
        prior=out[row['id']]
        if prior['after'].split(b'\0')[0]!=encode(change['parent_translation']):raise ValueError('Nine-name compiled parent differs')
        span=max(len(prior['before']),len(value)+1);at=row['offset'];before=raw[at:at+span]
        if span>24 or any(raw[at+row['source_bytes']:at+24]):raise ValueError('Nine-name field tail is not proved padding')
        out[row['id']]={**prior,'before':before,'after':value+bytes(span-len(value))}
        results[row['id']]['target_bytes']=len(value)
    report.update(policy=POLICY,maximum_target_bytes=19,
        unique_translated_labels=len({encode(e['translation']) for e in config['entries']}),
        remaining_name_release={'policy':POLICY,'binding':config['remaining_name_release'],'ids':[r['id'] for r in m['items']],
                            'legacy_global_ceiling_unchanged':True,'valid_existing_name_field_required':True,
                            'runtime_visual_status':'pending_user_verification'})
    return sorted(out.values(),key=lambda p:p['offset']),report


def validate_battle(config,item_config,rows,battle_rows):
    from item_name_user_review import validate_battle_config
    binding=config['remaining_name_release'];m,parent=load(binding)
    parent_names(item_config)
    if config!=changed_config(parent,'spack_battle',m['actions'],binding):raise ValueError('Unrelated battle changes in nine-name release')
    old=validate_battle_config(parent['spack_battle'],parent['item_names'],rows,battle_rows)
    byid={r['id']:r for r in battle_rows}
    for c in m['actions']:
        row=byid[c['id']]
        if row['kind']!='action' or any(row[k]!=c[k] for k in ('offset','source_sha256','record_sha256')):raise ValueError('Action record identity differs')
    return old+[{'id':c['id'],'item_ids':[c['item_id']],'source_sha256':c['source_sha256'],'record_sha256':c['record_sha256']} for c in m['actions']]


def compile_interface(elf,recipe):
    from interface_text import compile_draft
    from item_names import original,RESOURCE
    from spack_battle import catalog as battle_catalog
    parent=validate_interface(recipe);patches,report=compile_draft(elf,parent)
    names,nreport=compile_names(elf,recipe['item_names'])
    m,_=load(recipe['remaining_name_release'])
    raw=original(RESOURCE);rows={r['id']:r for r in battle_catalog(raw)}
    prior={p['id']:p for p in patches};replacements={p['id']:p for p in names if p['id'] in {r['id'] for r in m['items']}}
    for c in m['actions']:
        row=rows[c['id']];p=prior[c['id']];value=encode(c['translation'])
        if row['kind']!='action' or row['field_bytes']!=32 or row['native'] or row['empty']:raise ValueError('Action field mismatch')
        if any(row[k]!=c[k] for k in ('offset','source_sha256','record_sha256')):raise ValueError('Action source differs')
        if not 18<=len(value)<=19 or decode(value)!=c['translation'] or any(b in value for b in (0,9,10,13,37,124)):raise ValueError('Action encoding/control mismatch')
        if p['after'].split(b'\0')[0]!=encode(c['parent_translation']):raise ValueError('Compiled action parent differs')
        source=bytes.fromhex(row['source_hex']).decode('ascii')
        from translation_policy import validate
        from weapon_terms import validate as weapons
        if validate(source,c['translation']) or weapons(source,c['translation']) or re.findall(r'\d+',source)!=re.findall(r'\d+',c['translation']):raise ValueError('Action terminology differs')
        at=row['offset'];before=raw[at:at+32]
        if p['before']!=before or any(before[row['source_bytes']:]):raise ValueError('Action original padding differs')
        replacements[c['id']]={**p,'after':value+bytes(32-len(value))}
    ids={r['id'] for r in m['items']+m['actions']}
    if set(replacements)!=ids or sum(p['id'] in ids for p in patches)!=12:raise ValueError('Exact release patch set differs')
    report=copy.deepcopy(report);report['item_names']=nreport
    for result in report['spack_battle']['results']:
        if result['id'] in replacements:result['target_bytes']=len(replacements[result['id']]['after'].split(b'\0')[0])
    report['remaining_name_release']={'policy':POLICY,'names_revised':9,'actions_revised':3,'remaining_reviewed_names':0,'visual_validation':'pending_user'}
    return [replacements.get(p['id'],p) for p in patches],report


def normalize_transition(old_ui,new_ui,old_recipe,old_patches,new_patches):
    from item_names import original,RESOURCE,catalog
    if old_ui!=validate_interface(new_ui) or old_recipe.relative_to(ROOT).as_posix()!=PARENT:raise ValueError('Nine-name comparator parent differs')
    m,_=load(new_ui['remaining_name_release']);raw=original(RESOURCE);rows={r['id']:r for r in catalog(raw)}
    for c in m['items']:
        row=rows[c['id']];key=(RESOURCE,row['offset']);a,b=old_patches[key],new_patches[key]
        span=max(len(a['before']),len(b['before']))
        if span>24:raise ValueError('Release comparison escapes name field')
        source=raw[row['offset']:row['offset']+span]
        for patches,p in ((old_patches,a),(new_patches,b)):
            n=len(p['before'])
            if p['id']!=c['id'] or p['before']!=source[:n] or len(p['after'])!=n:raise ValueError('Release comparison prefix differs')
            patches[key]={**p,'before':source,'after':p['after']+source[n:]}
