import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import large_item_name_release as r
from item_names import compile_names,original,RESOURCE,catalog,validate_value
from spack_battle import compile_battle
from interface_text import SOURCE
from gfi import encode


class LargeItemNameRelease(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes();cls.raw=original(RESOURCE)
        cls.parent=json.loads((ROOT/r.PARENT).read_bytes())
        cls.child=json.loads((ROOT/'translations/interface-v053.json').read_bytes())
        cls.m,_=r.load(cls.child['large_name_release'])
        cls.old,cls.oreport=compile_names(cls.elf,cls.parent['item_names'])
        cls.new,cls.nreport=compile_names(cls.elf,cls.child['item_names'])
        cls.oldb,_=compile_battle(cls.elf,cls.parent['spack_battle'],cls.parent['item_names'])
        cls.newb,_=compile_battle(cls.elf,cls.child['spack_battle'],cls.child['item_names'])

    def test_exact_six_names_and_five_actions_only(self):
        self.assertEqual(r.validate_interface(self.child),self.parent)
        for a,b,ids in ((self.old,self.new,{x['id'] for x in self.m['items']}),
                        (self.oldb,self.newb,{x['id'] for x in self.m['actions']})):
            old={x['id']:x for x in a};new={x['id']:x for x in b}
            self.assertEqual(set(old),set(new))
            self.assertEqual({k for k in old if old[k]!=new[k]},ids)
        self.assertEqual(self.nreport['accepted'],541)
        self.assertEqual(self.nreport['maximum_target_bytes'],18)

    def test_approved_unicode_wording_and_actions_match(self):
        names={x['id']:x['translation'] for x in self.child['item_names']['entries']}
        actions={x['id']:x['translation'] for x in self.child['spack_battle']['entries']}
        for x in self.m['items']:
            self.assertEqual(names[x['id']],x['translation'])
            self.assertTrue(17<=len(encode(x['translation']))<=18)
        for x in self.m['actions']:self.assertEqual(actions[x['id']],names[x['item_id']])

    def test_legacy_16_byte_validator_still_rejects_all_six(self):
        by={x['id']:x for x in catalog(self.raw)}
        for x in self.m['items']:
            with self.assertRaises(ValueError):validate_value(by[x['id']],x['translation'],ceiling=16)

    def test_roundtrip_keeps_item_attributes_and_source_tail(self):
        output=bytearray(self.raw)
        for p in self.new:
            self.assertEqual(output[p['offset']:p['offset']+len(p['before'])],p['before'])
            self.assertEqual(len(p['before']),len(p['after']))
            output[p['offset']:p['offset']+len(p['after'])]=p['after']
        for row in catalog(self.raw):
            a=row['offset'];self.assertEqual(output[a+24:a+128],self.raw[a+24:a+128])
        for p in self.new:output[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(output,self.raw)

    def test_unrelated_name_action_or_omitted_accent_refused(self):
        for key in ('item_names','spack_battle'):
            bad=copy.deepcopy(self.child);bad[key]['entries'][0]['translation']='Outra mudança'
            with self.assertRaises(ValueError):r.validate_interface(bad)
        bad=copy.deepcopy(self.child);next(e for e in bad['item_names']['entries'] if e['id']=='item.name.0331')['translation']='Pilula Acucarada'
        with self.assertRaises(ValueError):compile_names(self.elf,bad['item_names'])

    def test_layout_manifest_and_source_fingerprint_refused(self):
        bad=copy.deepcopy(self.child);bad['layout_profile']='spacing-v003'
        with self.assertRaises(ValueError):r.validate_interface(bad)
        bad=copy.deepcopy(self.child['large_name_release']);bad['sha256']='0'*64
        with self.assertRaises(ValueError):r.load(bad)
        elf=bytearray(self.elf);elf[200]^=1
        with self.assertRaises(ValueError):compile_names(bytes(elf),self.child['item_names'])

    def test_existing_Idolo_fallback_and_other_profiles_remain_intact(self):
        old={p['id']:p for p in self.old};new={p['id']:p for p in self.new}
        self.assertEqual(old['item.name.0460'],new['item.name.0460'])
        for key in ('graphics','resource_texts','base_dialogue_draft','layout_profile','item_accent_fallback'):
            self.assertEqual(self.parent[key],self.child[key])

    def test_capacity_ledger_closes_only_six_names_and_keeps_nine_width_cases(self):
        from item_name_capacity import apply_authorized_fallback
        old=json.loads((ROOT/'reports/capacidade-nomes-v001.json').read_bytes())
        current=apply_authorized_fallback(old,ROOT/'translations/interface-v053.json')
        self.assertEqual(current['counts']['blocked'],9)
        self.assertEqual(current['counts']['above_observed_width_in_some_profile'],9)
        self.assertEqual(current['counts']['within_all_observed_width_profiles'],0)
        self.assertEqual(len(current['resolved_large_name_revisions']),6)
        self.assertEqual(len(old['items']),16)

    def test_comparator_normalizes_only_exact_six_name_prefixes(self):
        a={(p['resource'],p['offset']):copy.deepcopy(p) for p in self.old}
        b={(p['resource'],p['offset']):copy.deepcopy(p) for p in self.new}
        r.normalize_transition(self.parent,self.child,ROOT/r.PARENT,a,b)
        self.assertEqual(set(a),set(b))
        self.assertTrue(all(a[k]['before']==b[k]['before'] for k in a))
        self.assertTrue(all(len(a[k]['after'])==len(b[k]['after']) for k in a))
        with self.assertRaises(ValueError):r.normalize_transition(self.parent,self.child,ROOT/'translations/interface-v051.json',a,b)


if __name__=='__main__':unittest.main()
