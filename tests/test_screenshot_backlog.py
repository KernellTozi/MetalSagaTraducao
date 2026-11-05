import copy
import json
import mmap
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import screenshot_backlog as release


class ScreenshotBacklogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf = release.ELF.read_bytes()
        cls.patches, cls.evidence = release.derive(cls.elf)
        cls.recipe = json.loads((release.ROOT / release.CHILD).read_bytes())
        cls.manifest = release.binding_load(cls.recipe['screenshot_backlog_release'])

    def test_bound_outputs_are_reproducible(self):
        self.assertEqual(self.manifest['new'], [release.metadata(p) for p in self.patches])
        self.assertEqual(self.manifest['evidence'], self.evidence)
        self.assertEqual(len(self.patches), 14)

    def test_parent_and_unrelated_recipe_changes_are_rejected(self):
        parent = json.loads((release.ROOT / release.PARENT).read_bytes())
        self.assertEqual(release.validate(self.recipe)[0], parent)
        changed = copy.deepcopy(self.recipe)
        changed['entries'][0]['translation'] = 'Alteração alheia'
        with self.assertRaises(ValueError):
            release.validate(changed)
        changed = copy.deepcopy(self.recipe['screenshot_backlog_release'])
        changed['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            release.binding_load(changed)

    def test_diary_keeps_native_ellipsis_and_page_separators(self):
        body = next(p for p in self.patches if p['id'] == 'diary.031.body')
        self.assertEqual(body['after'].count(release.ELLIPSIS), 1)
        self.assertEqual(body['before'].count(b'|'), body['after'].count(b'|'))
        self.assertEqual(len(body['before']), 80)
        self.assertEqual(len(body['after']), 80)
        self.assertEqual(body['after'][-1], 0)
        self.assertIn(release.encode('Dr. Mortem'), body['after'])
        self.assertIn(release.encode('Professor Grey'), body['after'])

    def test_diary_edits_are_reversible_and_record_headers_intact(self):
        from diary import fields
        original = release.original(release.DIARY)
        data = bytearray(original)
        for p in self.patches:
            if p['resource'] == release.DIARY:
                at = p['offset']
                self.assertEqual(data[at:at+len(p['before'])], p['before'])
                data[at:at+len(p['after'])] = p['after']
        self.assertEqual([(r['offset'],r['capacity']) for r in fields(original)],
                         [(r['offset'],r['capacity']) for r in fields(data)])
        for p in self.patches:
            if p['resource'] == release.DIARY:
                data[p['offset']:p['offset']+len(p['before'])] = p['before']
        self.assertEqual(data, original)

    def test_dance_icons_order_and_adjacent_literal_intact(self):
        p = next(p for p in self.patches if p['id'] == 'reported.elf.00338b18')
        self.assertEqual(re.findall(rb'\$\x81.', p['before']), re.findall(rb'\$\x81.', p['after']))
        self.assertTrue(p['after'].startswith(release.encode('Dançar:')))
        self.assertEqual(len(p['after']),32)
        self.assertEqual(self.elf[p['offset']+32:p['offset']+37],b'Pose:')

    def test_literal_overflow_and_interior_alias_are_rejected(self):
        at = 0x31b858
        source = b'Land Battleship Tiamat'
        refs = {at+0xff000: [1]}
        with self.assertRaises(ValueError):
            release.literal(self.elf,refs,at,source,'A'*40)
        refs[at+0xff001] = [1]
        with self.assertRaises(ValueError):
            release.literal(self.elf,refs,at,source,'Encouraçado Tiamat')

    def test_all_six_scene_labels_keep_32_byte_limit(self):
        patches = [p for p in self.patches if p['resource'] == release.MCT]
        self.assertEqual(len(patches),6)
        self.assertEqual(sorted(r['map'] for r in self.evidence['locations']),[11,143,143,153,153,153])
        for p in patches:
            self.assertLessEqual(len(p['after']),32)
            self.assertEqual(len(p['before']),len(p['after']))
            self.assertEqual(p['after'][-1],0)
        self.assertEqual(len(release.encode(release.LOCATIONS['First Continental RR Tunnel'])),31)

    def test_raster_changes_stay_inside_bound_word_rectangles(self):
        for evidence, kind in zip(self.evidence['graphics'], ('tank','dance')):
            p = next(p for p in self.patches if p['id'] == 'reported.raster.'+kind)
            width = evidence['texture']['width']
            x,y,right,bottom = evidence['rect']
            differences = [i for i,(a,b) in enumerate(zip(p['before'],p['after'])) if a != b]
            self.assertTrue(differences)
            self.assertTrue(all(x <= i%width < right and y <= i//width < bottom for i in differences))
            self.assertEqual(len(p['before']),len(p['after']))

    def test_hamir_controls_labels_and_capacity(self):
        from dialogue_formats import parse_msgn
        with release.MAP.open('rb') as stream, mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
            for key, target in release.HAMIR.items():
                p,_ = parse_msgn(data,int(key.rsplit('.',1)[1],16))
                self.assertEqual(p['display_label']['source'],'MC Hamir')
                self.assertLessEqual(len(release.encode(target)),p['capacity'])
                self.assertEqual(re.findall(r'%[FM][\d_]+',p['source']),re.findall(r'%[FM][\d_]+',target))
                self.assertEqual(re.findall('[\t\n]',p['source']),re.findall('[\t\n]',target))

    def test_narrative_only_two_reviewed_dialogues(self):
        from build_translation_pilot import load_draft
        child,_ = load_draft(release.ROOT / release.CHILD_MAP)
        release.validate_narrative(child)
        changed = copy.deepcopy(child)
        changed['translations']['map.msgn.1774327c'] = 'Outra fala'
        with self.assertRaises(ValueError):
            release.validate_narrative(changed)


if __name__ == '__main__':
    unittest.main()
