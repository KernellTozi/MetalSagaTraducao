import copy,json,struct,sys,unittest
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import title_menu_revision as t


class MenuRevisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from interface_text import SOURCE,compile_draft
        cls.elf=SOURCE.read_bytes();cls.parent=json.loads((t.ROOT/t.PARENT).read_bytes())
        cls.parents,cls.report=compile_draft(cls.elf,cls.parent)
        cls.child=json.loads((t.ROOT/t.CHILD).read_bytes());cls.manifest=json.loads((t.ROOT/t.MANIFEST).read_bytes())
        cls.revised,cls.new,cls.evidence=t.derive(cls.parents,t.word_pixels(cls.manifest['word']))

    def test_manifest_exact_and_child_scope(self):
        self.assertEqual(self.manifest['revised'],[t.metadata(p) for p in self.revised])
        self.assertEqual(self.manifest['new'],[t.metadata(p) for p in self.new])
        self.assertEqual(self.manifest['evidence'],self.evidence)
        self.assertEqual(len(self.revised),3);self.assertEqual(len(self.new),20)
        self.assertEqual(t.validate(self.child)[0],self.parent)

    def test_complete_word_palette_alpha_and_single_scale(self):
        Image=t.pillow();binding=self.manifest['word']
        with Image.open(t.WORD) as im:
            self.assertEqual(im.size,(228,24));self.assertEqual(im.mode,'P')
        self.assertEqual(binding['text'],'CARREGAR');self.assertEqual(binding['cap_height'],16)
        self.assertLessEqual(binding['rendered_size'][0],224)
        self.assertEqual(len(t.word_pixels(binding)),228*24)

    def test_credit_removed_from_load_sprite(self):
        p=next(p for p in self.revised if p['id']=='title.texture.0')
        old=next(p for p in self.parents if p['id']=='title.texture.0')
        self.assertEqual(p['after'][:128*256],old['after'][:128*256])
        self.assertFalse(any(p['after'][152*256:]))
        for y in range(24):self.assertEqual(p['after'][(128+y)*256+14:(128+y)*256+242],t.word_pixels(self.manifest['word'])[y*228:(y+1)*228])

    def test_load_frame_only_and_anchor_preserved(self):
        p=next(p for p in self.revised if p['id']=='title.frames');old=next(q for q in self.parents if q['id']==p['id'])
        self.assertEqual(p['after'][:16],old['after'][:16]);self.assertEqual(p['after'][32:],old['after'][32:])
        self.assertEqual(struct.unpack_from('<8h',p['after'],16),(14,128,242,152,114,12,0,0))

    def test_vendas_only_right_cell(self):
        p=next(p for p in self.revised if p['id']=='observed.headers');old=next(q for q in self.parents if q['id']==p['id'])
        for i,(a,b) in enumerate(zip(old['after'],p['after'])):
            if a!=b:self.assertTrue(120<=i%256<256 and 144<=i//256<156)
        self.assertEqual(self.evidence['sales']['translation'],'VENDAS')
        self.assertFalse(self.evidence['sales']['resized'])

    def patched_resource(self,name):
        raw=t.original(name);out=bytearray(raw)
        for p in self.new:
            if p['resource']==name:
                self.assertEqual(p['before'],raw[p['offset']:p['offset']+len(p['before'])])
                self.assertEqual(len(p['before']),len(p['after']))
                out[p['offset']:p['offset']+len(p['after'])]=p['after']
        return raw,bytes(out)

    def test_official_three_lines_preserved_pixel_for_pixel(self):
        old,new=self.patched_resource(t.TEXTURE)
        a=0x40430;meta,_=t.inspect_texture(old[a:a+263184])
        x=t.unpack_indices(old[a:a+263184],meta);y=t.unpack_indices(new[a:a+263184],meta)
        for line in range(40):self.assertEqual(x[(298+line)*512+275:(298+line)*512+510],y[(284+line)*512+275:(284+line)*512+510])
        self.assertNotEqual(x[325*512+275:338*512],y[325*512+275:338*512])

    def test_fade_swatch_lossless_and_all_uv_keys_translated(self):
        old,new=self.patched_resource(t.TEXTURE);a=0x40430;meta,_=t.inspect_texture(old[a:a+263184])
        x=t.unpack_indices(old[a:a+263184],meta);y=t.unpack_indices(new[a:a+263184],meta)
        for line in range(8):self.assertEqual(x[(290+line)*512+320:(290+line)*512+336],y[(480+line)*512+480:(480+line)*512+496])
        before,after=self.patched_resource(t.SCENE)
        refs=self.evidence['credit']['fade_uv_references'];self.assertEqual(len(refs),12)
        for at in refs:
            u,v=struct.unpack_from('<2f',before,at);a,b=struct.unpack_from('<2f',after,at)
            self.assertEqual((a-u,b-v),(160/512,190/512))

    def test_quad_expansion_keeps_top_and_original_scales(self):
        old,new=self.patched_resource(t.SCENE)
        self.assertEqual(struct.unpack_from('<2f',new,0xdb0),(275/512,284/512))
        self.assertEqual(struct.unpack_from('<2f',new,0xde8),(510/512,338/512))
        self.assertEqual(176-19,183-26);self.assertEqual(176+20+14,183+27)
        self.assertEqual(struct.unpack_from('<h',new,0xce2)[0],54)
        self.assertEqual(self.evidence['credit']['screen_top_before_after'],[381,381])

    def test_unrelated_atlas_pixels_and_palettes_unchanged(self):
        old,new=self.patched_resource(t.TEXTURE);a=0x40430;meta,_=t.inspect_texture(old[a:a+263184])
        self.assertEqual(old[:a+1040],new[:a+1040])
        x=t.unpack_indices(old[a:a+263184],meta);y=t.unpack_indices(new[a:a+263184],meta)
        for i,(m,n) in enumerate(zip(x,y)):
            if m!=n:self.assertTrue((275<=i%512<510 and 284<=i//512<338) or (480<=i%512<496 and 480<=i//512<488))
        self.assertEqual(old[a+263184:],new[a+263184:])

    def test_all_new_changes_reverse_roundtrip(self):
        for resource in (t.TEXTURE,t.SCENE):
            old,new=self.patched_resource(resource);out=bytearray(new)
            for p in self.new:
                if p['resource']==resource:out[p['offset']:p['offset']+len(p['before'])]=p['before']
            self.assertEqual(bytes(out),old)

    def test_new_patches_no_overlap(self):
        rows=self.revised+self.new
        for i,a in enumerate(rows):
            for b in rows[i+1:]:
                if a['resource']==b['resource']:self.assertFalse(max(a['offset'],b['offset'])<min(a['offset']+len(a['before']),b['offset']+len(b['before'])))

    def test_merge_preserves_items_ore_and_all_other_patches(self):
        with patch('interface_text.compile_draft',return_value=(copy.deepcopy(self.parents),copy.deepcopy(self.report))):
            rows,report=t.compile_interface(self.elf,self.child)
        by={p['id']:p for p in rows};revised={p['id'] for p in self.revised}
        for p in self.parents:
            if p['id'] not in revised:self.assertEqual(p,by[p['id']])
        self.assertEqual(report['accepted'],4363);self.assertEqual(report['item_names'],self.report['item_names'])
        self.assertEqual(report['graphic_labels']['reviewed_artwork']['credit']['text'],t.TEXT)
        self.assertFalse(report['graphic_labels']['reviewed_artwork']['credit']['inherits_button_tint'])

    def test_recipe_tampering_rejected(self):
        for field,value in (('layout_profile','bad'),('base_dialogue_draft','bad'),('status','bad')):
            bad=copy.deepcopy(self.child);bad[field]=value
            with self.assertRaises(ValueError):t.validate(bad)
        bad=copy.deepcopy(self.child);bad['title_menu_release']['sha256']='0'*64
        with self.assertRaises(ValueError):t.validate(bad)

    def test_comparator_requires_exact_parent(self):
        from verify_interface_revision import normalize_item_name_review_transition
        normalize_item_name_review_transition(self.parent,self.child,t.ROOT/t.PARENT,{}, {})
        with self.assertRaises(ValueError):normalize_item_name_review_transition(self.parent,self.child,t.ROOT/'translations/interface-v062.json',{}, {})


if __name__=='__main__':unittest.main()
