"""Prepare verified input copies or render argv; never launch a workload."""

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PINS = json.loads((ROOT / "pins.json").read_text())
PACKED = PINS["packed_identifier"]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def path(value):
    p = Path(value)
    require(
        p.is_absolute()
        and ".." not in p.parts
        and ":" not in str(p)
        and not any(c in str(p) for c in ("\n", "\r", "\0", ",")),
        "unsafe absolute Linux path",
    )
    require(not any(q.is_symlink() for q in (p, *p.parents)), "symlink path refused")
    return p


def bounded_files(root):
    root = path(root)
    require(root.is_dir(), "input directory missing")
    files, total, entries = [], 0, 0
    pending = [root]
    while pending:
        for item in pending.pop().iterdir():
            entries += 1
            require(entries <= 256, "input entry limit exceeded")
            mode = item.lstat().st_mode
            require(not stat.S_ISLNK(mode), "symlink input refused")
            if stat.S_ISDIR(mode):
                pending.append(item)
            else:
                require(stat.S_ISREG(mode), "nonregular input refused")
                total += item.stat().st_size
                require(total <= 314572800, "input byte limit exceeded")
                files.append(item)
    return files


def hash_file(p):
    digest = hashlib.sha256()
    with p.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_packed(source, destination):
    files = bounded_files(source)
    require(not destination.exists(), "packed destination already exists")
    destination.mkdir(parents=False)
    for member in files:
        target = destination / member.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Fresh independent bytes; no retained mode, ownership, symlink or hardlink.
        with member.open("rb") as src, target.open("xb") as dst:
            shutil.copyfileobj(src, dst, 1024 * 1024)
    return len(files)


def transfer_manifest(inputs, output):
    inputs, output = path(inputs), path(output)
    require(
        not output.is_relative_to(inputs), "manifest must be outside retained inputs"
    )
    require(not output.exists(), "manifest output already exists")
    rows = [
        {
            "path": p.relative_to(inputs).as_posix(),
            "bytes": p.stat().st_size,
            "sha256": hash_file(p),
        }
        for p in sorted(bounded_files(inputs))
    ]
    document = {
        "format": "tinystories-transfer-bytes-v1",
        "source_root": str(inputs),
        "source_attempt": PINS["cpu_attempt"],
        "files": rows,
        "total_bytes": sum(row["bytes"] for row in rows),
        "native_verification_required": True,
    }
    with output.open("x") as stream:
        json.dump(document, stream, indent=2)
        stream.write("\n")
    return {
        "manifest": str(output),
        "sha256": hash_file(output),
        "files": len(rows),
        "copies_or_workloads_started": False,
    }


def prepared_source_preflight(inputs, execution_source=None):
    """Read-only pin check before binding; native verification still follows."""
    manifest = path(path(inputs) / "packed" / PACKED / "manifest.json")
    require(manifest.exists(), "reviewed prepared cache manifest missing")
    require(stat.S_ISREG(manifest.stat().st_mode) and manifest.stat().st_size <= 65536,
            "bounded regular prepared manifest required")
    with manifest.open("rb") as stream:
        raw = stream.read(65537)
    require(len(raw) <= 65536, "prepared manifest byte limit")
    require(hashlib.sha256(raw).hexdigest() == PINS["packed_manifest_byte_sha256"],
            "prepared manifest bytes differ from reviewed pin")
    document = json.loads(raw)
    expected = PINS["prepared_source_identity_sha256"]
    require(document["settings_sha256"] == PACKED,
            "prepared cache identifier differs from reviewed pin")
    require(document["cache_identity"]["source_identity_sha256"] == expected
            and document["source_identity_sha256"] == expected,
            "prepared cache source differs from pinned execution source")
    require(execution_source is None or execution_source == expected,
            "installed package source differs from prepared cache source")
    return {"prepared_source_identity_sha256": expected, "packed_identifier": PACKED,
            "native_verification_required": True}


def stage(inputs=Path("/inputs"), state=Path("/state")):
    import sys
    from importlib.metadata import version

    from sparselab.config.models import RunConfig
    from sparselab.data.sources import verify_lock, verify_snapshot
    from sparselab.experiments.artifacts import verify_artifact
    from sparselab.experiments.plan import Artifact
    from sparselab.runtime_identity_probe import source_identity
    from sparselab.training.manifest import source_identity as package_identity

    inputs, state = path(inputs), path(state)
    require(
        sys.version.split()[0] == PINS["python_version"]
        and version("torch") == PINS["torch_version"]
        and source_identity()["source_sha256"] == PINS["installed_source_sha256"],
        "runtime/source pin mismatch",
    )
    prepared_source_preflight(inputs, package_identity()["sha256"])
    bounded_files(inputs)
    lock = verify_lock(inputs / "source.lock.json")
    require(
        lock["source"]["revision"] == PINS["dataset_revision"], "dataset pin mismatch"
    )
    expected = json.loads((ROOT / "first-files.json").read_text())
    require(
        {p.name for p in (inputs / "parquet").iterdir()}
        == {Path(v["path"]).name for v in expected.values()},
        "exactly two cached Parquet files required",
    )
    for split, pin in expected.items():
        require(
            all(
                lock["provenance"]["files"][split][0].get(k) == v
                for k, v in pin.items()
            ),
            "source inventory pin mismatch",
        )
        payload = inputs / "parquet" / Path(pin["path"]).name
        require(
            payload.stat().st_size == pin["size"]
            and hash_file(payload) == pin["lfs_sha256"],
            "cached Parquet identity mismatch",
        )
    snapshot = verify_snapshot(
        inputs / "snapshot/manifest.json", verification_mode="cold"
    )
    require(
        snapshot["manifest_sha256"] == PINS["snapshot_manifest_sha256"]
        and snapshot["lock"]["lock_sha256"] == lock["lock_sha256"],
        "snapshot identity mismatch",
    )
    cache = state / "cache"
    require(not cache.exists(), "fresh writable cache parent required")
    cache.mkdir()
    copy_packed(inputs / "packed" / PACKED, cache / PACKED)
    config = RunConfig.model_validate(json.loads((ROOT / "run.json").read_text()))
    for row in json.loads((ROOT / "campaign.json").read_text())["stages"]:
        if row["kind"] == "artifact_reference":
            verify_artifact(
                Artifact.model_validate(row["artifact"]),
                ROOT / "campaign.json",
                dataset=config.dataset,
                verification_mode="cold",
            )
    with (state / "input-copy-complete.json").open("x") as stream:
        json.dump(
            {
                "input_revision": PINS["dataset_revision"],
                "packed": PACKED,
                "independent_writable_copy": True,
                "model_work": False,
            },
            stream,
        )
    return {"state": "COMPLETE", "model_work": False}


