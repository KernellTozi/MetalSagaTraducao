import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import card_terms_review as review


class CardTermsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from interface_text import compile_draft
        cls.parent=json.loads((review.ROOT/review.PARENT).read_bytes())
        cls.child=json.loads((review.ROOT/review.CHILD).read_bytes())
        cls.elf=review.base.ELF.read_bytes()
        cls.parents,cls.report=compile_draft(cls.elf,cls.parent)
        cls.patches,cls.evidence=review.derive(cls.elf,cls.parents)
        cls.manifest=review.binding_load(cls.child['card_terms_review'])

    def test_reproducible_outputs(self):
        self.assertEqual(self.manifest['revised'],[review.base.metadata(p) for p in self.patches])
        self.assertEqual(self.manifest['evidence'],self.evidence)

    def test_exact_parent_and_unrelated_changes_rejected(self):
        self.assertEqual(review.validate(self.child)[0],self.parent)
        changed=copy.deepcopy(self.child)
        changed['entries'][0]['translation']='Outro'
        with self.assertRaises(ValueError):review.validate(changed)
        binding=copy.deepcopy(self.child['card_terms_review']);binding['sha256']='0'*64
        with self.assertRaises(ValueError):review.binding_load(binding)

    def test_every_patch_revises_existing_exact_interval(self):
        self.assertEqual(len({p['id'] for p in self.patches}),len(self.patches))
        for patch in self.patches:
            parent=next(p for p in self.parents if p['id']==patch['id'])
            for field in ('id','resource','offset','before'):
                self.assertEqual(parent[field],patch[field])
            self.assertEqual(len(parent['after']),len(patch['after']))
            self.assertNotEqual(parent['after'],patch['after'])

    def test_brazilian_terms_and_common_portuguese_names(self):
        revised=json.dumps([b for a,b in review.revised_specs()],ensure_ascii=False)
        for old in review.TERMS:
            self.assertNotIn(old,revised)
        for term in ('ROYAL FLUSH','STRAIGHT FLUSH','FULL HOUSE','FLUSH',
                     'QUADRA','TRINCA','SEQUÊNCIA','DOIS PARES','QUINA'):
            self.assertIn(term,revised)
        for term in ('blackjack','BLACKJACK PAGA 3:2','Poker'):
            self.assertIn(term,revised)

    def test_explanations_and_controller_icons_preserved(self):
        for old,new in review.revised_specs():
            self.assertEqual(old['resource'],new['resource'])
            self.assertEqual(old['offset'],new['offset'])
            if 'panel' in old:
                for a,b in zip(old['panel']['parts'],new['panel']['parts']):
                    if a['kind']=='copy':self.assertEqual(a,b)
                    else:
                        expected=a.get('text','')
                        for source,target in review.TERMS.items():expected=expected.replace(source,target)
                        self.assertEqual(b.get('text',''),expected)

    def test_literal_names_fit_original_cells(self):
        for at,text in review.LITERALS.items():
            patch=next(p for p in self.patches if p['offset']==at and p['resource']=='SLUS_212.93')
            self.assertEqual(patch['after'].split(b'\0',1)[0],review.encode(text))
            self.assertEqual(patch['after'][-1],0)

    def test_noncard_textures_not_released(self):
        allowed={0xc18800,0xc59000,0xc99800,0xdb4800,0xdd5000,0xd6b800,0xe16000}
        self.assertEqual({b['offset'] for a,b in review.revised_specs()},allowed)
        self.assertTrue(all(b['resource']=='DATA/NDATA/NDATA.SDA' for a,b in review.revised_specs()))

    def test_compiler_keeps_all_other_patches_and_unit_count(self):
        from unittest.mock import patch
        with patch('interface_text.compile_draft',return_value=(self.parents,self.report)):
            result,report=review.compile_interface(self.elf,self.child)
        self.assertEqual(len(result),len(self.parents))
        self.assertEqual(report['accepted'],self.report['accepted'])
        revised={p['id'] for p in self.patches}
        for before,after in zip(self.parents,result):
            if before['id'] not in revised:self.assertEqual(before,after)


if __name__=='__main__':unittest.main()
