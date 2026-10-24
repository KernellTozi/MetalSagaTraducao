import copy,json,struct,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from spack_satcom import *

class Satcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.draft=json.loads((ROOT/'translations/interface-v016.json').read_text(encoding='utf-8'))
        cls.config=cls.draft['satcom_records'];cls.elf=original('SLUS_212.93');cls.raw=original(RESOURCE)
        cls.rows={k:parse_table(cls.raw,k) for k in TABLES}
        cls.patches,cls.report=compile_satcom(cls.elf,cls.config)
        cls.after=bytearray(cls.raw)
        for p in cls.patches:cls.after[p['offset']:p['offset']+len(p['after'])]=p['after']
    def test_counts_and_all_prior_fields_unchanged(self):
        old=json.loads((ROOT/'translations/interface-v015.json').read_text(encoding='utf-8'))
        for key in old:
            if key not in ('status','iso_name'):self.assertEqual(old[key],self.draft[key],key)
        self.assertEqual(self.report['accepted'],119)
        self.assertEqual(self.report['mail_records'],41);self.assertEqual(self.report['wanted_records'],40)
        self.assertEqual(len(self.patches),81)
    def test_identity_roundtrip_and_record_metadata(self):
        for kind,rows in self.rows.items():
            for row in rows:self.assertEqual(rebuild(row,kind,{}),row['raw'])
        for p in self.patches:
            self.assertEqual(len(p['before']),len(p['after']))
            self.assertEqual(p['before'][:4 if '.mail.' in p['id'] else 44],p['after'][:4 if '.mail.' in p['id'] else 44])
        restored=self.after.copy()
        for p in self.patches:restored[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(restored,self.raw)
        # Last mail has an opaque C1 tail. It never becomes capacity.
        self.assertEqual(self.after[0x8860c:0x88610],self.raw[0x8860c:0x88610])
    def test_outer_offsets_names_and_source_control_sequence(self):
        targets={e['id']:e['translation'] for e in self.config['entries']}
        for kind,(_,base,size,count) in TABLES.items():
            self.assertEqual(self.raw[base:base+4+count*4],self.after[base:base+4+count*4])
            actual=parse_table(self.after,kind,translated=True)
            for before,after in zip(self.rows[kind],actual):
                locked='sender' if kind=='mail' else 'name'
                self.assertEqual(before['fields'][locked],after['fields'][locked])
                for field in ('subject','body') if kind=='mail' else ('body',):
                    old=before['fields'][field]['raw'];new=after['fields'][field]['raw']
                    key=f"spack.{kind}.{before['id']:03d}.{field}"
                    self.assertEqual(new,encode(targets[key]) if key in targets else old)
                    self.assertEqual(tokens(old),tokens(new));self.assertLessEqual(len(new),len(old))
    def test_original_mail_getter_all_original_and_translated_records(self):
        _,base,size,_=TABLES['mail']
        for raw in (self.raw,self.after):
            rows=parse_table(raw,'mail',translated=raw is self.after)
            for row in rows:
                pointers=execute_mail_getter(self.elf,bytes(raw[base:base+size]),row['id'])
                for field in ('sender','subject','body'):
                    self.assertEqual(pointers[field],row['offset']-base+row['fields'][field]['relative'])
    def test_original_sda_access_and_all_text_byte_lengths(self):
        for kind,(entry,base,size,_) in TABLES.items():
            self.assertEqual(execute_sda_pointer(self.elf,self.raw[0x35000:],entry),base-0x35000)
            for row in parse_table(self.after,kind,translated=True):
                for value in row['fields'].values():
                    self.assertEqual(execute_byte_length(self.elf,value['raw']),len(value['raw']))
    def test_source_and_instruction_bindings(self):
        for path in ('source_sha256','policy','window','table','field','record'):
            cfg=copy.deepcopy(self.config)
            if path in ('source_sha256','policy'):cfg[path]='bad'
            elif path=='window':cfg['instruction_windows'][0]['sha256']='0'*64
            elif path=='table':cfg['table_sha256']['mail']='0'*64
            elif path=='field':cfg['entries'][0]['source_sha256']='0'*64
            else:cfg['entries'][0]['record_sha256']='0'*64
            with self.subTest(path=path),self.assertRaises(ValueError):compile_satcom(self.elf,cfg)
    def test_immutable_names_unknown_fields_duplicates_and_ids(self):
        for key in ('spack.mail.000.sender','spack.wanted.000.name','spack.mail.999.body','spack.mail.0.body'):
            cfg=copy.deepcopy(self.config);cfg['entries'][0]['id']=key
            with self.subTest(key=key),self.assertRaises(ValueError):compile_satcom(self.elf,cfg)
        cfg=copy.deepcopy(self.config);cfg['entries'].append(copy.deepcopy(cfg['entries'][0]))
        with self.assertRaises(ValueError):compile_satcom(self.elf,cfg)
    def test_text_budget_tokens_numbers_names_and_native_guards(self):
        for before,text in [(b'Hi %N0|Bye','Oi|%N0!'),(b'Hi %N0','Oi %N1'),(b'Bye','Oi\0'),
                            (b'30 minutes','20 minutos'),(b'Jack and Jack','Jack'),(b'MAIN gun','Arma'),
                            (b'1234567890','uma frase longa'),(b'abcde|fghij','abcdef|ghi'),
                            (b'junk','lixo'),(b'junkyard','sucata'),(b'Suicide Bomber','Bombardeiro')]:
            with self.subTest(text=text),self.assertRaises(ValueError):validate_text(before,text,'mail','body')
        modified=bytearray(self.raw);modified[self.rows['mail'][0]['offset']+4]=0x82
        with self.assertRaises(ValueError):parse_table(modified,'mail')
    def test_bad_boundaries_and_opaque_tail_not_silently_claimed(self):
        for at,value in [(0x86700,40),(0x86704,0x04),(0x88610+4,0xffffff),(0x8860f,0xff)]:
            raw=bytearray(self.raw)
            if at==0x8860f:raw[at]=value
            else:struct.pack_into('<I',raw,at,value)
            with self.subTest(at=at),self.assertRaises(ValueError):parse_table(raw,'mail' if at<0x88610 else 'wanted')

if __name__=='__main__':unittest.main()
