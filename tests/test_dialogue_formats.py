import struct
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from dialogue_formats import parse_msg, parse_msgn, classify, reconstruct, native_text, tokens
from test_dialogue import fixture


def message(tag, text, label=None, gap=2):
    original = fixture()
    body=text+b'\0'
    if label is not None: body+=bytes(gap)+label+b'\0'
    body+=bytes((-len(body))%4)
    header=struct.pack('<4sHH',tag,3,32+len(body))+bytes(24)
    return original[:24]+header+body+original[88:]


class FormatTests(unittest.TestCase):
    def test_msgn_second_string_after_variable_zero_gap(self):
        for gap in (0,1,2,3,7):
            data=message(b'msgn',b'First\tSecond %W2',b'Label',gap)
            item,opaque=parse_msgn(data,24)
            self.assertFalse(opaque)
            self.assertEqual(item['display_label']['source'],'Label')
            self.assertEqual(reconstruct(item),data[24:24+item['size']])
            self.assertEqual(classify(data,24)[0],'validated')

    def test_msgn_without_name_or_unbounded_tail_rejected(self):
        for data in (message(b'msgn',b'Text'), message(b'msgn',b'Text',b'Name\0Other')):
            with self.assertRaises(ValueError):parse_msgn(data,24)

    def test_msg_and_msgn_have_distinct_suffix_rules(self):
        with self.assertRaises(ValueError):parse_msg(message(b'msg\0',b'Text',b'Name'),24)
        with self.assertRaises(ValueError):parse_msgn(message(b'msg\0',b'Text'),24)

    def test_tabs_controls_and_negative_parameter_exact(self):
        data=message(b'msg\0',b'%F1%M-1_5Hello\n%N0\t%W20Bye')
        item,opaque=parse_msg(data,24)
        self.assertFalse(opaque)
        self.assertEqual(reconstruct(item),data[24:24+item['size']])
        self.assertEqual([t['hex'] for t in item['control_tokens']],
                         [b.hex() for b in (b'%F1',b'%M-1_5',b'\n',b'%N0',b'\t',b'%W20')])

    def test_opaque_dynamic_and_malformed_commands_not_promoted(self):
        for raw in (b'Item %I$0',b'Money %$15G',b'%M_1Hello',b'%NO, thanks',b'50%'):
            data=message(b'msg\0',raw)
            state,item=classify(data,24)
            self.assertEqual(state,'identified')
            self.assertFalse(item['editable'])
            self.assertEqual(reconstruct(item),data[24:24+item['size']])

    def test_native_encoding_strict_lossless_and_not_utf8(self):
        raw=bytes.fromhex('82ce82ae815b8142')
        text,spans=native_text(raw)
        self.assertEqual(text,'\u3070\u3050\u30fc\u3002')
        self.assertEqual(text.encode('cp932'),raw)
        self.assertEqual(len(spans),4)
        data=message(b'msg\0',raw)
        state,item=classify(data,24)
        self.assertEqual(state,'identified')
        self.assertEqual(reconstruct(item),data[24:24+item['size']])
        self.assertNotEqual(native_text('\u00e7'.encode('utf-8'))[0],'\u00e7')
        for bad in (b'\x82',b'\x82\x7f',b'\xff',b'\x1b'):
            with self.assertRaises((ValueError,UnicodeError)):native_text(bad)

    def test_missing_context_identifies_but_does_not_validate(self):
        data=message(b'msgn',b'Text',b'Name')
        with patch('dialogue_formats.neighbors',side_effect=ValueError('Ambiguous boundary')):
            state,item=classify(data,24)
        self.assertEqual(state,'identified')
        self.assertIn('context_error',item)

    def test_reconstruct_detects_text_tampering(self):
        item,_=parse_msg(message(b'msg\0',b'Text'),24)
        item['source']='Other'
        with self.assertRaises(ValueError):reconstruct(item)


if __name__=='__main__':unittest.main()
