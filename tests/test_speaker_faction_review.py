import copy,json,mmap,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import speaker_faction_review as s
from build_translation_pilot import compile_draft,load_draft
from reinsertion import SOURCE
from interface_text import SOURCE as ELF
from gfi import encode

class SpeakerFactionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stream=SOURCE.open('rb');cls.data=mmap.mmap(cls.stream.fileno(),0,access=mmap.ACCESS_READ)
        cls.parent,_=load_draft(ROOT/s.PARENT_MAP);cls.child,_=load_draft(ROOT/s.MAP)
        cls.old,cls.op,cls.orp=compile_draft(cls.data,cls.parent)
        cls.new,cls.np,cls.nrp=compile_draft(cls.data,cls.child)
        cls.oldby={e['id']:e for e in cls.old['entries']};cls.newby={e['id']:e for e in cls.new['entries']}
        cls.op={p['id']:p for p in cls.op};cls.np={p['id']:p for p in cls.np}
        cls.manifest=s.load(cls.child['speaker_faction_review']);cls.ids={r['id'] for r in cls.manifest['entries']}
    @classmethod
    def tearDownClass(cls):cls.data.close();cls.stream.close()

    def test_exact_32_roles_and_all_occurrences_covered(self):
        found={e['id'] for e in self.old['entries'] if e['segments'][-1]['key']=='label' and e['segments'][-1]['source'] in s.TARGETS}
        self.assertEqual(self.ids,found);self.assertEqual(len(found),32)
        self.assertEqual(self.nrp['speaker_faction_review']['accepted'],32)
        self.assertEqual(sum(bytes.fromhex(self.newby[k]['tag'])==b'smnn' for k in found),1)

    def test_every_body_option_control_and_unselected_record_unchanged(self):
        for key,e in self.oldby.items():
            if key not in self.ids:self.assertEqual(e,self.newby[key]);self.assertEqual(self.op.get(key),self.np.get(key));continue
            self.assertEqual(e['segments'][:-1],self.newby[key]['segments'][:-1])
            a=copy.deepcopy(e);b=copy.deepcopy(self.newby[key]);a['segments'][-1].pop('translation');b['segments'][-1].pop('translation')
            self.assertEqual(a,b)

    def test_deltas_only_original_label_slots_and_nuls(self):
        for key in self.ids:
            e=self.oldby[key];label=e['segments'][-1];at=label['offset']-e['offset'];end=at+label['capacity']+1
            before=self.op.get(key,{'after':bytes(self.data[e['offset']:e['offset']+e['size']])})['after'];after=self.np[key]['after']
            self.assertEqual(before[:at],after[:at]);self.assertEqual(before[end:],after[end:]);self.assertEqual(len(before),len(after))
            raw=encode(s.TARGETS[label['source']]);self.assertEqual(after[at:end],raw+bytes(end-at-len(raw)))
            self.assertFalse(label['editable']);self.assertEqual(self.np[key]['before'],bytes(self.data[e['offset']:e['offset']+e['size']]))

    def test_hunter_soldier_names_sounds_and_13_blockers_preserved(self):
        for key,e in self.oldby.items():
            if e['segments'][-1]['source'] in ('Hunter','Soldier','Punk','Rosa','Mr. TNT'):
                self.assertEqual(e,self.newby[key])
        for row in json.loads((ROOT/'translations/rotulos-espaco-v005.json').read_bytes())['remaining']:
            key=row['id'];self.assertEqual(self.oldby[key],self.newby[key]);self.assertEqual(self.op.get(key),self.np.get(key))

    def test_context_metadata_ordinals_ex_prefix_and_probe_guards(self):
        self.assertEqual(s.TARGETS['Ex-BB Trooper'],'Ex-soldado BB')
        for i in range(1,7):self.assertEqual(s.TARGETS[f'BB Trooper #{i}'],f'Soldado BB #{i}')
        for row in self.nrp['speaker_faction_review']['results']:
            self.assertTrue(row['copy_and_guards']);self.assertTrue(row['static_getter'])
        for src,dst,cap in [('Hunter','Caçador',20),('Soldier','Soldado',20),('BB Trooper #1','Soldado BB #2',15),('BB Trooper','Soldado BB',8)]:
            with self.assertRaises(ValueError):s.validate_label(src,dst,cap)

    def test_legacy_fixed_policy_still_refuses_bb_roles(self):
        from speaker_labels import validate_label
        for src,dst in s.TARGETS.items():
            with self.assertRaises(ValueError):validate_label(src,dst,30)

    def test_whole_recipe_binding_and_extra_changes_refused(self):
        for field,value in [('layout_profile','bad'),('translations',{}),('aliases',{}),('preservation_decisions',{})]:
            bad=copy.deepcopy(self.child);bad[field]=value
            with self.assertRaises(ValueError):s.validate_narrative(bad)
        bad=copy.deepcopy(self.child);bad['speaker_faction_review']['sha256']='0'*64
        with self.assertRaises(ValueError):compile_draft(self.data,bad)

    def test_ui_history_and_fonts_untouched_and_invalid_changes_refused(self):
        from dialogue_native_eight import validate_interface
        ui=json.loads((ROOT/s.UI).read_bytes());old=json.loads((ROOT/s.PARENT_UI).read_bytes());validate_interface(ui);validate_interface(old)
        fields={'speaker_faction_review','base_dialogue_draft','iso_name','status'}
        self.assertEqual({k:v for k,v in ui.items() if k not in fields},{k:v for k,v in old.items() if k not in fields})
        bad=copy.deepcopy(ui);bad['layout_profile']='bad'
        with self.assertRaises(ValueError):validate_interface(bad)

    def test_historical_layers_and_accounting_retained(self):
        from audit_dialogue_backlog import collect_labels
        count,_=collect_labels(self.new);self.assertEqual(count['translated_label_references'],980);self.assertEqual(count['remaining_label_references'],547)
        for key in ('speaker_labels','speaker_label_relocations','speaker_label_byte_packing','speaker_context_review','speaker_body_review','native_fallback_overlay','deferred','preservation_decisions'):
            self.assertEqual(self.orp.get(key),self.nrp.get(key))
        added=set(self.np)-set(self.op);self.assertEqual(len(added),11)
        self.assertEqual(self.nrp['accepted'],6043);self.assertEqual(self.nrp['refused'],0)
        self.assertEqual(self.nrp['speaker_faction_review']['new_changed_records'],11)

if __name__=='__main__':unittest.main()
