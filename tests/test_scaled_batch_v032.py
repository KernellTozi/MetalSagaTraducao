import json,mmap,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from build_translation_pilot import load_draft,compile_draft,SOURCE
from control_scaled100 import tokenize


class ScaledBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old,_=load_draft(ROOT/'translations/regiao-inicial-v031.json')
        cls.new,_=load_draft(ROOT/'translations/regiao-inicial-v032.json')
        cls.child=json.loads((ROOT/'translations/regiao-inicial-v032.json').read_text(encoding='utf-8'))
        with SOURCE.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
            _,cls.before,cls.previous_report=compile_draft(data,cls.old)
            cls.plan,cls.after,cls.report=compile_draft(data,cls.new)
    def test_exact_eight_new_and_all_previous_patches_preserved(self):
        self.assertTrue(self.report['valid']);self.assertEqual(self.report['accepted'],5969)
        self.assertEqual(self.report['refused'],0);self.assertEqual(len(self.new['deferred']),41)
        before={p['id']:p for p in self.before};after={p['id']:p for p in self.after}
        self.assertEqual(len(before),5961)
        for key,p in before.items():self.assertEqual(p,after[key],key)
        self.assertEqual(set(after)-set(before),set(self.child['resume_deferred']))
        self.assertEqual(set(self.old['deferred'])-set(self.new['deferred']),set(self.child['resume_deferred']))
        self.assertEqual(self.old['preservation_decisions'],self.new['preservation_decisions'])
    def test_complete_control_bytes_and_all_slots_roundtrip(self):
        from gfi import encode
        by_id={e['id']:e for e in self.plan['entries']}
        from reinsertion import control_check
        for p in self.after:
            self.assertEqual(len(p['before']),len(p['after']))
            if p['id'] not in self.child['resume_deferred']:continue
            for s in by_id[p['id']]['segments']:
                control_check(bytes.fromhex(s['source_hex']),encode(s['translation']),tokenize)
                at=s['offset']-p['offset'];self.assertEqual(p['after'][at:].split(b'\0',1)[0],encode(s['translation']))
        for a,b in zip(sorted(self.after,key=lambda p:p['offset']),sorted(self.after,key=lambda p:p['offset'])[1:]):
            self.assertLessEqual(a['offset']+len(a['before']),b['offset'])
    def test_interface_and_font_recipes_identical_except_version_and_map(self):
        old=json.loads((ROOT/'translations/interface-v030.json').read_text(encoding='utf-8'))
        new=json.loads((ROOT/'translations/interface-v031.json').read_text(encoding='utf-8'))
        for key in old:
            if key not in ('base_dialogue_draft','iso_name','status'):self.assertEqual(old[key],new[key],key)
        self.assertEqual(new['base_dialogue_draft'],'translations/regiao-inicial-v032.json')
        self.assertEqual(new['layout_profile'],'ptbr-layout-v005')


if __name__=='__main__':unittest.main()
