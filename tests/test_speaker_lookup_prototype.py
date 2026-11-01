import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import speaker_lookup_prototype as p
from interface_text import SOURCE


class SpeakerLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=SOURCE.read_bytes()
        cls.report=json.loads((p.ROOT/'reports/falantes-lookup-v001.json').read_bytes())
        cls.proposals=json.loads((p.ROOT/'work/falantes-lookup-v001/proposta-local.json').read_bytes())

    def test_five_complete_names_at_all_source_alignments(self):
        for i,(_,target) in enumerate(p.ROLES):
            for alignment in range(8):
                r=p.emulate(f'~{i}'.encode(),source_alignment=alignment)
                self.assertEqual(r['raw'],p.encode(target))
                self.assertTrue(r['resolved'])
                self.assertTrue(r['live_registers_preserved'])
                self.assertTrue(r['source_and_stack_unchanged'])
                self.assertEqual(r['return_address'],p.HOOK+p.DELTA+8)

    def test_empty_short_malformed_and_ordinary_names_are_untouched(self):
        for raw in [b'',b'~',b'~/',b'~5',b'~9',b'~0X',b'~00',b'Worker',b'Nina',b'Hunter',p.encode('Mecânico')]:
            r=p.emulate(raw)
            self.assertFalse(r['resolved']);self.assertEqual(r['raw'],raw)

    def test_other_callers_cannot_resolve_even_a_valid_marker(self):
        for caller in [0,0x1c6de8+p.DELTA,p.CALLER-4,p.CALLER+4]:
            for i in range(5):
                token=f'~{i}'.encode();r=p.emulate(token,caller=caller)
                self.assertFalse(r['resolved']);self.assertEqual(r['raw'],token)

    def test_synthetic_blob_is_relocatable_and_names_force_scalar_copy(self):
        for base in [p.BASE,0x698000,0x7fff00]:
            blob,meta=p.program(base)
            self.assertEqual(p.sha(blob),meta['sha256'])
            for row in meta['names']:
                self.assertEqual(row['pointer']%4,1)
                self.assertEqual(p.emulate(f"~{row['role_index']}".encode(),base=base)['raw'],bytes.fromhex(row['encoded_hex']))
        with self.assertRaises(ValueError):p.program(0x123456)

    def test_all_13_proposed_records_preserve_every_nonlabel_byte(self):
        rows={r['id']:r for r in self.report['proposed_records']}
        proposed=self.proposals['patches_not_applied']
        self.assertEqual(set(rows),set(p.IDS));self.assertEqual(len(proposed),13)
        for q in proposed:
            r=rows[q['id']];a=bytes.fromhex(q['before_hex']);b=bytes.fromhex(q['after_hex'])
            at=r['label_offset']-r['offset'];end=at+r['capacity']+1
            self.assertEqual(len(a),len(b));self.assertEqual(a[:at],b[:at]);self.assertEqual(a[end:],b[end:])
            self.assertEqual(p.sha(a),r['compiled_record_sha256'])
            self.assertEqual(p.sha(b),r['proposed_record_sha256'])
            self.assertEqual(b[at:end].split(b'\0')[0],bytes.fromhex(r['marker_hex']))
            self.assertEqual(p.emulate(bytes.fromhex(r['marker_hex']))['raw'],p.encode(r['translation']))

    def test_native_copy_allocation_and_getter_proofs_exist_for_every_record(self):
        for row in self.report['proposed_records']:
            proof=row['original_copy_probe']
            self.assertEqual(proof['bytes'],row['target_bytes'])
            self.assertEqual(proof['allocated_bytes'],(row['target_bytes']+4)&~3)
            self.assertTrue(proof['copy_and_guards']);self.assertTrue(proof['static_getter'])
            self.assertTrue(row['native_label_traversal_unchanged'])

    def test_reserved_marker_collision_refuses_before_any_proposal(self):
        doc={'entries':[{'id':'other','segments':[{'key':'label','translation':'~0'}]}]}
        with self.assertRaisesRegex(ValueError,'collides'):p.build_proposal(b'',doc,[],self.elf)

    def test_other_record_family_and_changed_elf_are_refused(self):
        entries=[]
        for key,index in p.IDS.items():
            source=p.ROLES[index][0]
            entries.append({'id':key,'tag':b'smnn'.hex(),'mode':'slots','blocked_reasons':[],
                            'segments':[{'key':'label','translation':source,'source':source}]})
        with self.assertRaisesRegex(ValueError,'metadata'):p.build_proposal(b'',{'entries':entries},[],self.elf)
        bad=bytearray(self.elf);bad[p.HOOK]^=1
        with self.assertRaisesRegex(ValueError,'differs'):p.build_proposal(b'',{'entries':[]},[],bytes(bad))

    def test_no_runtime_storage_or_game_execution_is_claimed(self):
        self.assertFalse(self.report['can_apply_to_iso']);self.assertFalse(self.report['iso_modified'])
        self.assertFalse(self.report['pcsx2_executed']);self.assertFalse(self.proposals['can_apply_to_iso'])
        self.assertEqual(self.report['existing_label_marker_collisions'],0)
        self.assertEqual(self.report['census_records'],7231)

    def test_storage_census_does_not_confuse_bss_or_file_padding_with_free_ram(self):
        s=p.storage_evidence(self.elf)
        self.assertTrue(s['header_padding_all_zero'])
        self.assertEqual(len(s['end_address_references']),12)
        self.assertEqual(s['original_memory_end'],0x4b599c)
        self.assertEqual(s['startup_clear_stop_exclusive'],0x4b59a0)
        self.assertEqual(s['clearing_rounding_bytes_beyond_declared_end'],4)
        self.assertFalse(s['candidate_declared_segment']['can_apply'])
        self.assertEqual(s['candidate_declared_segment']['program_bytes'],170)
        self.assertEqual(s['candidate_declared_segment']['proposed_heap_start'],0x4b5a50)


if __name__=='__main__':unittest.main()
