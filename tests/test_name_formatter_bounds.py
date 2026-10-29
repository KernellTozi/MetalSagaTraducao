import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import name_formatter_bounds as f
from item_names import original,RESOURCE
from item_name_buffers import name_table,RECIPE
from interface_text import SOURCE
from gfi import encode


class NameFormatterBounds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes()
        recipe=json.loads((ROOT/RECIPE).read_bytes())
        d=json.loads((ROOT/'translations/revisao-humana-itens-v001.json').read_bytes())
        cls.table,cls.targets=name_table(cls.elf,original(RESOURCE),recipe,d)
        cls.result=f.investigate()

    def test_two_real_destinations_have_64_byte_separation(self):
        r=self.result['evidence']
        self.assertEqual([c['call_offset'] for c in r['two_observed_scratch_areas']],[0x123f50,0x123f60])
        self.assertEqual([c['bytes'] for c in r['two_observed_scratch_areas']],[64,64])
        self.assertEqual(r['actor_name_field']['bytes_initialized'],32)
        self.assertTrue(r['actor_name_field']['setter_uses_unbounded_strcpy'])
        self.assertFalse(r['actor_name_field']['runtime_nul_within_field_proven'])

    def test_18_exact_outputs_and_literal_item_name_lookup(self):
        self.assertEqual(self.result['case_count'],18)
        for r in self.result['cases']:
            self.assertTrue(r['text'].startswith('Achou '+self.targets[r['item_id']]+'\n'))
            self.assertTrue(r['text'].endswith('!'))
            self.assertEqual(bytes.fromhex(r['output_hex']),encode(r['text']))
            self.assertEqual(r['lookup_item_ids'],[r['item_id']])
            self.assertTrue(r['nul_written']);self.assertTrue(r['callee_saved'])
            self.assertTrue(r['source_pipes_changed_to_lf'])
            self.assertTrue(r['copy_helpers_modeled'])
            self.assertFalse(r['upstream_inputs_proven'])

    def test_ascii_empty_input_and_accented_source_pair_copy(self):
        for text,name,expected in [('','', ''),('Olá|Ação','','Olá\nAção'),('%N0!','','!')]:
            r=f.format_text(self.elf,self.table,text,name)
            self.assertEqual(r['text'],expected)
            self.assertTrue(r['source_other_bytes_unchanged'])

    def test_boundary_includes_nul_and_overflow_is_caught(self):
        name=self.targets[331]
        text='A'*(63-len(encode(name)))+'%I331'
        r=f.format_text(self.elf,self.table,text,'Nina')
        self.assertEqual(r['output_bytes'],63)
        with self.assertRaisesRegex(ValueError,'outside supplied memory'):
            f.format_text(self.elf,self.table,'A'+text,'Nina')

    def test_repeated_items_can_exceed_bound_even_if_source_fits(self):
        text='%I331/'*4
        self.assertLess(len(encode(text)),64)
        with self.assertRaisesRegex(ValueError,'outside supplied memory'):
            f.format_text(self.elf,self.table,text,'Nina')
        self.assertFalse(self.result['editing_authorized'])

    def test_indirect_unsupported_and_invalid_names_refused(self):
        for text,name,capacity in [('%I$0','Nina',64),('%N$0','Nina',64),
             ('%N1','Nina',64),('%B15','Nina',64),('%I1349','Nina',64),
             ('%N0','A'*32,64),('%N0','é'*16,64),('a\tb','Nina',64),('%I331','Nina',128)]:
            with self.assertRaises(ValueError):f.format_text(self.elf,self.table,text,name,capacity)

    def test_name_is_copied_without_recursive_token_expansion(self):
        r=f.format_text(self.elf,self.table,'%N0|%I331','%I838')
        self.assertEqual(r['text'],'%I838\n'+self.targets[331])
        self.assertEqual(r['lookup_item_ids'],[331])

    def test_source_revision_and_truncated_name_table_refused(self):
        bad=bytearray(self.elf);bad[f.START]^=1
        with self.assertRaises(ValueError):f.format_text(bytes(bad),self.table,'Teste','Nina')
        with self.assertRaises(ValueError):f.format_text(self.elf,self.table[:-1],'Teste','Nina')

    def test_two_callers_resolve_to_82_mail_headers_without_item_dependencies(self):
        r=self.result['mail_dependency_audit']
        self.assertEqual(r['resolved_direct_calls'],[0x123f50,0x123f60])
        self.assertEqual((r['mail_records'],r['fields'],r['original_getter_executions']),(41,82,82))
        self.assertEqual(len({(x['mail_id'],x['field']) for x in r['rows']}),82)
        self.assertTrue(all(x['item_references']==0 for x in r['rows']))
        self.assertFalse(r['item_name_growth_affects_these_two_inputs'])
        self.assertFalse(r['all_other_formatting_capacity_proven'])
        self.assertEqual(r['remaining_direct_calls_to_trace'],7)

    def test_all_nine_observed_calls_map_to_299_fields_without_I(self):
        r=self.result['consumer_input_audit']
        self.assertEqual((r['mail_fields'],r['wanted_bodies'],r['diary_fields']),(123,40,136))
        self.assertEqual(r['unique_fields'],299)
        self.assertEqual(len({x['id'] for x in r['rows']}),299)
        self.assertEqual(len(r['direct_call_input_classes']),9)
        self.assertEqual(r['unresolved_direct_input_classes'],0)
        self.assertTrue(all(x['item_references']==0 for x in r['rows']))
        self.assertFalse(r['item_name_growth_affects_observed_corpora'])
        self.assertFalse(r['all_runtime_mutations_or_indirect_calls_proven'])


if __name__=='__main__':unittest.main()
