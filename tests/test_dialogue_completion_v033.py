import json,mmap,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from build_translation_pilot import load_draft,compile_draft,SOURCE
from reinsertion import descriptor,compile_batch,QUIRK_POLICY,SCALED_POLICY,RESOURCE
from dialogue import sha
from dialogue_advanced import SsdIndex
from dialogue_native_review import RECORDS,encode


class DialogueCompletion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old,_=load_draft(ROOT/'translations/regiao-inicial-v032.json')
        cls.new,_=load_draft(ROOT/'translations/regiao-inicial-v033.json')
        cls.child=json.loads((ROOT/'translations/regiao-inicial-v033.json').read_text(encoding='utf-8'))
        with SOURCE.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
            _,cls.before,_=compile_draft(data,cls.old)
            cls.plan,cls.after,cls.report=compile_draft(data,cls.new)
    def test_exact_fourteen_new_and_every_previous_patch_identical(self):
        self.assertTrue(self.report['valid']);self.assertEqual(self.report['accepted'],5983)
        self.assertEqual(len(self.new['deferred']),27);self.assertEqual(self.report['refused'],0)
        before={p['id']:p for p in self.before};after={p['id']:p for p in self.after}
        self.assertEqual(len(before),5969)
        for key,p in before.items():self.assertEqual(p,after[key],key)
        self.assertEqual(set(after)-set(before),set(self.child['resume_deferred']))
        self.assertEqual(len(self.child['resume_deferred']),14)
        self.assertEqual(self.old['preservation_decisions'],self.new['preservation_decisions'])
    def test_all_segments_and_native_symbols_read_back_exactly(self):
        rows={r['id']:r for r in self.plan['entries']}
        for p in self.after:
            if p['id'] not in self.child['resume_deferred']:continue
            self.assertEqual(len(p['before']),len(p['after']))
            for s in rows[p['id']]['segments']:
                at=s['offset']-p['offset'];expected=bytes.fromhex(s['source_hex']) if s['source']==s['translation'] else encode(s['translation'],p['id'])
                self.assertEqual(p['after'][at:].split(b'\0',1)[0],expected)
    def test_unreviewed_native_and_hash_drift_stay_blocked(self):
        with SOURCE.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
            ix=SsdIndex(data)
            for key in ('map.msg.040ef0ec','map.msg.1df7ec14'):
                r=descriptor(data,int(key.split('.')[-1],16),ix,quirk_refs=True,named_choices=True)
                self.assertTrue(r['blocked_reasons']);r['segments'][0]['translation']='Teste.'
                d={'schema':1,'policy':QUIRK_POLICY,'resource':RESOURCE,'source_sha256':sha(data),'entries':[r]}
                ps,report=compile_batch(data,d,ix);self.assertFalse(report['valid']);self.assertEqual(ps,[])
            key='map.msg.07b264e0';r=descriptor(data,int(key.split('.')[-1],16),ix,quirk_refs=True,named_choices=True)
            r['segments'][0]['translation']='La la la...\tHee hee hee!\nSou Syd!☆';r['record_sha256']='0'*64
            d={'schema':1,'policy':QUIRK_POLICY,'resource':RESOURCE,'source_sha256':sha(data),'entries':[r]}
            self.assertFalse(compile_batch(data,d,ix)[1]['valid'])
    def test_old_policy_does_not_release_six_native_records(self):
        with SOURCE.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
            ix=SsdIndex(data)
            for key in RECORDS:
                r=descriptor(data,int(key.split('.')[-1],16),ix,named_choices=True,scaled_refs=True)
                self.assertTrue(any('nativos' in reason for reason in r['blocked_reasons']))


if __name__=='__main__':unittest.main()
