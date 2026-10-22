import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from glyph_single import START,END,BASES,elf_patch
from layout_probe import execute
from validate_glyph_layout import incoming


class SingleGlyphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=(ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes();cls.patch=elf_patch(cls.data)

    def test_ascii_punctuation_and_other_modes_unchanged(self):
        for side in (19,22,26,32):
            for mode in (0,1,2):
                for code in range(256):
                    raw=code.to_bytes(2,'big')
                    a=execute(self.data,self.patch['before'],raw,side,mode,single=True)
                    b=execute(self.data,self.patch['after'],raw,side,mode,single=True)
                    self.assertEqual(a,b,(side,mode,code))
                    self.assertTrue(b['callee_saved'])

    def test_accents_match_base_draw_and_advance_but_retain_cache_code(self):
        for side in (19,22,26,32):
            for mode in (0,1,2):
                for pair,base in BASES.items():
                    expected=execute(self.data,self.patch['before'],bytes([base]),side,mode,single=True)
                    actual=execute(self.data,self.patch['after'],pair.to_bytes(2,'big'),side,mode,single=True)
                    self.assertEqual(actual,{**expected,'cache_codes':[pair]},(side,mode,pair))

    def test_native_boundaries_and_cache_lookup_unchanged(self):
        for pair in (0x8140,0x823f,0x824f,0x8258,0x825c,0x829f,0xa040,0x5757,0xf040,0xffff):
            for side in (19,22,26):
                raw=pair.to_bytes(2,'big')
                self.assertEqual(execute(self.data,self.patch['before'],raw,side,single=True),
                                 execute(self.data,self.patch['after'],raw,side,single=True))

    def test_fixed_function_revision_and_entry_points(self):
        self.assertEqual(len(self.patch['after']),END-START)
        self.assertTrue(all(r['function_entry'] for r in incoming(self.data,START,END)))
        with self.assertRaises(ValueError):elf_patch(self.data[:-1]+b'X')

if __name__=='__main__':unittest.main()
