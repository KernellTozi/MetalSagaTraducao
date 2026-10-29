import copy,json,mmap,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import dialogue_context_finish as s
from build_translation_pilot import load_draft,compile_draft
from reinsertion import SOURCE,control_check
from gfi import encode

class ContextFinish(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file=SOURCE.open('rb');cls.data=mmap.mmap(cls.file.fileno(),0,access=mmap.ACCESS_READ)
        cls.parent,_=load_draft(ROOT/s.PARENT_MAP);cls.child,_=load_draft(ROOT/s.MAP)
        cls.old,op,cls.old_report=compile_draft(cls.data,cls.parent)
        cls.new,np,cls.report=compile_draft(cls.data,cls.child)
        cls.op={r['id']:r for r in op};cls.np={r['id']:r for r in np}
        cls.a={e['id']:e for e in cls.old['entries']};cls.b={e['id']:e for e in cls.new['entries']}
        cls.m=s.load(cls.child['context_finish_review']);cls.labels={r['id'] for r in cls.m['captions']}
    @classmethod
    def tearDownClass(cls):cls.data.close();cls.file.close()

    def test_exact_11_captions_and_5_bodies_with_honest_counts(self):
        from audit_dialogue_backlog import collect_labels
        self.assertEqual(len(self.labels),11);self.assertEqual(len(self.m['bodies']),5);self.assertFalse(self.labels&set(s.BODIES))
        self.assertEqual(self.report['accepted'],6044);self.assertEqual(self.report['refused'],0)
        self.assertEqual(self.report['context_finish_review']['new_changed_records'],1)
        self.assertEqual(collect_labels(self.new)[0]['translated_label_references'],991)
        self.assertEqual(sum(any(p['key']!='label' and p['source']!=p['translation'] for p in e['segments']) for e in self.new['entries']),5991)

    def test_all_other_records_and_patches_unchanged(self):
        selected=self.labels|set(s.BODIES)
        for key,e in self.a.items():
            if key not in selected:self.assertEqual(e,self.b[key]);self.assertEqual(self.op.get(key),self.np.get(key))
        self.assertEqual(set(self.np)-set(self.op),{'map.msgn.1033ebc8'})
        for key in ('native_fallback_overlay','speaker_labels','speaker_label_relocations','speaker_label_byte_packing','speaker_context_review','speaker_body_review','speaker_faction_review','deferred','preservation_decisions'):
            self.assertEqual(self.old_report.get(key),self.report.get(key))

    def test_captions_only_change_original_label_fields(self):
        for key in self.labels:
            e=self.a[key];label=e['segments'][-1];at=label['offset']-e['offset'];end=at+label['capacity']+1
            before=self.op.get(key,{'after':bytes(self.data[e['offset']:e['offset']+e['size']])})['after'];after=self.np[key]['after']
            self.assertEqual(before[:at],after[:at]);self.assertEqual(before[end:],after[end:])
            self.assertEqual(e['segments'][:-1],self.b[key]['segments'][:-1]);self.assertFalse(self.b[key]['segments'][-1]['editable'])
            self.assertEqual(self.b[key]['segments'][-1]['translation'],s.ROLES[label['source']])

    def test_body_controls_adjacent_captions_choices_and_reverse_roundtrip(self):
        from interface_text import SOURCE as ELF
        from speaker_label_space import locate
        elf=ELF.read_bytes()
        for row in self.m['bodies']:
            self.assertNotEqual(row['parent_body_sha256'],row['target_body_sha256'])
            key=row['id'];e=self.a[key];start=row['offset']-e['offset'];end=start+row['span']
            a=self.op[key]['after'];b=self.np[key]['after'];self.assertEqual(a[:start],b[:start]);self.assertEqual(a[end:],b[end:])
            self.assertEqual(self.a[key]['segments'][1:],self.b[key]['segments'][1:])
            self.assertEqual(a,b[:start]+a[start:end]+b[end:]);self.assertLessEqual(row['offset']+row['span'],row['compiled_next_segment_offset'])
            body=self.b[key]['segments'][0];control_check(bytes.fromhex(body['source_hex']),encode(body['translation']))
            self.assertEqual(b[start:].split(b'\0',1)[0],encode(body['translation']))
            self.assertEqual(row['warnings'],[])
            if bytes.fromhex(e['tag'])==b'msgn':
                label_at=self.old.get('compiled_speaker_label_offsets',{}).get(key,e['segments'][-1]['offset'])-e['offset']
                self.assertEqual(locate(elf,a,start,b'msgn'),label_at)
                self.assertEqual(locate(elf,b,start,b'msgn'),label_at)

    def test_aliases_extraction_fingerprints_and_compiled_offsets_unchanged(self):
        self.assertEqual(self.parent['aliases'],self.child['aliases'])
        self.assertFalse(any(k in s.BODIES or p in s.BODIES for k,p in self.parent['aliases'].items()))
        for key in self.labels|set(s.BODIES):
            a=copy.deepcopy(self.a[key]);b=copy.deepcopy(self.b[key])
            for e in (a,b):
                for p in e['segments']:p.pop('translation')
            self.assertEqual(a,b)
        for key in ('compiled_dialogue_segment_offsets','compiled_speaker_label_offsets'):
            self.assertEqual(self.old.get(key),self.new.get(key))

    def test_named_entities_and_meaningful_context_are_preserved(self):
        self.assertIn('Binramen',self.b['map.msgn.1033ebc8']['segments'][-1]['translation'])
        self.assertIn('Torikami',s.BODIES['map.msgn.0be22c78']);self.assertIn('Scorpions',s.BODIES['map.msgn.0be22c78'])
        # A JSON newline followed by "esse" is not the word "nesse".
        self.assertEqual(self.a['map.msg.0be140fc'],self.b['map.msg.0be140fc'])
        self.assertIn('Como seria\nesse peixe',self.b['map.msg.0be140fc']['segments'][0]['translation'])
        for key,e in self.a.items():
            if e['segments'][-1]['source'] in ('Hunter','Soldier','Punk'):
                self.assertEqual(e['segments'][-1],self.b[key]['segments'][-1])

    def test_wrong_source_header_body_target_and_root_metadata_fail_closed(self):
        key=next(iter(s.BODIES));e=self.a[key];base=self.op[key]['after']
        with self.assertRaises(ValueError):s.revised_body(self.data,e,base,'Frase não revisada.',self.old)
        bad=bytearray(base);bad[0]^=1
        with self.assertRaises(ValueError):s.revised_body(self.data,e,bytes(bad),s.BODIES[key],self.old)
        bad=copy.deepcopy(e);bad['segments'][0]['source_hex']='41'
        with self.assertRaises(ValueError):s.revised_body(self.data,bad,base,s.BODIES[key],self.old)
        bad=copy.deepcopy(self.child);bad['translations'][key]='Tradução arbitrária'
        with self.assertRaises(ValueError):s.validate_narrative(bad)
        bad=copy.deepcopy(self.child);bad['layout_profile']='bad'
        with self.assertRaises(ValueError):s.validate_narrative(bad)

    def test_ui_exact_parent_and_legacy_caption_policy_remain_strict(self):
        from dialogue_native_eight import validate_interface
        from speaker_labels import validate_label
        ui=json.loads((ROOT/s.UI).read_bytes());old=json.loads((ROOT/s.PARENT_UI).read_bytes())
        validate_interface(ui);validate_interface(old)
        changed={'context_finish_review','base_dialogue_draft','iso_name','status'}
        self.assertEqual({k:v for k,v in ui.items() if k not in changed},{k:v for k,v in old.items() if k not in changed})
        for src,dst in s.ROLES.items():
            with self.assertRaises(ValueError):validate_label(src,dst,40)
        bad=copy.deepcopy(ui);bad['item_names']['entries'][0]['translation']='Mudança extra'
        with self.assertRaises(ValueError):validate_interface(bad)

    def test_13_space_blockers_16_item_decisions_and_poster_art_not_reopened(self):
        for row in json.loads((ROOT/'translations/rotulos-espaco-v005.json').read_bytes())['remaining']:
            key=row['id'];self.assertEqual(self.a[key],self.b[key]);self.assertEqual(self.op.get(key),self.np.get(key))
        before=json.loads((ROOT/s.PARENT_UI).read_bytes());after=json.loads((ROOT/s.UI).read_bytes())
        for key in ('item_names','spack_battle','graphics','layout_profile'):
            self.assertEqual(before[key],after[key])

if __name__=='__main__':unittest.main()
