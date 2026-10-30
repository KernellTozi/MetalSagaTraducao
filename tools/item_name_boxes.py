"""Read-only caller geometry for the nine remaining approved item names.

Measures requested logical geometry, not GPU clipping or every menu context.
No compiler ceilings, game files or recipes are changed.
"""
import argparse
import json
import struct
from functools import lru_cache
from pathlib import Path

from dialogue import ROOT, sha
from gfi import encode
from glyph_spacing import ORIGINAL_SHA
from interface_text import SOURCE

SCOPE = 'remaining-item-names-requested-boxes-v001'
IDS = (354, 373, 431, 647, 711, 798, 826, 836, 840)
RECIPE = 'translations/interface-v053.json'
DECISIONS = 'translations/revisao-humana-itens-v001.json'
WINDOWS = ((0x1b357c, 0x1b35a4), (0x1b3af8, 0x1b3b6c),
           (0x1d54dc, 0x1d5560), (0x509d8, 0x509f4),
           (0x50040, 0x50054), (0x50c40, 0x50c90))


def instruction(elf, offset, expected):
    word = struct.unpack_from('<I', elf, offset)[0]
    if word != expected:
        raise ValueError(f'Unexpected geometry instruction at {offset:x}')
    return word & 0xffff


def geometry(elf):
    if sha(elf) != ORIGINAL_SHA:
        raise ValueError('Geometry source ELF differs')
    # Exact addiu destination/source, not a search for coincidental constants.
    width = instruction(elf, 0x1b3580, 0x24070110)
    name_x = instruction(elf, 0x1b3b54, 0x26a60026)
    font = instruction(elf, 0x1b3b58, 0x24080016)
    instruction(elf, 0x1b3b64, 0x0c04f46a)  # jal 0x13d1a8
    instruction(elf, 0x1b3588, 0x240800d0)
    price_width = instruction(elf, 0x1d54ec, 0x24070190)
    instruction(elf, 0x1d54f0, 0x0c053f10)  # rectangle wrapper 0x14fc40
    left = instruction(elf, 0x1d550c, 0x24050008)
    right = instruction(elf, 0x1d5504, 0x24080008)
    instruction(elf, 0x1d5508, 0x0c053c10)  # stores margins 0x14f040
    default_size = instruction(elf, 0x509f0, 0x24090016)
    at = 0x341658
    fmt = elf[at:elf.index(0, at)]
    if fmt != b'%%I%02d%-20s  %8d\x82f':
        raise ValueError('Name/price original format differs')
    return {
        'direct_name_panel': {
            'requested_width': width, 'name_x_from_draw_origin': name_x,
            'requested_font_size': font,
            'conditional_remaining_width': width - name_x,
            'same_origin_and_effective_clip_proven': False,
        },
        'name_price_panel': {
            'requested_width': price_width, 'left_margin': left,
            'right_margin': right, 'conditional_inner_width': price_width-left-right,
            'constructor_default_size': default_size,
            'string_minimum_bytes': 20, 'price_minimum_columns': 8,
            'format_offset': at, 'format_sha256': sha(fmt),
            'minimum_is_not_precision_or_truncation': True,
            'actual_render_bounds_proven': False,
        },
        'windows': [{'offset': a, 'size': z-a, 'sha256': sha(elf[a:z])}
                    for a, z in WINDOWS],
    }


def padded_name(text, width=20):
    """Model only the unchanged printf %-20s byte-padding operation."""
    value = encode(text)
    if any(c in value for c in (0, 10, 13, 37, 124)):
        raise ValueError('Name contains control/separator')
    return value + b' ' * max(0, width-len(value))


def investigate(elf):
    g = geometry(elf)
    from glyph_layout import elf_patch
    from layout_probe import execute
    from item_names import original, RESOURCE, catalog as names
    from spack_battle import catalog
    recipe = json.loads((ROOT/RECIPE).read_bytes())
    decisions = json.loads((ROOT/DECISIONS).read_bytes())
    entries = {r['id']: r['translation'] for r in recipe['item_names']['entries']}
    proposed = {r['id']: r['desired_not_applied'] for r in decisions['blocked']}
    raw = original(RESOURCE)
    if sha(raw) != recipe['item_names']['source_sha256']:
        raise ValueError('Name source table differs')
    actions = catalog(raw)
    name_rows = {r['id']: r for r in names(raw)}
    layout = elf_patch(elf)['after']

    @lru_cache(None)
    def advance(char, mode):
        value = encode(char)
        r = execute(elf, layout, value, 22, mode)
        if r['consumed'] != len(value) or not r['callee_saved']:
            raise ValueError('Name metric execution differs')
        return r['metrics'][3]

    rows = []
    for index in IDS:
        item_id = f'item.name.{index:04d}'
        target = proposed[item_id]
        current = entries[item_id]
        encoded = encode(target)
        metrics = [sum(advance(c, mode) for c in target) for mode in (0, 1, 2)]
        # Names and action IDs are tied through their immutable source names.
        source = name_rows[item_id]
        related = [r['id'] for r in actions if r['kind']=='action'
                   and r['source_hex'] == source['source_hex']]
        rows.append({
            'id': item_id, 'current_translation': current,
            'approved_translation': target, 'encoded_bytes': len(encoded),
            'logical_advances_size22_modes012': metrics,
            'conditional_direct_panel_remaining': g['direct_name_panel']['conditional_remaining_width']-max(metrics),
            'name_price_padded_field_bytes': len(padded_name(target)),
            'fits_price_minimum_byte_field': len(encoded) <= 20,
            'battle_actions': related, 'action_ceiling_exceeded': bool(related) and len(encoded)>18,
            'editing_authorized': False,
        })
    return {
        'schema': 1, 'scope': SCOPE, 'recipe': RECIPE,
        'recipe_sha256': sha((ROOT/RECIPE).read_bytes()),
        'human_decisions_sha256': sha((ROOT/DECISIONS).read_bytes()),
        'elf_sha256': sha(elf), 'spack_sha256': sha(raw),
        'geometry': g, 'items': rows,
        'counts': {'remaining_names':len(rows),
                   'conditional_direct_advance_fits':sum(r['conditional_direct_panel_remaining']>=0 for r in rows),
                   'name_price_byte_field_fits':sum(r['fits_price_minimum_byte_field'] for r in rows),
                   'action_ceiling_exceeded_names':sum(r['action_ceiling_exceeded'] for r in rows)},
        'editing_authorized': False, 'originals_modified': False,
        'iso_created': False, 'pcsx2_executed': False,
        'next_evidence': [
            'Resolve effective rectangle implementation and draw origin for the direct-name panel.',
            'Trace inventory/shop list columns and battle action consumers; these two panels do not cover them.',
            'Separately prove 19-byte action names and variable-message budgets before any release.',
        ],
        'limits': 'Original caller instructions and existing metric harness only. Virtual rectangle calls, full printf, GPU drawing, clipping, glyph overhang and every caller are not executed. Requested geometry and byte padding alone do not authorize names or compiler ceilings.',
    }


def run(output):
    output = Path(output).resolve()
    if not output.is_relative_to(ROOT/'work'):
        raise ValueError('Detailed name geometry belongs under work/')
    if output.exists() and json.loads(output.read_bytes()).get('scope') != SCOPE:
        raise ValueError('Refuse unrelated output')
    result = investigate(SOURCE.read_bytes())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Conferir geometria solicitada dos nove nomes pendentes, sem editar o jogo')
    p.add_argument('--output', type=Path, default=ROOT/'work/caixas-nomes-v001.json')
    args = p.parse_args()
    print(json.dumps(run(args.output)['counts']))
