import copy
import json
import mmap
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_translation_pilot import compile_draft,DRAFT
from reinsertion import SOURCE


class PilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stream=SOURCE.open('rb')
        cls.data=mmap.mmap(cls.stream.fileno(),0,access=mmap.ACCESS_READ)
        cls.draft=json.loads(DRAFT.read_text(encoding='utf-8'))

    @classmethod
    def tearDownClass(cls):
        cls.data.close();cls.stream.close()

    def test_complete_scene_and_unchanged_pauses(self):
        document,patches,report=compile_draft(self.data,self.draft)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(23,3,0))
        self.assertEqual(len(document['entries']),26)
        self.assertEqual(len(patches),23)
        self.assertTrue(all(len(p['before'])==len(p['after']) for p in patches))
        self.assertTrue(all(r.get('source_offsets')==r.get('target_offsets') for r in report['results']))

    def test_missing_record_refused(self):
        draft=copy.deepcopy(self.draft)
        draft['translations'].pop(next(iter(draft['translations'])))
        with self.assertRaises(ValueError):compile_draft(self.data,draft)

    def test_changed_control_prevents_entire_batch(self):
        draft=copy.deepcopy(self.draft)
        key='map.msg.1df47f9c'
        draft['translations'][key]=draft['translations'][key].replace('%M0_5','%M0_6')
        _,patches,report=compile_draft(self.data,draft)
        self.assertFalse(report['valid'])
        self.assertEqual(patches,[])

    def test_overflow_prevents_entire_batch(self):
        draft=copy.deepcopy(self.draft)
        draft['translations']['map.msg.1df47f0c']='X'*60+'\nHunter?'
        _,patches,report=compile_draft(self.data,draft)
        self.assertFalse(report['valid'])
        self.assertEqual(patches,[])


if __name__=='__main__':unittest.main()
