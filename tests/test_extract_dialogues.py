import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from extract_dialogues import inspect, scan, reconstruct, legacy_entry, extract, ROOT, SECOND_SOURCE
from dialogue import changes, sha
from test_dialogue import fixture


class ExtractionTests(unittest.TestCase):
    def test_existing_ascii_and_exact_record_roundtrip(self):
        data = fixture()
        state, item = inspect(data, 24)
        self.assertEqual(state, 'validated')
        self.assertEqual(reconstruct(item), data[24:88])
        plan = {'schema':1, 'resource':'DATA/MAP/MAP.MCT', 'source_sha256':sha(data),
                'policy':'msg-null-fixed-size-ascii-lf-v1', 'entries':[legacy_entry(item)]}
        self.assertEqual(changes(data, plan), [])
        self.assertEqual(json.loads(json.dumps(item)), item)

    def test_bad_size_unaligned_and_truncated_rejected(self):
        for data, at in ((fixture()[:50],24), (b'x'+fixture(),25),
                         (fixture()[:30]+b'\xff\xff'+fixture()[32:],24)):
            with self.subTest(at=at):
                self.assertEqual(inspect(data,at)[0], 'rejected')

    def test_unknown_bytes_and_nonzero_padding_preserved_pending(self):
        for index, value in ((56,0x82),(87,1)):
            data = bytearray(fixture()); data[index] = value
            state, item = inspect(data,24)
            self.assertEqual(state, 'pending')
            self.assertEqual(bytes.fromhex(item['record_hex']),data[24:88])
            self.assertFalse(item['editable'])

    def test_readable_commands_remain_pending(self):
        data = bytearray(fixture());data[56:59] = b'%N1'
        state,item = inspect(data,24)
        self.assertEqual(state,'pending')
        self.assertIn('254e31',item['control_hex'])

    def test_msgn_not_interpreted_as_msg_null(self):
        data = bytearray(fixture());data[24:28] = b'msgn'
        state,item = inspect(data,24)
        self.assertEqual(state,'pending')
        self.assertNotIn('readable_candidate',item)

    def test_scan_classifies_every_signature_once(self):
        data = fixture()+b'msg\0'+b'\0'*4+b'msgn'
        result = list(scan(data))
        self.assertEqual(len(result),3)
        self.assertEqual([r[0] for r in result],['validated','rejected','rejected'])

    def test_ambiguous_context_is_pending(self):
        with patch('extract_dialogues.record',side_effect=ValueError('Ambiguous previous record boundary')):
            self.assertEqual(inspect(fixture(),24)[0],'pending')

    def test_controlled_pilot_bytes_and_pages_roundtrip(self):
        base = fixture()
        raw = SECOND_SOURCE.encode('ascii')
        data = base[:24]+struct.pack('<4sHH',b'msg\0',3,152)+bytes(24)+raw+bytes(120-len(raw))+base[88:]
        with patch('extract_dialogues.SECOND_OFFSET',24):
            state,item = inspect(data,24)
        self.assertEqual(state,'validated')
        self.assertEqual(item['profile'],'nina-controlled-pilot-v1')
        self.assertEqual(reconstruct(item),data[24:176])
        self.assertIn('09',item['control_hex'])
        self.assertTrue(item['source'].startswith('%F1%M0_5'))

    def test_local_pipeline_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='extract-test-') as folder:
            folder=Path(folder); source=folder/'fixture.mct'; original=fixture()
            source.write_bytes(original)
            summary=extract(source,folder/'output')
            self.assertEqual(summary['counts'],{'validated':1,'pending':0,'rejected':0})
            self.assertEqual(source.read_bytes(),original)
            self.assertTrue(summary['record_roundtrip_passed'])
            item=json.loads((folder/'output/dialogos.jsonl').read_text(encoding='utf-8'))
            self.assertEqual(item['offset'],24)
            with self.assertRaises(ValueError):extract(source,folder/'output')
            self.assertTrue((folder/'output/relatorio.json').is_file())


if __name__ == '__main__':
    unittest.main()
