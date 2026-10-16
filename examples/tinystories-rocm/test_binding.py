"""Binder fixtures only; never call native handlers or Docker."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import bind_session as b


class BindingTests(unittest.TestCase):
    def test_bind_and_actual_report_no_clobber(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
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


if __name__ == "__main__":
    unittest.main()
