import copy,json,struct,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from item_descriptions import *
from prepare_item_batch import prepare,validate_review,wrap_words

class BroadItems(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent=json.loads((ROOT/'translations/interface-v017.json').read_text(encoding='utf-8'))
        cls.draft=json.loads((ROOT/'translations/interface-v018.json').read_text(encoding='utf-8'))
        cls.elf=original('SLUS_212.93');cls.raw=original(RESOURCE);cls.rows=catalog(cls.raw)
        cls.cfg=cls.draft['item_descriptions'];cls.review=cls.draft['description_review']
        cls.patches,cls.report=compile_descriptions(cls.elf,cls.cfg)
        cls.after=bytearray(cls.raw)
        for p in cls.patches:cls.after[p['offset']:p['offset']+len(p['after'])]=p['after']
    def test_previous_translation_and_other_resources_preserved(self):
        for key in self.parent:
            if key not in ('status','iso_name','item_descriptions','description_review'):
                self.assertEqual(self.parent[key],self.draft[key],key)
        old={e['id']:e for e in self.parent['item_descriptions']['entries']};new={e['id']:e for e in self.cfg['entries']}
        for key,target in old.items():self.assertEqual(target,new[key])
        self.assertEqual(len(new)-len(old),239);self.assertEqual(self.report['item_occurrences'],602)
    def test_disjoint_complete_ledger_and_single_control_blocker(self):
        validate_review(self.review,self.cfg,self.rows)
        self.assertEqual((self.review['reviewed'],self.review['accepted'],self.review['not_reviewed']),(567,353,0))
        self.assertEqual(len(self.review['pending']),213);self.assertEqual(len(self.review['preserved']),1)
        blockers=[e for e in self.review['pending'] if e.get('kind')=='technical-control']
        self.assertEqual([e['id'] for e in blockers],['item.description.03226'])
        self.assertEqual(next(r for r in self.rows if r['id']==self.review['preserved'][0]['id'])['source_hex'],'3f3f3f')
    def test_every_pointer_byte_length_and_alias_readback(self):
        targets={e['id']:e for e in self.cfg['entries']};seen=0
        for row in self.rows:
            at=row['offset'];value=bytes(self.after[at:self.after.index(0,at)])
            self.assertEqual(value,encode(targets[row['id']]['translation']) if row['id'] in targets else bytes.fromhex(row['source_hex']))
            self.assertEqual(execute_description_pointer(self.elf,bytes(self.after[POOL:POOL+SIZE]),at-POOL),at-POOL)
            self.assertEqual(execute_byte_length(self.elf,value),len(value));seen+=len(row['items'])
        self.assertEqual(seen,927)
        self.assertEqual(self.after[:POOL],self.raw[:POOL]);self.assertEqual(self.after[POOL+SIZE:],self.raw[POOL+SIZE:])
    def test_preparer_reproduces_recipe_without_network_or_local_proposal_file(self):
        old={e['id'] for e in self.parent['item_descriptions']['entries']}|{e['id'] for e in self.parent['description_review']['pending']}
        proposals={e['id']:e['translation'] for e in self.cfg['entries'] if e['id'] not in old}
        proposals.update({e['id']:e['proposed'] for e in self.review['pending'] if e['id'] not in old})
        sources={r['id']:bytes.fromhex(r['source_hex']).decode('ascii') for r in self.rows}
        proposals.update({e['id']:sources[e['id']] for e in self.review['preserved']})
        self.assertEqual(len(proposals),392)
        self.assertEqual(prepare(self.parent,proposals,'interface-v018'),self.draft)
    def test_bad_ledger_hash_duplicates_and_counts_rejected(self):
        for change in ('count','overlap','hash','policy'):
            ledger=copy.deepcopy(self.review)
            if change=='count':ledger['accepted']+=1
            elif change=='overlap':ledger['pending'][0]['id']=self.cfg['entries'][0]['id']
            elif change=='hash':ledger['pending'][0]['source_sha256']='bad'
            else:ledger['policy']='unknown'
            with self.subTest(change=change),self.assertRaises(ValueError):validate_review(ledger,self.cfg,self.rows)
    def test_accepted_cannot_be_overwritten_deferred_requires_explicit_resume(self):
        accepted=self.cfg['entries'][0]['id'];pending=self.review['pending'][0]['id']
        for key in (accepted,pending,'unknown'):
            with self.assertRaises(ValueError):prepare(self.draft,{key:'Teste'},'interface-v019')
        # Rejected attempt remains deferred and does not double-count its ID.
        new=prepare(self.draft,{pending:'x'*500},'interface-v019',resume_deferred=True)
        validate_review(new['description_review'],new['item_descriptions'],self.rows)
        self.assertEqual(new['description_review']['reviewed'],567)
        self.assertEqual(len(new['description_review']['pending']),213)
    def test_explicit_unique_component_name_guard_and_old_policy_compatibility(self):
        for source,target in [('Part of Drill Claw.','Peça da Garra.'),('G3A3 part.','Peça.'),('C Unit component.','Peça.'),('Memory for Spiked Fender.','Memória.')]:
            with self.assertRaises(ValueError):validate_names(source,target)
        validate_names('Part of Drill Claw.','Parte da Drill|Claw.')
        legacy=self.parent['item_descriptions'];self.assertNotIn('name_reference_policy',legacy)
        patches,report=compile_descriptions(self.elf,legacy);self.assertEqual(report['accepted'],114)
        bad=copy.deepcopy(self.cfg)
        target=next(e for e in bad['entries'] if 'G3A3' in e['translation'])
        # Keep the old digit sequence so the nominal guard, rather than the
        # independent numeric-fact guard, is responsible for rejecting this.
        target['translation']='Peça 3 por 3.'
        with self.assertRaisesRegex(ValueError,'Unique item reference missing'):compile_descriptions(self.elf,bad)
        bad=copy.deepcopy(self.cfg);bad['name_reference_policy']='unknown';bad['entries']=[]
        with self.assertRaisesRegex(ValueError,'Unknown item name policy'):compile_descriptions(self.elf,bad)
    def test_safe_wrapping_never_splits_words_or_changes_text(self):
        target='MAIN: rajadas de dois tiros.';wrapped=wrap_words(target,'Main gun: Fires|two-round bursts.')
        self.assertEqual(wrapped.replace('|',' '),target);self.assertEqual(wrapped.count('|'),1)
        with self.assertRaises(ValueError):wrap_words('palavraexcessivamentecomprida','abc|def')

if __name__=='__main__':unittest.main()
