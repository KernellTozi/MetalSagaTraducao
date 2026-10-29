"""Read-only original glyph-stream execution and bounded caller provenance.

No production compiler is changed. Classification and glyph registration are
modeled; the original emitter and its jump tables execute instruction by
instruction. Plain project text, newlines and %I references are accepted;
the literal N0 lookup is a separate explicit probe option.
"""
import argparse
import json
import mmap
import re
import struct
from pathlib import Path

from dialogue import ROOT, sha
from glyph_spacing import ORIGINAL_SHA
from interface_text import SOURCE, sections
from item_names import ITEM_COUNT, STRIDE, RESOURCE, original
from item_name_buffers import name_table, RECIPE
from control_b15 import execute_argument
from gfi import encode
from control_variable_refs import SELECTORS

SCOPE = 'item-name-stream-and-inputs-read-only-v003'
START, END = 0x1b5b20, 0x1b5f94
WINDOWS = ((0x1fa0c8, 0x1fa0ec), (0x1fa73c, 0x1fa758),
           (0x1face0, 0x1fad88), (0x54960, 0x549f0),
           (0x472c4, 0x473d0), (0x1fcec0, 0x1fd05c),
           (0x1fd274, 0x1fd2c4), (START, END),
           (0x33dd40, 0x33de30), (0x1c6310, 0x1c6370),
           (0x1c648c, 0x1c6500), (0x1c69cc, 0x1c6a44),
           (0x1c6cac, 0x1c6d24), (0x1fe978, 0x1fea00))


def direct_calls(elf, target):
    t = sections(elf)['.text']
    word = 0x0c000000 | ((target + 0xff000) >> 2)
    return [at for at in range(t['offset'], t['offset'] + t['size'], 4)
            if struct.unpack_from('<I', elf, at)[0] == word]


def input_evidence(elf, recipe):
    if sha(elf) != ORIGINAL_SHA:
        raise ValueError('Input provenance ELF differs')
    expected_calls = {0x54960: [0x1fad80], 0x1face0: [0x1fa0e4, 0x1fa750],
                      0x47220: [0x460a0], START: [0x1fd2bc],
                      0x1fcec0: [0x1fe9f8],
                      0x1fe978: [0x1c6334, 0x1c6368, 0x1c64c0, 0x1c64f8,
                                  0x1c6a00, 0x1c6a3c, 0x1c6ce0, 0x1c6d1c]}
    for target, expected in expected_calls.items():
        if direct_calls(elf, target) != expected:
            raise ValueError('Input provenance direct calls differ')
    expected = {0x1facec: 0x00a0802d, 0x1fad78: 0x0200302d,
                0x1fad80: 0x0c054e58, 0x54984: 0x00c0902d,
                0x549e4: 0x0240282d, 0x1fa0d4: 0x3c050045,
                0x1fa0dc: 0x24a58ff0, 0x1fa73c: 0x3c050044,
                0x1fa744: 0x24a531b8, 0x1fd2c0: 0x8e250038,
                0x1fd034: 0xae020038, 0x1fcee4: 0x00a0902d,
                0x1fe99c: 0x00e0882d, 0x1fe9e8: 0x0220282d,
                0x1c6310: 0x8e31001c, 0x1c632c: 0x0220382d,
                0x1c648c: 0x8e30001c, 0x1c64b8: 0x0200382d,
                0x1c69cc: 0x8e70001c, 0x1c69f8: 0x0200382d,
                0x1c6cac: 0x8e70001c, 0x1c6cd8: 0x0200382d}
    for at, value in expected.items():
        if struct.unpack_from('<I', elf, at)[0] != value:
            raise ValueError(f'Input provenance instruction differs {at:x}')
    literals = []
    for at, site in ((0x349ff0, 0x1fa0e4), (0x3441b8, 0x1fa750)):
        raw = elf[at:at+32].split(b'\0', 1)[0]
        if not raw or b'%' in raw:
            raise ValueError('Expected nonexpanding literal differs')
        # This conclusion is for this recipe; a later translation must be
        # rechecked instead of inheriting an original-only absence of tokens.
        if any(e['id'] == f'elf.ui.{at:08x}' for e in recipe['entries']):
            raise ValueError('Provenance literal now has a translation override')
        literals.append({'offset': at, 'upstream_call': site, 'bytes': len(raw),
                         'sha256': sha(raw), 'has_item_token': False})
    return {'small_caller_0x549e8': {
                'direct_entry_calls': expected_calls[0x54960],
                'forwarding_function': 0x1face0,
                'direct_forwarder_calls': expected_calls[0x1face0],
                'input_literals': literals,
                'conclusion': 'Both observed direct upstream inputs are fixed literals without item expansion.',
                'indirect_aliases_excluded': False},
            'small_caller_0x473c8': {
                'known_fixed_literal_offset': 0x317720,
                'other_inputs': 'Copies returned through virtual calls at 0x47334, 0x47370 and 0x47394; canonical targets and complete incoming strings unresolved.',
                'context_zeroed_bytes': 40, 'complete_inputs_proven': False},
            'stream_input': {
                'object_source_field': 0x38, 'load_at': 0x1fd2c0,
                'constructor': 0x1fcec0, 'store_at': 0x1fd034,
                'constructor_direct_calls': expected_calls[0x1fcec0],
                'forwarding_function': 0x1fe978,
                'forwarder_direct_calls': expected_calls[0x1fe978],
                'observed_vm_string_pointer_field': 0x1c,
                'source': 'Constructor argument a1, possibly cut at tab; copied into allocated storage. Not proved to be a finite literal catalogue.',
                'complete_inputs_proven': False},
            'instruction_windows': [{'offset': a, 'size': z-a, 'sha256': sha(elf[a:z])}
                                    for a, z in WINDOWS]}


