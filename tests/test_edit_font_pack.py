import json
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from edit_font_pack import export,import_pack,reference,NAMES
from gfi_refined import font_patches
from PIL import Image


class FontPackTests(unittest.TestCase):
    def test_export_import_recreates_exact_v002_fonts(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'work') as temp:
            path=Path(temp);export(path/'pack');import_pack(path/'pack',path/'rebuilt')
            self.assertTrue((path/'pack.zip').is_file())
            for name in NAMES:
                source=reference(name);expected=bytearray(source)
                for p in font_patches(source):expected[p['offset']:p['offset']+len(p['after'])]=p['after']
                self.assertEqual((path/'rebuilt'/name).read_bytes(),expected)

    def test_resize_or_color_mode_refused_before_writing_fonts(self):
        for mode,size in (('L',(44,44)),('RGBA',(22,22))):
            with tempfile.TemporaryDirectory(dir=ROOT/'work') as temp:
                path=Path(temp);export(path/'pack')
                Image.new(mode,size).save(path/'pack'/NAMES[0]/'U00E7.png')
                with self.assertRaises(ValueError):import_pack(path/'pack',path/'bad')
                self.assertFalse((path/'bad').exists())

    def test_changed_source_manifest_refused(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'work') as temp:
            path=Path(temp);export(path/'pack');m=path/'pack/manifest.json'
            doc=json.loads(m.read_text(encoding='utf-8'));doc['fonts'][NAMES[0]]['source_sha256']='0'*64
            m.write_text(json.dumps(doc),encoding='utf-8')
            with self.assertRaises(ValueError):import_pack(path/'pack',path/'bad')
            self.assertFalse((path/'bad').exists())

if __name__=='__main__':unittest.main()
