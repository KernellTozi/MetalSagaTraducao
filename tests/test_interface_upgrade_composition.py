import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from item_descriptions import original
from spack_composition import TEXT,SOURCE,POLICY,binding,proof,execute_arguments
from spack_ui import compile_ui,validate_value
from plan_interface_menus import counted_strings,TABLE_BASE,TABLE_SIZE,COUNT
from gfi import decode,encode

class UpgradeComposition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.draft=json.loads((ROOT/'translations/interface-v020.json').read_text(encoding='utf-8'))
        cls.elf=original('SLUS_212.93');cls.raw=original('DATA/S/S_PACK.SDA')
        cls.patches,cls.report=compile_ui(cls.elf,cls.draft['spack_ui'])
        cls.before=cls.raw[TABLE_BASE:TABLE_BASE+TABLE_SIZE];cls.after=cls.patches[0]['after']
        cls.table=counted_strings(cls.before,0,TABLE_SIZE,COUNT)
        cls.rows={i:r for r in cls.table['entries'] for i in r['pointer_ids']}
        cls.result=counted_strings(cls.after,0,TABLE_SIZE,COUNT)
        cls.new={i:r for r in cls.result['entries'] for i in r['pointer_ids']}
    def test_only_exact_composition_newly_enabled(self):
        row=self.rows[142];policy=json.loads((ROOT/'translations/politica.json').read_text(encoding='utf-8'))
        self.assertEqual(bytes.fromhex(row['source_hex']),SOURCE)
        with self.assertRaises(ValueError):validate_value(row,TEXT,policy)
        self.assertEqual(decode(validate_value(row,TEXT,policy,composition=True)),TEXT)
        with self.assertRaises(ValueError):validate_value(row,TEXT+'!',policy,composition=True)
        for index in (143,144,145,146):
            with self.assertRaises(ValueError):validate_value(self.rows[index],'Outro',policy,composition=True)
    def test_original_argument_forwarding_all_sixteen_states(self):
        for a in range(4):
            for p in range(4):
                regs=execute_arguments(self.elf,self.after,a,p)
                self.assertEqual(regs['attribute_pointer'],self.new[[22,29,28,31][a]]['offset'])
                self.assertEqual(regs['prefix_pointer'],self.new[[143,144,145,146][p]]['offset'])
                self.assertEqual((regs['format_pointer'],regs['item_number'],regs['item_name_pointer']),(0x610000,7,0x620000))
                attribute=decode(bytes.fromhex(self.new[[22,29,28,31][a]]['source_hex']))
                prefix=decode(bytes.fromhex(self.new[[143,144,145,146][p]]['source_hex']))
                # Python formats the fixture for lexical verification only; it
                # does not emulate the game's sprintf or its expanded buffers.
                rendered=TEXT%(7,'Item',attribute,prefix)
                self.assertIn('incremento' if p in (0,2) else 'decremento',rendered)
                self.assertNotIn('creased',rendered)
                prior=SOURCE.decode('ascii')%(7,'Item',attribute,prefix)
                self.assertLessEqual(len(encode(rendered)),len(encode(prior)))
        with self.assertRaises(ValueError):execute_arguments(self.elf,self.after,4,0)
    def test_prefix_aliases_preserved_and_old_recipe_reproducible(self):
        for i in (143,144,145,146):
            self.assertEqual(self.new[i]['source_hex'],self.rows[i]['source_hex'])
            self.assertEqual(self.new[i]['pointer_ids'],self.rows[i]['pointer_ids'])
        old=json.loads((ROOT/'translations/interface-v019.json').read_text(encoding='utf-8'))
        _,report=compile_ui(self.elf,old['spack_ui']);self.assertEqual(report['accepted'],278)
        self.assertNotIn('composition',report)
    def test_source_windows_arrays_and_opt_in_binding(self):
        self.assertEqual(proof(self.elf,self.draft['spack_ui']['composition'])['policy'],POLICY)
        bad=copy.deepcopy(self.draft['spack_ui']);bad['composition']['windows'][0]['sha256']='bad'
        with self.assertRaises(ValueError):compile_ui(self.elf,bad)
        bad=copy.deepcopy(self.draft['spack_ui']);del bad['composition']
        with self.assertRaises(ValueError):compile_ui(self.elf,bad)
        bad=copy.deepcopy(self.draft['spack_ui']);del bad['translations']['142']
        with self.assertRaises(ValueError):compile_ui(self.elf,bad)

if __name__=='__main__':unittest.main()
