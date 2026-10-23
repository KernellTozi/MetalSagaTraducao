import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from help_index import catalog,compile_index,parse,OFFSET,SIZE
from interface_resources import original,NDATA
from interface_text import SOURCE,compile_draft
from weapon_terms import validate


class IndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes();cls.raw=original(NDATA)
        cls.recipe=json.loads((ROOT/'translations/interface-v005.json').read_text(encoding='utf-8'))
        cls.config=cls.recipe['resource_texts']['help_index']

    def test_full_index_linkage_and_readback(self):
        source=catalog(self.elf,self.raw);patches,results=compile_index(self.elf,self.config)
        self.assertEqual(len(source['rows']),56);self.assertEqual(len(results),53)
        self.assertEqual(len({r['reference'] for r in source['rows'] if r['kind']=='page'}),44)
        p=patches[0];self.assertEqual(p['before'],self.raw[OFFSET:OFFSET+SIZE]);self.assertEqual(len(p['after']),SIZE)
        after=parse(p['after']);self.assertEqual([r['text'] for r in after],[r['translation'] for r in self.config['rows']])
        for a,b in zip(source['rows'],after):
            self.assertEqual((a['prefix'],a['category_row']),(b['prefix'],b['category_row']))
        modified=bytearray(self.raw);modified[OFFSET:OFFSET+SIZE]=p['after'];modified[OFFSET:OFFSET+SIZE]=p['before']
        self.assertEqual(modified,self.raw)

    def test_bad_bindings_order_delimiters_and_overflow_rejected(self):
        for case in ('binding','order','count','comma','tab','newline','empty','overflow','terms'):
            d=copy.deepcopy(self.config)
            if case=='binding':d['source_sha256']='0'*64
            elif case=='order':d['rows'][0],d['rows'][1]=d['rows'][1],d['rows'][0]
            elif case=='count':d['rows'].pop()
            else:d['rows'][14]['translation']={'comma':'MAIN,SUB','tab':'MAIN\tSUB','newline':'MAIN\nSUB','empty':' ',
                'overflow':'MAIN SUB '+'X'*1000,'terms':'Principal x auxiliar'}[case]
            with self.subTest(case=case),self.assertRaises(ValueError):compile_index(self.elf,d)

    def test_v004_all_text_preserved_and_new_counts(self):
        old=json.loads((ROOT/'translations/interface-v004.json').read_text(encoding='utf-8'))
        self.assertEqual(self.recipe['entries'][:-1],old['entries'])
        for key in old['resource_texts']:self.assertEqual(self.recipe['resource_texts'][key],old['resource_texts'][key])
        self.assertEqual(self.recipe['base_dialogue_draft'],old['base_dialogue_draft'])
        patches,r=compile_draft(self.elf,self.recipe)
        self.assertEqual((r['accepted'],r['elf_strings'],len(patches)),(573,278,425))

    def test_grammar_and_main_sub_rule(self):
        for raw in (b'000,No category\n',b'9999,A\r\n',b'9999,A',b'9999,A\n\t00,B\n'):
            with self.assertRaises(ValueError):parse(raw)
        self.assertTrue(validate('Main vs Sub','Principal x secundária'))
        self.assertFalse(validate('Main vs Sub','MAIN x SUB'))
        self.assertTrue(validate('Main %d Sub %d SE %d','MAIN %d Sub %d SE %d'))


if __name__=='__main__':unittest.main()
