import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from control_n0 import tokenize,verify,execute_lookup
from control_b15 import execute_argument
from dialogue_formats import tokens
from dialogue import sha
from dialogue_advanced import SsdIndex
from reinsertion import descriptor,compile_batch,N0_POLICY,I0_POLICY,RESOURCE
from test_dialogue_advanced import command,ssd


class N0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.elf=(ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes()

    def plan(self,data):
        index=SsdIndex(data)
        return {'schema':1,'policy':N0_POLICY,'resource':RESOURCE,'source_sha256':sha(data),
            'catalog_version':'v003','entries':[descriptor(data,at,index,named_choices=True,b15=True,numeric1=True,numeric15=True,t0=True,i0=True,n0=True)
                                               for at in index.records]}

    def test_exact_indirect_only_and_literal_legacy_unchanged(self):
        for raw in (b'%N$0',b'Hi %N$0!',b'%N$0f',b'%B$15 %$1G %$15G %T$0 %I$0 %N$0'):
            self.assertFalse(tokenize(raw)[1],raw);self.assertTrue(tokens(raw)[1])
        self.assertFalse(tokens(b'%N0')[1])
        self.assertEqual(tokens(b'%N0'),tokenize(b'%N0'))
        for raw in (b'%N$00',b'%N$01',b'%N$1',b'%N-$0',b'%n$0',b'%N$3',b'%N$0_1'):
            self.assertTrue(tokenize(raw)[1],raw)

    def test_original_handler_pointer_table_reader_and_delay_slot(self):
        for index in (0,1,127,1024,65535):
            self.assertEqual(execute_lookup(self.elf,index),{
                'string_pointer':0x100000+index*16,'consumed_after_percent':3,'variable_indices':[0],
                'memory_reads':[0x2028,0x47558c+index*4]})
        self.assertEqual(verify(self.elf)['pointer_stride'],4)
        with self.assertRaises(ValueError):execute_lookup(self.elf,-1)

    def test_slots_and_named_label_roundtrip(self):
        data=ssd(command(b'2snm',[b'It costs %N$0G, okay?',b'Yes\tNo',b'Innkeeper']))
        doc=self.plan(data);self.assertEqual(compile_batch(data,doc,verify_source=False)[0],[])
        doc['entries'][0]['segments'][0]['translation']='Custa %N$0G, certo?'
        patches,r=compile_batch(data,doc,verify_source=False)
        self.assertTrue(r['valid'],r);self.assertEqual(len(patches),1)
        self.assertEqual(r['results'][0]['source_offsets'],r['results'][0]['target_offsets'])
        patch=patches[0];self.assertEqual(len(patch['before']),len(patch['after']))
        label=doc['entries'][0]['segments'][2]['offset']-patch['offset']
        self.assertEqual(patch['before'][label:],patch['after'][label:])

    def test_growth_index_and_repack_refused(self):
        data=ssd(command(b'smsg',[b'Price %N$0G!',b'Yes\tNo']))
        for target,mode in (('Custa caro %N$0G!','slots'),('Valor %$2G!','slots'),
                            ('Valor %N$1!','slots'),('Valor %N$0G!','repack')):
            doc=self.plan(data);doc['entries'][0]['mode']=mode
            doc['entries'][0]['segments'][0]['translation']=target
            patches,r=compile_batch(data,doc,verify_source=False)
            self.assertFalse(r['valid'],(target,r));self.assertEqual(patches,[])

    def test_legacy_unknown_and_atomic_failure(self):
        data=ssd(command(b'msgb',[b'Price %N$0G!'])+command(b'msgb',[b'Hello %N$3!']))
        doc=self.plan(data)
        for e,target in zip(doc['entries'],('Valor %N$0G!','Oi %N$3!')):e['segments'][0]['translation']=target
        patches,r=compile_batch(data,doc,verify_source=False)
        self.assertFalse(r['valid']);self.assertEqual(patches,[])
        data=ssd(command(b'msgb',[b'Price %N$0G!']));doc=self.plan(data)
        doc['policy']=I0_POLICY;doc['entries'][0]['segments'][0]['translation']='Valor %N$0G!'
        self.assertFalse(compile_batch(data,doc,verify_source=False)[1]['valid'])

    def test_executable_revision_binding(self):
        modified=bytearray(self.elf);modified[0x1b5cdc]^=1
        with self.assertRaises(ValueError):verify(modified)


if __name__=='__main__':unittest.main()
