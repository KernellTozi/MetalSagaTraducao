import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_translation_coverage import audit,load_compiled


class CoverageTests(unittest.TestCase):
    def fixture(self):
        def entry(key,text,target=None,editable=True):
            return {'id':key,'segments':[{'source':text,'translation':text if target is None else target,
                    'source_hex':text.encode('ascii').hex(),'editable':editable}]}
        document={'source_sha256':'hash','entries':[
            entry('a','Hello','Olá'),entry('b','%I$15'),entry('c','%N0...'),
            entry('d','- Newfolk -'),entry('e','Welcome to Newfolk.'),entry('f','...')]}
        document['entries'][5]['segments'].append({'source':'Hunter','translation':'Hunter',
                                                  'source_hex':'48756e746572','editable':False})
        report={'valid':True,'refused':0,'source_sha256':'hash','accepted':1,'unchanged':5,
                'deferred':[{'id':'b','reason':'opaque'}]}
        policy={'protected_names':['Newfolk'],'protected_terms':['Hunter'],
                'preserve_expressions':[],'case_sensitive_names':[]}
        return document,report,policy

    def test_triage_preserves_uncertainty_and_ignores_readonly_label(self):
        doc,report,policy=self.fixture();summary,rows=audit(doc,report,policy)
        self.assertEqual(summary['classes'],{'modified':1,'deferred':1,'controls_or_punctuation':2,
                         'name_or_expression_candidate':1,'review_unchanged':1})
        self.assertFalse(summary['automatic_edit_approval'])
        self.assertEqual(rows[4]['class'],'review_unchanged')

    def test_rejects_invalid_duplicate_or_inconsistent_inputs(self):
        doc,report,policy=self.fixture()
        for change in ('invalid','duplicate','count','hash','deferral'):
            a,b=copy.deepcopy(doc),copy.deepcopy(report)
            if change=='invalid':b['valid']=False
            elif change=='duplicate':a['entries'].append(a['entries'][0])
            elif change=='count':b['accepted']=2
            elif change=='hash':b['source_sha256']='other'
            else:b['deferred'].append({'id':'unknown'})
            with self.subTest(change=change),self.assertRaises(ValueError):audit(a,b,policy)

    def test_never_guesses_opaque_controls_without_deferral(self):
        doc,report,policy=self.fixture();report['deferred']=[]
        with self.assertRaises(ValueError):audit(doc,report,policy)

    def test_reports_opaque_spans_without_promoting_records(self):
        doc,report,policy=self.fixture()
        summary,_=audit(doc,report,policy)
        self.assertEqual(summary['deferred_by_tag'],{'unknown':1})
        self.assertEqual(summary['opaque_parser_spans'],[{'syntax':'%I$15','occurrences':1,'records':1}])
        self.assertFalse(summary['automatic_edit_approval'])

    def test_compact_plan_rebuilt_only_from_same_recipe_chain_and_counts(self):
        import json,tempfile
        from unittest.mock import patch
        root=Path(__file__).resolve().parents[1]
        report={'draft_sources':[{'path':'translations/regiao-inicial-v031.json','sha256':'bound'}],
                'valid':True,'accepted':1,'unchanged':0,'refused':0,'deferred':[],
                'source_sha256':'map','policy':'test'}
        with tempfile.TemporaryDirectory(dir=root/'work',prefix='test-compact-audit-') as folder:
            folder=Path(folder);(folder/'relatorio.json').write_text(json.dumps(report),encoding='utf-8')
            with patch('build_translation_pilot.load_draft',return_value=({},report['draft_sources'])),patch(
                'build_translation_pilot.compile_draft',return_value=({'entries':[]},[],report)):
                plan,_=load_compiled(folder);self.assertEqual(json.loads(plan),{'entries':[]})
            with patch('build_translation_pilot.load_draft',return_value=({},[])),self.assertRaises(ValueError):load_compiled(folder)
            with patch('build_translation_pilot.load_draft',return_value=({},report['draft_sources'])),patch(
                'build_translation_pilot.compile_draft',return_value=({},[],{**report,'accepted':2})),self.assertRaises(ValueError):load_compiled(folder)

    def test_new_variable_policy_classifies_preserved_name_without_promoting_unknown(self):
        from reinsertion import VARIABLE_POLICY
        doc,report,policy=self.fixture();doc['policy']=VARIABLE_POLICY
        entry=doc['entries'][2];entry['segments'][0].update(source='%N$1.',translation='%N$1.',source_hex=b'%N$1.'.hex())
        summary,_=audit(doc,report,policy)
        self.assertEqual(summary['classes']['controls_or_punctuation'],2)
        self.assertEqual(summary['classes']['deferred'],1)
