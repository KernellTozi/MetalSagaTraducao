import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from interface_texture_pack import export,import_pack,replace_indices,unpack_indices,records,pillow
from interface_textures import inspect_texture


class PackTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-texture-pack-')
        self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()

    def test_six_pngs_exact_binary_roundtrip(self):
        manifest=export(self.root/'pack');report=import_pack(self.root/'pack',self.root/'out')
        self.assertEqual(len(manifest['entries']),6)
        self.assertTrue(all(r['changed_bytes']==0 and r['reverse_roundtrip'] for r in report['records']))
        for r in report['resources']:
            self.assertEqual((self.root/'out'/Path(r['resource']).name).read_bytes(),(ROOT/'JOGO/Metal Saga'/r['resource']).read_bytes())

    def test_single_pixel_edit_changes_only_index_byte(self):
        manifest=export(self.root/'pack');row=manifest['entries'][0];path=self.root/'pack'/row['png'];Image=pillow()
        with Image.open(path) as image:
            image.load();alpha=image.info['transparency'];old=image.getpixel((0,0));image.putpixel((0,0),(old+1)%256)
            image.save(path,transparency=alpha)
        report=import_pack(self.root/'pack',self.root/'out')
        self.assertEqual(sum(r['changed_bytes'] for r in report['records']),1)
        source=(ROOT/'JOGO/Metal Saga'/row['resource']).read_bytes();after=(self.root/'out'/Path(row['resource']).name).read_bytes()
        self.assertEqual([i for i,(a,b) in enumerate(zip(source,after)) if a!=b],
                         [row['offset']+row['texture']['pixel_offset']])

    def test_palette_alpha_dimensions_mode_manifest_rejected_before_output(self):
        for case in ('rgb','alpha','size','mode','manifest'):
            pack=self.root/case;manifest=export(pack);path=pack/manifest['entries'][0]['png'];Image=pillow()
            with Image.open(path) as im:
                im.load();alpha=im.info['transparency']
                if case=='rgb':
                    palette=im.getpalette();palette[0]^=1;im.putpalette(palette)
                elif case=='alpha':alpha=bytes([alpha[0]^1])+alpha[1:]
                elif case=='size':im=im.crop((0,0,128,128))
                elif case=='mode':im=im.convert('RGB')
                if case!='mode':im.save(path,transparency=alpha)
                else:im.save(path)
            if case=='manifest':
                manifest['entries'][0]['offset']+=1;(pack/'manifest.json').write_text(json.dumps(manifest))
            with self.subTest(case=case),self.assertRaises(ValueError):import_pack(pack,self.root/('out-'+case))
            self.assertFalse((self.root/('out-'+case)).exists())

    def test_odd_4bit_unused_nibble_and_opaque_tail_preserved(self):
        record=struct.pack('<HHIII',3,1,4,16,80)+bytes(64)+bytes((0x21,0xf3))+b'opaque-tail'
        meta,_=inspect_texture(record)
        self.assertEqual(unpack_indices(record,meta),bytes((1,2,3)))
        after=replace_indices(record,bytes((4,5,6)))
        self.assertEqual(after[80:82],bytes((0x54,0xf6)));self.assertEqual(after[82:],b'opaque-tail')
        self.assertEqual(after[:80],record[:80])
        for indices in (bytes((1,2)),bytes((1,2,16))):
            with self.assertRaises(ValueError):replace_indices(record,indices)


if __name__=='__main__':unittest.main()
