import copy,json,struct,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from item_descriptions import *

class ItemDescriptions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.draft=json.loads((ROOT/'translations/interface-v017.json').read_text(encoding='utf-8'))
        cls.cfg=cls.draft['item_descriptions'];cls.elf=original('SLUS_212.93');cls.raw=original(RESOURCE)
        cls.rows=catalog(cls.raw);cls.patches,cls.report=compile_descriptions(cls.elf,cls.cfg)
        cls.after=bytearray(cls.raw)
        for p in cls.patches:cls.after[p['offset']:p['offset']+len(p['after'])]=p['after']
    def test_previous_recipe_unchanged(self):
        old=json.loads((ROOT/'translations/interface-v016.json').read_text(encoding='utf-8'))
        for k in old:
            if k not in ('status','iso_name'):self.assertEqual(old[k],self.draft[k],k)
        self.assertEqual(self.report['accepted'],114);self.assertEqual(self.report['item_occurrences'],126)
    def test_all_names_stats_aliases_and_source_boundaries_preserved(self):
        self.assertEqual(self.raw[:POOL],self.after[:POOL]);self.assertEqual(self.raw[POOL+SIZE:],self.after[POOL+SIZE:])
        self.assertEqual(len(self.raw),len(self.after))
        self.assertEqual(len(self.rows),567)
        actual=catalog(self.after)
        for a,b in zip(self.rows,actual):
            self.assertEqual(a['id'],b['id']);self.assertEqual(a['items'],b['items']);self.assertEqual(a['offset'],b['offset'])
    def test_original_forwarding_instructions_for_every_reference_and_readback(self):
        translated={x['id']:x for x in self.cfg['entries']}
        for row in self.rows:
            at=row['offset'];relative=at-POOL
            self.assertEqual(execute_description_pointer(self.elf,bytes(self.after[POOL:POOL+SIZE]),relative),relative)
            end=self.after.index(0,at);value=bytes(self.after[at:end]);target=translated.get(row['id'])
            self.assertEqual(value,encode(target['translation']) if target else bytes.fromhex(row['source_hex']))
            self.assertEqual(execute_byte_length(self.elf,value),len(value))
    def test_reverse_roundtrip(self):
        restored=self.after.copy()
        for p in self.patches:
            self.assertEqual(len(p['before']),len(p['after']))
            restored[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(restored,self.raw)
    def test_bindings_and_unknown_ids_fail_closed(self):
        for fault in ('policy','source_sha256','pool_sha256','window','field','item','duplicate','id'):
            cfg=copy.deepcopy(self.cfg)
            if fault in ('policy','source_sha256','pool_sha256'):cfg[fault]='bad'
            elif fault=='window':cfg['instruction_windows'][0]['sha256']='bad'
            elif fault=='field':cfg['entries'][0]['source_sha256']='bad'
            elif fault=='item':cfg['entries'][0]['item_records'][0]['id']=999
            elif fault=='duplicate':cfg['entries'].append(cfg['entries'][0])
            else:cfg['entries'][0]['id']='item.description.fffff'
            with self.subTest(fault=fault),self.assertRaises(ValueError):compile_descriptions(self.elf,cfg)
    def test_no_overflow_unknown_controls_or_lost_facts(self):
        for before,text in [(b'abc','texto longo'),(b'Hello','Oi\0'),(b'Hello','%N0'),(b'Hello','Oi\n'),
             (b'abc|def','abcdef'),(b'abc|def','abcd|e'),(b'150 damage','100 de dano'),
             (b'Scarlet gun','Arma'),(b'\x82\x60','A')]:
            with self.subTest(text=text),self.assertRaises(ValueError):validate_value(before,text)
    def test_invalid_reference_and_interior_alias_blocked(self):
        for offset in (SIZE,1):
            data=bytearray(self.raw);struct.pack_into('<I',data,ITEM_BASE+24,offset)
            with self.assertRaises(ValueError):catalog(data)

if __name__=='__main__':unittest.main()
