import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from interface_text import SOURCE,compile_draft
from password_graphics import run,memory32


class ConsolidatedV032(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/'translations/interface-v031.json').read_text(encoding='utf-8'))
        cls.new=json.loads((ROOT/'translations/interface-v032.json').read_text(encoding='utf-8'))
        cls.elf=SOURCE.read_bytes();cls.patches,cls.report=compile_draft(cls.elf,cls.new)
    def test_seventy_five_new_fields_all_previous_recipe_content_preserved(self):
        self.assertEqual(self.report['accepted'],3526);self.assertEqual(self.report['character_titles']['accepted'],73)
        for key in self.old:
            if key not in ('entries','iso_name','status'):self.assertEqual(self.old[key],self.new[key],key)
        self.assertEqual(self.old['entries'],self.new['entries'][:-2])
        self.assertEqual(self.new['base_dialogue_draft'],'translations/regiao-inicial-v032.json')
        self.assertEqual(self.report['item_names']['accepted'],516)
    def test_original_two_reward_arguments_and_exact_space_control_preservation(self):
        regs=[0]*32;regs[17]=0x620000;regs[29]=0x640000
        r=run(self.elf,0x160194,0x1601ac,0x227a28,regs,memory32(((0x621788,12345),)))
        self.assertEqual((r[5],r[6]),(0x436610,12345))
        regs=[0]*32;regs[17]=0x620000;regs[29]=0x640000
        r=run(self.elf,0x160268,0x160290,0x227a28,regs,memory32(((0x62178c,42),(0x475ae8,0x680000))))
        self.assertEqual((r[5],r[6]),(0x436628,0x680000+42*128))
        for p in self.patches:
            if p['id'] not in ('elf.ui.00337610','elf.ui.00337628'):continue
            self.assertTrue(p['after'].startswith(b'    '))
            self.assertIn(b'!    \0',p['after'])
            self.assertEqual(len(p['before']),len(p['after']))
    def test_full_resource_patch_disjointness_and_reverse_roundtrip(self):
        from interface_resources import original
        groups={}
        for p in self.patches:groups.setdefault(p['resource'],[]).append(p)
        for resource,ps in groups.items():
            raw=original(resource);out=bytearray(raw);ps.sort(key=lambda p:p['offset'])
            for a,b in zip(ps,ps[1:]):self.assertLessEqual(a['offset']+len(a['before']),b['offset'])
            for p in ps:
                at=p['offset'];self.assertEqual(raw[at:at+len(p['before'])],p['before'])
                self.assertEqual(len(p['before']),len(p['after']));out[at:at+len(p['after'])]=p['after']
            for p in reversed(ps):out[p['offset']:p['offset']+len(p['before'])]=p['before']
            self.assertEqual(out,raw)
    def test_local_planner_distinguishes_titles_from_legacy_string_hashes(self):
        from plan_interface_menus import audit
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-v032-plan-') as folder:
            path=Path(folder)/'catalog.json';r=audit(ROOT/'translations/interface-v032.json',path)
            self.assertEqual(r['character_title_fields'],73);self.assertEqual(r['character_title_unique'],78)
            self.assertEqual(r['character_title_preserved'],5)
            data=json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(len(data['character_titles']),78);self.assertEqual(r['name_legend_pending'],['TITLE'])


if __name__=='__main__':unittest.main()
