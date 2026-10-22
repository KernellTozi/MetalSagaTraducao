import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'work/python-deps')]
from gfi import Gfi,CHAR_TO_BYTES
from gfi_refined import font_patches,accented_pixels


class RefinedTests(unittest.TestCase):
    def test_real_fonts_fixed_cells_and_native_banks(self):
        for name in ('SUC20I22.GFI','SUC24I26.GFI'):
            with self.subTest(font=name):
                data=(ROOT/'JOGO/Metal Saga/DATA/SYS'/name).read_bytes()
                font=Gfi(data);modified=bytearray(data);allowed=set()
                patches=font_patches(data)
                self.assertEqual(len(patches),18)
                for p in patches:
                    self.assertEqual(len(p['after']),font.stride)
                    self.assertTrue(any(p['after']))
                    self.assertEqual(p['before'],bytes(font.stride))
                    allowed.update(range(p['offset'],p['offset']+font.stride))
                    modified[p['offset']:p['offset']+font.stride]=p['after']
                self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(data,modified))))
                self.assertEqual(Gfi(modified).rows,font.rows)
                for base in 'aeou':
                    native=font.pixels(font.ascii_offset(base))
                    char=next(c for c in CHAR_TO_BYTES if __import__('unicodedata').normalize('NFD',c)[0]==base)
                    new=accented_pixels(font,char)
                    # Lowercase body never shrinks or loses a native pixel.
                    self.assertTrue(all(b>=a for a,b in zip(native,new)))
                for c in ('\u00e7','\u00c7'):
                    new=accented_pixels(font,c)
                    core=[(i%font.side,i//font.side) for i,p in enumerate(new) if p>=7]
                    self.assertTrue(core)
                    self.assertLess(max(y for x,y in core),font.side)


if __name__=='__main__':unittest.main()
