import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import item_name_buffers as b
from interface_text import SOURCE
from item_names import original,RESOURCE,catalog,validate_value
from gfi import encode

class ItemNameBuffers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes();cls.raw=original(RESOURCE)
        cls.recipe=json.loads((ROOT/b.RECIPE).read_bytes());cls.decisions=json.loads((ROOT/'translations/revisao-humana-itens-v001.json').read_bytes())
        cls.table,cls.targets=b.name_table(cls.elf,cls.raw,cls.recipe,cls.decisions)
        cls.result=b.investigate()

    def test_four_exact_direct_calls_and_live_area_boundaries(self):
        e=self.result['caller_evidence']
        self.assertEqual(e['direct_calls'],[0x473c8,0x549e8,0x1c6fe4,0x1ccdb0])
        self.assertEqual([r['bytes_before_next_live_area'] for r in e['callers']],[128,128,1024,1024])
        self.assertEqual(e['aligned_function_pointer_literals'],[])
        self.assertFalse(self.result['upstream_runtime_input_lengths_proven'])

    def test_48_original_function_cases_exact_names_and_terminators(self):
        self.assertEqual(self.result['case_count'],48)
        for r in self.result['cases']:
            self.assertEqual(r['output_text'],'Recebeu '+self.targets[r['item_id']]+'!')
            self.assertEqual(bytes.fromhex(r['output_hex']),encode(r['output_text']))
            self.assertEqual(r['lookup_item_ids'],[r['item_id']])
            self.assertEqual(r['variable_indices'],[0] if r['indirect'] else [])
            self.assertTrue(r['guard_unchanged']);self.assertTrue(r['nul_written']);self.assertTrue(r['callee_saved'])
            self.assertFalse(r['upstream_inputs_proven'])

    def test_synthetic_overflow_detected_even_when_input_itself_fits(self):
        n=self.result['negative_case'];self.assertLess(n['input_bytes'],128);self.assertGreater(n['expected_output_bytes'],128)
        self.assertFalse(n['observed_in_game'])
        with self.assertRaisesRegex(ValueError,'next live caller area'):
            b.expand(self.elf,self.table,' '.join(['%I331']*7),128)
        r=b.expand(self.elf,self.table,' '.join(['%I331']*7),1024)
        self.assertEqual(r['output_text'],' '.join([self.targets[331]]*7))

    def test_boundary_includes_space_for_final_nul(self):
        target=self.targets[838];raw=encode(target)
        text='A'*(127-len(raw))+'%I838'
        r=b.expand(self.elf,self.table,text,128);self.assertEqual(r['output_bytes'],127)
        with self.assertRaisesRegex(ValueError,'next live caller area'):
            b.expand(self.elf,self.table,'A'+text,128)

    def test_ascii_accented_literal_and_multiple_item_references(self):
        text='Ação: %I331 + %I838.'
        r=b.expand(self.elf,self.table,text,128)
        self.assertEqual(r['output_text'],'Ação: '+self.targets[331]+' + '+self.targets[838]+'.')
        self.assertEqual(r['lookup_item_ids'],[331,838])

    def test_bad_item_index_context_token_and_arbitrary_scratch_refused(self):
        for text,cap,var in [('%I1349',128,()),('%I$0',128,()),('%I$1',128,(331,372)),('%X0',128,()),('%I331',32,())]:
            with self.assertRaises(ValueError):b.expand(self.elf,self.table,text,cap,var)
        bad=bytearray(self.elf);bad[0x1cd488]^=1
        with self.assertRaises(ValueError):b.expand(bytes(bad),self.table,'%I331',128)
        with self.assertRaises(ValueError):b.caller_evidence(bytes(bad))

    def test_separate_800_byte_cell_stream_is_not_claimed_executed(self):
        e=self.result['caller_evidence']['separate_glyph_emitter']
        self.assertEqual(e['observed_allocation_request_bytes'],800)
        self.assertEqual(e['glyph_cell_stride_bytes'],8)
        self.assertEqual(e['maximum_cells_before_terminal_for_observed_allocation'],99)
        self.assertFalse(e['executed_in_this_probe']);self.assertEqual(e['direct_calls'],[0x1fd2bc])

    def test_synthetic_tables_preserve_attributes_and_legacy_guard_still_blocks(self):
        rows={r['index']:r for r in catalog(self.raw)}
        for index in range(b.ITEM_COUNT):
            at=index*b.STRIDE
            self.assertEqual(self.table[at+24:at+b.STRIDE],self.raw[b.ITEM_BASE+at+24:b.ITEM_BASE+at+b.STRIDE])
        for index,text in self.targets.items():
            with self.assertRaises(ValueError):validate_value(rows[index],text,ceiling=16)
        self.assertFalse(self.result['editing_authorized']);self.assertFalse(self.result['iso_created'])

if __name__=='__main__':unittest.main()
