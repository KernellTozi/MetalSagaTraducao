import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from translation_policy import validate


class PolicyTests(unittest.TestCase):
    def test_names_professions_and_expressions(self):
        self.assertEqual(validate('Nina, a hunter. *sigh* Ha ha!','Nina, uma Hunter. *sigh* Ha ha!'),[])
        self.assertTrue(validate('Scarlet, Red Fox, Soldier.','Scarlet, Raposa Vermelha, soldado.'))
        self.assertTrue(validate('*sigh*','*suspiro*'))
        self.assertTrue(validate('Hahaha!','Risada!'))

    def test_junk_material_and_city_exception(self):
        self.assertEqual(validate('junk in Junkyard','sucata em Junkyard'),[])
        self.assertTrue(validate('junk in Junkyard','lixo em Sucata'))
        self.assertEqual(validate('Junkyard','Junkyard'),[])
        self.assertEqual(validate('trash','lixo'),[])

    def test_existing_loanwords_and_unique_names(self):
        self.assertEqual(validate('punk upgrade Gibson LOVE machine','punk upgrade Gibson LOVE machine'),[])
        self.assertTrue(validate('upgrade Gibson','melhoria guitarra'))
