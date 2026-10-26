import copy,json,struct,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import paint_graphic_proposals as p
from interface_text import SOURCE


class PaintProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw,cls.inventory=p.inventory();cls.elf=SOURCE.read_bytes();cls.Image=p.pillow()
        cls.temp=tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-paint-proposals-')
        cls.folder=Path(cls.temp.name)/'proposal'
        cls.result=p.run(cls.folder)
        cls.proposed=(cls.folder/'reconstruido/S_PAINT.SDA').read_bytes()

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_four_texture_ganm_pairs_execute_original_forwarding(self):
        proof=p.usage_proof(self.elf,self.raw)
        self.assertEqual([(c['texture_entry'],c['ganm_entry']) for c in proof['cases']],[(11,12),(13,14),(15,16),(17,18)])
        self.assertTrue(all(c['forwarding_executed'] for c in proof['cases']))
        self.assertEqual(proof,self.result['usage_proof'])

    def test_source_hash_mutations_blocked(self):
        bad=bytearray(self.elf);bad[0]^=1
        with self.assertRaises(ValueError):p.usage_proof(bad,self.raw)
        bad=bytearray(self.raw);bad[-1]^=1
        with self.assertRaises(ValueError):p.usage_proof(self.elf,bad)

    def test_six_new_drawings_and_six_original_crops(self):
        changed={r['id'] for r in self.result['proposed_labels']}
        self.assertEqual(len(changed),6);self.assertEqual(len(self.result['preserved_crop_ids']),6)
        for row in self.inventory['entries']:
            with self.Image.open(self.folder/'originais'/row['png']) as before,self.Image.open(self.folder/'botoes'/row['png']) as after:
                self.assertEqual(before.mode,'P');self.assertEqual(after.mode,'P')
                self.assertEqual(before.size,after.size);self.assertEqual(before.getpalette(),after.getpalette())
                self.assertEqual(before.info['transparency'],after.info['transparency'])
                if row['id'] in changed:self.assertNotEqual(before.tobytes(),after.tobytes())
                else:self.assertEqual(before.tobytes(),after.tobytes())
        for key in ('paint.button.13.01','paint.button.13.02','paint.button.13.06','paint.button.13.07'):
            self.assertIn(key,self.result['preserved_crop_ids'])

    def test_original_frames_and_canvas_dimensions_preserved(self):
        for row in self.inventory['entries']:
            if row['texture_entry']!=13 or row['sprite_index'] not in p.TARGETS:continue
            with self.Image.open(self.folder/'originais'/row['png']) as before,self.Image.open(self.folder/'botoes'/row['png']) as after:
                a=before.tobytes();b=after.tobytes()
                for i,(old,new) in enumerate(zip(a,b)):
                    if not (2<=i%238<236 and 2<=i//238<27):self.assertEqual(old,new)

    def test_no_resize_consistent_capital_body_and_baseline(self):
        for row in self.result['proposed_labels']:
            self.assertEqual(row['capital_body_pixels'],16)
            self.assertEqual(row['baseline_in_crop'],20);self.assertEqual(row['horizontal_scale'],1)
            glyph=p.mask(row['translation'])
            self.assertEqual(row['mask_sha256'],p.sha(glyph.tobytes()));self.assertLessEqual(glyph.width,226)
            self.assertEqual(set(glyph.tobytes()),{0,255})

    def test_unmapped_characters_controls_and_overflow_refused(self):
        for text in ('Teste Ω','%N$0','linha\nnova',''):
            with self.assertRaises(ValueError):p.mask(text)
        row=self.inventory['entries'][0]
        with self.Image.open(self.folder/'originais'/row['png']) as before:
            with self.assertRaises(ValueError):p.render_crop(before,'Editar'*100)
            with self.assertRaises(ValueError):p.render_crop(before.convert('RGBA').convert('RGB'),'Editar')
            with self.assertRaises(ValueError):p.render_crop(before.crop((0,0,40,20)),'Editar')

    def test_228_translated_captions_survive_combined_reverse_roundtrip(self):
        report=p.verify_caption_overlay(self.raw,self.proposed,self.elf)
        self.assertEqual(report,self.result['caption_overlay'])
        self.assertEqual(report['caption_fields_preserved'],228)
        self.assertTrue(report['combined_reverse_roundtrip']);self.assertFalse(report['caption_art_overlap'])
        self.assertEqual(len(self.proposed),len(self.raw))
        bad=bytearray(self.proposed);bad[-1]^=1
        with self.assertRaises(ValueError):p.verify_caption_overlay(self.raw,bad,self.elf)

    def test_changes_in_other_label_or_frame_refused(self):
        from interface_texture_pack import unpack_indices,replace_indices
        row=self.inventory['entries'][0];at=row['texture_offset'];z=at+row['texture_size']
        source=self.proposed[at:z];indices=bytearray(unpack_indices(source,row['texture']))
        for index in (0,34*256+20,200*256+20):
            bad_indices=indices.copy();bad_indices[index]^=1
            bad=self.proposed[:at]+replace_indices(source,bad_indices)+self.proposed[z:]
            with self.assertRaises(ValueError):p.verify_caption_overlay(self.raw,bad,self.elf)

    def test_report_stays_work_only_and_output_path_not_overwritten(self):
        self.assertFalse(self.result['iso_modified']);self.assertFalse(self.result['pcsx2_executed'])
        self.assertEqual(self.result['art_approval'],'pending_user_review')
        with self.assertRaises(ValueError):p.run(self.folder)
        with self.assertRaises(ValueError):p.run(ROOT/'JOGO/proposta-bloqueada')


if __name__=='__main__':unittest.main()
