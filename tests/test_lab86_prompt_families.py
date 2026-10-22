"""Offline native schema check; no acquisition or model workload."""
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "experiments/devmind/preparation/lab86"


@unittest.skipUnless(os.environ.get("WORKSHOP_LAB_CHECKOUT"), "requires current Lab checkout")
class NativePromptFamilies(unittest.TestCase):
    def test_exact_prompt_rule_preserves_acquisition_identity(self):
        sys.path.insert(0, str(Path(os.environ["WORKSHOP_LAB_CHECKOUT"]) / "src"))
        from sparselab.corpus.acquisition import _project_sha
        from sparselab.corpus.project import SplitDeclaration, load_project

        project = load_project(PACKAGE / "project-acquire.yaml")
        synthetic = {source.id for source in project.sources
                     if source.acquisition.qualification.profile == "synthetic_text"}
        self.assertEqual(len(synthetic), 14)
        self.assertEqual(project.splits.family_fields_by_source,
                         {source_id: ("prompt",) for source_id in synthetic})
        self.assertTrue(all(source.acquisition.qualification.family_fields == ("seed_data",)
                            for source in project.sources if source.id in synthetic))
        original = project.splits.model_dump(mode="python")
        original.pop("family_fields_by_source")
        without_override = project.model_copy(update={"splits": SplitDeclaration.model_validate(original)})
        self.assertEqual(_project_sha(project), _project_sha(without_override))
