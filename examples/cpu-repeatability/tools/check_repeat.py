"""Read-only checks for the bounded single-cell Workshop acceptance plan.

Inputs are native lock/workspace/index triples, not caller-authored reports.
This checks selected snapshots; the operator must additionally establish that
those snapshots cover all attempts in each isolated root. No work is launched.
"""

import argparse
import json
import math
import re
from pathlib import Path


def _require(condition, reason):
    if not condition:
        raise ValueError(reason)


def _integer(value, expected, reason):
    _require(type(value) is int and value == expected, reason)


def _digest(value, reason):
    _require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None, reason)


def _identifier(value, reason):
    _require(isinstance(value, str) and bool(value.strip()), reason)


def _completed(report):
    _require(
        report["readiness"]["evidence_integrity"] == "verified_snapshot",
        "unverified evidence",
    )
    _require(
        report["readiness"]["execution_coverage"] == "complete", "incomplete coverage"
    )
    _require(len(report["cells"]) == 1, "expected one cell")
    cell = report["cells"][0]
    _require(
        cell["status"] == "complete",
        "cell incomplete",
    )
    _integer(cell["seed"], 7, "unexpected seed")
    _require(cell["cell_id"] == "main:single", "unexpected cell identity")
    expected = {"max_steps": 1, "max_tokens": 16, "seq_len": 16,
                "micro_batch_size": 1, "gradient_accumulation": 1}
    _require(set(cell["planned_budget"]) == set(expected), "training budget fields")
    for name, value in expected.items():
        _integer(cell["planned_budget"][name], value, f"training budget: {name}")
    _require(set(cell["planned_evaluation"]) == {"max_batches"}, "evaluation budget fields")
    _integer(cell["planned_evaluation"]["max_batches"], 1, "evaluation budget: max_batches")
    _digest(cell["config_sha256"], "invalid config identity")
    inputs = cell["inputs"]
    _require(len(inputs) == 2 and {i["kind"] for i in inputs} == {"tokenizer", "prepared_data"},
             "invalid input kinds/count")
    for item in inputs:
        _digest(item["sha256"], "invalid input identity")
        _integer(item["version"], 1, "invalid input version")
    for name in ("scientific_sha256", "source_identity_sha256", "plan_sha256", "evidence_index_sha256"):
        _digest(report["provenance"][name], f"invalid {name}")
    _identifier(report["provenance"]["plan_id"], "missing plan identity")
    _require(len(cell["attempts"]) == 1, "expected exactly one attempt")
    attempt = cell["attempts"][0]
    _require(attempt["status"] == "complete", "attempt incomplete")
    _identifier(attempt.get("attempt_id"), "missing attempt identity")
    _identifier(attempt.get("run_id"), "missing run identity")
    _require(attempt["run_id"] == cell["selected_run_id"], "selected run mismatch")
    for name in ("missing_report_count", "rejected_report_count"):
        _integer(attempt[name], 0, name)
    _require(
        report["diagnostic_status"] == "collected"
        and len(report["diagnostic_evaluations"]) == 1,
        "missing diagnostic",
    )
    diagnostic = report["diagnostic_evaluations"][0]
    _require(
        diagnostic["status"] == "COMPLETED"
        and diagnostic["cell_id"] == cell["cell_id"]
        and diagnostic["run_id"] == cell["selected_run_id"],
        "diagnostic incomplete or mismatched",
    )
    _require(diagnostic["stage"] == "evaluate-heldout", "unexpected diagnostic stage")
    _digest(diagnostic["suite_sha256"], "invalid suite identity")
    metrics = diagnostic["metrics"]
    _integer(metrics.get("batches"), 1, "diagnostic batches")
    _integer(metrics.get("valid_targets"), 16, "diagnostic targets")
    for key in ("loss", "perplexity"):
        value = metrics.get(key)
        _require(
            type(value) in (int, float) and math.isfinite(value),
            "missing/nonfinite diagnostic",
        )
    return cell, attempt, diagnostic


def compare_reports(left, right, *, mode):
    """Compare native verified projections; deliberately not a verifier itself."""
    _require(mode in ("replay", "repeat"), "unknown comparison mode")
    a, attempt_a, diagnostic_a = _completed(left)
    b, attempt_b, diagnostic_b = _completed(right)
    for field in ("scientific_sha256", "source_identity_sha256"):
        _require(
            left["provenance"][field] == right["provenance"][field],
            f"changed {field}",
        )
    # Cell, seed and budget equality follow from independent fixed-pin checks above.
    for field in ("config_sha256", "inputs"):
        _require(a[field] == b[field], f"changed {field}")
    for field in ("suite_sha256",):
        _require(
            diagnostic_a[field] == diagnostic_b[field], f"changed diagnostic {field}"
        )
    if mode == "replay":
        _require(
            a == b
            and left["diagnostic_evaluations"] == right["diagnostic_evaluations"],
            "replay changed attempts or evidence",
        )
        _require(left["provenance"] == right["provenance"], "replay changed provenance")
    else:
        _require(
            attempt_a["attempt_id"] != attempt_b["attempt_id"]
            and attempt_a["run_id"] != attempt_b["run_id"],
            "repeat reused attempt",
        )
        for key in ("loss", "perplexity"):
            _require(
                math.isclose(
                    diagnostic_a["metrics"][key],
                    diagnostic_b["metrics"][key],
                    rel_tol=1e-6,
                    abs_tol=1e-6,
                ),
                f"repeat differs: {key}",
            )
    return {
        "mode": mode,
        "status": "PASS",
        "scope": "selected_verified_snapshots",
        "scientific_result": "not_assessed",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("replay", "repeat"))
    parser.add_argument(
        "--left",
        nargs=3,
        type=Path,
        required=True,
        metavar=("LOCK", "WORKSPACE", "INDEX"),
    )
    parser.add_argument(
        "--right",
        nargs=3,
        type=Path,
        required=True,
        metavar=("LOCK", "WORKSPACE", "INDEX"),
    )
    args = parser.parse_args(argv)
    # Lazy native verifier import: --help never imports optional execution code.
    from sparselab.experiments.publication_report import build_publication_report

    try:
        reports = [
            build_publication_report(lock, workspace=workspace, index_path=index)
            for lock, workspace, index in (args.left, args.right)
        ]
        result = compare_reports(*reports, mode=args.mode)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"acceptance check refused: {error}\n")
    print(json.dumps(result, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
