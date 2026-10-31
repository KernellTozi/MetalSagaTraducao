"""Exact human-approved weapon names; no global release of protected items."""
import argparse,copy,json,re,struct
from functools import lru_cache
from pathlib import Path
from dialogue import ROOT,sha
from gfi import encode,decode
from glyph_spacing import ORIGINAL_SHA
from item_names import original,RESOURCE,catalog,execute_record_pointer,execute_name_forwarding
from spack_ui import execute_byte_length

POLICY='human-approved-86-weapon-names-fixed-fields-v001'
PARENT='translations/interface-v057.json'
MANIFEST='translations/armas-aprovadas-v001.json'
DOCUMENT='work/revisao-armas-v001/METAL_SAGA_ARMAS_INSTRUCOES_CODEX.md'
DOCUMENT_SHA='4a622a8682d61f865c797eb4af7c435396aea7e38ba7fc5996f00adcf2ee8dcf'
PROOF='reports/armas-aprovadas-largura-v001.json'
STATUS='86 nomes de armas aprovados e 91 referências de batalha; 89 nomes mantidos.'
TERM_EXCEPTIONS={5:['Termo/nome protegido ausente: Tiger'],
                 59:['Termo/nome protegido ausente: Remote'],
                 247:['Termo/nome protegido ausente: Swatter'],
                 252:['Termo/nome protegido ausente: Drill Gun']}
WEAPON_IDS=frozenset(range(1,100))|{1042}|frozenset(range(191,266))


def checked_value(row,text,exceptions):
    from translation_policy import validate
    from weapon_terms import validate as terms
    source=bytes.fromhex(row['source_hex']).decode('ascii');value=encode(text)
    if (not value or len(value)>16 or value!=value.strip() or decode(value)!=text
        or any(c in value for c in (0,9,10,13,37,124))):
        raise ValueError('Approved weapon encoding/16-byte/control guard differs: '+row['id'])
    if re.findall(r'\d+',source)!=re.findall(r'\d+',text):raise ValueError('Weapon caliber/model changed')
    if validate(source,text)+terms(source,text)!=exceptions:
        raise ValueError('Unapproved weapon terminology override: '+row['id'])
    return value


def load(binding):
    if set(binding)!={'recipe','sha256'} or binding['recipe']!=MANIFEST:raise ValueError('Unknown weapon approval binding')
    raw=(ROOT/MANIFEST).read_bytes()
    if sha(raw)!=binding['sha256']:raise ValueError('Weapon approval manifest differs')
    m=json.loads(raw);parent_raw=(ROOT/PARENT).read_bytes()
    if (m['schema'],m['policy'],m['parent_recipe'],m['parent_sha256'],m['approval_document_sha256'])!=(1,POLICY,PARENT,sha(parent_raw),DOCUMENT_SHA):
        raise ValueError('Weapon parent/approval document differs')
    if m['proof']!=PROOF or sha((ROOT/PROOF).read_bytes())!=m['proof_sha256']:raise ValueError('Weapon geometry proof differs')
    decisions=m['decisions'];ids=[r['index'] for r in decisions]
    if len(ids)!=175 or set(ids)!=WEAPON_IDS or len(set(ids))!=len(ids):raise ValueError('Incomplete weapon approval scope')
    if sum(r['decision']=='ALTERAR' for r in decisions)!=86 or sum(r['decision']=='MANTER' for r in decisions)!=89:
        raise ValueError('Weapon decision counts differ')
    if m['fallback_ids'] or m['conflict_ids']:raise ValueError('This approval profile has no fallback/conflict release')
    return m,json.loads(parent_raw)


def configured(parent,key,entries,binding):
    config=copy.deepcopy(parent[key]);known={r['id'] for r in config['entries']}
    if known&{r['id'] for r in entries}:raise ValueError('Weapon change already present; do not duplicate/rewrite')
    config['entries'].extend(copy.deepcopy(entries));config['weapon_approval']=binding
    return config


def validate_config(config,key):
    m,parent=load(config['weapon_approval'])
    entries=m['items'] if key=='item_names' else m['actions']
    if config!=configured(parent,key,entries,config['weapon_approval']):raise ValueError('Unrelated change in weapon table config')
    return m,parent


def validate_interface(recipe):
    binding=recipe['approved_weapons'];m,parent=load(binding);expected=copy.deepcopy(parent)
    expected['item_names']=configured(parent,'item_names',m['items'],binding)
    expected['spack_battle']=configured(parent,'spack_battle',m['actions'],binding)
    expected.update(approved_weapons=binding,iso_name='MetalSaga-ptbr-interface-v058.iso',status=STATUS)
    if recipe!=expected:raise ValueError('Unrelated root change in weapon approval')
    return parent,m


