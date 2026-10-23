import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from interface_graphics import compile_graphics,original,RESOURCE,catalog
from interface_texture_pack import unpack_indices,replace_indices
from interface_textures import inspect_texture
from satcom_native_font import alphabet,mask


class NativeTypefaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=json.loads((ROOT/'translations/interface-graphics-v004.json').read_text(encoding='utf-8'))
        cls.old=json.loads((ROOT/'translations/interface-graphics-v003.json').read_text(encoding='utf-8'))
        cls.patches,cls.report=compile_graphics(cls.config)

    def test_only_satcom_texture_revised_and_all_other_graphics_preserved(self):
        previous,_=compile_graphics(self.old)
        self.assertEqual(self.report['accepted'],40);self.assertEqual(self.report['revised_labels'],26)
        self.assertEqual(self.report['unchanged_other_graphic_labels'],14)
        old={p['id']:p for p in previous};new={p['id']:p for p in self.patches}
        self.assertEqual(set(old),set(new))
        for key in old:
            if key!='fbs.texture.3':self.assertEqual(old[key],new[key])
            else:
                self.assertEqual(old[key]['before'],new[key]['before'])
                self.assertNotEqual(old[key]['after'],new[key]['after'])

    def test_remote_borders_and_disabled_labels_remain_original(self):
        raw=original(RESOURCE);before=raw[0x30c70:0x38cc0];p=next(p for p in self.patches if p['id']=='fbs.texture.3')
        after=before[:80]+p['after'];meta,_=inspect_texture(before)
        old=unpack_indices(before,meta);new=unpack_indices(after,meta);allowed=set()
        for row in self.report['results']:
            if row['texture']!=3:continue
            x,y,z,w=row['inner_rect'];allowed.update(yy*256+xx for yy in range(y,w) for xx in range(x,z))
        self.assertTrue({i for i,(a,b) in enumerate(zip(old,new)) if a!=b}<=allowed)
        # Remote selected/normal and both crossed unavailable labels.
        for x,y,z,w in [(0,24,80,48),(80,72,160,96),(160,192,240,216),(160,216,240,240)]:
            for yy in range(y,w):self.assertEqual(old[yy*256+x:yy*256+z],new[yy*256+x:yy*256+z])
        self.assertEqual(replace_indices(after,old),before)

    def test_native_glyph_body_size_accents_and_no_resizing(self):
        for boxed in (False,True):
            letters=alphabet(boxed)
            for char,base in (('á','a'),('ú','u')):
                self.assertEqual(letters[char].crop((0,6,letters[char].width,18)).tobytes(),
                                 letters[base].crop((0,6,letters[base].width,18)).tobytes())
            with patch('PIL.Image.Image.resize',side_effect=AssertionError('native glyph scaling forbidden')):
                for word in ('Procurados','Mensagens','Música','Diário','Ajuda'):
                    im,layout=mask(word,74,boxed)
                    self.assertEqual(im.height,18);self.assertLessEqual(im.width,74)
                    self.assertEqual(layout['horizontal_scale'],1);self.assertEqual(layout['capital_body_pixels'],12)
        with self.assertRaises(ValueError):mask('Procurados'*10,74)
        with self.assertRaises(ValueError):mask('X',74)

    def test_source_scope_mask_binding_and_translation_mutations_rejected(self):
        for case in ('base','source','mask','scope','label','duplicate'):
            d=copy.deepcopy(self.config)
            if case=='base':d['base_recipe_sha256']='0'*64
            elif case=='source':d['source_sha256']='0'*64
            elif case=='mask':d['entries'][0]['mask_sha256']='0'*64
            elif case=='scope':d['entries'].pop()
            elif case=='label':d['entries'][0]['translation']='Other'
            else:d['entries'][-1]=d['entries'][0]
            with self.subTest(case=case),self.assertRaises(ValueError):compile_graphics(d)

    def test_v006_text_and_counts_unchanged(self):
        from interface_text import SOURCE,compile_draft
        old=json.loads((ROOT/'translations/interface-v006.json').read_text(encoding='utf-8'))
        new=json.loads((ROOT/'translations/interface-v007.json').read_text(encoding='utf-8'))
        for key in ('entries','resource_texts','base_dialogue_draft','layout_profile'):self.assertEqual(old[key],new[key])
        patches,report=compile_draft(SOURCE.read_bytes(),new)
        self.assertEqual(report['accepted'],613);self.assertEqual(len(patches),428)


if __name__=='__main__':unittest.main()
