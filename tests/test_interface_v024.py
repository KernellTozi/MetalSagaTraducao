import collections,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from interface_text import compile_draft,SOURCE
from item_names import original,RESOURCE,ITEM_BASE,ITEM_COUNT,STRIDE,compile_names,catalog,validate_review
from item_descriptions import compile_descriptions
from prepare_item_batch import validate_review as validate_descriptions,prepare
from item_descriptions import catalog as description_catalog

DESCRIPTION_IDS={f'item.description.{suffix}' for suffix in ('003bb','0049e','0310c','04e00','04e5a')}
NAME_IDS={f'item.name.{i:04d}' for i in (861,899,1015,1043,1044,1045)}

class RegularV024(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/'translations/interface-v023.json').read_text(encoding='utf-8'))
        cls.new=json.loads((ROOT/'translations/interface-v024.json').read_text(encoding='utf-8'))
        cls.raw=original(RESOURCE);cls.elf=SOURCE.read_bytes()
        cls.patches,cls.report=compile_draft(cls.elf,cls.new)
    def test_scoped_counts_and_unchanged_other_resources(self):
        self.assertEqual(self.report['accepted'],2104)
        self.assertEqual(self.report['item_names']['accepted'],499)
        self.assertEqual(self.report['item_descriptions']['accepted'],541)
        allowed={'item_names','item_name_review','item_descriptions','description_review','status','iso_name'}
        for key in self.old:
            if key not in allowed:self.assertEqual(self.old[key],self.new[key],key)
        for section,expected in (('item_names',NAME_IDS),('item_descriptions',DESCRIPTION_IDS)):
            before={r['id']:r for r in self.old[section]['entries']};after={r['id']:r for r in self.new[section]['entries']}
            self.assertEqual(set(after)-set(before),expected)
            for key,row in before.items():self.assertEqual(row,after[key])
    def test_old_name_and_description_patches_identical(self):
        names,_=compile_names(self.elf,self.old['item_names'])
        descriptions,_=compile_descriptions(self.elf,self.old['item_descriptions'])
        current={r['id']:r for r in self.patches}
        for patch in names+descriptions:self.assertEqual(patch,current[patch['id']])
    def test_ledgers_resume_only_explicit_targets(self):
        self.assertEqual(self.new['description_review']['pending'],[r for r in self.old['description_review']['pending'] if r['id'] not in DESCRIPTION_IDS])
        self.assertEqual(self.new['item_name_review']['pending'],[r for r in self.old['item_name_review']['pending'] if r['id']!='item.name.0861'])
        self.assertEqual(len(self.new['description_review']['pending']),25)
        self.assertEqual(len(self.new['item_name_review']['pending']),32)
        validate_review(self.new['item_name_review'],self.new['item_names'],catalog(self.raw))
        validate_descriptions(self.new['description_review'],self.new['item_descriptions'],description_catalog(self.raw))
        with self.assertRaises(ValueError):prepare(self.old,{'item.description.003bb':'Arma branca:|paralisa orgânicos'},'interface-v024')
    def test_all_resource_roundtrips_and_record_attributes(self):
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
            for p in reversed(patches):out[p['offset']:p['offset']+len(p['before'])]=p['before']
            self.assertEqual(out,raw)
    def test_protected_alias_and_reward_numbers_preserved(self):
        targets={r['id']:r['translation'] for r in self.new['item_names']['entries']}
        self.assertNotIn('item.name.0877',targets);self.assertNotIn('item.name.0590',targets)
        for index,number in ((1043,10),(1044,20),(1045,30)):
            self.assertEqual(targets[f'item.name.{index:04d}'],f'Pin {number} vitórias')

if __name__=='__main__':unittest.main()
