import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from control_numeric15 import tokenize,verify
from control_b15 import execute_argument
from dialogue_formats import tokens
from dialogue import sha
from dialogue_advanced import SsdIndex
from reinsertion import descriptor,compile_batch,NUMERIC15_POLICY,NUMERIC1_POLICY,RESOURCE
from test_dialogue_advanced import command,ssd


class Numeric15Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.elf=(ROOT/'JOGO/Metal Saga/SLUS_212.93').read_bytes()

    def plan(self,data):
        index=SsdIndex(data)
        return {'schema':1,'policy':NUMERIC15_POLICY,'resource':RESOURCE,'source_sha256':sha(data),
            'catalog_version':'v003','entries':[descriptor(data,at,index,named_choices=True,b15=True,numeric1=True,numeric15=True)
                                               for at in index.records]}

    def test_exact_integer_only_and_legacy_unchanged(self):
        for raw in (b'%$15G',b'%$15 minutes.',b'%$15F',b'%$15',b'%B$15: %$15G'):
            self.assertFalse(tokenize(raw)[1],raw);self.assertTrue(tokens(raw)[1])
        for raw in (b'%$150',b'%$155',b'%$14',b'%$015',b'%$-15',b'%$15f',b'%$15f100',b'%$15f$2',b'%$15fX',b'%N$1',b'%$15 %T$0'):
            self.assertTrue(tokenize(raw)[1],raw)

    def test_original_reader_signed_decimal_boundaries(self):
        for value in (0,1,999,2147483647,0x80000000,0xffffffff):
            result=execute_argument(self.elf,b'$15G\0',[777]*15+[value])
            self.assertEqual(result,{'consumed':3,'value':value,'variable_indices':[15]})
            signed=value if value<0x80000000 else value-0x100000000
            self.assertLessEqual(len(str(signed)),11)
        self.assertEqual(verify(self.elf)['format_hex'],'256400')

    def test_slots_and_named_label_roundtrip(self):
        data=ssd(command(b'2snm',[b'It costs %$15G, okay?',b'Yes\tNo',b'Innkeeper']))
        doc=self.plan(data);self.assertEqual(compile_batch(data,doc,verify_source=False)[0],[])
        doc['entries'][0]['segments'][0]['translation']='Custa %$15G, certo?'
        patches,r=compile_batch(data,doc,verify_source=False)
        self.assertTrue(r['valid'],r);self.assertEqual(len(patches),1)
        self.assertEqual(r['results'][0]['source_offsets'],r['results'][0]['target_offsets'])
        patch=patches[0];self.assertEqual(len(patch['before']),len(patch['after']))
        label=doc['entries'][0]['segments'][2]['offset']-patch['offset']
        self.assertEqual(patch['before'][label:],patch['after'][label:])

    def test_growth_index_float_suffix_and_repack_refused(self):
        data=ssd(command(b'smsg',[b'Price %$15G!',b'Yes\tNo']))
        for target,mode in (('Custa caro %$15G!','slots'),('Valor %$2G!','slots'),
                            ('Valor %$15f!','slots'),('Valor %$15G!','repack')):
            doc=self.plan(data);doc['entries'][0]['mode']=mode
            doc['entries'][0]['segments'][0]['translation']=target
            patches,r=compile_batch(data,doc,verify_source=False)
            self.assertFalse(r['valid'],(target,r));self.assertEqual(patches,[])

    def test_legacy_unknown_and_atomic_failure(self):
        data=ssd(command(b'msgb',[b'Price %$15G!'])+command(b'msgb',[b'Hello %T$0!']))
        doc=self.plan(data)
        for e,target in zip(doc['entries'],('Valor %$15G!','Oi %T$0!')):e['segments'][0]['translation']=target
        patches,r=compile_batch(data,doc,verify_source=False)
        self.assertFalse(r['valid']);self.assertEqual(patches,[])
        data=ssd(command(b'msgb',[b'Price %$15G!']));doc=self.plan(data)
        doc['policy']=NUMERIC1_POLICY;doc['entries'][0]['segments'][0]['translation']='Valor %$15G!'
        self.assertFalse(compile_batch(data,doc,verify_source=False)[1]['valid'])

    def test_executable_revision_binding(self):
        modified=bytearray(self.elf);modified[0x349dc0]=ord('X')
        with self.assertRaises(ValueError):verify(modified)


if __name__=='__main__':unittest.main()
