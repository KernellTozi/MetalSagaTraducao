import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from glyph_layout import elf_patch,START,END,BASES
from layout_probe import execute
from validate_glyph_layout import incoming


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=(ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes()
        cls.patch=elf_patch(cls.data)

    def test_native_ascii_modes_sizes_and_float_calls_unchanged(self):
        for side in (12,19,22,26,32):
            for mode in (0,1,2):
                for code in range(256):
                    raw=bytes([code,0x3f])
                    a=execute(self.data,self.patch['before'],raw,side,mode)
                    b=execute(self.data,self.patch['after'],raw,side,mode)
                    self.assertEqual(a,b,(side,mode,code))
                    self.assertTrue(b['callee_saved'])

    def test_all_accents_inherit_base_metrics_and_preserve_pair(self):
        for side in (12,19,22,26,32):
            for mode in (0,1,2):
                for pair,base in BASES.items():
                    expected=execute(self.data,self.patch['before'],bytes([base]),side,mode)
                    actual=execute(self.data,self.patch['after'],pair.to_bytes(2,'big'),side,mode)
                    self.assertEqual(actual,{**expected,'code':pair,'consumed':2})

    def test_native_pair_boundaries_unchanged(self):
        for pair in (0x8140,0x823f,0x824f,0x8258,0x825c,0x829f,0x876f,0x889f,0xf040,0xf9fc,0xffff):
            for side in (19,22,26):
                raw=pair.to_bytes(2,'big')
                self.assertEqual(execute(self.data,self.patch['before'],raw,side),
                                 execute(self.data,self.patch['after'],raw,side))

    def test_size_source_and_direct_entries(self):
        self.assertEqual(len(self.patch['after']),END-START)
        refs=incoming(self.data)
        self.assertTrue(refs)
        self.assertTrue(all(r['function_entry'] for r in refs),refs)
        with self.assertRaises(ValueError):elf_patch(self.data[:-1]+b'X')

if __name__=='__main__':unittest.main()
