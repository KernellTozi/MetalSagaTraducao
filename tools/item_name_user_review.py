"""Bound explicit human revisions; legacy names/terminology remain strict."""
import copy,json
from pathlib import Path
from reinsertion import ROOT
from dialogue import sha

POLICY='spack-user-reviewed-item-names-observed-ceiling-v003'
MANIFEST_POLICY='item-user-review-exact-records-v001'
REMOTE={360:('Remote Grenade','Granada Remota'),874:('Remote Laser','Laser remoto'),
        875:('Remote Laser EX','Laser remoto EX')}
SCRAP={822:'Sucata leve',823:'Sucata média',824:'Sucata pesada'}
UNIFORM={142:'Traje de criada',780:'Roupa empregada'}
BATTLE_POLICY='spack-user-reviewed-item-action-labels-fixed-fields-v002'
REMOTE_ACTION={112:REMOTE[360],134:REMOTE[874],135:REMOTE[875]}


def remote_exception(row,text):
    expected=REMOTE.get(row['index'])
    return expected is not None and (bytes.fromhex(row['source_hex']).decode('ascii'),text)==expected


def load_manifest(binding):
    if set(binding)!={'recipe','sha256'}:raise ValueError('Unknown human-review binding fields')
    path=(ROOT/binding['recipe']).resolve()
    if not path.is_relative_to(ROOT/'translations'):raise ValueError('Human item review outside translations')
    raw=path.read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('Human item review hash differs')
    manifest=json.loads(raw)
    if manifest.get('policy')!=MANIFEST_POLICY or manifest.get('schema')!=1:
        raise ValueError('Unknown human item review manifest')
    return manifest


def prepare_config(parent,manifest,rows,binding):
    from item_names import CEILING_POLICY
    from gfi import encode
    if parent['item_names']['policy']!=CEILING_POLICY:raise ValueError('Human review requires its exact v002 name parent')
    byid={r['id']:r for r in rows};expected=copy.deepcopy(parent['item_names'])
    entries={r['id']:r for r in expected['entries']};pending={r['id']:r for r in parent['item_name_review']['pending']}
    approved=manifest['approved'];ids=[r['id'] for r in approved]
    if len(ids)!=72 or len(set(ids))!=72:raise ValueError('Human review must contain 72 unique authorized IDs')
    for target in approved:
        row=byid[target['id']]
        if (target['source_sha256']!=row['source_sha256'] or target['record_sha256']!=row['record_sha256']):
            raise ValueError('Human review item identity differs')
        old=entries.get(row['id']);editorial=old['translation'] if old else pending.get(row['id'],{}).get('proposed')
        if editorial!=target['audited_translation']:raise ValueError('Human review conflicts with its audited parent')
        effective=encode(old['translation']) if old else bytes.fromhex(row['source_hex'])
        if sha(effective)!=target['parent_effective_name_sha256']:raise ValueError('Human review old name fingerprint differs')
        if old:old['translation']=target['translation']
        else:
            if row['index'] not in (332,378,383) or row['id'] not in pending:
                raise ValueError('Unreviewed pending item promotion')
            entry={'id':row['id'],'source_sha256':row['source_sha256'],'record_sha256':row['record_sha256'],
                'translation':target['translation'],'group':'consumables-materials'}
            expected['entries'].append(entry);entries[row['id']]=entry
    expected['policy']=POLICY;expected['user_review']=binding
    return expected