def emit(elf, table, text, variables=(), *, literal_name=None):
    """Execute original emitter for a deliberately narrow, fail-closed subset.

    The observed 800-byte destination, synthetic variable context and item table
    are supplied by this harness. It does not execute allocation, upstream
    callers, initialization of byte classes, glyph registration or rendering.
    """
    if sha(elf) != ORIGINAL_SHA or len(table) != ITEM_COUNT * STRIDE:
        raise ValueError('Stream source/table differs')
    source = encode(text) + b'\0'
    name_source = None
    if literal_name is not None:
        name_source = encode(literal_name) + b'\0'
        if any(b < 32 for b in name_source[:-1]) or b'%' in name_source:
            raise ValueError('Literal name must be a plain glyph string')
    for token in re.finditer(rb'%I(\$?)([0-9]+)', source[:-1]):
        if token[1] and int(token[2]) not in (0, *SELECTORS['item']):
            raise ValueError('Stream item selector outside reviewed subset')
    rest = re.sub(rb'%I(?:\$[0-9]+|[0-9]+)', b'', source[:-1])
    if literal_name is not None:
        rest = re.sub(rb'%N0(?![0-9$])', b'', rest)
    if b'%' in rest or any(b < 32 and b != 10 for b in rest):
        raise ValueError('Stream probe accepts only plain text, newline and item references')
    regs = [0] * 32
    regs[4:9] = [0x650000, 0x600000, 0x620000, 30, 0x610000]
    regs[29], regs[31] = 0x700000, 0x7ffff0
    initial = regs.copy()
    dest = bytearray(b'\xa5' * 800 + b'GUARD')
    mem, glyphs, lookups, variable_indices, visited = {}, [], [], [], set()
    name_lookups = []
    pc, pending = START, None

    def read(at, size, signed=False):
        if 0x600000 <= at and at+size <= 0x600000+len(source):
            b = source[at-0x600000:at-0x600000+size]
        elif 0x640000 <= at and at+size <= 0x640000+len(table):
            b = table[at-0x640000:at-0x640000+size]
        elif at == 0x475ae8 and size == 4:
            b = (0x640000).to_bytes(4, 'little')
        elif at == 0x47558c and size == 4 and name_source is not None:
            b = (0x680000).to_bytes(4, 'little')
        elif name_source is not None and 0x680000 <= at and at+size <= 0x680000+len(name_source):
            b = name_source[at-0x680000:at-0x680000+size]
        elif all(at+i in mem for i in range(size)):
            b = bytes(mem[at+i] for i in range(size))
        elif 0xff000 <= at and at+size <= 0xff000+len(elf):
            b = elf[at-0xff000:at-0xff000+size]
        else:
            raise ValueError(f'Stream read outside bounded RAM {at:x}/{size}')
        return int.from_bytes(b, 'little', signed=signed)

    def write(at, value, size):
        b = (value & ((1 << (8*size))-1)).to_bytes(size, 'little')
        # A cell's payload store (+4) can be the first out-of-range access;
        # classify it as destination overflow too, before its header is stored.
        if 0x610000 <= at < 0x620000:
            if at+size > 0x610000+800:
                raise ValueError('Original stream exceeds observed 800-byte allocation')
            dest[at-0x610000:at-0x610000+size] = b
        elif 0x6fff20 <= at and at+size <= 0x700010:
            for i, value in enumerate(b):
                mem[at+i] = value
        else:
            raise ValueError(f'Stream write outside bounded RAM {at:x}/{size}')

    for steps in range(200000):
        if pc == 0x7ffff0:
            cells = []
            for at in range(0, 800, 8):
                kind = int.from_bytes(dest[at:at+2], 'little')
                if kind == 5:
                    break
                if kind not in (0, 1):
                    raise ValueError('Unexpected output cell in restricted stream')
                cells.append({'kind': kind, 'code': int.from_bytes(dest[at+4:at+8], 'little') if kind == 0 else None})
            else:
                raise ValueError('Stream terminal missing')
            if dest[800:] != b'GUARD' or any(regs[r] != initial[r] for r in (*range(16,24),29,30,31)):
                raise ValueError('Stream guard/callee-saved registers differ')
            if [c['code'] for c in cells if c['kind'] == 0] != glyphs:
                raise ValueError('Stream registration and output differ')
            return {'cells': cells, 'content_cells': len(cells), 'terminal_cell_index': len(cells),
                    'allocation_bytes': 800, 'guard_unchanged': True, 'callee_saved': True,
                    'lookup_item_ids': lookups, 'variable_indices': variable_indices,
                    'literal_name_indices': name_lookups,
                    'executed_instructions': steps, 'instruction_offsets': sorted(visited),
                    'glyph_registration_modeled': True, 'classification_modeled': True,
                    'upstream_inputs_proven': False}
        if pc == 0x197080:
            b = regs[4] & 255
            value = -1 if b == 0x82 else 0 if b < 32 else 1 if b <= 127 else None
            if value is None:
                raise ValueError('Unmodeled stream classification byte')
            regs[2], pc = value & 0xffffffff, regs[31]
            continue
        if pc == 0x1b5a30:
            if regs[6] != 0x620000:
                raise ValueError('Stream context differs')
            pos = regs[4]-0x600000
            if not 0 <= pos < len(source):
                raise ValueError('Stream argument outside input')
            arg = execute_argument(elf, source[pos:], list(variables))
            index = arg['value']
            if source[pos-1:pos] == b'N':
                if name_source is None or index != 0 or arg['variable_indices']:
                    raise ValueError('Stream literal name must use exact N0')
                name_lookups.append(index)
            else:
                if not 0 <= index < ITEM_COUNT:
                    raise ValueError('Stream item index outside table')
                at = index * STRIDE
                if 0 not in table[at:at+24]:
                    raise ValueError('Stream item name lacks physical-field NUL')
                lookups.append(index)
            write(regs[5], index, 4)
            regs[2] = regs[4] + arg['consumed']
            variable_indices.extend(arg['variable_indices'])
            pc = regs[31]
            continue
        if pc == 0x197778:
            if regs[4] != 0x650000:
                raise ValueError('Stream glyph context differs')
            glyphs.append(regs[5] & 65535)
            pc = regs[31]
            continue
        if not START <= pc < END:
            raise ValueError(f'Stream escaped restricted original function {pc:x}')
        visited.add(pc)
        w = struct.unpack_from('<I', elf, pc)[0]
        op, rs, rt, rd, fn = w >> 26, w >> 21 & 31, w >> 16 & 31, w >> 11 & 31, w & 63
        u = w & 65535; n = u if u < 32768 else u-65536
        old, pending, nextpc = pending, None, pc+4
        if op == 0:
            if fn == 0: regs[rd] = regs[rt] << (w >> 6 & 31)
            elif fn in (33,45): regs[rd] = regs[rs]+regs[rt]
            elif fn == 37: regs[rd] = regs[rs] | regs[rt]
            elif fn == 11:
                if regs[rt]: regs[rd] = regs[rs]
            elif fn == 8:
                target = regs[rs]
                pending = target-0xff000 if 0xff000 <= target < 0xff000+len(elf) else target
            else: raise ValueError(f'Unsupported stream R opcode {w:08x}')
        elif op == 9: regs[rt] = regs[rs]+n
        elif op == 11: regs[rt] = int((regs[rs] & 0xffffffff) < (n & 0xffffffff))
        elif op == 12: regs[rt] = regs[rs] & u
        elif op == 15: regs[rt] = u << 16
        elif op in (30,32,35,36,55):
            regs[rt] = read((regs[rs]+n) & 0xffffffff, {30:16,32:1,35:4,36:1,55:8}[op], op == 32)
        elif op in (31,40,41,43,63):
            write((regs[rs]+n) & 0xffffffff, regs[rt], {31:16,40:1,41:2,43:4,63:8}[op])
        elif op in (4,5,20,21):
            take = regs[rs] == regs[rt] if op in (4,20) else regs[rs] != regs[rt]
            if op in (20,21) and not take: nextpc = pc+8
            else: pending = pc+4+n*4 if take else pc+8
        elif op == 1 and rt in (1,3):
            take = not (regs[rs] & 0x80000000)
            if rt == 3 and not take: nextpc = pc+8
            else: pending = pc+4+n*4 if take else pc+8
        elif op == 3:
            regs[31] = pc+8; pending = ((w & 0x3ffffff) << 2)-0xff000
        else:
            raise ValueError(f'Unsupported stream opcode {w:08x}')
        regs = [v & ((1 << 128)-1) for v in regs]; regs[0] = 0
        pc = old if old is not None else nextpc
    raise ValueError('Stream instruction budget exceeded')


