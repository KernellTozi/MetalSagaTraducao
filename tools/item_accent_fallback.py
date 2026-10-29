"""One user-authorized ASCII fallback; no general accent or ceiling release."""
import copy
import json
from dialogue import ROOT, sha
from glyph_spacing import ORIGINAL_SHA
from gfi import encode

POLICY = 'single-item-authorized-ascii-accent-fallback-v001'
PARENT = 'translations/interface-v051.json'
MANIFEST = 'translations/excecao-acento-item460-v001.json'
TARGET = 'Idolo de barro'
STATUS = 'Revisão autorizada do item 460 para Idolo de barro; demais traduções preservadas.'


def load(binding):
    if set(binding) != {'recipe', 'sha256'} or binding['recipe'] != MANIFEST:
        raise ValueError('Unknown single-item accent binding')
    raw = (ROOT/MANIFEST).read_bytes()
    if sha(raw) != binding['sha256']:
        raise ValueError('Single-item accent manifest differs')
    m = json.loads(raw)
    if (m.get('schema'), m.get('policy'), m.get('parent_recipe'), m.get('item_id'),
        m.get('approved_accented'), m.get('translation')) != (1, POLICY, PARENT,
            'item.name.0460', 'Ídolo de barro', TARGET):
        raise ValueError('Unapproved item/accent exception')
    parent_raw = (ROOT/PARENT).read_bytes()
    if sha(parent_raw) != m['parent_sha256']:
        raise ValueError('Single-item accent parent differs')
    return m, json.loads(parent_raw)


def expected_names(binding):
    m, parent = load(binding)
    config = copy.deepcopy(parent['item_names'])
    target = next(e for e in config['entries'] if e['id'] == m['item_id'])
    if target['translation'] != 'Imagem de barro':
        raise ValueError('Single-item previous wording differs')
    target['translation'] = TARGET
    config['accent_fallback'] = binding
    return config


def parent_names(config):
    binding = config['accent_fallback']
    _, parent = load(binding)
    if config != expected_names(binding):
        raise ValueError('Single-item fallback changes unrelated names/configuration')
    return parent['item_names']


def validate_interface(recipe):
    binding = recipe['item_accent_fallback']
    _, parent = load(binding)
    expected = copy.deepcopy(parent)
    expected['item_names'] = expected_names(binding)
    expected.update(item_accent_fallback=binding, iso_name='MetalSaga-ptbr-interface-v052.iso', status=STATUS)
    if recipe != expected:
        raise ValueError('Single-item fallback changes unrelated interface fields')
    return parent


def compile_names(elf, config):
    from item_names import compile_names as compile_parent, original, RESOURCE, catalog, validate_value
    if sha(elf) != ORIGINAL_SHA:
        raise ValueError('Single-item fallback ELF differs')
    m, _ = load(config['accent_fallback'])
    parent = parent_names(config)
    patches, report = compile_parent(elf, parent)
    raw = original(RESOURCE)
    row = catalog(raw)[460]
    if any(row[k] != m[k] for k in ('source_sha256', 'record_sha256')):
        raise ValueError('Single-item fallback source identity differs')
    value = validate_value(row, TARGET, ceiling=16)
    if len(value) != 14 or not value.isascii():
        raise ValueError('Single-item fallback must remain exact 14-byte ASCII')
    from spack_battle import catalog as battle_catalog
    if any(r['kind'] == 'action' and r['source_hex'] == row['source_hex'] for r in battle_catalog(raw)):
        raise ValueError('Unexpected battle counterpart needs explicit review')
    if sum(r['source_hex'] == row['source_hex'] for r in catalog(raw)) != 1:
        raise ValueError('Unexpected duplicate name needs explicit review')
    found = [p for p in patches if p['id'] == row['id']]
    if len(found) != 1:
        raise ValueError('Single-item parent patch missing/duplicated')
    old = found[0]
    if old['after'] != encode('Imagem de barro')+b'\0':
        raise ValueError('Single-item parent bytes differ')
    after = value+bytes(len(old['after'])-len(value))
    if len(after) != len(old['after']) or len(after) > 24:
        raise ValueError('Single-item fallback escapes name prefix')
    patches = [{**p, 'after': after} if p['id'] == row['id'] else p for p in patches]
    report = copy.deepcopy(report)
    next(r for r in report['results'] if r['id'] == row['id'])['target_bytes'] = len(value)
    report['unique_translated_labels'] = len({encode(e['translation']) for e in config['entries']})
    report['accent_fallback'] = {'policy': POLICY, 'id': row['id'], 'translation': TARGET,
        'target_bytes': len(value), 'modified_span_bytes': len(after),
        'offset': row['offset'], 'source_record_sha256': row['record_sha256'],
        'all_other_names_unchanged': True, 'fonts_unchanged': True,
        'only_this_accent_omission_authorized': True}
    return patches, report


def compile_interface(elf, recipe):
    from interface_text import compile_draft
    parent = validate_interface(recipe)
    patches, report = compile_draft(elf, parent)
    names, name_report = compile_names(elf, recipe['item_names'])
    target = next(p for p in names if p['id'] == 'item.name.0460')
    if sum(p['id'] == target['id'] for p in patches) != 1:
        raise ValueError('Single-item interface parent patch differs')
    patches = [target if p['id'] == target['id'] else p for p in patches]
    report = copy.deepcopy(report)
    report['item_names'] = name_report
    report['item_accent_fallback'] = name_report['accent_fallback']
    return patches, report
