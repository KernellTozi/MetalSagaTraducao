"""Regression checks for title placement and the separate battle renderer."""
import copy,json,struct,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from battle_font_advance import START,END,WINDOW_SHA,POLICY,elf_patch,replacement
from battle_advance_probe import run
from interface_graphics import original,sha
from glyph_spacing import ORIGINAL_SHA
from title_revision import artwork,compile_revision

class BattleAdvance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.elf=original('SLUS_212.93')
    def test_exact_source_and_size(self):
        cfg={'policy':POLICY,'source_sha256':ORIGINAL_SHA,'window_sha256':WINDOW_SHA}
        p=elf_patch(self.elf,cfg)
        self.assertEqual(len(p['before']),len(p['after']))
        self.assertEqual(len(p['after']),END-START)
        bad=bytearray(self.elf);bad[START]^=1
        with self.assertRaises(ValueError):elf_patch(bad,cfg)
        words=struct.unpack('<'+'I'*((END-START)//4),p['after'])
        self.assertIn(0x3c013f00,words);self.assertIn(0x4481a000,words)
    def test_classifier_equivalence_all_leads(self):
        for b in range(256):
            self.assertEqual(((b+127)&255)<31,((b-129)&0xffffffff)<31)
            self.assertEqual(((b+32)&255)<29,((b-224)&0xffffffff)<29)
    def test_all_18_codes_sizes_scales_and_advances(self):
        for trail in list(range(0x40,0x4f))+list(range(0x59,0x5c)):
            raw=bytes([0x82,trail])
            for size,scale,advance in ((22,1,0),(24,0.75,19),(26,1.5,13)):
                a=run(self.elf,raw,False,size,scale,advance);b=run(self.elf,raw,True,size,scale,advance)
                self.assertEqual(a['draws'],b['draws']);self.assertEqual(a['maps'],b['maps'])
                self.assertEqual(a['consumed'],b['consumed']);self.assertEqual(b['consumed'],2)
                self.assertAlmostEqual(b['advance'],advance+size*scale*0.5)
    def test_lead_and_trail_boundaries_unchanged(self):
        cases=[bytes([b,t]) for b in range(256) for t in (0,0x3f,0x40,0x4f,0x58,0x5c,0x7e,0x7f,0x80,0xfc,0xfd,0xff)]
        cases += [bytes([0x82,t]) for t in range(256)]
        for raw in cases:
            a=run(self.elf,raw);b=run(self.elf,raw,True)
            special=raw[0]==0x82 and (0x40<=raw[1]<=0x4e or 0x59<=raw[1]<=0x5b)
            if special:a['advance']/=2
            self.assertEqual(a,b,raw.hex())

class InterfaceRevision(unittest.TestCase):
    def test_previous_translations_and_explicit_total_restorations(self):
        old=json.loads((ROOT/'translations/interface-v011.json').read_text(encoding='utf-8'))
        new=json.loads((ROOT/'translations/interface-v012.json').read_text(encoding='utf-8'))
        before={e['id']:e for e in old['entries']};after={e['id']:e for e in new['entries']}
        self.assertEqual(set(before)-set(after),set(new['restored_originals']))
        for key in set(before)&set(after):self.assertEqual(before[key],after[key])
        self.assertEqual(len(set(after)-set(before)),23)
        self.assertEqual(old['base_dialogue_draft'],new['base_dialogue_draft'])
        self.assertEqual(new['layout_profile'],'ptbr-layout-v005')
    def test_title_geometry_palette_roundtrip_and_binding(self):
        config=json.loads((ROOT/'translations/interface-graphics-v008.json').read_text(encoding='utf-8'))
        patches,report=compile_revision(config);raw=original('DATA/RDATA/RTITLE.SDA');out=bytearray(raw)
        for p in patches:
            if p['resource']=='DATA/RDATA/RTITLE.SDA':out[p['offset']:p['offset']+len(p['after'])]=p['after']
        self.assertEqual(out[:1072],raw[:1072]);self.assertEqual(len(out),len(raw))
        for p in patches:
            if p['resource']=='DATA/RDATA/RTITLE.SDA':out[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(out,raw)
        self.assertEqual(report['reviewed_artwork']['menu_positions']['two_options'],[296,330])
        rect=report['reviewed_artwork']['menu_positions']['credit_screen_rect']
        self.assertLessEqual(rect[3],448);self.assertGreaterEqual(rect[1],428)
        bad=copy.deepcopy(config);bad['reviewed_artwork']['labels'][0]['width']+=1
        with self.assertRaises(ValueError):compile_revision(bad)

if __name__=='__main__':unittest.main()
