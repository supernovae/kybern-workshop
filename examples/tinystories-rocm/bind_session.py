"""Bind committed offline jobs for the fixed Docker campaign. Never launches them."""

import argparse
import json
import os
import sys
import subprocess
from pathlib import Path
import handoff as h


def git(root, *args):
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True, timeout=10
    ).strip()


def bind(
    checkout,
    harness,
    inputs,
    state,
    receipts,
    runtime,
    job_id,
    reviewed_commit,
    owner,
    approval_reference,
    boot_id,
    gpu=False,
):
    checkout, harness, inputs, state, receipts = map(
        h.path, (checkout, harness, inputs, state, receipts)
    )
    h.require(
        git(checkout, "rev-parse", "HEAD") == reviewed_commit
        and not git(checkout, "status", "--porcelain"),
        "clean reviewed Workshop checkout required",
    )
    h.require(
        h.ROOT.resolve() == checkout / "examples/tinystories-rocm",
        "run binder from selected checkout",
    )
    h.require(
        not git(harness, "status", "--porcelain"), "clean reviewed harness required"
    )
    h.require(owner.strip() and boot_id.strip(), "owner and observed boot ID required")
    h.require(
        runtime["python"] == h.PINS["python_version"], "image Python pin mismatch"
    )
    rendered = h.render(
        checkout,
        inputs,
        state,
        job_id,
        reviewed_commit,
        approval_reference,
        os.getuid(),
        os.getgid(),
    )
    h.require(not receipts.exists(), "fresh receipt root required")
    roots = (checkout, harness, inputs, state, receipts)
    h.require(
        len(set(roots)) == len(roots)
        and all(not a.is_relative_to(b) for a in roots for b in roots if a != b),
        "disjoint roots required",
    )
    # Check the exact bounded science before producing runnable job specifications.
    run = json.loads((h.ROOT / "run.json").read_text())
    plan = json.loads((h.ROOT / "plan.json").read_text())
    h.require(
        run["staging"] == {"smoke_steps": 2, "warmup_steps": 5}
        and run["training"]["max_steps"] == 1,
        "16-update recipe required",
    )
    h.require(
        run["evaluation"] == {"every_steps": 1, "max_batches": 1}
        and len(plan["axes"]) == 1
        and [x["set"] for x in plan["axes"][0]["choices"]]
        == [{"model.ffn_dim": 64}, {"model.ffn_dim": 96}],
        "two-arm evaluation ceiling required",
    )
    h.prepared_source_preflight(inputs)  # Refuse before writing state or claiming a GPU attempt.
    state.mkdir()
    receipts.mkdir()
    (state / "worker-leases").mkdir()
    approval = {"owner": owner, "reference": approval_reference}
    limits = {
        "wall_seconds": 1800,
        "shutdown_reserve_seconds": 20,
        "rss": {"mode": "observe_rss", "max_bytes": 4294967296},
        "storage": {
            "mode": "observe_retained",
            "root_bytes": {"A": 2143289344},
            "aggregate_bytes": 2147483648,
            "shared_overhead_bytes": 4194304,
        },
        "scan_entries": 20000,
        "scan_seconds": 2,
        "capture_bytes": 1048576,
    }
    session = {
        "schema": 3,
        "session_id": job_id,
        "card_id": job_id,
        "approval": approval,
        "python": runtime["python"],
        "boot_id": boot_id,
        "runtime_sha256": runtime["executable_sha256"],
        "source_paths": [str(harness), str(checkout)],
        "roots": {"A": str(state)},
        "receipt_root": str(receipts),
        "limits": limits,
        "slots": [],
    }
    if "venv" in runtime:
        session["runtime_venv"] = runtime["venv"]
    invocation = runtime.get("venv", {}).get("invocation", "/opt/venv/bin/python")
    env = {
        "SPARSELAB_WORK_DIR": str(state),
        "SPARSELAB_WORKER_LEASE_DIR": str(state / "worker-leases"),
        **{
            k: "1"
            for k in (
                "OMP_NUM_THREADS",
                "MKL_NUM_THREADS",
                "OPENBLAS_NUM_THREADS",
                "HF_HUB_OFFLINE",
                "HF_DATASETS_OFFLINE",
                "TRANSFORMERS_OFFLINE",
                "UV_OFFLINE",
            )
        },
    }
    required = {
        str(p): h.hash_file(p)
        for p in h.ROOT.iterdir()
        if p.suffix in (".json", ".py") and p.is_file()
    }
    requests = []
    for row, allowance in zip(
        rendered["steps"], (30, 10, 30, 10, 1640, 10), strict=True
    ):
        step = row["step"]
        argv = [
            invocation,
            *[arg.replace("/reviewed", str(checkout)) for arg in row["argv"][1:]],
        ]
        slot = {
            "id": step,
            "root": "A",
            "step": step,
            "allowance_seconds": allowance,
            "retained_allowance_bytes": 16777216,
            "captures": [],
        }
        session["slots"].append(slot)
        job = {
            "schema": 1,
            "job_id": step,
            "card_id": job_id,
            "approval": approval,
            "source": {"path": str(checkout), "commit": reviewed_commit},
            "cwd": str(checkout),
            "output_root": str(receipts / job_id / "A"),
            "argv": argv,
            "runtime": runtime,
            "required_files": required,
            "wrap": None,
            "environment": env,
            "limits": {
                "wall_seconds": allowance,
                "log_bytes": 1048576,
                "artifact_bytes": 1048576,
                "artifact_entries": 1000,
                "memory": {"mode": "observe_rss", "max_bytes": 4294967296},
            },
        }
        p = state / (step + ".json")
        p.write_text(json.dumps(job, indent=2))
        requests.append({"slot": step, "job": str(p)})
    session["slots"].append(
        {
            "id": "report",
            "root": "A",
            "step": "report",
            "allowance_seconds": 10,
            "retained_allowance_bytes": 16777216,
            "captures": ["audit/report.json"],
        }
    )
    (state / "session.json").write_text(json.dumps(session, indent=2))
    (state / "requests.json").write_text(json.dumps(requests, indent=2))
    # Native report paths become known only from apply/run receipts. Bind and commit
    # that final report job during the same live session; never invent native paths.
    return {
        "execution_enabled": False,
        "session": str(state / "session.json"),
        "requests": str(state / "requests.json"),
        "report_job": "Use bind_session.py report with actual native receipt paths, then commit report.json before submission",
        "wrapper_argv": [
            sys.executable,
            "-B",
            str(harness / "docker_session.py"),
            str(state / "session.json"),
            "--harness",
            str(harness),
            "--harness-commit",
            git(harness, "rev-parse", "HEAD"),
            "--inputs",
            str(inputs),
            "--recipe",
            str(checkout),
            *(["--gpu"] if gpu else []),
        ],
        "required_next_action": "Commit generated session/jobs in the fresh state repository. Start wrapper once; submit steps individually only after inspecting native gates. Report job and finish use the same live deadline. No automatic approvals/retries.",
    }


