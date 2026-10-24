# Focused LM declarations and optional native routing; no acquisition or build.
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "experiments/devmind/preparation/lab86"


class LmBuildDeclarations(unittest.TestCase):
    def test_build_references_packaged_native_lm_transform(self):
        reference = "transforms/000-lm-text.yaml"
        self.assertIn(reference, (PACKAGE / "project-build.template.yaml").read_text())
        self.assertTrue((PACKAGE / reference).is_file())


@unittest.skipUnless(os.environ.get("WORKSHOP_LAB_CHECKOUT"), "requires current Lab checkout")
class NativeLmBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(Path(os.environ["WORKSHOP_LAB_CHECKOUT"]) / "src"))

    def test_full_admitted_lm_project_selects_bounded_builder_without_reacquisition(self):
        import yaml
        from sparselab.corpus.acquisition import _project_sha
        from sparselab.corpus.pipeline import _ordered_transforms, _uses_disk_lm_builder
        from sparselab.corpus.project import load_project

        acquired = load_project(PACKAGE / "project-acquire.yaml")
        with tempfile.TemporaryDirectory() as directory:
            recipe = Path(directory) / "recipe"
            shutil.copytree(PACKAGE, recipe)
            template = yaml.safe_load((recipe / "project-build.template.yaml").read_text())
            template["splits"] = "splits-pre-freeze.yaml"
            template["release"] = "release-schema-fixture.json"
            release = yaml.safe_load((recipe / "release-quarantine.yaml").read_text())
            # Only schema/routing is tested; no reviewed admission or data use is asserted.
            release["lm"] = {"selected": True, "training_splits": ["train", "validation"]}
            release["chat"] = {"selected": False, "training_splits": []}
            release["record_admission"] = {"path": "admission-schema-fixture.json", "sha256": "0" * 64}
            (recipe / template["release"]).write_text(json.dumps(release))
            path = recipe / "project-build.yaml"
            path.write_text(yaml.safe_dump(template))
            prepared = load_project(path)

        transforms = _ordered_transforms(prepared)
        self.assertEqual(len(transforms), 1)
        self.assertEqual(transforms[0].kind, "lm_text")
        self.assertEqual(transforms[0].inputs, ())
        self.assertEqual(transforms[0].parameters, {})
        self.assertTrue(_uses_disk_lm_builder(prepared, transforms))
        self.assertEqual(prepared.sources, acquired.sources)
        self.assertEqual(prepared.config.source_effects, acquired.config.source_effects)
        self.assertEqual(_project_sha(prepared), _project_sha(acquired))
