import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from description_percent import *
from interface_text import SOURCE as ELF
from item_descriptions import original,RESOURCE


class LiteralDescriptionPercent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=ELF.read_bytes();cls.raw=original(RESOURCE)
        cls.recipe=json.loads((ROOT/'translations/interface-v028.json').read_text(encoding='utf-8'))
        cls.config=cls.recipe['item_descriptions']['literal_percent']
    def test_original_case_emits_literal_and_does_not_read_arguments(self):
        r=execute_percent_case(self.elf)
        self.assertEqual((r['emitted_byte'],r['emitted_length'],r['format_bytes_consumed']),(37,1,1))
        self.assertTrue(r['argument_pointer_unchanged']);self.assertEqual(r['argument_memory_reads'],0)
        self.assertEqual(len(r['stores']),4)
    def test_exact_source_and_code_windows_bound(self):
        self.assertEqual(proof(self.elf,self.raw,self.config)['policy'],POLICY)
        bad=copy.deepcopy(self.config);bad['instruction_windows'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):proof(self.elf,self.raw,bad)
        raw=bytearray(self.raw);raw[POOL+0x3226]^=1
        with self.assertRaises(ValueError):proof(self.elf,raw,self.config)
    def test_reviewed_translation_preserves_probability_and_literal_bytes(self):
        target='Impede a fuga de inimigos|em 80%% das vezes.'
        value=validate_value(SOURCE,target)
        self.assertIn(b'80%%',value);self.assertEqual(value.count(b'%'),2)
        self.assertEqual(value.count(b'|'),1)
    def test_printf_commands_other_probabilities_and_new_delimiters_refused(self):
        for target in ('Impede a fuga|em 80% das vezes.','Impede a fuga|em 80%% %s.',
            'Impede a fuga|em 90%% das vezes.','Impede a fuga|em 80%%\0.',
            'Impede a fuga|em 80%% %% das vezes.'):
            with self.subTest(target=target),self.assertRaises(ValueError):validate_value(SOURCE,target)
        with self.assertRaises(ValueError):validate_value(b'Other 80%%',target)
    def test_ordinary_policy_still_blocks_all_percent_strings(self):
        from description_pool import validate_value as ordinary
        with self.assertRaises(ValueError):ordinary(SOURCE,'Impede a fuga|em 80%% das vezes.')

if __name__=='__main__':unittest.main()
