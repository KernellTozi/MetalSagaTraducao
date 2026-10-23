import copy
import json
from pathlib import Path
import struct
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from interface_graphics import compile_graphics,catalog,original,RESOURCE,mask
from interface_texture_pack import unpack_indices,replace_indices
from interface_textures import inspect_texture
from probe_resources import nested


class GraphicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recipe=json.loads((ROOT/'translations/interface-graphics-v003.json').read_text(encoding='utf-8'))
        cls.raw=original(RESOURCE);cls.offsets=nested(cls.raw)[0]['offsets']
        cls.patches,cls.report=compile_graphics(cls.recipe)

    def test_all_forty_labels_bound_to_original_ganm(self):
        rows=catalog();self.assertEqual(len(rows),40)
        self.assertEqual({k:sum(r['family']==k for r in rows) for k in ('satcom','battle','header')},
                         {'satcom':26,'battle':10,'header':4})
        self.assertEqual(len(self.patches),3)
        for r in rows:
            at=self.offsets[r['ganm']]+16+16*r['ganm_index']
            self.assertEqual(tuple(r['rect']),struct.unpack_from('<4h',self.raw,at))
        targets={r['id']:r['translation'] for r in rows}
        self.assertEqual([targets[f'fbs.battle.{i:02d}'] for i in (3,4,5)],['MAIN','SUB','SE'])
        self.assertEqual(targets['fbs.header.09'],'Assunto')

    def test_only_authorized_inner_pixels_change_and_whole_resource_reverses(self):
        modified=bytearray(self.raw)
        for p in self.patches:
            self.assertEqual(p['before'],self.raw[p['offset']:p['offset']+len(p['before'])])
            self.assertEqual(len(p['before']),len(p['after']))
            modified[p['offset']:p['offset']+len(p['after'])]=p['after']
        for texture in (0,2,3):
            a,z=self.offsets[texture:texture+2];before=self.raw[a:z];after=bytes(modified[a:z]);meta,_=inspect_texture(before)
            start=meta['pixel_offset'];end=start+meta['pixel_bytes']
            self.assertEqual(before[:start],after[:start]);self.assertEqual(before[end:],after[end:])
            allowed=set()
            for r in self.report['results']:
                if r['texture']!=texture:continue
                x,y,u,v=r['inner_rect'];allowed.update(yy*meta['width']+xx for yy in range(y,v) for xx in range(x,u))
            old=unpack_indices(before,meta);new=unpack_indices(after,meta)
            changed={i for i,(p,q) in enumerate(zip(old,new)) if p!=q}
            self.assertTrue(changed);self.assertTrue(changed<=allowed)
            self.assertEqual(replace_indices(after,old),before)
        for p in self.patches:modified[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(modified,self.raw)

    def test_duplicates_drift_unknown_ids_and_unreviewed_labels_rejected(self):
        for case in ('duplicate','hash','unknown','label','source','rectangle'):
            d=copy.deepcopy(self.recipe)
            if case=='duplicate':d['entries'].append(d['entries'][0])
            elif case=='hash':d['entries'][0]['mask_sha256']='0'*64
            elif case=='unknown':d['entries'][0]['id']='fbs.satcom.28'
            elif case=='label':d['entries'][0]['translation']='A'*1000
            elif case=='rectangle':d['entries'][0]['rect']=[0,0,256,256]
            else:d['source_sha256']='0'*64
            with self.subTest(case=case),self.assertRaises(ValueError):compile_graphics(d)

    def test_render_guard_and_deterministic_native_glyph_masks(self):
        for text in ('çãé','MAIN','Munição'):
            a,ma=mask(text,16,74);b,mb=mask(text,16,74)
            self.assertEqual(a.tobytes(),b.tobytes());self.assertEqual(ma,mb)
            self.assertEqual(a.height,16)
        with self.assertRaises(ValueError):mask('A'*1000,16,40)
        with self.assertRaises(ValueError):mask('😀',16,40)

    def test_all_v005_text_preserved_and_graphic_recipe_hash_required(self):
        from interface_text import compile_draft,SOURCE
        old=json.loads((ROOT/'translations/interface-v005.json').read_text(encoding='utf-8'))
        new=json.loads((ROOT/'translations/interface-v006.json').read_text(encoding='utf-8'))
        for key in ('entries','resource_texts','base_dialogue_draft','layout_profile'):
            self.assertEqual(old[key],new[key])
        patches,report=compile_draft(SOURCE.read_bytes(),new)
        self.assertEqual(report['accepted'],613);self.assertEqual(report['graphic_labels']['accepted'],40)
        self.assertEqual(report['elf_strings'],278);self.assertEqual(len(patches),428)
        new['graphics']['sha256']='0'*64
        with self.assertRaises(ValueError):compile_draft(SOURCE.read_bytes(),new)


if __name__=='__main__':unittest.main()
