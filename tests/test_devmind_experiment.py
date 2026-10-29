"""Run authoring contract; generated bindings only, never execute a model."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / 'experiments/devmind/experiment.json'
spec = importlib.util.spec_from_file_location('bind_experiment', ROOT / 'scripts/bind-experiment.py')
binder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(binder)


def fixture_bindings(root):
    """Synthetic path/count contract, explicitly not artifact readiness evidence."""
    bindings = binder.read(PLAN.with_name('binding.example.json'))
    bindings['dataset'].update(
        mixture_declaration_path=str(root / 'mixture.yaml'),
        mixture_output_path=str(root / 'mixture'), cache_dir=str(root / 'cache'),
        train_path=str(root / 'mixture/train.jsonl'),
        validation_path=str(root / 'mixture/validation.jsonl'),
        train_max_documents=12, validation_max_documents=3,
        train_max_tokens=12000000000, validation_max_tokens=262145,
        license='synthetic fixture only')
    bindings['tokenizer']['path'] = str(root / 'tokenizer.json')
    bindings['logging']['root_dir'] = str(root / 'runs')
    bindings['runtime']['backend'] = 'cpu'
    return bindings


class ExperimentContract(unittest.TestCase):
    def test_baseline_and_full_model_are_not_smoke_settings(self):
        run = binder.assemble(PLAN, fixture_bindings(Path('/fixture')))
        self.assertEqual(run['model'], binder.read(PLAN.with_name('model.json')))
        self.assertEqual(run['training']['max_tokens'], 12000000000)
        self.assertEqual(run['training']['micro_batch_size'], 2)
        self.assertEqual(run['training']['gradient_accumulation'], 32)
        self.assertEqual(run['runtime']['memory']['estimate_policy'], 'observe')
        self.assertEqual(binder.read(PLAN)['recipe']['mixture'],
                         {'web': .6, 'synthetic': .2, 'code': .2})

    def test_unbound_example_refuses(self):
        with self.assertRaisesRegex(ValueError, 'Unbound'):
            binder.assemble(PLAN, binder.read(PLAN.with_name('binding.example.json')))

    def test_missing_section_and_relative_path_refuse(self):
        bindings = fixture_bindings(Path('/fixture'))
        del bindings['runtime']
        with self.assertRaisesRegex(ValueError, 'sections'):
            binder.assemble(PLAN, bindings)
        bindings = fixture_bindings(Path('/fixture'))
        bindings['tokenizer']['path'] = 'tokenizer.json'
        with self.assertRaisesRegex(ValueError, 'absolute'):
            binder.assemble(PLAN, bindings)


@unittest.skipUnless(os.environ.get('WORKSHOP_LAB_CHECKOUT'), 'requires installed Lab')
class NativeExperimentContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(Path(os.environ['WORKSHOP_LAB_CHECKOUT']) / 'src'))

    def test_bind_inventory_derive_and_native_commands_without_execution(self):
        from sparselab.config.loading import load_config
        from sparselab.derivation import derive_config
        from sparselab.model.inspection import parameter_inventory
        from sparselab.cli.main import build_parser
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = root / 'bindings.json'
            inputs.write_text(json.dumps(fixture_bindings(root)))
            output = root / 'run.json'
            result = binder.bind(PLAN, inputs, output)
            self.assertTrue(result['schema_valid'])
            self.assertFalse(result['artifacts_verified'])
            original = output.read_bytes()
            config = load_config(output)
            inventory = parameter_inventory(config)
            self.assertEqual(inventory.total, 341885952)
            with self.assertRaises(FileExistsError):
                binder.bind(PLAN, inputs, output)
            variant = root / 'first32.yaml'
            derive_config(output, variant, {
                'name': 'devmind-340m-first32', 'training.max_steps': 32,
                'training.max_tokens': 4194304, 'optimizer.warmup_steps': 4,
                'optimizer.decay_steps': 32, 'checkpoint.every_steps': 4,
                'evaluation.every_steps': 32})
            child = load_config(variant)
            self.assertEqual(child.model, config.model)
            self.assertEqual(child.training.max_tokens, 4194304)
            self.assertEqual(output.read_bytes(), original)
            parser = build_parser(work_dir=root)
            checkpoint = str(root / 'runs/parent/checkpoint/generation')
            cases = [
                (['train', str(output), '--run-id', 'parent'], '_train'),
                (['inspect', str(output), '--json'], '_inspect'),
                (['checkpoint', 'verify', checkpoint, '--config', str(output), '--json'], '_checkpoint_verify'),
                (['train', str(output), '--resume', checkpoint, '--run-id', 'child'], '_train'),
                (['eval', 'child', '--checkpoint', checkpoint, '--runs-dir', str(root / 'runs')], '_eval')]
            for argv, handler in cases:
                parsed = parser.parse_args(argv)
                self.assertEqual(parsed.handler.__name__, handler)
                self.assertTrue(callable(parsed.handler))
            # Intentionally never call any handler: no training, eval or artifact claim.

    def test_native_schema_rejects_incompatible_binding_without_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bindings = fixture_bindings(root)
            bindings['runtime']['backend'] = 'imaginary'
            inputs = root / 'bindings.json'
            inputs.write_text(json.dumps(bindings))
            output = root / 'run.json'
            with self.assertRaises(ValueError):
                binder.bind(PLAN, inputs, output)
            self.assertFalse(output.exists())
