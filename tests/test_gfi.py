import sys,unittest,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from gfi import CHAR_TO_BYTES,decode,encode,pack,sjis_to_jis
from build_accent_experiment import message_patch,GROUP_A,GROUP_B,SECOND_SOURCE
from test_dialogue import fixture

class GfiEncodingTests(unittest.TestCase):
    def test_stable_mapping_roundtrip(self):
        text='Teste: '+' '.join(CHAR_TO_BYTES)
        self.assertEqual(decode(encode(text)),text)
        self.assertEqual(encode('\u00e7\u00d5'),bytes.fromhex('8240825b'))
        self.assertEqual(len(set(CHAR_TO_BYTES.values())),18)

    def test_engine_conversion_known_and_reserved(self):
        self.assertEqual(sjis_to_jis(0x8163),0x2144)
        self.assertEqual(sjis_to_jis(0x8240),0x2321)
        self.assertEqual(sjis_to_jis(0x8259),0x233a)
        self.assertEqual(sjis_to_jis(0x825b),0x233c)
        for invalid in (0x8070,0x827f,0x824,0xffff):
            with self.assertRaises(ValueError):sjis_to_jis(invalid)

    def test_reject_unknown_encoding(self):
        for raw in (b'\x82',b'\x82\xff','\u00e7'.encode('utf-8'),b'\xe7'):
            with self.assertRaises(ValueError):decode(raw)
        with self.assertRaises(ValueError):encode('\u00f1')

    def test_nibble_order(self):
        self.assertEqual(pack([1,2,15,0]),b'\x21\x0f')
        with self.assertRaises(ValueError):pack([16,0])

    def test_group_a_fits_existing_message(self):
        patch=message_patch(fixture(),24,'You want to become\na hunter?',GROUP_A)
        self.assertEqual(len(patch['after']),32)
        self.assertEqual(patch['encoded_length'],26)
        self.assertEqual(patch['after'].count(b'\n'),1)

    def test_group_b_preserves_page_and_commands(self):
        base=fixture()
        header=struct.pack('<4sHH',b'msg\0',3,152)+bytes(24)
        source=SECOND_SOURCE.encode('ascii')
        data=base[:24]+header+source+bytes(120-len(source))+base[88:]
        patch=message_patch(data,24,SECOND_SOURCE,GROUP_B)
        self.assertEqual(len(patch['after']),120)
        self.assertEqual(decode(encode(GROUP_B)),GROUP_B)
        self.assertEqual(patch['after'].split(b'\t')[1].rstrip(b'\0'),source.split(b'\t')[1])
        self.assertTrue(patch['after'].startswith(b'%F1%M0_5'))

    def test_message_control_or_capacity_rejected(self):
        for replacement in ('Teste',GROUP_A+'\n','A: '+'\u00e7 '*20+'\nX','A: %N1\nX'):
            with self.assertRaises(ValueError):message_patch(fixture(),24,'You want to become\na hunter?',replacement)

if __name__=='__main__':unittest.main()
