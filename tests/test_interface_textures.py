import struct
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from interface_textures import inspect_texture,SOURCES
from probe_resources import nested


class TextureTests(unittest.TestCase):
    def test_synthetic_indices_4bit_low_first_and_8bit(self):
        for bpp,pixels in ((4,b'\x21'),(8,b'\x01\x02')):
            palette=b''.join(bytes((i,2*i,3*i,128)) for i in range(1<<bpp)) if bpp==4 else bytes(1024)
            palette=bytearray(palette);palette[4:12]=bytes((1,2,3,128,4,5,6,128))
            raw=struct.pack('<HHIII',2,1,bpp,16,16+len(palette))+palette+pixels+b'tail'
            meta,rgb=inspect_texture(raw)
            self.assertEqual(rgb,bytes((1,2,3,4,5,6)))
            self.assertEqual(meta['trailing_bytes'],4)

    def test_bounds_and_unsupported_layout_rejected(self):
        for raw in (b'',struct.pack('<HHIII',256,256,8,16,1040),
                    struct.pack('<HHIII',2,2,32,16,16)+bytes(64),
                    struct.pack('<HHIII',2,2,4,17,80)+bytes(100)):
            with self.assertRaises(ValueError):inspect_texture(raw)

    def test_six_inspected_original_entries_fit_without_mutation(self):
        for name in SOURCES:
            raw=(ROOT/'JOGO/Metal Saga/DATA/FDATA'/name).read_bytes();original=bytes(raw)
            root=nested(raw)[0]
            for index in range(3):
                a,b=root['offsets'][index:index+2];meta,rgb=inspect_texture(raw[a:b])
                self.assertEqual(len(rgb),meta['width']*meta['height']*3)
            self.assertEqual(raw,original)


if __name__=='__main__':unittest.main()
