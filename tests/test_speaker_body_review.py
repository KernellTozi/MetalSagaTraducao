import copy,json,mmap,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import speaker_body_review as s
from build_translation_pilot import compile_draft,load_draft
from reinsertion import SOURCE
from interface_text import SOURCE as ELF
from gfi import encode,decode

class SpeakerBodyReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stream=SOURCE.open('rb');cls.data=mmap.mmap(cls.stream.fileno(),0,access=mmap.ACCESS_READ);cls.elf=ELF.read_bytes()
        cls.parent,_=load_draft(ROOT/s.PARENT_MAP);cls.child,_=load_draft(ROOT/'translations/regiao-inicial-v042.json')
        cls.before,cls.oldpatches,cls.oldreport=compile_draft(cls.data,cls.parent)
        cls.after,cls.patches,cls.report=compile_draft(cls.data,cls.child)
        cls.oldby={e['id']:e for e in cls.before['entries']};cls.newby={e['id']:e for e in cls.after['entries']}
        cls.oldp={p['id']:p for p in cls.oldpatches};cls.newp={p['id']:p for p in cls.patches}
        cls.m=s.load(cls.child['speaker_body_review'])
    @classmethod
    def tearDownClass(cls):cls.data.close();cls.stream.close()

    def test_36_full_labels_13_preserved_without_record_growth(self):
        self.assertEqual(len(self.m['entries']),36);self.assertEqual(len(self.m['remaining']),13)
        self.assertEqual(self.report['speaker_body_review']['accepted'],36)
        for row in self.m['entries']:
            e=self.oldby[row['id']];self.assertEqual(row['translation'],s.ROLES[e['segments'][-1]['source']])
            self.assertLess(row['new_body_bytes'],row['old_body_bytes'])
            self.assertEqual(len(self.newp[row['id']]['after']),e['size'])

    def test_parent_phrases_and_labels_preserved_for_all_13_deferred(self):
        for row in self.m['remaining']:
            key=row['id'];self.assertEqual(self.oldby[key],self.newby[key])
            self.assertEqual(self.oldp.get(key),self.newp.get(key))
        texts=[self.newby[r['id']]['segments'][0]['translation'] for r in self.m['remaining']]
        for expression in ('Woohoo!','Meow...','Woof...','Ice, ice, baby!','Banzai!','......','Quem te ama, baby?','Mm--mmm, bom!'):
            self.assertIn(expression,texts)

    def test_all_other_records_patches_and_native_fallbacks_unchanged(self):
        selected=set(s.bodies());self.assertEqual(set(self.oldp),set(self.newp))
        for key in self.oldby:
            if key not in selected:self.assertEqual(self.oldby[key],self.newby[key])
        for key in self.oldp:
            if key not in selected:self.assertEqual(self.oldp[key],self.newp[key])
        self.assertEqual(self.report['native_fallback_overlay'],self.oldreport['native_fallback_overlay'])
        self.assertEqual(self.report['preservation_decisions'],self.oldreport['preservation_decisions'])

    def test_header_body_label_codec_and_guards(self):
        from speaker_label_space import locate
        from reinsertion import control_check
        from control_dialogue_quirks import tokenize
        for row in self.m['entries']:
            key=row['id'];p=self.newp[key];e=self.newby[key];at=row['target_label_offset']-e['offset']
            self.assertEqual(p['after'][:32],p['before'][:32]);self.assertEqual(p['before'],self.oldp[key]['before'])
            self.assertEqual(p['after'][32:].split(b'\0',1)[0],encode(row['body_translation']))
            self.assertEqual(p['after'][at:],encode(row['translation'])+bytes(len(p['after'])-at-len(encode(row['translation']))))
            self.assertEqual(locate(self.elf,p['after'],32,b'msgn'),at)
            self.assertEqual(decode(p['after'][at:].split(b'\0',1)[0]),row['translation'])
            control_check(bytes.fromhex(e['segments'][0]['source_hex']),encode(row['body_translation']),tokenize)

    def test_extraction_fingerprints_and_offsets_only_in_compiled_wrapper(self):
        for row in self.m['entries']:
            key=row['id'];old=copy.deepcopy(self.oldby[key]);new=copy.deepcopy(self.newby[key])
            for e in (old,new):
                for part in e['segments']:part.pop('translation')
            self.assertEqual(old,new);self.assertFalse(new['segments'][-1]['editable'])
            self.assertEqual(self.after['compiled_speaker_label_offsets'][key],row['target_label_offset'])
            self.assertEqual(self.after['compiled_dialogue_segment_offsets'][key],{'body':new['offset']+32,'label':row['target_label_offset']})

    def test_resolved_aliases_match_compiled_bodies_without_unselected_changes(self):
        def resolved(d):
            values=dict(d['translations']);todo=dict(d['aliases'])
            while todo:
                ready=[k for k,p in todo.items() if p in values]
                self.assertTrue(ready)
                for key in ready:values[key]=values[todo.pop(key)]
            return values
        old,new=resolved(self.parent),resolved(self.child)
        for key in old:
            if key not in s.bodies():self.assertEqual(old[key],new[key])
        for key,text in s.bodies().items():
            self.assertEqual(new[key],text);self.assertEqual(self.newby[key]['segments'][0]['translation'],text)
        self.assertEqual(self.parent['aliases'],self.child['aliases'])

    def test_report_offsets_lengths_and_counters(self):
        rows={r['id']:r for r in self.report['results']}
        self.assertTrue(self.report['valid']);self.assertEqual(self.report['accepted'],6032)
        self.assertEqual(self.report['unchanged'],1199);self.assertEqual(self.report['refused'],0)
        self.assertEqual(self.report['deferred'],self.oldreport['deferred'])
        for item in self.m['entries']:
            key=item['id'];e=self.newby[key]
            self.assertEqual(rows[key]['target_lengths'],[len(encode(p['translation'])) for p in e['segments']])
            self.assertEqual(rows[key]['target_offsets'],[e['offset']+32,item['target_label_offset']])

    def test_changes_to_body_label_source_and_global_recipe_refused(self):
        row=self.m['entries'][0];e=self.oldby[row['id']];base=self.oldp[row['id']]['after']
        with self.assertRaises(ValueError):s.construct(self.data,e,base,'Frase arbitrária.',self.elf)
        bad=bytearray(base);bad[32]^=1
        with self.assertRaises(ValueError):s.construct(self.data,e,bytes(bad),row['body_translation'],self.elf)
        for field in ('layout_profile','preservation_decisions','aliases'):
            bad=copy.deepcopy(self.child);bad[field]={} if field!='layout_profile' else 'spacing-v003'
            with self.assertRaises(ValueError):s.validate_narrative(bad)
        bad=copy.deepcopy(self.child);bad['speaker_body_review']['sha256']='0'*64
        with self.assertRaises(ValueError):compile_draft(self.data,bad)

    def test_names_roles_and_remaining_labels_not_generically_editable(self):
        for key in [r['id'] for r in self.m['remaining']]:
            e=self.oldby[key];base=self.oldp.get(key,{'after':bytes(self.data[e['offset']:e['offset']+e['size']])})['after']
            with self.assertRaises(ValueError):s.construct(self.data,e,base,'X',self.elf)

    def test_legacy_validator_dispatch_and_every_ui_resource_preserved(self):
        from dialogue_native_eight import validate_interface
        ui=json.loads((ROOT/'translations/interface-v049.json').read_text(encoding='utf-8'));parent=json.loads((ROOT/s.PARENT_UI).read_text(encoding='utf-8'))
        validate_interface(ui);validate_interface(parent)
        allowed={'speaker_body_review','base_dialogue_draft','iso_name','status'}
        self.assertEqual({k:v for k,v in ui.items() if k not in allowed},{k:v for k,v in parent.items() if k not in allowed})
        bad=copy.deepcopy(ui);bad['paint_captions']={}
        with self.assertRaises(ValueError):validate_interface(bad)

    def test_current_backlog_counts_actual_948_translated_labels(self):
        from audit_dialogue_backlog import collect_labels
        meta,rows=collect_labels(self.after)
        self.assertEqual(meta['translated_label_references'],948)
        self.assertEqual(meta['remaining_label_references'],579)
        self.assertEqual(meta['explicit_body_review_policy'],s.POLICY)

    def test_final_padding_survey_is_not_an_expansion_license(self):
        survey=s.tail_storage_survey(self.data,self.before,self.oldpatches)
        self.assertEqual(survey['pending_examined'],49);self.assertEqual(survey['distinct_ssd_blocks'],31)
        self.assertEqual(survey['with_final_padding_candidate'],4)
        self.assertEqual(survey['single_record_blocks'],1);self.assertFalse(survey['editing_authorized'])

if __name__=='__main__':unittest.main()
