import mmap
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from investigate_named_choices import investigate,verify_elf,WORDS,DELTA
from reinsertion import ROOT,SOURCE


class NamedChoiceEvidenceTests(unittest.TestCase):
    def test_real_corpus_keeps_label_and_all_editing_blocked(self):
        elf=(ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes()
        with SOURCE.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
            result=investigate(elf,data)
        self.assertEqual(result['records'],112)
        self.assertEqual(result['by_tag'],{'2snm':29,'smnn':83})
        self.assertEqual(result['without_other_known_blockers'],91)
        self.assertFalse(result['editing_enabled'])
        self.assertFalse(result['repack_enabled'])
        self.assertEqual(len({e['id'] for e in result['entries']}),112)

    def test_different_executable_is_refused(self):
        elf=bytearray((ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes())
        elf[min(WORDS)-DELTA]^=1
        with self.assertRaises(ValueError):verify_elf(elf)
