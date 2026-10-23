import stat
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import archive_alpha
from iso_retention import plan


@unittest.skipUnless(archive_alpha.TARGET.exists(),'Archived alpha not present in this checkout')
class AlphaTests(unittest.TestCase):
    def test_archived_alpha_has_bound_hash_and_read_only_copy(self):
        self.assertEqual(archive_alpha.checksum(archive_alpha.TARGET),archive_alpha.EXPECTED)
        self.assertFalse(archive_alpha.TARGET.stat().st_mode&stat.S_IWRITE)
        self.assertEqual(archive_alpha.TARGET.stat().st_nlink,1)
        self.assertFalse(archive_alpha.TARGET.is_relative_to(ROOT/'work'))

    def test_retention_refuses_alpha_directory(self):
        with self.assertRaises(ValueError):plan(archive_alpha.TARGET.parent)

    def test_archive_refuses_to_replace_existing_snapshot(self):
        with self.assertRaisesRegex(ValueError,'never replace'):archive_alpha.main()


if __name__=='__main__':unittest.main()
