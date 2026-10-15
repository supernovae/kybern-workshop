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
            files={split:[dict(**pin,blob_id='a'*40)] for split,pin in h.read(ROOT/'first-files.json').items()})
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

    def test_exact_approved_limits_and_story_selection(self):
        _,lock=self.lock()
        self.assertEqual(h.acquisition(lock),dict(acquisition_version=1,provider='huggingface',
            repo_id='roneneldan/TinyStories',revision='f54c09fd23315a6f9c86f9dc80f725de7d8f9c64',
            lock_sha256=lock['lock_sha256'],allow_network=True,decoder_profile='scalar-parquet-v1',
            max_source_body_bytes=314572800,max_metadata_body_bytes=1048576,max_transfers=2,
            max_requests=12,max_retries_per_shard=0,max_wall_seconds=3600,max_cache_bytes=314572800,
            max_cache_files=2,max_scanned_rows=2048,max_verification_bytes=1073741824,
            max_observed_owned_bytes=2147483648,max_observed_owned_inodes=4096))
        self.assertEqual(h.PREP,dict(max_documents=80,max_tokens=327680,max_vocab_size=512,
            min_free_bytes=1073741824,min_free_inodes=128,max_snapshot_bytes=16777216,max_snapshot_records=2048))
        self.assertEqual(h.FLOW,dict(max_training_updates=16,max_target_positions=512,max_eval_batches=1))
        self.assertEqual(h.read(ROOT/'approval-provenance.json')['limits'],dict(source_body_bytes=314572800,
            cache_bytes=314572800,transfers=2,cache_files=2,shard_retries=0,train_stories=64,validation_stories=16,
            cpu_configurations=2,total_wall_seconds=3600,training_updates=16,evaluation_batches=24,
            observed_ram_bytes=4294967296,retained_output_bytes=2147483648))
        self.assertEqual(h.read(ROOT/'source.json')['selection'],{'mode':'bounded','documents':{'train':64,'validation':16}})
        for name in ('run.json','tokenizer-config.json'):
            data=h.read(ROOT/name)['dataset']
            self.assertEqual((data['train_max_documents'],data['validation_max_documents']),(64,16))
            self.assertEqual((data['train_max_tokens'],data['validation_max_tokens']),(262144,65536))
        self.assertEqual(h.read(ROOT/'monitor.json'),dict(monitor_policy_version=1,max_wall_seconds=3600,
            max_tree_rss_bytes=4294967296,max_added_workspace_bytes=2147483648,interval_seconds=1,termination_grace_seconds=5))

    def test_exact_first_file_pins_and_each_identity_guard(self):
        expected={'train':dict(path='data/train-00000-of-00004-2d5a1467fff1081b.parquet',size=248731111,
            lfs_sha256='77cf780cebe52b6e83e3a2ac84bc56d8059363113e41d17a023f1d8b2ed0fc0b'),
            'validation':dict(path='data/validation-00000-of-00001-869c898b519ad725.parquet',size=9989127,
            lfs_sha256='33406a6206554cfc279c29c11f4df51528af487aa1a602b075566fc83c49dcab')}
        self.assertEqual(h.read(ROOT/'first-files.json'),expected)
        _,original=self.lock();source=h.read(ROOT/'source.json')
        for split in expected:
            for key,value in [('path','other.parquet'),('size',1),('lfs_sha256','c'*64)]:
                with self.subTest(split=split,key=key):
                    lock=copy.deepcopy(original);lock['provenance']['files'][split][0][key]=value
                    with self.assertRaises(ValueError):h.check_lock(lock,source)
        for mutate in (lambda x:x['provenance'].update(loader='json'),
                       lambda x:x['source'].update(text_field='different'),
                       lambda x:x['provenance']['files'].update(extra=[dict(x['provenance']['files']['train'][0],size=1)]),
                       lambda x:x['provenance']['files'].update(train=[])):
            lock=copy.deepcopy(original);mutate(lock)
            with self.assertRaises(ValueError):h.check_lock(lock,source)

    def test_cpu_offline_flags_and_wait_ceiling(self):
        for row in h.commands(self.args)['steps']:
            env={item.split('=',1)[0]:item.split('=',1)[1] for item in row['argv'][1:] if '=' in item}
            online=row['step'] in ('source-lock','preparation-apply')
            self.assertEqual(env['HF_HUB_OFFLINE'],'0' if online else '1')
            self.assertEqual(env['HF_DATASETS_OFFLINE'],'0' if online else '1')
            self.assertEqual(env['CUDA_VISIBLE_DEVICES'],'')
            for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','TRANSFORMERS_OFFLINE','UV_OFFLINE'):
                self.assertEqual(env[key],'1')
            if row['step']=='workflow-run':
                self.assertEqual(row['argv'][row['argv'].index('--max-wait-seconds')+1],'3600')

    def test_each_receipt_guard_refuses_before_binding(self):
        rows=[]
        for stage,kind,artifact,location in [
            ('snapshot','dataset_snapshot','dataset_snapshot',self.work/'snapshot/manifest.json'),
            ('train-tokenizer','tokenizer_train','tokenizer',self.work/'payload/tokenizer/tokenizer.json'),
            ('pack-data','data_prepare','prepared_data',self.work/'payload/cache/fixture')]:
            rows.append(dict(id=stage,kind=kind,state='COMPLETE',receipt='fixture-receipt',
                outputs=[dict(kind=artifact,identifier='a'*64,sha256='b'*64)],availability={'path':str(location)}))
        mutations=[lambda x:x.append(copy.deepcopy(x[0])),
            lambda x:x.append(dict(x[0],id='extra')),lambda x:x.pop(),
            lambda x:x[0].update(id='wrong'),lambda x:x[0].update(state='INTERRUPTED'),
            lambda x:x[1].update(state='FAILED'),lambda x:x[2].update(state='BLOCKED'),
            lambda x:x[0].update(kind='artifact_reference'),lambda x:x[1].update(kind='data_prepare'),
            lambda x:x[2].update(kind='tokenizer_train'),
            lambda x:x[0]['availability'].update(path=str(self.work/'wrong/manifest.json'))]
        for n in (0,1,2):
            mutations += [lambda x,n=n:x[n]['outputs'].append(copy.deepcopy(x[n]['outputs'][0])),
                lambda x,n=n:x[n].update(outputs=[]),lambda x,n=n:x[n].update(receipt=''),
                lambda x,n=n:x[n]['outputs'][0].update(kind='wrong-kind')]
        for index,mutate in enumerate(mutations):
            with self.subTest(index=index):
                damaged=copy.deepcopy(rows);mutate(damaged)
                receipt=self.root/f'receipt-{index}.json';h.save(receipt,{'stages':damaged})
                args=argparse.Namespace(recipe=str(ROOT),receipt=str(receipt),destination=str(self.root/f'sealed-{index}'),
                    work=str(self.work),bindings=str(self.root/f'bindings-{index}.json'))
                with self.assertRaises(ValueError):h.seal_workflow(args)
                self.assertFalse(Path(args.destination).exists());self.assertFalse(Path(args.bindings).exists())

    def test_pair_projection_is_checked_in_admission(self):
        from types import SimpleNamespace
        from sparselab.config.models import RunConfig
        cfg=RunConfig.model_validate(h.read(ROOT/'run.json'))
        two=SimpleNamespace(cells=[SimpleNamespace(config=cfg),SimpleNamespace(config=cfg)])
        self.assertEqual(h.check_pair_budget(two),dict(training_updates=16,target_positions=512,evaluation_batches=24))
        for count in (1,3):
            with self.assertRaises(ValueError):h.check_pair_budget(SimpleNamespace(cells=[two.cells[0]]*count))
        for group,key,value in [('staging','smoke_steps',3),('staging','warmup_steps',6),
            ('training','max_steps',2),('training','seq_len',31),('training','micro_batch_size',2),
            ('training','gradient_accumulation',2),('evaluation','every_steps',2),('evaluation','max_batches',2)]:
            raw=cfg.model_dump(mode='json');raw[group][key]=value
            bad=SimpleNamespace(cells=[SimpleNamespace(config=RunConfig.model_validate(raw)),two.cells[1]])
            with self.assertRaises(ValueError):h.check_pair_budget(bad)
        args=argparse.Namespace(recipe=str(ROOT),bindings=str(self.root/'bindings.json'),reviewed_commit='a'*40,
            phase='workflow',output=str(self.root/'admission.json'))
        native=dict(recipe_sha256='b'*64,binding_sha256='c'*64)
        with patch.object(subprocess,'check_output',side_effect=lambda *a,**k:'a'*40 if 'rev-parse' in a[0] else ''), \
             patch('sparselab.experiments.workflow_recipe.inspect_workflow',return_value=native), \
             patch('sparselab.experiments.workflow_recipe.resolve_workflow',return_value=SimpleNamespace(cells=two.cells+[two.cells[0]])):
            with self.assertRaises(ValueError):h.admission(args)
            self.assertFalse(Path(args.output).exists())
        with patch.object(subprocess,'check_output',side_effect=lambda *a,**k:'a'*40 if 'rev-parse' in a[0] else ''), \
             patch('sparselab.experiments.workflow_recipe.inspect_workflow',return_value=native), \
             patch('sparselab.experiments.workflow_recipe.resolve_workflow',return_value=two):
            h.admission(args)
            self.assertEqual(h.read(Path(args.output))['limits'],h.FLOW)
            before=Path(args.output).read_bytes()
            with self.assertRaises(FileExistsError):h.admission(args)
            self.assertEqual(Path(args.output).read_bytes(),before)

    def test_no_clobber_and_bounded_json_entrypoints(self):
        existing=self.root/'existing.json';existing.write_text('{"keep":true}')
        with self.assertRaises(FileExistsError):h.save(existing,{'overwrite':True})
        self.assertEqual(existing.read_text(),'{"keep":true}')
        with self.assertRaises(ValueError):h.copy_recipe(ROOT,self.work)
        self.assertEqual(list(self.work.iterdir()),[])
        target,_=self.lock()
        args=argparse.Namespace(recipe=str(ROOT),work=str(self.work),source_lock=str(target),
            destination=str(self.root/'fresh'),bindings=str(existing))
        with self.assertRaises(ValueError):h.bind_preparation(args)
        self.assertFalse(Path(args.destination).exists())
        big=self.root/'big.json';big.write_text(json.dumps({'padding':'x'*(8*1024*1024)}))
        with self.assertRaisesRegex(ValueError,'bounded regular'):h.read(big)


if __name__=='__main__':unittest.main()
