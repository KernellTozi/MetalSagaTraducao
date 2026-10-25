import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from interface_text import SOURCE,compile_draft


class ConsolidatedV029(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/'translations/interface-v028.json').read_text(encoding='utf-8'))
        cls.new=json.loads((ROOT/'translations/interface-v029.json').read_text(encoding='utf-8'))
        cls.patches,cls.report=compile_draft(SOURCE.read_bytes(),cls.new)
    def test_three_new_graphics_no_double_count_of_legend_revisions(self):
        self.assertEqual(self.report['accepted'],3449)
        self.assertEqual(self.report['password_graphics']['accepted'],3)
        self.assertEqual(self.report['name_entry']['accepted'],4)
    def test_previous_translation_and_assets_preserved(self):
        for key in self.old:
            if key not in ('status','iso_name','name_entry'):self.assertEqual(self.old[key],self.new[key],key)
        self.assertEqual(self.report['item_descriptions']['accepted'],566)
        self.assertEqual(self.report['item_names']['accepted'],516)
    def test_all_patches_disjoint_and_exactly_reversible(self):
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
    def test_local_planner_catalogues_graphics_and_remaining_title_command(self):
        import tempfile
        from plan_interface_menus import audit
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-v029-plan-') as folder:
            path=Path(folder)/'catalogue.json';summary=audit(ROOT/'translations/interface-v029.json',path)
            data=json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(summary['password_graphic_fields'],3)
            self.assertEqual(summary['name_legend_pending'],['TITLE'])
            self.assertEqual([r['translation'] for r in data['password_graphics']],['DESTRAVAR','TRAVAR','SAIR'])

if __name__=='__main__':unittest.main()
