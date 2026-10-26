import copy,json,struct,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import discover_unknown_entries as discover
from explore_interface_atlases import classify


class UnknownDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=json.loads((ROOT/'reports/descoberta-desconhecidos-v001.json').read_text(encoding='utf-8'))
        cls.resources={r['resource']:(ROOT/'JOGO/Metal Saga'/r['resource']).read_bytes() for r in cls.report['records']}
        cls.elf=discover.SOURCE.read_bytes()

    def raw(self,row):return self.resources[row['resource']][row['offset']:row['offset']+row['size']]
    def rows(self,kind):return [r for r in self.report['records'] if r['discovery']['kind']==kind]

    def test_frozen_baseline_complete_unique_and_no_edit_release(self):
        r=self.report
        self.assertEqual(len(r['records']),365);self.assertEqual(sum(r['classes'].values()),365)
        self.assertEqual(len({(v['resource'],v['offset']) for v in r['records']}),365)
        self.assertTrue(all(not v['editing_authorized'] for v in r['records']))
        self.assertEqual(r['classes']['unresolved'],81)
        self.assertEqual(sum(r['unresolved_groups'].values()),81)
        self.assertEqual(r['child_classes']['opaque-bundle-child'],5740)
        self.assertFalse(r['iso_created']);self.assertFalse(r['translation_created'])

    def test_all_140_bundles_roundtrip_offsets_without_promoting_5740_payloads(self):
        self.assertEqual(len(self.rows('41-part-offset-bundle')),140)
        for row in self.rows('41-part-offset-bundle'):
            parsed=discover.bundle41(self.raw(row))
            self.assertEqual(len(parsed['ranges']),41);self.assertTrue(parsed['roundtrip'])
        raw=bytearray(self.raw(self.rows('41-part-offset-bundle')[0]))
        for position,value in ((0,42),(4,0),(8,168),(164,len(raw))):
            bad=bytearray(raw);struct.pack_into('<I',bad,position,value)
            with self.assertRaises(ValueError):discover.bundle41(bad)

    def test_all_dai_dpi_containers_and_each_new_child_texture_roundtrip(self):
        counts={'indexed-texture':0,'direct-rgba-texture':0}
        for kind in ('dai-texture-container','dpi-texture-container'):
            for row in self.rows(kind):
                raw=self.raw(row);parsed=discover.offset_container(raw,raw[:4]);self.assertTrue(parsed['roundtrip'])
                for a,z in parsed['ranges']:
                    image=discover.child_texture(raw[a:z]);counts[image['kind']]+=1
                    self.assertTrue(image['roundtrip'])
        self.assertEqual(counts,{'indexed-texture':103,'direct-rgba-texture':19})

    def test_container_bad_size_count_order_alignment_header_overlap_refused(self):
        raw=self.raw(self.rows('dai-texture-container')[0])
        count=struct.unpack_from('<I',raw,8)[0]
        for position,value in ((4,len(raw)+1),(8,0),(8,999999),(12,0),(12,17)):
            bad=bytearray(raw);struct.pack_into('<I',bad,position,value)
            with self.assertRaises(ValueError):discover.offset_container(bad,b'dai\0')
        if count>1:
            bad=bytearray(raw);bad[16:20]=bad[12:16]
            with self.assertRaises(ValueError):discover.offset_container(bad,b'dai\0')

    def test_all_sequence_ganm_rebuilt_with_opaque_tails_and_explicit_variants(self):
        rows=self.rows('ganm-sprite-sequence-table');self.assertEqual(len(rows),15)
        variants=0
        for row in rows:
            variant=row['discovery']['first_field_profile']=='source-bound-nonsequential-opaque'
            parsed=discover.ganm_sequences(self.raw(row),variant);self.assertTrue(parsed['roundtrip'])
            self.assertTrue(all(f['sprite']<parsed['sprite_count'] for g in parsed['groups'] for f in g['frames']))
            if variant:
                variants+=1
                with self.assertRaises(ValueError):discover.ganm_sequences(self.raw(row))
        self.assertEqual(variants,2)
        tail=next(r for r in rows if r['resource'].endswith('S_PAINT.SDA') and r['offset']==0xcbe0)
        self.assertTrue(discover.ganm_sequences(self.raw(tail))['tail_nonzero'])

    def test_ganm_header_sequence_frame_bounds_refused(self):
        raw=self.raw(self.rows('ganm-sprite-sequence-table')[0]);start=struct.unpack_from('<I',raw,12)[0]
        for position,value,fmt in ((4,0,'H'),(6,0,'H'),(8,12,'I'),(12,0,'I'),(start+4,99999,'I'),(start+10,65535,'H')):
            bad=bytearray(raw);struct.pack_into('<'+fmt,bad,position,value)
            with self.assertRaises(ValueError):discover.ganm_sequences(bad)

    def test_actual_original_header_frame_and_stamp_nibble_instructions(self):
        evidence=discover.consumer_evidence(self.elf,self.report['records'],self.resources)
        self.assertEqual(evidence['ganm_original_header_cases'],15)
        self.assertEqual(evidence['ganm_original_frame_lookup_cases'],335)
        self.assertEqual(evidence['stamp_original_nibble_cases'],256)

    def test_stamp_palettes_pixels_and_direct_images_keep_exact_bounds(self):
        for row in self.rows('paint-headerless-palette16-stamp'):
            meta=discover.stamp(self.raw(row));self.assertTrue(meta['roundtrip']);self.assertEqual(meta['pixel_bytes'],2048)
        for row in self.rows('direct-rgb-texture'):
            raw=self.raw(row);meta=discover.direct_texture(raw);self.assertEqual((meta['width'],meta['height'],meta['bpp']),(512,64,24))
            bad=bytearray(raw);bad[-1]=1
            with self.assertRaises(ValueError):discover.direct_texture(bad)
            with self.assertRaises(ValueError):discover.direct_texture(raw[:100])
        with self.assertRaises(ValueError):discover.stamp(bytes(2111))

    def test_came_records_cannot_escape_or_ignore_nonzero_tail(self):
        for row in self.rows('came-counted-fixed20-records'):
            self.assertTrue(discover.came(self.raw(row))['roundtrip'])
        raw=bytearray(self.raw(self.rows('came-counted-fixed20-records')[0]));raw[-1]=1
        with self.assertRaises(ValueError):discover.came(raw)
        with self.assertRaises(ValueError):discover.came(b'CAME'+struct.pack('<I',100))

    def test_character_list_and_note_do_not_promote_source_padding_as_dialogue(self):
        row=self.rows('name-entry-kanji-pair-list')[0];raw=self.raw(row)
        self.assertEqual(discover.kanji_list(raw)['pairs'],2965)
        self.assertEqual(discover.kanji_list(raw)['a5_tail_bytes'],58)
        bad=bytearray(raw);bad[0]=0
        with self.assertRaises(ValueError):discover.kanji_list(bad)
        row=self.rows('name-entry-technical-note-with-opaque-tail')[0]
        meta=discover.note(self.raw(row));self.assertEqual((meta['note_bytes'],meta['tail_bytes']),(163,29))

    def test_historical_classifiers_are_not_silently_expanded(self):
        for kind in ('dai-texture-container','dpi-texture-container','ganm-sprite-sequence-table','paint-headerless-palette16-stamp'):
            self.assertEqual(classify(self.raw(self.rows(kind)[0]))['kind'],'unknown')

    def test_local_output_replace_is_scoped_and_blocks_unrelated_json(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-unknown-') as folder:
            p=Path(folder)/'catalog.json';discover.write_local(p,{'scope':discover.SCOPE,'version':1})
            discover.write_local(p,{'scope':discover.SCOPE,'version':2})
            self.assertEqual(json.loads(p.read_text())['version'],2)
            p.write_text('{}')
            with self.assertRaises(ValueError):discover.write_local(p,{'scope':discover.SCOPE})

    def test_new_images_are_reviewed_once_without_inflating_translation_work(self):
        rows=self.report['new_image_visual_review'];self.assertEqual(len(rows),172)
        self.assertEqual(len({(r['resource'],r['offset']) for r in rows}),172)
        self.assertEqual(self.report['new_image_visual_classes']['environment-or-gameplay-word-review'],2)
        self.assertEqual(self.report['new_image_visual_classes']['paint-stamp-symbol-or-alphabet'],48)

    def test_opaque_text_probe_detects_embedded_phrase_but_does_not_promote_it(self):
        raw=b'\0\x01Hello distant world\0\x00'
        rows=[{'resource':'fixture','offset':0,'size':len(raw),'discovery':{'kind':'unresolved'}}]
        result=discover.text_shape_probe(rows,[],{'fixture':raw})
        self.assertEqual(result['candidate_count'],1)
        self.assertEqual(result['candidates'][0]['offset'],2)
        actual=self.report['opaque_text_probe']
        self.assertEqual((actual['ranges_scanned'],actual['candidate_count']),(5821,0))
        self.assertEqual(actual['bytes_scanned'],46473104)


if __name__=='__main__':unittest.main()
