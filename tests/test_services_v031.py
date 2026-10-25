import json,mmap,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from build_translation_pilot import load_draft,compile_draft,SOURCE


class ServicesV031(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent,_=load_draft(ROOT/'translations/regiao-inicial-v030.json')
        cls.child=json.loads((ROOT/'translations/regiao-inicial-v031.json').read_text(encoding='utf-8'))
        cls.draft,_=load_draft(ROOT/'translations/regiao-inicial-v031.json')
        with SOURCE.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
            _,cls.old,cls.old_report=compile_draft(data,cls.parent)
            cls.plan,cls.new,cls.report=compile_draft(data,cls.draft)
    def test_exact_seventy_four_resumptions_and_sixty_nine_changed(self):
        self.assertTrue(self.report['valid']);self.assertEqual(self.report['accepted'],5961)
        self.assertEqual(self.report['unchanged'],1270);self.assertEqual(len(self.draft['deferred']),49)
        resumed=set(self.child['resume_deferred']);self.assertEqual(len(resumed),74)
        self.assertEqual(resumed,set(self.child['translations']))
        self.assertEqual(set(self.parent['deferred'])-set(self.draft['deferred']),resumed)
        added={p['id'] for p in self.new}-{p['id'] for p in self.old}
        self.assertEqual(len(added),69)
        self.assertEqual(resumed-added,set(self.child['preservation_decisions']))
    def test_every_parent_patch_and_recipe_value_preserved(self):
        old={p['id']:p for p in self.old};new={p['id']:p for p in self.new}
        self.assertEqual(len(old),5892)
        for key,p in old.items():self.assertEqual(p,new[key],key)
        for key,value in self.parent['translations'].items():self.assertEqual(value,self.draft['translations'][key],key)
        self.assertEqual(self.parent['layout_profile'],self.draft['layout_profile'])
    def test_preserved_records_really_unchanged_and_n3_stays_blocked(self):
        statuses={r['id']:r['status'] for r in self.report['results']}
        for key in self.child['preservation_decisions']:self.assertEqual(statuses[key],'unchanged')
        protected=json.loads((ROOT/'reports/n3-preservation-v001.json').read_text(encoding='utf-8'))['records']
        self.assertEqual(len(protected),19)
        for record in protected:self.assertIn(record['id'],self.draft['deferred'])
        rows={e['id']:e for e in self.plan['entries']}
        self.assertEqual(sum(any('%N$3' in s['source'] for s in rows[key]['segments']) for key in self.draft['deferred']),19)
    def test_patches_disjoint_same_size_and_roundtrip(self):
        patches=sorted(self.new,key=lambda p:p['offset'])
        for a,b in zip(patches,patches[1:]):self.assertLessEqual(a['offset']+len(a['before']),b['offset'])
        with SOURCE.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
            for p in patches:
                self.assertEqual(data[p['offset']:p['offset']+len(p['before'])],p['before'])
                self.assertEqual(len(p['before']),len(p['after']))
                scratch=bytearray(p['before']);scratch[:]=p['after'];scratch[:]=p['before']
                self.assertEqual(scratch,p['before'])


if __name__=='__main__':unittest.main()