def investigate():
    elf = SOURCE.read_bytes()
    recipe = json.loads((ROOT/RECIPE).read_bytes())
    decisions = json.loads((ROOT/'translations/revisao-humana-itens-v001.json').read_bytes())
    table, targets = name_table(elf, original(RESOURCE), recipe, decisions)
    proof = input_evidence(elf, recipe)
    cases = []
    for index, target in targets.items():
        for token, variables in ((f'%I{index}', ()), ('%I$0', (index,))):
            text = 'Ação: '+token+'!\nPróximo.'
            result = emit(elf, table, text, variables)
            expected = 'Ação: '+target+'!\nPróximo.'
            want = [{'kind': 1, 'code': None} if c == '\n' else
                    {'kind': 0, 'code': int.from_bytes(encode(c), 'big')} for c in expected]
            if result['cells'] != want:
                raise ValueError('Original stream does not match exact expected glyphs')
            cases.append({'item_id': index, 'indirect': bool(variables), **result})
    return {'schema': 1, 'scope': SCOPE, 'recipe': RECIPE,
            'recipe_sha256': sha((ROOT/RECIPE).read_bytes()), 'elf_sha256': sha(elf),
            'input_evidence': proof, 'cases': cases, 'case_count': len(cases),
            'emitter_original_instructions_executed': True,
            'editing_authorized': False, 'new_translations_applied': 0,
            'originals_modified': False, 'iso_created': False, 'pcsx2_executed': False,
            'limits': 'Restricted emitter paths only. Classification, registration and context/table modeled. No allocator, GPU, whole caller, complete message catalogue or whole-game safety proof.'}


