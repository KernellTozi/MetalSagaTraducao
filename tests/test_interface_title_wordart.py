import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from interface_graphics import compile_graphics
from title_wordart import compile_wordart

class AppliedWordArt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg=json.loads((ROOT/'translations/interface-graphics-v010.json').read_text(encoding='utf-8'))
        cls.parent=json.loads((ROOT/cls.cfg['parent']['recipe']).read_text(encoding='utf-8'))
        cls.old,cls.old_report=compile_graphics(cls.parent);cls.new,cls.report=compile_wordart(cls.cfg)
    def test_exactly_one_pixel_patch_changes(self):
        self.assertEqual(len(self.old),len(self.new));changed=[]
        for a,b in zip(self.old,self.new):
            if a!=b:changed.append((a,b))
        self.assertEqual(len(changed),1);a,b=changed[0]
        self.assertEqual(a['resource'],'DATA/RDATA/RTITLE.SDA');self.assertEqual(a['id'],'title.texture.0')
        self.assertEqual(a['before'],b['before']);self.assertEqual(len(a['after']),len(b['after']))
        for i,(x,y) in enumerate(zip(a['after'],b['after'])):
            if x!=y:self.assertTrue((i%256<228 and i//256<48) or 128<=i//256<152)
    def test_approved_indices_transported_exactly(self):
        from interface_texture_pack import pillow
        Image=pillow();patch=next(p for p in self.new if p['id']=='title.texture.0')
        for i,binding in enumerate(self.cfg['words']):
            with Image.open(ROOT/binding['path']) as im:expected=im.tobytes()
            y0=(0,128,24)[i];x0=14 if i==1 else 0
            actual=b''.join(patch['after'][(y0+y)*256+x0:(y0+y)*256+x0+228] for y in range(24))
            self.assertEqual(expected,actual)

    def test_credit_geometry_and_counts_preserved(self):
        self.assertEqual(self.report['accepted'],self.old_report['accepted'])
        self.assertEqual(self.report['reviewed_artwork']['credit'],self.old_report['reviewed_artwork']['credit'])
        self.assertEqual(self.report['reviewed_artwork']['frames'],self.old_report['reviewed_artwork']['frames'])
        self.assertTrue(self.report['reverse_roundtrip'])
    def test_asset_hash_order_and_parent_drift_blocked(self):
        for field in ('file_sha256','indices_sha256'):
            bad=copy.deepcopy(self.cfg);bad['words'][0][field]='0'*64
            with self.assertRaises(ValueError):compile_wordart(bad)
        bad=copy.deepcopy(self.cfg);bad['words'].reverse()
        with self.assertRaises(ValueError):compile_wordart(bad)
        bad=copy.deepcopy(self.cfg);bad['parent']['sha256']='0'*64
        with self.assertRaises(ValueError):compile_wordart(bad)
    def test_all_other_interface_fields_unchanged(self):
        a=json.loads((ROOT/'translations/interface-v013.json').read_text(encoding='utf-8'))
        b=json.loads((ROOT/'translations/interface-v014.json').read_text(encoding='utf-8'))
        for k in set(a)-{'graphics','status','iso_name'}:self.assertEqual(a[k],b[k],k)

if __name__=='__main__':unittest.main()
