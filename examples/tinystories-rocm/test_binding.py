"""Binder fixtures only; never call native handlers or Docker."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import bind_session as b


def prepared_fixture(root):
    target = root / "inputs" / "packed" / b.h.PACKED
    target.mkdir(parents=True)
    (target / "manifest.json").write_bytes(
        (Path(__file__).parent / "cache-rebuild/manifest.json").read_bytes())


class BindingTests(unittest.TestCase):
    def test_bind_and_actual_report_no_clobber(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prepared_fixture(root)
            checkout = root / "checkout"
            recipe = checkout / "examples/tinystories-rocm"
            recipe.mkdir(parents=True)
            for name in ("run.json", "plan.json"):
                (recipe / name).write_bytes((b.h.ROOT / name).read_bytes())

            def git(path, *args):
                return "a" * 40 if args == ("rev-parse", "HEAD") else ""

            with patch.object(b, "git", git), patch.object(b.h, "ROOT", recipe):
                result = b.bind(
                    checkout,
                    root / "harness",
                    root / "inputs",
                    root / "state",
                    root / "receipts",
                    {
                        "python": b.h.PINS["python_version"],
                        "executable_sha256": "b" * 64,
                    },
                    "fixture",
                    "a" * 40,
                    "owner",
                    "task:bounded-fixture",
                    "boot",
                )
            self.assertFalse(result["execution_enabled"])
            self.assertIn("--harness-commit", result["wrapper_argv"])
            state = root / "state"
            session = json.loads((state / "session.json").read_text())
            self.assertEqual(
                [x["step"] for x in session["slots"]],
                [
                    "copy-inputs",
                    "validate",
                    "apply",
                    "approve",
                    "run",
                    "status",
                    "report",
                ],
            )
            self.assertEqual(session["limits"]["wall_seconds"], 1800)
            self.assertEqual(session["command_policy"], "observe_stages")
            for step in ("apply", "run"):
                argv = json.loads((state / (step + ".json")).read_text())["argv"]
                self.assertEqual(argv[argv.index("--max-wait-seconds") + 1], "1800")
            for name in ("lock", "index"):
                (state / name).write_text("{}")
            (state / "workspace").mkdir()
            result = b.report(
                state, state / "lock", state / "workspace", state / "index"
            )
            job = json.loads(Path(result["job"]).read_text())
            self.assertEqual(
                job["argv"][4:8], ["experiment", "recipe", "workflow", "report"]
            )
            self.assertIn(str(state / "lock"), job["required_files"])
            with self.assertRaises(FileExistsError):
                b.report(state, state / "lock", state / "workspace", state / "index")
            with self.assertRaises(ValueError):
                b.report(state, root / "outside", state / "workspace", state / "index")


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        prepared_fixture(self.root)
        self.checkout = self.root / "checkout"
        self.recipe = self.checkout / "examples/tinystories-rocm"
        self.recipe.mkdir(parents=True)
        for name in ("run.json", "plan.json"):
            (self.recipe / name).write_bytes((b.h.ROOT / name).read_bytes())
        self.args = dict(
            checkout=self.checkout,
            harness=self.root / "harness",
            inputs=self.root / "inputs",
            state=self.root / "state",
            receipts=self.root / "receipts",
            runtime={
                "python": b.h.PINS["python_version"],
                "executable_sha256": "b" * 64,
            },
            job_id="fixture",
            reviewed_commit="a" * 40,
            owner="owner",
            approval_reference="task:bounded-fixture",
            boot_id="boot",
        )
        self.git_values = {}

        def git(path, *args):
            return self.git_values.get(
                (path, args), "a" * 40 if args == ("rev-parse", "HEAD") else ""
            )

        for patcher in (
            patch.object(b, "git", git),
            patch.object(b.h, "ROOT", self.recipe),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def refuse(self, message):
        with self.assertRaisesRegex(ValueError, message):
            b.bind(**self.args)
        self.assertFalse((self.args["state"] / "session.json").exists())

    def test_directory_manifest_refuses_before_state_or_receipts(self):
        manifest = self.args["inputs"] / "packed" / b.h.PACKED / "manifest.json"
        manifest.unlink()
        manifest.mkdir()
        self.refuse("bounded regular prepared manifest required")
        self.assertFalse(self.args["state"].exists())
        self.assertFalse(self.args["receipts"].exists())

    def test_stale_prepared_source_refuses_before_state_or_receipts(self):
        manifest = self.args["inputs"] / "packed" / b.h.PACKED / "manifest.json"
        doc = json.loads(manifest.read_text())
        doc["cache_identity"]["source_identity_sha256"] = "8d125d1207f2885e19efab0621e57db4cf75f7419eadfad92e5256b65fe6836b"
        manifest.write_text(json.dumps(doc))
        with patch.dict(b.h.PINS, packed_manifest_byte_sha256=b.h.hash_file(manifest)):
            self.refuse("prepared cache source")
        self.assertFalse(self.args["state"].exists())
        self.assertFalse(self.args["receipts"].exists())

    def test_wrong_workshop_head(self):
        self.git_values[(self.checkout, ("rev-parse", "HEAD"))] = "c" * 40
        self.refuse("clean reviewed Workshop")

    def test_dirty_workshop(self):
        self.git_values[(self.checkout, ("status", "--porcelain"))] = " M run.json"
        self.refuse("clean reviewed Workshop")

    def test_wrong_binder_checkout(self):
        with patch.object(b.h, "ROOT", self.root / "other"):
            self.refuse("selected checkout")

    def test_dirty_harness(self):
        self.git_values[(self.args["harness"], ("status", "--porcelain"))] = (
            " M docker_session.py"
        )
        self.refuse("clean reviewed harness")

    def test_missing_owner_and_boot(self):
        for key in ("owner", "boot_id"):
            with self.subTest(key=key):
                original = self.args[key]
                self.args[key] = " "
                self.refuse("owner and observed boot")
                self.args[key] = original

    def test_wrong_runtime(self):
        self.args["runtime"]["python"] = "0.0.0"
        self.refuse("image Python pin")

    def test_existing_receipts(self):
        self.args["receipts"].mkdir()
        self.refuse("fresh receipt")

    def test_equal_and_nested_roots(self):
        for key, value in (
            ("harness", self.checkout),
            ("harness", self.checkout / "nested"),
            ("receipts", self.args["state"]),
            ("receipts", self.args["state"] / "nested"),
        ):
            with self.subTest(key=key, value=value):
                old = self.args[key]
                self.args[key] = value
                self.refuse("disjoint roots")
                self.args[key] = old

    def test_training_budget_guards(self):
        path = self.recipe / "run.json"
        original = json.loads(path.read_text())
        for section, key, value in (
            ("staging", "smoke_steps", 3),
            ("staging", "warmup_steps", 6),
            ("training", "max_steps", 2),
        ):
            with self.subTest(key=key):
                run = json.loads(json.dumps(original))
                run[section][key] = value
                path.write_text(json.dumps(run))
                self.refuse("16-update")

    def test_evaluation_and_arm_guards(self):
        path = self.recipe / "run.json"
        original = json.loads(path.read_text())
        for key in ("every_steps", "max_batches"):
            run = json.loads(json.dumps(original))
            run["evaluation"][key] = 2
            path.write_text(json.dumps(run))
            self.refuse("evaluation ceiling")
        path.write_text(json.dumps(original))
        path = self.recipe / "plan.json"
        original = json.loads(path.read_text())
        for mutation in ("extra-axis", "extra-arm", "wrong-width"):
            plan = json.loads(json.dumps(original))
            if mutation == "extra-axis":
                plan["axes"].append(plan["axes"][0])
            elif mutation == "extra-arm":
                plan["axes"][0]["choices"].append(plan["axes"][0]["choices"][0])
            else:
                plan["axes"][0]["choices"][1]["set"]["model.ffn_dim"] = 128
            path.write_text(json.dumps(plan))
            self.refuse("evaluation ceiling")

    def test_exact_generated_profile_allowances_and_offline_environment(self):
        result = b.bind(**self.args)
        session = json.loads(Path(result["session"]).read_text())
        self.assertEqual(session["schema"], 3)
        self.assertEqual(session["limits"]["shutdown_reserve_seconds"], 20)
        self.assertEqual(
            [s["allowance_seconds"] for s in session["slots"]],
            [30, 10, 30, 10, 1640, 10, 10],
        )
        self.assertNotIn("--gpu", result["wrapper_argv"])
        for request in json.loads(Path(result["requests"]).read_text()):
            job = json.loads(Path(request["job"]).read_text())
            for key in (
                "HF_HUB_OFFLINE",
                "HF_DATASETS_OFFLINE",
                "TRANSFORMERS_OFFLINE",
                "UV_OFFLINE",
            ):
                self.assertEqual(job["environment"][key], "1")
            self.assertEqual(
                job["limits"]["wall_seconds"],
                next(
                    s["allowance_seconds"]
                    for s in session["slots"]
                    if s["id"] == request["slot"]
                ),
            )

    def test_existing_external_report_paths_refuse_before_write(self):
        b.bind(**self.args)
        state = self.args["state"]
        workspace = state / "workspace"
        workspace.mkdir()
        lock = state / "lock"
        index = state / "index"
        lock.write_text("{}")
        index.write_text("{}")
        outside_file = self.root / "outside.json"
        outside_file.write_text("{}")
        outside_dir = self.root / "outside-workspace"
        outside_dir.mkdir()
        for paths in (
            (outside_file, workspace, index),
            (lock, outside_dir, index),
            (lock, workspace, outside_file),
        ):
            with self.subTest(paths=paths):
                with self.assertRaisesRegex(ValueError, "within state"):
                    b.report(state, *paths)
                self.assertFalse((state / "report.json").exists())


if __name__ == "__main__":
    unittest.main()
