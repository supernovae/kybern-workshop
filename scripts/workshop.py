#!/usr/bin/env python3
"""Workshop operator adapter. Campaign owns the graph; Harness owns supervision."""
import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import select
import subprocess
import sys
import time

STEPS = ("copy-inputs", "validate", "apply", "approve", "run", "status", "report")


def require(value, message):
    if not value:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for k, v in pairs:
        require(k not in result, "duplicate JSON key")
        result[k] = v
    return result


def read(path):
    path = Path(path)
    require(path.stat().st_size <= 8 * 1024**2, "JSON exceeds 8 MiB")
    return json.loads(path.read_text(), object_pairs_hook=unique,
                      parse_constant=lambda value: require(False, "nonfinite JSON"))


def safe(value):
    p = Path(value)
    require(p.is_absolute() and ".." not in p.parts, "absolute canonical path required")
    require(not any(x.is_symlink() for x in (p, *p.parents)), "symlink path refused")
    return p


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    with Path(path).open("x") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True,
                                   timeout=10).strip()


def clean_pin(root, commit):
    require(re.fullmatch(r"[0-9a-f]{40}", commit), "exact commit required")
    require(git(root, "rev-parse", "HEAD") == commit and
            not git(root, "status", "--porcelain"), "clean pinned checkout required")


def commit_files(state, names):
    subprocess.run(["git", "-C", str(state), "add", "--", *names], check=True)
    subprocess.run(["git", "-C", str(state), "-c", "core.hooksPath=/dev/null",
                    "-c", "commit.gpgsign=false", "commit", "-m",
                    "Bind Workshop supervised attempt"], check=True, stdout=sys.stderr)


def bind(args):
    """Create existing Harness specs. Never launch, approve a native gate or claim."""
    checkout, harness, inputs, state, receipts = [safe(getattr(args, k)) for k in
                                               ("checkout", "harness", "inputs", "state", "receipts")]
    roots = (checkout, harness, inputs, state, receipts)
    require(all(a != b and not a.is_relative_to(b) for a in roots for b in roots if a is not b),
            "disjoint roots required")
    require(not state.exists() and not receipts.exists(), "fresh state and receipts required")
    require(all(p.is_dir() for p in (checkout, harness, inputs)), "missing input/source directory")
    clean_pin(checkout, args.commit)
    clean_pin(harness, args.harness_commit)
    campaign, profile = safe(args.campaign), safe(args.profile)
    require(all(p.is_file() and p.is_relative_to(checkout) for p in (campaign, profile)),
            "campaign and runtime profile must be in pinned checkout")
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", args.attempt), "invalid attempt ID")
    require(all(x.strip() for x in (args.experiment, args.owner, args.approval, args.approval_stage)),
            "experiment ID and actual approval provenance required")
    # Existing schema-3 session and schema-1 job are resource templates only.
    template, job_template, runtime = map(read, (args.session_template, args.job_template, args.runtime))
    require(template["schema"] == 3 and job_template["schema"] == 1, "existing schema 3/1 templates required")
    require([s["step"] for s in template["slots"]] == list(STEPS), "existing seven-slot Campaign required")
    require(set(template["roots"]) == {"A"}, "one-root template required")
    require(job_template.get("wrap") is None, "wrapping unsupported")
    limits = copy.deepcopy(template["limits"])
    require(all(type(limits[k]) in (int, float) and math.isfinite(limits[k])
                for k in ("wall_seconds", "shutdown_reserve_seconds")) and
            0 < limits["shutdown_reserve_seconds"] < limits["wall_seconds"],
            "finite Campaign deadline and smaller cleanup reserve required")
    declarations = read(campaign)
    approvals = [s for s in declarations["stages"] if s["kind"] == "approval"]
    require(len(approvals) == 1 and approvals[0]["id"] == args.approval_stage,
            "exactly one explicitly selected approval stage supported")
    script = checkout / "scripts/handoff.py"
    require(script.is_file(), "Workshop staging adapter missing from checkout")
    required = {str(p): digest(p) for p in (campaign, profile, script, checkout / "scripts/workshop.py")}
    approval = {"owner": args.owner, "reference": args.approval}
    session = {"schema": 3, "session_id": args.attempt, "card_id": args.experiment,
               "approval": approval, "python": runtime["python"],
               "runtime_sha256": runtime["executable_sha256"],
               "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
               "source_paths": [str(checkout), str(harness)], "roots": {"A": str(state)},
               "receipt_root": str(receipts), "limits": limits,
               "slots": copy.deepcopy(template["slots"])}
    for key in ("command_policy", "memory_policy"):
        if key in template:
            session[key] = template[key]
    if "venv" in runtime:
        session["runtime_venv"] = runtime["venv"]
    invocation = runtime.get("venv", {}).get("invocation", args.python)
    require(invocation == args.python, "explicit Python must match runtime invocation")
    prefix = [invocation, "-B", "-m", "sparselab", "campaign"]
    argv = {
        "copy-inputs": [invocation, "-B", str(script), "stage"],
        "validate": [*prefix, "validate", str(campaign), "--json"],
        "apply": [*prefix, "apply", str(campaign), "--runtime-profile", str(profile),
                  "--max-wait-seconds", str(limits["wall_seconds"]), "--json"],
        "approve": [*prefix, "approve", str(campaign), args.approval_stage,
                    "--note", args.approval, "--json"],
        "run": [*prefix, "resume", str(campaign), "--runtime-profile", str(profile),
                "--execute-runs", "--max-wait-seconds", str(limits["wall_seconds"]), "--json"],
        "status": [*prefix, "status", str(campaign), "--json"],
    }
    env = {"SPARSELAB_WORK_DIR": str(state), "SPARSELAB_WORKER_LEASE_DIR": str(state / "worker-leases"),
           **{k: "1" for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                               "HF_HUB_OFFLINE", "HF_DATASETS_OFFLINE", "TRANSFORMERS_OFFLINE", "UV_OFFLINE")}}
    jobs, requests = {}, []
    for slot in session["slots"]:
        require(slot["root"] == "A" and slot["id"] == slot["step"], "canonical slot IDs required")
        step = slot["step"]
        require(slot["captures"] == (["audit/report.json"] if step == "report" else []),
                "only final native report capture supported")
        if step == "report":
            continue
        jl = copy.deepcopy(job_template["limits"])
        jl["wall_seconds"] = slot["allowance_seconds"]
        jobs[step] = {"schema": 1, "job_id": step, "card_id": args.experiment, "approval": approval,
                      "source": {"path": str(checkout), "commit": args.commit}, "cwd": str(checkout),
                      "output_root": str(receipts / args.attempt / "A"), "argv": argv[step],
                      "runtime": runtime, "required_files": required, "wrap": None,
                      "environment": env, "limits": jl}
        requests.append({"slot": step, "job": str(state / (step + ".json"))})
    state.mkdir()
    receipts.mkdir()
    (state / "worker-leases").mkdir()
    (state / "audit").mkdir()
    for step, job in jobs.items():
        save(state / (step + ".json"), job)
    save(state / "session.json", session)
    save(state / "requests.json", requests)
    return {"session": str(state / "session.json"), "bound": True, "launched": False,
            "next": "Review generated specs, commit state, then explicitly run this attempt."}


