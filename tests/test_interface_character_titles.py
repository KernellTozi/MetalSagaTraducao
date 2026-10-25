import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from character_titles import *
from interface_text import SOURCE


class CharacterTitles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes();cls.config=json.loads((ROOT/'translations/interface-v032.json').read_text(encoding='utf-8'))['character_titles']
        cls.patches,cls.report=compile_titles(cls.elf,cls.config)
    def test_all_cells_reviewed_once_and_aliases_preserved(self):
        self.assertEqual(self.report['accepted'],73);self.assertEqual(self.report['preserved'],5)
        self.assertEqual(len(catalog(self.elf)),78)
        self.assertEqual(self.report['evidence']['nonempty_lookup_cases'],79)
        shared=[r for r in catalog(self.elf) if r['source']=='Pro Mechanic'][0]
        self.assertEqual(len(shared['references']),2)
        patch=[p for p in self.patches if p['id']==shared['id']][0]
        self.assertEqual(patch['after'].split(b'\0')[0],encode('Pro de oficina'))
    def test_original_lookup_caller_and_formatter_arguments(self):
        r=proof(self.elf);self.assertEqual(r['group_counts'],[47,7,7,8,8,1,1,1,1,1])
        self.assertEqual(r['original_maximum_title_bytes'],15)
        for group,index in ((-1,0),(10,0),(0,47),(1,7)):
            with self.assertRaises(ValueError):lookup(self.elf,group,index)
    def test_full_elf_apply_reverse_roundtrip_and_only_proved_cells_changed(self):
        out=bytearray(self.elf);last=0
        for p in sorted(self.patches,key=lambda p:p['offset']):
            at=p['offset'];self.assertGreaterEqual(at,last)
            self.assertEqual(out[last:at],self.elf[last:at]);self.assertEqual(out[at:at+len(p['before'])],p['before'])
            self.assertEqual(len(p['before']),len(p['after']));self.assertEqual(p['after'][-1],0)
            out[at:at+len(p['after'])]=p['after'];last=at+len(p['after'])
        self.assertEqual(out[last:],self.elf[last:])
        for r in catalog(self.elf):
            for ref in r['references']:self.assertEqual(lookup(out,ref['group'],ref['index']),r['offset']+0xff000)
        for p in reversed(self.patches):out[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(out,self.elf)
    def test_preserved_titles_empty_cells_and_all_pointer_bytes_unchanged(self):
        offsets={p['offset'] for p in self.patches}
        self.assertFalse(offsets&PRESERVED);self.assertNotIn(0x348c10,offsets)
        for p in self.patches:
            self.assertTrue(0x3198f0<=p['offset']<0x319d60 or 0x348bf8<=p['offset']<0x348c38)
    def test_unknown_duplicate_missing_hash_or_decision_refused(self):
        for mode in ('duplicate','missing','hash','decision','extra','code'):
            c=copy.deepcopy(self.config)
            if mode=='duplicate':c['entries'].append(c['entries'][0])
            elif mode=='missing':c['entries'].pop()
            elif mode=='hash':c['entries'][0]['source_sha256']='0'*64
            elif mode=='decision':c['preserved'].pop(next(iter(c['preserved'])))
            elif mode=='extra':c['extra']=1
            else:c['instruction_windows'][0]['sha256']='0'*64
            with self.subTest(mode=mode),self.assertRaises(ValueError):compile_titles(self.elf,c)
    def test_overflow_controls_unsupported_glyph_or_profession_removed_refused(self):
        for target in ('X'*16,'Hunter\nás','Hunter %s','Hunter Ó','Veterano'):
            c=copy.deepcopy(self.config);c['entries'][0]['translation']=target
            with self.subTest(target=target),self.assertRaises((ValueError,UnicodeError)):compile_titles(self.elf,c)
    def test_cell_table_and_instruction_drift_refused(self):
        for at in (0x3198ff,0x264478,0x264338,0x348c3c):
            changed=bytearray(self.elf);changed[at]^=1
            with self.subTest(at=at),self.assertRaises(ValueError):catalog(changed)
        changed=bytearray(self.elf);changed[0x6bb80]^=1
        with self.assertRaises(ValueError):proof(changed)
        from unittest.mock import patch
        with patch('interface_text.references',return_value={0x4188f1:[]}),self.assertRaises(ValueError):proof(self.elf)
        with patch('interface_text.references',return_value={}),self.assertRaises(ValueError):proof(self.elf)


if __name__=='__main__':unittest.main()
