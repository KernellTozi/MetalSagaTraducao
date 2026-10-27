import collections,json,re,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import export_item_name_audit as a


class ItemNameAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recipe=json.loads((ROOT/'translations/interface-v040.json').read_text(encoding='utf-8'))
        cls.raw=a.original(a.RESOURCE);cls.elf=a.SOURCE.read_bytes()
        cls.rows,cls.fields,cls.engine_meta,cls.variants=a.catalogue(cls.elf,cls.raw,cls.recipe)
        cls.summary=json.loads((ROOT/'reports/auditoria-itens-v040.json').read_text(encoding='utf-8'))

    def test_all_1349_ids_once_and_counts_close(self):
        self.assertEqual(len(self.rows),1349)
        self.assertEqual([r['index'] for r in self.rows],list(range(1349)))
        self.assertEqual(dict(collections.Counter(r['status'] for r in self.rows)),self.summary['counts'])
        self.assertEqual(sum(bool(r['original']) for r in self.rows),1041)

    def test_every_applied_name_matches_recipe_and_name_field(self):
        expected={r['id']:r['translation'] for r in self.recipe['item_names']['entries']}
        actual={r['id']:r['applied_translation'] for r in self.rows if r['status']=='translated'}
        self.assertEqual(actual,expected);self.assertEqual(len(actual),516)
        for r in self.rows:
            value=bytes.fromhex(r['current_name_field_hex']).split(b'\0',1)[0]
            self.assertEqual(value,a.encode(r['current_name']));self.assertEqual(len(value),r['current_bytes'])

    def test_pending_proposals_never_reported_as_applied(self):
        rows=[r for r in self.rows if r['status']=='pending'];self.assertEqual(len(rows),25)
        for row in rows:
            self.assertIsNone(row['applied_translation']);self.assertEqual(row['current_name'],row['original'])
            self.assertIsNotNone(row['existing_proposal']);self.assertIsNone(row['review_translation'])
        self.assertEqual(sum(r['proposal_budget']['bytes'] is None for r in rows),1)

    def test_all_preserved_and_empty_names_stay_exact(self):
        for row in self.rows:
            if row['status'] not in ('preserved','empty'):continue
            self.assertEqual(row['current_name'],row['original']);self.assertIsNone(row['applied_translation'])
            self.assertEqual(bytes.fromhex(row['current_name_field_hex']),self.raw[row['offset']:row['offset']+24])

    def test_engine_variant_appendix_complete_without_inflating_item_count(self):
        self.assertEqual(len(self.variants),50)
        self.assertEqual(sum(bool(r['original']) for r in self.variants),26)
        self.assertEqual({r['item_id'] for r in self.variants},set(range(299,309)))
        self.assertEqual(len({r['id'] for r in self.variants}),50)
        for row in self.variants:self.assertEqual(row['current_name'],row['original'])

    def test_markdown_contains_every_main_id_and_no_duplicate_merging(self):
        text=a.markdown(self.rows,self.variants,self.summary)
        ids=[int(x) for x in re.findall(r'^\| (\d+) \|',text,re.M)]
        self.assertEqual(len(ids),1349);self.assertEqual(set(ids),set(range(1349)))
        self.assertIn('| 118 | Bunny Ears |',text);self.assertIn('| 425 | Rabbit Ears |',text)
        self.assertIn('Tradução aplicada',text);self.assertIn('Proposta anterior — não aplicada',text)

    def test_project_byte_budget_and_safe_markdown_cells(self):
        self.assertEqual(a.budget('Peça')['bytes'],5)
        self.assertEqual(a.budget('Orelhas de coelho')['bytes'],17)
        self.assertFalse(a.budget('Orelhas de coelho')['within_16'])
        self.assertEqual(a.budget('Óculos')['missing_glyphs'],['Ó'])
        self.assertEqual(a.cell('a|b\nc'),'a\\|b / c')

    def test_iso_name_field_mismatch_is_rejected_without_touching_real_iso(self):
        row=next(r for r in self.rows if r['status']=='translated')
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-item-audit-') as tmp:
            path=Path(tmp)/'fixture.iso';blob=bytearray(self.raw)
            blob[row['offset']:row['offset']+24]=bytes.fromhex(row['current_name_field_hex']);path.write_bytes(blob)
            with patch('verify_test_iso.verify_image',return_value={'verified':True}),patch('disc.entries',return_value=[{'path':a.RESOURCE,'lba':0,'size':len(blob)}]):
                self.assertEqual(a.verify_iso_fields(path,[row],[])['main_name_fields_compared'],1)
                blob[row['offset']]^=1;path.write_bytes(blob)
                with self.assertRaisesRegex(ValueError,'differs from playable ISO'):a.verify_iso_fields(path,[row],[])


if __name__=='__main__':unittest.main()
