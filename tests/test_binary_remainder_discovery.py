import json,struct,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import discover_binary_remainder as d


class BinaryRemainderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=json.loads((ROOT/'reports/descoberta-desconhecidos-v002.json').read_text())
        cls.elf=d.SOURCE.read_bytes()
        cls.resources={k:(ROOT/'JOGO/Metal Saga'/k).read_bytes() for k in cls.report['source_sha256']}
        children=[];unique={}
        for row in cls.report['records']:
            if row['discovery']['kind']!='motion-offset-bundle':continue
            raw=cls.resources[row['resource']][row['offset']:row['offset']+row['size']]
            for index,(a,z) in enumerate(d.bundle_ranges(raw)):
                part=raw[a:z];key=d.sha(part)
                if key not in unique:unique[key]=d.motion(part)[0]
                children.append({'resource':row['resource'],'parent_offset':row['offset'],'index':index,
                    'offset':row['offset']+a,'size':z-a,'sha256':key})
        cls.catalogue={'children':children,'unique_payloads':unique}

    def raw(self,row):return self.resources[row['resource']][row['offset']:row['offset']+row['size']]

    def test_baseline_unique_and_classes_honest(self):
        r=self.report
        self.assertEqual(r['follow_up_roots'],221)
        self.assertEqual(sum(r['classes'].values()),221)
        self.assertEqual(len({(v['resource'],v['offset']) for v in r['records']}),221)
        self.assertEqual(r['classes']['motion-offset-bundle'],158)
        self.assertEqual(r['classes']['consumer-bound-model-opaque-geometry'],55)
        self.assertEqual(r['classes']['sound-bank-chunk-envelope'],5)
        self.assertEqual(r['remaining_unresolved_root_semantics'],3)
        self.assertTrue(all(not v['editing_authorized'] for v in r['records']))
        self.assertFalse(r['iso_created']);self.assertFalse(r['pcsx2_executed'])

    def test_every_unique_motion_readback_and_token_roundtrip(self):
        seen=set()
        for c in self.catalogue['children']:
            if c['sha256'] in seen:continue
            meta,decoded=d.motion(self.raw(c))
            self.assertEqual(meta,self.catalogue['unique_payloads'][c['sha256']])
            self.assertEqual(d.sha(decoded),meta['decoded_sha256']);seen.add(c['sha256'])
        self.assertEqual(len(seen),571)
        self.assertEqual(len(self.catalogue['children']),5876)

    def test_motion_unknown_suffixes_retained(self):
        children=self.catalogue['children'];unique=self.catalogue['unique_payloads']
        nonzero=[c for c in children if unique[c['sha256']]['tail_nonzero']]
        self.assertEqual(len(nonzero),5)
        for c in nonzero:
            self.assertTrue(c['resource'].endswith('F_SPEND.SDA'))
            raw=self.raw(c);meta,decoded=d.motion(raw)
            self.assertTrue(0<meta['tail_size']<16)
            self.assertEqual(d.sha(raw[-meta['tail_size']:]),meta['tail_sha256'])

    def test_motion_track_count_is_u16_with_opaque_high_half(self):
        c=self.catalogue['children'][0];raw=bytearray(self.raw(c))
        a,_=d.motion(raw);struct.pack_into('<H',raw,6,0xabcd);b,_=d.motion(raw)
        self.assertEqual(a['track_count'],b['track_count']);self.assertEqual(b['header_u16_opaque'],0xabcd)
        self.assertEqual(a['decoded_sha256'],b['decoded_sha256'])

    def test_motion_corrupt_headers_and_size_refused(self):
        raw=self.raw(self.catalogue['children'][0])
        for at,fmt,value in ((4,'H',0),(4,'H',65535),(8,'I',0),(8,'I',len(raw)),(8,'I',13)):
            bad=bytearray(raw);struct.pack_into('<'+fmt,bad,at,value)
            with self.assertRaises(ValueError):d.motion(bad)
        bad=bytearray(raw);start=struct.unpack_from('<I',bad,8)[0]
        struct.pack_into('<I',bad,start,1024*1024+1)
        with self.assertRaises(ValueError):d.motion(bad)

    def test_variable_block_overflow_refused(self):
        raw=struct.pack('<IHHI',1,1,0,28)+bytes(6)+bytes([1,0])+struct.pack('<H',65535)+bytes(6)+bytes(4)
        with self.assertRaises(ValueError):d.motion(raw)

    def test_bundle_corrupt_offsets_and_header_overlap_refused(self):
        row=next(r for r in self.report['records'] if r['discovery']['kind']=='motion-offset-bundle')
        raw=self.raw(row)
        for at,value in ((0,0),(0,999999),(4,0),(8,struct.unpack_from('<I',raw,4)[0]),(4,len(raw))):
            bad=bytearray(raw);struct.pack_into('<I',bad,at,value)
            with self.assertRaises(ValueError):d.bundle_ranges(bad)

    def test_all_saf_envelopes_and_exact_hd_tiling(self):
        rows=[r for r in self.report['records'] if r['discovery']['kind']=='sound-bank-chunk-envelope']
        self.assertEqual(len(rows),5)
        for row in rows:
            result=d.saf(self.raw(row));self.assertEqual(result,row['discovery'])
            self.assertEqual([c['tag'] for c in result['chunks']],['SAF ','HD  ','BD  ','END '])
            self.assertFalse(result['audio_samples_decoded'])

    def test_saf_bad_chunk_flags_sizes_subsections_and_terminal_refused(self):
        row=next(r for r in self.report['records'] if r['discovery']['kind']=='sound-bank-chunk-envelope')
        raw=self.raw(row);hd=row['discovery']['chunks'][1]['payload_offset']
        for at,value in ((0,0),(4,len(raw)),(8,1),(hd,0),(hd+8,0),(len(raw)-12,1)):
            bad=bytearray(raw);struct.pack_into('<I',bad,at,value)
            with self.assertRaises(ValueError):d.saf(bad)
        with self.assertRaises(ValueError):d.saf(raw+b'\0'*16)

    def test_all_model_bindings_exact_and_no_geometry_edit_release(self):
        b=d.model_bindings(self.elf);rows=[r for r in self.report['records'] if r['discovery']['kind']=='consumer-bound-model-opaque-geometry']
        self.assertEqual(len(rows),55)
        for r in rows:
            expected=b[(Path(r['resource']).name,r['offset'])];actual=r['discovery']
            self.assertEqual({k:actual[k] for k in expected},expected)
            self.assertLessEqual(actual['model_size'],r['size'])
        broken=bytearray(self.elf);broken[0]^=1
        with self.assertRaises(ValueError):d.model_bindings(broken)

    def test_original_decoder_three_distinct_profiles_executed(self):
        cases=self.report['original_decoder_cases']
        self.assertEqual({c['profile'] for c in cases},{'flat','variable','nonzero-tail'})
        for c in cases:
            row=next(v for v in self.catalogue['children'] if v['sha256']==c['child_sha256'])
            raw=self.raw(row);meta,decoded=d.motion(raw)
            actual,used,steps=d.execute_decoder_loop(self.elf,raw[meta['compressed_offset']:])
            self.assertEqual(actual,decoded);self.assertEqual(used,meta['compressed_consumed']);self.assertEqual(steps,c['steps'])

    def test_sources_and_instruction_windows_still_bound(self):
        for resource,expected in self.report['source_sha256'].items():self.assertEqual(d.sha(self.resources[resource]),expected)
        for w in self.report['instruction_windows']:self.assertEqual(d.sha(self.elf[w['offset']:w['offset']+w['size']]),w['sha256'])


if __name__=='__main__':unittest.main()
