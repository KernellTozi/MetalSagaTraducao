import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from copy_onedrive import deliver,checksum,FILENAME


class CopyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-delivery-')
        self.root=Path(self.temp.name);self.build=self.root/'build';self.build.mkdir()
        self.dest=self.root/'destination';self.dest.mkdir()
        self.source=self.build/'MetalSaga-ptbr-fixture.iso';self.source.write_bytes(b'isolated fixture only')
        self.report={'valid':True,'iso':{'image_name':self.source.name,'iso_size':self.source.stat().st_size,
            'output_iso_sha256':checksum(self.source),'all_bytes_match_expected_patch':True,'iso_directory_identical':True}}
        self.write_report()
    def write_report(self):(self.build/'relatorio.json').write_text(json.dumps(self.report),encoding='utf-8')
    def tearDown(self):self.temp.cleanup()
    def test_verified_copy_replaces_only_named_file_and_preserves_source(self):
        (self.dest/FILENAME).write_bytes(b'old');(self.dest/'other.txt').write_text('keep')
        result=deliver(self.build,self.dest)
        self.assertTrue(result['local_copy_verified']);self.assertFalse(result['cloud_sync_confirmed'])
        self.assertEqual((self.dest/FILENAME).read_bytes(),self.source.read_bytes())
        self.assertEqual((self.dest/'other.txt').read_text(),'keep')
    def test_corruption_incomplete_build_and_journal_preserve_previous_copy(self):
        for case in ('hash','invalid','journal','partial'):
            with self.subTest(case=case):
                (self.dest/FILENAME).write_bytes(b'previous')
                self.report['valid']=case!='invalid';self.report['iso']['output_iso_sha256']=checksum(self.source) if case!='hash' else '0'*64
                self.write_report()
                extra=self.build/('transacao.json' if case=='journal' else 'anything.partial')
                if case in ('journal','partial'):extra.write_bytes(b'pending')
                try:
                    with self.assertRaises(ValueError):deliver(self.build,self.dest)
                    self.assertEqual((self.dest/FILENAME).read_bytes(),b'previous')
                finally:
                    if extra.exists():extra.unlink()
    def test_interrupted_copy_preserves_previous_copy(self):
        (self.dest/FILENAME).write_bytes(b'previous')
        with patch('copy_onedrive.os.replace',side_effect=OSError('fixture interruption')):
            with self.assertRaises(OSError):deliver(self.build,self.dest)
        self.assertEqual((self.dest/FILENAME).read_bytes(),b'previous')
        self.assertFalse(list(self.dest.glob('*.partial')))


if __name__=='__main__':unittest.main()
