import copy,json,struct,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import discover_credits as credits
import discover_paint as paint
from interface_text import SOURCE


class CreditsAndPaintDiscovery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes()
        cls.credits=(ROOT/'JOGO/Metal Saga'/credits.RESOURCE).read_bytes()
        cls.paint=(ROOT/'JOGO/Metal Saga'/paint.RESOURCE).read_bytes()
    def test_real_credits_decode_matches_original_loop_and_full_original_token_replay(self):
        metadata,local=credits.analyse(self.elf,self.credits)
        self.assertEqual((metadata['decoded_size'],metadata['compressed_bytes_consumed']),(4222,2351))
        self.assertEqual((metadata['declared_lines'],metadata['crlf_lines'],metadata['nonempty_lines']),(292,292,209))
        self.assertEqual(metadata['decoded_sha256'],'53a2c807ae676a11fedeb143000d737e284da43e22ad11a55f774a8a87f2286a')
        replay=struct.pack('<I',metadata['decoded_size'])+credits.replay(local['original_token_packets'])+bytes(metadata['original_zero_tail_bytes'])
        self.assertEqual(replay,self.credits[0x800:0x1800]);self.assertEqual(len(local['rows']),292)
        self.assertFalse(metadata['editing_authorized']);self.assertFalse(metadata['recompressor_implemented'])
        self.assertTrue(metadata['original_decoder_loop_executed'])
    def test_literal_stream_and_initial_zero_dictionary_and_overlap_match_original_instructions(self):
        examples=[struct.pack('<I',3)+b'\x07ABC',struct.pack('<I',3)+b'\x00\x00\x00',
            struct.pack('<I',6)+b'\x01A\xee\xf2']
        for raw in examples:
            out,consumed,packets=credits.decode(raw)
            executed,read,_=credits.execute_decoder_loop(self.elf,raw)
            self.assertEqual(out,executed);self.assertEqual(consumed,read);self.assertEqual(credits.replay(packets),raw[4:consumed])
        self.assertEqual(credits.decode(examples[1])[0],bytes(3));self.assertEqual(credits.decode(examples[2])[0],b'A'*6)
    def test_truncation_size_bound_and_overflow_are_not_padded_or_ignored(self):
        for raw in (b'\0',struct.pack('<I',1)+b'\x01',struct.pack('<I',1)+b'\x00\x00\x00',struct.pack('<I',100000000)):
            with self.assertRaises(ValueError):credits.decode(raw)
        raw=struct.pack('<I',1)+b'\x01'
        with self.assertRaises(ValueError):credits.execute_decoder_loop(self.elf,raw)
    def test_modified_elf_nonzero_tail_wrong_row_count_and_sda_boundary_refused(self):
        bad=bytearray(self.elf);bad[0x19b81c]^=1
        with self.assertRaises(ValueError):credits.analyse(bad,self.credits)
        bad=bytearray(self.credits);bad[0x17ff]=1
        with self.assertRaises(ValueError):credits.analyse(self.elf,bad)
        bad=bytearray(self.credits);bad[0x806]^=1
        with self.assertRaises(ValueError):credits.analyse(self.elf,bad)
        bad=bytearray(self.credits);struct.pack_into('<I',bad,12+4,0x1804)
        with self.assertRaises(ValueError):credits.analyse(self.elf,bad)
    def test_real_paint_table_aliases_and_name_forwarding_are_preserved_readonly(self):
        before=bytes(self.paint);metadata,local=paint.analyse(self.elf,self.paint)
        self.assertEqual((metadata['records'],metadata['unique_captions'],metadata['group_values']),(228,12,19))
        self.assertEqual((metadata['record_stride'],metadata['name_field_bytes'],metadata['maximum_original_caption_bytes']),(36,23,10))
        self.assertTrue(all(len(a['indices'])==19 for a in local['aliases']))
        self.assertEqual(len({r['id'] for r in local['rows']}),228);self.assertEqual(self.paint,before)
        self.assertTrue(all(not r['editing_authorized'] for r in local['rows']))
        self.assertEqual(metadata['name_forwarding_cases'],228)
    def test_paint_unterminated_or_nonzero_padding_or_source_revision_refused(self):
        bad=bytearray(self.paint);bad[paint.START+1:paint.START+24]=b'X'*23
        with self.assertRaises(ValueError):paint.analyse(self.elf,bad)
        bad=bytearray(self.paint);bad[paint.START+22]=1
        with self.assertRaises(ValueError):paint.analyse(self.elf,bad)
        bad=bytearray(self.elf);bad[0x1dff20]^=1
        with self.assertRaises(ValueError):paint.analyse(bad,self.paint)


if __name__=='__main__':unittest.main()