def select_report(native):
    stages = native.get("stages", [])
    require(stages and all(s["state"] == "COMPLETE" for s in stages), "native Campaign is incomplete")
    plans = [s for s in stages if s["kind"] == "experiment_plan"]
    terminals = [s for s in stages if s["kind"] == "experiment_collect" and
                 not any(s["id"] in t.get("requires", []) for t in stages)]
    require(len(plans) == len(terminals) == 1, "one plan and one terminal collection required")
    return (plans[0]["availability"]["path"], plans[0]["availability"]["workspace"],
            terminals[0]["availability"]["path"])


def bind_report(state, native):
    lock, workspace, index = map(safe, select_report(native))
    require(all(p.is_relative_to(state) for p in (lock, workspace, index)), "native report paths outside state")
    require(lock.is_file() and index.is_file() and workspace.is_dir(), "missing native evidence")
    job = read(state / "status.json")
    session = read(state / "session.json")
    job.update(job_id="report", argv=[job["argv"][0], "-B", "-m", "sparselab", "experiment", "recipe",
               "workflow", "report", str(lock), "--workspace", str(workspace), "--index", str(index),
               "--output", str(state / "audit/report.json"), "--json"])
    job["limits"]["wall_seconds"] = session["slots"][-1]["allowance_seconds"]
    job["required_files"].update({str(p): digest(p) for p in (lock, index)})
    save(state / "report.json", job)
    return {"slot": "report", "job": str(state / "report.json")}


