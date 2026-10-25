import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from name_finish_graphics import *
from interface_text import SOURCE


class NameFinish(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes();cls.raw=original(RESOURCE)
        cls.config=json.loads((ROOT/'translations/interface-v030.json').read_text(encoding='utf-8'))['name_finish_graphics']
        cls.patches,cls.report=compile_graphics(cls.elf,cls.config)
    def test_header_palette_tail_and_pinned_raster(self):
        p=self.patches[0];self.assertEqual(self.report['accepted'],2)
        self.assertEqual(p['after'][:1040],p['before'][:1040])
        self.assertEqual(p['after'][-48:],p['before'][-48:])
        self.assertEqual(len(p['after']),SIZE);self.assertEqual(sha(p['after']),TARGET_SHA)
        for r in self.report['results']:
            self.assertEqual(r['translation'],'FIM');self.assertEqual(r['layout']['horizontal_scale'],1)
    def test_only_two_text_interiors_change(self):
        p=self.patches[0];meta,_=inspect_texture(p['before'])
        a=unpack_indices(p['before'],meta);b=unpack_indices(p['after'],meta);changed=0
        rects=[r['inner_rect'] for r in self.report['results']]
        for i,(old,new) in enumerate(zip(a,b)):
            if old!=new:
                changed+=1;self.assertTrue(any(x<=i%512<z and y<=i//512<w for x,y,z,w in rects))
        self.assertGreater(changed,100)
    def test_whole_resource_roundtrip(self):
        p=self.patches[0];out=bytearray(self.raw);out[START:START+SIZE]=p['after']
        self.assertEqual(out[:START],self.raw[:START]);self.assertEqual(out[START+SIZE:],self.raw[START+SIZE:])
        out[START:START+SIZE]=p['before'];self.assertEqual(out,self.raw)
    def test_original_category_paths(self):
        r=probes(self.elf,self.raw)
        self.assertEqual(r['upload_bytes'],0x40410)
        self.assertEqual(r['category_cases'],[{'category':i,'default_sprite':i+32,'selected_sprite':i+12} for i in range(3)])
    def test_configuration_and_source_drift_refused(self):
        for key in ('policy','source_sha256','instruction_windows','extra'):
            c=copy.deepcopy(self.config);c[key]='invalid'
            with self.subTest(key=key),self.assertRaises(ValueError):compile_graphics(self.elf,c)
        with self.assertRaises(ValueError):preview(ROOT/'JOGO/forbidden-preview.png')
    def test_sprite_palette_and_output_drift_refused(self):
        from unittest.mock import patch
        for at in (GANM+16+14*16,START+16+17*4+3,START+16+218*4):
            raw=bytearray(self.raw);raw[at]^=1
            with self.subTest(at=at),self.assertRaises(ValueError):render(raw)
        with patch('name_finish_graphics.render',return_value=(self.patches[0]['before'],[])),self.assertRaises(ValueError):
            compile_graphics(self.elf,self.config)


if __name__=='__main__':unittest.main()
