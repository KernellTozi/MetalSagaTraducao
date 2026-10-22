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

    def test_new_scene_names_and_wrapped_enemy_names(self):
        self.assertEqual(validate('Rosa, Carl, Sebastian, Arthur, Leon, Fang and Helga.',
                                  'Rosa, Carl, Sebastian, Arthur, Leon, Fang e Helga.'),[])
        self.assertTrue(validate('Rosa and Sebastian','Rosa e o mordomo'))
        self.assertEqual(validate('Iron\nSlugs and Magnum Cycles','Iron Slugs e Magnum\nCycles'),[])
        self.assertTrue(validate('Iron\nSlugs','lesmas de ferro'))
        self.assertTrue(validate('Aheh. Mmm...','Ah. Hum...'))

    def test_tanks_locations_and_researcher_names(self):
        self.assertEqual(validate('IS-3 KV-2 Buggy Doc Solomon Laura East Zero',
                                  'IS-3 KV-2 Buggy Doc Solomon Laura East Zero'),[])
        self.assertTrue(validate('IS-3 and KV-2','tanque pesado'))
        self.assertTrue(validate('East\nZero','Leste Zero'))

    def test_wanted_name_business_and_generic_transport_pod(self):
        self.assertTrue(validate('Trash Heap and Rent-a-Tank','Montão de Lixo e Aluguel'))
        self.assertEqual(validate('Alex at Ziggurat','Alex em Ziggurat'),[])
        self.assertEqual(validate('I have the transport pod.','Tenho a cápsula de transporte.'),[])

    def test_material_junk_does_not_override_preserved_monster_name(self):
        self.assertEqual(validate('Three Junk Zombies attacked me.','Três Junk Zombies me atacaram.'),[])
        self.assertTrue(validate('Junk Zombies and junk','Junk Zombies e lixo'))
        self.assertEqual(validate('Junk Zombies and junk','Junk Zombies e sucata'),[])
        self.assertTrue(validate('Junk Zombies','Zumbis de sucata'))

    def test_shiny_name_and_adjective_are_distinct(self):
        self.assertEqual(validate('something shiny','algo brilhando'),[])
        self.assertTrue(validate('Shiny is here','Brilhante está aqui'))
        self.assertEqual(validate('Shiny is here','Shiny está aqui'),[])
