import copy,json,mmap,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from build_translation_pilot import SOURCE,load_draft,compile_draft
from interface_text import SOURCE as ELF
from speaker_label_space import BYTE_POLICY,placement,locate,byte_copy_probe,overlay
from gfi import encode


class BytePositionedSpeakerLabels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=ELF.read_bytes();cls.parent,_=load_draft(ROOT/'translations/regiao-inicial-v035.json')
        cls.child,_=load_draft(ROOT/'translations/regiao-inicial-v036.json')
        cls.stream=SOURCE.open('rb');cls.data=mmap.mmap(cls.stream.fileno(),0,access=mmap.ACCESS_READ)
        cls.old_doc,cls.old_patches,cls.old_report=compile_draft(cls.data,cls.parent)
        cls.doc,cls.patches,cls.report=compile_draft(cls.data,cls.child)
    @classmethod
    def tearDownClass(cls):cls.data.close();cls.stream.close()
    def test_all_earlier_fields_recipes_and_positions_preserved(self):
        self.assertTrue(self.report['valid']);self.assertEqual(self.report['refused'],0)
        for key in ('translations','deferred','speaker_labels','speaker_label_relocations','preservation_decisions'):
            self.assertEqual(self.parent[key],self.child[key])
        ids={e['id'] for e in self.child['speaker_label_byte_packing']['entries']};self.assertEqual(len(ids),75)
        for a,b in zip(self.old_doc['entries'],self.doc['entries']):
            self.assertEqual({k:v for k,v in a.items() if k!='segments'},{k:v for k,v in b.items() if k!='segments'})
            for s,t in zip(a['segments'],b['segments']):
                self.assertEqual({k:v for k,v in s.items() if k!='translation'},{k:v for k,v in t.items() if k!='translation'})
                if a['id'] not in ids or s['key']!='label':self.assertEqual(s,t)
        for key,value in self.old_doc['compiled_speaker_label_offsets'].items():
            self.assertEqual(self.doc['compiled_speaker_label_offsets'][key],value)
        self.assertEqual(len(self.doc['compiled_speaker_label_offsets']),314)
        self.assertEqual(sum(s['key']=='label' and s['source']!=s['translation'] for e in self.doc['entries'] for s in e['segments']),867)
    def test_binary_changes_only_existing_zero_tail_no_text_shortening(self):
        old={p['id']:p for p in self.old_patches};new={p['id']:p for p in self.patches};self.assertTrue(old.keys()<=new.keys())
        items={e['id']:e for e in self.child['speaker_label_byte_packing']['entries']}
        for e in self.doc['entries']:
            key=e['id'];original=bytes(self.data[e['offset']:e['offset']+e['size']])
            a=old[key]['after'] if key in old else original;b=new[key]['after'] if key in new else original
            if key not in items:self.assertEqual(a,b);continue
            previous=e['segments'][-2]['offset']-e['offset'];nul=a.index(0,previous);oldstart=e['segments'][-1]['offset']-e['offset']
            start=items[key]['target_offset']-e['offset'];raw=encode(items[key]['translation'])
            self.assertGreater(start,nul);self.assertLess(start,oldstart);self.assertIn(start%4,(2,3))
            self.assertEqual(a[:start],b[:start]);self.assertEqual(a[nul+1:oldstart],bytes(oldstart-nul-1))
            self.assertEqual(b[start:],raw+b'\0');self.assertEqual(len(a),len(b));self.assertEqual(b[:start]+a[start:],a)
            self.assertEqual(locate(self.elf,b,previous,bytes.fromhex(e['tag'])),start)
        self.assertEqual(sum(any(s['key']!='label' and s['translation']!=s['source'] for s in e['segments']) for e in self.doc['entries']),5983)
    def test_original_strcpy_accepts_all_unaligned_sources_with_aligned_destination(self):
        for alignment in range(1,8):
            for text in ('Homem','Cão','Alto-falante','Ancião '):
                self.assertTrue(byte_copy_probe(self.elf,encode(text),alignment))
        for alignment in (0,8):
            with self.assertRaises(ValueError):byte_copy_probe(self.elf,b'Dog',alignment)
        with self.assertRaises(ValueError):byte_copy_probe(self.elf,b'a\0b',1)
    def test_v002_still_rejects_new_fields_and_v003_rejects_policy_hash_position_tampering(self):
        saved_doc=copy.deepcopy(self.old_doc);saved_report=copy.deepcopy(self.old_report)
        config=copy.deepcopy(self.child['speaker_label_byte_packing']);config['entries']=config['entries'][:1]
        def run(c,byte=True,preserved=()):return overlay(self.data,self.old_doc,self.old_patches,self.old_report,c,self.elf,preserved,byte_packed=byte)
        with self.assertRaises(ValueError):run(config,byte=False)
        for key in ('target_offset','base_record_sha256','record_sha256','label_sha256'):
            bad=copy.deepcopy(config);bad['entries'][0][key]=0 if key=='target_offset' else '0'*64
            with self.assertRaises(ValueError):run(bad)
        bad=copy.deepcopy(config);bad['entries']*=2
        with self.assertRaises(ValueError):run(bad)
        with self.assertRaises(ValueError):run(config,preserved=[config['entries'][0]['id']])
        bad=copy.deepcopy(config);bad['instruction_windows'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):run(bad)
        key=config['entries'][0]['id'];entry=next(e for e in self.old_doc['entries'] if e['id']==key)
        prior=next((p for p in self.old_patches if p['id']==key),None)
        base=prior['after'] if prior else bytes(self.data[entry['offset']:entry['offset']+entry['size']])
        with self.assertRaises(ValueError):placement(base,entry,config['entries'][0]['translation'])
        with self.assertRaises(ValueError):placement(base,entry,config['entries'][0]['translation'],alignment=2)
        self.assertEqual(self.old_doc,saved_doc);self.assertEqual(self.old_report,saved_report)
    def test_preparer_reproduces_and_inherits_byte_entries_without_dropping_aligned_profile(self):
        import prepare_speaker_labels as tool
        from unittest.mock import patch
        with patch.object(tool,'compile_draft',return_value=(self.old_doc,self.old_patches,self.old_report)):
            config,report=tool.prepare_relocations(self.data,self.parent,self.elf,byte_packed=True)
        self.assertEqual(config,self.child['speaker_label_byte_packing']);self.assertEqual(report['new_label_fields'],75)
        self.assertEqual(report['remaining_reviewed_role_references'],53)
        with patch.object(tool,'compile_draft',return_value=(self.doc,self.patches,self.report)):
            config,report=tool.prepare_relocations(self.data,self.child,self.elf,byte_packed=True)
        self.assertEqual(config,self.child['speaker_label_byte_packing']);self.assertEqual(report['new_label_fields'],0)
    def test_interface_and_legacy_evidence_preserved_counts_separate(self):
        old=json.loads((ROOT/'translations/interface-v035.json').read_text(encoding='utf-8'));new=json.loads((ROOT/'translations/interface-v036.json').read_text(encoding='utf-8'))
        for key in old:
            if key not in ('status','iso_name','base_dialogue_draft'):self.assertEqual(old[key],new[key],key)
        for key in ('speaker_labels','speaker_label_relocations'):self.assertEqual(self.old_report[key],self.report[key])
        self.assertEqual(self.report['accepted'],self.old_report['accepted']+self.report['speaker_label_byte_packing']['new_changed_records'])
        self.assertEqual(self.report['speaker_label_byte_packing']['accepted'],75)


if __name__=='__main__':unittest.main()
