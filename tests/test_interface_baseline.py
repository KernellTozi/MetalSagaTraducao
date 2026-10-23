import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from satcom_native_font import alphabet,mask,SAMPLES,ALIGNED_POLICY
from interface_graphics import compile_graphics,original,RESOURCE


def core(im):return im.point(lambda p:255 if p>=160 else 0)


class BaselineTests(unittest.TestCase):
    def test_every_body_matches_remote_baseline_in_both_variants(self):
        for boxed in (False,True):
            glyphs=alphabet(boxed,True)
            self.assertEqual(core(glyphs['R']).getbbox()[1::2],(3,15))
            for char,im in glyphs.items():
                body=core(im).crop((0,6,im.width,15))
                with self.subTest(boxed=boxed,char=char):
                    self.assertEqual(body.getbbox()[3],9)
                    self.assertEqual(core(im).getbbox()[3],18 if char in 'gjç' else 15)
            for char in 'RMACDHLJP':self.assertEqual(core(glyphs[char]).getbbox()[1],3)
            for char in 'emonuascrg':self.assertEqual(core(glyphs[char]).getbbox()[1],7)

    def test_recovered_shapes_widths_and_solid_pixels_are_only_translated(self):
        for boxed in (False,True):
            previous=alphabet(boxed,False);current=alphabet(boxed,True)
            for char in SAMPLES:
                a=core(previous[char]);b=core(current[char])
                self.assertEqual(a.size,b.size)
                self.assertEqual(a.crop(a.getbbox()).tobytes(),b.crop(b.getbbox()).tobytes(),char)
            if not boxed:
                for char in previous:self.assertEqual(previous[char].tobytes(),current[char].tobytes())
        with patch('PIL.Image.Image.resize',side_effect=AssertionError('no scaling')):
            for boxed in (False,True):
                for word in ('Procurados','Mensagens','Diário','Música'):
                    im,r=mask(word,74,boxed,True);self.assertEqual(r['horizontal_scale'],1)

    def test_only_satcom_pixel_patch_changes_against_v007(self):
        old=json.loads((ROOT/'translations/interface-graphics-v004.json').read_text(encoding='utf-8'))
        new=json.loads((ROOT/'translations/interface-graphics-v005.json').read_text(encoding='utf-8'))
        previous,_=compile_graphics(old);current,r=compile_graphics(new)
        a={p['id']:p for p in previous};b={p['id']:p for p in current}
        self.assertEqual(set(a),set(b))
        self.assertEqual([k for k in a if a[k]!=b[k]],['fbs.texture.3'])
        self.assertEqual(r['baseline_pixel'],15);self.assertEqual(r['policy'],ALIGNED_POLICY)

    def test_previous_mask_hash_cannot_silently_pass_aligned_policy(self):
        old=json.loads((ROOT/'translations/interface-graphics-v004.json').read_text(encoding='utf-8'))
        old['policy']=ALIGNED_POLICY
        with self.assertRaises(ValueError):compile_graphics(old)

    def test_all_v007_text_and_metrics_unchanged(self):
        from interface_text import SOURCE,compile_draft
        old=json.loads((ROOT/'translations/interface-v007.json').read_text(encoding='utf-8'))
        new=json.loads((ROOT/'translations/interface-v008.json').read_text(encoding='utf-8'))
        for key in ('entries','resource_texts','base_dialogue_draft','layout_profile'):self.assertEqual(old[key],new[key])
        patches,r=compile_draft(SOURCE.read_bytes(),new)
        self.assertEqual(r['accepted'],613);self.assertEqual(len(patches),428)


if __name__=='__main__':unittest.main()
