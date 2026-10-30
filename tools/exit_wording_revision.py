"""User-approved wording only; retain the proved v056 slots and metadata."""
import copy,json
from dialogue import ROOT,sha
from gfi import encode

POLICY='user-approved-mundo-aberto-fixed-prefix-v001'
PARENT='translations/interface-v056.json'
TARGET='Mundo aberto'
ELF_ID='elf.ui.00317720'
STATUS='Avisos de saída revisados para Mundo aberto, conforme solicitado pelo usuário.'


def binding():
    return {'policy':POLICY,'parent_recipe':PARENT,
            'parent_sha256':sha((ROOT/PARENT).read_bytes()),'translation':TARGET}


def validate_interface(recipe):
    parent=json.loads((ROOT/PARENT).read_bytes());expected=copy.deepcopy(parent)
    row=next(r for r in expected['entries'] if r['id']==ELF_ID)
    if row['translation']!='Mapa do mundo':raise ValueError('Exit wording parent differs')
    row['translation']=TARGET
    expected.update(exit_wording_revision=binding(),iso_name='MetalSaga-ptbr-interface-v057.iso',status=STATUS)
    if recipe!=expected:raise ValueError('Unrelated change in approved exit wording')
    return parent


def revise(patches):
    value=encode(TARGET)
    if value!=b'Mundo aberto' or len(value)!=12:raise ValueError('Approved wording encoding differs')
    selected=[p for p in patches if p['id']==ELF_ID or p['id'].startswith('map.exit.')]
    if len(selected)!=114 or sum(p['id'].startswith('map.exit.') for p in selected)!=113:
        raise ValueError('Approved wording occurrence set differs')
    selected_ids={p['id'] for p in selected}
    output=[]
    for p in patches:
        if p['id'] not in selected_ids:output.append(p);continue
        size=14 if p['id']==ELF_ID else 13
        resource='SLUS_212.93' if p['id']==ELF_ID else 'DATA/MAP/MAP.MCT'
        if p.get('resource')!=resource or len(p['before'])!=size or p['after']!=b'Mapa do mundo'+bytes(size-13):
            raise ValueError('Approved exit source/span differs')
        # New NUL at +12; original NUL at +13 remains. No byte beyond the
        # original 13-byte prefix is taken from flags or destination metadata.
        output.append({**p,'after':value+bytes(size-len(value))})
    return output


def compile_interface(elf,recipe):
    from interface_text import compile_draft
    parent=validate_interface(recipe);patches,report=compile_draft(elf,parent)
    report=copy.deepcopy(report)
    for row in report['results']:
        if row['id']==ELF_ID:row.update(target_bytes=12,target_sha256=sha(encode(TARGET)))
    report['exit_wording_revision']={'policy':POLICY,'translation':TARGET,'revised_exit_labels':113,
                                    'revised_elf_fallback':1,'new_units':0,'pcsx2_executed':False}
    return revise(patches),report