def results(state):
    session = read(state / "session.json")
    directory = safe(session["receipt_root"]) / session["session_id"]
    records, read_errors = {}, []
    def observed(path):
        if not path.exists():
            return {}
        try:
            value = read(safe(path))
            require(isinstance(value, dict), "expected JSON object")
            return value
        except (OSError, ValueError) as exc:
            read_errors.append({"path": str(path), "error": str(exc)})
            return {}
    for slot in session["slots"]:
        p = directory / "A" / slot["id"] / "report.json"
        if p.is_file():
            d = observed(p)
            records[slot["id"]] = {k: d.get(k) for k in ("returncode", "signal", "process_success", "evidence_complete", "reason")}
    native_path = directory / "A/status/stdout.log"
    native = observed(native_path)
    stages = native.get("stages", [])
    report_path, report = None, {}
    if records.get("report", {}).get("process_success") is True:
        capture_file = directory / "A/report/captures.json"
        try:
            captures = read(safe(capture_file))
            require(len(captures) == 1, "one final report capture required")
            capture = captures[0]
            require(capture.get("complete") is True and capture.get("root") == "A" and
                    capture.get("path") == "audit/report.json", "final report capture incomplete")
            name = capture["copy"]
            require(Path(name).name == name and name not in ("", ".", ".."), "unsafe capture name")
            candidate = safe(capture_file.parent / name)
            require(candidate.is_file() and candidate.stat().st_size == capture["bytes"] and
                    digest(candidate) == capture["sha256"], "captured report digest/size mismatch")
            report = read(candidate)
            require(report.get("format") == "sparselab-publication-report", "native report format required")
            report_path = candidate
        except (OSError, ValueError, KeyError, TypeError) as exc:
            read_errors.append({"path": str(capture_file), "error": str(exc)})
            report = {}
    shared = directory / "shared/report.json"
    evidence = observed(shared)
    return {"experiment_id": session["card_id"], "attempt_id": session["session_id"],
            "execution": {"commands": records, "native_reported_complete": bool(stages) and all(s.get("state") == "COMPLETE" for s in stages)},
            "evidence": {"read_errors": read_errors, "session": evidence, "report_path": str(report_path) if report_path else None,
                         "report_sha256": digest(report_path) if report else None},
            "science": report.get("readiness", {"scientific_result": "not_assessed"})}


class Protocol:
    def __init__(self, process, deadline):
        self.process, self.deadline, self.buffer = process, deadline, b""

    def wait(self, key):
        while True:
            if b"\n" in self.buffer:
                line, self.buffer = self.buffer.split(b"\n", 1)
                frame = json.loads(line)
                require(not any(k in frame for k in ("refused", "stopped", "session_report")),
                        "supervisor stopped: " + str(frame))
                if key in frame:
                    require(not frame.get("reason"), "supervisor failure: " + str(frame))
                    return frame
                continue
            remaining = self.deadline - time.monotonic()
            require(remaining > 0, "supervisor response deadline")
            if not select.select([self.process.stdout], [], [], min(remaining, 1))[0]:
                continue
            block = os.read(self.process.stdout.fileno(), 4096)
            require(block, "supervisor closed protocol")
            self.buffer += block
            require(len(self.buffer) <= 65536, "supervisor frame exceeds 64 KiB")

    def send(self, request):
        self.process.stdin.write((json.dumps(request) + "\n").encode())
        self.process.stdin.flush()


def stop_supervisor(child, protocol, grace):
    """Request owned cleanup, then bound a stuck supervisor's termination/reaping."""
    forced = False
    try:
        protocol.send({"stop": True})
    except (OSError, ValueError, KeyboardInterrupt):
        pass
    try:
        child.wait(timeout=.2)  # Allow a responsive supervisor to consume stop.
    except (subprocess.TimeoutExpired, KeyboardInterrupt):
        if child.poll() is None:
            child.terminate()
        try:
            child.wait(timeout=grace)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            forced = True
            child.kill()
            # A second interruption must not skip reaping our direct child.
            while True:
                try:
                    child.wait()
                    break
                except KeyboardInterrupt:
                    continue
    return forced


