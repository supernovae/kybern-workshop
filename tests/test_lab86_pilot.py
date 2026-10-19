"""Offline pilot declarations; optional native ledger checks, never acquisition.

Run native checks with WORKSHOP_LAB_CHECKOUT pointing at a reviewed installed Lab
checkout. No dependencies are installed by this suite.
"""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "experiments/devmind/preparation/lab86"
SOURCES = {
    "sources/000-web.yaml": "63cc6086e2c68a9e17e84e35565954edaf6692194c295df12985d43799931341",
    "sources/001-synthetic.yaml": "865b08dc83e2086eec1483900b465e96b9481f55fb48d2a6fc3e32582f7a4c0e",
    "sources/002-code.yaml": "c0714ab0ffe9347c83620d126c6249952aea793ccc00ced3cac55a04bd5fa6df",
}

def read(name):
    return json.loads((PACKAGE / name).read_text())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

class PilotDeclarations(unittest.TestCase):
    def test_exact_sources_and_unchanged_policy(self):
        project = read("project-pilot-acquire.json")
        self.assertEqual(project["sources"], list(SOURCES))
        self.assertEqual([x["source_id"] for x in project["source_effects"]],
                         ["lab86_000_web", "lab86_001_synthetic", "lab86_002_code"])
        self.assertTrue(all(x["effect"] == "acquire" for x in project["source_effects"]))
        for name, expected in SOURCES.items():
            self.assertEqual(digest(PACKAGE / name), expected)
        self.assertEqual(digest(PACKAGE / "POLICY.md"),
                         "fc58397302ecc28f973d09c0a922fde390feab400201c2d6e888b12cf4c3cbfb")
        self.assertEqual(digest(PACKAGE / "project-acquire.yaml"),
                         "c1e7e031aa9ed81a8304c7fc1e77afdd89ae4ed4dd8eb3c3b18400725d235ba8")

    def test_limits_and_contract_binding(self):
        budget = read("project-pilot-acquire.json")["transport_budget"]
        self.assertEqual(budget["initial_body_bytes"], 4 * 1024**3)
        self.assertEqual(budget["max_disk_bytes"], 300 * 1024**3)
        self.assertEqual(budget["max_wall_seconds"], 172800)
        self.assertEqual(budget["max_total_body_bytes"], 100 * 1024**3)
        content = read("pilot-content.json")
        contract = read("pilot-contract.template.json")
        self.assertEqual(content["acquisition_project_file_sha256"], digest(PACKAGE / "project-pilot-acquire.json"))
        self.assertEqual(contract["acquisition_project_sha256"], content["acquisition_project_file_sha256"])
        self.assertEqual(contract["content_identity_sha256"], digest(PACKAGE / "pilot-content.json"))
        self.assertEqual(contract["max_wall_seconds"], budget["max_wall_seconds"])

    def test_all_pilot_dispatches_bind_subset(self):
        paths = sorted((PACKAGE / "pilot-jobs").glob("*.json")) + [PACKAGE / "pilot-session.template.json"]
        self.assertEqual(len(paths), 5)
        count = 0
        for path in paths:
            text = path.read_text()
            self.assertNotIn("${PACKAGE_ROOT}/project-acquire.yaml", text)
            value = json.loads(text)
            def visit(item):
                nonlocal count
                if isinstance(item, dict):
                    for v in item.values(): visit(v)
                elif isinstance(item, list):
                    for v in item: visit(v)
                elif isinstance(item, str) and item.startswith('{'):
                    binding = json.loads(item)
                    if "ACQUISITION_PROJECT" in binding:
                        self.assertEqual(binding["ACQUISITION_PROJECT"], "${PACKAGE_ROOT}/project-pilot-acquire.json")
                        count += 1
            visit(value)
        self.assertEqual(count, 6)

    def test_package_and_migration_hashes(self):
        manifest = read("package-sha256.json")
        self.assertIn("project-pilot-acquire.json", manifest)
        for name, expected in manifest.items():
            self.assertEqual(digest(PACKAGE / name), expected, name)
        migration = json.loads((ROOT / "experiments/devmind/migration.json").read_text())
        for entry in migration["files"]:
            self.assertEqual(digest(ROOT / entry["destination"]), entry["sha256"], entry["destination"])

@unittest.skipUnless(os.environ.get("WORKSHOP_LAB_CHECKOUT"), "requires existing reviewed Lab checkout")
class NativePilotLedger(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(Path(os.environ["WORKSHOP_LAB_CHECKOUT"]) / "src"))
        from sparselab.corpus.project import load_project
        from sparselab.corpus.transport_budget import TransportBudget
        self.load = load_project
        self.budget_type = TransportBudget
        self.project = load_project(PACKAGE / "project-pilot-acquire.json")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ledger = TransportBudget.initialize(Path(self.temp.name) / "ledger.sqlite", self.project)

    def test_native_projection_and_identity(self):
        from sparselab.corpus.acquisition import _project_sha
        self.assertEqual(self.ledger.projected_disk_bytes(), 28021704695)
        self.assertLess(self.ledger.projected_disk_bytes(), self.ledger.spec.max_disk_bytes)
        self.assertEqual(_project_sha(self.project), read("pilot-contract.template.json")["preparation_acquisition_identity_sha256"])
        full = self.load(PACKAGE / "project-acquire.yaml")
        self.assertEqual(self.project.config.transport_budget, full.config.transport_budget)
        selected = {source.id for source in self.project.sources}
        self.assertEqual(list(self.project.config.source_effects),
                         [effect for effect in full.config.source_effects if effect.source_id in selected])
        full_ledger = self.budget_type.initialize(Path(self.temp.name) / "full.sqlite", full)
        self.assertEqual(full_ledger.projected_disk_bytes(), 724028121832)
        self.assertGreater(full_ledger.projected_disk_bytes(), full_ledger.spec.max_disk_bytes)
        with self.assertRaisesRegex(ValueError, "binding changed"):
            self.budget_type(self.ledger.path, full)

    def test_cumulative_metadata_and_retry_reservations_never_reset(self):
        # Ledger entries only: no HTTP, source bytes, or model workloads.
        self.ledger.reserve_metadata(523253741)
        for source in self.project.sources:
            shard = source.acquisition.bounded_shards[0]
            self.ledger.reserve_transfer(source.id, shard.path, shard.max_shard_bytes)
        before = self.ledger.receipt()
        for action in (
            lambda: self.ledger.reserve_metadata(1),
            lambda: self.ledger.reserve_transfer(self.project.sources[0].id,
                self.project.sources[0].acquisition.bounded_shards[0].path, 1),
        ):
            with self.assertRaisesRegex(ValueError, "initial feasibility gate"):
                action()
        self.assertEqual(self.ledger.receipt(), before)
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.budget_type.initialize(self.ledger.path, self.project)
        self.assertEqual(self.budget_type(self.ledger.path, self.project).receipt(), before)

if __name__ == "__main__":
    unittest.main()
