import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from control_t0 import tokenize,verify,execute_lookup
from control_b15 import execute_argument
from dialogue_formats import tokens
from dialogue import sha
from dialogue_advanced import SsdIndex
from reinsertion import descriptor,compile_batch,T0_POLICY,NUMERIC15_POLICY,RESOURCE
from test_dialogue_advanced import command,ssd


class T0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.elf=(ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes()

    def plan(self,data):
        index=SsdIndex(data)
        return {'schema':1,'policy':T0_POLICY,'resource':RESOURCE,'source_sha256':sha(data),
            'catalog_version':'v003','entries':[descriptor(data,at,index,named_choices=True,b15=True,numeric1=True,numeric15=True,t0=True)
                                               for at in index.records]}

    def test_exact_token_only_legacy_unchanged(self):
        for raw in (b'%T$0',b'Hi %T$0!',b'%T$0f',b'%B$15 %$1G %$15G %T$0'):
            self.assertFalse(tokenize(raw)[1],raw);self.assertTrue(tokens(raw)[1])
        for raw in (b'%T$00',b'%T$01',b'%T$1',b'%T0',b'%T-$0',b'%t$0',b'%N$3',b'%T$0_1'):
            self.assertTrue(tokenize(raw)[1],raw)

    def test_original_handler_stride_accessors_and_selector(self):
        for index,selector in ((0,0),(2,7),(7,3)):
            result=execute_lookup(self.elf,index,selector)
            self.assertEqual(result,{'string_pointer':0x400000,'consumed_after_percent':3,'variable_indices':[0],
                'memory_reads':[0x2030,0x475570,0x100000+index*0x240+0x228,0x20006c,
                                0x2030,0x363478+index*4,0x300000+selector*4]})
        self.assertEqual(verify(self.elf)['entity_stride'],0x240)
        with self.assertRaises(ValueError):execute_lookup(self.elf,-1,0)

    def test_slots_and_named_label_roundtrip(self):
        data=ssd(command(b'2snm',[b'It costs %T$0G, okay?',b'Yes\tNo',b'Innkeeper']))
        doc=self.plan(data);self.assertEqual(compile_batch(data,doc,verify_source=False)[0],[])
        doc['entries'][0]['segments'][0]['translation']='Custa %T$0G, certo?'
        patches,r=compile_batch(data,doc,verify_source=False)
        self.assertTrue(r['valid'],r);self.assertEqual(len(patches),1)
        self.assertEqual(r['results'][0]['source_offsets'],r['results'][0]['target_offsets'])
        patch=patches[0];self.assertEqual(len(patch['before']),len(patch['after']))
        label=doc['entries'][0]['segments'][2]['offset']-patch['offset']
        self.assertEqual(patch['before'][label:],patch['after'][label:])

    def test_growth_index_and_repack_refused(self):
        data=ssd(command(b'smsg',[b'Price %T$0G!',b'Yes\tNo']))
        for target,mode in (('Custa caro %T$0G!','slots'),('Valor %$2G!','slots'),
                            ('Valor %T$1!','slots'),('Valor %T$0G!','repack')):
            doc=self.plan(data);doc['entries'][0]['mode']=mode
            doc['entries'][0]['segments'][0]['translation']=target
            patches,r=compile_batch(data,doc,verify_source=False)
            self.assertFalse(r['valid'],(target,r));self.assertEqual(patches,[])

    def test_legacy_unknown_and_atomic_failure(self):
        data=ssd(command(b'msgb',[b'Price %T$0G!'])+command(b'msgb',[b'Hello %I$0!']))
        doc=self.plan(data)
        for e,target in zip(doc['entries'],('Valor %T$0G!','Oi %I$0!')):e['segments'][0]['translation']=target
        patches,r=compile_batch(data,doc,verify_source=False)
        self.assertFalse(r['valid']);self.assertEqual(patches,[])
        data=ssd(command(b'msgb',[b'Price %T$0G!']));doc=self.plan(data)
        doc['policy']=NUMERIC15_POLICY;doc['entries'][0]['segments'][0]['translation']='Valor %T$0G!'
        self.assertFalse(compile_batch(data,doc,verify_source=False)[1]['valid'])

    def test_executable_revision_binding(self):
        modified=bytearray(self.elf);modified[0x7f698]^=1
        with self.assertRaises(ValueError):verify(modified)


if __name__=='__main__':unittest.main()
