import hashlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import verify_test_iso as v

class Preflight(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-preflight-')
        self.folder=Path(self.tmp.name);self.image=self.folder/'MetalSaga-ptbr-fixture.iso'
        self.image.write_bytes(b'isolated tiny integrity fixture')
        self.report={'valid':True,'iso':{'image_name':self.image.name,'iso_size':self.image.stat().st_size,
            'output_iso_sha256':hashlib.sha256(self.image.read_bytes()).hexdigest(),
            'all_bytes_match_expected_patch':True,'iso_directory_identical':True}}
        self.save()
    def save(self):(self.folder/'relatorio.json').write_text(json.dumps(self.report),encoding='utf-8')
    def tearDown(self):self.tmp.cleanup()
    def test_completed_image_passes_without_writes(self):
        before=self.image.read_bytes();self.assertTrue(v.verify_image(self.image)['verified']);self.assertEqual(self.image.read_bytes(),before)
    def test_single_bit_and_size_corruption_rejected(self):
        original=self.image.read_bytes()
        for data in (bytes([original[0]^32])+original[1:],original[:-1],original+b'x'):
            self.image.write_bytes(data)
            with self.assertRaises(ValueError):v.verify_image(self.image)
    def test_partial_and_transaction_rejected(self):
        for name in ('transacao.json','fixture.partial'):
            p=self.folder/name;p.write_text('{}')
            with self.assertRaises(ValueError):v.verify_image(self.image)
            p.unlink()
    def test_unbound_or_incomplete_manifests_rejected(self):
        for key,value in (('image_name','other.iso'),('all_bytes_match_expected_patch',False),('iso_directory_identical',False),('iso_size',True),('output_iso_sha256','wrong')):
            original=self.report['iso'][key];self.report['iso'][key]=value;self.save()
            with self.assertRaises(ValueError):v.verify_image(self.image)
            self.report['iso'][key]=original
        self.report['valid']=False;self.save()
        with self.assertRaises(ValueError):v.verify_image(self.image)
    def test_manifest_change_during_read_rejected(self):
        original=v._hash_stream
        def changed(stream):
            digest=original(stream);self.report['valid']=False;self.save();return digest
        with patch.object(v,'_hash_stream',side_effect=changed),self.assertRaises(ValueError):v.verify_image(self.image)
    def test_missing_report_and_outside_workspace_refused(self):
        (self.folder/'relatorio.json').unlink()
        with self.assertRaises(FileNotFoundError):v.verify_image(self.image)
        with self.assertRaises(ValueError):v.verify_image(ROOT/'JOGO/Metal Saga.iso')
    def test_launcher_cannot_start_a_corrupted_image(self):
        import start_test
        (self.folder/'pcsx2-qt.exe').write_bytes(b'fixture, never executed')
        (self.folder/'portable.txt').write_text('')
        data=self.image.read_bytes();self.image.write_bytes(bytes([data[0]^1])+data[1:])
        with patch.object(start_test,'BASE',self.folder),patch.dict(start_test.ISOS,{'fixture':self.image}),patch.object(sys,'argv',['start_test.py','--iso','fixture']),patch.object(start_test.subprocess,'Popen') as launch:
            with self.assertRaisesRegex(ValueError,'Hash da ISO'):start_test.main()
            launch.assert_not_called()

if __name__=='__main__':unittest.main()
