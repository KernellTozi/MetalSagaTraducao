import json,sys,unittest,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from interface_text import compile_draft,SOURCE
from item_names import original,RESOURCE,ITEM_BASE,ITEM_COUNT,STRIDE

class ConsolidatedV021(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/'translations/interface-v020.json').read_text(encoding='utf-8'))
        cls.new=json.loads((ROOT/'translations/interface-v021.json').read_text(encoding='utf-8'))
        cls.patches,cls.report=compile_draft(SOURCE.read_bytes(),cls.new)
    def test_counts_five_fronts_and_installer(self):
        self.assertEqual(self.report['accepted'],2057);self.assertEqual(self.report['item_names']['accepted'],457)
        self.assertEqual(self.report['install_texts']['accepted'],17)
        old={r['id'] for r in self.old['item_names']['entries']}
        groups=collections.Counter(r['group'] for r in self.new['item_names']['entries'] if r['id'] not in old)
        self.assertEqual(dict(groups),{'generic-equipment':37,'consumables-materials':105,'furniture-accessories':56,'skills':51,'generic-key-items':19})
    def test_all_previous_resources_descriptions_and_unresolved_commands_preserved(self):
        for key in self.old:
            if key not in ('item_names','item_name_review','status','iso_name'):self.assertEqual(self.old[key],self.new[key],key)
        self.assertEqual(self.report['item_descriptions']['accepted'],536)
        self.assertEqual(self.report['name_entry']['pending_command_semantics'],['TITLE','BACK'])
    def test_no_patch_overlaps_and_exact_source_bindings(self):
        resources=collections.defaultdict(list)
        for p in self.patches:resources[p['resource']].append(p)
        for name,patches in resources.items():
            raw=original(name);patches.sort(key=lambda p:p['offset'])
            for a,b in zip(patches,patches[1:]):self.assertLessEqual(a['offset']+len(a['before']),b['offset'])
            for p in patches:
                self.assertEqual(raw[p['offset']:p['offset']+len(p['before'])],p['before'])
                self.assertEqual(len(p['before']),len(p['after']))
    def test_compound_patch_preserves_all_item_attributes_and_tables(self):
        raw=original(RESOURCE);out=bytearray(raw)
        for p in self.patches:
            if p['resource']==RESOURCE:out[p['offset']:p['offset']+len(p['after'])]=p['after']
        for index in range(ITEM_COUNT):
            at=ITEM_BASE+index*STRIDE;self.assertEqual(out[at+17:at+128],raw[at+17:at+128])
        self.assertTrue(self.report['item_names']['attributes_description_offsets_and_ids_unchanged'])
    def test_previous_names_produce_identical_patches(self):
        from item_names import compile_names
        before,_=compile_names(SOURCE.read_bytes(),self.old['item_names'])
        after={p['id']:p for p in self.patches if p['id'].startswith('item.name.')}
        for p in before:self.assertEqual(after[p['id']],p)

if __name__=='__main__':unittest.main()