def audit_pages(elf, table, targets, fields):
    """Conditional scenarios for actual catalogue pages, not context recovery.

    All indirect I selectors receive the same tested item in each scenario.
    Mixed runtime values and other dynamic controls are not inferred.
    """
    rows = []
    for field in fields:
        for page_index, text in enumerate(field['text'].split('\t')):
            if '%I' not in text:
                continue
            cases = []
            for index in targets:
                try:
                    r = emit(elf, table, text, (index,)*20)
                except ValueError as error:
                    cases.append({'item_id': index, 'status': 'unresolved', 'reason': str(error)})
                else:
                    cases.append({'item_id': index, 'status': 'executed',
                                  'content_cells': r['content_cells'],
                                  'terminal_cell_index': r['terminal_cell_index'],
                                  'lookup_item_ids': r['lookup_item_ids'],
                                  'variable_indices': r['variable_indices'],
                                  'output_cells_sha256': sha(json.dumps(r['cells'], sort_keys=True).encode()),
                                  'guard_unchanged': r['guard_unchanged']})
            rows.append({k: field[k] for k in ('id', 'segment', 'offset', 'record_sha256')}
                        | {'page_index': page_index, 'page_sha256': sha(encode(text)),
                           'status': 'all_sampled_contexts_executed' if all(c['status'] == 'executed' for c in cases) else 'unresolved',
                           'cases': cases})
    return {'item_fields': len(fields), 'item_pages': len(rows),
            'pages_all_sampled_contexts_executed': sum(r['status'] == 'all_sampled_contexts_executed' for r in rows),
            'pages_unresolved': sum(r['status'] == 'unresolved' for r in rows),
            'executed_scenarios': sum(c['status'] == 'executed' for r in rows for c in r['cases']),
            'unresolved_scenarios': sum(c['status'] == 'unresolved' for r in rows for c in r['cases']),
            'rows': rows, 'canonical_variable_values_recovered': False,
            'all_runtime_combinations_proven': False,
            'limits': 'Known compiled MAP catalogue only, pages containing I references. Six conditional same-item contexts; other controls remain unresolved. Not proof of every input reaching the emitter.'}


