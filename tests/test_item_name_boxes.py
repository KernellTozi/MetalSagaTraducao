import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import item_name_boxes as boxes
from gfi import encode
from interface_text import SOURCE


class ItemNameBoxesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf = SOURCE.read_bytes()
        cls.result = boxes.investigate(cls.elf)

    def test_exact_caller_geometry_without_claiming_effective_clip(self):
        g = boxes.geometry(self.elf)
        self.assertEqual(g['direct_name_panel']['requested_width'],272)
        self.assertEqual(g['direct_name_panel']['conditional_remaining_width'],234)
        self.assertFalse(g['direct_name_panel']['same_origin_and_effective_clip_proven'])
        self.assertEqual(g['name_price_panel']['conditional_inner_width'],384)
        self.assertFalse(g['name_price_panel']['actual_render_bounds_proven'])

    def test_modified_source_rejected(self):
        bad = bytearray(self.elf)
        bad[0x1b3580] ^= 1
        with self.assertRaises(ValueError): boxes.geometry(bad)

    def test_wrong_register_opcode_rejected(self):
        with self.assertRaises(ValueError):
            boxes.instruction(self.elf,0x1b3580,0x24060110)

    def test_byte_padding_preserves_every_approved_name_roundtrip(self):
        for row in self.result['items']:
            text = row['approved_translation']
            padded = boxes.padded_name(text)
            self.assertEqual(len(padded),20)
            self.assertTrue(padded.startswith(encode(text)))
            self.assertEqual(padded[len(encode(text)):],b' '*(20-len(encode(text))))

    def test_minimum_field_does_not_truncate_long_strings(self):
        text = 'A'*21
        self.assertEqual(boxes.padded_name(text),b'A'*21)

    def test_controls_cannot_be_treated_as_plain_names(self):
        for text in ('Nome|outro','%I0','Nome\n'):
            with self.assertRaises(ValueError): boxes.padded_name(text)

    def test_all_nine_remain_unreleased_and_actions_have_separate_limits(self):
        r = self.result
        self.assertEqual([int(x['id'].rsplit('.',1)[1]) for x in r['items']],list(boxes.IDS))
        self.assertEqual(r['counts'],{'remaining_names':9,'conditional_direct_advance_fits':9,
                                     'name_price_byte_field_fits':9,'action_ceiling_exceeded_names':2})
        self.assertEqual([x['id'] for x in r['items'] if x['action_ceiling_exceeded']],
                         ['item.name.0836','item.name.0840'])
        self.assertTrue(all(not x['editing_authorized'] for x in r['items']))
        self.assertFalse(r['editing_authorized'])
        self.assertFalse(r['iso_created'])

    def test_output_cannot_replace_versioned_reports_or_source_files(self):
        with self.assertRaises(ValueError): boxes.run(boxes.ROOT/'reports/forbidden.json')
        with self.assertRaises(ValueError): boxes.run(SOURCE)


if __name__ == '__main__': unittest.main()
