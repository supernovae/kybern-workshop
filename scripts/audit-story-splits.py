#!/usr/bin/env python3
"""Read-only exact-text overlap audit of already verified native JSONL snapshots.

This is a supplementary experiment check, not native artifact verification or
curation. Holds only the small holdouts in memory; streams both training sets.
"""
import argparse
import json
from pathlib import Path


def texts(path):
    with Path(path).open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            text = row["text"]
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"Missing nonempty snapshot text in {path}")
            yield text


def audit(snapshots, panel):
    prompts = panel["prompts"]
    if not prompts or len({p["id"] for p in prompts}) != len(prompts):
        raise ValueError("Prompt IDs must be nonempty and unique")
    if any(not p["id"] or not p["prompt"].strip() for p in prompts):
        raise ValueError("Empty prompt or ID")
    holdouts, counts, duplicates = {}, {}, {}
    for arm, root in snapshots.items():
        rows = list(texts(root / "validation.jsonl"))
        if not rows:
            raise ValueError(f"Empty validation snapshot: {arm}")
        holdouts[arm] = set(rows)
        duplicates[arm] = len(rows) - len(holdouts[arm])
        counts[arm] = {"validation": len(rows), "train": 0}
    overlap = {a: {b: 0 for b in snapshots} for a in snapshots}
    prompt_hits = {a: {p["id"]: 0 for p in prompts} for a in snapshots}
    for arm, root in snapshots.items():
        for text in texts(root / "train.jsonl"):
            counts[arm]["train"] += 1
            for source, heldout in holdouts.items():
                overlap[arm][source] += text in heldout
            for prompt in prompts:
                prompt_hits[arm][prompt["id"]] += prompt["prompt"] in text
        if not counts[arm]["train"]:
            raise ValueError(f"Empty training snapshot: {arm}")
    cross_holdout = len(set.intersection(*holdouts.values()))
    clean = not (any(duplicates.values()) or cross_holdout or
                 any(any(row.values()) for row in overlap.values()) or
                 any(any(row.values()) for row in prompt_hits.values()))
    return {"status": "pass" if clean else "blocked", "counts": counts,
            "train_to_holdout_matches": overlap,
            "prompt_substring_matches": prompt_hits,
            "within_holdout_duplicates": duplicates,
            "cross_holdout_duplicates": cross_holdout,
            "scope": "Exact decoded text and case-sensitive full-prompt substring only; "
                     "no normalization, semantic near-duplicate or native verification claim. "
                     "Native snapshot verification supplies within-training dedup checks."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tinystories", type=Path, required=True)
    parser.add_argument("--simplestories", type=Path, required=True)
    parser.add_argument("--prompts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    roots = {a: getattr(args, a).resolve() for a in ("tinystories", "simplestories")}
    if roots["tinystories"] == roots["simplestories"]:
        parser.error("Supply two distinct snapshot roots")
    if any(args.output.resolve().is_relative_to(p) for p in roots.values()):
        parser.error("Audit output must be outside immutable snapshot roots")
    # Exclusive creation prevents overwriting any prior evidence.
    with args.output.open("x", encoding="utf-8") as stream:
        try:
            result = audit(roots, json.loads(args.prompts.read_text()))
        except (OSError, ValueError, KeyError, TypeError) as error:
            result = {"status": "incomplete", "reason": str(error)}
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(result["status"])
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
