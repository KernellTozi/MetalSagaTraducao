import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from interface_text import SOURCE,compile_draft
from name_entry_text import catalog,compile_name_entry


class NameEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes()
        cls.draft=json.loads((ROOT/'translations/interface-v010.json').read_text(encoding='utf-8'))
        cls.config=cls.draft['name_entry']

    def test_exact_set_and_all_native_bytes_positions_preserved(self):
        rows=catalog(self.elf);patches,report=compile_name_entry(self.elf,self.config)
        self.assertEqual(len(patches),4)
        self.assertEqual(report['accepted'],4)
        rebuilt=bytearray(self.elf)
        for row,p in zip(rows,patches):
            self.assertEqual(len(p['before']),len(p['after']))
            self.assertEqual(p['before'][-1],0);self.assertEqual(p['after'][-1],0)
            if row['kind']=='legend':
                allowed={i for s in row['slots'] for i in range(s['offset'],s['offset']+s['size'])}
                for i,(a,b) in enumerate(zip(p['before'],p['after'])):
                    if i not in allowed:self.assertEqual(a,b)
                self.assertEqual([i for i,b in enumerate(p['before']) if b==0x81],
                                 [i for i,b in enumerate(p['after']) if b==0x81])
            else:self.assertEqual(p['after'].split(b'\0')[0],b'DIGITE SEU NOME')
            rebuilt[p['offset']:p['offset']+len(p['after'])]=p['after']
        for p in patches:rebuilt[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(rebuilt,self.elf)

    def test_bad_identity_order_slot_length_native_injection_and_labels_rejected(self):
        for case in ('hash','order','duplicate','offset','size','overflow','token','back','heading'):
            config=copy.deepcopy(self.config)
            if case=='hash':config['entries'][0]['source_sha256']='0'*64
            elif case=='order':config['entries'].reverse()
            elif case=='duplicate':config['entries'].append(config['entries'][0])
            elif case=='offset':config['entries'][1]['slots'][0]['offset']+=1
            elif case=='size':config['entries'][1]['slots'][0]['size']+=1
            elif case=='heading':config['entries'][0]['translation']='%s'
            elif case=='back':config['entries'][1]['slots'][3]['translation']='SAIR'
            else:config['entries'][1]['slots'][0]['translation']='INSERIR' if case=='overflow' else '\u3000'
            with self.subTest(case=case),self.assertRaises(ValueError):compile_name_entry(self.elf,config)

    def test_original_revision_and_native_bytes_bound(self):
        for offset in (0x177788,0x10a9d4,0x10e614,0x32a310):
            raw=bytearray(self.elf);raw[offset]^=1
            with self.assertRaises(ValueError):compile_name_entry(raw,self.config)

    def test_ui_parent_and_graphics_preserved_and_count(self):
        old=json.loads((ROOT/'translations/interface-v009.json').read_text(encoding='utf-8'))
        for key in set(old)-{'status','iso_name'}:self.assertEqual(old[key],self.draft[key],key)
        patches,report=compile_draft(self.elf,self.draft)
        self.assertEqual(report['accepted'],620)
        self.assertEqual(report['name_entry']['accepted'],4)
        self.assertEqual(sum(p['id'].startswith('name-entry.') for p in patches),4)


if __name__=='__main__':unittest.main()
