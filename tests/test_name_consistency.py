import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from dialogue import sha
from build_translation_pilot import load_draft
from audit_name_consistency import scan,reviewed_findings,signature
from name_reference_review import load,validate_interface,validate_narrative,revised_descriptions,filter_terminology

class NameConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/'translations/interface-v043.json').read_text(encoding='utf-8'))
        cls.new=json.loads((ROOT/'translations/interface-v044.json').read_text(encoding='utf-8'))
        cls.binding=cls.new['name_reference_review'];cls.m,_=load(cls.binding)
        cls.before=scan(cls.old);cls.after=scan(cls.new)
        cls.decision_path=ROOT/'translations/consistencia-nomes-decisoes-v001.json'
        cls.decisions=json.loads(cls.decision_path.read_text(encoding='utf-8'))

    def test_exact_interface_scope_and_unchanged_names(self):
        validate_interface(self.new)
        self.assertEqual(len(self.m['interface_changes']),16)
        self.assertEqual(self.old['item_names'],self.new['item_names'])
        self.assertEqual(self.old['item_name_review'],self.new['item_name_review'])
        self.assertEqual(self.old['spack_battle'],self.new['spack_battle'])
        # Descendants may retain the v043 name extension unchanged. That is
        # not a fresh v042 -> v043 transition and must not reapply its prefix fix.
        from verify_interface_revision import normalize_item_name_review_transition
        normalize_item_name_review_transition(self.old,self.new,ROOT/'translations/interface-v043.json',{}, {})
        bad=copy.deepcopy(self.new);bad['entries'][0]['translation']='Mudança extra'
        with self.assertRaises(ValueError):validate_interface(bad)

    def test_exact_eight_narrative_revisions_all_other_decisions_preserved(self):
        old,_=load_draft(ROOT/self.old['base_dialogue_draft']);new,_=load_draft(ROOT/self.new['base_dialogue_draft'])
        validate_narrative(new)
        changed={k for k in old['translations'] if old['translations'][k]!=new['translations'][k]}
        self.assertEqual(changed,{r['id'] for r in self.m['dialogue_changes']});self.assertEqual(len(changed),8)
        for key in ('deferred','aliases','preservation_decisions','speaker_context_review','layout_profile'):
            self.assertEqual(old[key],new[key])
        bad=copy.deepcopy(new);bad['translations']['map.sel.1df48484']='Outro texto'
        with self.assertRaises(ValueError):validate_narrative(bad)

    def test_twelve_description_revisions_pool_roundtrip_and_alias_readback(self):
        import description_pool as pool
        from interface_text import SOURCE
        from gfi import encode
        config=self.new['item_descriptions'];ids=revised_descriptions(config);self.assertEqual(len(ids),12)
        patches,report=pool.compile_pool(SOURCE.read_bytes(),config)
        raw=pool.original(pool.RESOURCE);out=bytearray(raw)
        for p in patches:out[p['offset']:p['offset']+len(p['after'])]=p['after']
        targets={r['id']:encode(r['translation']) for r in config['entries']}
        import struct
        for r in pool.topology(raw):
            for item in r['items']:
                at=pool.ITEM_BASE+item['id']*pool.STRIDE;offset=struct.unpack_from('<I',out,at+24)[0]
                self.assertEqual(out[at:at+24],raw[at:at+24]);self.assertEqual(out[at+28:at+128],raw[at+28:at+128])
                value=bytes(out[pool.POOL+offset:pool.POOL+offset+60]).split(b'\0',1)[0]
                self.assertEqual(value,targets.get(r['id'],bytes.fromhex(r['source_hex'])))
        for p in reversed(patches):out[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(out,raw);self.assertGreater(report['free_bytes'],0)

    def test_unapproved_description_change_rejected(self):
        bad=copy.deepcopy(self.new['item_descriptions']);bad['entries'][0]['translation']='Outra coisa'
        with self.assertRaises(ValueError):revised_descriptions(bad)
        bad=copy.deepcopy(self.new);bad['name_reference_review']['sha256']='0'*64
        with self.assertRaises(ValueError):validate_interface(bad)

    def test_all_81_matches_classified_only_25_corrected(self):
        self.assertEqual(self.before['name_fields'],527);self.assertEqual(self.before['fields_scanned'],10682)
        self.assertEqual(self.before['possible_references'],81);self.assertEqual(self.after['possible_references'],56)
        self.assertEqual(self.decisions['counts'],{'correct':25,'preserve':56})
        self.assertEqual(self.decisions['changed_unique_fields'],24)
        after={signature(r) for r in self.after['matches']}
        preserved={(r['field'],r['term_sha256'],r['text_sha256']) for r in self.decisions['decisions'] if r['action']=='preserve'}
        self.assertEqual(after,preserved)
        review=reviewed_findings(self.after,self.decisions['output_recipe_sha256'],self.decision_path)
        self.assertEqual(review['unresolved_matches'],[])

    def test_false_positives_and_existing_names_remain(self):
        reasons={r['reason'] for r in self.decisions['decisions'] if r['action']=='preserve'}
        for reason in ('hardware-memory-card','military-blockade-not-skill','protected-junk-zombies-enemy-name',
                       'treasure-map-not-cache-map','save-system-memory-center','c-unit-memory-chip-different-item',
                       'already-canonical-name-substring','ordinary-regenerate-verb'):
            self.assertIn(reason,reasons)
        text=self.new['resource_texts']['help'][14]['translation']
        self.assertIn('Secreção doce',text);self.assertIn('Massa gelatinosa',text)
        import re
        self.assertEqual(re.findall('<[^>]*>',text),re.findall('<[^>]*>',self.old['resource_texts']['help'][14]['translation']))

    def test_repair_kit_exception_is_record_and_source_bound(self):
        from translation_policy import validate
        from reinsertion import descriptor,SOURCE
        from dialogue_advanced import SsdIndex
        import mmap
        with SOURCE.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as raw:
            index=SsdIndex(raw)
            for key in ('map.msg.084ab3fc','map.msg.084ac950'):
                d=descriptor(raw,int(key.rsplit('.',1)[1],16),index,named_choices=True,quirk_refs=True)
                source=d['segments'][0]['source'];target=next(r['translation'] for r in self.m['dialogue_changes'] if r['id']==key)
                issues=validate(source,target);self.assertIn('Termo/nome protegido ausente: Repair Kit',issues)
                self.assertEqual(filter_terminology(self.binding,key,'body',source,target,issues),[])
                self.assertEqual(filter_terminology(self.binding,'map.msg.00000000','body',source,target,issues),issues)
                with self.assertRaises(ValueError):filter_terminology(self.binding,key,'body',source+'x',target,issues)

    def test_new_findings_and_recipe_mutations_cannot_be_silenced(self):
        modified=copy.deepcopy(self.after);modified['matches'][0]['text_sha256']='0'*64
        result=reviewed_findings(modified,self.decisions['output_recipe_sha256'],self.decision_path)
        self.assertEqual(len(result['unresolved_matches']),1)
        with self.assertRaises(ValueError):reviewed_findings(self.after,'0'*64,self.decision_path)

if __name__=='__main__':unittest.main()
