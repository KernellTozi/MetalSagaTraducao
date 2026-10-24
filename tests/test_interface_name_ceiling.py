import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from item_names import *

class ObservedNameCeiling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/'translations/interface-v020.json').read_text(encoding='utf-8'))
        cls.new=json.loads((ROOT/'translations/interface-v021.json').read_text(encoding='utf-8'))
        cls.raw=original(RESOURCE);cls.elf=original('SLUS_212.93');cls.rows=catalog(cls.raw)
        cls.patches,cls.report=compile_names(cls.elf,cls.new['item_names'])
    def test_exact_observed_bound_and_all_generic_forwarding_indices(self):
        evidence=ceiling_binding(self.elf,self.raw)
        self.assertEqual(evidence['maximum_original_name_bytes'],16)
        self.assertEqual(evidence['witness_item_ids'],[954]);self.assertTrue(evidence['zero_name_tails'])
        for index in range(ITEM_COUNT):self.assertEqual(execute_name_forwarding(self.elf,index),(index*128,0x630000))
    def test_historic_profile_stays_fixed_and_new_growth_is_scoped(self):
        row=self.rows[381]
        with self.assertRaises(ValueError):validate_value(row,'Arroz')
        self.assertEqual(validate_value(row,'Arroz',ceiling=16),b'Arroz')
        for text in ('x'*17,'x'*24):
            with self.assertRaises(ValueError):validate_value(row,text,ceiling=16)
        with self.assertRaises(ValueError):validate_value(row,'Arroz',ceiling=23)
        old,report=compile_names(self.elf,self.old['item_names']);self.assertFalse(report['per_name_growth'])
        self.assertEqual(report['accepted'],189)
    def test_growth_modifies_only_proven_name_zero_tails(self):
        output=bytearray(self.raw);grown=0
        for p in self.patches:
            at=p['offset'];index=(at-ITEM_BASE)//STRIDE;source=self.rows[index]
            self.assertLessEqual(len(p['after']),17);self.assertEqual(len(p['before']),len(p['after']))
            self.assertEqual(p['before'][source['source_bytes']:],bytes(len(p['before'])-source['source_bytes']))
            grown+=len(p['after'])>source['source_bytes']+1
            output[at:at+len(p['after'])]=p['after']
        self.assertEqual(grown,264)
        for result in self.report['results']:
            self.assertEqual(result['source_bytes'],self.rows[result['item_id']]['source_bytes'])
        targets={r['id']:r['translation'] for r in self.new['item_names']['entries']}
        for row in self.rows:
            at=row['offset'];self.assertEqual(output[at+17:at+128],self.raw[at+17:at+128])
            name=bytes(output[at:at+24]).split(b'\0')[0]
            self.assertEqual(name,encode(targets[row['id']]) if row['id'] in targets else bytes.fromhex(row['source_hex']))
            self.assertLessEqual(len(name),16)
        for p in reversed(self.patches):output[p['offset']:p['offset']+len(p['before'])]=p['before']
        self.assertEqual(output,self.raw)
    def test_evidence_and_policy_cannot_silently_open_tail_bytes(self):
        for mutation in ('missing','ceiling','witness','window','legacy'):
            cfg=copy.deepcopy(self.new['item_names'])
            if mutation=='missing':del cfg['ceiling_evidence']
            elif mutation=='ceiling':cfg['ceiling_evidence']['maximum_original_name_bytes']=23
            elif mutation=='witness':cfg['ceiling_evidence']['witness_item_ids']=[]
            elif mutation=='window':cfg['ceiling_evidence']['instruction_windows'][0]['sha256']='bad'
            else:cfg['policy']=POLICY
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):compile_names(self.elf,cfg)
    def test_nonzero_tail_rejected_even_with_matching_source_hashes(self):
        raw=bytearray(self.raw);raw[ITEM_BASE+381*STRIDE+20]=1;raw=bytes(raw)
        cfg=copy.deepcopy(self.new['item_names']);cfg['source_sha256']=sha(raw)
        cfg['table_sha256']=sha(raw[ITEM_BASE:ITEM_BASE+ITEM_COUNT*STRIDE]);cfg['ceiling_evidence']=ceiling_binding(self.elf,raw)
        with patch('item_names.original',return_value=raw),self.assertRaisesRegex(ValueError,'ceiling evidence'):
            compile_names(self.elf,cfg)
    def test_all_old_targets_and_deferred_evidence_preserved(self):
        old={e['id']:e for e in self.old['item_names']['entries']};new={e['id']:e for e in self.new['item_names']['entries']}
        self.assertEqual(len(new)-len(old),268);self.assertEqual(len(new),457)
        for key,row in old.items():self.assertEqual(new[key],row)
        pending={e['id']:e for e in self.new['item_name_review']['pending']}
        for e in self.old['item_name_review']['pending']:
            if e['id'] not in new:self.assertEqual(pending[e['id']],e)
        validate_review(self.new['item_name_review'],self.new['item_names'],self.rows)
    def test_protected_names_and_shared_occurrences_stay_locked(self):
        for index in (48,55,300,489,659,715,725,801,990,1046):
            with self.subTest(index=index),self.assertRaises(ValueError):validate_value(self.rows[index],'Teste',ceiling=16)
        targets={e['id']:e['translation'] for e in self.new['item_names']['entries']}
        self.assertEqual(targets['item.name.0335'],targets['item.name.1000'])
        self.assertEqual(targets['item.name.0377'],targets['item.name.1042'])

if __name__=='__main__':unittest.main()
