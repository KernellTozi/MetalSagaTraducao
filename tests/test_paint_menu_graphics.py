import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import paint_menu_graphics as p
from interface_text import SOURCE
from paint_captions import compile_captions


class PaintMenuGraphicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes();cls.raw,cls.manifest=p.inventory()
        cls.recipe=json.loads((ROOT/'translations/interface-v041.json').read_text(encoding='utf-8'))
        cls.config=cls.recipe['paint_menu_graphics'];cls.patches,cls.report=p.compile_graphics(cls.elf,cls.config)

    def test_only_six_explicit_user_reviewed_labels(self):
        self.assertEqual(self.report['accepted'],6)
        self.assertEqual([r['translation'] for r in self.report['results']],
            ['Editar','Veículo','Ferramentas','Escolher carimbo','Editar carimbo','Paleta'])
        approval=json.loads((ROOT/p.APPROVAL).read_text(encoding='utf-8'))
        self.assertTrue(approval['user_art_approved']);self.assertFalse(approval['runtime_visual_validation'])
        self.assertEqual([r['id'] for r in self.report['results']],approval['approved_art_ids'])

    def test_patch_is_only_the_original_texture_pixel_plane(self):
        self.assertEqual(len(self.patches),1);patch=self.patches[0]
        self.assertEqual((patch['offset'],len(patch['before']),len(patch['after'])),(0x34770,0x20000,0x20000))
        self.assertEqual(p.sha(patch['after']),p.PIXELS_SHA)
        r=bytearray(self.raw);r[patch['offset']:patch['offset']+len(patch['after'])]=patch['after']
        self.assertEqual(r[:0x34770],self.raw[:0x34770]);self.assertEqual(r[0x54770:],self.raw[0x54770:])

    def test_all_other_pixels_and_protected_labels_identical(self):
        row=next(r for r in self.manifest['entries'] if r['texture_entry']==13)
        at=row['texture_offset'];record=self.raw[at:at+row['texture_size']]
        patch=self.patches[0];after=record[:row['texture']['pixel_offset']]+patch['after']
        before_indices=p.unpack_indices(record,row['texture']);after_indices=p.unpack_indices(after,row['texture'])
        allowed=[r['rect'] for r in self.report['results']]
        for i,(a,b) in enumerate(zip(before_indices,after_indices)):
            if a!=b:self.assertTrue(any(x+2<=i%256<z-2 and y+2<=i//256<w-2 for x,y,z,w in allowed))
        for source in self.manifest['entries']:
            if source['texture_entry']!=13 or source['sprite_index'] in p.TARGETS:continue
            x,y,z,w=source['rect']
            for yy in range(y,w):self.assertEqual(before_indices[yy*256+x:yy*256+z],after_indices[yy*256+x:yy*256+z])

    def test_palette_alpha_reverse_roundtrip_and_228_caption_composition(self):
        captions,report=compile_captions(self.elf,self.recipe['paint_captions'],raw=self.raw)
        combined=bytearray(self.raw);all_patches=self.patches+captions
        self.assertEqual(report['accepted'],228)
        for patch in all_patches:
            a=patch['offset'];b=a+len(patch['before'])
            self.assertEqual(combined[a:b],patch['before']);combined[a:b]=patch['after']
        for patch in all_patches:self.assertEqual(combined[patch['offset']:patch['offset']+len(patch['after'])],patch['after'])
        for patch in reversed(all_patches):combined[patch['offset']:patch['offset']+len(patch['before'])]=patch['before']
        self.assertEqual(combined,self.raw)

    def test_recipe_source_geometry_mask_output_approval_mutations_refused(self):
        for key in ('policy','source_sha256','elf_sha256','target_pixel_sha256'):
            bad=copy.deepcopy(self.config);bad[key]='wrong'
            with self.assertRaises(ValueError):p.compile_graphics(self.elf,bad)
        for mutate in ('rect','text','mask','approval','duplicate','missing'):
            bad=copy.deepcopy(self.config)
            if mutate=='rect':bad['entries'][0]['rect'][0]+=1
            elif mutate=='text':bad['entries'][0]['translation']='Outro'
            elif mutate=='mask':bad['entries'][0]['mask_sha256']='0'*64
            elif mutate=='approval':bad['art_approval']['sha256']='0'*64
            elif mutate=='duplicate':bad['entries'].append(copy.deepcopy(bad['entries'][0]))
            else:bad['entries'].pop()
            with self.assertRaises(ValueError):p.compile_graphics(self.elf,bad)

    def test_original_elf_mutation_refused(self):
        elf=bytearray(self.elf);elf[0]^=1
        with self.assertRaises(ValueError):p.compile_graphics(elf,self.config)

    def test_v040_item_choices_and_every_other_field_preserved(self):
        old=json.loads((ROOT/'translations/interface-v040.json').read_text(encoding='utf-8'))
        new=self.recipe
        self.assertEqual({k:v for k,v in old.items() if k not in ('iso_name','status')},
            {k:v for k,v in new.items() if k not in ('iso_name','status','paint_menu_graphics')})
        self.assertEqual(new['item_names'],old['item_names']);self.assertEqual(new['item_name_review'],old['item_name_review'])
        self.assertEqual(new['layout_profile'],'ptbr-layout-v005')


if __name__=='__main__':unittest.main()
