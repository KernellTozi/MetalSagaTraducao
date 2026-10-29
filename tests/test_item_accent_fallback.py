import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
import item_accent_fallback as f
import item_names as n
from interface_text import SOURCE
from gfi import encode


class ItemAccentFallback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf = SOURCE.read_bytes()
        cls.parent = json.loads((ROOT/f.PARENT).read_bytes())
        cls.child = json.loads((ROOT/'translations/interface-v052.json').read_bytes())
        cls.raw = n.original(n.RESOURCE)
        cls.rows = n.catalog(cls.raw)
        cls.old, cls.old_report = n.compile_names(cls.elf, cls.parent['item_names'])
        cls.new, cls.new_report = n.compile_names(cls.elf, cls.child['item_names'])

    def test_exact_parent_and_one_authorized_name(self):
        self.assertEqual(f.validate_interface(self.child), self.parent)
        self.assertEqual(f.parent_names(self.child['item_names']), self.parent['item_names'])
        old = {e['id']: e for e in self.parent['item_names']['entries']}
        new = {e['id']: e for e in self.child['item_names']['entries']}
        self.assertEqual([k for k in old if old[k] != new[k]], ['item.name.0460'])
        self.assertEqual(new['item.name.0460']['translation'], 'Idolo de barro')
        self.assertEqual(len(encode(f.TARGET)), 14)
        self.assertEqual(self.new_report['accepted'], 541)

    def test_only_one_patch_changes_and_preserves_entire_prefix_extent(self):
        a = {p['id']: p for p in self.old}; b = {p['id']: p for p in self.new}
        self.assertEqual(set(a), set(b))
        self.assertEqual([k for k in a if a[k] != b[k]], ['item.name.0460'])
        x, y = a['item.name.0460'], b['item.name.0460']
        self.assertEqual(x['before'], y['before'])
        self.assertEqual(len(y['after']), 16)
        self.assertEqual(y['after'], b'Idolo de barro\0\0')
        self.assertEqual(x['offset'], y['offset'])

    def test_source_table_attributes_and_adjacent_names_roundtrip(self):
        for patches in (self.old, self.new):
            out = bytearray(self.raw)
            for p in patches:
                self.assertEqual(bytes(out[p['offset']:p['offset']+len(p['before'])]), p['before'])
                out[p['offset']:p['offset']+len(p['after'])] = p['after']
            for row in self.rows:
                at = row['offset']
                self.assertEqual(out[at+24:at+n.STRIDE], self.raw[at+24:at+n.STRIDE])
            for p in patches:
                out[p['offset']:p['offset']+len(p['before'])] = p['before']
            self.assertEqual(bytes(out), self.raw)

    def test_other_name_or_accent_omission_cannot_use_exception(self):
        for index, text in ((0, 'Alterado'), (460, 'Idolo'), (460, 'Ídolo de barro')):
            config = copy.deepcopy(self.child['item_names'])
            target = config['entries'][index] if index == 0 else next(e for e in config['entries'] if e['id'] == 'item.name.0460')
            target['translation'] = text
            with self.assertRaises(ValueError):
                n.compile_names(self.elf, config)

    def test_other_interface_or_layout_changes_refused(self):
        for field, value in (('layout_profile', 'spacing-v003'), ('iso_name', 'wrong.iso'), ('status', 'alterado')):
            recipe = copy.deepcopy(self.child); recipe[field] = value
            with self.assertRaises(ValueError):
                f.validate_interface(recipe)

    def test_binding_source_and_parent_revision_refused(self):
        b = copy.deepcopy(self.child['item_accent_fallback']); b['sha256'] = '0'*64
        with self.assertRaises(ValueError): f.load(b)
        b['recipe'] = '../work/unknown.json'
        with self.assertRaises(ValueError): f.load(b)
        elf = bytearray(self.elf); elf[100] ^= 1
        with self.assertRaises(ValueError): n.compile_names(bytes(elf), self.child['item_names'])

    def test_historical_policy_and_glyph_mapping_stay_strict(self):
        with self.assertRaises(ValueError): encode('Ídolo de barro')
        self.assertNotIn('accent_fallback', self.parent['item_names'])
        self.assertEqual(self.old_report['maximum_target_bytes'], self.new_report['maximum_target_bytes'])
        from item_name_user_review import validate_config
        self.assertEqual(validate_config(self.child['item_names'], self.rows),
                         validate_config(self.parent['item_names'], self.rows))

    def test_current_capacity_ledger_excludes_only_compiled_authorized_fallback(self):
        from item_name_capacity import apply_authorized_fallback
        historical = json.loads((ROOT/'reports/capacidade-nomes-v001.json').read_bytes())
        current = apply_authorized_fallback(historical, ROOT/'translations/interface-v052.json')
        self.assertEqual(current['counts']['blocked'], 15)
        self.assertEqual(current['counts']['codec_supported'], 15)
        self.assertEqual([r['id'] for r in current['items']],
                         [r['id'] for r in historical['items'] if r['id'] != 'item.name.0460'])
        self.assertEqual(len(historical['items']), 16)
        self.assertEqual(current['resolved_authorized_fallbacks'][0]['translation'], 'Idolo de barro')


if __name__ == '__main__':
    unittest.main()
