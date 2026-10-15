"""Bounded metadata and fake-child tests; no payload download or model runtime."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('handoff', ROOT/'handoff.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.work = self.root/'work'; self.work.mkdir()
        self.args = argparse.Namespace(python=sys.executable,recipe=str(ROOT),work=str(self.work),
            lock=None,experiment=None,index=None)

    def lock(self):
        from sparselab.data.sources import lock_source, verify_lock
        source = h.read(ROOT/'source.json')
        provenance = dict(repo_id=source['repo_id'],revision=h.REVISION,loader='parquet',loader_options={},
            files={split:[dict(path=split+'.parquet',size=100,blob_id='a'*40,lfs_sha256='b'*64)]
                   for split in ('train','validation')})
        target=self.root/'source.lock.json'
        with patch('sparselab.data.sources._hub_identity',return_value=provenance):
            lock_source(ROOT/'source.json',target,self.root/'unused-cache')
        return target, verify_lock(target)

    def test_native_preparation_inspection_no_work(self):
        from sparselab.experiments.preparation_recipe import inspect_preparation_recipe
        from sparselab.experiments.preparation_execution import PreparationAdmission
        target,lock=self.lock()
        args=argparse.Namespace(recipe=str(ROOT),work=str(self.work),source_lock=str(target),
            destination=str(self.root/'recipe'),bindings=str(self.root/'bindings.json'))
        h.bind_preparation(args)
        result=inspect_preparation_recipe(Path(args.destination)/'preparation.json',Path(args.bindings))
        self.assertFalse(result['executable'])
        PreparationAdmission.model_validate(dict(reviewed_commit='a'*40,recipe_sha256=result['recipe_sha256'],
            binding_sha256=result['binding_sha256'],cpu_python=sys.executable,**h.PREP,
            acquisitions={'snapshot':h.acquisition(lock)}))
        self.assertEqual(list(self.work.iterdir()),[])
        with self.assertRaises(ValueError):h.bind_preparation(args)

    def test_first_files_budget_and_pin_refusals(self):
        _,original=self.lock()
        for mutate in (lambda x:x['source'].update(revision='c'*40),
                       lambda x:x['provenance']['files']['validation'].append(copy.deepcopy(x['provenance']['files']['validation'][0])),
                       lambda x:x['provenance']['files']['train'][0].update(size=314572801),
                       lambda x:x['provenance']['files']['train'][0].pop('lfs_sha256')):
            lock=copy.deepcopy(original); mutate(lock)
            with self.assertRaises(ValueError):h.check_lock(lock,h.read(ROOT/'source.json'))

    def test_commands_are_native_parseable(self):
        from sparselab.cli.main import build_parser
        parser=build_parser(self.work)
        self.args.lock=str(self.work/'experiment.lock.json')
        self.args.experiment=str(self.work/'experiment')
        self.args.index=str(self.work/'index.json')
        with patch.object(subprocess,'run',side_effect=AssertionError('unexpected execution')):
            result=h.commands(self.args)
        self.assertFalse(result['execution_enabled'])
        for row in result['steps']:
            argv=row['argv']; native=argv[argv.index('sparselab')+1:]
            parsed=parser.parse_args(native)
            self.assertTrue(callable(parsed.handler))
        self.assertEqual(sum('--execute-runs' in row['argv'] for row in result['steps']),1)

    def test_fake_process_preserves_argument_bytes_and_failure(self):
        # Replace the payload with a tiny child; never call the rendered Lab CLI.
        self.args.recipe=str(self.root/'space $() ; quoted recipe')
        args=h.commands(self.args)['steps'][0]['argv']
        for code in (0,7):
            child=subprocess.run([sys.executable,'-c',
                'import json,sys;print(json.dumps(sys.argv[2:]));print("fixture stderr",file=sys.stderr);sys.exit(int(sys.argv[1]))',
                str(code),*args],capture_output=True,text=True,timeout=5)
            self.assertEqual(child.returncode,code)
            self.assertEqual(json.loads(child.stdout),args)
            self.assertEqual(child.stderr.strip(),'fixture stderr')

    def test_schema_and_scientific_budget(self):
        from sparselab.config.models import RunConfig, TokenizerTrainConfig
        from sparselab.campaign.plan import CampaignPlan
        run=RunConfig.model_validate(h.read(ROOT/'run.json'))
        token=TokenizerTrainConfig.model_validate(h.read(ROOT/'tokenizer-config.json'))
        CampaignPlan.model_validate(h.read(ROOT/'preparation-campaign.json'))
        updates=2*(run.staging.smoke_steps+run.staging.warmup_steps+run.training.max_steps)
        self.assertEqual(updates,16)
        self.assertEqual(updates*run.training.seq_len,512)
        # initial + each update for smoke/warmup/main, plus native heldout per arm
        self.assertEqual(2*((2+1)+(5+1)+(1+1)+1)*run.evaluation.max_batches,24)
        self.assertEqual(token.max_documents,64)
        self.assertEqual(run.dataset.validation_max_documents,16)

    def test_incomplete_receipt_and_path_refuse(self):
        receipt=self.root/'receipt.json'; h.save(receipt,{'stages':[]})
        with self.assertRaises(ValueError):h.seal_workflow(argparse.Namespace(receipt=str(receipt)))
        with self.assertRaises(ValueError):h.path('/tmp/../escape')
        link=self.root/'link';link.symlink_to(self.work,target_is_directory=True)
        with self.assertRaises(ValueError):h.path(link/'child')
        duplicate=self.root/'duplicate.json';duplicate.write_text('{"a":1,"a":2}')
        with self.assertRaises(ValueError):h.read(duplicate)

    def test_hard_memory_semantics_refuse(self):
        from sparselab.experiments.acquisition_admission import AcquisitionAdmission
        _,lock=self.lock(); value=h.acquisition(lock)
        self.assertEqual(value['max_retries_per_shard'],0)
        for field in ('require_hard_decoder_memory_bytes','require_hard_disk_bytes','require_expanded_bytes'):
            with self.assertRaises(ValueError):AcquisitionAdmission.model_validate({**value,field:1024})

    def test_reviewed_commit_is_not_inferred(self):
        args=argparse.Namespace(recipe=str(ROOT),bindings=str(self.root/'bindings'),reviewed_commit='a'*40)
        with patch.object(subprocess,'check_output',side_effect=['b'*40,'']):
            with self.assertRaisesRegex(ValueError,'reviewed commit'):h.admission(args)
        with patch.object(subprocess,'check_output',side_effect=['a'*40,' M run.json']):
            with self.assertRaisesRegex(ValueError,'reviewed commit'):h.admission(args)

    def test_sealed_pair_native_metadata_and_no_clobber(self):
        from sparselab.experiments.workflow_recipe import inspect_workflow
        rows=[]
        for stage,kind,artifact,location in [
            ('snapshot','dataset_snapshot','dataset_snapshot',self.work/'snapshot/manifest.json'),
            ('train-tokenizer','tokenizer_train','tokenizer',self.work/'payload/tokenizer/tokenizer.json'),
            ('pack-data','data_prepare','prepared_data',self.work/'payload/cache/fixture')]:
            rows.append(dict(id=stage,kind=kind,state='COMPLETE',receipt='fixture-receipt',
                outputs=[dict(kind=artifact,identifier='a'*64,sha256='b'*64)],availability={'path':str(location)}))
        receipt=self.root/'fixture-receipt.json';h.save(receipt,{'stages':rows})
        args=argparse.Namespace(recipe=str(ROOT),receipt=str(receipt),destination=str(self.root/'sealed'),
            work=str(self.work),bindings=str(self.root/'flow-bindings.json'))
        h.seal_workflow(args)
        result=inspect_workflow(Path(args.destination)/'workflow.json',Path(args.bindings),max_runs=2)
        self.assertFalse(result['executable'])
        campaign=h.read(Path(args.destination)/'campaign.json')
        runs=[s for s in campaign['stages'] if s['kind']=='experiment_run']
        self.assertEqual(len(runs),2)
        self.assertIn('run-baseline',runs[1]['requires'])
        self.assertEqual(list(self.work.iterdir()),[])
        with self.assertRaises(ValueError):h.seal_workflow(args)

    def test_partial_report_bindings_refuse(self):
        self.args.lock=str(self.work/'lock.json')
        with self.assertRaisesRegex(ValueError,'report requires'):h.commands(self.args)


if __name__=='__main__':unittest.main()
