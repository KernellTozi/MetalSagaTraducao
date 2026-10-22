import copy
import sys
import unittest
from pathlib import Path
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from reinsertion import descriptor,compile_batch,POLICY,NAMED_POLICY,RESOURCE
from dialogue import sha
from dialogue_advanced import SsdIndex
from test_dialogue_advanced import command,ssd


def plan(data,named=True):
    index=SsdIndex(data)
    return {'schema':1,'policy':NAMED_POLICY if named else POLICY,'resource':RESOURCE,
            'source_sha256':sha(data),'catalog_version':'v003',
            'entries':[descriptor(data,at,index,named_choices=named) for at in index.records]}


class NamedChoicePolicyTests(unittest.TestCase):
    def compile(self,data,doc):return compile_batch(data,doc,verify_source=False)

    def test_fixed_slots_roundtrip_both_editable_fields_and_label_tail(self):
        for tag in (b'smnn',b'2snm'):
            data=ssd(command(tag,[b'%F1A longer question\nHere',b'Yes please\tNo thanks',b'Protected Name']))
            doc=plan(data);e=doc['entries'][0]
            self.assertEqual(self.compile(data,doc)[0],[])
            e['segments'][0]['translation']='%F1Uma pergunta\nAqui'
            e['segments'][1]['translation']='Sim!\tNão, valeu'
            patches,report=self.compile(data,doc)
            self.assertTrue(report['valid'],report)
            self.assertEqual(len(patches),1)
            p=patches[0];at=e['segments'][2]['offset']-e['offset']
            self.assertEqual(p['before'][at:],p['after'][at:])
            self.assertEqual(len(p['before']),len(p['after']))
            self.assertEqual(report['results'][0]['source_offsets'],report['results'][0]['target_offsets'])
            changed=bytearray(data);changed[p['offset']:p['offset']+len(p['after'])]=p['after']
            self.assertEqual(SsdIndex(changed).blocks,SsdIndex(data).blocks)

    def test_rejects_label_repack_and_metadata_changes(self):
        data=ssd(command(b'smnn',[b'Long question here',b'Yes please\tNo thanks',b'Label']))
        base=plan(data)
        for change in ('label','repack','offset','control'):
            doc=copy.deepcopy(base);e=doc['entries'][0]
            e['segments'][0]['translation']='Pergunta curta'
            if change=='label':e['segments'][2]['translation']='Other'
            elif change=='repack':e['mode']='repack'
            elif change=='offset':e['segments'][2]['offset']+=1
            else:e['segments'][1]['translation']='Yes please No thanks'
            with self.subTest(change=change):self.assertFalse(self.compile(data,doc)[1]['valid'])

    def test_opaque_controls_and_native_bytes_remain_blocked(self):
        for body in (b'Price %$1',bytes.fromhex('82ce82ae815b8142')):
            data=ssd(command(b'2snm',[body,b'Yes\tNo',b'Label']));doc=plan(data)
            doc['entries'][0]['segments'][0]['translation']='Teste'
            patches,report=self.compile(data,doc)
            self.assertFalse(report['valid']);self.assertEqual(patches,[])

    def test_choice_runtime_limit_remains_254_bytes(self):
        data=ssd(command(b'smnn',[b'Question',b'B'*252+b'\tC',b'Label']))
        doc=plan(data);field=doc['entries'][0]['segments'][1]
        field['translation']='A'*252+'\tB'
        self.assertTrue(self.compile(data,doc)[1]['valid'])
        field['translation']='A'*253+'\tB'
        patches,report=self.compile(data,doc)
        self.assertFalse(report['valid']);self.assertEqual(patches,[])

    def test_legacy_policy_cannot_edit_named_records(self):
        data=ssd(command(b'smnn',[b'Long question',b'Yes\tNo',b'Label']))
        for named in (False,True):
            doc=plan(data,named);doc['policy']=POLICY
            doc['entries'][0]['segments'][0]['translation']='Teste'
            self.assertFalse(self.compile(data,doc)[1]['valid'])

    def test_opt_in_checks_executable_evidence(self):
        data=ssd(command(b'smnn',[b'Long question',b'Yes\tNo',b'Label']))
        with mock.patch('investigate_named_choices.verify_elf',side_effect=ValueError('revision mismatch')):
            with self.assertRaises(ValueError):self.compile(data,plan(data))

    def test_bad_named_record_cancels_entire_batch(self):
        data=ssd(command(b'smnn',[b'Long question',b'Yes\tNo',b'Label'])+
                 command(b'2snm',[b'Other question',b'Yes\tNo',b'Label']))
        doc=plan(data);doc['entries'][0]['segments'][0]['translation']='Teste'
        doc['entries'][1]['segments'][0]['translation']='X'*200
        patches,report=self.compile(data,doc)
        self.assertFalse(report['valid']);self.assertEqual(report['accepted'],1);self.assertEqual(patches,[])
