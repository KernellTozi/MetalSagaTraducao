import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import pending_name_resolution as pending
import item_names as names
from gfi import encode,decode
from interface_text import SOURCE as ELF
from build_translation_pilot import load_draft

class PendingNameResolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/'translations/interface-v044.json').read_text(encoding='utf-8'))
        cls.new=json.loads((ROOT/'translations/interface-v045.json').read_text(encoding='utf-8'))
        cls.binding=cls.new['pending_name_resolution'];cls.m,_=pending.load(cls.binding)
        cls.raw=names.original(names.RESOURCE);cls.rows=names.catalog(cls.raw);cls.by={r['index']:r for r in cls.rows}
        cls.elf=ELF.read_bytes();cls.a,_=names.compile_names(cls.elf,cls.old['item_names'])
        cls.b,cls.report=names.compile_names(cls.elf,cls.new['item_names'])

    def test_exact_fourteen_pending_promoted_and_all_527_previous_names_frozen(self):
        a={r['id']:r for r in self.old['item_names']['entries']};b={r['id']:r for r in self.new['item_names']['entries']}
        self.assertEqual(set(b)-set(a),{r['id'] for r in self.old['item_name_review']['pending']})
        self.assertEqual(len(b)-len(a),14);self.assertEqual(self.report['accepted'],541)
        for k,v in a.items():self.assertEqual(v,b[k])
        self.assertEqual(self.new['item_name_review']['pending'],[])
        names.validate_review(self.new['item_name_review'],self.new['item_names'],self.rows)
        self.assertEqual(self.old['item_name_review']['preserved'],self.new['item_name_review']['preserved'])

    def test_supported_glyphs_exact_names_bytes_and_independent_ids(self):
        for r in self.m['approved']:
            value=encode(r['translation']);self.assertEqual(value.hex(),r['encoded_hex'])
            self.assertEqual(len(value),r['encoded_bytes']);self.assertLessEqual(len(value),16)
            self.assertEqual(decode(value),r['translation'])
            self.assertEqual(r['translation'],pending.NAMES[r['index']])
            self.assertEqual([x['index'] for x in self.rows if x['source_hex']==self.by[r['index']]['source_hex']],[r['index']])

    def test_combined_name_and_description_roundtrip_preserves_attributes(self):
        from description_pool import compile_pool
        old_desc,_=compile_pool(self.elf,self.old['item_descriptions']);new_desc,_=compile_pool(self.elf,self.new['item_descriptions'])
        a=bytearray(self.raw);b=bytearray(self.raw)
        for target,patches in ((a,self.a+old_desc),(b,self.b+new_desc)):
            for p in patches:target[p['offset']:p['offset']+len(p['after'])]=p['after']
        for r in self.rows:
            at=r['offset'];self.assertEqual(b[at+28:at+128],self.raw[at+28:at+128])
            if r['index'] not in pending.NAMES:self.assertEqual(a[at:at+24],b[at:at+24])
            else:self.assertEqual(b[at:at+24].split(b'\0',1)[0],encode(pending.NAMES[r['index']]))
        for p in reversed(self.b+new_desc):b[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(b,self.raw)

    def test_term_exceptions_do_not_release_character_or_unique_weapon_names(self):
        for idx in (625,631,695):
            target=pending.NAMES[idx]
            with self.assertRaises(ValueError):names.validate_value(self.by[idx],target,ceiling=16)
            self.assertEqual(names.validate_value(self.by[idx],target,ceiling=16,pending_review=True),encode(target))
            with self.assertRaises(ValueError):names.validate_value(self.by[idx],'Outro nome',ceiling=16,pending_review=True)
        self.assertIsNone(pending.term_exception(self.by[630],'Presa'))
        from translation_policy import validate
        self.assertIn('Termo/nome protegido ausente: Fang',validate('You are Fang.','Você é Presa.'))
        self.assertTrue(validate('Basic component of the Twin Fang.','Componente da Presa.'))

    def test_exact_interface_and_single_fridge_description_revision(self):
        pending.validate_interface(self.new)
        old={r['id']:r for r in self.old['item_descriptions']['entries']};new={r['id']:r for r in self.new['item_descriptions']['entries']}
        self.assertEqual({k for k,v in new.items() if old[k]!=v},{self.m['fridge_description']['id']})
        row=new[self.m['fridge_description']['id']]
        self.assertEqual(row['translation'],pending.FRIDGE);self.assertEqual([i['id'] for i in row['item_records']],[768])
        for key in ('spack_battle','resource_texts','spack_interactions','graphics','entries','layout_profile'):
            self.assertEqual(self.old[key],self.new[key])
        bad=copy.deepcopy(self.new);bad['item_names']['entries'][0]['translation']='Alteração extra'
        with self.assertRaises(ValueError):pending.validate_interface(bad)
        bad=copy.deepcopy(self.new['item_descriptions']);bad['entries'][0]['translation']='Alteração extra'
        with self.assertRaises(ValueError):pending.validate_descriptions(bad)

    def test_four_bus_references_and_one_speaker_hash_preserve_other_narrative(self):
        old,_=load_draft(ROOT/self.old['base_dialogue_draft']);new,_=load_draft(ROOT/self.new['base_dialogue_draft'])
        pending.validate_narrative(new)
        self.assertEqual({k for k,v in new['translations'].items() if old['translations'][k]!=v},set(pending.BUS_IDS))
        for key in ('aliases','deferred','preservation_decisions','speaker_context_review','speaker_labels','speaker_label_byte_packing'):
            self.assertEqual(old[key],new[key])
        a=old['speaker_label_relocations'];b=copy.deepcopy(new['speaker_label_relocations'])
        changed=[(x,y) for x,y in zip(a['entries'],b['entries']) if x!=y];self.assertEqual(len(changed),1)
        x,y=changed[0];self.assertEqual(y['id'],'map.msgn.0e76fcc4')
        self.assertEqual(y['translation'],'Homem');self.assertEqual(y['target_offset'],x['target_offset'])
        y['base_record_sha256']=x['base_record_sha256'];self.assertEqual(a,b)
        for r in self.m['bus_stop_references']:
            key=r['id'];before=old['translations'][key];after=r['translation']
            if isinstance(after,dict):self.assertEqual(before['choices'],after['choices'])
        self.assertIn('rara...',new['translations']['map.smsg.0e5517d4']['body'])

    def test_name_consistency_ledger_preserves_fang_and_closes_all_matches(self):
        from audit_name_consistency import scan,reviewed_findings
        result=scan(self.new);self.assertEqual(result['name_fields'],541);self.assertEqual(result['possible_references'],65)
        path=ROOT/'translations/consistencia-nomes-decisoes-v002.json';ledger=json.loads(path.read_text(encoding='utf-8'))
        review=reviewed_findings(result,ledger['output_recipe_sha256'],path)
        self.assertEqual(review['unresolved_matches'],[])
        reasons=[r['reason'] for r in ledger['decisions']]
        self.assertEqual(reasons.count('protected-twin-fang-weapon-name'),2)
        self.assertEqual(reasons.count('protected-fang-character-name'),7)
        self.assertEqual(reasons.count('same-bus-stop-sign-item-canonical-reference'),4)

    def test_width_probes_keep_all_names_within_original_envelope(self):
        from measure_item_name_widths import measure
        result=measure(ROOT/'translations/interface-v045.json')
        self.assertEqual(result['reviewed_names_measured'],14)
        self.assertEqual(result['unique_glyph_profile_probes'],444)
        self.assertEqual(result['names_above_observed_advance_envelope'],[])

if __name__=='__main__':unittest.main()
