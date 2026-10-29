import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
import item_name_stream as s
from item_name_buffers import name_table, RECIPE
from item_names import original, RESOURCE
from interface_text import SOURCE
from gfi import encode


def cells(text):
    return [{'kind': 1, 'code': None} if c == '\n' else
            {'kind': 0, 'code': int.from_bytes(encode(c), 'big')} for c in text]


class ItemNameStream(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf = SOURCE.read_bytes()
        cls.recipe = json.loads((ROOT/RECIPE).read_bytes())
        decisions = json.loads((ROOT/'translations/revisao-humana-itens-v001.json').read_bytes())
        cls.table, cls.targets = name_table(cls.elf, original(RESOURCE), cls.recipe, decisions)
        cls.result = s.investigate()

    def test_direct_chain_reaches_two_literals_without_item_tokens(self):
        p = self.result['input_evidence']['small_caller_0x549e8']
        self.assertEqual(p['direct_entry_calls'], [0x1fad80])
        self.assertEqual(p['direct_forwarder_calls'], [0x1fa0e4, 0x1fa750])
        self.assertEqual([r['bytes'] for r in p['input_literals']], [5, 10])
        self.assertFalse(any(r['has_item_token'] for r in p['input_literals']))
        self.assertFalse(p['indirect_aliases_excluded'])

    def test_future_literal_override_invalidates_provenance(self):
        recipe = copy.deepcopy(self.recipe)
        recipe['entries'].append({'id': 'elf.ui.00349ff0', 'translation': '%I331'})
        with self.assertRaisesRegex(ValueError, 'translation override'):
            s.input_evidence(self.elf, recipe)

    def test_unresolved_virtual_and_constructor_inputs_stay_explicit(self):
        p = self.result['input_evidence']
        self.assertFalse(p['small_caller_0x473c8']['complete_inputs_proven'])
        self.assertFalse(p['stream_input']['complete_inputs_proven'])
        self.assertEqual(p['stream_input']['object_source_field'], 0x38)
        self.assertEqual(len(p['stream_input']['forwarder_direct_calls']), 8)
        self.assertEqual(p['stream_input']['observed_vm_string_pointer_field'], 0x1c)
        self.assertFalse(self.result['editing_authorized'])
        self.assertEqual(self.result['new_translations_applied'], 0)

    def test_twelve_cases_include_exact_names_accents_newline_and_suffix(self):
        self.assertEqual(self.result['case_count'], 12)
        for r in self.result['cases']:
            self.assertEqual(r['cells'], cells('Ação: '+self.targets[r['item_id']]+'!\nPróximo.'))
            self.assertEqual(r['lookup_item_ids'], [r['item_id']])
            self.assertEqual(r['variable_indices'], [0] if r['indirect'] else [])
            self.assertTrue(r['guard_unchanged'])
            self.assertTrue(r['callee_saved'])
            self.assertFalse(r['upstream_inputs_proven'])
            self.assertIn(0x1b5f88, r['instruction_offsets'])
            self.assertIn(0x1b5d90, r['instruction_offsets'])

    def test_empty_input_has_only_terminal(self):
        r = s.emit(self.elf, self.table, '')
        self.assertEqual(r['cells'], [])
        self.assertEqual(r['terminal_cell_index'], 0)

    def test_ascii_boundary_reserves_terminal_cell(self):
        r = s.emit(self.elf, self.table, 'A'*99)
        self.assertEqual(r['content_cells'], 99)
        with self.assertRaisesRegex(ValueError, '800-byte allocation'):
            s.emit(self.elf, self.table, 'A'*100)

    def test_two_byte_glyphs_count_as_one_cell_and_a3_is_not_a_cell_limit(self):
        text = 'é'*99
        self.assertEqual(len(encode(text)), 198)
        r = s.emit(self.elf, self.table, text)
        self.assertEqual(r['cells'], cells(text))
        self.assertEqual(r['content_cells'], 99)
        with self.assertRaisesRegex(ValueError, '800-byte allocation'):
            s.emit(self.elf, self.table, text+'é')

    def test_newline_consumes_cell_and_boundary_is_checked(self):
        r = s.emit(self.elf, self.table, '\n'*99)
        self.assertEqual(r['content_cells'], 99)
        self.assertTrue(all(c['kind'] == 1 for c in r['cells']))
        with self.assertRaisesRegex(ValueError, '800-byte allocation'):
            s.emit(self.elf, self.table, '\n'*100)

    def test_expanded_item_boundary_checks_full_message(self):
        name = self.targets[331]
        text = 'X'*(99-len(name))+'%I331'
        r = s.emit(self.elf, self.table, text)
        self.assertEqual(r['content_cells'], 99)
        with self.assertRaisesRegex(ValueError, '800-byte allocation'):
            s.emit(self.elf, self.table, 'X'+text)

    def test_multiple_references_and_context_lookup_keep_exact_order(self):
        r = s.emit(self.elf, self.table, '%I331/%I$0\n%I849', (838,))
        self.assertEqual(r['cells'], cells(self.targets[331]+'/'+self.targets[838]+'\n'+self.targets[849]))
        self.assertEqual(r['lookup_item_ids'], [331, 838, 849])
        self.assertEqual(r['variable_indices'], [0])

    def test_all_reviewed_item_selectors_execute_original_reader_and_emitter(self):
        for selector in (0, 1, 2, 9, 10, 15, 19):
            for index, name in self.targets.items():
                values = [0]*20; values[selector] = index
                r = s.emit(self.elf, self.table, f'%I${selector}!', values)
                self.assertEqual(r['cells'], cells(name+'!'))
                self.assertEqual(r['variable_indices'], [selector])
                self.assertEqual(r['lookup_item_ids'], [index])

    def test_page_audit_keeps_unsupported_controls_and_overflow_unresolved(self):
        fields = [{'id': 'synthetic', 'segment': 'body', 'offset': 123,
                   'record_sha256': 'synthetic', 'text': '%I$0!\t%N0 %I$0\t'+'X'*99+'%I$0'}]
        r = s.audit_pages(self.elf, self.table, self.targets, fields)
        self.assertEqual(r['item_fields'], 1)
        self.assertEqual(r['item_pages'], 3)
        self.assertEqual(r['pages_all_sampled_contexts_executed'], 1)
        self.assertEqual(r['pages_unresolved'], 2)
        self.assertEqual(r['executed_scenarios'], 6)
        self.assertEqual(r['unresolved_scenarios'], 12)
        self.assertIn('800-byte allocation', r['rows'][2]['cases'][0]['reason'])
        self.assertFalse(r['all_runtime_combinations_proven'])
        self.assertFalse(r['canonical_variable_values_recovered'])

    def test_page_audit_ignores_pages_without_item_references(self):
        f = {'id': 'synthetic', 'segment': 'body', 'offset': 0,
             'record_sha256': 'synthetic', 'text': 'Olá.\t%I$0\tFim.'}
        r = s.audit_pages(self.elf, self.table, self.targets, [f])
        self.assertEqual(r['item_pages'], 1)
        self.assertEqual(r['rows'][0]['page_index'], 1)

    def test_unsupported_tokens_context_indices_and_unterminated_names_refused(self):
        for text, variables in [('%X0', ()), ('%I$3', (331,372,459,838)), ('%I$0', ()),
                                ('%I1349', ()), ('a\tb', ()), ('a\0b', ()), ('%%', ())]:
            with self.assertRaises(ValueError):
                s.emit(self.elf, self.table, text, variables)
        table = bytearray(self.table)
        table[331*128:331*128+24] = b'A'*24
        with self.assertRaisesRegex(ValueError, 'physical-field NUL'):
            s.emit(self.elf, bytes(table), '%I331')

    def test_source_mismatch_and_truncated_table_refused(self):
        elf = bytearray(self.elf); elf[s.START] ^= 1
        with self.assertRaises(ValueError):
            s.emit(bytes(elf), self.table, 'Teste')
        with self.assertRaises(ValueError):
            s.input_evidence(bytes(elf), self.recipe)
        with self.assertRaises(ValueError):
            s.emit(self.elf, self.table[:-1], 'Teste')


if __name__ == '__main__':
    unittest.main()
