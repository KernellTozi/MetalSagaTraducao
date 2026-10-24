import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from item_names import *

class GenericNames(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.draft=json.loads((ROOT/'translations/interface-v020.json').read_text(encoding='utf-8'))
        cls.cfg=cls.draft['item_names'];cls.raw=original(RESOURCE);cls.elf=original('SLUS_212.93')
        cls.rows=catalog(cls.raw);cls.byid={r['id']:r for r in cls.rows}
        cls.patches,cls.report=compile_names(cls.elf,cls.cfg)
    def test_proven_record_topology_and_original_maximum(self):
        self.assertEqual(len(self.rows),1349);self.assertEqual(sum(not r['empty'] for r in self.rows),1041)
        self.assertEqual(execute_table_bounds(self.raw),(0x820,1349*128))
        self.assertEqual(max(r['source_bytes'] for r in self.rows),16)
        self.assertEqual(self.report['accepted'],189);self.assertEqual(self.report['unique_translated_labels'],183)
    def test_original_getter_all_indices_and_range(self):
        for index in range(ITEM_COUNT):self.assertEqual(execute_record_pointer(self.elf,index),index*128)
        for index in (-1,ITEM_COUNT):
            with self.assertRaises(ValueError):execute_record_pointer(self.elf,index)
    def test_only_original_name_slots_changed_and_complete_roundtrip(self):
        after=bytearray(self.raw);targets={r['id']:r for r in self.cfg['entries']}
        for p in self.patches:
            at=p['offset'];self.assertEqual(after[at:at+len(p['before'])],p['before'])
            self.assertEqual(len(p['before']),len(p['after']));after[at:at+len(p['after'])]=p['after']
        for row in self.rows:
            at=row['offset'];name=bytes(after[at:at+24]).split(b'\0')[0]
            self.assertEqual(name,encode(targets[row['id']]['translation']) if row['id'] in targets else bytes.fromhex(row['source_hex']))
            self.assertEqual(after[at+24:at+128],self.raw[at+24:at+128])
        for p in reversed(self.patches):after[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(after,self.raw)
    def test_protected_weapons_engines_and_unique_names_stay_blocked(self):
        for index in (1,48,75,190,200,300,309,489,659,692,712,715,725,726,752,801,929,949,950,990,1022,1046):
            row=self.rows[index]
            with self.subTest(index=index),self.assertRaises(ValueError):validate_value(row,'Teste')
    def test_bound_records_policy_and_editorial_metadata_fail_closed(self):
        for change in ('source','table','window','policy','record','unknown','duplicate','group'):
            bad=copy.deepcopy(self.cfg)
            if change=='source':bad['source_sha256']='bad'
            elif change=='table':bad['table_sha256']='bad'
            elif change=='window':bad['instruction_windows'][0]['sha256']='bad'
            elif change=='policy':bad['policy']='unknown'
            elif change=='record':bad['entries'][0]['record_sha256']='bad'
            elif change=='unknown':bad['entries'][0]['extra']='unreviewed'
            elif change=='duplicate':bad['entries'].append(copy.deepcopy(bad['entries'][0]))
            else:bad['entries'][0]['group']='unknown'
            with self.subTest(change=change),self.assertRaises(ValueError):compile_names(self.elf,bad)
    def test_same_source_labels_cannot_diverge(self):
        bad=copy.deepcopy(self.cfg)
        row=next(e for e in bad['entries'] if e['id']=='item.name.0394');row['translation']='Fungo'
        with self.assertRaisesRegex(ValueError,'Shared item name'):compile_names(self.elf,bad)
    def test_controls_unsupported_glyph_numbers_and_growth_rejected(self):
        row=self.byid['item.name.0991']
        for target in ('Foto 2','Foto 1\n','%s','Foto|1','Ó 1','x'*17):
            with self.subTest(target=target),self.assertRaises(ValueError):validate_value(row,target)
        self.assertEqual(validate_value(row,'Foto 1'),b'Foto 1')
        with self.assertRaisesRegex(ValueError,'level markers'):
            validate_value(self.byid['item.name.0853'],'Reparo I')
        row=copy.deepcopy(self.byid['item.name.0991']);row['source_hex']=b'%s'.hex()
        with self.assertRaisesRegex(ValueError,'Variable/control'):validate_value(row,'a')
    def test_review_accounting_disjoint_and_bound(self):
        review=self.draft['item_name_review'];validate_review(review,self.cfg,self.rows)
        for change in ('count','overlap','hash'):
            bad=copy.deepcopy(review)
            if change=='count':bad['selected']+=1
            elif change=='overlap':bad['pending'][0]['id']=self.cfg['entries'][0]['id']
            else:bad['pending'][0]['source_sha256']='bad'
            with self.subTest(change=change),self.assertRaises(ValueError):validate_review(bad,self.cfg,self.rows)
    def test_accent_payload_byte_is_not_an_ascii_level_marker(self):
        self.assertEqual(validate_value(self.byid['item.name.0783'],'Maiô'),encode('Maiô'))
        self.assertIn(b'I',encode('Maiô'))

if __name__=='__main__':unittest.main()
