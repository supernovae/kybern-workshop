import argparse
import copy
import json
from pathlib import Path
import sys
import subprocess
import time
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import workshop as w
import handoff


def put(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value))


def template():
    return {"schema": 3, "roots": {"A": "/old"}, "command_policy": "observe_stages",
            "memory_policy": "container_12g_observe_rss",
            "limits": {"wall_seconds": 20, "shutdown_reserve_seconds": 2,
                       "rss": {"mode": "observe_rss", "max_bytes": 1000000},
                       "storage": {"mode": "observe_retained", "root_bytes": {"A": 2000000},
                                   "aggregate_bytes": 3000000, "shared_overhead_bytes": 1000000},
                       "scan_entries": 100, "scan_seconds": 2, "capture_bytes": 100000},
            "slots": [{"id": x, "step": x, "root": "A", "allowance_seconds": 2,
                       "retained_allowance_bytes": 100000,
                       "captures": ["audit/report.json"] if x == "report" else []} for x in w.STEPS]}


def native(state, complete=True):
    put(state / "lock.json", {})
    put(state / "index.json", {})
    return {"stages": [
        {"id": "plan", "kind": "experiment_plan", "state": "COMPLETE", "requires": [],
         "availability": {"path": str(state / "lock.json"), "workspace": str(state)}},
        {"id": "final", "kind": "experiment_collect", "state": "COMPLETE" if complete else "BLOCKED",
         "requires": ["plan"], "availability": {"path": str(state / "index.json")}}]}


class WorkshopTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.args = argparse.Namespace(**{k: str(self.root / k) for k in
            ("checkout", "harness", "inputs", "state", "receipts", "runtime", "session_template", "job_template")},
            commit="a" * 40, harness_commit="b" * 40, experiment="EXP-42", attempt="attempt-1",
            owner="fixture-owner", approval="fixture-only-not-real-authority", approval_stage="accept", python="/opt/python")
        for name in ("checkout", "harness", "inputs"):
            (self.root / name).mkdir()
        checkout = Path(self.args.checkout)
        (checkout / "scripts").mkdir()
        for name in ("handoff.py", "workshop.py"):
            (checkout / "scripts" / name).write_text("fixture")
        self.args.campaign = str(checkout / "campaign.json")
        self.args.profile = str(checkout / "runtime.json")
        put(Path(self.args.campaign), {"stages": [{"id": "accept", "kind": "approval"}], "custom_science": {"width": 512, "steps": 200}})
        put(Path(self.args.profile), {})
        put(Path(self.args.runtime), {"python": "3.14.4", "executable_sha256": "d" * 64})
        put(Path(self.args.session_template), template())
        put(Path(self.args.job_template), {"schema": 1, "wrap": None, "limits": {
            "wall_seconds": 2, "log_bytes": 100000, "artifact_bytes": 100000, "artifact_entries": 100,
            "memory": {"mode": "observe_rss", "max_bytes": 1000000}}})
        self.state = Path(self.args.state)

    def bind(self):
        with patch.object(w, "clean_pin"):
            return w.bind(self.args)

    def test_bind_preserves_science_and_separates_identity(self):
        original = Path(self.args.campaign).read_bytes()
        result = self.bind()
        self.assertFalse(result["launched"])
        self.assertEqual(Path(self.args.campaign).read_bytes(), original)
        session = w.read(self.state / "session.json")
        self.assertEqual((session["card_id"], session["session_id"]), ("EXP-42", "attempt-1"))
        self.assertEqual(w.read(self.state / "run.json")["argv"][-2:], ["20", "--json"])
        with self.assertRaises(ValueError):
            self.bind()

    def test_missing_approval_refuses_before_state(self):
        self.args.approval = ""
        with self.assertRaises(ValueError): self.bind()
        self.assertFalse(self.state.exists())

    def test_multiple_gates_refuse(self):
        put(Path(self.args.campaign), {"stages": [{"id": "accept", "kind": "approval"}, {"id": "other", "kind": "approval"}]})
        with self.assertRaises(ValueError): self.bind()
        self.assertFalse(self.state.exists())

    def test_invalid_reserve_refuses(self):
        t = template(); t["limits"]["shutdown_reserve_seconds"] = 21
        put(Path(self.args.session_template), t)
        with self.assertRaises(ValueError): self.bind()

    def test_explicit_long_budget_is_passed_through(self):
        t = template(); t["limits"]["wall_seconds"] = 86400
        put(Path(self.args.session_template), t)
        self.bind()
        self.assertEqual(w.read(self.state / "session.json")["limits"]["wall_seconds"], 86400)
        argv = w.read(self.state / "run.json")["argv"]
        self.assertEqual(argv[argv.index("--max-wait-seconds") + 1], "86400")

    def test_report_uses_declared_root_and_no_clobber(self):
        self.bind()
        request = w.bind_report(self.state, native(self.state))
        job = w.read(request["job"])
        self.assertEqual(job["argv"][job["argv"].index("--output") + 1], str(self.state / "audit/report.json"))
        with self.assertRaises(FileExistsError): w.bind_report(self.state, native(self.state))

    def test_incomplete_or_ambiguous_native_results_refuse(self):
        self.bind()
        with self.assertRaises(ValueError): w.bind_report(self.state, native(self.state, False))
        n = native(self.state); n["stages"].append(copy.deepcopy(n["stages"][-1]))
        with self.assertRaises(ValueError): w.select_report(n)

    def test_report_escape_refuses(self):
        self.bind(); n = native(self.state)
        n["stages"][-1]["availability"]["path"] = str(self.root / "outside")
        with self.assertRaises(ValueError): w.bind_report(self.state, n)

    def test_results_keep_quality_separate(self):
        self.bind()
        receipt = Path(self.args.receipts) / self.args.attempt
        put(receipt / "A/status/stdout.log", native(self.state))
        put(receipt / "shared/report.json", {"reason": "capture_incomplete", "evidence_complete": False})
        put(self.state / "audit/report.json", {"readiness": {"scientific_result": "not_assessed", "decision": "no_automatic_promotion"}})
        before = (self.state / "audit/report.json").read_bytes()
        result = w.results(self.state)
        self.assertTrue(result["execution"]["native_complete"])
        self.assertFalse(result["evidence"]["session"]["evidence_complete"])
        self.assertEqual(result["science"]["scientific_result"], "not_assessed")
        self.assertEqual(before, (self.state / "audit/report.json").read_bytes())

    def test_partial_json_remains_inspectable(self):
        self.bind()
        p = Path(self.args.receipts) / self.args.attempt / "A/status/stdout.log"
        p.parent.mkdir(parents=True); p.write_text('{"partial":')
        result = w.results(self.state)
        self.assertFalse(result["execution"]["native_complete"])
        self.assertEqual(len(result["evidence"]["read_errors"]), 1)

    def test_exact_pin_and_clean_checkout_required(self):
        with self.assertRaises(ValueError): w.clean_pin(self.root, "short")
        with patch.object(w, "git", side_effect=["a" * 40, " M changed"]):
            with self.assertRaises(ValueError): w.clean_pin(self.root, "a" * 40)

    def test_stage_copies_once_and_refuses_symlinks(self):
        self.bind(); source = Path(self.args.inputs)
        (source / "data").write_bytes(b"fixture")
        self.assertEqual(handoff.stage(source, self.state)["bytes"], 7)
        with self.assertRaises(FileExistsError): handoff.stage(source, self.state)
        (source / "link").symlink_to(source / "data")
        with self.assertRaises(ValueError): handoff.stage(source, self.state)

    def test_stage_budget_refuses_before_copy(self):
        self.bind(); source = Path(self.args.inputs)
        (source / "data").write_bytes(b"x" * 2000001)
        with self.assertRaises(ValueError): handoff.stage(source, self.state)
        self.assertFalse((self.state / "inputs").exists())

    def fake_driver(self, fail=None, incomplete=False):
        self.bind()
        n = native(self.state, not incomplete)
        fake = self.root / "fake.py"
        fake.write_text("""import json,sys
from pathlib import Path
s=Path(sys.argv[1]); spec=json.loads((s/'session.json').read_text()); r=Path(spec['receipt_root'])/spec['session_id']/'A'
print(json.dumps({'ready':'fixture'}),flush=True)
i=0
for line in sys.stdin:
 q=json.loads(line)
 if 'finish' in q or 'stop' in q: break
 name=q['slot']; d=r/name; d.mkdir(parents=True)
 code=1 if name==sys.argv[2] else 0
 (d/'report.json').write_text(json.dumps({'process_success':code==0,'returncode':code,'evidence_complete':True}))
 out=json.loads((s/'native-fixture.json').read_text())
 if name=='apply': out={'stages':[{'id':'accept','kind':'approval','state':'AWAITING_APPROVAL'}]}
 (d/'stdout.log').write_text(json.dumps(out))
 if name=='report': (s/'audit/report.json').write_text(json.dumps({'readiness':{'scientific_result':'not_assessed'}}))
 i+=1;print(json.dumps({'completed':i,'reason':'job_failed' if code else None}),flush=True)
 if code: sys.exit(1)
""")
        put(self.state / "native-fixture.json", n)
        with patch.object(w, "commit_files"):
            result = w.drive(self.state, [sys.executable, str(fake), str(self.state), fail or "none"])
        return result

    def test_driver_success_finishes_and_reports_without_quality_gate(self):
        result = self.fake_driver()
        self.assertIsNone(result["driver_error"])
        self.assertEqual(result["supervisor_exit"], 0)
        self.assertEqual(result["science"]["scientific_result"], "not_assessed")
        with self.assertRaises(ValueError): w.drive(self.state, ["must-not-start"])

    def test_driver_nonzero_stops_before_report(self):
        result = self.fake_driver(fail="run")
        self.assertIsNotNone(result["driver_error"])
        self.assertFalse((self.state / "report.json").exists())

    def test_interruption_retains_attempt_and_stops_supervisor(self):
        with patch.object(w.Protocol, "wait", side_effect=KeyboardInterrupt):
            result = self.fake_driver()
        self.assertEqual(result["driver_error"], "interrupted")
        self.assertTrue((self.state / ".workshop-driver").exists())
        self.assertFalse((self.state / "report.json").exists())

    def test_protocol_timeout_and_oversized_frame(self):
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(2)"], stdout=subprocess.PIPE)
        try:
            with self.assertRaisesRegex(ValueError, "deadline"):
                w.Protocol(child, time.monotonic() + .03).wait("ready")
        finally:
            child.terminate(); child.wait(); child.stdout.close()
        child = subprocess.Popen([sys.executable, "-c", "import os; os.write(1,b\"x\"*70000)"], stdout=subprocess.PIPE)
        try:
            with self.assertRaisesRegex(ValueError, "64 KiB"):
                w.Protocol(child, time.monotonic() + 2).wait("ready")
        finally:
            child.terminate(); child.wait(); child.stdout.close()

    def test_zero_exit_incomplete_native_stops(self):
        result = self.fake_driver(incomplete=True)
        self.assertIn("incomplete", result["driver_error"])
        self.assertFalse((self.state / "report.json").exists())


if __name__ == "__main__": unittest.main()
