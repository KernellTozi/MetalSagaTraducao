import copy,io,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from discover_remaining_catalogue import ascii_stream,phrase_candidate,label_deficit,item_discovery,title_discovery,elf_discovery,write_local,run,SCOPE,phrase_triage,engine_variants,font_discovery,location_discovery


class DiscoveryCatalogue(unittest.TestCase):
    def test_stream_crosses_every_small_chunk_boundary_without_duplicates(self):
        data=b'\x01First sentence here.\0Second line\r\ncontinues here.\0END\0'
        expected=[(1,b'First sentence here.'),(22,b'Second line\r\ncontinues here.')]
        for size in (1,2,3,4,7,16,64):self.assertEqual(list(ascii_stream(io.BytesIO(data),size)),expected,size)
    def test_stream_rejects_long_runs_and_does_not_emit_truncated_suffixes(self):
        data=b'X'*1025+b'\0Good new sentence.\0'+b'Y'*1024+b'\0'
        for size in (7,64,1024,2048):
            rows=list(ascii_stream(io.BytesIO(data),size));self.assertEqual(rows,[(1026,b'Good new sentence.'),(1045,b'Y'*1024)])
        with self.assertRaises(ValueError):list(ascii_stream(io.BytesIO(b''),0))
    def test_phrase_filter_is_only_shape_and_excludes_paths_short_noise(self):
        self.assertTrue(phrase_candidate(b'Please select a vehicle.'))
        self.assertTrue(phrase_candidate(b'Line one\r\nLine two'))
        for raw in (b'data/game/file.sda',b'aa bb',b'X! @#A %%b C',b'Menu'):self.assertFalse(phrase_candidate(raw))
    def test_record_minimum_counts_nul_bytes_not_unicode_characters(self):
        entry={'tag':b'msgn'.hex(),'offset':0,'segments':[{'offset':32},{}]};record=bytes(32)+b'ABC\0Man\0'
        r=label_deficit(entry,record,'Homem');self.assertEqual(r['extra_bytes_required'],2)
        r=label_deficit(entry,record,'Cão');self.assertEqual(r['label_target_bytes'],4);self.assertEqual(r['extra_bytes_required'],1)
        with self.assertRaises(ValueError):label_deficit({**entry,'tag':b'smnn'.hex()},record,'Homem')
    def test_existing_item_proposals_group_all_causes_without_authorizing_growth(self):
        from interface_text import SOURCE
        recipe=json.loads((ROOT/'translations/interface-v037.json').read_text(encoding='utf-8'))
        raw=(ROOT/'JOGO/Metal Saga/DATA/S/S_PACK.SDA').read_bytes();before=bytes(raw)
        r,rows=item_discovery(recipe,SOURCE.read_bytes(),raw)
        self.assertEqual(r['pending_names'],25);self.assertEqual(r['proposals_above_16_but_within_23'],20)
        self.assertEqual(r['original_maximum_bytes'],16);self.assertEqual(r['description_pointer_at'],24)
        self.assertEqual(r['blockers_nonexclusive'],{'unmapped-glyph':1,'exceeds-observed-16-byte-ceiling':20,'terminology-or-name-review':4})
        self.assertTrue(all(not row['editing_authorized'] for row in rows));self.assertEqual(raw,before)
    def test_title_shared_action_does_not_claim_external_destination(self):
        from interface_text import SOURCE
        raw=SOURCE.read_bytes();r=title_discovery(raw)
        self.assertEqual(len(r['title_slots']),1);self.assertEqual(r['title_slots'][0],{'offset':0x32a31e,'capacity':5})
        self.assertEqual([c['requested_state'] for c in r['request_cases']],[None,4,4,4])
        self.assertEqual([c['return_value'] for c in r['completion_cases']],[1,0])
        self.assertEqual([(c['flags'],c['index']) for c in r['title_initialization_cases'] if c['title_mode']],[(1,0)])
        self.assertFalse(r['editing_authorized']);self.assertTrue(r['terminal_lh_simulated_by_harness'])
        bad=bytearray(raw);bad[0x10b7d0]^=1
        with self.assertRaises(ValueError):title_discovery(bad)
    def test_elf_overlap_and_pointer_shapes_are_triage_not_edit_approval(self):
        from interface_text import SOURCE
        raw=SOURCE.read_bytes();pointer=(0x21526c).to_bytes(4,'little')[:3]
        rows=[{'id':'a','offset':0x32b110,'source_hex':b'Status/Equip'.hex(),'source':'Status/Equip','planning_status':'review-reference','references':[]},
            {'id':'b','offset':0x32b550,'source_hex':pointer.hex(),'source':pointer.decode('ascii'),'planning_status':'short-fragment-review','references':[]}]
        patches=[{'resource':'SLUS_212.93','offset':0x32b110,'after':b'PT-BR       ','id':'authored'}]
        r,found=elf_discovery(raw,{'elf':rows},patches)
        self.assertEqual(found[0]['discovery_class'],'within-authored-patch');self.assertEqual(found[1]['discovery_class'],'address-like-data-review')
        self.assertTrue(all(not row['editing_authorized'] for row in found))
    def test_output_is_atomic_work_only_and_unrelated_files_preserved(self):
        with self.assertRaises(ValueError):write_local(ROOT/'reports/forbidden-originals.json',{'scope':SCOPE})
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-discovery-') as folder:
            target=Path(folder)/'catalog.json';target.write_text('{}',encoding='utf-8')
            with self.assertRaises(ValueError):write_local(target,{'scope':SCOPE})
            self.assertEqual(target.read_text(encoding='utf-8'),'{}')
            target.unlink();write_local(target,{'scope':SCOPE,'version':1});write_local(target,{'scope':SCOPE,'version':2})
            self.assertEqual(json.loads(target.read_text(encoding='utf-8'))['version'],2)
            target.with_suffix('.json.tmp').write_text('busy',encoding='utf-8')
            with self.assertRaises(FileExistsError):write_local(target,{'scope':SCOPE,'version':3})
            self.assertEqual(json.loads(target.read_text(encoding='utf-8'))['version'],2)
    def test_main_rejects_unsafe_output_before_reading_any_game_resource(self):
        with self.assertRaises(ValueError):run(ROOT/'translations/interface-v037.json',ROOT/'reports/not-allowed.json',ROOT/'reports/never-written-discovery.json')
    def test_phrase_triage_uses_original_description_offsets_and_keeps_raster_separate(self):
        planning={'item_names':[],'item_descriptions':[{'offset':300,'original_offset':200,'source_hex':b'Name'.hex()}],
            'spack_ui':{'entries':[]},'battle_fields':[{'offset':400,'field_bytes':32}]}
        def row(resource,at,text):return {'resource':resource,'offset':at,'size':len(text)+1,'source':text,'authored_patch_overlap':False}
        rows=[row('DATA/S/S_PACK.SDA',200,'Name'),row('DATA/S/S_PACK.SDA',300,'Name'),row('DATA/S/S_PACK.SDA',398,'@@Name'),row('DATA/FDATA/X.SDA',800,'Paint Menu')]
        counts=phrase_triage(rows,planning,[{'resource':'DATA/FDATA/X.SDA','entries':[{'kind':'texture','offset':800,'size':100}]}])
        self.assertEqual(rows[0]['catalogue_relation'],'known-description-field');self.assertNotEqual(rows[1]['catalogue_relation'],'known-description-field')
        self.assertEqual(rows[2]['catalogue_relation'],'known-battle-field-or-adjacent-bytes');self.assertEqual(rows[3]['catalogue_relation'],'recognized-raster-bytes')
    def test_engine_variant_names_are_located_and_preserved_not_added_to_translation_queue(self):
        raw=(ROOT/'JOGO/Metal Saga/DATA/S/S_PACK.SDA').read_bytes();metadata,rows=engine_variants(raw)
        self.assertEqual((metadata['records'],metadata['name_fields'],metadata['nonempty_names']),(10,50,26))
        self.assertFalse(metadata['consumer_proven']);self.assertFalse(metadata['editing_authorized'])
        self.assertTrue(all(r['decision']=='preserve-user-engine-name-rule' for r in rows))
        bad=bytearray(raw);bad[0x320f0]^=1
        with self.assertRaises(ValueError):engine_variants(bad)
    def test_font_discovery_does_not_extend_codec_or_touch_existing_cells(self):
        from gfi import CHAR_TO_BYTES
        original=copy.deepcopy(CHAR_TO_BYTES);r=font_discovery()
        self.assertEqual(r['current_project_mapping_count'],18);self.assertEqual(len(r['unmapped_ptbr_codepoints']),8)
        self.assertIn('U+00D3',r['unmapped_ptbr_codepoints']);self.assertEqual(len(r['common_blank_unassigned_pairs']),14)
        self.assertFalse(r['editing_authorized']);self.assertFalse(r['font_or_codec_changed']);self.assertEqual(CHAR_TO_BYTES,original)
    def test_destination_records_and_opaque_tail_are_not_a_free_text_pool(self):
        from interface_text import SOURCE
        raw=(ROOT/'JOGO/Metal Saga/DATA/S/S_PACK.SDA').read_bytes();meta,rows,tail=location_discovery(SOURCE.read_bytes(),raw)
        self.assertEqual((meta['records'],meta['unique_names'],meta['name_field_bytes']),(25,25,32))
        self.assertEqual(len({r['id'] for r in rows}),25);self.assertEqual(meta['original_pointer_cases'],25)
        self.assertTrue(tail['matching_known_enemy_record']['byte_identical']);self.assertEqual(tail['tail_size'],1440)
        self.assertFalse(meta['editing_authorized']);self.assertFalse(tail['editing_authorized'])


if __name__=='__main__':unittest.main()
