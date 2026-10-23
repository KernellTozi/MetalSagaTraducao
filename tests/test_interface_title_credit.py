import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from title_credit import artwork,compile_credit,FRAMES,TEXT
from title_native_font import alphabet,RESOURCE
from interface_graphics import original,compile_graphics
from interface_texture_pack import pillow,unpack_indices
from interface_textures import inspect_texture


class CreditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=json.loads((ROOT/'translations/interface-graphics-v007.json').read_text(encoding='utf-8'))

    def test_only_r_changes_native_alphabet_and_counters_remain_open(self):
        old,new=alphabet(),alphabet(True)
        for char in old:
            if char!='R':self.assertEqual((old[char].size,old[char].tobytes()),(new[char].size,new[char].tobytes()))
        self.assertNotEqual(old['R'].tobytes(),new['R'].tobytes())
        self.assertEqual(new['R'].height,old['R'].height)
        self.assertEqual(new['R'].getpixel((12,9)),0)
        self.assertEqual(new['R'].getpixel((12,18)),0)

    def test_all_six_frames_disjoint_and_old_background_fade_exact(self):
        Image=pillow();before=original(RESOURCE);after,review=artwork()
        self.assertEqual(len(before),len(after));self.assertEqual(before[:1072],after[:1072])
        self.assertEqual(before[66608:66624],after[66608:66624])
        old=Image.frombytes('L',(256,256),unpack_indices(before[32:66608],inspect_texture(before[32:66608])[0]))
        new=Image.frombytes('L',(256,256),unpack_indices(after[32:66608],inspect_texture(after[32:66608])[0]))
        for index,rect in ((3,(1,74,6,78)),(4,(0,96,228,136)),(5,(0,136,228,176))):
            self.assertEqual(old.crop(rect).tobytes(),new.crop(FRAMES[index][:4]).tobytes())
        self.assertFalse(any(new.crop((0,152,256,240)).tobytes()))
        for i,a in enumerate(FRAMES):
            self.assertTrue(0<=a[0]<a[2]<=256 and 0<=a[1]<a[3]<=256)
            for b in FRAMES[i+1:]:
                self.assertFalse(max(a[0],b[0])<min(a[2],b[2]) and max(a[1],b[1])<min(a[3],b[3]))

    def test_credit_text_virtual_bounds_and_tint_limit_are_explicit(self):
        _,review=artwork();credit=review['credit']
        self.assertEqual(credit['text'],TEXT)
        x,y,z,w=credit['screen_rect']
        self.assertEqual((x+z)//2,320)
        self.assertEqual((y,w),(430,444));self.assertLessEqual(w,448)
        self.assertTrue(credit['inherits_continue_tint_and_visibility'])
        self.assertEqual(credit['layout']['horizontal_scale'],1)

    def test_prior_non_title_patches_identical_and_title_roundtrip(self):
        parent=json.loads((ROOT/'translations/interface-graphics-v006.json').read_text(encoding='utf-8'))
        old,_=compile_graphics(parent);new,report=compile_credit(self.config)
        self.assertEqual([p for p in old if p['resource']!=RESOURCE], [p for p in new if p['resource']!=RESOURCE])
        self.assertEqual(report['accepted'],44)
        data=bytearray(original(RESOURCE))
        for p in new:
            if p['resource']==RESOURCE:data[p['offset']:p['offset']+len(p['after'])]=p['after']
        self.assertEqual(data,artwork()[0])
        for p in new:
            if p['resource']==RESOURCE:data[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(data,original(RESOURCE))

    def test_unreviewed_frames_credit_masks_source_and_parent_blocked(self):
        for case in ('frame','text','mask','source','parent'):
            c=copy.deepcopy(self.config)
            if case=='frame':c['reviewed_artwork']['frames'][1][3]-=1
            elif case=='text':c['reviewed_artwork']['credit']['text']='Outro nome'
            elif case=='mask':c['reviewed_artwork']['credit']['mask_sha256']='0'*64
            elif case=='source':c['source_sha256']='0'*64
            else:c['parent']['recipe']='translations/interface-graphics-v005.json'
            with self.subTest(case=case),self.assertRaises(ValueError):compile_credit(c)

    def test_ui_texts_and_layout_preserved(self):
        old=json.loads((ROOT/'translations/interface-v010.json').read_text(encoding='utf-8'))
        new=json.loads((ROOT/'translations/interface-v011.json').read_text(encoding='utf-8'))
        for k in set(old)-{'graphics','status','iso_name'}:self.assertEqual(old[k],new[k],k)


if __name__=='__main__':unittest.main()
