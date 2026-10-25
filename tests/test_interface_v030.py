import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from interface_text import SOURCE,compile_draft


class ConsolidatedV030(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/'translations/interface-v029.json').read_text(encoding='utf-8'))
        cls.new=json.loads((ROOT/'translations/interface-v030.json').read_text(encoding='utf-8'))
        cls.patches,cls.report=compile_draft(SOURCE.read_bytes(),cls.new)
    def test_two_new_fields_and_previous_assets_preserved(self):
        self.assertEqual(self.report['accepted'],3451)
        self.assertEqual(self.report['name_finish_graphics']['accepted'],2)
        for key in self.old:
            if key not in ('status','iso_name','base_dialogue_draft'):self.assertEqual(self.old[key],self.new[key],key)
        self.assertEqual(self.report['item_descriptions']['accepted'],566)
        self.assertEqual(self.report['item_names']['accepted'],516)
        self.assertEqual(self.report['password_graphics']['target_texture_sha256'],
            '60d7d56a31f7ac6e53fe9513daf931cf8d33737f24dc17954ee17eabffaf80cd')
    def test_all_resource_patches_disjoint_exactly_reversible(self):
        from interface_resources import original
        groups={}
        for p in self.patches:groups.setdefault(p['resource'],[]).append(p)
        for resource,patches in groups.items():
            raw=original(resource);out=bytearray(raw);patches.sort(key=lambda p:p['offset'])
            for a,b in zip(patches,patches[1:]):self.assertLessEqual(a['offset']+len(a['before']),b['offset'])
            for p in patches:
                at=p['offset'];self.assertEqual(raw[at:at+len(p['before'])],p['before'])
                self.assertEqual(len(p['before']),len(p['after']));out[at:at+len(p['after'])]=p['after']
            for p in reversed(patches):out[p['offset']:p['offset']+len(p['before'])]=p['before']
            self.assertEqual(out,raw)
    def test_local_planner_includes_only_two_finish_variants(self):
        from plan_interface_menus import audit
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-v030-plan-') as folder:
            path=Path(folder)/'catalogue.json';r=audit(ROOT/'translations/interface-v030.json',path)
            self.assertEqual(r['name_finish_graphic_fields'],2)
            self.assertEqual(r['password_graphic_fields'],3);self.assertEqual(r['name_legend_pending'],['TITLE'])
            data=json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual([r['sprite_index'] for r in data['name_finish_graphics']],[14,34])


if __name__=='__main__':unittest.main()
