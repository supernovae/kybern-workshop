import importlib.util
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("handoff", ROOT / "handoff.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def args(self):
        return {
            "checkout": self.root / "reviewed source",
            "inputs": self.root / "retained inputs",
            "state": self.root / "new output",
            "job_id": "fixture-one",
            "reviewed_commit": "a" * 40,
            "approval_reference": "owner record; literal $(no-shell)",
            "uid": 1000,
            "gid": 1000,
        }

    def test_exact_pins_gpu_authorization_and_argv_boundaries(self):
        result = h.render(**self.args())
        self.assertFalse(result["execution_enabled"])
        self.assertFalse(self.args()["state"].exists())
        self.assertEqual(
            [s["step"] for s in result["steps"]],
            ["copy-inputs", "validate", "apply", "approve", "run", "status"],
        )
        for step in result["steps"]:
            argv = step["argv"]
            self.assertIn(h.PINS["image"], argv)
            for flag in (
                "--network=none",
                "--pull=never",
                "--memory=4g",
                "--memory-swap=4g",
                "--cpus=2",
                "--pids-limit=256",
                "--userns=keep-id",
                "--user=1000:1000",
                "--device=/dev/dxg",
                "CUDA_VISIBLE_DEVICES=0",
                "HF_HUB_OFFLINE=1",
                "HF_DATASETS_OFFLINE=1",
                "TRANSFORMERS_OFFLINE=1",
                "UV_OFFLINE=1",
            ):
                self.assertIn(flag, argv)
            self.assertNotIn("CUDA_VISIBLE_DEVICES=", argv)
            self.assertFalse(any("/opt/rocm" in arg for arg in argv))
            self.assertIn(f"type=bind,src={self.args()['inputs']},dst=/inputs,ro", argv)
        run = result["steps"][4]["argv"]
        self.assertIn("--execute-runs", run)
        self.assertIn("--runtime-profile", run)
        self.assertEqual(run[run.index("--max-wait-seconds") + 1], "1740")
        approve = result["steps"][3]["argv"]
        self.assertEqual(
            approve[approve.index("--note") + 1], self.args()["approval_reference"]
        )
        self.assertNotIn("--runtime-profile", approve)  # Unsupported on native approve.

    def test_checked_in_recipe_preserves_owner_budget_and_gpu_bindings(self):
        run = json.loads((ROOT / "run.json").read_text())
        plan = json.loads((ROOT / "plan.json").read_text())
        campaign = json.loads((ROOT / "campaign.json").read_text())
        self.assertEqual(
            run["runtime"],
            {
                "engine": "pytorch",
                "backend": "rocm",
                "precision": "fp32",
                "device_index": 0,
            },
        )
        self.assertEqual(run["seed"], 7)
        self.assertEqual(
            [
                run["model"][k]
                for k in ("vocab_size", "hidden_dim", "num_layers", "num_heads")
            ],
            [512, 32, 1, 2],
        )
        self.assertEqual(
            [
                run["training"][k]
                for k in (
                    "seq_len",
                    "micro_batch_size",
                    "gradient_accumulation",
                    "max_steps",
                )
            ],
            [32, 1, 1, 1],
        )
        self.assertEqual(run["staging"], {"smoke_steps": 2, "warmup_steps": 5})
        self.assertEqual(run["evaluation"], {"every_steps": 1, "max_batches": 1})
        self.assertEqual(
            [v["set"] for v in plan["axes"][0]["choices"]],
            [{"model.ffn_dim": 64}, {"model.ffn_dim": 96}],
        )
        self.assertEqual(plan["execution"]["backend"], "rocm")
        self.assertEqual(
            plan["artifacts"],
            {
                s["id"]: s["artifact"]
                for s in campaign["stages"]
                if s["kind"] == "artifact_reference"
            },
        )
        self.assertEqual(len(campaign["stages"]), 12)
        for row in campaign["stages"]:
            if row["kind"] == "evaluation":
                self.assertEqual(
                    (row["backend"], row["runtime"]), ("rocm", "accept-rocm")
                )
                self.assertIn("accept-rocm", row["requires"])
        self.assertEqual(
            json.loads((ROOT / "monitor.json").read_text())["max_wall_seconds"], 1800
        )

    def test_missing_authority_pin_and_unsafe_paths_refuse(self):
        for key, value in (
            ("reviewed_commit", "main"),
            ("approval_reference", ""),
            ("job_id", "../old"),
            ("uid", 0),
            ("state", "/tmp/../escape"),
            ("inputs", "/tmp/input,ro"),
            ("inputs", "/tmp/input:ro"),
            ("inputs", "/tmp/a\nb"),
        ):
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                h.render(**{**self.args(), key: value})
        with self.assertRaises(ValueError):
            h.render(**{**self.args(), "state": self.args()["inputs"] / "nested"})
        self.args()["state"].mkdir()
        with self.assertRaisesRegex(ValueError, "fresh output"):
            h.render(**self.args())

    def test_byte_cap_refuses_before_copy_or_hashing(self):
        source = self.root / "oversized"
        source.mkdir()
        member = source / "sparse.bin"
        with member.open("wb") as stream:
            stream.truncate(314572800)
        self.assertEqual(h.bounded_files(source), [member])
        with member.open("ab") as stream:
            stream.write(b"x")
        destination = self.root / "copy"
        with self.assertRaisesRegex(ValueError, "byte limit"):
            h.copy_packed(source, destination)
        self.assertFalse(destination.exists())
        output = self.root / "manifest.json"
        with (
            patch.object(h, "hash_file", side_effect=AssertionError("must not hash")),
            self.assertRaisesRegex(ValueError, "byte limit"),
        ):
            h.transfer_manifest(source, output)
        self.assertFalse(output.exists())

    def test_symlink_parent_refused_by_public_helpers(self):
        real = self.root / "real"
        real.mkdir()
        link = self.root / "linked"
        link.symlink_to(real, target_is_directory=True)
        nested = link / "nested"
        for value in (link, nested):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "symlink path"):
                    h.path(value)
                with self.assertRaisesRegex(ValueError, "symlink path"):
                    h.render(**{**self.args(), "inputs": value})
                with self.assertRaisesRegex(ValueError, "symlink path"):
                    h.transfer_manifest(value, self.root / "manifest.json")

    def test_relative_paths_refused_by_public_helpers(self):
        for value in ("relative", ".", "nested/input"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "absolute"):
                    h.path(value)
                for field in ("checkout", "inputs", "state"):
                    with self.assertRaisesRegex(ValueError, "absolute"):
                        h.render(**{**self.args(), field: value})
                with self.assertRaisesRegex(ValueError, "absolute"):
                    h.transfer_manifest(value, self.root / "manifest.json")
                with self.assertRaisesRegex(ValueError, "absolute"):
                    h.transfer_manifest(self.root, value)

    def test_independent_writable_copy_preserves_retained_input(self):
        source = self.root / "old"
        source.mkdir()
        member = source / "arrays.bin"
        member.write_bytes(b"tiny fixture")
        member.chmod(0o444)
        before = (
            member.read_bytes(),
            member.stat().st_ino,
            stat.S_IMODE(member.stat().st_mode),
        )
        destination = self.root / "copy"
        self.assertEqual(h.copy_packed(source, destination), 1)
        copied = destination / member.name
        self.assertNotEqual(copied.stat().st_ino, member.stat().st_ino)
        self.assertTrue(copied.stat().st_mode & stat.S_IWUSR)
        copied.write_bytes(b"changed copy")
        self.assertEqual(
            before,
            (
                member.read_bytes(),
                member.stat().st_ino,
                stat.S_IMODE(member.stat().st_mode),
            ),
        )
        with self.assertRaisesRegex(ValueError, "already exists"):
            h.copy_packed(source, destination)
        self.assertEqual(copied.read_bytes(), b"changed copy")

    def test_symlink_nonregular_and_entry_bounds_refuse_before_copy(self):
        source = self.root / "old"
        source.mkdir()
        destination = self.root / "copy"
        (source / "link").symlink_to(self.root / "absent")
        with self.assertRaisesRegex(ValueError, "symlink"):
            h.copy_packed(source, destination)
        self.assertFalse(destination.exists())
        (source / "link").unlink()
        os.mkfifo(source / "fifo")
        with self.assertRaisesRegex(ValueError, "nonregular"):
            h.copy_packed(source, destination)
        self.assertFalse(destination.exists())
        (source / "fifo").unlink()
        for n in range(257):
            (source / str(n)).touch()
        with self.assertRaisesRegex(ValueError, "entry limit"):
            h.copy_packed(source, destination)
        self.assertFalse(destination.exists())

    def test_transfer_manifest_records_bytes_without_changing_source(self):
        source = self.root / "inputs"
        source.mkdir()
        member = source / "fixture.bin"
        member.write_bytes(b"tiny approved fixture")
        output = self.root / "transfer.json"
        result = h.transfer_manifest(source, output)
        record = json.loads(output.read_text())
        self.assertEqual(
            record["files"],
            [{"path": "fixture.bin", "bytes": 21, "sha256": h.hash_file(member)}],
        )
        self.assertEqual(result["sha256"], h.hash_file(output))
        self.assertFalse(result["copies_or_workloads_started"])
        self.assertEqual(member.read_bytes(), b"tiny approved fixture")
        with self.assertRaisesRegex(ValueError, "already exists"):
            h.transfer_manifest(source, output)
        with self.assertRaisesRegex(ValueError, "outside retained"):
            h.transfer_manifest(source, source / "index.json")

    def test_interrupted_copy_keeps_partial_evidence_and_refuses_reuse(self):
        source = self.root / "old"
        source.mkdir()
        (source / "data").write_bytes(b"fixture")
        destination = self.root / "copy"

        def fail(src, dst, length):
            dst.write(b"partial")
            raise InterruptedError("fixture stop")

        with (
            patch.object(h.shutil, "copyfileobj", fail),
            self.assertRaises(InterruptedError),
        ):
            h.copy_packed(source, destination)
        self.assertEqual((destination / "data").read_bytes(), b"partial")
        self.assertEqual((source / "data").read_bytes(), b"fixture")
        with self.assertRaisesRegex(ValueError, "already exists"):
            h.copy_packed(source, destination)


if __name__ == "__main__":
    unittest.main()
