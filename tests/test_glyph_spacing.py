import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from glyph_spacing import elf_patch,execute_window,PAIRS,CONTINUE,RETURN_ZERO


def native_class(code):
    if code<256:
        if code<0x20:return 0
        if code<=0x7f:return 1
        if 0xa0<=code<=0xdf:return 2
        if 0xf0<=code<=0xf9:return -2
        return -1
    if 0xf000<=code<0xfa00:return -2
    if 0x876f<=code<0x889f:return -3
    return -1


class SpacingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=(ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes()
        cls.patch=elf_patch(cls.data)

    def test_every_16bit_code_against_original_instructions(self):
        changed=[]
        for code in range(65536):
            old=execute_window(self.patch['before'],code,native_class(code))
            new=execute_window(self.patch['after'],code,native_class(code))
            if code in PAIRS:
                self.assertEqual(new,{**old,'flags':old['flags']|1})
                changed.append(code)
            else:self.assertEqual(new,old,f'Native code {code:04x}')
        self.assertEqual(set(changed),PAIRS)

    def test_flags_classes_and_lookup_argument_preservation(self):
        for flags in (0,1,0x55aa,0xffff):
            for code in (0x61,0xa1,0x8240,0x824e,0x824f,0x8258,0x8259,0x825b,0x825c,0x8140):
                old=execute_window(self.patch['before'],code,native_class(code),flags)
                new=execute_window(self.patch['after'],code,native_class(code),flags)
                self.assertEqual(new['calls'],old['calls'])
                self.assertEqual(new['flags']&0xfffe,old['flags']&0xfffe)
                self.assertEqual(new['bitmap'],old['bitmap'])
        for kind in (-4,-3,-2,-1,0,1,2,3):
            old=execute_window(self.patch['before'],0x61,kind)
            new=execute_window(self.patch['after'],0x61,kind)
            self.assertEqual(new,old)

    def test_fixed_length_and_source_revision(self):
        self.assertEqual(len(self.patch['before']),128)
        self.assertEqual(len(self.patch['after']),128)
        with self.assertRaises(ValueError):elf_patch(self.data[:-1]+b'X')


if __name__=='__main__':unittest.main()
