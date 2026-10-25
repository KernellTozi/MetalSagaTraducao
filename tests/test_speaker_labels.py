import copy,json,mmap,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from speaker_labels import ROLES,POLICY,bindings,probe,validate_label,overlay
from interface_text import SOURCE as ELF
from build_translation_pilot import SOURCE,load_draft,compile_draft
from gfi import encode


class SpeakerLabels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf=ELF.read_bytes()
        cls.parent,_=load_draft(ROOT/'translations/regiao-inicial-v033.json')
        cls.child,_=load_draft(ROOT/'translations/regiao-inicial-v034.json')
        cls.stream=SOURCE.open('rb');cls.data=mmap.mmap(cls.stream.fileno(),0,access=mmap.ACCESS_READ)
        cls.old_doc,cls.old_patches,cls.old_report=compile_draft(cls.data,cls.parent)
        cls.doc,cls.patches,cls.report=compile_draft(cls.data,cls.child)
    @classmethod
    def tearDownClass(cls):cls.data.close();cls.stream.close()
    def test_all_prior_body_translations_and_deferred_preserved(self):
        self.assertTrue(self.report['valid']);self.assertEqual(self.report['refused'],0)
        self.assertEqual(self.parent['translations'],self.child['translations'])
        self.assertEqual(self.parent['deferred'],self.child['deferred'])
        self.assertEqual(len(self.report['deferred']),27)
        config=self.child['speaker_labels'];ids={i['id'] for i in config['entries']}
        self.assertEqual(len(ids),553);self.assertEqual(self.report['speaker_labels']['accepted'],553)
        for old,new in zip(self.old_doc['entries'],self.doc['entries']):
            self.assertEqual({k:v for k,v in old.items() if k!='segments'},{k:v for k,v in new.items() if k!='segments'})
            for a,b in zip(old['segments'],new['segments']):
                self.assertEqual({k:v for k,v in a.items() if k!='translation'},{k:v for k,v in b.items() if k!='translation'})
                if old['id'] not in ids or a['key']!='label':self.assertEqual(a,b)
                else:self.assertFalse(b['editable']);self.assertEqual(b['translation'],ROLES[a['source']])
    def test_binary_delta_is_only_approved_label_slots_and_reverse_roundtrip(self):
        old={p['id']:p for p in self.old_patches};new={p['id']:p for p in self.patches}
        ids={i['id'] for i in self.child['speaker_labels']['entries']}
        self.assertTrue(old.keys()<=new.keys())
        for e in self.doc['entries']:
            key=e['id'];original=bytes(self.data[e['offset']:e['offset']+e['size']])
            a=old[key]['after'] if key in old else original;b=new[key]['after'] if key in new else original
            if key not in ids:self.assertEqual(a,b);continue
            label=next(s for s in e['segments'] if s['key']=='label');at=label['offset']-e['offset'];end=at+label['capacity']+1
            self.assertEqual(a[:at],b[:at]);self.assertEqual(a[end:],b[end:]);self.assertEqual(len(a),len(b))
            self.assertEqual(b[at:end],encode(label['translation'])+bytes(end-at-len(encode(label['translation']))))
            restored=b[:at]+a[at:end]+b[end:];self.assertEqual(restored,a)
        for a,b in zip(self.patches,self.patches[1:]):self.assertLessEqual(a['offset']+len(a['before']),b['offset'])
    def test_record_counts_do_not_claim_labels_as_new_dialogue_sentences(self):
        info=self.report['speaker_labels']
        self.assertEqual(self.report['accepted'],self.old_report['accepted']+info['new_changed_records'])
        self.assertEqual(self.old_report['accepted'],5983)
        self.assertFalse(info['pcsx2_executed']);self.assertIn('allocator stubbed',info['probe_limits'])
    def test_original_instructions_handle_full_ptbr_byte_lengths_and_guard(self):
        for text in ('Agente','Mecânico','Líder','Operário A','Recepcionista','Filha rica','ç á à ã â é ê í ó ô õ ú ü Ç Á É Ã Õ'):
            raw=encode(text);r=probe(self.elf,raw)
            self.assertEqual(r['bytes'],len(raw));self.assertEqual(r['allocated_bytes'],(len(raw)+4)&~3)
            self.assertTrue(r['static_getter']);self.assertTrue(r['copy_and_guards'])
        with self.assertRaises(ValueError):probe(self.elf,b'a\0b')
    def test_fixed_capacity_protected_names_and_unreviewed_targets(self):
        for source,target,capacity in [('Man','Homem',3),('Dog','Cão',3),('Hunter','Caçador',7),('Nina','Nina',7),('Guard','Guarda\n',7)]:
            with self.assertRaises(ValueError):validate_label(source,target,capacity)
        self.assertEqual(validate_label('Guard','Guarda',7),b'Guarda')
    def attempt(self,config,doc=None,elf=None,preserved=()):
        return overlay(self.data,self.old_doc if doc is None else doc,self.old_patches,self.old_report,config,self.elf if elf is None else elf,preserved)
    def test_drift_duplicate_protection_and_padding_fail_atomically(self):
        original_doc=copy.deepcopy(self.old_doc);original_report=copy.deepcopy(self.old_report)
        config=copy.deepcopy(self.child['speaker_labels']);config['entries']=config['entries'][:1]
        for field in ('record_sha256','label_sha256'):
            bad=copy.deepcopy(config);bad['entries'][0][field]='0'*64
            with self.assertRaises(ValueError):self.attempt(bad)
        bad=copy.deepcopy(config);bad['entries']*=2
        with self.assertRaises(ValueError):self.attempt(bad)
        with self.assertRaises(ValueError):self.attempt(config,preserved=[config['entries'][0]['id']])
        bad=copy.deepcopy(config);bad['instruction_windows'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):self.attempt(bad)
        elf=bytearray(self.elf);elf[0x1fda20]^=1
        with self.assertRaises(ValueError):self.attempt(config,elf=elf)
        doc=copy.deepcopy(self.old_doc);e=next(e for e in doc['entries'] if e['id']==config['entries'][0]['id'])
        next(s for s in e['segments'] if s['key']=='label')['capacity']+=1
        with self.assertRaises(ValueError):self.attempt(config,doc=doc)
        self.assertEqual(self.old_doc,original_doc);self.assertEqual(self.old_report,original_report)
    def test_legacy_compiler_still_rejects_label_edit(self):
        from reinsertion import compile_batch
        from dialogue_advanced import SsdIndex
        key=self.child['speaker_labels']['entries'][0]['id']
        doc=copy.deepcopy(self.old_doc);doc['entries']=[copy.deepcopy(next(e for e in self.doc['entries'] if e['id']==key))]
        patches,report=compile_batch(self.data,doc,SsdIndex(self.data))
        self.assertFalse(report['valid']);self.assertEqual(patches,[])
        self.assertIn('protegido',report['results'][0]['reason'])
    def test_interface_recipe_is_preserved_exactly(self):
        old=json.loads((ROOT/'translations/interface-v033.json').read_text(encoding='utf-8'))
        new=json.loads((ROOT/'translations/interface-v034.json').read_text(encoding='utf-8'))
        for key in old:
            if key not in ('status','iso_name','base_dialogue_draft'):self.assertEqual(old[key],new[key],key)


if __name__=='__main__':unittest.main()