def compile_names(elf,config):
    from item_names import compile_names as base
    if sha(elf)!=ORIGINAL_SHA:raise ValueError('Weapon ELF revision differs')
    m,parent=validate_config(config,'item_names');patches,report=base(elf,parent['item_names'])
    raw=original(RESOURCE)
    if sha(raw)!=m['spack_sha256']:raise ValueError('Weapon S_PACK revision differs')
    rows={r['id']:r for r in catalog(raw)};prior={p['id']:p['after'].split(b'\0')[0] for p in patches}
    decisions={r['id']:r for r in m['decisions']};extra=[];results=[]
    for row in decisions.values():
        source=rows[row['id']];current=prior.get(row['id'],bytes.fromhex(source['source_hex']))
        if sha(current)!=row['parent_name_sha256'] or any(row[k]!=source[k] for k in ('source_sha256','record_sha256','offset')):
            raise ValueError('Weapon current/source conflict: '+row['id'])
        if struct.unpack_from('<I',raw,source['offset']+28)[0]!=row['category']:raise ValueError('Weapon category changed')
        if row['decision']=='MANTER' and sha(current)!=row['approved_name_sha256']:raise ValueError('Protected weapon current value differs')
    for target in m['items']:
        row=rows[target['id']];decision=decisions[target['id']]
        if decision['decision']!='ALTERAR' or target['group']!='approved-weapons':raise ValueError('Unapproved weapon ID')
        value=checked_value(row,target['translation'],TERM_EXCEPTIONS.get(row['index'],[]))
        if len(value)!=decision['approved_bytes'] or sha(value)!=decision['approved_name_sha256']:
            raise ValueError('Approved weapon bytes/wording changed')
        if any(target[k]!=row[k] for k in ('source_sha256','record_sha256')):raise ValueError('Weapon item identity differs')
        if target['id'] in prior:raise ValueError('Do not replace existing names in this profile')
        if execute_record_pointer(elf,row['index'])!=row['index']*128 or execute_name_forwarding(elf,row['index'])!=(row['index']*128,0x630000):
            raise ValueError('Original weapon pointer forwarding differs')
        if execute_byte_length(elf,value)!=len(value):raise ValueError('Original weapon byte count differs')
        span=max(row['source_bytes'],len(value))+1;at=row['offset'];before=raw[at:at+span]
        if span>24 or before!=bytes.fromhex(row['source_hex'])+bytes(span-row['source_bytes']):raise ValueError('Weapon zero-tail/field bound differs')
        extra.append({'id':row['id'],'resource':RESOURCE,'offset':at,'before':before,'after':value+bytes(span-len(value))})
        results.append({'id':row['id'],'item_id':row['index'],'offset':at,'source_bytes':row['source_bytes'],'target_bytes':len(value),'group':'approved-weapons'})
    if len(extra)!=86:raise ValueError('Expected exactly 86 changed weapon names')
    values=prior|{p['id']:p['after'].split(b'\0')[0] for p in extra};exceptions=[]
    for target in m['items']:
        row=rows[target['id']];aliases=[r for r in rows.values() if r['source_hex']==row['source_hex']]
        distinct={values.get(r['id'],bytes.fromhex(r['source_hex'])) for r in aliases}
        if len(distinct)>1:
            if [r['index'] for r in aliases]!=[55,946] or target['id']!='item.name.0055' or 'item.name.0946' in values:
                raise ValueError('Unreviewed external weapon alias')
            exceptions.append({'translated_item':55,'out_of_scope_item_preserved':946})
    if exceptions!=m['external_alias_exceptions']:raise ValueError('Weapon alias preservation ledger differs')
    report=copy.deepcopy(report);report['accepted']+=86;report['results'].extend(results)
    report['unique_translated_labels']=len({v for v in values.values()})
    report['shared_labels_consistent']=False
    report['approved_weapons']={'policy':POLICY,'changed':86,'already_applied':0,'kept':89,'fallback':0,'conflicts':0,
                                'new_name_ceiling_bytes':16,'global_legacy_protection_unchanged':True,
                                'external_alias_exceptions':exceptions,'visual_validation':'pending_user'}
    return sorted(patches+extra,key=lambda p:p['offset']),report


