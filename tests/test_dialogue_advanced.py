import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from dialogue_advanced import SsdIndex, LAYOUTS, parse, reconstruct
from extract_dialogues import scan


def command(tag,strings):
    header,_=LAYOUTS[tag]
    body=b'\0\0'.join(strings)+b'\0'
    body+=bytes((-len(body))%4)
    return struct.pack('<4sHH',tag,0,header+len(body))+bytes(header-8)+body


def ssd(code):
    return b'ssd\0'+struct.pack('<II',1129,len(code)+12)+code


class AdvancedTests(unittest.TestCase):
    def test_ssd_declared_end_includes_header(self):
        code=command(b'sel\0',[b'Yes\tNo'])
        data=ssd(code)+b'msg\0'+bytes(8)
        index=SsdIndex(data)
        self.assertEqual(len(index.blocks),1)
        self.assertEqual(index.blocks[0]['end'],12+len(code))
        self.assertIn(12,index.records)
        self.assertEqual(index.footer(12+len(code))['relative_offset'],0)
        self.assertFalse(index.footer(12))

    def test_ssd_rejects_crossing_instruction_and_truncation(self):
        good=ssd(command(b'sel\0',[b'Yes\tNo']))
        for data in (good[:-4],good[:8]+struct.pack('<I',16)+good[12:]):
            index=SsdIndex(data)
            self.assertEqual(index.blocks,[])
            self.assertTrue(index.errors)

    def test_all_eleven_layouts_roundtrip_independently(self):
        for tag,(header,count) in LAYOUTS.items():
            data=command(tag,[b'Example']*count)
            state,item=parse(data,0)
            self.assertEqual(item['header_size'],header)
            self.assertEqual(len(item['segments']),count)
            self.assertEqual(reconstruct(item),data)
            self.assertFalse(item['editable'])

    def test_selection_offsets_and_tab_preserved(self):
        data=command(b'smsg',[b'Question?',b'Yes\tNo'])
        state,item=parse(data,0)
        self.assertEqual(item['segments'][0]['text_offset'],40)
        self.assertEqual(item['segments'][1]['source'],'Yes\tNo')
        self.assertIn({'relative_offset':3,'hex':'09','kind':'page'},item['segments'][1]['control_tokens'])
        self.assertEqual(state,'validated')

    def test_missing_extra_and_third_string_cautious(self):
        with self.assertRaises(ValueError):parse(command(b'smsg',[b'Question']),0)
        with self.assertRaises(ValueError):parse(command(b'sel\0',[b'One',b'Extra']),0)
        state,item=parse(command(b'smnn',[b'Question',b'Yes\tNo',b'Label']),0)
        self.assertEqual(state,'identified')
        self.assertIn('Third display',item['reason'])

    def test_no_unbounded_strings_or_modified_payload(self):
        data=bytearray(command(b'sel\0',[b'Yes\tNo']))
        data[-1]=255
        with self.assertRaises(ValueError):parse(data,0)
        _,item=parse(command(b'sel\0',[b'Yes\tNo']),0)
        item['segments'][0]['source']='Changed'
        with self.assertRaises(ValueError):reconstruct(item)

    def test_new_layout_requires_real_ssd_instruction_boundary(self):
        code=command(b'sel\0',[b'Yes\tNo'])
        self.assertEqual(list(scan(code)),[])
        result=list(scan(ssd(code)))
        self.assertEqual(len(result),1)
        self.assertEqual(result[0][0],'validated')

    def test_footer_signature_cannot_be_promoted_to_dialogue(self):
        data=ssd(command(b'sel\0',[b'Yes\tNo']))+b'msg\0\0\0d\0'+bytes(120)
        results=list(scan(data))
        self.assertEqual(results[-1][0],'rejected')
        self.assertIn('ssd_evidence',results[-1][1])

    def test_native_and_opaque_advanced_text_stay_locked(self):
        for text in (b'%I$0',bytes.fromhex('82ce82ae815b8142')):
            state,item=parse(command(b'msgb',[text]),0)
            self.assertEqual(state,'identified')
            self.assertEqual(reconstruct(item),command(b'msgb',[text]))


if __name__=='__main__':unittest.main()
