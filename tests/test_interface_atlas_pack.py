import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from explore_interface_atlases import classify, inspect
from interface_atlas_pack import export, import_pack, sources
from interface_texture_pack import pillow


class AtlasTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT/'work', prefix='test-ui-atlas-')
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_all_69_textures_and_five_resources_exact_roundtrip(self):
        draft = export(self.root/'pack')
        self.assertEqual(len(draft['entries']), 69)
        self.assertEqual({r['texture']['bpp'] for r in draft['entries']}, {4, 8})
        report = import_pack(self.root/'pack', self.root/'out')
        self.assertTrue(all(r['changed_bytes'] == 0 and r['reverse_roundtrip'] for r in report['records']))
        self.assertEqual(len(report['resources']), 5)
        for resource, raw in sources().items():
            self.assertEqual((self.root/'out'/Path(resource).name).read_bytes(), raw)
        self.assertFalse(report['iso_modified'])

    def test_one_pixel_4_and_8_bit_preserves_every_other_byte(self):
        Image = pillow()
        for bpp in (4, 8):
            pack = self.root/f'pack{bpp}'
            draft = export(pack)
            row = next(r for r in draft['entries'] if r['texture']['bpp'] == bpp)
            path = pack/row['png']
            with Image.open(path) as image:
                image.load()
                alpha = image.info['transparency']
                image.putpixel((1, 0), (image.getpixel((1, 0))+1) % (1 << bpp))
                image.save(path, transparency=alpha, bits=bpp)
            out = self.root/f'out{bpp}'
            report = import_pack(pack, out)
            self.assertEqual(sum(r['changed_bytes'] for r in report['records']), 1)
            for resource, raw in sources().items():
                actual = (out/Path(resource).name).read_bytes()
                differences = [i for i, (a, b) in enumerate(zip(raw, actual)) if a != b]
                expected = [row['offset']+row['texture']['pixel_offset']+(1 if bpp == 8 else 0)] if resource == row['resource'] else []
                self.assertEqual(differences, expected)

    def test_invalid_last_asset_rejected_without_partial_output(self):
        Image = pillow()
        for case in ('rgb', 'alpha', 'mode', 'size', 'indices', 'manifest', 'missing'):
            pack = self.root/case
            draft = export(pack)
            row = next(r for r in reversed(draft['entries']) if r['texture']['bpp'] == 4) if case == 'indices' else draft['entries'][-1]
            path = pack/row['png']
            with Image.open(path) as image:
                image.load()
                alpha = image.info['transparency']
                if case == 'rgb':
                    palette = image.getpalette()
                    palette[0] ^= 1
                    image.putpalette(palette)
                elif case == 'alpha':
                    alpha = bytes([alpha[0] ^ 1])+alpha[1:]
                elif case == 'mode':
                    image = image.convert('RGB')
                elif case == 'size':
                    image = image.crop((0, 0, 2, 2))
                elif case == 'indices':
                    # Force an illegal index for a 4-bit resource in
                    # an 8-bit PNG without modifying the first 16 palette entries.
                    self.assertEqual(row['texture']['bpp'], 4)
                    palette = image.getpalette()
                    image.putpalette(palette+([0]*(768-len(palette))))
                    image.putpixel((0, 0), 16)
                image.save(path, **({'transparency': alpha, 'bits': 8} if case != 'mode' else {}))
            if case == 'manifest':
                draft['entries'][-1]['offset'] += 1
                (pack/'manifest.json').write_text(json.dumps(draft), encoding='utf-8')
            if case == 'missing':
                path.unlink()
            out = self.root/('out-'+case)
            with self.subTest(case=case), self.assertRaises((ValueError, FileNotFoundError)):
                import_pack(pack, out)
            self.assertFalse(out.exists())

    def test_unknown_and_invalid_structures_remain_unknown(self):
        for raw in (b'', b'unknown'*8, b'ganm'+bytes(20),
                    struct.pack('<4sIII', b'ganm', 100, 16, 1616)):
            self.assertEqual(classify(raw)['kind'], 'unknown')
        self.assertEqual(classify(struct.pack('<4sIII8h', b'ganm', 1, 16, 32, *([0]*8)))['kind'], 'ganm')
        self.assertEqual(inspect(b'not a container'), [])

    def test_title_sprite_bounds_are_geometric_evidence_only(self):
        rows = inspect(sources()['DATA/RDATA/RTITLE.SDA'])
        ganm = next(r for r in rows if r['kind'] == 'ganm')
        self.assertEqual(ganm['count'], 6)
        self.assertEqual([r['rect'] for r in ganm['sprites'][:3]],
                         [[0, 0, 180, 24], [0, 24, 180, 48], [0, 48, 180, 72]])
        self.assertEqual(ganm['sprites'][0]['geometric_texture_candidates'], [32])

    def test_existing_output_and_outside_work_rejected(self):
        pack = self.root/'pack'
        export(pack)
        with self.assertRaises(ValueError):
            export(pack)
        with self.assertRaises(ValueError):
            import_pack(pack, ROOT/'translations/atlas-output-forbidden')
        out = self.root/'out'
        out.mkdir()
        sentinel = out/'preservar.txt'
        sentinel.write_text('original')
        with self.assertRaises(ValueError):
            import_pack(pack, out)
        self.assertEqual(sentinel.read_text(), 'original')


if __name__ == '__main__':
    unittest.main()