def report(state, lock, workspace, index):
    """Bind actual receipt paths without launching or guessing native outputs."""
    state, lock, workspace, index = map(h.path, (state, lock, workspace, index))
    h.require(
        all(p.is_relative_to(state) and p.exists() for p in (lock, workspace, index)),
        "existing native paths within state required",
    )
    h.require(
        lock.is_file() and index.is_file() and workspace.is_dir(),
        "native lock/index files and workspace directory required",
    )
    job = json.loads((state / "status.json").read_text())
    job.update(
        job_id="report",
        argv=[
            job["argv"][0],
            "-B",
            "-m",
            "sparselab",
            "experiment",
            "recipe",
            "workflow",
            "report",
            str(lock),
            "--workspace",
            str(workspace),
            "--index",
            str(index),
            "--output",
            "/state/audit/report.json",
            "--json",
        ],
    )
    job["required_files"].update({str(p): h.hash_file(p) for p in (lock, index)})
    with (state / "report.json").open("x") as stream:
        json.dump(job, stream, indent=2)
    return {"slot": "report", "job": str(state / "report.json")}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="operation", required=True)
    b = sub.add_parser("bind")
    for name in (
        "checkout",
        "harness",
        "inputs",
        "state",
        "receipts",
        "runtime",
        "job-id",
        "reviewed-commit",
        "owner",
        "approval-reference",
        "boot-id",
    ):
        b.add_argument("--" + name, required=True)
    b.add_argument(
        "--gpu",
        action="store_true",
        help="Include device mapping only for a separately approved GPU job",
    )
    r = sub.add_parser("report")
    for name in ("state", "lock", "workspace", "index"):
        r.add_argument("--" + name, required=True)
    args = vars(p.parse_args())
    operation = args.pop("operation")
    if operation == "bind":
        args["runtime"] = json.loads(Path(args["runtime"]).read_text())
    print(json.dumps(bind(**args) if operation == "bind" else report(**args), indent=2))
