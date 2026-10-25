import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from control_dialogue_quirks import tokenize,verify,execute_motion
from interface_text import SOURCE
from dialogue import sha
from dialogue_advanced import SsdIndex
from reinsertion import descriptor,compile_batch,QUIRK_POLICY,SCALED_POLICY,RESOURCE
from test_dialogue_advanced import command,ssd


class DialogueQuirks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.elf=SOURCE.read_bytes()
    def plan(self,data):
        ix=SsdIndex(data)
        return {'schema':1,'policy':QUIRK_POLICY,'resource':RESOURCE,'source_sha256':sha(data),
            'entries':[descriptor(data,at,ix,named_choices=True,b15=True,numeric1=True,numeric15=True,
                t0=True,i0=True,n0=True,variable_refs=True,scaled_refs=True,quirk_refs=True) for at in ix.records]}
    def test_only_observed_whole_lexemes_allowed(self):
        for raw in (b'%M_1Thanks',b'%M_4there',b'%T0.',b'%NO, hi',b'%500 G',b'%5000 G\tNo',b'%8000 G',b'%1000 G'):
            self.assertFalse(tokenize(raw)[1],raw)
        for raw in (b'%M_2',b'%M_10',b'%T1',b'%T00',b'%NOriginal',b'%600 G',b'%500G',b'%N$3'):
            self.assertTrue(tokenize(raw)[1],raw)
    def test_original_defaults_m_t_n_and_digit_dispatch(self):
        e=verify(self.elf);self.assertTrue(e['original_typos_preserved'])
        self.assertEqual([r['packed_value'] for r in e['motion_cases']],[1,4])
        self.assertEqual(e['omitted_name_argument']['consumed_after_percent'],1)
        self.assertEqual(len(e['literal_title_cases']),4)
        self.assertTrue(all(r['consumes_percent_and_first_digit'] for r in e['percent_digit_default_cases']))
        with self.assertRaises(ValueError):execute_motion(self.elf,2)
    def test_slots_legacy_stays_blocked_and_no_source_bug_repair(self):
        data=ssd(command(b'smsg',[b'Buy a map?',b'Map: %500 G\tNo thanks.']))
        d=self.plan(data);d['entries'][0]['segments'][0]['translation']='Quer mapa?'
        ps,r=compile_batch(data,d,verify_source=False);self.assertTrue(r['valid'],r);self.assertEqual(len(ps),1)
        d['policy']=SCALED_POLICY;self.assertFalse(compile_batch(data,d,verify_source=False)[1]['valid'])
        d=self.plan(data);d['entries'][0]['segments'][1]['translation']='Mapa: 500 G\tPasso.'
        self.assertFalse(compile_batch(data,d,verify_source=False)[1]['valid'])
    def test_control_changes_growth_repack_and_unknown_mixture_refused_atomically(self):
        data=ssd(command(b'smsg',[b'Hello %NO, are you okay?',b'Yes\tNo']))
        for target,mode in (('Oi %N0, tudo bem?','slots'),('Oi %NO, tudo bem com voce mesmo?','slots'),('Oi %NO, tudo bem?','repack')):
            d=self.plan(data);e=d['entries'][0];e['mode']=mode;e['segments'][0]['translation']=target
            ps,r=compile_batch(data,d,verify_source=False);self.assertFalse(r['valid'],(target,r));self.assertEqual(ps,[])
        data=ssd(command(b'msgb',[b'Hello %NO, okay?'])+command(b'msgb',[b'Hello %M_2!']))
        d=self.plan(data)
        for e in d['entries']:e['segments'][0]['translation']=e['segments'][0]['source'].replace('Hello','Oi')
        self.assertEqual(compile_batch(data,d,verify_source=False)[0],[])
    def test_executable_drift_refused(self):
        changed=bytearray(self.elf);changed[0x33dd60+(ord('5')-0x24)*4]^=1
        with self.assertRaises(ValueError):verify(changed)


if __name__=='__main__':unittest.main()
