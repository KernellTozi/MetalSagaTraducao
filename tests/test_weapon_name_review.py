import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import weapon_name_review as w


class WeaponReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=w.original(w.RESOURCE)
        cls.recipe=json.loads((w.ROOT/w.CURRENT).read_bytes())
        cls.proposals=json.loads((w.ROOT/w.SUGGESTIONS).read_bytes())
        cls.rows=w.collect(cls.raw,cls.recipe,cls.proposals)

    def test_complete_classification_includes_outlier_and_duplicates(self):
        self.assertEqual({k:sum(r['category']==k for r in self.rows) for k in w.GROUPS},w.EXPECTED)
        self.assertEqual(len({r['id'] for r in self.rows}),190)
        self.assertEqual(next(r for r in self.rows if r['index']==1042)['current'],'Rede elétrica')
        self.assertEqual([r['index'] for r in self.rows if r['source']=='Bare Hands'],[19,74])
        self.assertNotIn(190,[r['index'] for r in self.rows])

    def test_model_names_unchanged_and_no_application_authority(self):
        by={r['index']:r for r in self.rows}
        for i in (48,61,84,86,221,256,257,264):
            self.assertEqual(by[i]['suggestion'],by[i]['source'])
        self.assertTrue(all(r['approval'] is None and not r['application_authorized'] for r in self.rows))
        self.assertEqual(sum(r['category']!=15 and r['source']!=r['current'] for r in self.rows),1)

    def test_game_encoded_size_and_overflow_only_flagged(self):
        by={r['index']:r for r in self.rows}
        self.assertEqual(by[1]['suggested_game_bytes'],18)
        self.assertFalse(by[1]['within_legacy_16_byte_guard'])
        self.assertEqual(by[4]['suggested_game_bytes'],6)
        self.assertEqual(by[4]['suggestion'],'Facão')

    def test_missing_duplicate_and_foreign_id_refused(self):
        for mode in ('missing','duplicate','foreign'):
            bad=copy.deepcopy(self.proposals)
            if mode=='missing':bad['entries'].pop()
            elif mode=='duplicate':bad['entries'].append(copy.deepcopy(bad['entries'][0]))
            else:bad['entries'][0]['id']='item.name.0190'
            with self.assertRaises(ValueError):w.collect(self.raw,self.recipe,bad)

    def test_bound_source_and_approval_flag_checked(self):
        for field,value in [('source_sha256','0'*64),('approved_for_application',True)]:
            bad=copy.deepcopy(self.proposals);bad[field]=value
            with self.assertRaises(ValueError):w.collect(self.raw,self.recipe,bad)
        bad=copy.deepcopy(self.proposals);bad['entries'][0]['source_sha256']='0'*64
        with self.assertRaises(ValueError):w.collect(self.raw,self.recipe,bad)

    def test_duplicate_wording_and_caliber_changes_refused(self):
        bad=copy.deepcopy(self.proposals)
        next(r for r in bad['entries'] if r['id']=='item.name.0074')['suggestion']='Outra coisa'
        with self.assertRaisesRegex(ValueError,'Inconsistent'):w.collect(self.raw,self.recipe,bad)
        bad=copy.deepcopy(self.proposals)
        next(r for r in bad['entries'] if r['id']=='item.name.0191')['suggestion']='Canhão 38mm'
        with self.assertRaisesRegex(ValueError,'numbers changed'):w.collect(self.raw,self.recipe,bad)

    def test_capacity_current_overlay_preserves_closed_ledger(self):
        from item_name_capacity import apply_authorized_fallback
        historical=json.loads((w.ROOT/'reports/capacidade-nomes-v001.json').read_bytes())
        ledger=apply_authorized_fallback(historical,w.ROOT/w.CURRENT)
        self.assertEqual(ledger['counts']['blocked'],0)
        self.assertEqual(len(ledger['resolved_remaining_name_revisions']),9)
        self.assertEqual(ledger['effective_recipe'],w.CURRENT)

    def test_repeated_export_preserves_user_edits_before_any_write(self):
        with tempfile.TemporaryDirectory(dir=w.ROOT/'work') as directory:
            output=Path(directory);files={'a.json':'{}\n','b.md':'Original\n'}
            w.write_review_files(output,files);w.write_review_files(output,files)
            (output/'b.md').write_text('Minha revisão\n',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Revisão existente diferente'):
                w.write_review_files(output,{'a.json':'outro','b.md':'Original\n'})
            self.assertEqual((output/'a.json').read_text(encoding='utf-8'),'{}\n')
            self.assertEqual((output/'b.md').read_text(encoding='utf-8'),'Minha revisão\n')


if __name__=='__main__':unittest.main()
