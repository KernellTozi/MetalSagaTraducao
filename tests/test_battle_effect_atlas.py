import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import battle_effect_atlas as b
from interface_text import SOURCE,compile_draft


class EffectAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes()
        cls.recipe=json.loads((b.ROOT/'translations/interface-v059.json').read_bytes())
        cls.parent,cls.manifest=b.validate_interface(cls.recipe)
        cls.patches,cls.report=b.compile_slots(cls.elf,cls.manifest)

    def test_exact_extents_and_original_decoder_roundtrip(self):
        self.assertEqual([p['id'] for p in self.patches],['battle.tim2.1587','battle.tim2.1588'])
        self.assertEqual([p['offset'] for p in self.patches],[321425408,321443840])
        self.assertEqual([len(p['after']) for p in self.patches],[18432,16384])
        self.assertEqual(self.report['accepted'],34)
        self.assertTrue(self.report['original_decoder_roundtrip'])
        for p,row in zip(self.patches,self.report['results']):
            self.assertEqual(len(p['before']),len(p['after']))
            decoded,used,_=b.decode(p['after'],maximum=66624)
            self.assertEqual(len(decoded),66624)
            self.assertEqual(used,row['packed_size'])
            self.assertGreater(row['remaining_slot_bytes'],0)
            self.assertFalse(any(p['after'][used:]))

    def test_no_pixel_change_outside_original_ink_boxes(self):
        for p,row in zip(self.patches,self.report['results']):
            before,_,_=b.decode(p['before']);after,_,_=b.decode(p['after'])
            self.assertEqual(before[:64],after[:64])
            self.assertEqual(before[65600:],after[65600:])
            a,palette=b.tim2(before);z,_=b.tim2(after)
            boxes=[l['original_ink_rect'] for l in row['labels']]
            for at,(x,y) in enumerate(zip(a,z)):
                if x!=y:
                    self.assertTrue(any(l<=at%256<r and t<=at//256<bt for l,t,r,bt in boxes))
                    self.assertIn(palette[y][3],(0,128))

    def test_protected_words_pending_terms_and_arrows_preserved(self):
        for p in self.patches:
            index=int(p['id'].rsplit('.',1)[1])
            raw,_,_=b.decode(p['before']);new,_,_=b.decode(p['after'])
            a,_=b.tim2(raw);z,_=b.tim2(new)
            boxes=[cell for _,text,cell in b.CELLS[index] if text is None]
            if index==1588:
                boxes.extend([(220,183,250,212),(208,213,238,242)])
            for l,t,r,bt in boxes:
                for yy in range(t,bt):
                    self.assertEqual(a[yy*256+l:yy*256+r],z[yy*256+l:yy*256+r])

    def test_old_translation_weapons_fonts_and_patches_unchanged(self):
        old,old_report=compile_draft(self.elf,self.parent)
        new,report=compile_draft(self.elf,self.recipe)
        self.assertEqual(new[:len(old)],old)
        self.assertEqual(new[len(old):],self.patches)
        self.assertEqual(report['accepted'],old_report['accepted']+34)
        self.assertEqual(report['item_names'],old_report['item_names'])
        self.assertEqual(report['approved_weapons'],old_report['approved_weapons'])

    def test_child_modifications_or_changed_binding_refused(self):
        for key,value in [('iso_name','bad.iso'),('status','bad'),('layout_profile','other')]:
            bad=copy.deepcopy(self.recipe);bad[key]=value
            with self.assertRaises(ValueError):b.validate_interface(bad)
        bad=copy.deepcopy(self.recipe);bad['battle_effect_release']['sha256']='0'*64
        with self.assertRaises(ValueError):b.validate_interface(bad)

    def test_changed_manifest_mask_rectangle_or_font_refused(self):
        for mutate in ('mask','rect','font','index'):
            bad=copy.deepcopy(self.manifest)
            if mutate=='mask':bad['entries'][0]['labels'][0]['mask_sha256']='0'*64
            elif mutate=='rect':bad['entries'][0]['labels'][0]['original_ink_rect'][0]-=1
            elif mutate=='index':bad['entries'][0]['index']=1589
            else:bad['font']['sha256']='0'*64
            with self.assertRaises(ValueError):b.compile_slots(self.elf,bad)

    def test_overflow_and_corrupt_compressor_output_refused(self):
        with patch.object(b,'_recompress',return_value=bytes(20000)):
            with self.assertRaisesRegex(ValueError,'exceeds original slot'):
                b.compile_slots(self.elf,self.manifest)
        with patch.object(b,'_recompress',return_value=bytes.fromhex('00000100')):
            with self.assertRaises(ValueError):b.compile_slots(self.elf,self.manifest)

    def test_word_raster_limit_and_reproduction(self):
        with self.assertRaises(ValueError):b.word_mask('Uma frase que não cabe',10,18)
        for row in self.report['results']:
            for label in row['labels']:
                l,t,r,bt=label['original_ink_rect']
                mask,info=b.word_mask(label['translation'],r-l,bt-t)
                self.assertEqual(b.sha(mask.tobytes()),label['mask_sha256'])
                self.assertGreaterEqual(info['horizontal_scale'],0.70)
                self.assertLessEqual(info['height_reduction'],2)

    def test_selector_revision_and_incomplete_cell_refused(self):
        bad=bytearray(self.elf);bad[0x109108]^=1
        with self.assertRaises(ValueError):b.instruction_bindings(bytes(bad))
        with self.assertRaises(ValueError):b.ink_bounds(bytes(65536),[(0,0,0,128)],(1,1,3,3))

    def test_comparator_requires_exact_parent(self):
        from verify_interface_revision import normalize_item_name_review_transition
        normalize_item_name_review_transition(self.parent,self.recipe,b.ROOT/b.PARENT,{}, {})
        with self.assertRaises(ValueError):
            normalize_item_name_review_transition(self.parent,self.recipe,b.ROOT/'translations/interface-v057.json',{}, {})


if __name__=='__main__':
    unittest.main()
