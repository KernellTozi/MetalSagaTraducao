import copy
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from interface_text import SOURCE,compile_draft,embedded_catalog,catalog
from interface_resources import original,NDATA,DIARY,table_rows,TABLES,execute_count,compile_resources,sha
from gfi import encode,decode


class ResourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes()
        cls.recipe=json.loads((ROOT/'translations/interface-v003.json').read_text(encoding='utf-8'))

    def test_complete_lot_preserves_v002_and_has_expected_real_changes(self):
        old=json.loads((ROOT/'translations/interface-v002.json').read_text(encoding='utf-8'))
        current={e['id']:e for e in self.recipe['entries']}
        for entry in old['entries']:self.assertEqual(current[entry['id']],entry)
        patches,r=compile_draft(self.elf,self.recipe)
        self.assertEqual(r['accepted'],473);self.assertEqual(r['elf_strings'],275)
        self.assertEqual(r['resource_texts']['accepted'],198)
        self.assertEqual(len(patches),377)
        self.assertEqual(set(current)-{e['id'] for e in old['entries']},set(self.recipe['added_ids']))

    def test_original_counter_crlf_lf_cr_padding_and_accent_bytes(self):
        for raw,n in ((b'A\r\nB\r\n',2),(b'A\nB\n',2),(b'A\rB\r',2),
                      (encode('Não')+b'\r\n'+bytes(20),1)):
            self.assertEqual(execute_count(self.elf,raw),n)
        ndata=original(NDATA)
        for index,(at,size,n,_) in TABLES.items():self.assertEqual(execute_count(self.elf,ndata[at:at+size]),n)

    def test_resources_readback_reverse_and_original_counter_all_rows(self):
        patches,r=compile_resources(self.elf,self.recipe)
        for resource in (NDATA,DIARY):
            before=original(resource);after=bytearray(before);own=[p for p in patches if p['resource']==resource]
            for p in own:
                self.assertEqual(before[p['offset']:p['offset']+len(p['before'])],p['before'])
                after[p['offset']:p['offset']+len(p['after'])]=p['after']
            self.assertEqual(len(after),len(before))
            if resource==NDATA:
                for index,(at,size,n,_) in TABLES.items():
                    body=bytes(after[at:at+size]);self.assertEqual(execute_count(self.elf,body),n)
                    rows=body.rstrip(b'\0')[:-2].split(b'\r\n');self.assertEqual(len(rows),n)
                    for row,target in zip(rows,next(t['rows'] for t in self.recipe['resource_texts']['tables'] if t['index']==index)):
                        self.assertEqual(decode(row),target['translation'])
            for p in own:after[p['offset']:p['offset']+len(p['before'])]=p['before']
            self.assertEqual(after,before)

    def test_resource_tokens_ids_delimiters_and_budget_rejected(self):
        for case in ('token','order','newline','overflow','loaded-budget','count','binding'):
            d=copy.deepcopy(self.recipe);table=d['resource_texts']['tables'][0]
            if case=='token':table['rows'][23]['translation']=table['rows'][23]['translation'].replace('$MD$','$MP$')
            elif case=='order':table['rows'][0],table['rows'][1]=table['rows'][1],table['rows'][0]
            elif case=='newline':table['rows'][0]['translation']='A\r\nB'
            elif case=='overflow':table['rows'][0]['translation']='X'*512
            elif case=='loaded-budget':table['rows'][0]['translation']='X'*500
            elif case=='count':table['rows'].pop()
            else:d['resource_texts']['source_bindings'][NDATA]='0'*64
            with self.assertRaises(ValueError):compile_resources(self.elf,d)

    def test_diary_overflow_names_controls_and_native_fields_remain_blocked(self):
        d=copy.deepcopy(self.recipe);target=d['resource_texts']['diary'][0];target['translation']='X'*1000
        with self.assertRaisesRegex(ValueError,'slot overflow'):compile_resources(self.elf,d)
        d=copy.deepcopy(self.recipe);target=next(e for e in d['resource_texts']['diary'] if '%N1' in e['translation']);target['translation']=target['translation'].replace('%N1','%N2')
        with self.assertRaisesRegex(ValueError,'controls'):compile_resources(self.elf,d)
        from diary import fields
        raw=original(DIARY);item=next(e for e in fields(raw) if e['record']==16 and e['field']=='body')
        old=raw[item['offset']:item['offset']+item['capacity']+1].split(b'\0',1)[0]
        d=copy.deepcopy(self.recipe);d['resource_texts']['diary'].append({'id':'diary.016.body','source_sha256':sha(old),'translation':'MC Hamir?'})
        with self.assertRaisesRegex(ValueError,'Native diary'):compile_resources(self.elf,d)
        patches,_=compile_resources(self.elf,self.recipe)
        for key in ('diary.016.body','diary.031.body','diary.062.body'):
            self.assertNotIn(key,{p['id'] for p in patches})

    def test_embedded_literals_require_explicit_profile_and_six_values(self):
        self.assertNotIn('elf.ui.0032c6c0',{e['id'] for e in catalog(self.elf)['entries']})
        self.assertEqual(len(embedded_catalog(self.elf)),2)
        d=copy.deepcopy(self.recipe);d.pop('embedded_literal_profile')
        with self.assertRaises(KeyError):compile_draft(self.elf,d)
        d=copy.deepcopy(self.recipe);entry=next(e for e in d['entries'] if e['id']=='elf.ui.0032c6c0');entry['translation']=entry['translation'].replace('%4d','%3d',1)
        with self.assertRaisesRegex(ValueError,'format/control'):compile_draft(self.elf,d)

    def test_resource_protected_name_change_rejected(self):
        d=copy.deepcopy(self.recipe)
        entry=next(e for e in d['resource_texts']['diary'] if e['id']=='diary.020.body')
        entry['translation']=entry['translation'].replace('Kaede','Karla')
        with self.assertRaisesRegex(ValueError,'Resource terminology'):compile_resources(self.elf,d)


if __name__=='__main__':unittest.main()