def audit_mixed_pages(elf, table, targets, fields):
    """Measure conditional N0 budgets without claiming runtime name bounds."""
    rows = []
    scenarios = 0
    for field in fields:
        for page_index, text in enumerate(field['text'].split('\t')):
            if '%I' not in text or '%N0' not in text:
                continue
            if text.count('%N0') != 1:
                raise ValueError('Mixed-name budget requires one exact N0 reference')
            cases = []
            for index in targets:
                variables = (index,)*20
                empty = emit(elf, table, text, variables, literal_name='')
                if empty['literal_name_indices'] != [0]:
                    raise ValueError('Mixed-name lookup is not literal zero')
                budget = 99-empty['content_cells']
                if budget < 0:
                    raise ValueError('Mixed page does not fit even with empty name')
                outputs = []
                for name in ('Nina', 'João', 'A'*budget, 'é'*budget):
                    r = emit(elf, table, text, variables, literal_name=name)
                    if r['content_cells'] != empty['content_cells']+len(name):
                        raise ValueError('Mixed-name cells differ from additive expectation')
                    outputs.append({'name_characters': len(name), 'name_bytes': len(encode(name)),
                                    'name_sha256': sha(encode(name)), 'content_cells': r['content_cells'],
                                    'cells_sha256': sha(json.dumps(r['cells'], sort_keys=True).encode())})
                failure = None
                try:
                    emit(elf, table, text, variables, literal_name='A'*(budget+1))
                except ValueError as error:
                    failure = str(error)
                if failure != 'Original stream exceeds observed 800-byte allocation':
                    raise ValueError('Mixed-name over-budget scenario did not reach expected bound')
                scenarios += 6  # empty, two sample names, two exact boundaries, one negative
                cases.append({'item_id': index, 'literal_name_index': 0,
                              'content_cells_without_name': empty['content_cells'],
                              'maximum_name_cells_for_this_page_and_context': budget,
                              'samples_and_boundaries': outputs, 'over_budget_refused': True,
                              'guard_unchanged': True, 'canonical_name_length_proven': False})
            rows.append({k: field[k] for k in ('id', 'segment', 'offset', 'record_sha256')}
                        | {'page_index': page_index, 'page_sha256': sha(encode(text)), 'cases': cases})
    return {'pages': len(rows), 'conditional_cases': sum(len(r['cases']) for r in rows),
            'instruction_scenarios': scenarios, 'rows': rows,
            'minimum_conditional_name_cell_budget': min((c['maximum_name_cells_for_this_page_and_context']
                                                        for r in rows for c in r['cases']), default=None),
            'canonical_name_identity_proven': False, 'runtime_name_maximum_proven': False,
            'limits': 'The original N0 handler executes; its pointer table and supplied name are synthetic. Two sample names are not identified scene actors. Budgets are conditional on the six supplied item contexts, not all runtime values.'}


