import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import name_source_paths as n
from interface_text import SOURCE


class NameSourcePaths(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes()
        cls.result=n.investigate()

    def test_virtual_descriptors_bind_four_distinct_paths(self):
        rows=self.result['proof']['virtual_descriptors']
        self.assertEqual([r['getter_offset'] for r in rows],[0x79eb8,0x7a3b0,0x7f6c0,0x827c8])
        self.assertTrue(all(r['adjustment']==0 for r in rows))

    def test_original_initializer_executes_39_stores_and_real_virtual_getters(self):
        r=self.result['N_table_initialization']
        self.assertEqual((r['entries'],r['actor_entries'],r['tank_entries']),(39,10,29))
        self.assertEqual(len(r['writes']),39)
        self.assertEqual([w['address'] for w in r['writes']],[n.TABLE+4*i for i in range(39)])
        self.assertTrue(r['original_virtual_getters_executed'])
        self.assertTrue(r['surrounding_guards_unchanged'])
        self.assertIn(0x7f6c8,r['instruction_offsets'])
        self.assertIn(0x827cc,r['instruction_offsets'])

    def test_pool_boundary_and_N0_pointer_are_exact_but_name_length_unproved(self):
        r=self.result['N_table_initialization'];p=r['synthetic_pointers']
        self.assertEqual(p[0],0x600130)
        self.assertEqual(p[9],0x600000+9*0x240+0x130)
        self.assertEqual(p[10],0x620120)
        self.assertEqual(p[38],0x620000+28*0x2a0+0x120)
        self.assertFalse(r['name_lengths_proven'])

    def test_33_byte_scene_terminator_is_not_transferred_to_N0(self):
        for r in self.result['scene_name_paths']:
            self.assertEqual(r['maximum_bytes_before_forced_terminator'],33)
            self.assertEqual(r['tail_instructions_executed'],2)
            self.assertEqual(r['getter_instructions_executed'],2)
            self.assertTrue(r['other_payload_bytes_unchanged'])
            self.assertTrue(r['not_the_N0_actor_source'])
            self.assertFalse(r['full_setter_or_lifecycle_executed'])
        with self.assertRaises(ValueError): n.terminate_scene_name(self.elf,13)

    def test_additional_formatter_has_nine_direct_callers_without_capacity_claim(self):
        r=self.result['additional_I_consumer']
        self.assertEqual(r['function_offset'],0x10e0e8)
        self.assertEqual(len(r['direct_calls']),9)
        self.assertFalse(r['destination_capacity_proven'])
        self.assertFalse(r['executed'])
        self.assertFalse(self.result['editing_authorized'])
        self.assertEqual(self.result['new_translations_applied'],0)

    def test_divergent_source_is_rejected_before_execution(self):
        bad=bytearray(self.elf);bad[0x178500]^=1
        with self.assertRaises(ValueError): n.initialize_table(bytes(bad))
        with self.assertRaises(ValueError): n.terminate_scene_name(bytes(bad),2)

    def test_original_store_cannot_write_read_only_or_unmapped_memory(self):
        regs=[0]*32;regs[17]=0x600000;regs[18]=0x620000
        for regions in ([],[(0x600000,bytes(0x50),False)]):
            with self.assertRaises(ValueError):
                n.run(self.elf,0x79a18,((0x79a18,0x79a20),),regs.copy(),regions,0x79a20+n.DELTA)

    def test_execution_windows_prevent_escaping_into_adjacent_code(self):
        with self.assertRaises(ValueError):
            n.run(self.elf,0x1784ac,((0x1784ac,0x1784b0),),[0]*32,[],0x178520+n.DELTA)


if __name__=='__main__':unittest.main()
