import copy,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import item_name_capacity as c
from interface_text import SOURCE
from item_names import catalog,original,RESOURCE,validate_value,compile_names
from gfi import encode

class ItemNameCapacity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes();cls.raw=original(RESOURCE)
        cls.recipe=json.loads((ROOT/c.RECIPE).read_bytes());cls.decisions=json.loads((ROOT/c.DECISIONS).read_bytes())
        cls.result=c.investigate(cls.elf,cls.raw,cls.recipe,cls.decisions)
        cls.rows={r['id']:r for r in catalog(cls.raw)}

    def test_exact_authorized_wording_and_16_identity_bindings(self):
        self.assertEqual(len(self.result['items']),16)
        for row,decision in zip(self.result['items'],self.decisions['blocked']):
            self.assertEqual((row['id'],row['desired_translation']),(decision['id'],decision['desired_not_applied']))
            self.assertEqual(row['record_sha256'],self.rows[row['id']]['record_sha256'])
            self.assertFalse(row['editing_authorized'])
        self.assertFalse(self.result['editing_authorized']);self.assertFalse(self.result['iso_created'])

    def test_separate_storage_width_and_glyph_constraints(self):
        self.assertEqual(self.result['counts']['codec_supported'],15)
        within={r['id'] for r in self.result['items'] if r['within_all_observed_width_profiles']}
        self.assertEqual(within,{'item.name.0331','item.name.0372','item.name.0459','item.name.0838','item.name.0841','item.name.0849'})
        self.assertEqual(sum(r['within_all_observed_width_profiles'] is False for r in self.result['items']),9)
        glyph=next(r for r in self.result['items'] if r['id']=='item.name.0460')
        self.assertIn('U+00CD',glyph['codec_error']);self.assertIsNone(glyph['fits_physical_name_field'])
        self.assertIsNone(glyph['renderer_scan_probe']);self.assertEqual(glyph['profiles'],[])

    def test_original_renderer_scans_every_accent_and_final_letter(self):
        for row in self.result['items']:
            if row['codec_error']:continue
            actual=c.probe(self.elf,encode(row['desired_translation']))
            self.assertEqual(actual['glyph_codes'],[int.from_bytes(encode(char),'big') for char in row['desired_translation']])
            self.assertEqual(actual['consumed_bytes'],row['encoded_bytes']+1)
            self.assertTrue(actual['callee_saved']);self.assertTrue(actual['classification_table_modeled'])

    def test_scalar_copy_does_not_write_terminator_or_imply_real_buffer(self):
        for row in self.result['items']:
            if row['codec_error']:continue
            p=row['scalar_expansion_copy_probe'];self.assertEqual(p['copied_bytes'],row['encoded_bytes'])
            self.assertTrue(p['guard_unchanged']);self.assertTrue(p['source_terminator_read'])
            self.assertFalse(p['destination_nul_written']);self.assertFalse(p['real_destination_capacity_proven'])

    def test_second_direct_renderer_scans_accented_codes_without_drawing_spaces(self):
        for row in self.result['items']:
            if row['codec_error']:continue
            p=row['direct_draw_loop_probe'];self.assertEqual(p['loop_offset'],0x3e1f0)
            self.assertEqual(p['glyph_codes'],[int.from_bytes(encode(c),'big') for c in row['desired_translation'] if c!=' '])
            self.assertEqual(p['consumed_bytes'],row['encoded_bytes']+1)
            self.assertTrue(p['draw_and_escape_compare_modeled']);self.assertIsNone(p['callee_saved'])

    def test_copy_bounds_malformed_pair_and_source_revision_fail_closed(self):
        with self.assertRaises(ValueError):c.probe(self.elf,b'A'*40,copy=True)
        with self.assertRaises(ValueError):c.probe(self.elf,b'\x82')
        with self.assertRaises(ValueError):c.probe(self.elf,b'A\0B')
        bad=bytearray(self.elf);bad[0x1978bc]^=1
        with self.assertRaises(ValueError):c.probe(bytes(bad),b'A')
        with self.assertRaises(ValueError):c.census(bytes(bad))

    def test_fifteen_hypothetical_fields_roundtrip_preserve_all_attributes(self):
        for row in self.result['items']:
            if row['codec_error']:continue
            source=self.rows[row['id']];at=source['offset'];before=self.raw[at:at+128]
            value=encode(row['desired_translation']);field=value+bytes(24-len(value))
            after=field+before[24:];self.assertEqual(after[24:],before[24:]);self.assertEqual(len(after),len(before))
            restored=before[:24]+after[24:];self.assertEqual(restored,before)

    def test_eight_related_actions_keep_aliases_and_independent_18_byte_limit(self):
        pairs={r['id']:[a['id'] for a in r['battle_counterparts']] for r in self.result['items']}
        self.assertEqual(pairs['item.name.0354'],pairs['item.name.0373'])
        self.assertEqual(len(pairs['item.name.0849']),2)
        self.assertEqual(len({a for group in pairs.values() for a in group}),8)
        exceeding={a['id'] for r in self.result['items'] for a in r['battle_counterparts'] if a['desired_exceeds_action_ceiling']}
        self.assertEqual(exceeding,{'battle.action.0881','battle.action.0886'})

    def test_census_is_reproducible_candidates_without_safety_promotion(self):
        roots=self.result['pointer_candidates']
        self.assertEqual(len(roots['raw_low_immediate_load_candidates']),54)
        self.assertEqual(len(roots['direct_record_getter_calls']),190)
        self.assertTrue(any(r['offset']==0x6d940 for r in roots['raw_low_immediate_load_candidates']))
        self.assertTrue(all('not necessarily a name' in r['status'] for r in roots['direct_record_getter_calls']))
        self.assertIn('not full data-flow proof',self.result['limits'])

    def test_historical_compiler_still_rejects_all_16_proposals(self):
        for row in self.result['items']:
            with self.assertRaises(ValueError):validate_value(self.rows[row['id']],row['desired_translation'],ceiling=16)
        patches,report=compile_names(self.elf,self.recipe['item_names'])
        self.assertEqual(report['accepted'],541);self.assertEqual(len(patches),541)

    def test_cli_rejects_external_or_unrelated_outputs_before_analysis(self):
        with self.assertRaises(ValueError):c.run(ROOT/'reports/wrong-detailed-output.json')
        with tempfile.TemporaryDirectory(dir=ROOT/'work') as folder:
            path=Path(folder)/'unrelated.json';path.write_text('{}',encoding='utf-8')
            with self.assertRaises(ValueError):c.run(path)
            self.assertEqual(path.read_text(encoding='utf-8'),'{}')

if __name__=='__main__':unittest.main()