def audit_map(*, include_mixed=False):
    from build_translation_pilot import load_draft, compile_draft
    from reinsertion import SOURCE as MAP_SOURCE
    elf = SOURCE.read_bytes()
    recipe = json.loads((ROOT/RECIPE).read_bytes())
    decisions = json.loads((ROOT/'translations/revisao-humana-itens-v001.json').read_bytes())
    table, targets = name_table(elf, original(RESOURCE), recipe, decisions)
    draft, bindings = load_draft(ROOT/recipe['base_dialogue_draft'])
    with MAP_SOURCE.open('rb') as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as data:
        document, _, report = compile_draft(data, draft)
        if not report['valid']:
            raise ValueError('Dialogue baseline compilation failed')
        fields = [{'id': e['id'], 'segment': part['key'], 'offset': part['offset'],
                   'record_sha256': e['record_sha256'], 'text': part['translation']}
                  for e in document['entries'] for part in e['segments'] if '%I' in part['translation']]
    result = {'catalogue_records': len(document['entries']), 'recipe_bindings': bindings,
              **audit_pages(elf, table, targets, fields)}
    if include_mixed:
        result['mixed_names'] = audit_mixed_pages(elf, table, targets, fields)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Investigar entradas e fluxo de glifos de nomes, sem editar o jogo')
    p.add_argument('--output', type=Path, default=ROOT/'work/fluxo-nomes-atual.json')
    p.add_argument('--audit-map', action='store_true', help='Também compilar e conferir páginas do catálogo MAP atual')
    p.add_argument('--audit-mixed-names', action='store_true', help='Medir também as páginas N0+I e seus limites condicionais')
    args = p.parse_args()
    out = args.output.resolve()
    if not out.is_relative_to(ROOT/'work'):
        raise ValueError('Keep detailed stream output under work/')
    if out.exists() and json.loads(out.read_bytes()).get('scope') != SCOPE:
        raise ValueError('Refuse unrelated stream output')
    result = investigate()
    if args.audit_map or args.audit_mixed_names:
        result['map_audit'] = audit_map(include_mixed=args.audit_mixed_names)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'cases': result['case_count'], 'editing_authorized': False,
                      'map_audit': {k: v for k, v in result.get('map_audit', {}).items()
                                    if k not in ('rows', 'recipe_bindings', 'mixed_names')},
                      'mixed_names': {k: v for k, v in result.get('map_audit', {}).get('mixed_names', {}).items()
                                      if k != 'rows'}}))
