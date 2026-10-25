import collections,copy,json,mmap,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from build_translation_pilot import SOURCE,load_draft,compile_draft
from interface_text import SOURCE as ELF
from speaker_label_review import POLICY,EXTRA,construct,locate_choices,overlay
from speaker_label_space import locate
from gfi import encode


class ContextReviewedSpeakerLabels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=ELF.read_bytes();cls.parent,_=load_draft(ROOT/'translations/regiao-inicial-v036.json');cls.child,_=load_draft(ROOT/'translations/regiao-inicial-v037.json')
        cls.stream=SOURCE.open('rb');cls.data=mmap.mmap(cls.stream.fileno(),0,access=mmap.ACCESS_READ)
        cls.old_doc,cls.old_patches,cls.old_report=compile_draft(cls.data,cls.parent)
        cls.doc,cls.patches,cls.report=compile_draft(cls.data,cls.child)
    @classmethod
    def tearDownClass(cls):cls.data.close();cls.stream.close()
    def test_inherited_bodies_options_metadata_and_all_previous_labels_preserved(self):
        self.assertTrue(self.report['valid']);self.assertEqual(self.report['refused'],0)
        for key in ('translations','deferred','speaker_labels','speaker_label_relocations','speaker_label_byte_packing','preservation_decisions'):self.assertEqual(self.parent[key],self.child[key])
        ids={e['id'] for e in self.child['speaker_context_review']['entries']};self.assertEqual(len(ids),45)
        for a,b in zip(self.old_doc['entries'],self.doc['entries']):
            self.assertEqual({k:v for k,v in a.items() if k!='segments'},{k:v for k,v in b.items() if k!='segments'})
            for s,t in zip(a['segments'],b['segments']):
                self.assertEqual({k:v for k,v in s.items() if k!='translation'},{k:v for k,v in t.items() if k!='translation'})
                if a['id'] not in ids or s['key']!='label':self.assertEqual(s,t)
        for key,at in self.old_doc['compiled_speaker_label_offsets'].items():self.assertEqual(self.doc['compiled_speaker_label_offsets'][key],at)
        self.assertEqual(sum(s['key']=='label' and s['source']!=s['translation'] for e in self.doc['entries'] for s in e['segments']),912)
        self.assertEqual(len(self.report['deferred']),27)
    def test_final_bytes_all_other_records_identical_and_options_only_relocated(self):
        old={p['id']:p for p in self.old_patches};new={p['id']:p for p in self.patches};items={e['id']:e for e in self.child['speaker_context_review']['entries']}
        self.assertTrue(old.keys()<=new.keys());layouts=collections.Counter()
        for e in self.doc['entries']:
            key=e['id'];original=bytes(self.data[e['offset']:e['offset']+e['size']]);a=old[key]['after'] if key in old else original;b=new[key]['after'] if key in new else original
            if key not in items:self.assertEqual(a,b);continue
            item=items[key];layouts[item['layout']]+=1;positions=[at-e['offset'] for at in item['target_offsets']]
            self.assertEqual(len(a),len(b));header=len(bytes.fromhex(e['header_hex']));self.assertEqual(a[:header],b[:header])
            for s,at in zip(e['segments'][:-1],positions[:-1]):
                before=a[s['offset']-e['offset']:].split(b'\0',1)[0];after=b[at:].split(b'\0',1)[0];self.assertEqual(before,after)
            self.assertEqual(b[positions[-1]:].split(b'\0',1)[0],encode(item['translation']))
            self.assertEqual(locate(self.elf,b,positions[-2],bytes.fromhex(e['tag'])),positions[-1])
            if item['layout']=='named-choice-separator-pack':
                self.assertEqual(positions[0],header);self.assertEqual(positions[1]%4,0)
                self.assertLess(positions[1],e['segments'][1]['offset']-e['offset'])
                self.assertEqual(locate_choices(self.elf,b,positions[0]),positions[1])
            else:self.assertEqual(a[:positions[-1]],b[:positions[-1]])
        self.assertEqual(layouts,{'fixed-label-slot':38,'label-tail-bytes':3,'named-choice-separator-pack':4})
        for a,b in zip(self.patches,self.patches[1:]):self.assertLessEqual(a['offset']+len(a['before']),b['offset'])
    def test_context_selection_exact_counts_and_names_not_globally_authorized(self):
        rows={e['id']:e for e in self.old_doc['entries']};counts=collections.Counter()
        for item in self.child['speaker_context_review']['entries']:
            source=rows[item['id']]['segments'][-1]['source']
            if source in EXTRA:counts[source]+=1;self.assertEqual(item['translation'],EXTRA[source])
        self.assertEqual(counts,{'Muscle Man':19,'Executive Believer':17,'Bus Maniac':3,'Hunter Office employee':2})
        item=self.child['speaker_context_review']['entries'][0];entry=copy.deepcopy(rows[item['id']]);base=next(p['after'] for p in self.old_patches if p['id']==item['id'])
        for name in ('Nina','Father Muscle','Hunter','Soldier','BB Trooper'):
            entry['segments'][-1].update(source=name,translation=name,source_hex=name.encode().hex())
            with self.assertRaises(ValueError):construct(base,entry,name)
    def test_original_question_to_choices_scanner_empty_tail_and_accent_lead(self):
        for padding in (1,2,7,16):
            raw=b'ABC'+bytes(padding)+encode('É isso.\tNão.')+b'\0Man\0'
            self.assertEqual(locate_choices(self.elf,raw,0),3+padding)
        with self.assertRaises(ValueError):locate_choices(self.elf,b'ABC\0\0\0',0)
    def test_adulterated_bindings_offsets_names_and_preservations_refuse_without_mutation(self):
        config=copy.deepcopy(self.child['speaker_context_review']);config['entries']=config['entries'][:1]
        saved=copy.deepcopy(self.old_doc);saved_report=copy.deepcopy(self.old_report)
        def run(c,elf=None,preserved=()):return overlay(self.data,self.old_doc,self.old_patches,self.old_report,c,self.elf if elf is None else elf,preserved)
        for field in ('record_sha256','label_sha256','base_record_sha256','translation','layout','target_offsets'):
            bad=copy.deepcopy(config);bad['entries'][0][field]=[] if field=='target_offsets' else 'invalid'
            with self.assertRaises(ValueError):run(bad)
        bad=copy.deepcopy(config);bad['entries']*=2
        with self.assertRaises(ValueError):run(bad)
        with self.assertRaises(ValueError):run(config,preserved=[config['entries'][0]['id']])
        bad=copy.deepcopy(config);bad['instruction_windows'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):run(bad)
        elf=bytearray(self.elf);elf[0x1c6d58]^=1
        with self.assertRaises(ValueError):run(config,elf=elf)
        self.assertEqual(self.old_doc,saved);self.assertEqual(self.old_report,saved_report)
    def test_preparer_reproduces_config_and_retains_previous_context_entries(self):
        import prepare_speaker_context as tool
        from unittest.mock import patch
        with patch.object(tool,'compile_draft',return_value=(self.old_doc,self.old_patches,self.old_report)):
            config,report=tool.prepare(self.data,self.parent,self.elf)
        self.assertEqual(config,self.child['speaker_context_review']);self.assertEqual(report['new_label_fields'],45)
        self.assertEqual(report['remaining_role_references'],49)
        with patch.object(tool,'compile_draft',return_value=(self.doc,self.patches,self.report)):
            config,report=tool.prepare(self.data,self.child,self.elf)
        self.assertEqual(config,self.child['speaker_context_review']);self.assertEqual(report['new_label_fields'],0)
    def test_legacy_compiler_stays_protected_and_counts_do_not_claim_new_bodies(self):
        from reinsertion import compile_batch
        from dialogue_advanced import SsdIndex
        key=self.child['speaker_context_review']['entries'][0]['id'];doc=copy.deepcopy(self.doc);doc['entries']=[next(e for e in doc['entries'] if e['id']==key)]
        patches,report=compile_batch(self.data,doc,SsdIndex(self.data));self.assertFalse(report['valid']);self.assertEqual(patches,[])
        self.assertEqual(sum(any(s['key']!='label' and s['source']!=s['translation'] for s in e['segments']) for e in self.doc['entries']),5983)
        self.assertEqual(self.report['accepted'],self.old_report['accepted']+self.report['speaker_context_review']['new_changed_records'])
    def test_interface_is_unchanged(self):
        old=json.loads((ROOT/'translations/interface-v036.json').read_text(encoding='utf-8'));new=json.loads((ROOT/'translations/interface-v037.json').read_text(encoding='utf-8'))
        for key in old:
            if key not in ('status','iso_name','base_dialogue_draft'):self.assertEqual(old[key],new[key],key)


if __name__=='__main__':unittest.main()
