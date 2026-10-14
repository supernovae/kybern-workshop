import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class Recipe(unittest.TestCase):
    def read(self,name): return json.loads((ROOT/name).read_text())

    def test_preparation_and_workflow_inventory_bytes(self):
        for name in ('preparation.json','workflow.json'):
            for member in self.read(name)['files']:
                self.assertEqual(hashlib.sha256((ROOT/member['path']).read_bytes()).hexdigest(),member['sha256'])
        for name,digest in self.read('pins.json')['declaration_file_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest)

    def test_no_historical_or_fabricated_prepared_identities(self):
        self.assertEqual(self.read('workflow.json')['artifacts'],{})
        refs=[s for s in self.read('campaign.json')['stages'] if s['kind']=='artifact_reference']
        self.assertEqual(len(refs),2)
        self.assertTrue(all(s['artifact'] is None for s in refs))
        self.assertIsNone(self.read('pins.json')['native_input_identities'])

    def test_nine_stage_terminal_evidence_and_workload(self):
        stages=self.read('campaign.json')['stages']; self.assertEqual(len(stages),9)
        final=stages[-1]
        self.assertEqual(final,{'id':'final-evidence','kind':'experiment_collect','scope':'evaluation',
                               'plan':'lock-plan','run':'train-once','evaluations':['evaluate-heldout'],
                               'requires':['lock-plan','train-once','evaluate-heldout']})
        self.assertFalse(any('final-evidence' in s.get('requires',[]) for s in stages))
        run=self.read('run.json');env=self.read('envelope.json');t=run['training'];s=run['staging']
        self.assertEqual(run['seed'],7);self.assertEqual(run['dataset']['synthetic_seed'],7)
        updates=t['max_steps']+s['smoke_steps']+s['warmup_steps']
        positions=t['seq_len']*t['micro_batch_size']*t['gradient_accumulation']
        self.assertEqual(updates,8);self.assertEqual(positions,16)
        self.assertEqual(env['per_root']['training_updates'],updates)
        self.assertEqual(env['per_root']['training_target_positions'],updates*positions)
        self.assertEqual(env['per_root']['evaluation_batches'],updates+3+1)
        self.assertEqual(env['per_root']['evaluation_targets'],(updates+4)*16)
        for key,value in env['per_root'].items(): self.assertEqual(env['total'][key],2*value)
        self.assertEqual(env['stop_work_seconds']+env['reserve_seconds'],env['whole_window_seconds'])
        self.assertEqual(env['whole_window_seconds']-env['command_allowance_seconds']-env['reserve_seconds'],2990)
        self.assertEqual(env['retries'],0);self.assertEqual(env['replay_additional_work'],0)

    def test_preserved_science_bytes(self):
        original=ROOT.parent/'synthetic-cpu'
        for name in ('run.json','tokenizer-config.json','plan.json','suite.json','monitor.json',
                     'preparation.json','preparation-campaign.json'):
            self.assertEqual((ROOT/name).read_bytes(),(original/name).read_bytes())
