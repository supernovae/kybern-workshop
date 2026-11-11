"""Fresh native recipe contract. No training, GPU work, downloads or inventory."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'experiments/devmind-v2'
PLAN = PACKAGE / 'experiment.json'
spec = importlib.util.spec_from_file_location('v2_binder', ROOT / 'scripts/bind-experiment.py')
binder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(binder)


def bindings(root):
    """Synthetic locations and hashes only, never evidence of usable capacity."""
    value = binder.read(PACKAGE / 'binding.example.json')
    value['dataset'].update(
        mixture_declaration_path=str(root / 'mixture.json'),
        mixture_output_path=str(root / 'mixture'), cache_dir=str(root / 'cache'),
        train_path=str(root / 'mixture/train.jsonl'),
        validation_path=str(root / 'mixture/validation.jsonl'),
        train_max_documents=10, validation_max_documents=5,
        train_max_tokens=10256578560, validation_max_tokens=1310720,
        license='synthetic fixture, not admitted data')
    value['tokenizer']['path'] = str(root / 'tokenizer.json')
    value['logging']['root_dir'] = str(root / 'fresh-runs')
    value['runtime']['backend'] = 'cpu'
    value['runtime']['precision'] = 'fp32'
    for panel in value['evaluation']['panels']:
        panel['prepared_path'] = str(root / panel['name'])
        for name in ('prepared_manifest_sha256', 'tokenizer_file_sha256', 'tokenizer_canonical_sha256'):
            panel[name] = 'a' * 64
    return value


class FreshRecipe(unittest.TestCase):
    def test_unbound_inputs_refuse_authoring(self):
        with self.assertRaisesRegex(ValueError, 'Unbound'):
            binder.assemble(PLAN, binder.read(PACKAGE / 'binding.example.json'))

    def test_fresh_architecture_is_complete_without_inherited_state(self):
        run = binder.assemble(PLAN, bindings(Path('/fixture')))
        model = run['model']
        self.assertEqual((model['num_layers'], model['hidden_dim'], model['max_seq_len']), (24, 1024, 4096))
        self.assertEqual(model['memory_block_indices'], [1, 14])
        self.assertEqual(model['memory_variant'], 'context_key')
        self.assertEqual(model['memory_addressing'], 'prime_xor_v1')
        self.assertTrue(model['memory_independent_init'])
        self.assertNotIn('memory_token_mapping', model)
        matched = run['training']['matched_stories']
        self.assertNotIn('frozen_update_ends', matched)
        self.assertNotIn('target_group_transition', matched)
        self.assertEqual(matched['targets_per_update'], 131072)
        self.assertEqual(matched['document_batching'], 'padded')
        self.assertFalse(run['checkpoint']['keep_periodic'])
        self.assertEqual(run['checkpoint']['retention']['max_generations'], 4)

    def test_full_mixture_and_all_pillars_remain_explicit(self):
        plan = binder.read(PLAN)
        mixture = binder.read(PACKAGE / 'mixture.template.json')
        floors = binder.read(PACKAGE / 'token-floors.template.json')
        self.assertEqual(sum(mixture['target_quotas'].values()), plan['recipe']['unique_training_targets'])
        self.assertEqual(mixture['target_quotas'], floors['min_unique_train_tokens_by_domain'])
        self.assertEqual(mixture['max_exposures'], 1)
        self.assertEqual(set(mixture['target_quotas']), {p['name'] for p in bindings(Path('/fixture'))['evaluation']['panels']})


@unittest.skipUnless(os.environ.get('WORKSHOP_LAB_CHECKOUT'), 'requires installed compatible Lab')
class NativeFreshRecipe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(Path(os.environ['WORKSHOP_LAB_CHECKOUT']) / 'src'))

    def test_native_schema_full_model_and_five_panels(self):
        from klab.config.models import RunConfig
        from klab.model.inspection import parameter_inventory
        config = RunConfig.model_validate(binder.assemble(PLAN, bindings(Path('/fixture'))))
        self.assertEqual(len(config.evaluation.panels), 5)
        self.assertEqual(config.evaluation.batch_limit, 320)
        self.assertGreater(parameter_inventory(config).total, 341885952)
        bad = config.model_dump(mode='json')
        bad['evaluation']['panels'][1]['name'] = bad['evaluation']['panels'][0]['name']
        with self.assertRaises(ValueError):
            RunConfig.model_validate(bad)

    def test_bind_mapping_and_exclusive_native_derivation(self):
        from klab.config.loading import load_config
        from klab.derivation import derive_config
        from klab.memory_tokenizer import build_memory_token_map
        from tokenizers import Tokenizer, models
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # Full vocabulary shape but invented fixture tokens, not a fitted tokenizer.
            vocabulary = {'<unk>': 0, **{f'fixture_{i}': i for i in range(1,32768)}}
            tokenizer = Tokenizer(models.WordLevel(vocabulary, unk_token='<unk>'))
            tokenizer.save(str(root / 'tokenizer.json'))
            source = root / 'bindings.json'
            source.write_text(json.dumps(bindings(root)))
            bound = root / 'packing.json'
            result = binder.bind(PLAN, source, bound)
            self.assertTrue(result['schema_valid'])
            self.assertFalse(result['artifacts_verified'])
            self.assertFalse(result['launched'])
            original = bound.read_bytes()
            mapping = build_memory_token_map(root / 'tokenizer.json', mode='identity')
            output = root / 'mapped.yaml'
            derive_config(bound, output, {'model.memory_token_mapping': mapping.to_dict()})
            self.assertEqual(load_config(output).model.memory_token_mapping.token_ids, tuple(range(32768)))
            self.assertEqual(bound.read_bytes(), original)
            runtime = root / 'runtime.yaml'
            derive_config(output, runtime, binder.read(PACKAGE / 'runtime-xpu.delta.json'))
            self.assertEqual(load_config(runtime).runtime.secondary_device_indices, (1,))
            with self.assertRaises(FileExistsError):
                binder.bind(PLAN, source, bound)

    def test_native_mixture_probe_and_command_contracts(self):
        from klab.corpus.mixture import MixtureDeclaration
        from klab.probes.config import load_probe_config
        from klab.cli.main import build_parser
        declaration = binder.read(PACKAGE / 'mixture.template.json')
        declaration['tokenizer_origin_release_id'] = 'b' * 64
        self.assertEqual(MixtureDeclaration.model_validate(declaration).max_exposures, 1)
        for name in ('standard', 'full', 'final'):
            policy = load_probe_config(str(PACKAGE / f'probe-{name}.json'))
            self.assertEqual(policy.final, name == 'final')
        with tempfile.TemporaryDirectory() as directory:
            parser = build_parser(work_dir=Path(directory))
            cases = [
                ['tokenizer','memory-map','/fixture/tokenizer.json','--mode','identity','--output','/fixture/map.json','--bind-config','/fixture/packing.json','--config-output','/fixture/mapped.yaml'],
                ['data','prepared-inputs','publish','/fixture/mapped.yaml','--output','/fixture/prepared'],
                ['data','prepared-inputs','verify','/fixture/mapped.yaml','/fixture/prepared'],
                ['config','derive','/fixture/mapped.yaml','--set','runtime.secondary_device_indices=[1]','--output','/fixture/runtime.yaml'],
                ['stage','/fixture/final.yaml','--through','validate','--prepared-inputs','/fixture/prepared','--cold-verify','--output','/fixture/stage'],
                ['config','schedule','/fixture/mapped.yaml','--prepared-inputs','/fixture/prepared','--output','/fixture/final.yaml'],
                ['checkpoint','verify','/fixture/checkpoint','--config','/fixture/final.yaml','--json'],
                ['train','/fixture/final.yaml','--run-id','fresh-v2'],
                ['train','/fixture/final.yaml','--run-id','v2-recovery','--resume','/fixture/checkpoint'],
                ['probe','/fixture/checkpoint','--backend','cpu','--config',str(PACKAGE / 'probe-standard.json'),'--json'],
                ['report','fresh-v2','--kind','run','--json'],
            ]
            for argv in cases:
                with self.subTest(command=argv[:3]):
                    self.assertTrue(callable(parser.parse_args(argv).handler))
            # Do not invoke handlers: no workload or artifact-readiness claim.
