import copy
import json
import mmap
import sys
import unittest
from unittest import mock
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_translation_pilot import compile_draft,DRAFT,DEFAULT_DRAFT,REGION_V2_DRAFT,REGION_V3_DRAFT,REGION_V4_DRAFT,REGION_V5_DRAFT,load_draft
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

    def test_expanded_scene_preserves_deferred_records_and_labels(self):
        draft,sources=load_draft(REGION_V2_DRAFT)
        document,patches,report=compile_draft(self.data,draft)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(85,13,0))
        self.assertEqual(len(sources),2)
        self.assertEqual(len(report['deferred']),6)
        changed={p['id'] for p in patches}
        self.assertFalse(changed&set(draft['deferred']))
        for entry in document['entries']:
            for segment in entry['segments']:
                if not segment['editable']:self.assertEqual(segment['source'],segment['translation'])
        first=document['entries'][0]['segments'][0]
        self.assertEqual(first['translation'],'Voc\u00ea quer mesmo ser um\nHunter?')

    def test_alias_requires_same_source(self):
        draft,_=load_draft(REGION_V2_DRAFT)
        draft['aliases']['map.msg.1df4a394']='map.msg.1df47f0c'
        with self.assertRaises(ValueError):compile_draft(self.data,draft)

    def test_protected_name_change_blocks_entire_batch(self):
        draft,_=load_draft(REGION_V2_DRAFT)
        draft['translations']['map.msg.1df4a0a8']=draft['translations']['map.msg.1df4a0a8'].replace('McKinley','Outro')
        _,patches,report=compile_draft(self.data,draft)
        self.assertFalse(report['valid']);self.assertEqual(patches,[])
        self.assertTrue(report['terminology_issues'])

    def test_v003_preserves_entire_previous_lot_and_city_name(self):
        previous,_=load_draft(REGION_V2_DRAFT)
        old,_,_=compile_draft(self.data,previous)
        current,sources=load_draft(REGION_V3_DRAFT)
        document,patches,report=compile_draft(self.data,current)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(165,28,0))
        self.assertEqual(len(sources),3)
        self.assertEqual(document['entries'][:98],old['entries'])
        self.assertEqual(len(report['deferred']),7)
        self.assertFalse({p['id'] for p in patches}&set(current['deferred']))
        city=next(e for e in document['entries'] if e['id']=='map.MC.1df4e5e4')
        self.assertEqual(city['segments'][0]['translation'],'Junkyard')

    def test_wanted_name_change_blocks_v003(self):
        draft,_=load_draft(REGION_V3_DRAFT)
        draft['translations']['map.msg.1df549fc']='...Outro sujeito,\ncerto?'
        _,patches,report=compile_draft(self.data,draft)
        self.assertFalse(report['valid']);self.assertEqual(patches,[])
        self.assertTrue(any('Derringer Jack' in issue['reason'] for issue in report['terminology_issues']))

    def test_v004_preserves_v003_and_item_control_deferrals(self):
        previous,_=load_draft(REGION_V3_DRAFT)
        old,_,_=compile_draft(self.data,previous)
        draft,sources=load_draft(REGION_V4_DRAFT)
        document,patches,report=compile_draft(self.data,draft)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(288,38,0))
        self.assertEqual(len(sources),4)
        self.assertEqual(document['entries'][:193],old['entries'])
        self.assertEqual(len(report['deferred']),10)
        self.assertFalse({p['id'] for p in patches}&set(draft['deferred']))
        doctor=next(e for e in document['entries'] if e['id']=='map.msgn.1df59f34')
        self.assertIn('Dr. Martin',doctor['segments'][0]['translation'])
        city=next(e for e in document['entries'] if e['id']=='map.supr.1df5935c')
        self.assertEqual(city['segments'][0]['translation'],'- Junkyard -')

    def test_v005_preserves_all_previous_records_and_exact_reuse(self):
        from prepare_translation_lot import prepare
        parent,_=load_draft(REGION_V4_DRAFT)
        old,_,_=compile_draft(self.data,parent)
        proposal,pending=prepare(self.data,parent,0x1df630b8)
        self.assertEqual((len(pending),len(proposal['aliases'])),(30,29))
        incomplete=copy.deepcopy(parent)
        incomplete['scope']=proposal['scope']
        for field in ('translations','aliases','deferred'):
            incomplete.setdefault(field,{}).update(proposal[field])
        with self.assertRaisesRegex(ValueError,'Empty or invalid'):
            compile_draft(self.data,incomplete)
        draft,sources=load_draft(REGION_V5_DRAFT)
        current,patches,report=compile_draft(self.data,draft)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(343,42,0))
        self.assertEqual(current['entries'][:326],old['entries'])
        self.assertEqual(len(sources),5)
        self.assertEqual(len(current['entries']),385)
        self.assertEqual(len(report['deferred']),10)
        with self.assertRaises(ValueError):prepare(self.data,parent,0x1df5ff98)

    def test_v006_preserves_v005_and_defers_opaque_item_name(self):
        parent,_=load_draft(REGION_V5_DRAFT)
        old,_,_=compile_draft(self.data,parent)
        draft,sources=load_draft(DEFAULT_DRAFT)
        current,patches,report=compile_draft(self.data,draft)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(384,60,0))
        self.assertEqual(current['entries'][:385],old['entries'])
        self.assertEqual(len(current['entries']),444)
        self.assertEqual(len(report['deferred']),11)
        self.assertIn('map.msg.1df6435c',draft['deferred'])
        self.assertNotIn('map.msg.1df6435c',{p['id'] for p in patches})
        self.assertEqual(len(sources),6)

    def test_duplicate_authored_keys_are_not_silently_overwritten(self):
        raw=b'{"schema":1,"translations":{"same.id":"first","same.id":"second"}}'
        with mock.patch.object(Path,'read_bytes',return_value=raw):
            with self.assertRaisesRegex(ValueError,'Duplicate authored JSON key'):
                load_draft(DEFAULT_DRAFT)


if __name__=='__main__':unittest.main()
