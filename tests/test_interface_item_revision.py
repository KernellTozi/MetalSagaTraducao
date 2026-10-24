"""Deferred-only revision: preserve all prior translations and rejected evidence."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from item_descriptions import catalog,original,RESOURCE,POOL,SIZE,compile_descriptions,encode,sha
from prepare_item_batch import prepare,validate_review,diagnose_budget

class DeferredItemRevision(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent=json.loads((ROOT/'translations/interface-v018.json').read_text(encoding='utf-8'))
        cls.draft=json.loads((ROOT/'translations/interface-v019.json').read_text(encoding='utf-8'))
        cls.raw=original(RESOURCE);cls.elf=original('SLUS_212.93');cls.rows=catalog(cls.raw)
        cls.old={r['id']:r for r in cls.parent['item_descriptions']['entries']}
        cls.targets={r['id']:r for r in cls.draft['item_descriptions']['entries']}
        cls.added={k:r for k,r in cls.targets.items() if k not in cls.old}

    def test_only_explicit_deferred_ids_resumed(self):
        pending={r['id'] for r in self.parent['description_review']['pending']}
        self.assertEqual(len(self.added),142)
        self.assertLessEqual(set(self.added),pending)
        self.assertEqual(len(self.targets),495)
        for key,row in self.old.items():self.assertEqual(self.targets[key],row,key)
        for key in self.parent:
            if key not in ('status','iso_name','item_descriptions','description_review'):
                self.assertEqual(self.parent[key],self.draft[key],key)

    def test_remaining_pending_and_preserved_evidence_unchanged(self):
        review=self.draft['description_review'];validate_review(review,self.draft['item_descriptions'],self.rows)
        expected=[r for r in self.parent['description_review']['pending'] if r['id'] not in self.added]
        self.assertEqual(review['pending'],expected);self.assertEqual(len(expected),71)
        self.assertEqual(review['preserved'],self.parent['description_review']['preserved'])
        self.assertEqual((review['reviewed'],review['not_reviewed']),(567,0))
        self.assertIn('item.description.03226',{r['id'] for r in expected})

    def test_recipe_reproducible_from_versioned_targets(self):
        proposals={k:r['translation'] for k,r in self.added.items()}
        self.assertEqual(prepare(self.parent,proposals,'interface-v019',resume_deferred=True),self.draft)
        with self.assertRaises(ValueError):prepare(self.parent,proposals,'interface-v019')

    def test_all_payloads_roundtrip_and_untargeted_bytes_unchanged(self):
        patches,report=compile_descriptions(self.elf,self.draft['item_descriptions'])
        self.assertEqual(report['accepted'],495)
        output=bytearray(self.raw)
        for p in patches:
            at=p['offset'];self.assertEqual(output[at:at+len(p['before'])],p['before'])
            self.assertEqual(len(p['before']),len(p['after']))
            output[at:at+len(p['after'])]=p['after']
        for row in self.rows:
            at=row['offset'];end=output.index(0,at)
            expected=encode(self.targets[row['id']]['translation']) if row['id'] in self.targets else bytes.fromhex(row['source_hex'])
            self.assertEqual(bytes(output[at:end]),expected,row['id'])
        self.assertEqual(output[:POOL],self.raw[:POOL]);self.assertEqual(output[POOL+SIZE:],self.raw[POOL+SIZE:])
        for p in reversed(patches):output[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(output,self.raw)

    def test_budget_reports_real_two_byte_accents_and_multiple_failures(self):
        report=diagnose_budget(b'12345','ááá')
        self.assertEqual((report['target_bytes'],report['byte_excess']),(6,1))
        self.assertIn('byte-budget',report['issues']);self.assertFalse(report['edit_authorized'])
        report=diagnose_budget(b'ab|cd','palavra longa')
        self.assertIn('word-wrap',report['issues']);self.assertIn('byte-budget',report['issues'])
        self.assertIn('columns',report['issues'])

    def test_budget_does_not_authorize_controls_native_or_missing_glyph(self):
        self.assertIn('native-source',diagnose_budget(bytes.fromhex('826e'),'Texto')['issues'])
        self.assertIn('source-control',diagnose_budget(b'80%%','80%%')['issues'])
        self.assertIn('target-control',diagnose_budget(b'Text','a\nb')['issues'])
        self.assertIn('unsupported-glyph',diagnose_budget(b'Text','Ó')['issues'])
        fit=diagnose_budget(b'Long enough.','Cabe.')
        self.assertEqual(fit['issues'],[]);self.assertFalse(fit['edit_authorized'])

if __name__=='__main__':unittest.main()
