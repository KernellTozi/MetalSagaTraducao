import json,sys,unittest,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from interface_text import SOURCE,compile_draft
from item_names import original,RESOURCE,ITEM_BASE,ITEM_COUNT,STRIDE
from gfi import decode

class ConsolidatedV020(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent=json.loads((ROOT/'translations/interface-v019.json').read_text(encoding='utf-8'))
        cls.draft=json.loads((ROOT/'translations/interface-v020.json').read_text(encoding='utf-8'))
        cls.patches,cls.report=compile_draft(SOURCE.read_bytes(),cls.draft)
    def test_three_blocks_exact_counts_and_prior_approved_entries_preserved(self):
        self.assertEqual(self.report['accepted'],1772)
        self.assertEqual(self.report['item_names']['accepted'],189)
        self.assertEqual(self.report['item_descriptions']['accepted'],536)
        self.assertEqual(self.report['elf_strings'],305)
        self.assertEqual(self.report['spack_ui']['accepted'],279)
        a={e['id']:e for e in self.parent['entries']};b={e['id']:e for e in self.draft['entries']}
        self.assertEqual(len(b)-len(a),7)
        for key,row in a.items():self.assertEqual(b[key],row,key)
        a={e['id']:e for e in self.parent['item_descriptions']['entries']};b={e['id']:e for e in self.draft['item_descriptions']['entries']}
        self.assertEqual(len(b)-len(a),41)
        for key,row in a.items():self.assertEqual(b[key],row,key)
        for key,row in self.parent['spack_ui']['translations'].items():
            self.assertEqual(self.draft['spack_ui']['translations'][key],row,key)
    def test_unrelated_resources_maps_fonts_title_and_pending_evidence_preserved(self):
        changed={'status','iso_name','entries','spack_ui','item_descriptions','description_review'}
        for key in self.parent:
            if key not in changed:self.assertEqual(self.parent[key],self.draft[key],key)
        ids={r['id'] for r in self.draft['item_descriptions']['entries']}
        expected=[r for r in self.parent['description_review']['pending'] if r['id'] not in ids]
        self.assertEqual(self.draft['description_review']['pending'],expected)
        self.assertEqual(len(expected),30)
        self.assertEqual(self.draft['description_review']['preserved'],self.parent['description_review']['preserved'])
    def test_all_resource_patches_disjoint_and_bounded(self):
        grouped=collections.defaultdict(list)
        for p in self.patches:grouped[p['resource']].append(p)
        for resource,patches in grouped.items():
            raw=original(resource);patches.sort(key=lambda p:p['offset'])
            for a,b in zip(patches,patches[1:]):self.assertLessEqual(a['offset']+len(a['before']),b['offset'])
            for p in patches:
                at=p['offset'];self.assertEqual(len(p['before']),len(p['after']))
                self.assertEqual(raw[at:at+len(p['before'])],p['before'])
    def test_item_attributes_offsets_and_actual_names_survive_combined_build(self):
        raw=original(RESOURCE);output=bytearray(raw)
        for p in self.patches:
            if p['resource']==RESOURCE:output[p['offset']:p['offset']+len(p['after'])]=p['after']
        targets={int(r['id'].split('.')[-1]):r['translation'] for r in self.draft['item_names']['entries']}
        for index in range(ITEM_COUNT):
            at=ITEM_BASE+index*STRIDE
            self.assertEqual(output[at+24:at+STRIDE],raw[at+24:at+STRIDE])
            if index in targets:self.assertEqual(decode(bytes(output[at:at+24]).split(b'\0')[0]),targets[index])
            else:self.assertEqual(output[at:at+24],raw[at:at+24])
        self.assertNotIn('names_and_item_records_unchanged',self.report['item_descriptions'])
        self.assertTrue(self.report['item_descriptions']['names_and_item_records_unchanged_by_description_patches'])
        self.assertTrue(self.report['item_descriptions']['generic_names_modified_under_separate_policy'])
    def test_shared_balance_direction_and_weapon_labels_exact(self):
        values={r['id']:r['translation'] for r in self.draft['entries']}
        self.assertEqual(values['elf.ui.00349620'],'Dir.');self.assertEqual(values['elf.ui.00349628'],'Esq.')
        for at in (0x349a88,0x349ad8,0x349b68):self.assertEqual(values[f'elf.ui.{at:08x}'],'Saldo')
        self.assertEqual(values['elf.ui.00349f58'],'MAIN');self.assertEqual(values['elf.ui.00349f60'],'SUB')

if __name__=='__main__':unittest.main()
