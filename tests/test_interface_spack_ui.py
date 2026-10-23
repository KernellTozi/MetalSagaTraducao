import copy,json,struct,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from spack_ui import *

class SpackUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.draft=json.loads((ROOT/'translations/interface-v015.json').read_text(encoding='utf-8'))
        cls.cfg=cls.draft['spack_ui'];cls.elf=original('SLUS_212.93');cls.raw=original(RESOURCE)
        cls.table=counted_strings(cls.raw,TABLE_BASE,TABLE_SIZE,COUNT)
        cls.rows={r['pointer_ids'][0]:r for r in cls.table['entries']}
        cls.patches,cls.report=compile_ui(cls.elf,cls.cfg);cls.after=cls.patches[0]['after']
    def test_original_identity_and_exact_extent(self):
        before=self.raw[TABLE_BASE:TABLE_BASE+TABLE_SIZE]
        self.assertEqual(rebuild(before,self.table,{})[0],before)
        self.assertEqual(self.patches[0]['before'],before);self.assertEqual(len(self.after),8192)
        self.assertEqual(self.report['accepted'],278);self.assertEqual(self.report['changed_pointer_occurrences'],333)
        self.assertEqual(self.report['free_bytes'],236)
    def test_original_sda_pointer_instructions(self):
        self.assertEqual(execute_sda_pointer(self.elf,self.raw,1),0x35000)
        self.assertEqual(execute_sda_pointer(self.elf,self.raw[0x35000:],0),0x70)
    def test_original_lookup_instructions_all_378_ids_and_aliases(self):
        pointers={};seen=0
        for row in self.table['entries']:
            key=row['pointer_ids'][0];target=self.cfg['translations'].get(str(key))
            expected=encode(target['translation']) if target else bytes.fromhex(row['source_hex'])
            for index in row['pointer_ids']:
                at=execute_ui_pointer(self.elf,self.after,index);stop=self.after.index(0,at)
                self.assertEqual(self.after[at:stop],expected)
                pointers[index]=at;seen+=1
            self.assertEqual(len({pointers[i] for i in row['pointer_ids']}),1)
        self.assertEqual(seen,378);self.assertEqual(len(set(pointers.values())),317)
    def test_original_byte_length_instructions_for_every_unique_text(self):
        parsed=counted_strings(self.after,0,TABLE_SIZE,COUNT)
        for row in parsed['entries']:
            raw=bytes.fromhex(row['source_hex']);self.assertEqual(execute_byte_length(self.elf,raw),len(raw))
    def test_native_and_composed_values_are_immutable(self):
        policy=json.loads((ROOT/'translations/politica.json').read_text(encoding='utf-8'))
        for index in (2,3,142,143,144,161,170,261,370):
            with self.assertRaises(ValueError):validate_value(self.rows[index],'Teste',policy)
    def test_unknown_alias_and_source_drift_rejected(self):
        for key in ('7','999'):
            bad=copy.deepcopy(self.cfg);bad['translations'][key]=bad['translations']['5']
            with self.assertRaises(ValueError):compile_ui(self.elf,bad)
        for key in ('source_sha256','table_sha256'):
            bad=copy.deepcopy(self.cfg);bad[key]='0'*64
            with self.assertRaises(ValueError):compile_ui(self.elf,bad)
        bad=copy.deepcopy(self.cfg);bad['instruction_windows'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):compile_ui(self.elf,bad)
    def test_control_numeric_prefix_space_glyph_and_growth_guards(self):
        policy=json.loads((ROOT/'translations/politica.json').read_text(encoding='utf-8'))
        for index,text in ((219,'Trocou %s selos|por %%I%02d%s'),(219,'Trocou %d selos|por %%T%02d%s'),
            (274,'Alugue até 5 veículos'),(64,'comprado'),(11,'a'*32),(11,'Nome\0'),
            (15,'Principal'),(33,'Normal')):
            with self.assertRaises(ValueError,msg=str(index)):validate_value(self.rows[index],text,policy)
    def test_total_pool_overflow_is_rejected(self):
        with self.assertRaises(ValueError):rebuild(self.patches[0]['before'],self.table,{k:b'A'*500 for k in self.rows})
    def test_status_preserves_format_and_original_nul(self):
        p,r=compile_status(self.elf,self.draft['character_status']);p=p[0]
        self.assertEqual(len(p['before']),len(p['after']));self.assertEqual(p['after'][-1],0)
        self.assertEqual(controls(p['before'][:-1]),controls(p['after'].rstrip(b'\0')))
        bad=copy.deepcopy(self.draft['character_status']);bad['translation']=bad['translation'].replace('%4d','%s',1)
        with self.assertRaises(ValueError):compile_status(self.elf,bad)
    def test_prior_recipe_fields_unchanged(self):
        old=json.loads((ROOT/'translations/interface-v014.json').read_text(encoding='utf-8'))
        for key in old:
            if key not in ('status','iso_name'):self.assertEqual(old[key],self.draft[key],key)
    def test_compact_preflight_outputs_only_report_and_keeps_recipe_hashes(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'work') as temp:
            folder=Path(temp).resolve();self.assertTrue(folder.is_relative_to((ROOT/'work').resolve()))
            output=folder/'preflight'
            proc=subprocess.run([sys.executable,str(ROOT/'tools/build_translation_pilot.py'),'--draft',
                str(ROOT/'translations/regiao-inicial-v030.json'),'--interface-draft',str(ROOT/'translations/interface-v015.json'),
                '--output',str(output),'--compact-output'],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr[-2500:]);self.assertEqual({p.name for p in output.iterdir()},{'relatorio.json'})
            report=json.loads((output/'relatorio.json').read_text(encoding='utf-8'))
            self.assertTrue(report['valid']);self.assertEqual(report['output_mode'],'compact')
            self.assertEqual(report['interface']['accepted'],920);self.assertTrue(report['draft_sources'])

if __name__=='__main__':unittest.main()
