import json,sys,unittest,collections,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from interface_text import compile_draft,SOURCE
from interface_resources import original
from item_names import catalog,validate_review,RESOURCE
from plan_interface_menus import audit

class LargeConsolidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/'translations/interface-v025.json').read_text(encoding='utf-8'))
        cls.new=json.loads((ROOT/'translations/interface-v026.json').read_text(encoding='utf-8'))
        cls.patches,cls.report=compile_draft(SOURCE.read_bytes(),cls.new)
    def test_effective_scale_above_twice_largest_previous_batch(self):
        self.assertEqual(self.report['accepted'],3419)
        self.assertEqual(self.report['accepted']-2121,1298)
        self.assertGreaterEqual(1298,647*2)
        self.assertEqual(self.report['spack_battle']['accepted'],999)
        self.assertEqual(self.report['spack_interactions']['accepted'],299)
    def test_previous_translations_profiles_and_assets_unchanged(self):
        for key in self.old:
            if key not in ('status','iso_name','item_name_review'):self.assertEqual(self.old[key],self.new[key],key)
        self.assertEqual(self.report['item_names']['accepted'],516)
        self.assertEqual(self.report['item_descriptions']['accepted'],541)
    def test_review_complete_without_counting_preservations_as_translations(self):
        r=self.new['item_name_review'];self.assertEqual(r['selected'],566)
        self.assertEqual((r['accepted'],len(r['pending']),len(r['preserved'])),(516,25,25))
        source=catalog(original(RESOURCE));validate_review(r,self.new['item_names'],source)
        self.assertEqual(self.new['item_names'],self.old['item_names'])
        # Four new deferrals and two explicit preservation decisions; all others retain historical data.
        before={e['id']:e for e in self.old['item_name_review']['pending']};after={e['id']:e for e in r['pending']}
        for key,row in before.items():
            if key not in ('item.name.0946','item.name.1035'):self.assertEqual(row,after[key])
    def test_whole_resource_source_binding_disjoint_patches_and_roundtrip(self):
        groups=collections.defaultdict(list)
        for p in self.patches:groups[p['resource']].append(p)
        for name,patches in groups.items():
            source=original(name);out=bytearray(source);patches.sort(key=lambda p:p['offset'])
            for a,b in zip(patches,patches[1:]):self.assertLessEqual(a['offset']+len(a['before']),b['offset'])
            for p in patches:
                at=p['offset'];self.assertEqual(source[at:at+len(p['before'])],p['before'])
                self.assertEqual(len(p['before']),len(p['after']));out[at:at+len(p['after'])]=p['after']
            for p in reversed(patches):out[p['offset']:p['offset']+len(p['before'])]=p['before']
            self.assertEqual(out,source)
    def test_new_patches_use_only_five_authorized_regions(self):
        allowed=((0x325d0,0x34870),(0x37070,0x6cdb0),(0x6cdb0,0x7e714),(0x11c820,0x11d6c0))
        ids={e['id'] for e in self.new['spack_battle']['entries']}|{'spack.reaction.pool','spack.bar.pool'}
        new=[p for p in self.patches if p['id'] in ids]
        self.assertEqual(len(new),1001)
        for p in new:
            self.assertEqual(p['resource'],RESOURCE)
            self.assertTrue(any(a<=p['offset'] and p['offset']+len(p['before'])<=z for a,z in allowed))
    def test_local_planner_exports_new_catalogues_and_preservation_decisions(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-v026-planning-') as folder:
            path=Path(folder)/'catalogue.json'
            summary=audit(ROOT/'translations/interface-v026.json',path)
            document=json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(summary['battle_translated'],{'action':679,'hint':248,'enemy_name':72})
            self.assertEqual(summary['interaction_translated'],{'reaction':149,'bar':150})
            self.assertEqual(summary['item_name_statuses']['reviewed-preserved-name'],24)
            self.assertEqual(summary['item_name_statuses']['deferred-name'],25)
            self.assertNotIn('unreviewed-name',summary['item_name_statuses'])
            self.assertEqual((len(document['battle_fields']),len(document['interaction_fields'])),(1489,317))
            self.assertFalse(document['originals_modified']);self.assertFalse(document['iso_created'])

if __name__=='__main__':unittest.main()
