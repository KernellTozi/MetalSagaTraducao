import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from install_texts import *

class InstallerText(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.draft=json.loads((ROOT/'translations/interface-v021.json').read_text(encoding='utf-8'))
        cls.cfg=cls.draft['install_texts'];cls.elf=original('SLUS_212.93');cls.raw=original(NDATA)
        cls.patches,cls.report=compile_install(cls.elf,cls.cfg)
    def test_all_rows_variable_token_and_original_counter(self):
        self.assertEqual(self.report['accepted'],17);self.assertEqual(self.report['used_bytes'],804)
        p=self.patches[0];self.assertEqual((p['offset'],len(p['before']),len(p['after'])),(START,SIZE,SIZE))
        self.assertEqual(execute_count(self.elf,p['after']),17)
        source=rows(self.raw,self.elf);target=p['after'].split(b'\0',1)[0][:-2].split(b'\r\n')
        for a,b,t in zip(source,target,self.cfg['rows']):
            self.assertEqual(tokens(a),tokens(b));self.assertEqual(decode(b),t['translation'])
        self.assertEqual(sum(b'%INSTALLSIZE%' in s for s in target),2)
    def test_source_descriptor_and_external_padding_unchanged(self):
        out=bytearray(self.raw);p=self.patches[0];out[START:START+SIZE]=p['after']
        self.assertEqual(out[:START],self.raw[:START]);self.assertEqual(out[START+SIZE:],self.raw[START+SIZE:])
        out[START:START+SIZE]=p['before'];self.assertEqual(out,self.raw)
        self.assertEqual(struct.unpack_from('<II',self.elf,DESCRIPTOR),(START,SIZE))
    def test_source_and_exact_consumer_binding_fail_closed(self):
        for field in ('policy','source_sha256','table_sha256','instruction_windows'):
            bad=copy.deepcopy(self.cfg);bad[field]='bad'
            with self.subTest(field=field),self.assertRaises(ValueError):compile_install(self.elf,bad)
    def test_row_order_counts_hashes_and_unknown_metadata_rejected(self):
        for kind in ('order','count','hash','extra'):
            bad=copy.deepcopy(self.cfg)
            if kind=='order':bad['rows'][0],bad['rows'][1]=bad['rows'][1],bad['rows'][0]
            elif kind=='count':bad['rows'].pop()
            elif kind=='hash':bad['rows'][0]['source_sha256']='bad'
            else:bad['rows'][0]['extra']='unreviewed'
            with self.subTest(kind=kind),self.assertRaises(ValueError):compile_install(self.elf,bad)
    def test_token_changes_delimiters_and_loaded_size_rejected(self):
        for text in ('HDD %INSTALLSIZE%\n','HDD %OTHER%','HDD 999MB','a'*512):
            bad=copy.deepcopy(self.cfg);bad['rows'][0]['translation']=text
            with self.subTest(text=text),self.assertRaises(ValueError):compile_install(self.elf,bad)
        bad=copy.deepcopy(self.cfg)
        for row in bad['rows']:row['translation']='x'*self.report['column_ceiling']
        with self.assertRaises(ValueError):compile_install(self.elf,bad)
    def test_existing_resource_profile_does_not_admit_table_twelve(self):
        from interface_resources import table_rows
        with self.assertRaises(ValueError):table_rows(self.raw,self.elf,12)
        # Choice rows are variable records in this table, not two-byte slots.
        self.assertEqual(self.cfg['rows'][14]['translation'],'Não')

if __name__=='__main__':unittest.main()
