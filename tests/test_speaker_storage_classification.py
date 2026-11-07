import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import classify_speaker_storage as storage


class StorageTests(unittest.TestCase):
    def test_all_twelve_consumers_and_six_arguments(self):
        proof=storage.classify(storage.SOURCE.read_bytes())
        self.assertEqual(len(proof['references']),12)
        self.assertEqual(proof['bounded_range_argument_proofs'],6)
        self.assertFalse(proof['can_apply_to_iso']);self.assertFalse(proof['originals_modified'])

    def test_altered_source_refused(self):
        source=bytearray(storage.SOURCE.read_bytes());source[0x180ed8]^=1
        with self.assertRaises(ValueError):storage.classify(bytes(source))

    def test_changed_range_argument_refused(self):
        source=bytearray(storage.SOURCE.read_bytes());source[0x19d56c]^=4
        with self.assertRaises(ValueError):storage.range_lower_bound(source,0x19d564,0x19d588)


if __name__=='__main__':unittest.main()
