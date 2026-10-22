import copy
import json
import mmap
import sys
import unittest
import tempfile
from unittest import mock
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_translation_pilot import compile_draft,DRAFT,DEFAULT_DRAFT,REGION_V2_DRAFT,REGION_V3_DRAFT,REGION_V4_DRAFT,REGION_V5_DRAFT,REGION_V6_DRAFT,REGION_V7_DRAFT,REGION_V8_DRAFT,REGION_V9_DRAFT,REGION_V10_DRAFT,REGION_V11_DRAFT,REGION_V12_DRAFT,REGION_V13_DRAFT,REGION_V14_DRAFT,REGION_V15_DRAFT,REGION_V16_DRAFT,REGION_V17_DRAFT,load_draft
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
        draft,sources=load_draft(REGION_V6_DRAFT)
        current,patches,report=compile_draft(self.data,draft)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(384,60,0))
        self.assertEqual(current['entries'][:385],old['entries'])
        self.assertEqual(len(current['entries']),444)
        self.assertEqual(len(report['deferred']),11)
        self.assertIn('map.msg.1df6435c',draft['deferred'])
        self.assertNotIn('map.msg.1df6435c',{p['id'] for p in patches})
        self.assertEqual(len(sources),6)

    def test_v007_preserves_v006_and_named_labels(self):
        parent,_=load_draft(REGION_V6_DRAFT)
        old,_,_=compile_draft(self.data,parent)
        draft,sources=load_draft(REGION_V7_DRAFT)
        current,patches,report=compile_draft(self.data,draft)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(442,69,0))
        self.assertEqual(current['entries'][:444],old['entries'])
        self.assertEqual(len(current['entries']),511)
        self.assertEqual(len(report['deferred']),14)
        for entry in current['entries'][444:]:
            for segment in entry['segments']:
                if not segment['editable']:
                    self.assertEqual(segment['translation'],segment['source'])
        self.assertEqual(len(sources),7)

    def test_v008_preserves_v007_and_rank_names(self):
        parent,_=load_draft(REGION_V7_DRAFT)
        old,_,_=compile_draft(self.data,parent)
        draft,sources=load_draft(REGION_V8_DRAFT)
        current,patches,report=compile_draft(self.data,draft)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(503,74,0))
        self.assertEqual(current['entries'][:511],old['entries'])
        self.assertEqual(len(current['entries']),577)
        self.assertEqual(len(report['deferred']),14)
        targets=' '.join(s['translation'].replace('\n',' ') for e in current['entries'][511:] for s in e['segments'])
        for name in ('Veteran Hunter','Elite Hunter','Ace Hunter','Invincible Hunter','Disassembler','Scarlet','Red Fox'):
            self.assertIn(name,targets)
        self.assertEqual(len(sources),8)

    def test_v009_large_lot_preserves_previous_prefix_and_game_names(self):
        parent,_=load_draft(REGION_V8_DRAFT)
        old,_,_=compile_draft(self.data,parent)
        draft,sources=load_draft(REGION_V9_DRAFT)
        current,patches,report=compile_draft(self.data,draft)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(666,111,0))
        self.assertEqual(current['entries'][:577],old['entries'])
        self.assertEqual(len(current['entries']),777)
        self.assertEqual(len(report['deferred']),16)
        self.assertFalse(set(draft['deferred'])&{p['id'] for p in patches})
        self.assertEqual(len(sources),9)
        for entry in current['entries'][577:]:
            for segment in entry['segments']:
                if not segment['editable']:
                    self.assertEqual(segment['source'],segment['translation'])
        targets=' '.join(s['translation'].replace('\n',' ') for e in current['entries'][577:] for s in e['segments'])
        for name in ('Rosa Beldaire','Sebastian','Arthur','Leon','Fang','Helga','Crossfire','Iron Slugs','Magnum Cycles'):
            self.assertIn(name,targets)

    def test_v010_preserves_v009_places_native_blocks_and_gameplay_details(self):
        parent,_=load_draft(REGION_V9_DRAFT)
        old,_,_=compile_draft(self.data,parent)
        draft,sources=load_draft(REGION_V10_DRAFT)
        current,patches,report=compile_draft(self.data,draft)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(829,148,0))
        self.assertEqual(current['entries'][:777],old['entries'])
        self.assertEqual(len(current['entries']),977)
        self.assertEqual(len(report['deferred']),19)
        self.assertFalse(set(draft['deferred'])&{p['id'] for p in patches})
        self.assertEqual(len(sources),10)
        by_id={e['id']:e for e in current['entries']}
        for entry in current['entries'][777:]:
            for segment in entry['segments']:
                if not segment['editable'] or entry['id'].startswith('map.supr.'):
                    self.assertEqual(segment['source'],segment['translation'])
        def body(key):return by_id[key]['segments'][0]['translation']
        self.assertIn('440 libras',body('map.smsg.1df82154'))
        self.assertIn('62 segundos',body('map.msg.1df86484'))
        for key,percent in [('map.msg.1df828b8','30'),('map.msg.1df829c8','60'),('map.msg.1df82b14','90')]:
            self.assertIn(percent+' por cento',body(key))
        self.assertIn('direita',body('map.msg.1df823ec'))
        self.assertIn('esquerda',body('map.msg.1df828b8'))
        self.assertIn('barril',body('map.msg.1df829c8'))
        self.assertIn('debaixo da mesa',body('map.msg.1df82b14'))
        self.assertIn('geladeira',body('map.msg.1df82c6c'))

    def test_v011_preserves_v010_ui_names_and_too_short_negative_response(self):
        parent,_=load_draft(REGION_V10_DRAFT)
        old,_,_=compile_draft(self.data,parent)
        draft,sources=load_draft(REGION_V11_DRAFT)
        current,patches,report=compile_draft(self.data,draft)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(990,187,0))
        self.assertEqual(current['entries'][:977],old['entries'])
        self.assertEqual(len(current['entries']),1177)
        self.assertEqual(len(report['deferred']),25)
        self.assertFalse(set(draft['deferred'])&{p['id'] for p in patches})
        self.assertEqual(len(sources),11)
        by_id={e['id']:e for e in current['entries']}
        negative=by_id['map.msg.1df8bec0']['segments'][0]
        self.assertEqual(negative['capacity'],3)
        self.assertEqual(negative['source'],negative['translation'])
        self.assertIn('3 bytes',draft['deferred']['map.msg.1df8bec0'])
        self.assertIn('Drive',by_id['map.msg.1f326a0c']['segments'][0]['translation'])
        self.assertIn('HELP',by_id['map.msgb.1f326acc']['segments'][0]['translation'])
        self.assertEqual(by_id['map.msg.1f328034']['segments'][0]['translation'].count('Trash Heap'),2)
        self.assertIn('nível 3',by_id['map.msg.1f3281ec']['segments'][0]['translation'])

    def test_v012_ascii_no_and_previous_prefix(self):
        import re
        from gfi import encode
        parent,_=load_draft(REGION_V11_DRAFT)
        old,_,_=compile_draft(self.data,parent)
        draft,sources=load_draft(REGION_V12_DRAFT)
        current,patches,report=compile_draft(self.data,draft)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(1083,280,0))
        self.assertEqual(len(current['entries']),1363)
        self.assertEqual(len(report['deferred']),67)
        self.assertEqual(len(sources),12)
        resumed='map.msg.1df8bec0'
        for before,after in zip(old['entries'],current['entries']):
            expected=copy.deepcopy(before)
            if before['id']==resumed:expected['segments'][0]['translation']='nao'
            self.assertEqual(after,expected)
        self.assertNotIn(resumed,draft['deferred'])
        patch=next(p for p in patches if p['id']==resumed)
        self.assertEqual(patch['before'][:32],patch['after'][:32])
        self.assertEqual(patch['before'][32:],b'No.\0')
        self.assertEqual(patch['after'][32:],b'nao\0')
        self.assertEqual(len(patch['before']),len(patch['after']))
        self.assertEqual(encode('nao'),bytes.fromhex('6e616f'))
        self.assertEqual(len(encode('Não')),4)
        exceptions={e['id'] for e in current['entries'] for s in e['segments']
                    if re.search(r'\bnao\b',s['translation'])}
        self.assertEqual(exceptions,{resumed})
        self.assertFalse(set(draft['deferred'])&{p['id'] for p in patches})

    def test_v013_extends_lower_boundary_and_preserves_all_v012_records(self):
        from prepare_translation_lot import prepare
        parent,_=load_draft(REGION_V12_DRAFT)
        old,_,_=compile_draft(self.data,parent)
        proposal,pending=prepare(self.data,parent,start=0x1d0b5680)
        self.assertEqual(proposal['scope']['records'],1563)
        self.assertEqual((len(pending),len(proposal['aliases']),len(proposal['deferred'])),(139,48,13))
        draft,sources=load_draft(REGION_V13_DRAFT)
        current,patches,report=compile_draft(self.data,draft)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(1241,322,0))
        self.assertEqual(current['entries'][200:],old['entries'])
        self.assertEqual(len(report['deferred']),80)
        self.assertEqual(len(sources),13)
        self.assertFalse(set(draft['deferred'])&{p['id'] for p in patches})
        by_id={e['id']:e for e in current['entries']}
        self.assertEqual(by_id['map.msg.1df8bec0']['segments'][0]['translation'],'nao')
        self.assertIn('10 minutos',by_id['map.msg.1dc5ef98']['segments'][0]['translation'])
        self.assertIn('Spiffy Tube',by_id['map.msg.1dc5ef98']['segments'][0]['translation'])
        self.assertIn('Dragon Choppers',by_id['map.msgn.1d0b9fb0']['segments'][0]['translation'])

    def test_v014_doubled_lot_keeps_previous_records_and_item_variants(self):
        import re
        from prepare_translation_lot import prepare
        parent,_=load_draft(REGION_V13_DRAFT)
        old,_,_=compile_draft(self.data,parent)
        proposal,pending=prepare(self.data,parent,start=0x1c64a06c)
        self.assertEqual(proposal['scope']['records'],1963)
        self.assertEqual((len(pending),len(proposal['aliases']),len(proposal['deferred'])),(291,100,9))
        draft,sources=load_draft(REGION_V14_DRAFT)
        current,patches,report=compile_draft(self.data,draft)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(1572,391,0))
        self.assertEqual(current['entries'][400:],old['entries'])
        self.assertEqual(len(current['entries']),1963)
        self.assertEqual(len(report['deferred']),89)
        self.assertEqual(len(sources),14)
        self.assertFalse(set(draft['deferred'])&{p['id'] for p in patches})
        by_id={e['id']:e for e in current['entries']}
        def body(key):return by_id[key]['segments'][0]['translation']
        for key,name in [('map.msg.1d0ab8f8','Growgaine'),('map.msg.1d0abfac','Growgaine 3'),
                         ('map.msg.1d0ac5f8','Growgaine T'),('map.msg.1d0acc24','Growgaine L'),
                         ('map.msg.1d0ad250','Growgaine A')]:
            self.assertIn(name,body(key))
        self.assertIn('0 espaços',body('map.msg.1c64ab68'))
        self.assertIn('21',body('map.msg.1d0b5488'))
        route=body('map.msg.1d0afd58')
        for part in ('norte','noroeste','sul de East Zero','Grande Destruição'):
            self.assertIn(part,route)
        exceptions={e['id'] for e in current['entries'] for s in e['segments']
                    if re.search(r'\bnao\b',s['translation'])}
        self.assertEqual(exceptions,{'map.msg.1df8bec0'})

    def test_v015_eight_hundred_records_preserve_prior_lot_and_context(self):
        import re
        from prepare_translation_lot import prepare
        parent,_=load_draft(REGION_V14_DRAFT)
        old,_,_=compile_draft(self.data,parent)
        proposal,pending=prepare(self.data,parent,start=0x169b91dc)
        self.assertEqual(proposal['scope']['records'],2763)
        self.assertEqual((len(pending),len(proposal['aliases']),len(proposal['deferred'])),(469,300,31))
        draft,sources=load_draft(REGION_V15_DRAFT)
        current,patches,report=compile_draft(self.data,draft)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(2165,598,0))
        self.assertEqual(current['entries'][800:],old['entries'])
        self.assertEqual(len(sources),15)
        self.assertEqual(len(report['deferred']),120)
        self.assertFalse(set(draft['deferred'])&{p['id'] for p in patches})
        by_id={e['id']:e for e in current['entries']}
        def body(key):return by_id[key]['segments'][0]['translation']
        self.assertIn('Gluteus Maximism',body('map.msg.169b9388'))
        self.assertIn('seis\nlibras',body('map.msg.169befb4'))
        self.assertIn('cinco milhas',body('map.msg.169befb4'))
        self.assertIn('300 objetos',body('map.msg.19f541b4'))
        for part in ('Marilyn Grey','Hunter'):
            self.assertIn(part,body('map.msg.17746ae4'))
        route=body('map.msgn.1774bdf4')
        for part in ('Tin Tunas','noroeste','ao sul'):
            self.assertIn(part,route)
        self.assertEqual(body('map.msg.1afd9694'),'Não...')
        self.assertEqual(body('map.msg.1774e8e8'),body('map.msg.169bffc8'))
        exceptions={e['id'] for e in current['entries'] for s in e['segments']
                    if re.search(r'\bnao\b',s['translation'])}
        self.assertEqual(exceptions,{'map.msg.1df8bec0'})

    def test_v016_preserves_all_prior_records_and_train_dowan_context(self):
        import re
        from prepare_translation_lot import prepare
        parent,_=load_draft(REGION_V15_DRAFT)
        old,_,_=compile_draft(self.data,parent)
        proposal,pending=prepare(self.data,parent,start=0x1282f8cc)
        self.assertEqual(proposal['scope']['records'],3563)
        self.assertEqual((len(pending),len(proposal['aliases']),len(proposal['deferred'])),(507,270,23))
        draft,sources=load_draft(REGION_V16_DRAFT)
        current,patches,report=compile_draft(self.data,draft)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(2806,757,0))
        self.assertEqual(current['entries'][800:],old['entries'])
        self.assertEqual(len(current['entries']),3563)
        self.assertEqual(len(sources),16)
        self.assertEqual(len(report['deferred']),143)
        self.assertFalse(set(draft['deferred'])&{p['id'] for p in patches})
        by_id={e['id']:e for e in current['entries']}
        def body(key):return by_id[key]['segments'][0]['translation']
        self.assertIn('150G',body('map.2smg.128316ec'))
        self.assertIn('10G',body('map.2smg.13709d6c'))
        self.assertIn('100G',body('map.2smg.1371fd7c'))
        self.assertIn('Gluttony',body('map.msgn.1370e54c'))
        self.assertIn('Catherine',body('map.msg.1370e608'))
        for part in ('Sky Demon','B2 Manta Ray','Eagle 1'):
            self.assertIn(part,re.sub(r'\s+',' ',body('map.msg.1476db28')))
        for part in ('sudeste','leste'):
            self.assertIn(part,body('map.msgn.14aab7b8'))
        self.assertIn('3 vezes',body('map.msgn.1576e884'))
        self.assertIn('Fang',body('map.msg.1576a8b8'))
        self.assertIn('Rouge Rogues',body('map.msg.1576a8b8'))
        exceptions={e['id'] for e in current['entries'] for s in e['segments']
                    if re.search(r'\bnao\b',s['translation'])}
        self.assertEqual(exceptions,{'map.msg.1df8bec0'})

    def test_v017_preserves_prior_lot_and_dynamic_names_and_controls(self):
        import re
        from prepare_translation_lot import prepare
        from dialogue_formats import tokens
        from gfi import encode
        parent,_=load_draft(REGION_V16_DRAFT)
        old,_,_=compile_draft(self.data,parent)
        proposal,pending=prepare(self.data,parent,start=0x0e77a270)
        self.assertEqual(proposal['scope']['records'],4363)
        self.assertEqual((len(pending),len(proposal['aliases']),len(proposal['deferred'])),(419,333,48))
        draft,sources=load_draft(REGION_V17_DRAFT)
        current,patches,report=compile_draft(self.data,draft)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(3432,931,0))
        self.assertEqual(current['entries'][800:],old['entries'])
        self.assertEqual(len(current['entries']),4363)
        self.assertEqual(len(sources),17)
        self.assertEqual(len(report['deferred']),191)
        self.assertFalse(set(draft['deferred'])&{p['id'] for p in patches})
        by_id={e['id']:e for e in current['entries']}
        def body(key):return by_id[key]['segments'][0]['translation']
        self.assertIn('Maus',body('map.msg.0f83443c'))
        self.assertIn('Fort Gears',body('map.msgn.0f835940'))
        self.assertIn('braço direito',body('map.msg.0e782624'))
        self.assertIn('crítico',body('map.msg.0e782624'))
        for part in ('100G','punk','canivete borboleta'):
            self.assertIn(part,body('map.msgn.1282db58'))
        for part in ('sudeste','nordeste','sudoeste','Bazooka Pooches'):
            self.assertIn(part,body('map.msgn.1282d924'))
        for key in ('map.msg.0f835554','map.msg.10cf5518','map.msg.12121d58',
                    'map.msg.12823574'):
            segment=by_id[key]['segments'][0]
            a,_=tokens(bytes.fromhex(segment['source_hex']))
            b,_=tokens(encode(segment['translation']))
            self.assertEqual([x['hex'] for x in a],[x['hex'] for x in b])
        exceptions={e['id'] for e in current['entries'] for s in e['segments']
                    if re.search(r'\bnao\b',s['translation'])}
        self.assertEqual(exceptions,{'map.msg.1df8bec0'})

    def test_v018_preserves_prior_lot_and_collection_names(self):
        import re
        from prepare_translation_lot import prepare
        parent,_=load_draft(REGION_V17_DRAFT)
        old,_,_=compile_draft(self.data,parent)
        proposal,pending=prepare(self.data,parent,start=0x0be1fd64)
        self.assertEqual(proposal['scope']['records'],5163)
        self.assertEqual((len(pending),len(proposal['aliases']),len(proposal['deferred'])),(444,282,74))
        draft,sources=load_draft(DEFAULT_DRAFT)
        current,patches,report=compile_draft(self.data,draft)
        self.assertTrue(report['valid'])
        self.assertEqual((report['accepted'],report['unchanged'],report['refused']),(4034,1129,0))
        self.assertEqual(current['entries'][800:],old['entries'])
        self.assertEqual(len(sources),18)
        self.assertEqual(len(report['deferred']),265)
        patched={p['id'] for p in patches}
        self.assertFalse(set(draft['deferred'])&patched)
        by_id={e['id']:e for e in current['entries']}
        for suffix in ('b81c','b87c','b8cc','b92c','b98c','b9ec','ba4c','ba9c','baec','bb4c'):
            key='map.msgn.0be2'+suffix
            self.assertNotIn(key,patched)
            for segment in by_id[key]['segments']:
                self.assertEqual(segment['source'],segment['translation'])
        exceptions={e['id'] for e in current['entries'] for s in e['segments']
                    if re.search(r'\bnao\b',s['translation'])}
        self.assertEqual(exceptions,{'map.msg.1df8bec0'})

    def test_prepare_rejects_ambiguous_or_shrinking_boundaries(self):
        from prepare_translation_lot import prepare
        parent={'scope':{'first_offset':'20','last_offset':'40'}}
        with mock.patch('prepare_translation_lot.compile_draft',return_value=({'entries':[]},[],{'valid':True})), \
             mock.patch('prepare_translation_lot.SsdIndex'):
            for kwargs in ({},{'end':0x50,'start':0x10},{'start':0x20},
                           {'start':0x30},{'start':-1},{'end':0x40},{'end':0x30}):
                with self.subTest(kwargs=kwargs):
                    with self.assertRaises(ValueError):prepare(b'',parent,**kwargs)

    def test_resume_requires_explicit_child_target_and_existing_parent_deferral(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-resume-') as folder:
            folder=Path(folder)
            base={'translations':{},'deferred':{'old':'why'},'aliases':{}}
            (folder/'base.json').write_text(json.dumps(base),encoding='utf-8')
            valid={'extends':'base.json','resume_deferred':['old'],'translations':{'old':'nao'}}
            (folder/'child.json').write_text(json.dumps(valid),encoding='utf-8')
            draft,_=load_draft(folder/'child.json')
            self.assertEqual(draft['deferred'],{})
            unchanged,_=load_draft(folder/'base.json')
            self.assertEqual(unchanged['deferred'],{'old':'why'})
            for extra in ({'translations':{}},{'resume_deferred':['missing']},
                          {'resume_deferred':['old','old']},{'deferred':{'old':'still deferred'}},
                          {'aliases':{'old':'other'}},{'resume_deferred':'old'}):
                with self.subTest(extra=extra):
                    (folder/'child.json').write_text(json.dumps({**valid,**extra}),encoding='utf-8')
                    with self.assertRaises(ValueError):load_draft(folder/'child.json')

    def test_lot_preparation_excludes_manually_deferred_alias_sources(self):
        from prepare_translation_lot import prepare
        previous={'id':'old','blocked_reasons':[],
                  'segments':[{'key':'body','source_hex':'4e6f2e','editable':True}]}
        following={**previous,'id':'new'}
        parent={'scope':{'first_offset':'0','last_offset':'20'},'deferred':{'old':'slot too short'}}
        data=bytearray(104);data[100:104]=b'msg\0'
        with mock.patch('prepare_translation_lot.compile_draft',return_value=({'entries':[previous]},[],{'valid':True})), \
             mock.patch('prepare_translation_lot.SsdIndex') as index, \
             mock.patch('prepare_translation_lot.descriptor',return_value=following):
            index.return_value.records={100:None}
            proposal,pending=prepare(data,parent,100)
        self.assertEqual(proposal['aliases'],{})
        self.assertEqual(proposal['translations'],{'new':''})
        self.assertEqual(len(pending),1)
        parent['deferred']={}
        parent['ascii_exception']={'id':'old','target':'nao'}
        with mock.patch('prepare_translation_lot.compile_draft',return_value=({'entries':[previous]},[],{'valid':True})), \
             mock.patch('prepare_translation_lot.SsdIndex') as index, \
             mock.patch('prepare_translation_lot.descriptor',return_value=following):
            index.return_value.records={100:None}
            proposal,_=prepare(data,parent,100)
        self.assertEqual(proposal['aliases'],{})
        self.assertEqual(proposal['translations'],{'new':''})

    def test_more_than_eight_draft_versions_and_cycle_rejection(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-draft-chain-') as folder:
            folder=Path(folder)
            for n in range(10):
                draft={'translations':{},'aliases':{},'deferred':{}}
                if n:draft['extends']=f'{n-1}.json'
                (folder/f'{n}.json').write_text(json.dumps(draft),encoding='utf-8')
            _,sources=load_draft(folder/'9.json')
            self.assertEqual(len(sources),10)
            (folder/'0.json').write_text(json.dumps({'extends':'9.json'}),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'circular inheritance'):
                load_draft(folder/'9.json')

    def test_duplicate_authored_keys_are_not_silently_overwritten(self):
        raw=b'{"schema":1,"translations":{"same.id":"first","same.id":"second"}}'
        with mock.patch.object(Path,'read_bytes',return_value=raw):
            with self.assertRaisesRegex(ValueError,'Duplicate authored JSON key'):
                load_draft(DEFAULT_DRAFT)


if __name__=='__main__':unittest.main()
