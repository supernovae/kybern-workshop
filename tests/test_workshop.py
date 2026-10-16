import argparse
import copy
import hashlib
import io
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
        self.args.approved_wall_seconds = 86400
        t = template(); t["limits"]["wall_seconds"] = 86400
        put(Path(self.args.session_template), t)
        self.bind()
        self.assertEqual(w.read(self.state / "session.json")["limits"]["wall_seconds"], 86400)
        self.assertEqual(w.read(self.state / "session.json")["approval"]["approved_wall_seconds"], 86400)
        self.assertEqual(w.read(self.state / "run.json")["approval"]["approved_wall_seconds"], 86400)
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
        self.assertTrue(result["execution"]["native_reported_complete"])
        self.assertFalse(result["evidence"]["session"]["evidence_complete"])
        self.assertEqual(result["science"]["scientific_result"], "not_assessed")
        self.assertIsNone(result["evidence"]["report_path"])
        self.assertEqual(before, (self.state / "audit/report.json").read_bytes())

    def test_partial_json_remains_inspectable(self):
        self.bind()
        p = Path(self.args.receipts) / self.args.attempt / "A/status/stdout.log"
        p.parent.mkdir(parents=True); p.write_text('{"partial":')
        result = w.results(self.state)
        self.assertFalse(result["execution"]["native_reported_complete"])
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

    def fake_driver(self, fail=None, incomplete=False, gate=None, report_count=7):
        self.bind()
        n = native(self.state, not incomplete)
        fake = self.root / "fake.py"
        fake.write_text("import json,sys,hashlib\nfrom pathlib import Path\ns=Path(sys.argv[1]); spec=json.loads((s/'session.json').read_text()); r=Path(spec['receipt_root'])/spec['session_id']/'A'\nprint(json.dumps({'ready':'fixture'}),flush=True)\ni=0\nfor line in sys.stdin:\n q=json.loads(line)\n with (s/'sent.jsonl').open('a') as log: log.write(json.dumps(q)+'\\n')\n if 'finish' in q or 'stop' in q: break\n name=q['slot']; d=r/name; d.mkdir(parents=True)\n code=1 if name==sys.argv[2] else 0\n (d/'report.json').write_text(json.dumps({'process_success':code==0,'returncode':code,'evidence_complete':True}))\n out=json.loads((s/'native-fixture.json').read_text())\n if name=='apply': out={'stages':json.loads((s/'gate-fixture.json').read_text())}\n (d/'stdout.log').write_text(json.dumps(out))\n if name=='report':\n  payload=json.dumps({'format':'sparselab-publication-report','readiness':{'scientific_result':'not_assessed'}}).encode()\n  (d/'capture-0.bin').write_bytes(payload)\n  (d/'captures.json').write_text(json.dumps([{'complete':True,'root':'A','path':'audit/report.json','copy':'capture-0.bin','bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()}]))\n i+=1\n if name=='report': i=json.loads((s/'report-count.json').read_text())\n print(json.dumps({'completed':i,'reason':'job_failed' if code else None}),flush=True)\n if code: sys.exit(1)\n")
        put(self.state / "native-fixture.json", n)
        put(self.state / "gate-fixture.json", gate if gate is not None else [{"id":"accept","kind":"approval","state":"AWAITING_APPROVAL"}])
        put(self.state / "report-count.json", report_count)
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

    def assert_no_approval(self, gate):
        result = self.fake_driver(gate=gate)
        self.assertIn("approval gate", result["driver_error"])
        sent = [json.loads(x) for x in (self.state / "sent.jsonl").read_text().splitlines()]
        self.assertNotIn("approve", [x.get("slot") for x in sent])
        self.assertIn({"stop": True}, sent)

    def test_missing_gate_sends_no_approval(self): self.assert_no_approval([])

    def test_wrong_gate_sends_no_approval(self):
        self.assert_no_approval([{"id":"other", "kind":"approval", "state":"AWAITING_APPROVAL"}])

    def test_nonawaiting_gate_sends_no_approval(self):
        self.assert_no_approval([{"id":"accept", "kind":"approval", "state":"COMPLETE"}])

    def test_binding_wrong_gate_refuses(self):
        self.args.approval_stage = "other"
        with self.assertRaisesRegex(ValueError, "selected approval"): self.bind()
        self.assertFalse(self.state.exists())

    def test_missing_report_file_and_bound_digests(self):
        self.bind(); n = native(self.state)
        (self.state / "lock.json").unlink()
        with self.assertRaisesRegex(ValueError, "missing native"): w.bind_report(self.state, n)
        n = native(self.state)
        job = w.read(w.bind_report(self.state, n)["job"])
        for name in ("lock.json", "index.json"):
            self.assertEqual(job["required_files"][str(self.state / name)], w.digest(self.state / name))

    def test_report_completion_frame_required(self):
        result = self.fake_driver(report_count=6)
        self.assertIn("report slot incomplete", result["driver_error"])
        sent = [json.loads(x) for x in (self.state / "sent.jsonl").read_text().splitlines()]
        self.assertNotIn({"finish": True}, sent)

    def test_tampered_capture_is_not_science(self):
        result = self.fake_driver()
        path = Path(result["evidence"]["report_path"])
        path.write_bytes(path.read_bytes().replace(b"not_assessed", b"bad_assessed"))
        result = w.results(self.state)
        self.assertIsNone(result["evidence"]["report_path"])
        self.assertEqual(result["science"]["scientific_result"], "not_assessed")
        self.assertTrue(result["evidence"]["read_errors"])

    def test_unsuccessful_report_slot_cannot_supply_science(self):
        result = self.fake_driver()
        slot = Path(self.args.receipts) / self.args.attempt / "A/report/report.json"
        put(slot, {"process_success": False})
        self.assertIsNone(w.results(self.state)["evidence"]["report_path"])

    def run_preflight(self, changed=None, validation_fails=False):
        def git(root, *args):
            name = args[-1].split(":")[-1]
            if name == changed: return "uncommitted bytes"
            return (self.state / name).read_text().strip()
        def validate(*args, **kwargs):
            if validation_fails and kwargs.get("check"):
                raise subprocess.CalledProcessError(1, args[0])
            return subprocess.CompletedProcess(args[0], 1 if validation_fails else 0)
        argv = ["run", "--state", str(self.state), "--harness", self.args.harness,
                "--harness-commit", self.args.harness_commit, "--inputs", self.args.inputs, "--image", "fixture"]
        with patch.object(w, "clean_pin"), patch.object(w, "git", side_effect=git), \
             patch.object(w.subprocess, "run", side_effect=validate), \
             patch.object(w, "drive", return_value={}) as drive, patch("sys.stdout", new=io.StringIO()):
            try:
                return w.main(argv)
            finally:
                self.last_drive_calls = drive.call_count

    def test_run_preflight_accepts_committed_specs(self):
        self.bind(); self.assertEqual(self.run_preflight(), 0)
        self.assertEqual(self.last_drive_calls, 1)

    def test_uncommitted_session_refuses_before_drive(self):
        self.bind()
        with self.assertRaisesRegex(ValueError, "commit generated"): self.run_preflight(changed="session.json")
        self.assertEqual(self.last_drive_calls, 0)

    def test_modified_job_refuses_before_drive(self):
        self.bind()
        with self.assertRaisesRegex(ValueError, "commit all"): self.run_preflight(changed="run.json")
        self.assertEqual(self.last_drive_calls, 0)

    def test_job_outside_state_refuses_before_drive(self):
        self.bind(); requests = w.read(self.state / "requests.json")
        outside = self.root / "run.json"; outside.write_bytes((self.state / "run.json").read_bytes())
        requests[-2]["job"] = str(outside); put(self.state / "requests.json", requests)
        with self.assertRaisesRegex(ValueError, "job outside"): self.run_preflight()
        self.assertEqual(self.last_drive_calls, 0)

    def test_native_session_validator_failure_blocks_drive(self):
        self.bind()
        with self.assertRaises(subprocess.CalledProcessError): self.run_preflight(validation_fails=True)
        self.assertEqual(self.last_drive_calls, 0)

    def test_disjoint_roots(self):
        self.args.inputs = self.args.checkout
        with self.assertRaisesRegex(ValueError, "disjoint"): self.bind()

    def test_safe_refuses_symlink_parent(self):
        link = self.root / "link"; link.symlink_to(self.root / "checkout", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"): w.safe(link / "campaign.json")

    def test_recipe_must_be_inside_checkout(self):
        outside = self.root / "campaign.json"; outside.write_bytes(Path(self.args.campaign).read_bytes())
        self.args.campaign = str(outside)
        with self.assertRaisesRegex(ValueError, "pinned checkout"): self.bind()

    def test_seven_slots(self):
        t = template(); t["slots"].pop(); put(Path(self.args.session_template), t)
        with self.assertRaisesRegex(ValueError, "seven-slot"): self.bind()

    def test_canonical_slot_id(self):
        t = template(); t["slots"][0]["id"] = "other"; put(Path(self.args.session_template), t)
        with self.assertRaisesRegex(ValueError, "canonical slot"): self.bind()

    def test_capture_only_final_report(self):
        t = template(); t["slots"][0]["captures"] = ["other"]; put(Path(self.args.session_template), t)
        with self.assertRaisesRegex(ValueError, "only final"): self.bind()

    def test_runtime_invocation_must_match(self):
        r = w.read(self.args.runtime); r["venv"] = {"invocation":"/different"}; put(Path(self.args.runtime), r)
        with self.assertRaisesRegex(ValueError, "invocation"): self.bind()

    def test_driver_sequence_guard(self):
        self.bind(); requests = w.read(self.state / "requests.json"); requests.reverse(); put(self.state / "requests.json", requests)
        with patch.object(w.subprocess, "Popen") as launch:
            with self.assertRaisesRegex(ValueError, "sequence"): w.drive(self.state, [])
            launch.assert_not_called()

    def test_driver_provenance_guard(self):
        self.bind(); p = self.state / "run.json"; job = w.read(p); job["card_id"] = "other"; put(p, job)
        with patch.object(w.subprocess, "Popen") as launch:
            with self.assertRaisesRegex(ValueError, "provenance"): w.drive(self.state, [])
            launch.assert_not_called()

    def test_stage_entry_budget(self):
        self.bind(); session = w.read(self.state / "session.json"); session["limits"]["scan_entries"] = 1; put(self.state / "session.json", session)
        source = Path(self.args.inputs)
        (source / "one").touch(); (source / "two").touch()
        with self.assertRaisesRegex(ValueError, "entry budget"): handoff.stage(source, self.state)
        self.assertFalse((self.state / "inputs").exists())

    def test_empty_staging_is_exclusive(self):
        self.bind(); handoff.stage(Path(self.args.inputs), self.state)
        with self.assertRaises(FileExistsError): handoff.stage(Path(self.args.inputs), self.state)

    def test_stage_growth_budget(self):
        self.bind(); source = Path(self.args.inputs); item = source / "data"; item.write_bytes(b"x")
        session = w.read(self.state / "session.json"); session["limits"]["storage"]["root_bytes"]["A"] = 5; put(self.state / "session.json", session)
        def walk(*args, **kwargs):
            yield str(source), [], ["data"]
            item.write_bytes(b"xxxxxx")
        with patch.object(handoff.os, "walk", walk):
            with self.assertRaisesRegex(ValueError, "grew"): handoff.stage(source, self.state)

    def test_stubborn_supervisor_is_killed_and_reaped(self):
        code = "import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); print('ready',flush=True); time.sleep(10)"
        child = subprocess.Popen([sys.executable, "-c", code], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        child.stdout.readline()
        protocol = w.Protocol(child, time.monotonic() + 2)
        try:
            forced = w.stop_supervisor(child, protocol, .02)
            self.assertTrue(forced)
            self.assertEqual(child.returncode, -9)
        finally:
            if child.poll() is None: child.kill(); child.wait()
            child.stdin.close(); child.stdout.close()

    def test_second_interrupt_still_kills_and_reaps(self):
        from unittest.mock import Mock
        child, protocol = Mock(), Mock()
        child.poll.return_value = None
        child.wait.side_effect = [subprocess.TimeoutExpired("fixture", .2), KeyboardInterrupt(), 0]
        self.assertTrue(w.stop_supervisor(child, protocol, .02))
        protocol.send.assert_called_once_with({"stop": True})
        child.terminate.assert_called_once(); child.kill.assert_called_once()
        self.assertEqual(child.wait.call_count, 3)

    def test_stop_ignoring_child_is_terminated(self):
        code = "import json,sys,time; print('ready',flush=True); q=json.loads(sys.stdin.readline()); print(q.get('stop'),flush=True); time.sleep(10)"
        child = subprocess.Popen([sys.executable, "-c", code], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        child.stdout.readline()
        try:
            self.assertFalse(w.stop_supervisor(child, w.Protocol(child, time.monotonic()+2), .1))
            self.assertEqual(child.stdout.readline().strip(), b"True")
            self.assertEqual(child.returncode, -15)
        finally:
            if child.poll() is None: child.kill(); child.wait()
            child.stdin.close(); child.stdout.close()

    def test_forced_shutdown_returns_driver_result(self):
        self.bind()
        real_popen, real_stop = subprocess.Popen, w.stop_supervisor
        code = "import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); print('ready',flush=True); time.sleep(10)"
        def launch(*args, **kwargs):
            child = real_popen([sys.executable, "-c", code], **kwargs)
            child.stdout.readline()
            return child
        with patch.object(w.subprocess, "Popen", side_effect=launch), \
             patch.object(w.Protocol, "wait", side_effect=KeyboardInterrupt), \
             patch.object(w, "stop_supervisor", side_effect=lambda child, protocol, grace: real_stop(child, protocol, .02)):
            result = w.drive(self.state, ["fixture"])
        self.assertEqual(result["driver_error"], "interrupted")
        self.assertEqual(result["supervisor_exit"], -9)
        self.assertTrue(result["forced_supervisor_kill"])
        self.assertIn("unverified", result["cleanup_note"])

    def test_invalid_wall_values_refuse_before_binding(self):
        for wall in (float("inf"), float("nan"), True, "3600", -1, 1e300, 1e17):
            with self.subTest(wall=wall):
                t = template(); t["limits"]["wall_seconds"] = wall
                put(Path(self.args.session_template), t)
                self.args.approved_wall_seconds = wall
                with self.assertRaises(ValueError): self.bind()
                self.assertFalse(self.state.exists())

    def test_long_wall_requires_explicit_matching_operator_argument(self):
        t = template(); t["limits"]["wall_seconds"] = 86400
        put(Path(self.args.session_template), t)
        for approved in (None, 7200, True):
            with self.subTest(approved=approved):
                self.args.approved_wall_seconds = approved
                with self.assertRaisesRegex(ValueError, "approved wall"): self.bind()
                self.assertFalse(self.state.exists())

    def test_existing_native_paths_outside_state_refuse(self):
        self.bind(); original = native(self.state)
        outside = self.root / "outside.json"; put(outside, {})
        for row, key, value in ((0,"path",outside),(0,"workspace",self.root),(1,"path",outside)):
            with self.subTest(key=key, row=row):
                n = copy.deepcopy(original); n["stages"][row]["availability"][key] = str(value)
                with self.assertRaisesRegex(ValueError, "outside state"): w.bind_report(self.state, n)
                self.assertFalse((self.state / "report.json").exists())

    def test_capture_metadata_binds_exact_final_report(self):
        self.fake_driver()
        directory = Path(self.args.receipts) / self.args.attempt / "A/report"
        path = directory / "captures.json"; original = w.read(path)
        variants = []
        for key, value in (("complete",False),("root","B"),("path","other.json"),("copy","../capture-0.bin")):
            c = copy.deepcopy(original); c[0][key] = value; variants.append(c)
        variants.append(original + original)
        for captures in variants:
            with self.subTest(captures=captures):
                put(path, captures)
                result = w.results(self.state)
                self.assertIsNone(result["evidence"]["report_path"])
                self.assertEqual(result["science"]["scientific_result"], "not_assessed")
        put(path, original)
        payload = {"format":"wrong-format", "readiness":{"scientific_result":"fabricated"}}
        copy_path = directory / original[0]["copy"]; put(copy_path, payload)
        original[0].update(bytes=copy_path.stat().st_size, sha256=w.digest(copy_path)); put(path, original)
        result = w.results(self.state)
        self.assertIsNone(result["evidence"]["report_path"])
        self.assertEqual(result["science"]["scientific_result"], "not_assessed")


if __name__ == "__main__": unittest.main()
