import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import battle_menu_atlas as b
from interface_text import SOURCE,compile_draft


class BattleAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes()
        cls.recipe=json.loads((b.ROOT/'translations/interface-v055.json').read_bytes())
        cls.parent,cls.manifest=b.validate_interface(cls.recipe)
        cls.patches,cls.report=b.compile_slots(cls.elf,cls.manifest)

    def test_exact_two_existing_extents_original_decoder(self):
        self.assertEqual([p['id'] for p in self.patches],['battle.tim2.1589','battle.tim2.1594'])
        self.assertEqual([p['offset'] for p in self.patches],[321460224,321573888])
        self.assertEqual(self.report['accepted'],14)
        self.assertTrue(self.report['original_decoder_roundtrip'])
        for p in self.patches:
            self.assertEqual(len(p['before']),len(p['after']))
            after,used,_=b.decode(p['after'])
            self.assertEqual(len(after),66624)
            self.assertFalse(any(p['after'][used:]))

    def test_only_letter_interiors_palette_header_and_icons_preserved(self):
        for p in self.patches:
            index=int(p['id'].rsplit('.',1)[1])
            before,_,_=b.decode(p['before']);after,_,_=b.decode(p['after'])
            self.assertEqual(before[:64],after[:64]);self.assertEqual(before[65600:],after[65600:])
            a,_=b.tim2(before);z,_=b.tim2(after)
            for at,(x,y) in enumerate(zip(a,z)):
                if x!=y:
                    self.assertTrue(any(l<=at%256<r and t<=at//256<bt for _,_,(l,t,r,bt),_,_,_ in b.LABELS[index]))
            if index==1589:
                # MAIN/SUB/SE and Item are copied pixel for pixel.
                for l,t,r,bt in [(36,104,84,128),(92,104,140,128),(148,104,196,128),(36,168,84,192)]:
                    for row in range(t,bt):self.assertEqual(a[row*256+l:row*256+r],z[row*256+l:row*256+r])

    def test_parent_all_prior_text_fonts_names_patches_identical(self):
        old,old_report=compile_draft(self.elf,self.parent)
        new,report=compile_draft(self.elf,self.recipe)
        self.assertEqual(new[:len(old)],old)
        self.assertEqual(new[len(old):],self.patches)
        self.assertEqual(report['accepted'],old_report['accepted']+14)
        self.assertEqual(report['item_names'],old_report['item_names'])

    def test_foreign_interface_mutation_and_bad_binding_refused(self):
        for key,value in [('layout_profile','other'),('iso_name','bad.iso'),('base_dialogue_draft','bad')]:
            bad=copy.deepcopy(self.recipe);bad[key]=value
            with self.assertRaises(ValueError):b.validate_interface(bad)
        bad=copy.deepcopy(self.recipe);bad['battle_atlas_release']['sha256']='0'*64
        with self.assertRaises(ValueError):b.validate_interface(bad)

    def test_changed_rect_source_or_mask_refused(self):
        for mutate in ('rect','mask','offset'):
            bad=copy.deepcopy(self.manifest)
            if mutate=='rect':bad['entries'][0]['labels'][0]['rect'][0]-=1
            elif mutate=='mask':bad['entries'][0]['labels'][0]['mask_sha256']='0'*64
            else:bad['entries'][0]['offset']+=1
            with self.assertRaises(ValueError):b.compile_slots(self.elf,bad)

    def test_compressed_overflow_refused_without_partial_result(self):
        with patch.object(b,'_recompress',return_value=bytes(40000)):
            with self.assertRaisesRegex(ValueError,'exceeds original slot'):b.compile_slots(self.elf,self.manifest)

    def test_foreign_tim2_and_modified_elf_refused(self):
        with self.assertRaises(ValueError):b.tim2(bytes(66624))
        bad=bytearray(self.elf);bad[0x109180]^=1
        with self.assertRaises(ValueError):b.instruction_bindings(bytes(bad))

    def test_comparator_accepts_only_exact_parent(self):
        from verify_interface_revision import normalize_item_name_review_transition
        normalize_item_name_review_transition(self.parent,self.recipe,b.ROOT/b.PARENT,{}, {})
        with self.assertRaises(ValueError):
            normalize_item_name_review_transition(self.parent,self.recipe,b.ROOT/'translations/interface-v053.json',{}, {})


if __name__=='__main__':unittest.main()
