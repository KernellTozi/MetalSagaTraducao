import collections,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from interface_text import compile_draft,SOURCE
from item_names import original,RESOURCE,catalog,compile_names,validate_review,ITEM_BASE,ITEM_COUNT,STRIDE
from gfi import encode,decode

ADDED={111,116,123,134,138,140,177,179,183,441,460,646,647,870,871,872,873}
RESUMED={179,441,460,646,647,870,871,872,873}

class SeventeenNamesV025(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/'translations/interface-v024.json').read_text(encoding='utf-8'))
        cls.new=json.loads((ROOT/'translations/interface-v025.json').read_text(encoding='utf-8'))
        cls.raw=original(RESOURCE);cls.elf=SOURCE.read_bytes()
        cls.patches,cls.report=compile_draft(cls.elf,cls.new)
        oldids={e['id'] for e in cls.old['item_names']['entries']}
        cls.added=[e for e in cls.new['item_names']['entries'] if e['id'] not in oldids]
    def test_seventeen_names_and_all_other_resources_unchanged(self):
        self.assertEqual({int(e['id'].split('.')[-1]) for e in self.added},ADDED)
        self.assertEqual(self.report['accepted'],2121)
        self.assertEqual(self.report['item_names']['accepted'],516)
        self.assertEqual(self.report['item_names']['unique_translated_labels'],500)
        for key in self.old:
            if key not in ('item_names','item_name_review','status','iso_name'):
                self.assertEqual(self.old[key],self.new[key],key)
    def test_all_previous_targets_and_name_patches_identical(self):
        targets={e['id']:e for e in self.new['item_names']['entries']}
        for entry in self.old['item_names']['entries']:self.assertEqual(entry,targets[entry['id']])
        previous,_=compile_names(self.elf,self.old['item_names'])
        current={p['id']:p for p in self.patches}
        for p in previous:self.assertEqual(p,current[p['id']])
    def test_only_nine_explicit_resumptions_and_evidence_preserved(self):
        resumed={f'item.name.{i:04d}' for i in RESUMED};review=self.new['item_name_review']
        self.assertEqual(review['pending'],[e for e in self.old['item_name_review']['pending'] if e['id'] not in resumed])
        self.assertEqual(review['selected'],540);self.assertEqual(len(review['pending']),23)
        validate_review(review,self.new['item_names'],catalog(self.raw))
    def test_proper_identifiers_series_and_distinct_objects(self):
        targets={e['id']:e['translation'] for e in self.new['item_names']['entries']}
        for index,term in ((111,'Kevy'),(116,'Kaiser'),(123,'Kevy'),(134,'Saratoga'),(138,'Ali Baba'),(140,'Kevy'),(177,'Kevy'),(183,'AAP')):
            self.assertIn(term,targets[f'item.name.{index:04d}'])
        for i in range(4):
            self.assertEqual(targets[f'item.name.{870+i:04d}'],f'Barril vital {i+1}')
            self.assertNotEqual(targets[f'item.name.{870+i:04d}'],targets[f'item.name.{866+i:04d}'])
        self.assertNotEqual(targets['item.name.0459'],targets['item.name.0460'])
    def test_roundtrip_gfi_disjoint_patches_and_record_attributes(self):
        groups=collections.defaultdict(list)
        for p in self.patches:groups[p['resource']].append(p)
        for name,patches in groups.items():
            raw=original(name);out=bytearray(raw);patches.sort(key=lambda p:p['offset'])
            for a,b in zip(patches,patches[1:]):self.assertLessEqual(a['offset']+len(a['before']),b['offset'])
            for p in patches:
                at=p['offset'];self.assertEqual(raw[at:at+len(p['before'])],p['before'])
                self.assertEqual(len(p['before']),len(p['after']));out[at:at+len(p['after'])]=p['after']
            if name==RESOURCE:
                for i in range(ITEM_COUNT):
                    at=ITEM_BASE+i*STRIDE;self.assertEqual(out[at+17:at+128],raw[at+17:at+128])
                rows={e['id']:e for e in catalog(raw)}
                for e in self.added:
                    at=rows[e['id']]['offset'];value=bytes(out[at:at+24]).split(b'\0')[0]
                    self.assertLessEqual(len(value),16);self.assertEqual(value,encode(e['translation']));self.assertEqual(decode(value),e['translation'])
            for p in reversed(patches):out[p['offset']:p['offset']+len(p['before'])]=p['before']
            self.assertEqual(out,raw)

if __name__=='__main__':unittest.main()
