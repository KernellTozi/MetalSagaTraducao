import copy
import json
import mmap
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from interface_text import SOURCE,compile_draft
from interface_resources import original,NDATA
from help_text import catalog,compile_help,restore_whitespace,TAGS
from weapon_terms import validate


class HelpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes()
        cls.recipe=json.loads((ROOT/'translations/interface-v004.json').read_text(encoding='utf-8'))
        cls.pages=catalog(cls.elf,original(NDATA))

    def test_all_pages_exact_markup_and_fixed_windows(self):
        patches,results=compile_help(self.elf,self.recipe['resource_texts']['help'])
        self.assertEqual(len(patches),44)
        raw=original(NDATA);out=bytearray(raw)
        for p in patches:
            self.assertEqual(raw[p['offset']:p['offset']+len(p['before'])],p['before'])
            self.assertEqual(len(p['before']),len(p['after']))
            self.assertEqual(TAGS.findall(p['before']),TAGS.findall(p['after']))
            self.assertEqual(p['before'].count(b'\r\n'),p['after'].count(b'\r\n'))
            out[p['offset']:p['offset']+len(p['after'])]=p['after']
        for p in patches:out[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(out,raw)

    def test_markup_numbers_percentage_names_newline_rejected(self):
        for before,target in ((b'<HTML>A<BR>B</HTML>','<HTML>A B</HTML>'),
                              (b'<HTML>50%%</HTML>','<HTML>60%%</HTML>'),
                              (b'<HTML>50%%</HTML>','<HTML>50%</HTML>'),
                              (b'<HTML>Hunter</HTML>','<HTML>Caçador</HTML>'),
                              (b'<HTML><IMG ALT=1>A</HTML>','<HTML><IMG ALT=2>A</HTML>'),
                              (b'<HTML><BR>A</HTML>','<HTML>\n<BR>A</HTML>'),
                              (b'<HTML>A</HTML>','<HTML>A</HTML>extra')):
            with self.subTest(target=target),self.assertRaises(ValueError):restore_whitespace(before,target)

    def test_bindings_duplicates_and_overflow_rejected(self):
        items=self.recipe['resource_texts']['help']
        with self.assertRaises(ValueError):compile_help(self.elf,items+[items[0]])
        d=copy.deepcopy(items[:1]);d[0]['source_sha256']='0'*64
        with self.assertRaises(ValueError):compile_help(self.elf,d)
        d=copy.deepcopy(items[:1]);d[0]['translation']=d[0]['translation'].replace('<HTML>','<HTML>'+'X'*10000)
        with self.assertRaises(ValueError):compile_help(self.elf,d)
        elf=bytearray(self.elf);elf[0xd4160]^=1
        with self.assertRaises(ValueError):catalog(elf,original(NDATA))

    def test_v003_preserved_except_explicit_revisions(self):
        old=json.loads((ROOT/'translations/interface-v003.json').read_text(encoding='utf-8'))
        current={e['id']:e for e in self.recipe['entries']}
        for e in old['entries']:
            if e['id']=='elf.ui.0032ced0':self.assertEqual(current[e['id']]['translation'],'Tiro MAIN')
            else:self.assertEqual(current[e['id']],e)
        for section in ('tables','diary'):
            if section=='tables':self.assertEqual(old['resource_texts'][section],self.recipe['resource_texts'][section]);continue
            new={e['id']:e for e in self.recipe['resource_texts'][section]}
            for e in old['resource_texts'][section]:
                expected=copy.deepcopy(e)
                if e['id']=='diary.056.body':expected['translation']=expected['translation'].replace('arma Sub','arma SUB')
                self.assertEqual(new[e['id']],expected)
        patches,r=compile_draft(self.elf,self.recipe)
        self.assertEqual((r['accepted'],r['elf_strings'],len(patches)),(519,277,423))

    def test_main_sub_se_guard(self):
        self.assertFalse(validate('Main gun / sub gun / SE','arma MAIN / SUB / SE'))
        self.assertTrue(validate('main\ngun','canhão'))
        self.assertTrue(validate('SEs','especiais'))
        self.assertFalse(validate('Not per se.','Não exatamente.'))
        self.assertTrue(validate('main gun and main cannon','MAIN'))

    def test_map_all_prior_records_and_metadata_preserved(self):
        from build_translation_pilot import load_draft,compile_draft as compile_map,SOURCE as MAP
        old,_=load_draft(ROOT/'translations/regiao-inicial-v029.json')
        new,_=load_draft(ROOT/'translations/regiao-inicial-v030.json')
        changed={k for k in old['translations'] if old['translations'][k]!=new['translations'][k]}
        self.assertEqual(changed,set(new['reviewed_changes']));self.assertEqual(len(changed),8)
        for key in ('deferred','aliases','scope','preservation_decisions','reinsertion_policy','layout_profile'):
            self.assertEqual(old.get(key),new.get(key))
        with MAP.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
            previous,_,old_report=compile_map(data,old)
            document,patches,r=compile_map(data,new)
        self.assertTrue(r['valid']);self.assertEqual(r['accepted'],5892)
        self.assertTrue(old_report['valid'])
        self.assertEqual(len(previous['entries']),len(document['entries']))
        for before,after in zip(previous['entries'],document['entries']):
            if before['id'] not in changed:self.assertEqual(before,after)
            else:
                for key in before:
                    if key!='segments':self.assertEqual(before[key],after[key])
                for a,b in zip(before['segments'],after['segments']):
                    for key in a:
                        if key!='translation':self.assertEqual(a[key],b[key])


if __name__=='__main__':unittest.main()
