import sys,struct,tempfile,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from audit_dialogue_backlog import classify,scan_unparsed_ssd,collect_labels,label_consumer_evidence,run
from test_dialogue_advanced import command,ssd
from dialogue_advanced import SsdIndex


class DialogueBacklog(unittest.TestCase):
    def test_unknown_ssd_text_is_candidate_not_approved_parser(self):
        raw=bytearray(command(b'msgb',[b'Unparsed dialogue sample.']))
        raw[:4]=b'abcd';data=ssd(raw);index=SsdIndex(data)
        meta,hits=scan_unparsed_ssd(data,index)
        self.assertEqual(meta['candidate_records'],1);self.assertEqual(len(hits),1)
        self.assertIn('no completeness proof',meta['limits'])
    def test_known_families_paths_and_short_data_not_repromoted(self):
        data=ssd(command(b'msgb',[b'Already parsed dialogue sample.']))
        meta,hits=scan_unparsed_ssd(data,SsdIndex(data));self.assertEqual(meta['other_records_scanned'],0);self.assertEqual(hits,[])
        raw=bytearray(command(b'msgb',[b'C:/game/path/file.sda']))
        raw[:4]=b'abcd';data=ssd(raw);self.assertEqual(scan_unparsed_ssd(data,SsdIndex(data))[1],[])
    def test_public_metadata_separates_repeated_native_and_protected_names(self):
        entries=[]
        for key,raw,reason in [('a',b'%N$3','Controle opaco: edição bloqueada'),
            ('b',b'\x82\xce','Origem com bytes nativos: preservação permitida, edição bloqueada'),
            ('c',b'\x82\xce','Origem com bytes nativos: preservação permitida, edição bloqueada')]:
            entries.append({'id':key,'record_sha256':key,'blocked_reasons':[reason],
                'segments':[{'source':'source','translation':'source','source_hex':raw.hex(),'editable':True}]})
        doc={'source_sha256':'bound','entries':entries};report={'valid':True,'refused':0,'source_sha256':'bound',
            'accepted':0,'unchanged':3,'deferred':[{'id':e['id']} for e in entries]}
        meta,buckets=classify(doc,report,[{'id':'a','record_sha256':'a'}])
        self.assertEqual(meta['protected_tank_names_still_noneditable'],1);self.assertEqual(meta['native_pending_context'],2)
        self.assertEqual(len(meta['native_groups']),1);self.assertNotIn('source_hex',json.dumps(meta))
        self.assertFalse(meta['automatic_edit_approval'])
    def test_n3_fingerprint_drift_is_not_silently_classified(self):
        doc={'source_sha256':'x','entries':[{'id':'a','record_sha256':'different','blocked_reasons':[],
            'segments':[{'source':'x','translation':'x','source_hex':'78','editable':True}]}]}
        report={'valid':True,'refused':0,'source_sha256':'x','accepted':0,'unchanged':1,'deferred':[{'id':'a'}]}
        with self.assertRaises(ValueError):classify(doc,report,[{'id':'a','record_sha256':'old'}])
    def test_output_cannot_leak_originals_outside_work_or_overwrite_unrelated_file(self):
        with self.assertRaises(ValueError):run(ROOT/'work/interface-v033',ROOT/'reports/originals-forbidden.json')
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-backlog-') as folder:
            target=Path(folder)/'unrelated.json';target.write_text('{}',encoding='utf-8')
            with self.assertRaises(ValueError):run(ROOT/'work/interface-v033',target)
    def test_speaker_labels_deduplicated_without_edit_approval(self):
        doc={'entries':[{'id':key,'segments':[{'key':'label','source':'Nina','source_hex':b'Nina'.hex(),
            'editable':False,'offset':at,'capacity':7}]} for key,at in (('a',100),('b',200))]}
        meta,rows=collect_labels(doc)
        self.assertEqual((meta['label_references'],meta['unique_labels']),(2,1))
        self.assertFalse(meta['editing_authorized']);self.assertEqual(len(rows[0]['references']),2)
        doc['entries'][0]['segments'][0]['editable']=True
        with self.assertRaises(ValueError):collect_labels(doc)
    def test_label_consumer_calls_bound_but_editing_still_not_enabled(self):
        from interface_text import SOURCE
        elf=SOURCE.read_bytes();r=label_consumer_evidence(elf)
        self.assertEqual(r['setter_destination_field'],0x34);self.assertFalse(r['editing_enabled'])
        self.assertFalse(r['instructions_executed']);self.assertEqual(len(r['instruction_assertions']),14)
        changed=bytearray(elf);changed[0x1fda1c]^=1
        with self.assertRaises(ValueError):label_consumer_evidence(changed)


if __name__=='__main__':unittest.main()
