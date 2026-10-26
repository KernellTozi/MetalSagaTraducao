import copy,json,random,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import credits_edit_pack as credits
import paint_button_pack as buttons
import interface_atlas_pack as atlases
from interface_texture_pack import pillow


class CreditsPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.elf,cls.raw,cls.meta,cls.cat=credits.original()
        cls.draft=credits.template(cls.elf,cls.raw,cls.meta,cls.cat)

    def rebuild(self,draft):return credits.rebuild(self.elf,self.raw,self.meta,self.cat,draft)

    def test_deterministic_compressor_interoperates_with_original_decoder_on_real_credits(self):
        decoded=bytes.fromhex(self.cat['decoded_hex']);encoded=credits.compress(decoded)
        self.assertEqual(encoded,credits.compress(decoded))
        self.assertLessEqual(len(encoded),4096)
        actual,consumed,_=credits.execute_decoder_loop(self.elf,encoded)
        self.assertEqual(actual,decoded);self.assertEqual(consumed,len(encoded))

    def test_initial_zeros_overlap_wrap_flags_and_random_binary_interoperability(self):
        rng=random.Random(381)
        for data in (b'',b'ABC',bytes(80),b'A'*2100,bytes(range(256))*5,bytes(rng.randrange(256) for _ in range(1500)),b'ABCD'*270):
            encoded=credits.compress(data);actual,consumed,_=credits.decode(encoded)
            self.assertEqual(actual,data);self.assertEqual(consumed,len(encoded))
            if data:self.assertEqual(credits.execute_decoder_loop(self.elf,encoded)[0],data)
        self.assertEqual(credits.compress(b'ABC')[4:],b'\x07ABC')
        with self.assertRaises(ValueError):credits.compress(b'ABC',maximum=2)

    def test_unedited_pack_preserves_original_compressed_resource_exactly(self):
        after,r=self.rebuild(self.draft)
        self.assertEqual(after,self.raw);self.assertEqual(r['changed_line_count'],0)
        self.assertEqual(r['editable_line_count'],51)

    def test_synthetic_role_edit_preserves_every_other_line_prefix_and_extent(self):
        draft=copy.deepcopy(self.draft);draft['rows'][3]['translation']='Teste á ç'
        after,report=self.rebuild(draft)
        self.assertEqual(report['changed_rows'],['credits.line.0003'])
        self.assertEqual(after[:0x800],self.raw[:0x800]);self.assertEqual(after[0x1800:],self.raw[0x1800:])
        decoded=credits.decode(after[0x800:0x1800])[0];rows=decoded[4:-2].split(b'\r\n')
        for i,row in enumerate(rows):
            expected=b'\x81\x9f'+credits.encode('Teste á ç') if i==3 else bytes.fromhex(self.cat['rows'][i]['source_hex'])
            self.assertEqual(row,expected)

    def test_staff_companies_order_metadata_and_count_are_immutable(self):
        for index in (0,1,4,276):
            draft=copy.deepcopy(self.draft);draft['rows'][index]['translation']='TEST'
            with self.assertRaises(ValueError):self.rebuild(draft)
        for change in ('order','hash','prefix','count','profile'):
            draft=copy.deepcopy(self.draft)
            if change=='order':draft['rows'][3],draft['rows'][6]=draft['rows'][6],draft['rows'][3]
            elif change=='hash':draft['source_sha256']='0'*64
            elif change=='prefix':draft['rows'][3]['immutable_prefix_hex']=''
            elif change=='count':draft['rows'].pop()
            else:draft['maximum_line_bytes']=100
            with self.assertRaises(ValueError):self.rebuild(draft)

    def test_line_total_compressed_budgets_controls_and_company_fact(self):
        for value in ('A'*34,'#12','A\nB','A|B','A%02d','A\0B',' ','Ω'):
            draft=copy.deepcopy(self.draft);draft['rows'][3]['translation']=value
            with self.assertRaises(ValueError):self.rebuild(draft)
        draft=copy.deepcopy(self.draft);draft['rows'][286]['translation']='TEST'
        with self.assertRaises(ValueError):self.rebuild(draft)
        draft=copy.deepcopy(self.draft)
        for row in draft['rows']:
            if row['kind']=='role-heading':row['translation']='A'*33
        with self.assertRaisesRegex(ValueError,'total'):self.rebuild(draft)
        draft=copy.deepcopy(self.draft);draft['rows'][3]['translation']='TEST'
        with patch.object(credits,'compress',return_value=b'A'*4097),self.assertRaisesRegex(ValueError,'slot'):
            self.rebuild(draft)


class GraphicPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-edit-prep-')
        self.root=Path(self.temp.name)

    def tearDown(self):self.temp.cleanup()

    def change_pixel(self,path):
        Image=pillow()
        with Image.open(path) as im:
            im.load();alpha=im.info['transparency'];im.putpixel((0,0),(im.getpixel((0,0))+1)%256)
            im.save(path,transparency=alpha,bits=8)

    def test_twelve_paint_crops_exact_resource_roundtrip_and_two_protected(self):
        manifest=buttons.export(self.root/'pack')
        self.assertEqual(len(manifest['entries']),12)
        self.assertEqual(sum(not r['editable'] for r in manifest['entries']),2)
        report=buttons.import_pack(self.root/'pack',self.root/'out')
        self.assertEqual(report['source_sha256'],report['output_sha256'])
        self.assertEqual((self.root/'out/S_PAINT.SDA').read_bytes(),buttons.inventory()[0])

    def test_one_crop_pixel_is_only_changed_byte_in_complete_paint_resource(self):
        manifest=buttons.export(self.root/'pack');row=manifest['entries'][0]
        self.change_pixel(self.root/'pack'/row['png'])
        buttons.import_pack(self.root/'pack',self.root/'out')
        actual=(self.root/'out/S_PAINT.SDA').read_bytes();source=buttons.inventory()[0]
        self.assertEqual([i for i,(a,b) in enumerate(zip(source,actual)) if a!=b],
            [row['texture_offset']+row['texture']['pixel_offset']])

    def test_protected_crop_manifest_palette_and_dimensions_refused_without_output(self):
        for case in ('protected','manifest','palette','size'):
            pack=self.root/case;manifest=buttons.export(pack)
            row=next(r for r in manifest['entries'] if not r['editable']) if case=='protected' else manifest['entries'][-1]
            path=pack/row['png']
            if case=='protected':self.change_pixel(path)
            elif case=='manifest':
                manifest['entries'][-1]['rect'][0]+=1
                (pack/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
            else:
                Image=pillow()
                with Image.open(path) as im:
                    im.load();alpha=im.info['transparency']
                    if case=='palette':
                        palette=im.getpalette();palette[0]^=1;im.putpalette(palette)
                    else:im=im.crop((0,0,1,1))
                    im.save(path,transparency=alpha,bits=8)
            out=self.root/('out-'+case)
            with self.assertRaises(ValueError):buttons.import_pack(pack,out)
            self.assertFalse(out.exists())

    def test_all_119_remaining_atlases_and_14_resources_exact_roundtrip(self):
        manifest=atlases.export(self.root/'pack',atlases.REMAINING_POLICY)
        self.assertEqual(len(manifest['entries']),119)
        report=atlases.import_pack(self.root/'pack',self.root/'out')
        self.assertEqual(len(report['resources']),14)
        self.assertTrue(all(r['changed_bytes']==0 for r in report['records']))
        for row in report['resources']:
            self.assertEqual(row['sha256'],row['source_sha256'])

    def test_visual_triage_classifies_each_known_texture_once_and_retains_unknowns(self):
        from triage_graphic_pack import REVIEW
        report=json.loads((ROOT/'reports/triagem-grafica-v001.json').read_text(encoding='utf-8'))
        self.assertEqual(report['recognized_textures'],119)
        self.assertEqual(sum(report['classes'].values()),119)
        self.assertEqual(len({r['id'] for r in report['records']}),119)
        self.assertEqual(report['unresolved_structure_records'],365)
        self.assertEqual(report['classes']['candidate-latin-interface'],18)
        self.assertEqual(sum(len(v) for v in REVIEW['candidate-latin-interface'].values()),18)
        self.assertFalse(report['runtime_and_complete_game_coverage_proven'])


if __name__=='__main__':unittest.main()
