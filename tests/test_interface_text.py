import copy
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from interface_text import SOURCE,catalog,compile_draft,sections,controls
from gfi import encode,decode


class InterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=SOURCE.read_bytes()
        cls.cat=catalog(cls.data)
        cls.rows={e['id']:e for e in cls.cat['entries']}
        cls.recipe=json.loads((ROOT/'translations/interface-v001.json').read_text(encoding='utf-8'))

    def one(self,key):
        draft=copy.deepcopy(self.recipe)
        draft['entries']=[copy.deepcopy(next(e for e in draft['entries'] if e['id']==key))]
        return draft

    def test_reviewed_recipe_fixed_addresses_readback_and_reverse_roundtrip(self):
        patches,report=compile_draft(self.data,self.recipe)
        self.assertEqual(report['accepted'],88)
        output=bytearray(self.data)
        for p in patches:
            self.assertEqual(self.data[p['offset']:p['offset']+len(p['before'])],p['before'])
            self.assertEqual(len(p['before']),len(p['after']))
            self.assertEqual(p['after'][-1:],b'\0')
            output[p['offset']:p['offset']+len(p['after'])]=p['after']
            old=self.rows[p['id']]
            self.assertEqual(controls(bytes.fromhex(old['source_hex'])),controls(p['after'].split(b'\0',1)[0]))
        self.assertEqual(sections(output),sections(self.data))
        for p in patches:output[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(output,self.data)

    def test_identity_revision_and_duplicate_rejected(self):
        draft=self.one('elf.ui.0032d188');draft['entries'][0]['source_sha256']='0'*64
        with self.assertRaises(ValueError):compile_draft(self.data,draft)
        draft=self.one('elf.ui.0032d188');draft['entries']*=2
        with self.assertRaises(ValueError):compile_draft(self.data,draft)
        with self.assertRaises(ValueError):compile_draft(self.data[:-1]+b'X',self.recipe)

    def test_printf_and_separator_changes_rejected(self):
        for key,text in (('elf.ui.0032cce8','Qual %d original?'),
                         ('elf.ui.0032d998','Veja as lojas'),
                         ('elf.ui.0032cc40','Estilo|Set1/Set2')):
            draft=self.one(key);draft['entries'][0]['translation']=text
            with self.assertRaisesRegex(ValueError,'format/control'):compile_draft(self.data,draft)
        with self.assertRaises(ValueError):controls(b'100%')
        with self.assertRaises(ValueError):controls(b'%n')

    def test_overflow_unknown_glyph_and_empty_target_rejected(self):
        for text in ('Mensagens','🙂',''):
            draft=self.one('elf.ui.003497c0');draft['entries'][0]['translation']=text
            with self.assertRaises(ValueError):compile_draft(self.data,draft)

    def test_interior_alias_and_unreferenced_candidate_stay_pending(self):
        for key in ('elf.ui.00349820','elf.ui.0032c000'):
            old=self.rows[key];self.assertEqual(old['status'],'pending')
            draft=copy.deepcopy(self.recipe);draft['entries']=[{'id':key,'source_sha256':old['source_sha256'],
                'group':'test','translation':'Oi'}]
            with self.assertRaisesRegex(ValueError,'reference evidence'):compile_draft(self.data,draft)

    def test_catalog_does_not_approve_debug_or_all_ui(self):
        self.assertGreater(len(self.cat['entries']),88)
        self.assertTrue(any(e['source']=='NullDevice' for e in self.cat['entries']))
        selected={e['id'] for e in self.recipe['entries']}
        self.assertTrue(all(self.rows[key]['source']!='NullDevice' for key in selected))
        for key in selected:
            self.assertTrue(self.rows[key]['references'])
            self.assertFalse(self.rows[key]['interior_references'])

    def test_project_glyphs_do_not_normalize_to_external_codec(self):
        text='Opções do diário'
        raw=encode(text)
        self.assertEqual(decode(raw),text)
        self.assertNotEqual(raw,text.encode('utf-8'))
        self.assertIn(bytes.fromhex('8240'),encode('ç'))

    def test_leading_alignment_spaces_preserved(self):
        draft=self.one('elf.ui.0032ca60');draft['entries'][0]['translation']='Sem msg'
        with self.assertRaisesRegex(ValueError,'alignment'):compile_draft(self.data,draft)

    def test_v002_preserves_v001_and_exact_new_ids(self):
        draft=json.loads((ROOT/'translations/interface-v002.json').read_text(encoding='utf-8'))
        by_id={e['id']:e for e in draft['entries']}
        for old in self.recipe['entries']:self.assertEqual(by_id[old['id']],old)
        self.assertEqual(set(by_id)-{e['id'] for e in self.recipe['entries']},set(draft['added_ids']))
        patches,report=compile_draft(self.data,draft)
        self.assertEqual(report['accepted'],273)
        self.assertEqual(len(draft['added_ids']),185)
        self.assertEqual(len(patches),len(by_id))

    def test_trailing_alignment_spaces_preserved(self):
        draft=json.loads((ROOT/'translations/interface-v002.json').read_text(encoding='utf-8'))
        draft['entries']=[next(e for e in draft['entries'] if e['id']=='elf.ui.00349960')]
        draft['entries'][0]['translation']='Grana'
        with self.assertRaisesRegex(ValueError,'trailing alignment'):compile_draft(self.data,draft)


if __name__=='__main__':unittest.main()