def compile_battle(elf,config,item_config,*,parent_output=None):
    from spack_battle import catalog as battle_catalog,execute_action,ACTION_STRIDE
    m,parent=validate_config(config,'spack_battle');validate_config(item_config,'item_names')
    # The root parent contains bounded 19-byte action releases. Its standalone
    # legacy battle compiler intentionally retains the 18-byte guard. Recover
    # the already validated parent output instead of relaxing that guard.
    if parent_output is None:
        from interface_text import compile_draft
        parent_output=compile_draft(elf,parent)
    all_patches,ui_report=parent_output;report=ui_report['spack_battle']
    parent_ids={r['id'] for r in report['results']}
    patches=[p for p in all_patches if p['id'] in parent_ids]
    if len(patches)!=len(parent_ids):raise ValueError('Parent battle patches missing')
    raw=original(RESOURCE)
    rows={r['id']:r for r in battle_catalog(raw)};byitem={r['id']:r for r in catalog(raw)}
    targets={bytes.fromhex(byitem[t['id']]['source_hex']):t for t in m['items']};known={p['id'] for p in patches}
    expected={r['id'] for r in rows.values() if r['kind']=='action' and bytes.fromhex(r['source_hex']) in targets}
    if len(expected)!=91 or {r['id'] for r in m['actions']}!=expected:raise ValueError('Weapon action alias set differs')
    extra=[];results=[]
    for target in m['actions']:
        row=rows[target['id']];item=targets[bytes.fromhex(row['source_hex'])]
        if row['id'] in known or target['translation']!=item['translation']:raise ValueError('Weapon action conflict/wording differs')
        if any(target[k]!=row[k] for k in ('source_sha256','record_sha256')):raise ValueError('Weapon action record differs')
        idx=int(item['id'].rsplit('.',1)[1]);value=checked_value(row,target['translation'],TERM_EXCEPTIONS.get(idx,[]))
        if execute_action(elf,row['index'])!=row['index']*ACTION_STRIDE:raise ValueError('Original weapon action pointer differs')
        at=row['offset'];before=raw[at:at+32]
        if any(before[row['source_bytes']:]):raise ValueError('Weapon action name tail differs')
        extra.append({'id':row['id'],'resource':RESOURCE,'offset':at,'before':before,'after':value+bytes(32-len(value))})
        results.append({k:row[k] for k in ('id','kind','index','offset','source_bytes')}|{'target_bytes':len(value)})
    report=copy.deepcopy(report);report['accepted']+=91;report['actions']+=91;report['results'].extend(results)
    report['approved_weapon_counterparts']={'names':86,'action_references':91,'attributes_unchanged':True}
    return patches+extra,report


def compile_interface(elf,recipe):
    from interface_text import compile_draft
    parent,m=validate_interface(recipe);patches,report=compile_draft(elf,parent)
    names,nreport=compile_names(elf,recipe['item_names'])
    battle,breport=compile_battle(elf,recipe['spack_battle'],recipe['item_names'],parent_output=(patches,report))
    old={p['id']:p for p in patches};candidates=names+battle
    for p in candidates:
        if p['id'] in old and p!=old[p['id']]:raise ValueError('Prior item/battle patch changed outside approval')
    extra=[p for p in candidates if p['id'] not in old]
    if len(extra)!=177:raise ValueError('Weapon addition patch count differs')
    report=copy.deepcopy(report);report['accepted']+=177;report['item_names']=nreport;report['spack_battle']=breport
    report['approved_weapons']={**nreport['approved_weapons'],'action_references_changed':91,'pcsx2_executed':False}
    return patches+extra,report


