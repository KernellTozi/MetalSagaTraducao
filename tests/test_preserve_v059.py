import hashlib
import json
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import preserve_v059 as b


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=b.ROOT/'work');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.value=b'verified test v059'
        self.sha=hashlib.sha256(self.value).hexdigest()
        self.alpha=b'old alpha fixture'.ljust(len(self.value),b'.')
        for name,value in [('ROOT',self.root),('EXPECTED',self.sha),('SIZE',len(self.value)),('ALPHA_SHA',hashlib.sha256(self.alpha).hexdigest())]:
            cm=patch.object(b,name,value);cm.start();self.addCleanup(cm.stop)
        source=self.root/b.SOURCE;source.parent.mkdir(parents=True);source.write_bytes(self.value)
        receipt={'iso':{'image_name':source.name},'valid':True}
        (source.parent/'relatorio.json').write_text(json.dumps(receipt))
        (self.root/'reports').mkdir()
        for v in range(55,59):
            rel=Path(f'work/interface-v{v:03d}/MetalSaga-ptbr-interface-v{v:03d}.iso')
            path=self.root/rel;path.parent.mkdir(parents=True);raw=f'old fixture {v:03d}xx'.encode().ljust(len(self.value),b'.')
            self.assertEqual(len(raw),len(self.value));path.write_bytes(raw)
            h=hashlib.sha256(raw).hexdigest()
            (self.root/f'reports/interface-v{v:03d}.json').write_text(json.dumps({'iso':{'sha256':h}}))
        alpha=self.root/b.OLD_ALPHA;alpha.parent.mkdir(parents=True);alpha.write_bytes(self.alpha);alpha.chmod(stat.S_IREAD)
        def verify(path):
            raw=path.read_bytes()
            if (path.parent/'transacao.json').exists():raise ValueError('Pending fixture transaction')
            return {'path':path.relative_to(self.root).as_posix(),'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'verified':True}
        cm=patch('verify_test_iso.verify_image',side_effect=verify);cm.start();self.addCleanup(cm.stop)

    def test_plan_does_not_copy_or_delete(self):
        r=b.run(False)
        self.assertEqual(len(r['delete_after_verified_copies']),5)
        self.assertTrue((self.root/b.OLD_ALPHA).exists());self.assertFalse((self.root/b.BACKUP).exists())

    def test_copies_verified_before_cleanup_and_other_files_preserved(self):
        original=self.root/'JOGO/original.iso';original.parent.mkdir();original.write_bytes(b'never remove')
        unknown=self.root/'work/unknown.iso';unknown.write_bytes(b'never remove')
        r=b.run(True)
        self.assertEqual(len(r['deleted']),5);self.assertEqual(r['status'],'complete')
        for rel in [b.SOURCE,b.BACKUP,b.WORKING]:self.assertEqual((self.root/rel).read_bytes(),self.value)
        self.assertFalse((self.root/b.BACKUP).stat().st_mode&stat.S_IWRITE)
        self.assertEqual((self.root/b.BACKUP).stat().st_nlink,1)
        self.assertEqual(original.read_bytes(),b'never remove');self.assertEqual(unknown.read_bytes(),b'never remove')
        self.assertFalse((self.root/b.OLD_ALPHA).exists())

    def test_repeat_preserves_cleanup_ledger(self):
        first=b.run(True);second=b.run(True)
        self.assertEqual(second['deleted'],first['deleted']);self.assertEqual(len(second['deleted']),5)

    def test_corrupt_source_refuses_before_copies_or_deletion(self):
        (self.root/b.SOURCE).write_bytes(b'corrupt')
        with self.assertRaises(ValueError):b.run(True)
        self.assertTrue((self.root/b.OLD_ALPHA).exists());self.assertFalse((self.root/b.BACKUP).exists())

    def test_existing_bad_backup_or_pending_destination_prevents_deletion(self):
        target=self.root/b.BACKUP;target.parent.mkdir(parents=True);target.write_bytes(b'wrong')
        with self.assertRaises(ValueError):b.run(True)
        self.assertTrue((self.root/b.OLD_ALPHA).exists())
        target.unlink();(target.parent/'transacao.json').write_text('{}')
        with self.assertRaises(ValueError):b.run(True)
        self.assertTrue((self.root/b.OLD_ALPHA).exists())

    def test_escape_paths_refused(self):
        with self.assertRaises(ValueError):b.safe(Path('../outside.iso'))
        with self.assertRaises(ValueError):b.safe(self.root/'absolute.iso')


if __name__=='__main__':unittest.main()
