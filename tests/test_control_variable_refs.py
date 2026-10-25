import copy,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from control_variable_refs import tokenize,verify,ALLOWED,_execute
from dialogue import sha
from dialogue_advanced import SsdIndex
from reinsertion import descriptor,compile_batch,VARIABLE_POLICY,N0_POLICY,RESOURCE
from test_dialogue_advanced import command,ssd


class ReviewedVariables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.elf=(ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes()
    def plan(self,data):
        index=SsdIndex(data)
        return {'schema':1,'policy':VARIABLE_POLICY,'resource':RESOURCE,'source_sha256':sha(data),
            'catalog_version':'v003','entries':[descriptor(data,at,index,named_choices=True,b15=True,
                numeric1=True,numeric15=True,t0=True,i0=True,n0=True,variable_refs=True) for at in index.records]}
    def test_exact_allowlist_and_suffixes(self):
        self.assertEqual(len(ALLOWED),21)
        for raw in ALLOWED:
            self.assertFalse(tokenize(raw+b'!')[1],raw)
            self.assertTrue(any(p['kind']=='preserved-reviewed-variable-reference' for p in tokenize(raw)[0]))
        for raw in (b'%$0f',b'%$02',b'%$19',b'%I$3',b'%I$01',b'%N$3',b'%N$01',b'%N$7',b'%N-$1',b'%M_1'):
            self.assertTrue(tokenize(raw)[1],raw)
    def test_original_reader_and_handlers_all_cases(self):
        r=verify(self.elf);self.assertEqual(r['case_count'],106)
        for value in (0x7fffffff,0x80000000,0xffffffff):
            result=_execute(self.elf,'decimal',18,value)
            self.assertEqual(result['signed_value'],value if value<0x80000000 else value-0x100000000)
        self.assertEqual(_execute(self.elf,'item',19,1348)['string_pointer'],0x100000+1348*128)
        self.assertEqual(_execute(self.elf,'name',10,65535)['string_pointer'],0x100000+65535*16)
        with self.assertRaises(ValueError):_execute(self.elf,'name',3,1)
    def test_slots_and_named_label_roundtrip(self):
        data=ssd(command(b'2snm',[b'It costs %$18G, okay?',b'Yes\tNo',b'Innkeeper']))
        doc=self.plan(data);self.assertEqual(compile_batch(data,doc,verify_source=False)[0],[])
        doc['entries'][0]['segments'][0]['translation']='Custa %$18G, certo?'
        patches,r=compile_batch(data,doc,verify_source=False);self.assertTrue(r['valid'],r)
        self.assertEqual(len(patches),1);p=patches[0]
        self.assertEqual(len(p['before']),len(p['after']))
        label=doc['entries'][0]['segments'][2]['offset']-p['offset']
        self.assertEqual(p['before'][label:],p['after'][label:])
        self.assertEqual(r['results'][0]['source_offsets'],r['results'][0]['target_offsets'])
    def test_growth_index_and_repack_refused(self):
        data=ssd(command(b'smsg',[b'Price %$2G!',b'Yes\tNo']))
        for target,mode in (('Custa caro %$2G!','slots'),('Valor %$5G!','slots'),('Valor %$2G!','repack')):
            doc=self.plan(data);doc['entries'][0]['mode']=mode
            doc['entries'][0]['segments'][0]['translation']=target
            patches,r=compile_batch(data,doc,verify_source=False)
            self.assertFalse(r['valid'],(target,r));self.assertEqual(patches,[])
    def test_unknown_native_legacy_and_atomic_failure(self):
        data=ssd(command(b'msgb',[b'Price %$2G!'])+command(b'msgb',[b'Hello %N$3!']))
        doc=self.plan(data)
        for e,target in zip(doc['entries'],('Valor %$2G!','Oi %N$3!')):e['segments'][0]['translation']=target
        self.assertFalse(compile_batch(data,doc,verify_source=False)[1]['valid'])
        self.assertEqual(compile_batch(data,doc,verify_source=False)[0],[])
        data=ssd(command(b'msgb',[b'Price %$2G!']));doc=self.plan(data)
        doc['policy']=N0_POLICY;doc['entries'][0]['segments'][0]['translation']='Valor %$2G!'
        self.assertFalse(compile_batch(data,doc,verify_source=False)[1]['valid'])
        data=ssd(command(b'msgb',[b'Hello %I$1 \x82\xa0!']));doc=self.plan(data)
        doc['entries'][0]['segments'][0]['translation']='Oi %I$1 !'
        self.assertFalse(compile_batch(data,doc,verify_source=False)[1]['valid'])
    def test_executable_binding(self):
        modified=bytearray(self.elf);modified[0x1b5dd0]^=1
        with self.assertRaises(ValueError):verify(modified)


if __name__=='__main__':unittest.main()
