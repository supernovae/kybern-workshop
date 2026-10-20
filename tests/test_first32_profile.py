"""First-run declarations only; native checks use an existing installed Lab."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "experiments/devmind/first32"

class First32Declaration(unittest.TestCase):
    def test_fixed_budget_and_model_identity(self):
        profile = json.loads((PACKAGE / "profile.json").read_text())
        self.assertEqual(profile["training_targets"], 32 * 2048 * 2 * 32)
        self.assertEqual(sum(profile["target_quotas"].values()), profile["training_targets"])
        self.assertEqual(profile["selection"]["max_rows"], 30000)
        self.assertEqual(profile["selection"]["max_bytes"], 100 * 1024**2)
        self.assertEqual(profile["max_exposures"], 1)
        model = ROOT / "experiments/devmind/model.json"
        self.assertEqual(hashlib.sha256(model.read_bytes()).hexdigest(), profile["model_sha256"])

@unittest.skipUnless(os.environ.get("WORKSHOP_LAB_CHECKOUT"), "requires installed subset-capable Lab")
class NativeFirst32Declaration(unittest.TestCase):
    def test_phase_map_uses_only_native_preparation_commands(self):
        sys.path.insert(0, str(Path(os.environ["WORKSHOP_LAB_CHECKOUT"]) / "src"))
        from sparselab.training.preparation import compile_phase, load_preparation
        from sparselab.cli.main import build_parser
        plan_path = PACKAGE / "preparation.json"
        plan = load_preparation(plan_path)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for label, phase in plan["phases"].items():
                keys = {v[2:-1] for v in phase["args"] if v.startswith("${")}
                bindings = {k: str(root / k) for k in keys - plan["defaults"].keys()}
                compiled = compile_phase(plan_path, root, label, bindings)
                build_parser().parse_args(compiled["args"])
                self.assertNotIn("budget-init", compiled["args"])
                self.assertNotIn("train", compiled["args"][:1])
        self.assertEqual(plan["defaults"]["MAX_INPUT_BYTES"], "104857600")
        self.assertEqual(plan["phases"]["freeze-splits"]["leaf"], "splits-reviewed.yaml")

    def test_rendered_acquisition_and_export_base_use_native_schemas(self):
        sys.path.insert(0, str(Path(os.environ["WORKSHOP_LAB_CHECKOUT"]) / "src"))
        import yaml
        from sparselab.corpus.project import load_project
        from sparselab.config.loading import load_config
        from sparselab.corpus.declaration_render import render_declaration
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            recipe = root / "recipe"
            shutil.copytree(PACKAGE, recipe)
            for index, name in enumerate(["000-web", "001-synthetic", "002-code"]):
                destination = recipe / "sources" / (name + ".yaml")
                destination.unlink()
                render_declaration(PACKAGE / "sources" / (name + ".yaml"), json.dumps({
                    f"PARENT_{index}_PATH": str(root / ("fixture-parent-" + str(index))),
                    f"PARENT_{index}_SHA256": "a" * 64,
                    f"PARENT_{index}_MANIFEST_SHA256": "b" * 64,
                }), destination, root)
            project = load_project(recipe / "project-acquire.yaml")
            self.assertEqual(len(project.sources), 3)
            self.assertIsNone(project.config.transport_budget)
            self.assertIsNone(project.config.source_effects)
            self.assertEqual(sum(s.acquisition.max_rows for s in project.sources), 30000)
            self.assertEqual(sum(s.acquisition.max_bytes for s in project.sources), 100 * 1024**2)
            self.assertEqual([s.acquisition.text_field for s in project.sources], ["text", "text", "code"])
            for source in project.sources:
                self.assertEqual(source.acquisition.retained_subset.seed, 86)
                self.assertEqual(source.acquisition.retained_subset.max_record_bytes, 256 * 1024)
            run = load_config(recipe / "base-run.yaml")
            self.assertEqual(run.dataset.source, "local_text")
            self.assertFalse(run.dataset.train_path.exists())
            self.assertEqual(run.training.max_steps, 32)
            self.assertEqual(run.training.max_tokens, 4194304)
            self.assertEqual(run.runtime.backend, "rocm")
            self.assertEqual(run.checkpoint.steps, (4, 32))
            expected = json.loads((ROOT / "experiments/devmind/model.json").read_text())
            self.assertEqual(yaml.safe_load((recipe / "base-run.yaml").read_text())["model"], expected)

if __name__ == "__main__":
    unittest.main()
