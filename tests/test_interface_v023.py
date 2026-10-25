import collections,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from interface_text import compile_draft,SOURCE
from item_names import compile_names,catalog,original,RESOURCE,validate_review,ITEM_BASE,ITEM_COUNT,STRIDE
from gfi import encode,decode

class TwoFrontsV023(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/'translations/interface-v022.json').read_text(encoding='utf-8'))
        cls.new=json.loads((ROOT/'translations/interface-v023.json').read_text(encoding='utf-8'))
        cls.raw=original(RESOURCE);cls.rows=catalog(cls.raw)
        cls.patches,cls.report=compile_draft(SOURCE.read_bytes(),cls.new)
        oldids={r['id'] for r in cls.old['item_names']['entries']}
        cls.added=[r for r in cls.new['item_names']['entries'] if r['id'] not in oldids]
    def test_two_fronts_and_all_other_resources_unchanged(self):
        self.assertEqual(dict(collections.Counter(r['group'] for r in self.added)),{'consumables-materials':9,'furniture-accessories':7})
        self.assertEqual(self.report['accepted'],2093)
        self.assertEqual(self.report['item_names']['accepted'],493)
        self.assertEqual(self.report['item_names']['unique_translated_labels'],477)
        for key in self.old:
            if key not in ('item_names','item_name_review','status','iso_name'):
                self.assertEqual(self.old[key],self.new[key],key)
    def test_previous_477_targets_and_patches_identical(self):
        targets={r['id']:r for r in self.new['item_names']['entries']}
        for row in self.old['item_names']['entries']:self.assertEqual(row,targets[row['id']])
        oldpatches,_=compile_names(SOURCE.read_bytes(),self.old['item_names'])
        newpatches={p['id']:p for p in self.patches}
        for p in oldpatches:self.assertEqual(p,newpatches[p['id']])
    def test_only_twelve_explicit_deferred_resumptions(self):
        resumed={f'item.name.{i:04d}' for i in (331,352,354,355,372,373,385,433,449,451,727,747)}
        review=self.new['item_name_review']
        self.assertEqual(review['pending'],[r for r in self.old['item_name_review']['pending'] if r['id'] not in resumed])
        self.assertEqual(len(review['pending']),33);self.assertEqual(review['selected'],527)
        validate_review(review,self.new['item_names'],self.rows)
    def test_aliases_and_safe_unicode_name_readback(self):
        out=bytearray(self.raw)
        for p in self.patches:
            if p['resource']==RESOURCE:out[p['offset']:p['offset']+len(p['after'])]=p['after']
        targets={r['id']:r['translation'] for r in self.added}
        self.assertEqual(targets['item.name.0354'],targets['item.name.0373'])
        for row in self.rows:
            if row['id'] in targets:
                value=bytes(out[row['offset']:row['offset']+24]).split(b'\0')[0]
                self.assertLessEqual(len(value),16)
                self.assertEqual(decode(value),targets[row['id']]);self.assertEqual(value,encode(targets[row['id']]))
        for i in range(ITEM_COUNT):
            at=ITEM_BASE+i*STRIDE;self.assertEqual(out[at+17:at+128],self.raw[at+17:at+128])
    def test_source_bounds_disjoint_patches_and_resource_roundtrip(self):
        groups=collections.defaultdict(list)
        for p in self.patches:groups[p['resource']].append(p)
        for name,patches in groups.items():
            raw=original(name);out=bytearray(raw);patches.sort(key=lambda p:p['offset'])
            for a,b in zip(patches,patches[1:]):self.assertLessEqual(a['offset']+len(a['before']),b['offset'])
            for p in patches:
                at=p['offset'];self.assertEqual(raw[at:at+len(p['before'])],p['before'])
                self.assertEqual(len(p['before']),len(p['after']));out[at:at+len(p['after'])]=p['after']
            for p in reversed(patches):out[p['offset']:p['offset']+len(p['before'])]=p['before']
            self.assertEqual(out,raw)

if __name__=='__main__':unittest.main()
