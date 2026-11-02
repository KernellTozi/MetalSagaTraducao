import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import credit_readability as c


class CreditReadabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from interface_text import SOURCE,compile_draft
        cls.elf=SOURCE.read_bytes();cls.parent=json.loads((c.ROOT/c.PARENT).read_bytes())
        cls.parents,cls.report=compile_draft(cls.elf,cls.parent)
        cls.old=next(p for p in cls.parents if p['id']=='title.official-block-credit')
        cls.new,cls.review=c.revised_patch(cls.old)
        cls.child=json.loads((c.ROOT/c.CHILD).read_bytes());cls.manifest=json.loads((c.ROOT/c.MANIFEST).read_bytes())

    def test_manifest_exact_and_parent_bound(self):
        self.assertEqual(self.manifest['patch'],c.metadata(self.old))
        self.assertEqual(self.manifest['review'],self.review)
        self.assertEqual(self.manifest['after_sha256'],c.sha(self.new['after']))
        self.assertEqual(c.validate(self.child)[0],self.parent)

    def test_credit_only_existing_strip_no_size_change(self):
        self.assertEqual(self.old['before'],self.new['before'])
        self.assertEqual(len(self.new['after']),len(self.old['after']))
        for i,(a,b) in enumerate(zip(self.old['after'],self.new['after'])):
            if a!=b:
                absolute=284*512+275+i
                self.assertTrue(275<=absolute%512<510 and 323<=absolute//512<338)
        self.assertNotEqual(self.old['after'],self.new['after'])

    def test_official_three_lines_and_their_outline_unchanged(self):
        raw=c.original(c.TEXTURE)[0x40430:0x40430+263184];meta,_=c.inspect_texture(raw)
        pixels=c.unpack_indices(raw,meta);palette=[tuple(raw[16+i*4:20+i*4]) for i in range(256)]
        for y in range(40):
            for x in range(235):
                value=pixels[(298+y)*512+275+x]
                if palette[value][3]:self.assertEqual(self.new['after'][y*512+x],value)
        self.assertEqual(self.old['after'][:39*512],self.new['after'][:39*512])

    def test_e_counter_and_right_aperture_remain_open(self):
        rows=self.review['e_bitmap'];w=len(rows[0]);h=len(rows)
        black={(x,y) for y,r in enumerate(rows) for x,v in enumerate(r) if v=='.'}
        exterior={p for p in black if p[0] in (0,w-1) or p[1] in (0,h-1)};todo=list(exterior)
        while todo:
            x,y=todo.pop()
            for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if p in black and p not in exterior:exterior.add(p);todo.append(p)
        self.assertGreaterEqual(len(black-exterior),3)  # readable upper bowl
        self.assertTrue(any(r.endswith('...') for r in rows[3:]))
        self.assertGreaterEqual(h,7)

    def test_native_raster_integer_origins_no_resizing_or_clipping(self):
        ink,review=c.raster();self.assertEqual(ink.size,(129,15));self.assertEqual(review['body_size'],12)
        self.assertEqual(review['text'],'tradução: Kernell Tozi')
        self.assertTrue(all(type(p['x']) is int and type(p['advance']) is int for p in review['placements']))
        self.assertLessEqual(ink.getbbox()[3],14);self.assertGreaterEqual(ink.getbbox()[1],1)
        self.assertEqual(set(ink.tobytes()),{0,255})

    def test_credit_palette_uses_original_white_black_transparency(self):
        raw=c.original(c.TEXTURE)[0x40430:0x40430+263184]
        palette=[tuple(raw[16+i*4:20+i*4]) for i in range(256)]
        colors={palette[self.new['after'][(y-284)*512+x]] for y in range(323,338) for x in range(235)}
        self.assertEqual(colors,{(0,0,0,0),(0,0,0,127),(255,255,255,127)})

    def test_merge_preserves_every_other_patch_and_all_counts(self):
        from interface_text import compile_draft
        with patch('interface_text.compile_draft',return_value=(copy.deepcopy(self.parents),copy.deepcopy(self.report))):
            rows,report=c.compile_interface(self.elf,self.child)
        changed=[(a,b) for a,b in zip(self.parents,rows) if a!=b]
        self.assertEqual(len(changed),1);self.assertEqual(changed[0][0]['id'],self.old['id'])
        self.assertEqual(report['accepted'],self.report['accepted']);self.assertEqual(report['item_names'],self.report['item_names'])
        self.assertEqual(report['graphic_labels']['reviewed_artwork']['credit']['ink_width'],129)

    def test_child_tampering_rejected(self):
        bad=copy.deepcopy(self.child);bad['layout_profile']='bad'
        with self.assertRaises(ValueError):c.validate(bad)
        bad=copy.deepcopy(self.child);bad['credit_readability_release']['sha256']='0'*64
        with self.assertRaises(ValueError):c.validate(bad)

    def test_comparator_requires_exact_parent(self):
        from verify_interface_revision import normalize_item_name_review_transition
        normalize_item_name_review_transition(self.parent,self.child,c.ROOT/c.PARENT,{}, {})
        with self.assertRaises(ValueError):normalize_item_name_review_transition(self.parent,self.child,c.ROOT/'translations/interface-v063.json',{}, {})


if __name__=='__main__':unittest.main()
