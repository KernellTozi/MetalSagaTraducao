import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from dialogue import ROOT
from interface_text import SOURCE,compile_draft
from item_names import original,RESOURCE,catalog,compile_names,validate_value
from gfi import encode
import remaining_item_name_release as release


class RemainingNameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes();cls.raw=original(RESOURCE)
        cls.parent=json.loads((ROOT/release.PARENT).read_bytes())
        cls.child=json.loads((ROOT/'translations/interface-v054.json').read_bytes())
        cls.manifest,_=release.load(cls.child['remaining_name_release'])
        cls.before,cls.old_report=compile_draft(cls.elf,cls.parent)
        cls.after,cls.report=compile_draft(cls.elf,cls.child)

    def test_exact_twelve_patches_only(self):
        a={p['id']:p for p in self.before};b={p['id']:p for p in self.after}
        self.assertEqual(set(a),set(b))
        changed={k for k in a if a[k]!=b[k]}
        expected={r['id'] for r in self.manifest['items']+self.manifest['actions']}
        self.assertEqual(changed,expected);self.assertEqual(len(changed),12)
        self.assertEqual(self.report['item_names']['accepted'],541)
        self.assertEqual(self.report['accepted'],self.old_report['accepted'])

    def test_targets_match_human_review_and_item_action_alias(self):
        p={r['id']:r['after'].split(b'\0')[0] for r in self.after}
        for row in self.manifest['items']+self.manifest['actions']:
            self.assertEqual(p[row['id']],encode(row['translation']))
        self.assertEqual(p['item.name.0354'],p['item.name.0373'])
        self.assertEqual(p['item.name.0354'],p['battle.action.0106'])

    def test_legacy_limits_remain_and_do_not_authorize_other_ids(self):
        by={r['id']:r for r in catalog(self.raw)}
        for r in self.manifest['items']:
            with self.assertRaises(ValueError):validate_value(by[r['id']],r['translation'],ceiling=16)
        from spack_battle import catalog as battle,validate_value as action
        a={r['id']:r for r in battle(self.raw)}
        for r in self.manifest['actions'][1:]:
            with self.assertRaises(ValueError):action(a[r['id']],r['translation'])

    def test_roundtrip_attributes_and_all_unrelated_bytes(self):
        patches,report=compile_names(self.elf,self.child['item_names'])
        output=bytearray(self.raw)
        for p in patches:
            at=p['offset'];n=len(p['before'])
            self.assertEqual(output[at:at+n],p['before']);self.assertEqual(n,len(p['after']))
            output[at:at+n]=p['after']
        for r in catalog(self.raw):
            at=r['offset'];self.assertEqual(output[at+24:at+128],self.raw[at+24:at+128])
        for p in patches:output[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(output,self.raw)

    def test_unrelated_names_actions_fonts_and_dialogues_rejected(self):
        for key in ('item_names','spack_battle'):
            bad=copy.deepcopy(self.child);bad[key]['entries'][0]['translation']='Outra coisa'
            with self.assertRaises(ValueError):release.validate_interface(bad)
        for key in ('layout_profile','base_dialogue_draft'):
            bad=copy.deepcopy(self.child);bad[key]='invalid'
            with self.assertRaises(ValueError):release.validate_interface(bad)

    def test_binding_and_source_mutation_rejected(self):
        bad=copy.deepcopy(self.child['remaining_name_release']);bad['sha256']='0'*64
        with self.assertRaises(ValueError):release.load(bad)
        data=bytearray(self.elf);data[200]^=1
        with self.assertRaises(ValueError):compile_names(bytes(data),self.child['item_names'])

    def test_previous_six_names_and_Idolo_fallback_unchanged(self):
        a={p['id']:p for p in self.before};b={p['id']:p for p in self.after}
        for index in (331,372,459,460,838,841,849):
            key=f'item.name.{index:04d}';self.assertEqual(a[key],b[key])
        self.assertEqual(self.child['layout_profile'],'ptbr-layout-v005')

    def test_capacity_ledger_closes_only_remaining_nine(self):
        from item_name_capacity import apply_authorized_fallback
        historical=json.loads((ROOT/'reports/capacidade-nomes-v001.json').read_bytes())
        r=apply_authorized_fallback(historical,ROOT/'translations/interface-v054.json')
        self.assertEqual(r['counts']['blocked'],0)
        self.assertEqual(len(r['resolved_remaining_name_revisions']),9)
        self.assertEqual(len(r['resolved_large_name_revisions']),6)
        self.assertEqual(len(r['resolved_authorized_fallbacks']),1)
        self.assertEqual(len(historical['items']),16)

    def test_comparator_only_exact_parent_and_bounded_prefixes(self):
        a={(p['resource'],p['offset']):copy.deepcopy(p) for p in self.before}
        b={(p['resource'],p['offset']):copy.deepcopy(p) for p in self.after}
        release.normalize_transition(self.parent,self.child,ROOT/release.PARENT,a,b)
        self.assertEqual(set(a),set(b))
        self.assertTrue(all(a[k]['before']==b[k]['before'] for k in a))
        with self.assertRaises(ValueError):release.normalize_transition(self.parent,self.child,ROOT/'translations/interface-v052.json',a,b)


if __name__=='__main__':unittest.main()
