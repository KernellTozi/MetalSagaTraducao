import copy
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from control_b15 import tokenize,verify,execute_argument
from dialogue_formats import tokens
from dialogue import sha
from dialogue_advanced import SsdIndex
from reinsertion import descriptor,compile_batch,B15_POLICY,NAMED_POLICY,RESOURCE
from test_dialogue_advanced import command,ssd


class B15Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.elf=(ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes()

    def plan(self,data):
        index=SsdIndex(data)
        return {'schema':1,'policy':B15_POLICY,'resource':RESOURCE,'source_sha256':sha(data),'catalog_version':'v003',
            'entries':[descriptor(data,at,index,named_choices=True,b15=True) for at in index.records]}

    def test_original_argument_reader_variable_index_sign_and_suffix(self):
        variables=list(range(160));variables[15]=321
        for raw,n,value,reads in ((b'$15!\0',3,321,[15]),(b'-$15F\0',4,-321,[15]),(b'15X\0',2,15,[]),
                                  (b'$150.\0',4,150,[150]),(b'_1\0',0,0,[])):
            self.assertEqual(execute_argument(self.elf,raw,variables),{'consumed':n,'value':value&0xffffffff,'variable_indices':reads})

    def test_only_exact_b15_promoted_legacy_unchanged(self):
        for raw in (b'%B$15',b'Hi %B$15!'):
            self.assertTrue(tokens(raw)[1]);self.assertFalse(tokenize(raw)[1])
        for raw in (b'%B$150',b'%B$14',b'%B15',b'%B-$15',b'%N$15',b'%$',b'%M_1'):
            self.assertTrue(tokenize(raw)[1],raw)

    def test_slots_roundtrip_preserves_reference_and_noop(self):
        data=ssd(command(b'msgb',[b'Hi there %B$15!']))
        doc=self.plan(data)
        self.assertEqual(compile_batch(data,doc,verify_source=False)[0],[])
        doc['entries'][0]['segments'][0]['translation']='Oi, %B$15!'
        patches,r=compile_batch(data,doc,verify_source=False)
        self.assertTrue(r['valid'],r);self.assertEqual(len(patches),1)
        self.assertEqual(len(patches[0]['before']),len(patches[0]['after']))
        self.assertEqual(r['results'][0]['source_offsets'],r['results'][0]['target_offsets'])
        self.assertIn(b'%B$15',patches[0]['after'])

    def test_growth_reference_change_and_repack_refused(self):
        data=ssd(command(b'smsg',[b'%B$15 hi',b'Yes\tNo']))
        for target,mode in (('%B$15 ola','slots'),('%B$14 hi','slots'),('%B$15 oi','repack')):
            doc=self.plan(data);doc['entries'][0]['mode']=mode
            doc['entries'][0]['segments'][0]['translation']=target
            p,r=compile_batch(data,doc,verify_source=False)
            self.assertFalse(r['valid']);self.assertEqual(p,[])

    def test_other_opaque_controls_and_legacy_still_blocked(self):
        data=ssd(command(b'msgb',[b'%B$15: %$1 is the price']))
        doc=self.plan(data);doc['entries'][0]['segments'][0]['translation']='%B$15: %$1 valor'
        self.assertFalse(compile_batch(data,doc,verify_source=False)[1]['valid'])
        data=ssd(command(b'msgb',[b'Hi there %B$15!']));doc=self.plan(data)
        doc['policy']=NAMED_POLICY;doc['entries'][0]['segments'][0]['translation']='Oi, %B$15!'
        self.assertFalse(compile_batch(data,doc,verify_source=False)[1]['valid'])

    def test_executable_evidence_revision_and_dispatch(self):
        self.assertEqual(verify(self.elf)['variable_index'],15)
        with self.assertRaises(ValueError):verify(self.elf[:-1]+b'X')

if __name__=='__main__':unittest.main()
