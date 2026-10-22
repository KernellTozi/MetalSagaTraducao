import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import development_iso as dev
from dialogue import ROOT


def directory_record(name,lba,size,folder=False):
    n=33+len(name);n+=n%2;r=bytearray(n);r[0]=n
    struct.pack_into('<I',r,2,lba);struct.pack_into('>I',r,6,lba)
    struct.pack_into('<I',r,10,size);struct.pack_into('>I',r,14,size)
    r[25]=2 if folder else 0;struct.pack_into('<H',r,28,1);struct.pack_into('>H',r,30,1)
    r[32]=len(name);r[33:33+len(name)]=name;return bytes(r)


def iso_fixture():
    data=bytearray(32*2048);pvd=bytearray(2048);pvd[:7]=b'\x01CD001\x01'
    struct.pack_into('<H',pvd,128,2048);pvd[156:190]=directory_record(b'\0',20,2048,True)
    data[16*2048:17*2048]=pvd
    for sector,name,child,size,folder in ((20,b'DATA',21,2048,True),(21,b'MAP',22,2048,True),(22,b'MAP.MCT;1',25,128,False)):
        r=directory_record(name,child,size,folder);data[sector*2048:sector*2048+len(r)]=r
    data[25*2048:25*2048+8]=b'Original'
    return bytes(data)


class DevelopmentIsoTests(unittest.TestCase):
    def setUp(self):
        # Fixture initialization must never trigger retention in the real work
        # directory. Retention itself is exercised on a separate temporary root
        # in test_iso_retention.py, not through these miniature ISO fixtures.
        guard=patch('iso_retention.prune',return_value={'delete':[]})
        self.retention=guard.start()
        self.addCleanup(guard.stop)

    def setup_session(self,root):
        original=root/'original.iso';image=root/'development.iso';raw=iso_fixture()
        original.write_bytes(raw);image.write_bytes(raw)
        state={'schema':1,'image':image.relative_to(ROOT).as_posix(),'patches':[],
               'output_iso_sha256':hashlib.sha256(raw).hexdigest(),'generation':0}
        dev.atomic_json(root/'estado.json',state)
        p={'resource':'DATA/MAP/MAP.MCT','offset':25*2048,'before':b'Orig','after':b'Test','id':'fixture'}
        return original,image,p,state

    def test_apply_reapply_and_restore_whole_image(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='iso-test-') as folder:
            root=Path(folder);original,image,p,state=self.setup_session(root)
            with patch.object(dev,'absolute_patches',side_effect=lambda x:x),patch.object(dev,'ORIGINAL_ISO_SHA256',state['output_iso_sha256']):
                r=dev.transact([p],'plan',root,image,original)
                self.assertEqual(image.read_bytes()[25*2048:25*2048+4],b'Test')
                self.assertFalse((root/'transacao.json').exists());self.assertEqual(r['generation'],1)
                second=dev.transact([p],'plan',root,image,original)
                self.assertEqual(second['output_iso_sha256'],r['output_iso_sha256'])
                self.assertTrue(second['idempotent_no_write']);self.assertEqual(second['generation'],r['generation'])
                dev.transact([],'restore',root,image,original)
                self.assertEqual(image.read_bytes(),original.read_bytes())

    def test_interrupt_persistent_journal_and_exact_recovery(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='iso-test-') as folder:
            root=Path(folder);original,image,p,state=self.setup_session(root)
            with patch.object(dev,'absolute_patches',side_effect=lambda x:x),patch.object(dev,'ORIGINAL_ISO_SHA256',state['output_iso_sha256']):
                def stop():raise RuntimeError('Injected interruption')
                with self.assertRaises(RuntimeError):dev.transact([p],'plan',root,image,original,stop)
                self.assertTrue((root/'transacao.json').is_file())
                with self.assertRaises(ValueError):dev.transact([p],'plan',root,image,original)
                # Model a torn write inside an expected range.
                with image.open('r+b') as stream:stream.seek(p['offset']);stream.write(b'XX')
                dev.recover(root,image,original)
                self.assertEqual(image.read_bytes(),original.read_bytes())
                self.assertFalse((root/'transacao.json').exists())

    def test_recovery_refuses_unrelated_damage(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='iso-test-') as folder:
            root=Path(folder);original,image,p,state=self.setup_session(root)
            with patch.object(dev,'absolute_patches',side_effect=lambda x:x),patch.object(dev,'ORIGINAL_ISO_SHA256',state['output_iso_sha256']):
                with self.assertRaises(RuntimeError):
                    dev.transact([p],'plan',root,image,original,lambda:(_ for _ in ()).throw(RuntimeError()))
                with image.open('r+b') as stream:stream.seek(5);stream.write(b'X')
                before=image.read_bytes()
                with self.assertRaises(ValueError):dev.recover(root,image,original)
                self.assertEqual(image.read_bytes(),before)

    def test_unexpected_current_iso_or_patch_baseline_never_written(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='iso-test-') as folder:
            root=Path(folder);original,image,p,state=self.setup_session(root)
            with patch.object(dev,'absolute_patches',side_effect=lambda x:x),patch.object(dev,'ORIGINAL_ISO_SHA256',state['output_iso_sha256']):
                p['before']=b'Fake'
                with self.assertRaises(ValueError):dev.transact([p],'plan',root,image,original)
                self.assertEqual(image.read_bytes(),original.read_bytes())
                self.assertFalse((root/'transacao.json').exists())

    @unittest.skipUnless(os.name=='nt','Windows share-mode semantics')
    def test_windows_reader_blocks_exclusive_update(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='iso-test-') as folder:
            path=Path(folder)/'held.iso';path.write_bytes(b'test')
            with path.open('rb'):
                with self.assertRaises(OSError):
                    with dev.exclusive(path):self.fail('Exclusive open should fail')

    def test_hardlink_to_original_is_refused(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='iso-test-') as folder:
            original=Path(folder)/'original.iso';original.write_bytes(b'test');alias=Path(folder)/'alias.iso'
            os.link(original,alias)
            with patch.object(dev,'ORIGINAL',original):
                with self.assertRaises(ValueError):
                    with dev.exclusive(alias):self.fail('Hardlink must be refused')
            self.assertEqual(original.read_bytes(),b'test')

    def test_initialization_resumes_verified_partial_copy(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='iso-test-') as folder:
            root=Path(folder);original=root/'original.iso';original.write_bytes(iso_fixture())
            image=root/'development.iso';image.with_suffix('.iso.partial').write_bytes(iso_fixture()[:12345])
            digest=hashlib.sha256(iso_fixture()).hexdigest()
            with patch.object(dev,'SESSION',root),patch.object(dev,'IMAGE',image),patch.object(dev,'ORIGINAL',original),patch.object(dev,'ORIGINAL_ISO_SHA256',digest):
                state=dev.initialize()
            self.retention.assert_called_once_with(reserve=1)
            self.assertEqual(image.read_bytes(),original.read_bytes());self.assertEqual(state['generation'],0)

    def test_initialization_refuses_bad_partial_without_writing(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'work',prefix='iso-test-') as folder:
            root=Path(folder);original=root/'original.iso';original.write_bytes(iso_fixture())
            image=root/'development.iso';partial=image.with_suffix('.iso.partial');partial.write_bytes(b'WRONG')
            with patch.object(dev,'SESSION',root),patch.object(dev,'IMAGE',image),patch.object(dev,'ORIGINAL',original):
                with self.assertRaises(ValueError):dev.initialize()
            self.retention.assert_not_called()
            self.assertEqual(partial.read_bytes(),b'WRONG');self.assertFalse(image.exists())


if __name__=='__main__':unittest.main()
