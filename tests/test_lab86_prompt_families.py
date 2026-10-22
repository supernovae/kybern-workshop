"""Offline native schema checks; no acquisition or model workload."""
import os
from pathlib import Path
import sys
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "experiments/devmind/preparation/lab86"


@unittest.skipUnless(os.environ.get("WORKSHOP_LAB_CHECKOUT"), "requires current Lab checkout")
class NativePromptFamilies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(Path(os.environ["WORKSHOP_LAB_CHECKOUT"]) / "src"))

    def test_pre_freeze_prompt_rule_keeps_acquisition_declarations(self):
        import yaml
        from sparselab.corpus.project import load_project

        acquired = load_project(PACKAGE / "project-acquire.yaml")
        with tempfile.TemporaryDirectory() as directory:
            recipe = Path(directory) / "recipe"
            shutil.copytree(PACKAGE, recipe)
            template = yaml.safe_load((recipe / "project-pre-freeze.template.yaml").read_text())
            self.assertEqual(template["splits"], "splits-pre-freeze.yaml")
            # Schema-only fixture: no reviewed admission or data use is asserted.
            template["release"] = "release-quarantine.yaml"
            path = recipe / "project-pre-freeze.yaml"
            path.write_text(yaml.safe_dump(template))
            prepared = load_project(path)
        synthetic = {source.id for source in prepared.sources
                     if source.acquisition.qualification.profile == "synthetic_text"}
        self.assertEqual(len(synthetic), 14)
        self.assertEqual(prepared.splits.family_fields_by_source,
                         {source_id: ("prompt",) for source_id in synthetic})
        self.assertTrue(all(source.acquisition.qualification.family_fields == ("seed_data",)
                            for source in prepared.sources if source.id in synthetic))
        self.assertEqual(acquired.sources, prepared.sources)
        self.assertEqual(acquired.config.id, prepared.config.id)
        self.assertEqual(acquired.config.source_effects, prepared.config.source_effects)

    def test_acquisition_declarations_do_not_inherit_the_full_family_map(self):
        from sparselab.corpus.project import load_project

        for name in ("project-acquire.yaml", "project-pilot-acquire.json"):
            with self.subTest(project=name):
                project = load_project(PACKAGE / name)
                self.assertEqual(project.splits.family_fields_by_source, {})
