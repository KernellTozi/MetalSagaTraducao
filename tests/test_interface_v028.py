import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from character_status_context import *
from interface_text import SOURCE,compile_draft


class ConsolidatedV028(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/'translations/interface-v026.json').read_text(encoding='utf-8'))
        cls.new=json.loads((ROOT/'translations/interface-v028.json').read_text(encoding='utf-8'))
        cls.elf=SOURCE.read_bytes();cls.patches,cls.report=compile_draft(cls.elf,cls.new)
    def test_all_description_payloads_except_marker_translated(self):
        self.assertEqual(self.report['accepted'],3446)
        r=self.report['item_descriptions'];self.assertEqual(r['accepted'],566)
        self.assertEqual(r['new_descriptions'],25)
        self.assertEqual(self.new['description_review']['pending'],[])
        self.assertEqual(len(self.new['description_review']['preserved']),1)
    def test_previous_translation_groups_unchanged(self):
        allowed={'entries','item_descriptions','description_review','status','iso_name'}
        for key in self.old:
            if key not in allowed:self.assertEqual(self.old[key],self.new[key],key)
        current={e['id']:e for e in self.new['entries']}
        for entry in self.old['entries']:self.assertEqual(entry,current[entry['id']])
        self.assertEqual(len(current)-len(self.old['entries']),2)
    def test_dog_classes_use_coat_and_other_classes_use_driving(self):
        result=proof(self.elf,self.new['canine_status_context'])
        self.assertEqual(result['canine_class_indexes'],[6,7,8,9])
        for c in result['class_cases']:
            self.assertEqual(c['label_offset'],0x32b690 if c['class_index']>=6 else 0x32b680)
            self.assertEqual(c['argument'],123 if c['class_index']>=6 else 456)
    def test_unknown_class_or_tampered_canine_evidence_refused(self):
        for i in (-1,10):
            with self.assertRaises(ValueError):execute(self.elf,i)
        cfg=copy.deepcopy(self.new['canine_status_context']);cfg['instruction_windows'][0]['sha256']='bad'
        with self.assertRaises(ValueError):proof(self.elf,cfg)
    def test_save_directory_strings_never_translated(self):
        ids={e['id'] for e in self.new['entries']}
        for at in (0x320bf0,0x321628,0x322ce0):
            self.assertNotIn(f'elf.ui.{at:08x}',ids)
            self.assertFalse(any(p['resource']=='SLUS_212.93' and p['offset']<=at<p['offset']+len(p['before']) for p in self.patches))
    def test_all_resource_patches_disjoint_and_exactly_reversible(self):
        from interface_resources import original
        groups={}
        for p in self.patches:groups.setdefault(p['resource'],[]).append(p)
        for resource,group in groups.items():
            raw=original(resource);out=bytearray(raw);group.sort(key=lambda p:p['offset'])
            for a,b in zip(group,group[1:]):self.assertLessEqual(a['offset']+len(a['before']),b['offset'])
            for p in group:
                at=p['offset'];self.assertEqual(raw[at:at+len(p['before'])],p['before'])
                self.assertEqual(len(p['before']),len(p['after']));out[at:at+len(p['after'])]=p['after']
            for p in reversed(group):out[p['offset']:p['offset']+len(p['before'])]=p['before']
            self.assertEqual(out,raw)

if __name__=='__main__':unittest.main()
