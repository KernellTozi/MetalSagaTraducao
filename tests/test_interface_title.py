import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from interface_graphics import compile_graphics, original
from title_graphics import compile_title, evidence
from title_native_font import RESOURCE, LABELS, alphabet, line
from interface_texture_pack import pillow


class TitleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((ROOT/'translations/interface-graphics-v006.json').read_text(encoding='utf-8'))
        cls.parent = json.loads((ROOT/'translations/interface-graphics-v005.json').read_text(encoding='utf-8'))

    def test_parent_patch_preservation_and_only_three_title_rectangles(self):
        before, _ = compile_graphics(self.parent)
        after, report = compile_title(self.config)
        self.assertEqual(after[:-1], before)
        self.assertEqual(report['accepted'], 43)
        title = after[-1]
        self.assertEqual(title['resource'], RESOURCE)
        original_resource = original(RESOURCE)
        rebuilt = bytearray(original_resource)
        rebuilt[title['offset']:title['offset']+len(title['after'])] = title['after']
        self.assertEqual(len(rebuilt), len(original_resource))
        changed = [i for i, (a, b) in enumerate(zip(original_resource, rebuilt)) if a != b]
        self.assertTrue(changed)
        for at in changed:
            pixel = at-32-1040
            self.assertTrue(0 <= pixel < 256*72 and pixel % 256 < 180)
        rebuilt[title['offset']:title['offset']+len(title['before'])] = title['before']
        self.assertEqual(rebuilt, original_resource)

    def test_native_glyph_sizes_no_scaling_and_unsupported_overflow(self):
        Image = pillow()
        with patch.object(Image.Image, 'resize', side_effect=AssertionError('No glyph resize')):
            alphabet.cache_clear()
            for text in LABELS:
                glyph = line(text)
                self.assertLessEqual(glyph.width, 176)
                self.assertEqual(glyph.height, 24)
        for text in ('', 'CARREGAR?', 'N'*20):
            with self.assertRaises(ValueError):
                line(text)

    def test_reviewed_recipe_bindings_reject_tampering(self):
        for case in ('parent', 'source', 'label', 'mask', 'geometry', 'order', 'duplicate'):
            config = copy.deepcopy(self.config)
            if case == 'parent': config['parent']['recipe'] = 'translations/interface-graphics-v004.json'
            elif case == 'source': config['source_sha256'] = '0'*64
            elif case == 'label': config['entries'][0]['translation'] = 'NOVO'
            elif case == 'mask': config['entries'][0]['mask_sha256'] = '0'*64
            elif case == 'geometry': config['entries'][0]['rect'][2] += 1
            elif case == 'order': config['entries'].reverse()
            else: config['entries'].append(config['entries'][0])
            with self.subTest(case=case), self.assertRaises(ValueError):
                compile_title(config)

    def test_consumers_and_static_ganm_fields(self):
        elf = original('SLUS_212.93')
        raw = original(RESOURCE)
        proof = evidence(elf, raw)
        self.assertEqual(proof['static_frames'], 6)
        self.assertEqual(proof['animations'], 0)
        self.assertEqual([r[0] for r in proof['object_frames_and_positions']], [5, 0, 1, 2, 4, 3])
        for offset in (66608+6, 66608+8, 66624+8):
            bad = bytearray(raw)
            bad[offset] ^= 1
            with self.assertRaises(ValueError): evidence(elf, bad)
        bad = bytearray(elf)
        bad[0x38650] ^= 1
        with self.assertRaises(ValueError): evidence(bad, raw)

    def test_ui_texts_map_and_layout_preserved(self):
        old = json.loads((ROOT/'translations/interface-v008.json').read_text(encoding='utf-8'))
        new = json.loads((ROOT/'translations/interface-v009.json').read_text(encoding='utf-8'))
        for field in set(old)-{'graphics', 'status', 'iso_name'}:
            self.assertEqual(new[field], old[field], field)
        self.assertEqual(new['layout_profile'], 'ptbr-layout-v005')


if __name__ == '__main__':
    unittest.main()
