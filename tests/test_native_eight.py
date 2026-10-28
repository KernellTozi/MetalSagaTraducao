import copy,json,mmap,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import dialogue_native_eight as n
from build_translation_pilot import load_draft,compile_draft
from reinsertion import SOURCE,compile_entry
from interface_text import SOURCE as ELF

class NativeEightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stream=SOURCE.open('rb');cls.data=mmap.mmap(cls.stream.fileno(),0,access=mmap.ACCESS_READ)
        cls.elf=ELF.read_bytes();cls.parent,_=load_draft(ROOT/n.PARENT_MAP)
        cls.draft,_=load_draft(ROOT/'translations/regiao-inicial-v041.json')
        cls.parent_doc,cls.parent_patches,cls.parent_report=compile_draft(cls.data,cls.parent)
        cls.doc,cls.patches,cls.report=compile_draft(cls.data,cls.draft)

    @classmethod
    def tearDownClass(cls):cls.data.close();cls.stream.close()

    def test_eight_occurrences_one_body_five_record_fingerprints(self):
        proof=self.report['native_fallback_overlay'];self.assertEqual(len(proof['records']),8)
        self.assertEqual(proof['distinct_bodies'],1);self.assertEqual(proof['distinct_record_fingerprints'],5)
        self.assertEqual(sum(len(r['marker_lookup_cases']) for r in proof['records']),41)
        self.assertEqual(sum(r['is_last_ssd_instruction'] for r in proof['records']),6)
        self.assertEqual({r['slot_capacity_bytes'] for r in proof['records']},{11})

    def test_original_branch_and_marker_slices_missing_and_existing_targets(self):
        self.assertEqual([r['return_code'] for r in n.branch_cases(self.elf)],[2,2,3])
        for marks in ([],[0],[0,1,2,3,4]):
            rows=n.marker_cases(self.elf,marks)
            self.assertEqual(sum(r['found'] for r in rows),len(marks));self.assertFalse(rows[-1]['found'])
        with self.assertRaises(ValueError):n.marker_cases(self.elf,[0,0])

    def test_every_patch_preserves_header_length_controls_and_reverse_roundtrip(self):
        from dialogue_formats import parse_msg,reconstruct
        for key in n.RECORDS:
            patch=n.patch_record(self.data,key,n.TARGET);before=patch['before'];after=patch['after']
            self.assertEqual(len(before),44);self.assertEqual(len(after),44)
            self.assertEqual(before[:32],after[:32]);self.assertEqual(after[32:],b'Erro.'+bytes(7))
            self.assertEqual(sum(a!=b for a,b in zip(before,after)),8)
            copy_record=bytearray(after);copy_record[:]=before;self.assertEqual(copy_record,before)
            self.assertEqual(before,self.data[patch['offset']:patch['offset']+44])
            parsed,opaque=parse_msg(after,0)
            self.assertFalse(opaque);self.assertFalse(parsed['native_spans'])
            self.assertEqual(parsed['source'],n.TARGET);self.assertEqual(reconstruct(parsed),after)
            original,_=parse_msg(before,0);self.assertEqual(reconstruct(original),before)

    def test_only_exact_ascii_target_at_exact_ids(self):
        key=next(iter(n.RECORDS))
        for text in ('Erro!','erro.','Bug.','Erro.\n','Erro.\t','%N0','ばぐー。',''):
            with self.assertRaises(ValueError):n.patch_record(self.data,key,text)
        with self.assertRaises(ValueError):n.patch_record(self.data,'map.msg.040ef0f0',n.TARGET)

    def test_changed_source_fingerprint_refused_without_copying_large_map(self):
        source=self.data;key=next(iter(n.RECORDS));at=int(key.rsplit('.',1)[1],16)
        class Mutation:
            def __getitem__(self,part):
                value=bytearray(source[part])
                if part.start==at:value[32]^=1
                return bytes(value)
        with self.assertRaises(ValueError):n.patch_record(Mutation(),key,n.TARGET)

    def test_legacy_native_policy_and_compiler_remain_blocked(self):
        from dialogue_native_review import RECORDS,allowed
        self.assertEqual(len(RECORDS),6)
        by={e['id']:e for e in self.parent_doc['entries']}
        for key,digest in n.RECORDS.items():
            self.assertFalse(allowed(key,digest));old=by[key];new=copy.deepcopy(old);new['segments'][0]['translation']=n.TARGET
            with self.assertRaises(ValueError):compile_entry(self.data,new,old,quirk_refs=True)

    def test_non_target_records_patches_and_metadata_identical_to_v040(self):
        old={e['id']:e for e in self.parent_doc['entries']};new={e['id']:e for e in self.doc['entries']}
        self.assertEqual(set(old),set(new));self.assertEqual(len(new),7231)
        for key,e in old.items():
            if key not in n.RECORDS:self.assertEqual(e,new[key])
            else:
                expected=copy.deepcopy(e);expected['segments'][0]['translation']=n.TARGET
                self.assertEqual(new[key],expected);self.assertTrue(new[key]['blocked_reasons'])
        before={p['id']:p for p in self.parent_patches};after={p['id']:p for p in self.patches}
        self.assertEqual(set(after)-set(before),set(n.RECORDS))
        for key,p in before.items():self.assertEqual(after[key],p)

    def test_counts_deferred_tank_names_and_preservation_unchanged(self):
        self.assertTrue(self.report['valid']);self.assertEqual(self.report['accepted'],6032)
        self.assertEqual(self.report['refused'],0);self.assertEqual(self.report['unchanged'],1199)
        self.assertEqual(len(self.report['deferred']),19)
        self.assertEqual(self.report['deferred'],[r for r in self.parent_report['deferred'] if r['id'] not in n.RECORDS])
        self.assertEqual(self.report['preservation_decisions'],self.parent_report['preservation_decisions'])

    def test_entire_batch_rejects_single_target_or_parent_mutation(self):
        for key in (next(iter(n.RECORDS)),next(k for k in self.draft['translations'] if k not in n.RECORDS)):
            bad=copy.deepcopy(self.draft);bad['translations'][key]='Errado.'
            with self.assertRaises(ValueError):compile_draft(self.data,bad)
        bad=copy.deepcopy(self.draft);bad['native_fallback_review']['sha256']='0'*64
        with self.assertRaises(ValueError):compile_draft(self.data,bad)

    def test_interface_parent_preserved_and_opt_in_validation_dispatch(self):
        from interface_remainder_graphics import validate_interface
        ui=json.loads((ROOT/'translations/interface-v048.json').read_text(encoding='utf-8'))
        parent=json.loads((ROOT/n.PARENT_UI).read_text(encoding='utf-8'));validate_interface(ui)
        allowed={'native_fallback_review','base_dialogue_draft','iso_name','status'}
        self.assertEqual({k:v for k,v in ui.items() if k not in allowed},{k:v for k,v in parent.items() if k not in allowed})
        bad=copy.deepcopy(ui);bad['layout_profile']='spacing-v003'
        with self.assertRaises(ValueError):validate_interface(bad)

    def test_existing_offline_backlog_recognizes_zero_native_pending(self):
        from audit_dialogue_backlog import classify
        protected=json.loads((ROOT/'reports/n3-preservation-v001.json').read_text(encoding='utf-8'))['records']
        meta,buckets=classify(self.doc,self.report,protected)
        self.assertEqual(meta['native_pending_context'],0);self.assertEqual(meta['technical_deferrals'],19)
        self.assertEqual(meta['other_controls_pending'],0);self.assertEqual(meta['translated_records'],6032)

    def test_elf_and_marker_record_mutations_not_accepted_as_new_evidence(self):
        bad=bytearray(self.elf);bad[0x1c54c0]^=1
        with self.assertRaises(ValueError):n.evidence(self.data,bad)
        self.assertTrue(all(r['jis']>>8!=0x23 for r in self.report['native_fallback_overlay']['original_source_glyphs']))

if __name__=='__main__':unittest.main()
