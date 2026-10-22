import os
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from iso_retention import plan,prune


class RetentionTests(unittest.TestCase):
    def setUp(self):
        (ROOT/'work').mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='test-retention-')
        self.root=Path(self.temp.name).resolve()
        self.assertTrue(self.root.is_relative_to((ROOT/'work').resolve()))

    def tearDown(self):self.temp.cleanup()

    def image(self,index,name=None):
        path=self.root/(name or f'MetalSaga-ptbr-{index}.iso')
        path.write_bytes(b'test-only')
        os.utime(path,(100+index,100+index));return path

    def test_reserve_removes_oldest_generated_only(self):
        files=[self.image(i) for i in range(10)]
        result=prune(self.root,reserve=1,pinned=())
        self.assertEqual(len(result['delete']),1)
        self.assertFalse(files[0].exists())
        self.assertTrue(all(p.exists() for p in files[1:]))

    def test_pinned_and_originals_are_not_candidates(self):
        a=self.image(0);b=self.image(1)
        result=plan(self.root,limit=1,pinned=(a,))
        self.assertEqual(result['delete'][0]['path'],str(b))
        with self.assertRaises(ValueError):plan(ROOT/'JOGO',limit=1)

    def test_unknown_files_cannot_be_deleted(self):
        self.image(0,'personal.iso');self.image(1,'reference.iso')
        with self.assertRaises(ValueError):prune(self.root,limit=1,pinned=())
        self.assertEqual(len(list(self.root.glob('*.iso'))),2)
