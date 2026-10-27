import copy,json,struct,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import loading_graphics as l


class LoadingGraphicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=l.original(l.RESOURCE);cls.elf=l.SOURCE.read_bytes()
        cls.after,cls.layout=l.render(cls.raw)
        cls.config=json.loads((ROOT/'translations/interface-v040.json').read_text(encoding='utf-8'))['loading_graphics']

    def test_five_procedural_glyphs_match_original_ink_geometry_exactly(self):
        b=self.raw[l.START:l.START+l.SIZE];meta,_=l.inspect_texture(b);indices=l.unpack_indices(b,meta)
        for char,x in (('o',113),('a',131),('d',149),('n',174),('g',192)):
            im=l.letter(char)
            expected=bytes(255 if indices[(5+y)*256+x+xx] in l.INK else 0 for y in range(24) for xx in range(15))
            self.assertEqual(im.size,(15,24));self.assertEqual(im.tobytes(),expected)

    def test_eight_original_forwarding_snippets_and_single_complete_sprite(self):
        proof=l.proof(self.elf,self.raw)
        self.assertEqual(proof['original_scalar_forwarding_cases'],8)
        self.assertEqual(proof['descriptor_cases'][1]['texture_offset'],l.START)
        self.assertEqual(proof['descriptor_cases'][1]['ganm_offset'],l.GANM)
        self.assertEqual(proof['sprite_rect'],[0,0,256,32]);self.assertEqual(proof['sprite_hotspot'],[128,16])

    def test_source_and_ganm_corruption_blocked(self):
        for at in (0,l.GANM,l.GANM+16,len(self.raw)-1):
            bad=bytearray(self.raw);bad[at]^=1
            with self.assertRaises(ValueError):l.proof(self.elf,bad)
        bad=bytearray(self.elf);bad[0x1752dc]^=1
        with self.assertRaises(ValueError):l.proof(bad,self.raw)

    def test_compiler_modifies_only_4096_pixel_bytes(self):
        patches,report=l.compile_graphics(self.elf,self.config)
        self.assertEqual(len(patches),1);p=patches[0]
        self.assertEqual(p['resource'],l.RESOURCE);self.assertEqual(p['offset'],0x920)
        self.assertEqual(len(p['before']),4096);self.assertEqual(len(p['after']),4096)
        rebuilt=self.raw[:p['offset']]+p['after']+self.raw[p['offset']+4096:]
        self.assertEqual(len(rebuilt),len(self.raw))
        self.assertEqual(rebuilt[:l.START+80],self.raw[:l.START+80])
        self.assertEqual(rebuilt[l.START+l.SIZE:],self.raw[l.START+l.SIZE:])
        self.assertEqual(report['accepted'],1);self.assertEqual(l.sha(self.after),l.TARGET_TEXTURE_SHA)

    def test_palette_alpha_header_and_reverse_roundtrip(self):
        before=self.raw[l.START:l.START+l.SIZE];meta,_=l.inspect_texture(before)
        self.assertEqual(self.after[:80],before[:80])
        self.assertEqual(l.replace_indices(self.after,l.unpack_indices(before,meta)),before)
        out=l.unpack_indices(self.after,meta)
        self.assertTrue(set(out)<=(set(l.INK)|{0}))
        self.assertEqual(self.layout['translation'],'Carregando');self.assertEqual(self.layout['horizontal_scale'],1)
        self.assertEqual(self.layout['capital_body_pixels'],19);self.assertEqual(self.layout['baseline'],23)
        self.assertEqual(self.layout['descender_bottom'],28)

    def test_recipe_identity_target_hash_extra_fields_or_translation_refused(self):
        for key,value in (('policy','unknown'),('source_sha256','0'*64),('translation','Aguarde'),('target_texture_sha256','0'*64)):
            bad=copy.deepcopy(self.config);bad[key]=value
            with self.assertRaises(ValueError):l.compile_graphics(self.elf,bad)
        bad=copy.deepcopy(self.config);bad['bound_windows'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):l.compile_graphics(self.elf,bad)
        bad=copy.deepcopy(self.config);bad['extra']=True
        with self.assertRaises(ValueError):l.compile_graphics(self.elf,bad)

    def test_no_other_interface_changes_including_posters_minigames_and_credits(self):
        old=json.loads((ROOT/'translations/interface-v039.json').read_text(encoding='utf-8'))
        new=json.loads((ROOT/'translations/interface-v040.json').read_text(encoding='utf-8'))
        self.assertEqual({k:v for k,v in old.items() if k not in ('iso_name','status')},
            {k:v for k,v in new.items() if k not in ('iso_name','status','loading_graphics')})
        self.assertEqual(new['layout_profile'],'ptbr-layout-v005')

    def test_unmapped_letter_and_preview_output_protection(self):
        for c in ('Ω','A','\n',' '):
            with self.assertRaises(ValueError):l.letter(c)
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-loading-preview-') as tmp:
            target=Path(tmp)/'comparison.png';layout=l.preview(target)
            self.assertEqual(layout,self.layout);self.assertTrue(target.is_file())
            with self.assertRaises(ValueError):l.preview(target)
            with self.assertRaises(ValueError):l.preview(Path(tmp)/'not-an-iso.iso')
        with self.assertRaises(ValueError):l.preview(ROOT/'JOGO/proibido.png')


if __name__=='__main__':unittest.main()