def validate_config(config,rows):
    if 'remaining_name_release' in config:
        from remaining_item_name_release import parent_names
        return validate_config(parent_names(config),rows)
    if 'large_name_release' in config:
        from large_item_name_release import parent_names
        return validate_config(parent_names(config),rows)
    if 'accent_fallback' in config:
        from item_accent_fallback import parent_names
        return validate_config(parent_names(config),rows)
    if 'pending_resolution' in config:
        from pending_name_resolution import validate_names
        return validate_config(validate_names(config,rows),rows)
    if 'approved_extension' in config:
        from item_name_approved_batch import validate
        return validate_config(validate(config,rows),rows)
    binding=config.get('user_review',{});m=load_manifest(binding)
    parent_path=(ROOT/m['parent_recipe']).resolve()
    if not parent_path.is_relative_to(ROOT/'translations'):raise ValueError('Human review parent outside translations')
    raw=parent_path.read_bytes()
    if sha(raw)!=m['parent_recipe_sha256']:raise ValueError('Human review parent recipe changed')
    parent=json.loads(raw)
    if prepare_config(parent,m,rows,binding)!=config:raise ValueError('Non-authorized item name/config change in reviewed batch')
    if (m.get('remote_term_exception_ids')!=list(REMOTE) or m.get('record_specific_scrap_ids')!=list(SCRAP)
        or m.get('record_specific_uniform_ids')!=list(UNIFORM)):
        raise ValueError('Human review exception scope differs')
    return m


def alias_allowed(source,group,values):
    # Only the two explicit independent-record groups may diverge. The old
    # uniform at 142 stays unchanged; the three scrap names are human-authored.
    targets={b'Scrap Metal':SCRAP,b'Maid Uniform':UNIFORM}.get(source)
    if targets is None or [r['index'] for r in group]!=list(targets):return False
    from gfi import encode
    return all(values.get(r['id'])==encode(targets[r['index']]) for r in group)


def battle_config(parent,m,rows,battle_rows,binding):
    """Synchronize only existing battle labels for the explicitly renamed items."""
    from spack_battle import POLICY as BASE_POLICY
    if parent['spack_battle']['policy']!=BASE_POLICY:raise ValueError('Human action review parent policy differs')
    byid={r['id']:r for r in rows};sources={}
    for target in m['approved']:
        source=byid[target['id']]['source_hex']
        sources.setdefault(source,[]).append(target)
    battle={r['id']:r for r in battle_rows};expected=copy.deepcopy(parent['spack_battle']);changed=[]
    for target in expected['entries']:
        row=battle[target['id']]
        matches=sources.get(row['source_hex'],[])
        if row['kind']!='action' or not matches:continue
        names={m['translation'] for m in matches}
        if len(names)!=1:raise ValueError('Ambiguous reviewed item wording for battle counterpart')
        name=next(iter(names))
        if target['translation']==name:continue
        if target['translation'] not in {m['audited_translation'] for m in matches}:
            raise ValueError('Battle counterpart wording differs from audited parent')
        target['translation']=name
        changed.append({'id':row['id'],'item_ids':[m['id'] for m in matches],
            'source_sha256':row['source_sha256'],'record_sha256':row['record_sha256']})
    if len(changed)!=30:raise ValueError('Expected exactly 30 existing battle counterparts')
    expected['policy']=BATTLE_POLICY;expected['item_review']=binding
    return expected,changed


def validate_battle_config(config,item_config,rows,battle_rows):
    if 'remaining_name_release' in config:
        from remaining_item_name_release import validate_battle
        return validate_battle(config,item_config,rows,battle_rows)
    if 'large_name_release' in config:
        from large_item_name_release import validate_battle
        return validate_battle(config,item_config,rows,battle_rows)
    m=validate_config(item_config,rows)
    if config.get('item_review')!=item_config.get('user_review'):raise ValueError('Battle/item human review mismatch')
    parent=json.loads((ROOT/m['parent_recipe']).read_text(encoding='utf-8'))
    expected,changed=battle_config(parent,m,rows,battle_rows,item_config['user_review'])
    if expected!=config:raise ValueError('Non-authorized battle label change in human review')
    return changed


def remote_action_exception(row,text):
    return (row['kind']=='action' and row['index'] in REMOTE_ACTION
        and (bytes.fromhex(row['source_hex']).decode('ascii'),text)==REMOTE_ACTION[row['index']])
