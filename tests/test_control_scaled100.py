import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from control_scaled100 import tokenize,execute,verify,TOKENS
from dialogue import sha
from dialogue_advanced import SsdIndex
from reinsertion import descriptor,compile_batch,SCALED_POLICY,VARIABLE_POLICY,RESOURCE
from test_dialogue_advanced import command,ssd


class Scaled100(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.elf=(ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes()
    def plan(self,data):
        ix=SsdIndex(data)
        return {'schema':1,'policy':SCALED_POLICY,'resource':RESOURCE,'source_sha256':sha(data),
            'entries':[descriptor(data,at,ix,named_choices=True,b15=True,numeric1=True,numeric15=True,
                t0=True,i0=True,n0=True,variable_refs=True,scaled_refs=True) for at in ix.records]}
    def test_complete_scaled_tokens_preserved_as_one_control(self):
        for raw in TOKENS:
            parts,opaque=tokenize(raw+b' tons.');self.assertFalse(opaque)
            self.assertEqual(bytes.fromhex(parts[0]['hex']),raw)
            self.assertEqual(parts[0]['kind'],'preserved-scaled100-reference')
        for raw in (b'%$1f100',b'%$2f10',b'%$2f1000',b'%$02f100',b'%$2f$0',b'%$2f100tons',b'%$2f0'):
            self.assertTrue(tokenize(raw)[1],raw)
    def test_original_reader_two_arguments_and_fp_forwarding(self):
        evidence=verify(self.elf);self.assertEqual(evidence['case_count'],24)
        for token in TOKENS:
            for value,want in ((0,0),(100,1),(12345,123.45),(0xffffffff,-.01)):
                r=execute(self.elf,token,value);self.assertAlmostEqual(r['ratio_f32'],want,places=4)
                self.assertEqual(r['consumed_after_percent'],len(token)-1)
                self.assertEqual(r['divisor'],100);self.assertEqual(r['format_offset'],0x349db8)
        with self.assertRaises(ValueError):execute(self.elf,b'%$3f100',100)
    def test_slots_roundtrip_and_legacy_remains_blocked(self):
        data=ssd(command(b'msgb',[b'Need %$2f100 tons of scrap.']))
        doc=self.plan(data);self.assertEqual(compile_batch(data,doc,verify_source=False)[0],[])
        doc['entries'][0]['segments'][0]['translation']='Pede %$2f100 t de sucata.'
        ps,r=compile_batch(data,doc,verify_source=False);self.assertTrue(r['valid'],r)
        self.assertEqual(len(ps),1);self.assertEqual(len(ps[0]['before']),len(ps[0]['after']))
        doc['policy']=VARIABLE_POLICY;self.assertFalse(compile_batch(data,doc,verify_source=False)[1]['valid'])
    def test_token_index_divisor_growth_and_repack_refused(self):
        data=ssd(command(b'smsg',[b'Need %$2f100 tons.',b'Yes\tNo']))
        for target,mode in (('Pede %$0f100 t.','slots'),('Pede %$2f10 t.','slots'),
            ('Pede muito %$2f100 t.','slots'),('Pede %$2f100 t.','repack')):
            doc=self.plan(data);e=doc['entries'][0];e['mode']=mode;e['segments'][0]['translation']=target
            ps,r=compile_batch(data,doc,verify_source=False);self.assertFalse(r['valid'],(target,r));self.assertEqual(ps,[])
    def test_unknown_mixture_atomic_and_empty_prefix_preserved(self):
        data=ssd(command(b'msgb',[b'Need %$2f100 tons.'])+command(b'msgb',[b'Need %$2f10 tons.']))
        doc=self.plan(data)
        for e in doc['entries']:e['segments'][0]['translation']=e['segments'][0]['source'].replace('Need','Pede')
        ps,r=compile_batch(data,doc,verify_source=False);self.assertFalse(r['valid']);self.assertEqual(ps,[])
        data=ssd(command(b'msgb',[b'%$2f100 tons needed.']));doc=self.plan(data)
        doc['entries'][0]['segments'][0]['translation']='Pede %$2f100 t.'
        self.assertFalse(compile_batch(data,doc,verify_source=False)[1]['valid'])
    def test_code_and_format_changes_refused(self):
        for at in (0x1b5e14,0x1b5e38,0x1b5e44,0x349db8):
            modified=bytearray(self.elf);modified[at]^=1
            with self.subTest(at=at),self.assertRaises(ValueError):verify(modified)


if __name__=='__main__':unittest.main()
