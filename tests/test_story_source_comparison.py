"""Offline scientific invariants and contamination fixtures; no model execution."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "experiments/story-source-comparison"
spec = importlib.util.spec_from_file_location("audit_story", ROOT / "scripts/audit-story-splits.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def read(name):
    return json.loads((RECIPE / name).read_text())


class StoryComparison(unittest.TestCase):
    def test_only_source_and_name_vary(self):
        a, b = (read(f"run-{arm}.json") for arm in ("tinystories", "simplestories"))
        for run in (a, b):
            run.pop("name")
            data = run.pop("dataset")
            for field in ("revision", "license", "cache_dir", "train_path", "validation_path", "source_manifest_path"):
                data.pop(field)
            run["common_dataset_policy"] = data
        self.assertEqual(a, b)

    def test_budget_and_retained_checkpoints(self):
        protocol = read("protocol.json")
        run = read("run-tinystories.json")
        training = run["training"]
        batch = training["seq_len"] * training["micro_batch_size"] * training["gradient_accumulation"]
        self.assertEqual(batch, 4096)
        self.assertEqual(training["max_tokens"], batch * training["max_steps"])
        self.assertEqual(run["optimizer"]["decay_steps"], training["max_steps"])
        for item in protocol["checkpoints"]:
            self.assertEqual(item["committed_targets"], item["step"] * batch)
            self.assertIn(item["step"], run["checkpoint"]["steps"])
        retained = {m["step"] for m in run["checkpoint"]["retention"]["milestones"]}
        self.assertTrue(set(protocol["quality_steps"]) <= retained | {training["max_steps"]})
        self.assertEqual(protocol["generation_outputs_expected"],
                         2 * len(protocol["quality_steps"]) * len(read("prompts.json")["prompts"]) * 2)

    def test_source_mapping_and_pending_evidence(self):
        simple = read("source-simplestories.json")
        self.assertEqual(simple["text_field"], "story")
        self.assertEqual(simple["splits"], {"train": "train", "validation": "test"})
        for arm in ("tinystories", "simplestories"):
            source, run = read(f"source-{arm}.json"), read(f"run-{arm}.json")
            self.assertRegex(source["revision"], r"^[a-f0-9]{40}$")
            self.assertEqual(source["revision"], run["dataset"]["revision"])
            self.assertEqual(source["license"], run["dataset"]["license"])
        self.assertIsNone(read("protocol.json")["results"])

    def fixture(self, root):
        roots = {arm: root / arm for arm in ("tinystories", "simplestories")}
        for i, path in enumerate(roots.values()):
            path.mkdir()
            for split in ("train", "validation"):
                (path / f"{split}.jsonl").write_text(json.dumps({"text": f"{i} {split} story"}) + "\n")
        return roots

    def test_clean_then_cross_source_and_prompt_leak(self):
        panel = {"prompts": [{"id": "p", "prompt": "secret phrase"}]}
        with tempfile.TemporaryDirectory() as directory:
            roots = self.fixture(Path(directory))
            self.assertEqual(audit.audit(roots, panel)["status"], "pass")
            path = roots["simplestories"] / "train.jsonl"
            path.write_text(json.dumps({"text": "0 validation story"}) + "\n" +
                            json.dumps({"text": "prefix secret phrase suffix"}) + "\n")
            result = audit.audit(roots, panel)
            self.assertEqual(result["status"], "blocked")
            self.assertEqual(result["train_to_holdout_matches"]["simplestories"]["tinystories"], 1)
            self.assertEqual(result["prompt_substring_matches"]["simplestories"]["p"], 1)

    def test_empty_input_and_duplicate_holdout_refuse(self):
        panel = {"prompts": [{"id": "p", "prompt": "unseen"}]}
        with tempfile.TemporaryDirectory() as directory:
            roots = self.fixture(Path(directory))
            path = roots["tinystories"] / "validation.jsonl"
            path.write_text(path.read_text() * 2)
            self.assertEqual(audit.audit(roots, panel)["status"], "blocked")
            path.write_text("")
            with self.assertRaisesRegex(ValueError, "Empty validation"):
                audit.audit(roots, panel)


@unittest.skipUnless(os.environ.get("WORKSHOP_LAB_CHECKOUT"), "requires pinned Lab source and pydantic")
class NativeSchema(unittest.TestCase):
    def test_native_configs_and_rejection_of_changed_retention_boundary(self):
        sys.path.insert(0, str(Path(os.environ["WORKSHOP_LAB_CHECKOUT"]) / "src"))
        from sparselab.config.models import RunConfig
        for arm in ("tinystories", "simplestories"):
            raw = read(f"run-{arm}.json")
            RunConfig.model_validate(raw)
            bad = copy.deepcopy(raw)
            bad["training"]["max_tokens"] += 1
            with self.assertRaises(ValueError):
                RunConfig.model_validate(bad)


if __name__ == "__main__":
    unittest.main()
