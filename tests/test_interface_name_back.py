import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from name_back_command import *
from name_entry_text import compile_name_entry
from interface_text import SOURCE


class NameBack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes()
        cls.old=json.loads((ROOT/'translations/interface-v028.json').read_text(encoding='utf-8'))['name_entry']
        cls.config=json.loads((ROOT/'translations/interface-v029.json').read_text(encoding='utf-8'))['name_entry']
        cls.patches,cls.report=compile_name_entry(cls.elf,cls.config)
    def test_back_moves_to_selector_and_does_not_delete_or_exit(self):
        r=proof(self.elf,self.config['back_evidence'])
        self.assertEqual(len(r['navigation_cases']),42)
        for c in r['navigation_cases']:
            self.assertEqual(c['next_row'],0);self.assertTrue(c['name_unchanged'])
        self.assertEqual(len(r['legend_cases']),8)
    def test_old_policy_keeps_back_and_new_policy_changes_only_twelve_bytes(self):
        old,_=compile_name_entry(self.elf,self.old);changed=0
        for a,b in zip(old,self.patches):
            self.assertEqual(a['before'],b['before']);self.assertEqual(a['offset'],b['offset'])
            diff=[i for i,(x,y) in enumerate(zip(a['after'],b['after'])) if x!=y];changed+=len(diff)
            self.assertTrue(all(a['after'][i:i+4]==b'BACK' and b['after'][i:i+4]==b'VOL.' for i in diff[::4]))
            self.assertEqual(a['after'][-1],b['after'][-1]);self.assertEqual(a['after'].count(b'TITLE'),b['after'].count(b'TITLE'))
        self.assertEqual(changed,12);self.assertEqual(self.report['accepted'],4)
        self.assertEqual(self.report['pending_command_semantics'],['TITLE'])
    def test_no_implicit_release_in_historical_policy(self):
        c=copy.deepcopy(self.old);c['back_evidence']=self.config['back_evidence']
        with self.assertRaises(ValueError):compile_name_entry(self.elf,c)
        c=copy.deepcopy(self.config);c['policy']=self.old['policy'];c.pop('back_evidence')
        with self.assertRaises(ValueError):compile_name_entry(self.elf,c)
    def test_unknown_context_code_or_slot_refused(self):
        for kind in ('code','title','back'):
            c=copy.deepcopy(self.config)
            if kind=='code':c['back_evidence']['instruction_windows'][0]['sha256']='bad'
            else:
                for e in c['entries']:
                    for s in e.get('slots',[]):
                        if kind=='title' and s['translation']=='TITLE':s['translation']='MENU'
                        if kind=='back' and s['translation']=='VOL.':s['translation']='SAIR'
            with self.subTest(kind=kind),self.assertRaises(ValueError):compile_name_entry(self.elf,c)
    def test_unreviewed_probe_parameters_refused(self):
        for row,alphabet in ((-1,0),(7,0),(0,-1),(0,3)):
            with self.assertRaises(ValueError):execute(self.elf,row,alphabet)

if __name__=='__main__':unittest.main()
