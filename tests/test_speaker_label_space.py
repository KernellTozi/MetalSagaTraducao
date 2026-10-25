import copy,json,mmap,sys,unittest,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from build_translation_pilot import SOURCE,load_draft,compile_draft
from interface_text import SOURCE as ELF
from speaker_label_space import POLICY,bindings,locate,placement,overlay
from gfi import encode


class SpeakerLabelSpace(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=ELF.read_bytes();cls.parent,_=load_draft(ROOT/'translations/regiao-inicial-v034.json')
        cls.child,_=load_draft(ROOT/'translations/regiao-inicial-v035.json')
        cls.stream=SOURCE.open('rb');cls.data=mmap.mmap(cls.stream.fileno(),0,access=mmap.ACCESS_READ)
        cls.old_doc,cls.old_patches,cls.old_report=compile_draft(cls.data,cls.parent)
        cls.doc,cls.patches,cls.report=compile_draft(cls.data,cls.child)
    @classmethod
    def tearDownClass(cls):cls.data.close();cls.stream.close()
    def test_prior_translations_labels_and_deferrals_preserved(self):
        self.assertTrue(self.report['valid']);self.assertEqual(self.report['refused'],0)
        for key in ('translations','deferred','speaker_labels','preservation_decisions'):
            self.assertEqual(self.parent[key],self.child[key])
        items=self.child['speaker_label_relocations']['entries'];ids={i['id'] for i in items}
        self.assertEqual(len(ids),239);self.assertEqual(len(self.report['deferred']),27)
        self.assertEqual(self.report['speaker_labels']['accepted'],553)
        self.assertEqual(self.report['speaker_label_relocations']['accepted'],239)
        for a,b in zip(self.old_doc['entries'],self.doc['entries']):
            self.assertEqual({k:v for k,v in a.items() if k!='segments'},{k:v for k,v in b.items() if k!='segments'})
            for s,t in zip(a['segments'],b['segments']):
                self.assertEqual({k:v for k,v in s.items() if k!='translation'},{k:v for k,v in t.items() if k!='translation'})
                if a['id'] not in ids or s['key']!='label':self.assertEqual(s,t)
                else:self.assertFalse(t['editable'])
    def test_real_delta_only_zero_separators_and_labels_with_full_reverse(self):
        old={p['id']:p for p in self.old_patches};new={p['id']:p for p in self.patches}
        items={i['id']:i for i in self.child['speaker_label_relocations']['entries']};families=collections.Counter()
        self.assertTrue(old.keys()<=new.keys())
        for e in self.doc['entries']:
            key=e['id'];original=bytes(self.data[e['offset']:e['offset']+e['size']])
            a=old[key]['after'] if key in old else original;b=new[key]['after'] if key in new else original
            if key not in items:self.assertEqual(a,b);continue
            item=items[key];family=bytes.fromhex(e['tag']);families[family]+=1
            start=item['target_offset']-e['offset'];oldstart=e['segments'][-1]['offset']-e['offset'];previous=e['segments'][-2]['offset']-e['offset']
            nul=a.index(0,previous);self.assertGreater(start,nul);self.assertLess(start,oldstart);self.assertEqual(start%4,0)
            self.assertEqual(a[:start],b[:start]);self.assertEqual(a[nul+1:oldstart],bytes(oldstart-nul-1));self.assertEqual(len(a),len(b))
            self.assertEqual(locate(self.elf,b,previous,family),start)
            expected=encode(item['translation']);self.assertEqual(b[start:],expected+bytes(len(b)-start-len(expected)))
            self.assertEqual(b[:start]+a[start:],a)
        self.assertEqual(families,{b'msgn':226,b'smnn':13})
    def test_original_zero_scanners_with_accent_first_byte_and_short_padding(self):
        for family in (b'msgn',b'smnn',b'2snm'):
            for zeros in (1,2,8,32):
                raw=b'ABC'+bytes(zeros)+encode('Ancião')+b'\0'
                self.assertEqual(locate(self.elf,raw,0,family),3+zeros)
                raw=b'ABC'+bytes(zeros)+encode('Élder')+b'\0'
                self.assertEqual(locate(self.elf,raw,0,family),3+zeros)
        with self.assertRaises(ValueError):locate(self.elf,b'ABC\0\0\0',0,b'msgn')
    def test_binding_duplicate_base_drift_and_immutable_decisions_refused_atomically(self):
        config=copy.deepcopy(self.child['speaker_label_relocations']);config['entries']=config['entries'][:1]
        def run(c,elf=None,preserved=()):return overlay(self.data,self.old_doc,self.old_patches,self.old_report,c,self.elf if elf is None else elf,preserved)
        old=copy.deepcopy(self.old_doc);report=copy.deepcopy(self.old_report)
        for key in ('record_sha256','label_sha256','base_record_sha256','target_offset'):
            c=copy.deepcopy(config);c['entries'][0][key]=0 if key=='target_offset' else '0'*64
            with self.assertRaises(ValueError):run(c)
        c=copy.deepcopy(config);c['entries']*=2
        with self.assertRaises(ValueError):run(c)
        with self.assertRaises(ValueError):run(config,preserved=[config['entries'][0]['id']])
        elf=bytearray(self.elf);elf[0x1c6530]^=1
        with self.assertRaises(ValueError):run(config,elf=elf)
        c=copy.deepcopy(config);c['instruction_windows'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):run(c)
        self.assertEqual(self.old_doc,old);self.assertEqual(self.old_report,report)
    def test_overflow_and_delimiter_injection_do_not_consume_text(self):
        key=self.child['speaker_label_relocations']['entries'][0]['id'];e=copy.deepcopy(next(e for e in self.old_doc['entries'] if e['id']==key))
        p=next(p for p in self.old_patches if p['id']==key);base=bytearray(p['after']);label=e['segments'][-1];previous=e['segments'][-2]['offset']-e['offset'];end=label['offset']-e['offset']
        base[previous:end]=b'A'*(end-previous-1)+b'\0'
        target=self.child['speaker_label_relocations']['entries'][0]['translation']
        with self.assertRaises(ValueError):placement(bytes(base),e,target)
        with self.assertRaises(ValueError):placement(p['after'],e,target+'\n')
        e['blocked_reasons']=['unknown']
        with self.assertRaises(ValueError):placement(p['after'],e,target)
    def test_prepare_reproduces_config_and_does_not_drop_inherited_relocations(self):
        import prepare_speaker_labels as tool
        from unittest.mock import patch
        with patch.object(tool,'compile_draft',return_value=(self.old_doc,self.old_patches,self.old_report)):
            config,report=tool.prepare_relocations(self.data,self.parent,self.elf)
        self.assertEqual(config,self.child['speaker_label_relocations']);self.assertEqual(report['new_label_fields'],239)
        self.assertEqual(report['remaining_reviewed_role_references'],128)
        with patch.object(tool,'compile_draft',return_value=(self.doc,self.patches,self.report)):
            config,report=tool.prepare_relocations(self.data,self.child,self.elf)
        self.assertEqual(config,self.child['speaker_label_relocations']);self.assertEqual(report['new_label_fields'],0)
    def test_interface_unchanged_and_body_counts_not_inflated(self):
        old=json.loads((ROOT/'translations/interface-v034.json').read_text(encoding='utf-8'));new=json.loads((ROOT/'translations/interface-v035.json').read_text(encoding='utf-8'))
        for key in old:
            if key not in ('status','iso_name','base_dialogue_draft'):self.assertEqual(old[key],new[key],key)
        self.assertEqual(sum(any(s['key']!='label' and s['translation']!=s['source'] for s in e['segments']) for e in self.doc['entries']),5983)
        self.assertEqual(self.report['accepted'],self.old_report['accepted']+self.report['speaker_label_relocations']['new_changed_records'])


if __name__=='__main__':unittest.main()