def drive(state, argv):
    """One existing supervisor, no retry, no separate native subprocesses."""
    session = read(state / "session.json")
    requests = read(state / "requests.json")
    require([r["slot"] for r in requests] == list(STEPS[:-1]), "unexpected request sequence")
    require(not (state / ".workshop-driver").exists(), "attempt already driven; never retry")
    require([read(r["job"])["card_id"] for r in requests] == [session["card_id"]] * 6, "experiment provenance mismatch")
    save(state / ".workshop-driver", {"attempt_id": session["session_id"]})
    deadline = time.monotonic() + session["limits"]["wall_seconds"] + 10
    child = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    protocol = Protocol(child, deadline)
    failure, forced = None, False
    try:
        protocol.wait("ready")
        for n, request in enumerate(requests):
            if request["slot"] == "approve":
                previous = read(safe(session["receipt_root"]) / session["session_id"] / "A/apply/stdout.log")
                job = read(state / "approve.json")
                gate = job["argv"][job["argv"].index("approve") + 2]
                rows = [s for s in previous.get("stages", []) if s["id"] == gate]
                require(len(rows) == 1 and rows[0]["kind"] == "approval" and
                        rows[0]["state"] == "AWAITING_APPROVAL", "selected native approval gate missing/failed")
            protocol.send(request)
            frame = protocol.wait("completed")
            require(frame["completed"] == n + 1, "unexpected completed slot")
            job_report = read(safe(session["receipt_root"]) / session["session_id"] / "A" / request["slot"] / "report.json")
            require(job_report.get("process_success") is True, "native command failed")
            if request["slot"] in ("run", "status"):
                native = read(safe(session["receipt_root"]) / session["session_id"] / "A" / request["slot"] / "stdout.log")
                select_report(native)  # Exit zero alone does not establish completion.
        report_request = bind_report(state, native)
        commit_files(state, ["report.json"])
        protocol.send(report_request)
        require(protocol.wait("completed")["completed"] == 7, "report slot incomplete")
        protocol.send({"finish": True})
        child.stdin.close()
        # Drain bounded supervisor output to avoid blocking shutdown.
        while child.poll() is None and time.monotonic() < deadline:
            if select.select([child.stdout], [], [], .1)[0]:
                os.read(child.stdout.fileno(), 65536)
        require(child.poll() is not None, "supervisor did not finish by deadline")
    except (Exception, KeyboardInterrupt) as exc:
        failure = str(exc) or "interrupted"
        forced = stop_supervisor(child, protocol,
                                 min(session["limits"]["shutdown_reserve_seconds"] + 2,
                                     max(1, deadline - time.monotonic())))
    finally:
        child.stdout.close()
        if not child.stdin.closed:
            child.stdin.close()
    return {"driver_error": failure, "supervisor_exit": child.returncode,
            "forced_supervisor_kill": forced,
            "cleanup_note": "Forced supervisor kill; container cleanup unverified, inspect receipts/host" if forced else None,
            **results(state)}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="operation", required=True)
    b = sub.add_parser("bind")
    for name in ("checkout", "harness", "inputs", "state", "receipts", "commit", "harness-commit",
                 "campaign", "profile", "runtime", "python", "session-template", "job-template",
                 "experiment", "attempt", "owner", "approval", "approval-stage"):
        b.add_argument("--" + name, required=True)
    for name in ("status", "results"):
        sub.add_parser(name).add_argument("--state", required=True)
    r = sub.add_parser("run")
    for name in ("state", "harness", "harness-commit", "inputs", "image"):
        r.add_argument("--" + name, required=True)
    r.add_argument("--gpu", action="store_true")
    args = p.parse_args(argv)
    if args.operation == "bind":
        result = bind(args)
    elif args.operation in ("status", "results"):
        result = results(safe(args.state))
    else:
        state, harness, inputs = map(safe, (args.state, args.harness, args.inputs))
        clean_pin(harness, args.harness_commit)
        session = read(state / "session.json")
        subprocess.run([sys.executable, "-B", "-c",
                        "import sys; sys.path.insert(0, sys.argv[1]); import session; session.read_spec(sys.argv[2])",
                        str(harness), str(state / "session.json")], check=True, timeout=10)
        job = read(state / "status.json")
        clean_pin(safe(job["source"]["path"]), job["source"]["commit"])
        require(git(state, "show", "HEAD:session.json") == (state / "session.json").read_text().strip(),
                "commit generated specs before run")
        for request in read(state / "requests.json"):
            spec_path = safe(request["job"])
            require(spec_path.parent == state, "job outside state")
            require(git(state, "show", "HEAD:" + spec_path.name) == spec_path.read_text().strip(),
                    "commit all generated jobs before run")
        argv = [sys.executable, "-B", str(harness / "docker_session.py"), str(state / "session.json"),
                "--harness", str(harness), "--harness-commit", args.harness_commit,
                "--inputs", str(inputs), "--recipe", job["source"]["path"], "--image", args.image]
        if args.gpu:
            argv.append("--gpu")
        result = drive(state, argv)
    print(json.dumps(result, indent=2))
    return 1 if result.get("driver_error") or result.get("supervisor_exit", 0) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(2)
