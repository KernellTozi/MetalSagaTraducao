import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from reinsertion import descriptor,compile_batch,merge,POLICY,RESOURCE
from dialogue import sha
from dialogue_advanced import SsdIndex
from test_dialogue_advanced import command,ssd
from test_dialogue_formats import message


def plan(data):
    index=SsdIndex(data)
    entries=[descriptor(data,at,index) for at,c in index.records.items()
             if data[at:at+4] in (b'msg\0',b'msgn',b'smsg',b'sel\0',b'2smg',b'2sel',b'msgb',b'supr',b'MC\0\0',b'SP\0\0',b'ST\0\0',b'smnn',b'2snm')]
    return {'schema':1,'policy':POLICY,'resource':RESOURCE,'source_sha256':sha(data),'catalog_version':'v003','entries':entries}


class ReinsertionTests(unittest.TestCase):
    def compile(self,data,document):return compile_batch(data,document,verify_source=False)

    def test_all_eleven_editable_families_smaller_and_same_size(self):
        for tag in (b'msg\0',b'msgn',b'smsg',b'sel\0',b'2smg',b'2sel',b'msgb',b'supr',b'MC\0\0',b'SP\0\0',b'ST\0\0'):
            if tag in (b'msg\0',b'msgn'):
                raw=message(tag,b'Example',b'Label' if tag==b'msgn' else None)[24:-24]
            else:raw=command(tag,[b'Example',b'Yes\tNo'] if tag in (b'smsg',b'2smg') else [b'Example'])
            data=ssd(raw);doc=plan(data)
            for text in ('Example','Samples','Teste'):
                doc['entries'][0]['segments'][0]['translation']=text
                patches,report=self.compile(data,doc)
                self.assertTrue(report['valid'],(tag,report))
                self.assertEqual(len(patches),0 if text=='Example' else 1)
                if patches:
                    self.assertEqual(len(patches[0]['before']),len(patches[0]['after']))
                    self.assertEqual(patches[0]['before'][:8],patches[0]['after'][:8])

    def test_expansion_uses_only_existing_record_padding(self):
        data=ssd(command(b'sel\0',[b'ABCDEFGH']));doc=plan(data)
        self.assertEqual(doc['entries'][0]['segments'][0]['capacity'],11)
        doc['entries'][0]['segments'][0]['translation']='ABCDEFGHIJK'
        patches,report=self.compile(data,doc)
        self.assertTrue(report['valid']);self.assertEqual(len(patches[0]['after']),28)
        doc['entries'][0]['segments'][0]['translation']='ABCDEFGHIJKL'
        patches,report=self.compile(data,doc)
        self.assertFalse(report['valid']);self.assertEqual(patches,[])

    def test_repack_borrows_space_without_record_or_block_growth(self):
        data=ssd(command(b'smsg',[b'Question',b'A very long answer\tAnother answer']))
        doc=plan(data);entry=doc['entries'][0]
        entry['segments'][0]['translation']='A much longer question'
        entry['segments'][1]['translation']='Yes\tNo'
        self.assertFalse(self.compile(data,doc)[1]['valid'])
        entry['mode']='repack';patches,report=self.compile(data,doc)
        self.assertTrue(report['valid'],report)
        self.assertEqual(len(patches[0]['before']),len(patches[0]['after']))
        changed=bytearray(data);p=patches[0];changed[p['offset']:p['offset']+len(p['after'])]=p['after']
        self.assertEqual(SsdIndex(changed).blocks,SsdIndex(data).blocks)
        self.assertNotEqual(report['results'][0]['source_offsets'],report['results'][0]['target_offsets'])

    def test_named_repack_preserves_label_and_moves_computed_pointer(self):
        raw=message(b'msgn',b'Hello',b'Long label',3)[24:-24]
        data=ssd(raw);doc=plan(data);e=doc['entries'][0]
        e['mode']='repack';e['segments'][0]['translation']='Hi'
        patches,report=self.compile(data,doc)
        self.assertTrue(report['valid'],report)
        self.assertIn(b'Long label\0',patches[0]['after'])
        e['segments'][1]['translation']='Other name'
        self.assertFalse(self.compile(data,doc)[1]['valid'])

    def test_ptbr_codec_roundtrip_and_unknown_unicode_rejected(self):
        data=ssd(command(b'msgb',[b'ABCDEFGHIJKLMNO']));doc=plan(data)
        doc['entries'][0]['segments'][0]['translation']='a\u00e7\u00e3o'
        patches,report=self.compile(data,doc)
        self.assertTrue(report['valid'],report);self.assertTrue(report['requires_ptbr_fonts'])
        self.assertIn(bytes.fromhex('8240'),patches[0]['after'])
        for text in ('\u00f1','a\0b','a\u0301'):
            doc['entries'][0]['segments'][0]['translation']=text
            self.assertFalse(self.compile(data,doc)[1]['valid'])

    def test_controls_prefix_newlines_choices_and_opaque_fail_closed(self):
        raw=message(b'msg\0',b'%F1Hi\nThere\tBye')[24:-24];data=ssd(raw);doc=plan(data)
        field=doc['entries'][0]['segments'][0]
        field['translation']='%F1Oi\nTudo\tFim'
        self.assertTrue(self.compile(data,doc)[1]['valid'])
        for text in ('%F2Oi\nTudo\tFim','Oi%F1\nTudo\tFim','%F1Oi Tudo\tFim','%F1Oi\nTudo\tFim\tExtra'):
            field['translation']=text;self.assertFalse(self.compile(data,doc)[1]['valid'])
        data=ssd(command(b'msgb',[b'Item %I$0']));doc=plan(data)
        doc['entries'][0]['segments'][0]['translation']='Item %I$0!'
        self.assertFalse(self.compile(data,doc)[1]['valid'])

    def test_tamper_duplicates_and_wrong_source(self):
        data=ssd(command(b'sel\0',[b'Example']));doc=plan(data)
        for mutate in (lambda d:d['entries'][0].update(record_sha256='0'*64),
                       lambda d:d['entries'][0]['segments'][0].update(source='Fake'),
                       lambda d:d['entries'].append(copy.deepcopy(d['entries'][0]))):
            bad=copy.deepcopy(doc);mutate(bad);self.assertFalse(self.compile(data,bad)[1]['valid'])
        doc['source_sha256']='0'*64
        with self.assertRaises(ValueError):self.compile(data,doc)

    def test_batch_is_all_or_nothing_and_noop_exact(self):
        data=ssd(command(b'sel\0',[b'Example'])+command(b'sel\0',[b'Another']))
        doc=plan(data);patches,report=self.compile(data,doc)
        self.assertTrue(report['valid']);self.assertEqual(patches,[])
        doc['entries'][0]['segments'][0]['translation']='Teste'
        doc['entries'][1]['segments'][0]['translation']='x'*500
        patches,report=self.compile(data,doc)
        self.assertFalse(report['valid']);self.assertEqual(report['accepted'],1);self.assertEqual(patches,[])

    def test_third_string_and_native_origins_remain_blocked(self):
        for data in (ssd(command(b'smnn',[b'Question',b'Yes\tNo',b'Label'])),
                     ssd(command(b'msgb',[bytes.fromhex('82ce82ae815b8142')]))):
            doc=plan(data);doc['entries'][0]['segments'][0]['translation']='Teste'
            self.assertFalse(self.compile(data,doc)[1]['valid'])

    def test_merge_noops_disjoint_batches_and_conflicts(self):
        data=ssd(command(b'smsg',[b'Question',b'Yes\tNo']));base=plan(data)
        a=copy.deepcopy(base);b=copy.deepcopy(base)
        a['entries'][0]['segments'][0]['translation']='Teste'
        b['entries'][0]['segments'][1]['translation']='Sim\tNao'
        merged=merge([base,a,b]);self.assertTrue(self.compile(data,merged)[1]['valid'])
        b['entries'][0]['segments'][0]['translation']='Other'
        with self.assertRaises(ValueError):merge([a,b])

    def test_selection_double_nul_runtime_buffer_limit(self):
        data=ssd(command(b'sel\0',[b'A'*252]));doc=plan(data)
        field=doc['entries'][0]['segments'][0]
        self.assertEqual(field['capacity'],255)
        field['translation']='A'*254
        self.assertTrue(self.compile(data,doc)[1]['valid'])
        field['translation']='A'*255
        self.assertFalse(self.compile(data,doc)[1]['valid'])

    def test_malformed_global_schema_refused(self):
        data=ssd(command(b'sel\0',[b'Example']))
        for document in (None,{'entries':None},{'entries':[None]}):
            with self.assertRaises(ValueError):self.compile(data,document)


if __name__=='__main__':unittest.main()