def prepare():
    """Parse the complete approved table, equivalent to the referenced CSV."""
    from interface_text import SOURCE
    from item_names import compile_names as base
    from spack_battle import catalog as battle_catalog
    document=(ROOT/DOCUMENT).read_bytes()
    if sha(document)!=DOCUMENT_SHA:raise ValueError('User approval document changed')
    parent_raw=(ROOT/PARENT).read_bytes();parent=json.loads(parent_raw);elf=SOURCE.read_bytes();raw=original(RESOURCE)
    rows={r['index']:r for r in catalog(raw)}
    current={p['id']:p['after'].split(b'\0')[0] for p in base(elf,parent['item_names'])[0]}
    audit=json.loads((ROOT/'work/revisao-armas-v001/armas-revisao.json').read_bytes())
    audited={r['index']:r for r in audit['rows']};decisions=[];items=[]
    pattern=r'^\| (\d{4}) \| ([^|]+) \| ([^|]+) \| (\d+) \| (ALTERAR|MANTER) \|\s*$'
    for match in re.finditer(pattern,document.decode('utf-8'),re.M):
        index,source,text,estimate,action=match.groups();index=int(index);source=source.strip();text=text.strip();r=rows[index]
        before=bytes.fromhex(r['source_hex']);now=current.get(r['id'],before);value=encode(text)
        if index not in WEAPON_IDS or source!=before.decode('ascii') or audited[index]['source']!=source:
            raise ValueError(f'ID {index}: original differs from approval/audit')
        if len(value)!=int(estimate) or len(value)>16:raise ValueError(f'ID {index}: real encoder disagrees with estimated bytes/ceiling')
        if decode(now) not in (audited[index]['current'],text):raise ValueError(f'ID {index}: conflicting current name')
        if action=='MANTER' and now!=value:raise ValueError(f'ID {index}: protected name changed')
        if action=='ALTERAR':
            checked_value(r,text,TERM_EXCEPTIONS.get(index,[]))
            if now==value:raise ValueError(f'ID {index}: already applied; prepare a distinct no-duplicate revision')
            items.append({k:r[k] for k in ('id','source_sha256','record_sha256')}|{'translation':text,'group':'approved-weapons'})
        decisions.append({k:r[k] for k in ('id','index','offset','source_sha256','record_sha256')}|
                         {'category':struct.unpack_from('<I',raw,r['offset']+28)[0],'decision':action,
                          'approved_bytes':len(value),'approved_name_sha256':sha(value),'parent_name_sha256':sha(now)})
    if len(decisions)!=175 or {r['index'] for r in decisions}!=WEAPON_IDS or len(items)!=86:
        raise ValueError('Expected 175 reviewed weapons, 86 changes and 89 preservations')
    targets={rows[int(t['id'].rsplit('.',1)[1])]['source_hex']:t['translation'] for t in items};actions=[]
    for r in battle_catalog(raw):
        if r['kind']=='action' and r['source_hex'] in targets:
            actions.append({k:r[k] for k in ('id','source_sha256','record_sha256')}|{'translation':targets[r['source_hex']]})
    if len(actions)!=91:raise ValueError('Expected 91 weapon battle aliases')
    from glyph_layout import elf_patch
    from layout_probe import execute
    from item_box_proof import shop
    layout=elf_patch(elf)['after']
    @lru_cache(None)
    def advance(char,mode):
        value=encode(char);r=execute(elf,layout,value,22,mode)
        if r['consumed']!=len(value) or not r['callee_saved']:raise ValueError('Weapon metric probe differs')
        return r['metrics'][3]
    measured=[{'id':t['id'],'advances_size22_modes012':[sum(advance(c,mode) for c in t['translation']) for mode in (0,1,2)]} for t in items]
    maximum=max(max(r['advances_size22_modes012']) for r in measured);geometry=shop(elf)
    if maximum>234 or maximum>geometry['name_budget_before_price']-22:raise ValueError('Weapon label reaches name/price margin')
    prior_proof=(ROOT/'reports/prova-nove-nomes-v002.json').read_bytes()
    proof={'schema':1,'policy':POLICY,'elf_sha256':sha(elf),'items':measured,'maximum_advance':maximum,
           'shop':geometry,'minimum_shop_margin':geometry['name_budget_before_price']-maximum,
           'minimum_direct_panel_margin':234-maximum,'prior_geometry_proof_sha256':sha(prior_proof),
           'limits':'Original metric/geometry windows with synthetic RAM; no GPU, full formatter, game execution or visual approval.'}
    proof_raw=(json.dumps(proof,ensure_ascii=False,indent=2)+'\n').encode();(ROOT/PROOF).write_bytes(proof_raw)
    m={'schema':1,'policy':POLICY,'parent_recipe':PARENT,'parent_sha256':sha(parent_raw),
       'approval_document_sha256':DOCUMENT_SHA,'approval_source_format':'Complete equivalent Markdown table; no CSV supplied',
       'audit_sha256':sha((ROOT/'work/revisao-armas-v001/armas-revisao.json').read_bytes()),'spack_sha256':sha(raw),
       'proof':PROOF,'proof_sha256':sha(proof_raw),'decisions':decisions,'items':items,'actions':actions,
       'external_alias_exceptions':[{'translated_item':55,'out_of_scope_item_preserved':946}],
       'fallback_ids':[],'conflict_ids':[]}
    manifest_raw=(json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode();(ROOT/MANIFEST).write_bytes(manifest_raw)
    b={'recipe':MANIFEST,'sha256':sha(manifest_raw)};child=copy.deepcopy(parent)
    child['item_names']=configured(parent,'item_names',items,b);child['spack_battle']=configured(parent,'spack_battle',actions,b)
    child.update(approved_weapons=b,iso_name='MetalSaga-ptbr-interface-v058.iso',status=STATUS)
    (ROOT/'translations/interface-v058.json').write_bytes((json.dumps(child,ensure_ascii=False,indent=2)+'\n').encode())
    validate_interface(child)
    return {'changed':len(items),'kept':89,'already_applied':0,'action_references':len(actions),'fallback':0,'conflicts':0,'maximum_advance':maximum}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Preparar lote exato de armas aprovado pelo usuário; sem modificar ISO')
    parser.add_argument('--prepare',action='store_true',required=True);parser.parse_args()
    print(json.dumps(prepare(),ensure_ascii=False))
