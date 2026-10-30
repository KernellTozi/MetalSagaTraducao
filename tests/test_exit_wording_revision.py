import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import exit_wording_revision as w
from interface_text import SOURCE,compile_draft


class ExitWordingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.child=json.loads((w.ROOT/'translations/interface-v057.json').read_bytes())
        cls.parent=w.validate_interface(cls.child)
        cls.before,cls.report=compile_draft(SOURCE.read_bytes(),cls.parent)
        cls.after=w.revise(cls.before)

    def test_exact_114_revisions_without_other_changes(self):
        self.assertEqual(len(self.before),len(self.after))
        changed=[(a,b) for a,b in zip(self.before,self.after) if a!=b]
        self.assertEqual(len(changed),114)
        for a,b in changed:
            self.assertEqual({k:v for k,v in a.items() if k!='after'},{k:v for k,v in b.items() if k!='after'})
            self.assertEqual(len(a['after']),len(b['after']))
            self.assertEqual(b['after'].split(b'\0')[0],b'Mundo aberto')
            self.assertEqual(b['after'][12],0)

    def test_root_parent_hash_and_other_changes_rejected(self):
        for key,value in [('layout_profile','bad'),('iso_name','bad.iso')]:
            bad=copy.deepcopy(self.child);bad[key]=value
            with self.assertRaises(ValueError):w.validate_interface(bad)
        bad=copy.deepcopy(self.child);bad['exit_wording_revision']['parent_sha256']='0'*64
        with self.assertRaises(ValueError):w.validate_interface(bad)

    def test_shorter_span_foreign_source_or_missing_occurrence_rejected(self):
        selected=next(p for p in self.before if p['id'].startswith('map.exit.'))
        for field,value in [('after',b'Other name!!!'),('before',selected['before'][:-1])]:
            bad=[dict(p) for p in self.before];next(p for p in bad if p['id']==selected['id'])[field]=value
            with self.assertRaises(ValueError):w.revise(bad)
        with self.assertRaises(ValueError):w.revise([p for p in self.before if p['id']!=selected['id']])

    def test_comparator_accepts_exact_parent_only(self):
        from verify_interface_revision import normalize_item_name_review_transition
        normalize_item_name_review_transition(self.parent,self.child,w.ROOT/w.PARENT,{}, {})
        with self.assertRaises(ValueError):
            normalize_item_name_review_transition(self.parent,self.child,w.ROOT/'translations/interface-v055.json',{}, {})


if __name__=='__main__':unittest.main()
