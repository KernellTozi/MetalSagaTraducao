import collections,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from interface_text import compile_draft,SOURCE
from item_names import compile_names,catalog,original,RESOURCE,validate_review,ITEM_BASE,STRIDE,ITEM_COUNT
from gfi import encode,decode

class EquipmentV022(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/'translations/interface-v021.json').read_text(encoding='utf-8'))
        cls.new=json.loads((ROOT/'translations/interface-v022.json').read_text(encoding='utf-8'))
        cls.raw=original(RESOURCE);cls.rows=catalog(cls.raw)
        cls.patches,cls.report=compile_draft(SOURCE.read_bytes(),cls.new)
        oldids={r['id'] for r in cls.old['item_names']['entries']}
        cls.added=[r for r in cls.new['item_names']['entries'] if r['id'] not in oldids]
    def test_single_front_counts_and_no_other_recipe_changes(self):
        self.assertEqual(len(self.added),20)
        self.assertEqual({r['group'] for r in self.added},{'generic-equipment'})
        self.assertEqual(self.report['accepted'],2077)
        self.assertEqual(self.report['item_names']['accepted'],477)
        for key in self.old:
            if key not in ('item_names','item_name_review','iso_name','status'):
                self.assertEqual(self.old[key],self.new[key],key)
    def test_prior_targets_patches_and_unresolved_review_preserved(self):
        targets={r['id']:r for r in self.new['item_names']['entries']}
        for row in self.old['item_names']['entries']:self.assertEqual(row,targets[row['id']])
        previous,_=compile_names(SOURCE.read_bytes(),self.old['item_names'])
        current={p['id']:p for p in self.patches}
        for patch in previous:self.assertEqual(patch,current[patch['id']])
        resumed={'item.name.0141','item.name.0187'}
        self.assertEqual(self.new['item_name_review']['pending'],[r for r in self.old['item_name_review']['pending'] if r['id'] not in resumed])
        self.assertEqual(len(self.new['item_name_review']['pending']),45)
        validate_review(self.new['item_name_review'],self.new['item_names'],self.rows)
    def test_series_and_siglas_preserved_with_safe_gfi_bytes(self):
        targets={r['id']:r['translation'] for r in self.added}
        for i in range(9):self.assertEqual(targets[f'item.name.{165+i:04d}'],f'Traje canino LV{i+1}')
        for index in (113,135,151,162):self.assertIn('CVC',targets[f'item.name.{index:04d}'])
        self.assertIn('BDU',targets['item.name.0127'])
        for text in targets.values():
            data=encode(text);self.assertLessEqual(len(data),16);self.assertEqual(decode(data),text)
    def test_compound_output_roundtrip_and_all_record_attributes(self):
        out=bytearray(self.raw);patches=[p for p in self.patches if p['resource']==RESOURCE]
        for p in patches:
            at=p['offset'];self.assertEqual(bytes(out[at:at+len(p['before'])]),p['before'])
            self.assertEqual(len(p['before']),len(p['after']));out[at:at+len(p['after'])]=p['after']
        for i in range(ITEM_COUNT):
            at=ITEM_BASE+i*STRIDE;self.assertEqual(out[at+17:at+128],self.raw[at+17:at+128])
        for p in reversed(patches):out[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(out,self.raw)
    def test_every_patch_is_source_bound_and_nonoverlapping(self):
        resources=collections.defaultdict(list)
        for p in self.patches:resources[p['resource']].append(p)
        for name,patches in resources.items():
            raw=original(name);patches.sort(key=lambda p:p['offset'])
            for a,b in zip(patches,patches[1:]):self.assertLessEqual(a['offset']+len(a['before']),b['offset'])
            for p in patches:self.assertEqual(raw[p['offset']:p['offset']+len(p['before'])],p['before'])

if __name__=='__main__':unittest.main()
