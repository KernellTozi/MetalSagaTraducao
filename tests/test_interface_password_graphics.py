import copy,json,struct,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from password_graphics import *
from interface_text import SOURCE


class PasswordGraphics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes();cls.raw=original(RESOURCE)
        cls.config=json.loads((ROOT/'translations/interface-v029.json').read_text(encoding='utf-8'))['password_graphics']
        cls.patches,cls.report=compile_graphics(cls.elf,cls.config)
    def test_three_labels_and_exact_palette_header_extent_preserved(self):
        self.assertEqual(self.report['accepted'],3)
        p=self.patches[0];self.assertEqual(p['offset'],START);self.assertEqual(p['resource'],RESOURCE)
        self.assertEqual(len(p['before']),SIZE);self.assertEqual(len(p['after']),SIZE)
        self.assertEqual(p['after'][:1040],p['before'][:1040])
        self.assertEqual([r['translation'] for r in self.report['results']],['DESTRAVAR','TRAVAR','SAIR'])
    def test_pixels_change_only_in_original_three_ganm_rectangles(self):
        p=self.patches[0];meta,_=inspect_texture(p['before'])
        a=unpack_indices(p['before'],meta);b=unpack_indices(p['after'],meta);changed=[]
        for i,(old,new) in enumerate(zip(a,b)):
            if old==new:continue
            self.assertTrue(any(x<=i%256<z and y<=i//256<w for _,_,(x,y,z,w) in LABELS));changed.append(i)
        self.assertGreater(len(changed),500)
        self.assertEqual(replace_indices(p['before'],a),p['before'])
        self.assertEqual(replace_indices(p['after'],b),p['after'])
    def test_resource_roundtrip_keeps_all_other_textures_and_sprite_records(self):
        p=self.patches[0];out=bytearray(self.raw);out[START:START+SIZE]=p['after']
        self.assertEqual(out[:START],self.raw[:START]);self.assertEqual(out[START+SIZE:],self.raw[START+SIZE:])
        out[START:START+SIZE]=p['before'];self.assertEqual(out,self.raw)
    def test_original_upload_and_all_fifteen_draw_arguments(self):
        r=probes(self.elf)
        self.assertEqual(r['logical_key_to_sprite'],list(range(4,16))+[18,1,0])
        self.assertEqual(r['action_keys'],{'unlock':12,'lock':13,'exit':14})
        self.assertEqual((r['texture_upload_cases'],r['label_draw_cases']),(1,15))
    def test_unknown_config_bad_hash_and_code_binding_refused(self):
        for kind in ('source','code','extra','policy'):
            c=copy.deepcopy(self.config)
            if kind=='source':c['source_sha256']='0'*64
            elif kind=='code':c['instruction_windows'][0]['sha256']='0'*64
            elif kind=='extra':c['extra_sprite']=4
            else:c['policy']='unknown'
            with self.subTest(kind=kind),self.assertRaises(ValueError):compile_graphics(self.elf,c)
        from unittest.mock import patch
        with patch('password_graphics.render',return_value=(self.patches[0]['before'],[])),self.assertRaises(ValueError):
            compile_graphics(self.elf,self.config)
    def test_sprite_palette_or_format_drift_refused(self):
        for at in (GANM+16+18*16,START+16+3,START+16+4+3):
            raw=bytearray(self.raw);raw[at]^=1
            with self.subTest(at=at),self.assertRaises(ValueError):render(raw)
    def test_baseline_height_and_bounded_compression(self):
        for row in self.report['results']:
            self.assertEqual(row['layout']['height'],20)
            self.assertGreaterEqual(row['layout']['horizontal_scale'],.94)
            self.assertLessEqual(row['layout']['rendered_width'],94)
    def test_reproducible_local_preview_without_iso(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-password-preview-') as folder:
            path=Path(folder)/'comparison.png';r=preview(path)
            self.assertTrue(path.is_file());self.assertEqual(r['target_texture_sha256'],self.report['target_texture_sha256'])
            with self.assertRaises((ValueError,FileExistsError)):preview(path)

if __name__=='__main__':unittest.main()
