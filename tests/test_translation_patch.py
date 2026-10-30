import hashlib,json,sys,tempfile,unittest,zipfile
from unittest.mock import patch as mock_patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import translation_patch as patch


class TranslationPatchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='patch-tests-',dir=patch.ROOT/'work')
        self.root=Path(self.temp.name).resolve()
        self.assertEqual(self.root.parent,(patch.ROOT/'work').resolve())
        self.source=self.root/'original.iso';self.target=self.root/'traducao.iso'
        self.bundle=self.root/'traducao.mspatch';self.output=self.root/'resultado.iso'
        self.before=bytes(range(256))*40+b'final'
        data=bytearray(self.before);data[3:8]=b'TESTE';data[-3:]=b'fim'
        self.after=bytes(data);self.source.write_bytes(self.before);self.target.write_bytes(self.after)

    def tearDown(self):self.temp.cleanup()

    def create(self):
        return patch.create_patch(self.source,self.target,self.bundle,
                                  expected_source_sha=hashlib.sha256(self.before).hexdigest(),
                                  expected_target_sha=hashlib.sha256(self.after).hexdigest())

    def rewrite(self,change):
        with zipfile.ZipFile(self.bundle) as z:
            m=json.loads(z.read('manifest.json'));delta=z.read('delta.bin')
        m,delta=change(m,delta)
        with zipfile.ZipFile(self.bundle,'w',compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr('manifest.json',json.dumps(m));z.writestr('delta.bin',delta)

    def assert_clean_failure(self):
        with self.assertRaises((ValueError,zipfile.BadZipFile)):
            patch.apply_patch(self.source,self.bundle,self.output)
        self.assertFalse(self.output.exists())
        self.assertFalse(list(self.root.glob('*.partial')))
        self.assertEqual(self.source.read_bytes(),self.before)

    def test_full_roundtrip_and_inputs_unchanged_including_short_last_page(self):
        m=self.create();self.assertEqual(m['records'],2)
        result=patch.apply_patch(self.source,self.bundle,self.output)
        self.assertTrue(result['verified']);self.assertEqual(self.output.read_bytes(),self.after)
        self.assertEqual(self.source.read_bytes(),self.before);self.assertEqual(self.target.read_bytes(),self.after)

    def test_unchanged_images_make_empty_valid_patch(self):
        self.target.write_bytes(self.before);self.after=self.before
        self.assertEqual(self.create()['records'],0)
        patch.apply_patch(self.source,self.bundle,self.output)
        self.assertEqual(self.output.read_bytes(),self.before)

    def test_wrong_original_rejected_before_creating_output(self):
        self.create();self.source.write_bytes(self.after)
        with self.assertRaises(ValueError):patch.apply_patch(self.source,self.bundle,self.output)
        self.assertFalse(self.output.exists());self.assertFalse(list(self.root.glob('*.partial')))
        self.assertEqual(self.source.read_bytes(),self.after)

    def test_publication_guard_failure_keeps_source_and_cleans_result(self):
        self.create();calls=[]
        def refuse():
            calls.append(1);self.assertFalse(self.output.exists())
            raise ValueError('Output policy refused')
        with self.assertRaises(ValueError):patch.apply_patch(self.source,self.bundle,self.output,before_publish=refuse)
        self.assertEqual(calls,[1]);self.assertFalse(self.output.exists())
        self.assertFalse(list(self.root.glob('*.partial')))
        self.assertEqual(self.source.read_bytes(),self.before)

    def test_cli_retention_cannot_delete_an_input_and_never_runs_in_fixture_core(self):
        with mock_patch('iso_retention.plan',return_value={'delete':[{'path':str(self.source)}]}),mock_patch('iso_retention.prune') as prune:
            with self.assertRaises(ValueError):patch.reserve_work_iso(self.source,self.bundle,self.output)
            prune.assert_not_called()

    def test_existing_output_and_input_paths_never_overwritten(self):
        self.create();self.output.write_bytes(b'PRESERVAR')
        with self.assertRaises(ValueError):patch.apply_patch(self.source,self.bundle,self.output)
        self.assertEqual(self.output.read_bytes(),b'PRESERVAR')
        with self.assertRaises(ValueError):patch.apply_patch(self.source,self.bundle,self.source)
        self.assertEqual(self.source.read_bytes(),self.before)

    def test_builder_rejects_wrong_expected_hash_and_cleans_temp(self):
        with self.assertRaises(ValueError):patch.create_patch(self.source,self.target,self.bundle,
            expected_source_sha='0'*64,expected_target_sha='0'*64)
        self.assertFalse(self.bundle.exists());self.assertFalse(list(self.root.glob('*.partial')))

    def test_overlapping_records_rejected_even_with_recomputed_delta_hash(self):
        self.create()
        def change(m,d):
            at=patch.HEADER.size+patch.PAGE;data=bytearray(d)
            patch.HEADER.pack_into(data,at,0,patch.PAGE)
            m['delta_sha256']=hashlib.sha256(data).hexdigest()
            return m,bytes(data)
        self.rewrite(change);self.assert_clean_failure()

    def test_unaligned_offset_refused(self):
        self.create()
        def change(m,d):
            data=bytearray(d);patch.HEADER.pack_into(data,0,1,patch.PAGE)
            m['delta_sha256']=hashlib.sha256(data).hexdigest();return m,bytes(data)
        self.rewrite(change);self.assert_clean_failure()

    def test_changed_payload_rejected_and_incomplete_result_removed(self):
        self.create()
        def change(m,d):
            data=bytearray(d);data[patch.HEADER.size+10]^=1;return m,bytes(data)
        self.rewrite(change);self.assert_clean_failure()

    def test_target_hash_checked_even_when_delta_hash_matches(self):
        self.create()
        def change(m,d):m['target_sha256']='0'*64;return m,d
        self.rewrite(change);self.assert_clean_failure()

    def test_truncated_delta_refused(self):
        self.create()
        def change(m,d):return m,d[:-1]
        self.rewrite(change);self.assert_clean_failure()

    def test_outside_image_offset_refused(self):
        self.create()
        def change(m,d):
            data=bytearray(d);patch.HEADER.pack_into(data,0,patch.PAGE*10,patch.PAGE)
            m['delta_sha256']=hashlib.sha256(data).hexdigest();return m,bytes(data)
        self.rewrite(change);self.assert_clean_failure()

    def test_excess_delta_bytes_refused(self):
        self.create()
        self.rewrite(lambda m,d:(m,d+b'extra'))
        self.assert_clean_failure()

    def test_boolean_count_is_not_an_integer_record_count(self):
        self.create()
        def change(m,d):m['records']=True;return m,d
        self.rewrite(change);self.assert_clean_failure()

    def test_archive_paths_are_never_extracted(self):
        self.create()
        with zipfile.ZipFile(self.bundle,'a') as z:z.writestr('../escape.txt','nada')
        self.assert_clean_failure();self.assertFalse((self.root.parent/'escape.txt').exists())

    def test_duplicate_json_fields_and_boolean_counts_refused(self):
        self.create()
        with zipfile.ZipFile(self.bundle,'r') as z:m=z.read('manifest.json');d=z.read('delta.bin')
        with zipfile.ZipFile(self.bundle,'w') as z:
            z.writestr('manifest.json',m[:-2]+b',"records":true}\n');z.writestr('delta.bin',d)
        self.assert_clean_failure()


if __name__=='__main__':unittest.main()
