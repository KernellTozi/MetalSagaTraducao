import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import dialogue_native_review as native
from gfi import encode as project_encode


class NativeDialogue(unittest.TestCase):
    def test_record_hashes_and_all_source_glyphs_bound_to_original_fonts(self):
        r=native.verify_fonts();self.assertEqual(len(r['source_records']),6)
        self.assertGreater(len(r['native_glyphs']),4)
        self.assertTrue(all(g['jis']>>8!=0x23 for g in r['native_glyphs']))
        self.assertFalse(native.allowed('map.msg.040ef0ec','0'*64))
        key=next(iter(native.RECORDS))
        self.assertFalse(native.allowed(key,'0'*64));self.assertTrue(native.allowed(key,native.RECORDS[key]))
    def test_passthrough_only_exact_native_symbols_and_anchored_positions(self):
        for key,text in (('map.msg.07b264e0','Sou Syd!☆'),('map.msg.13709cc0','。\nDesculpe.')):
            raw=native.encode(text,key);self.assertEqual(native.decode(raw),text)
            with self.assertRaises(ValueError):project_encode(text)
        for key,text in (('map.msg.07b264e0','Sou Syd!'),('map.msg.07b264e0','☆Sou Syd!'),
            ('map.msg.13709cc0','Desculpe。'),('map.msg.128226fc','Valeu!☆'),('map.msg.128226fc','ありがと')):
            with self.subTest(key=key,text=text),self.assertRaises(ValueError):native.encode(text,key)
    def test_ptbr_mapping_has_priority_and_no_global_native_codec_extension(self):
        raw=native.encode('Você, ação!','unreviewed.ascii.record')
        self.assertEqual(raw,project_encode('Você, ação!'));self.assertEqual(native.decode(raw),'Você, ação!')
        with self.assertRaises(ValueError):native.encode('☆','unreviewed.ascii.record')
        with self.assertRaises(ValueError):project_encode('。')
    def test_native_and_ptbr_widths_accept_bytearray_without_losing_controls(self):
        from control_dialogue_quirks import tokenize
        self.assertEqual(native.width_units(bytearray(b'\x81\x42\nabc'),tokenize),[2,3])
        self.assertEqual(native.width_units(native.encode('Ação','unreviewed'),tokenize),[6])


if __name__=='__main__':unittest.main()
