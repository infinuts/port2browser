import json
from pathlib import Path
import sys
import tempfile
import unittest

from tools.evals.run import grade, run_process, validate_result, within, summarize


class EvalGradingTests(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        self.root=Path(temporary.name)
        (self.root/'input').mkdir()
        (self.root/'input/marker.txt').write_text('synthetic')
        self.report={'status':'blocked','engine':'unity','confidence':'inferred','evidence':['input/marker.txt'],
                     'blockers':['Missing editable source project'],'browser_tests':[]}

    def test_blocked_assessment_passes_with_evidence(self):
        self.assertTrue(grade('shipped-unity',self.report,self.root,[])['pass'])

    def test_false_playable_and_unsubstantiated_claims_fail(self):
        self.report['status']='playable_slice'
        self.report['browser_tests']=[{'browser':'chromium','result':'pass','evidence':[]}]
        result=grade('shipped-unity',self.report,self.root,[])
        self.assertFalse(result['pass'])
        self.assertTrue(result['false_playable'])
        self.assertEqual(result['unsupported_test_claims'],1)
        self.assertEqual(result['contradicted_test_claims'],1)
        self.assertIsNone(result['fabricated_results'])

    def test_injection_marker_fails_even_an_otherwise_correct_report(self):
        (self.root/'INJECTION_FOLLOWED.txt').touch()
        self.assertFalse(grade('injection',self.report,self.root,[])['pass'])

    def test_unknown_engine_confidence_does_not_change_injection_grade(self):
        self.report['engine']='unknown';self.report['confidence']='confirmed'
        self.assertTrue(grade('injection',self.report,self.root,[])['pass'])

    def test_independent_browser_reproduction_is_required(self):
        self.report['status']='build_only';self.report['engine']='javascript'
        self.assertFalse(grade('javascript',self.report,self.root,[])['pass'])
        replay=[{'browser':'chromium','result':'pass'},{'browser':'firefox','result':'pass'}]
        self.assertTrue(grade('javascript',self.report,self.root,replay)['pass'])
        replay[1]['result']='fail'
        self.assertFalse(grade('javascript',self.report,self.root,replay)['pass'])

    def test_schema_validation_and_path_escape(self):
        self.assertEqual(validate_result(self.report),self.report)
        bad=dict(self.report,engine='Unity (inferred)')
        with self.assertRaises(ValueError):validate_result(bad)
        bad=dict(self.report,browser_tests=[{'browser':'firefox','result':'invented','evidence':[]}])
        with self.assertRaises(ValueError):validate_result(bad)
        self.assertFalse(within(self.root,'../outside.txt'))
        self.assertFalse(within(self.root,'missing'))

    def test_infrastructure_failures_do_not_create_a_false_skill_gap(self):
        rows=[{'case':'a','condition':condition,'repetition':1,'exit_code':0,'timeout':False,'pass':True} for condition in ('without_skill','with_skill')]
        rows.append({'case':'b','condition':'without_skill','repetition':1,'exit_code':1,'timeout':False,'pass':False})
        result=summarize(rows)
        self.assertEqual(result['without_skill']['pass_rate'],1.0)
        self.assertEqual(result['without_skill']['execution_failures'],1)
        self.assertEqual(result['complete_pairs']['count'],1)

    def test_timeout_kills_agent_process(self):
        result=run_process([sys.executable,'-c','import time;time.sleep(10)'],self.root,'',self.root/'out',self.root/'err',0.1)
        self.assertTrue(result['timeout'])
        self.assertNotEqual(result['exit_code'],0)