def render(
    checkout, inputs, state, job_id, reviewed_commit, approval_reference, uid, gid
):
    checkout, inputs, state = map(path, (checkout, inputs, state))
    require(
        len({checkout, inputs, state}) == 3
        and all(
            not a.is_relative_to(b)
            for a in (checkout, inputs, state)
            for b in (checkout, inputs, state)
            if a != b
        ),
        "roots must be separate",
    )
    require(not state.exists(), "fresh output root required")
    require(re.fullmatch(r"[a-z][a-z0-9-]{0,47}", job_id), "invalid fresh job ID")
    require(
        re.fullmatch(r"[0-9a-f]{40}", reviewed_commit), "reviewed commit pin required"
    )
    require(
        approval_reference.strip()
        and len(approval_reference) <= 2048
        and not any(c in approval_reference for c in "\n\r\0"),
        "actual approval reference required",
    )
    require(
        type(uid) is int and type(gid) is int and uid > 0 and gid > 0,
        "nonroot Linux UID/GID required",
    )
    recipe = "/reviewed/examples/tinystories-rocm"
    campaign = recipe + "/campaign.json"
    profile = ["--runtime-profile", recipe + "/runtime.json"]
    commands = [
        (
            "copy-inputs",
            ["/opt/venv/bin/python", "-B", recipe + "/handoff.py", "stage"],
        ),
        ("validate", ["sparselab", "campaign", "validate", campaign, "--json"]),
        (
            "apply",
            [
                "sparselab",
                "campaign",
                "apply",
                campaign,
                *profile,
                "--max-wait-seconds",
                "120",
                "--json",
            ],
        ),
        (
            "approve",
            [
                "sparselab",
                "campaign",
                "approve",
                campaign,
                "approve-model",
                "--note",
                approval_reference,
                "--json",
            ],
        ),
        (
            "run",
            [
                "sparselab",
                "campaign",
                "resume",
                campaign,
                *profile,
                "--execute-runs",
                "--max-wait-seconds",
                "1740",
                "--json",
            ],
        ),
        ("status", ["sparselab", "campaign", "status", campaign, "--json"]),
    ]
    return {
        "execution_enabled": False,
        "container_profile": {
            "engine": "docker",
            "endpoint": "unix:///var/run/docker.sock",
            "image": PINS["image"],
            "memory_bytes": 4294967296,
            "swap_bytes": 0,
            "cpus": 2,
            "pids": 256,
            "uid": uid,
            "gid": gid,
        },
        "job_id": job_id,
        "reviewed_workshop_commit": reviewed_commit,
        "approval_reference": approval_reference,
        "pins": PINS,
        "requires": "Chief-bound fresh claim, clean standalone reviewed checkout, approved staged CPUf inputs, reviewed lab-harness docker_session.py with schema-3 fixed campaign and one 1800-second whole-job clock including cleanup; never launch these native argv independently.",
        "steps": [
            {
                "step": name,
                "argv": (
                    ["/opt/venv/bin/python", "-B", "-m", "sparselab", *argv[1:]]
                    if argv[0] == "sparselab"
                    else argv
                ),
            }
            for name, argv in commands
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    sub.add_parser("stage")
    preflight = sub.add_parser("preflight")
    preflight.add_argument("--inputs", required=True)
    manifest = sub.add_parser("transfer-manifest")
    manifest.add_argument("--inputs", required=True)
    manifest.add_argument("--output", required=True)
    p = sub.add_parser("render")
    for name in (
        "checkout",
        "inputs",
        "state",
        "job-id",
        "reviewed-commit",
        "approval-reference",
    ):
        p.add_argument("--" + name, required=True)
    p.add_argument("--uid", type=int, default=os.getuid())
    p.add_argument("--gid", type=int, default=os.getgid())
    args = vars(parser.parse_args())
    operation = args.pop("operation")
    if operation == "preflight":
        print(json.dumps(prepared_source_preflight(**args), indent=2))
        return
    result = (
        stage()
        if operation == "stage"
        else (
            transfer_manifest(**args)
            if operation == "transfer-manifest"
            else render(**args)
        )
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
