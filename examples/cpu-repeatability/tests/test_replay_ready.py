"""Inspector-boundary unit tests, NOT completed native workflow execution."""
import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import replay_ready as gate


class ReplayReady(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.source=self.root/'workflow.json';self.source.write_text('{}')
        self.bindings=self.root/'bindings.json';self.bindings.write_text('{}')
        self.admission=self.root/'admission.json';self.admission.write_text('{}')
        self.result={'stages':[{'id':name,'state':'COMPLETE'} for name in gate.STAGES],
                     'next_action':{'action':'none'}}

    def check(self):
        return gate.check(self.source,self.bindings,self.root,self.admission)

    def test_mocked_complete_projection_passes_without_writes(self):
        before={p.name:p.read_bytes() for p in self.root.iterdir()}
        with patch.object(gate,'inspect_native',return_value=self.result) as inspector:
            result=self.check()
            inspector.assert_called_once_with(self.source,self.bindings,self.root,{})
        self.assertEqual(result['state'],'READY_FOR_BOUNDED_REPLAY')
        self.assertEqual(result['projection'],self.result)
        self.assertEqual({p.name:p.read_bytes() for p in self.root.iterdir()},before)

    def test_each_incomplete_stage_and_bad_next_action_refuse(self):
        for name in gate.STAGES:
            for state in ('READY','RUNNING','FAILED','BLOCKED','INTERRUPTED','AWAITING_APPROVAL',None):
                data=copy.deepcopy(self.result)
                next(row for row in data['stages'] if row['id']==name)['state']=state
                with self.subTest(stage=name,state=state),patch.object(gate,'inspect_native',return_value=data):
                    with self.assertRaisesRegex(ValueError,'COMPLETE'): self.check()
        for action in (None,{},'none',{'action':'apply'},{'action':'resume'}):
            data={**self.result,'next_action':action}
            with patch.object(gate,'inspect_native',return_value=data),self.assertRaises(ValueError): self.check()

    def test_missing_duplicate_unknown_or_malformed_stages_refuse(self):
        for rows in (None,[],self.result['stages'][:-1],self.result['stages']+[self.result['stages'][0]],
                     self.result['stages'][:-1]+[self.result['stages'][0]],
                     self.result['stages'][:-1]+[{'id':'other','state':'COMPLETE'}],['bad']*9):
            with patch.object(gate,'inspect_native',return_value={**self.result,'stages':rows}):
                with self.assertRaises(ValueError): self.check()

    def test_native_corruption_refuses_cli_without_ready_output(self):
        stdout,stderr=io.StringIO(),io.StringIO()
        with patch.object(gate,'inspect_native',side_effect=ValueError('native receipt corrupt')),\
             contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as stopped:
                gate.main(['--source',str(self.source),'--bindings',str(self.bindings),
                           '--work-dir',str(self.root),'--admission',str(self.admission)])
        self.assertEqual(stopped.exception.code,1)
        self.assertEqual(stdout.getvalue(),'')
        self.assertIn('native receipt corrupt',stderr.getvalue())

    def test_native_boundary_requests_only_cold_next_inspection(self):
        # The real constructor/engine are intentionally NOT executed here.
        engine=Mock(spec=['inspect']);engine.inspect.return_value=self.result
        context=Mock(spec=['engine']);context.engine.return_value=engine
        with patch('sparselab.experiments.workflow_execution.WorkflowExecution',return_value=context) as factory,\
             patch('sparselab.experiments.workflow_execution.WorkflowAdmission.model_validate',return_value='validated'):
            result=gate.inspect_native(self.source,self.bindings,self.root,{'fixture':'only'})
        factory.assert_called_once_with(self.source,self.bindings,self.root,'validated')
        context.engine.assert_called_once_with(cold_verify=True)
        engine.inspect.assert_called_once_with('next')
        self.assertEqual(engine.mock_calls,[unittest.mock.call.inspect('next')])
        self.assertEqual(result,self.result)


if __name__ == '__main__': unittest.main()
