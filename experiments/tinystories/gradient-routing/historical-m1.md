# Historical temporal capture (M1, amendment A1)

The centered step-256 output subspace captured **0.37728%** of the step-0
residual energy, versus **0.08542%** expected under the matched-drift null:
**+0.29186 percentage points** (4.42 times the expectation). The raw capture
was 0.27222%; it has no analytical null in A1. Centered self-capture was
3.47e-30, and both centered numerical ranks were 640 of an ambient 4095.
This is one retrospective comparison on one archived 4k-vocabulary, tied
TinyStories run. It does not establish efficacy, significance, or whether
another checkpoint pair or run shows the same pattern.

[Receipt](results/historical-m1.json) | [Comparison plot](results/historical-m1.svg)
| [Frozen plan](AMENDMENT-A1.md)

The probe uses only the first 128 eligible distinct stories from the run's
deduplicated source-training snapshot, as frozen before inspection. For each,
we verified the archival tokenizer's encoded IDs and trailing EOS against the
packed train file, passed tokens 0 through 31 as a standalone context, and scored
token 32 (zero-based). The model received no padding, artificial BOS/EOS, or
preceding story history. These are probes at story-relative positions, not
replays of the training sampler's causal windows. The receipt lists source
ordinals, packed target offsets, and hashes. Training exposure at step 256
was not verified. No development or final stories were scored. The archived
loader read artifact bytes, including the normal prepared validation integrity
check, but did not run model evaluation on validation.

We fixed the residual from step 0 throughout. The centered model places the
CE rows and both projector bases in the vocabulary's zero-sum space. The null
randomizes the future subspace's orientation only in the initial complement,
holding its measured principal-angle drift fixed. It is an expectation, not
a confidence interval or a p-value. The geometry ignores singular-value
weighting and does not measure parameter updates or predict finite loss gains.

## Reproduce

Use the original SparseLab source checkout at commit
`903ad2f0bb261935132dee53295aba6b66f8e792`; the script verifies all 402
Python source files from the archived run manifest. Use the current Model Lab
study checkout for its `klab.research.routing_mechanisms` diagnostics; the
receipt pins their file hash. Use a CPU Python environment with the archived
loader's dependencies (measured: Python 3.14.4 and PyTorch 2.14.1+cpu).
Set the variables below to local inputs, then work in a disposable directory
outside either checkout and the archive. Use four permitted CPU IDs in
`A1_CPU_LIST`. No separate training or data regeneration is needed.

```sh
export A1_RUN=/path/to/archived/runs/tinystories-50m-bf16
export A1_TRAIN=/path/to/archived/snapshot/train.jsonl
export A1_ARCHIVE_SRC=/path/to/archived/lab/src
export A1_CURRENT_SRC=/path/to/model-lab/src
export A1_PYTHON=/path/to/local/cpu-venv/bin/python
export A1_CPU_LIST=0-3
```

```sh
cat > probe.py <<'PY'
from __future__ import annotations
import hashlib, json, os, resource, sys, time
from pathlib import Path

started = time.monotonic()
run = Path(os.environ["A1_RUN"]).resolve(strict=True)
archive_src = Path(os.environ["A1_ARCHIVE_SRC"]).resolve(strict=True)
current_src = Path(os.environ["A1_CURRENT_SRC"]).resolve(strict=True)
load_json = lambda path: json.loads(path.read_text(encoding="utf-8"))
run_manifest = load_json(run / "manifest.json")

# Verify the historical code before importing it.
def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

source = run_manifest["source_identity"]
assert len(source["files"]) == 402
for relative, sha in source["files"]:
    assert digest(archive_src / "sparselab" / relative) == sha, relative
print("A1 verified 402 historical source files", file=sys.stderr, flush=True)

import numpy as np
import torch
import torch.nn.functional as F
import sparselab.evaluation.inference as historical
import klab.research.routing_mechanisms as geometry
from sparselab.canonical import canonical_digest

assert Path(historical.__file__).resolve().is_relative_to(archive_src)
assert Path(geometry.__file__).resolve().is_relative_to(current_src)
assert len(os.sched_getaffinity(0)) == 4
assert resource.getrlimit(resource.RLIMIT_AS) == (4 * 2**30, 4 * 2**30)
torch.set_num_threads(4)
torch.set_num_interop_threads(1)

train_file = Path(os.environ["A1_TRAIN"]).resolve(strict=True)
snapshot_file = train_file.with_name("manifest.json")
snapshot = load_json(snapshot_file)
prepared = load_json(run / "data/manifest.json")
assert prepared["dataset_snapshot"] == snapshot
assert prepared["packing_version"] == "contiguous-eos-v6"
assert prepared["supervision"] == {"kind": "all_tokens"}
assert snapshot["splits"]["train"]["path"] == train_file.name
train_sha = digest(train_file)
assert train_sha == snapshot["splits"]["train"]["sha256"]
assert snapshot["lock"]["source"]["dedup"]["overlap"] == "exclude"
assert snapshot["lock"]["source"]["dedup"]["within_split"] == "exclude"
print("A1 verified train-only snapshot bytes", file=sys.stderr, flush=True)

steps = (0, 256)
stats, heads, logits = [], [], []
sample, encoded_rows = [], []
for step, generation in zip(steps, (1, 2), strict=True):
    checkpoint = f"step_{step:08}_gen_{generation:06}"
    loaded = historical.load_run(run.name, run.parent, checkpoint=checkpoint, backend="cpu")
    identity = loaded.identity
    assert identity["runtime"]["backend"] == "cpu" and identity["runtime"]["precision"] == "fp32"
    assert identity["step"] == step and identity["source_identity_sha256"] == source["sha256"]
    assert loaded.config.model.tie_embeddings and loaded.config.model.memory == "none"
    assert loaded.config.model.hidden_dim == 640 and loaded.config.model.vocab_size == 4096
    manifest_file = run / "checkpoints" / checkpoint / "manifest.json"
    manifest = load_json(manifest_file)
    assert manifest["sha256"] == identity["checkpoint_sha256"]
    shards = [record for record in manifest["files"] if record["name"].endswith(".safetensors")]
    assert len(shards) == 1
    for shard in shards:
        assert digest(manifest_file.parent / shard["name"]) == shard["sha256"]
    stats.append({
        "step": step,
        "tokens_seen": identity["tokens_seen"],
        "checkpoint": checkpoint,
        "checkpoint_manifest_content_sha256": manifest["sha256"],
        "checkpoint_manifest_file_sha256": digest(manifest_file),
        "safetensors": [
            {name: shard[name] for name in ("name", "bytes", "sha256")} for shard in shards
        ],
        "tokenizer_file_sha256": identity["tokenizer_sha256"],
        "packed_train_file_sha256": identity["data_sha256"]["train"],
    })
    print(f"A1 native CPU loader verified step {step}", file=sys.stderr, flush=True)
    if step == steps[0]:
        packed = np.load(run / "data/train.npy", mmap_mode="r", allow_pickle=False)
        eos = loaded.tokenizer.token_to_id("<eos>")
        assert eos is not None
        offset, seen = 0, set()
        with train_file.open("rb") as stream:
            for line_no, raw in enumerate(stream):
                story = json.loads(raw)
                text = story["text"]
                ids = loaded.tokenizer.encode(text, add_special_tokens=False).ids
                # Native contiguous packing appends EOS after each source story.
                expected = np.asarray([*ids, eos], dtype=packed.dtype)
                np.testing.assert_array_equal(packed[offset:offset+len(expected)], expected)
                text_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
                if len(ids) >= 33 and eos not in ids[:33] and text_sha not in seen:
                    seen.add(text_sha)
                    sample.append({
                        "train_snapshot_line_zero_based": line_no,
                        "source_ordinal": story["ordinal"],
                        "target_story_token_position_zero_based": 32,
                        "target_packed_train_position_zero_based": offset + 32,
                        "text_sha256": text_sha,
                    })
                    encoded_rows.append(ids[:33])
                offset += len(expected)
                if len(sample) == 128:
                    break
        assert len(sample) == 128
        assert len({row["source_ordinal"] for row in sample}) == 128
        rows = torch.tensor(encoded_rows, dtype=torch.long)
        x, y = rows[:, :32].contiguous(), rows[:, 32].contiguous()
        del packed
        print("A1 fixed 128 distinct packed-train prefixes", file=sys.stderr, flush=True)
    else:
        assert stats[0]["tokenizer_file_sha256"] == stats[1]["tokenizer_file_sha256"]
        assert stats[0]["packed_train_file_sha256"] == stats[1]["packed_train_file_sha256"]
    with torch.inference_mode():
        weight = loaded.model.output.weight.detach().double().numpy()
        z = torch.cat([loaded.model(part)[:, -1].double() for part in x.split(8)])
        assert torch.isfinite(z).all()
        stats[-1]["train_probe_nll_nats"] = float(F.cross_entropy(z, y))
        heads.append(weight)
        logits.append(z)
    del loaded
    print(f"A1 evaluated 128 contexts at step {step}", file=sys.stderr, flush=True)

with torch.inference_mode():
    g = logits[0].softmax(dim=-1)
    g[torch.arange(len(y)), y] -= 1
    assert float(g.sum(dim=1).abs().max()) <= 1e-12
    G = g.numpy()
    vocab = G.shape[1]
    ret = {}
    for label, centered in (("raw", False), ("centered", True)):
        maps = [W - W.mean(0) if centered else W for W in heads]
        bases, ranks, spectra, tolerances = [], [], [], []
        dim = vocab - int(centered)
        for W in maps:
            U, s, _ = torch.linalg.svd(torch.from_numpy(W), full_matrices=False)
            tolerance = float(s[0]) * max(W.shape) * torch.finfo(torch.float32).eps
            rank = int((s > tolerance).sum())
            assert 0 < rank < dim
            Q = U[:, :rank].contiguous().numpy()
            np.testing.assert_allclose(Q.T @ Q, np.eye(rank), rtol=0, atol=1e-10)
            if centered:
                np.testing.assert_allclose(Q.sum(0), np.zeros(rank), rtol=0, atol=1e-10)
            bases.append(Q)
            ranks.append(rank)
            spectra.append(s.tolist())
            tolerances.append(tolerance)
        a, b = bases
        residual = geometry.residual_component(G, a)
        denominator = float(np.sum(residual**2))
        total = float(np.sum(G**2))
        overlap = float(np.sum((a.T @ b)**2))
        residual_capture = geometry.captured_residual_energy(residual, b)
        self_capture = geometry.captured_residual_energy(residual, a)
        assert self_capture <= 1e-20
        np.testing.assert_allclose(denominator + np.sum((G @ a)**2), total, rtol=1e-12)
        np.testing.assert_allclose(
            np.sum((G @ b - (G @ a) @ (a.T @ b))**2),
            denominator * residual_capture,
            rtol=1e-12, atol=1e-12
        )
        drift = float(np.sum((b - a @ (a.T @ b))**2))
        np.testing.assert_allclose(drift, ranks[1] - overlap, rtol=1e-10, atol=1e-10)
        null = (
            geometry.matched_drift_null(a, b, ambient_dimension=dim)
            if centered and ranks[0] == ranks[1] else None
        )
        ret[label] = {
            "ambient_dimension": dim,
            "singular_values": spectra,
            "numerical_ranks": ranks,
            "absolute_rank_tolerances": tolerances,
            "relative_head_frobenius_change": float(np.linalg.norm(maps[1] - maps[0]) / np.linalg.norm(maps[0])),
            "total_gradient_squared_energy": total,
            "fixed_initial_residual_squared_energy": denominator,
            "captured_squared_energy_0_0": float(np.sum((residual @ a)**2)),
            "captured_squared_energy_0_256": float(np.sum((residual @ b)**2)),
            "A_0_0": self_capture,
            "A_0_256": residual_capture,
            "subspace_overlap_squared_frobenius": overlap,
            "future_basis_drift_into_initial_complement_squared_frobenius": drift,
            "equal_rank_matched_drift_null": null,
            "excess_over_matched_drift_null": residual_capture - null if null is not None else None,
        }

assert ret["centered"]["equal_rank_matched_drift_null"] is not None
usage = resource.getrusage(resource.RUSAGE_SELF)
receipt = {
    "protocol": "AMENDMENT-A1",
    "classification": "single_run_historical_geometric_probe_not_efficacy",
    "archive_run_id": run.name,
    "archived_recorded_git_commit": run_manifest["git_commit"],
    "archived_run_manifest_file_sha256": digest(run / "manifest.json"),
    "verified_source_identity_sha256": source["sha256"],
    "verified_source_files": len(source["files"]),
    "temporal_metric_code_sha256": digest(Path(geometry.__file__)),
    "backend": "cpu",
    "forward_dtype": "torch.float32",
    "geometry_dtype": "torch.float64",
    "versions": {"torch": str(torch.__version__), "numpy": np.__version__, "python": sys.version.split()[0]},
    "storage_verification": "cold native load_run for each generation; SHA-256 safetensors and full source-train snapshot",
    "checkpoints": stats,
    "sample": {
        "split": "source_train",
        "role": "retrospective_training_only_geometry",
        "source_revision": snapshot["lock"]["source"]["revision"],
        "source_snapshot_manifest_sha256": snapshot["manifest_sha256"],
        "source_snapshot_manifest_file_sha256": digest(snapshot_file),
        "source_train_file_sha256": train_sha,
        "prepared_data_manifest_file_sha256": digest(run / "data/manifest.json"),
        "order": "first 128 distinct eligible stories in train.jsonl line order",
        "distinct_story_count": len(sample),
        "distinct_target_id_count": len(set(y.tolist())),
        "context_tokens": 32,
        "scored_targets": len(sample),
        "mask": "all positions valid; no supplied padding, manual EOS target, or cross-story history",
        "dedup": "native snapshot excludes within-split repeats and train-validation overlaps; local exact text hash filter",
        "step_256_exposure_status": "unknown; exact native sampler cursor membership was not verified",
        "selection_sha256": canonical_digest(sample),
        "context_and_target_ids_sha256": hashlib.sha256(rows.numpy().astype("<i8", copy=False).tobytes()).hexdigest(),
        "context_and_target_ids_encoding": "row-major 128 x 33 little-endian int64",
        "positions": sample,
    },
    "rank_tolerance": "sigma_max * max(V, d) * eps(float32)",
    "numerical_checks": {"g_row_sum_abs_max": float(np.abs(G.sum(axis=1)).max()), "self_capture_fraction_max_allowed": 1e-20},
    "null_policy": "Primary centered equal rank in 1-perp with complement orientation randomized conditional on drift; only report raw capture, no raw analytical null",
    "geometry": ret,
    "cost": {
        "wall_seconds_inside_process": time.monotonic()-started,
        "cpu_user_seconds": usage.ru_utime,
        "cpu_sys_seconds": usage.ru_stime,
        "peak_process_rss_kib": usage.ru_maxrss,
        "cpus_allowed": len(os.sched_getaffinity(0)),
        "wall_limit_seconds": 240,
        "address_space_limit_bytes": 4 * 2**30,
        "gpu_used": False,
        "optimizer_updates": 0,
        "forward_contexts_total": 256,
        "forward_input_positions": 8192,
        "attempts": 1,
    },
}
print(json.dumps(receipt, separators=(",", ":"), sort_keys=True, allow_nan=False))
PY
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$A1_ARCHIVE_SRC:$A1_CURRENT_SRC" \
CUDA_VISIBLE_DEVICES=-1 HIP_VISIBLE_DEVICES=-1 ROCR_VISIBLE_DEVICES=-1 \
TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 \
OPENBLAS_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4 MALLOC_ARENA_MAX=2 PYTHONHASHSEED=0 \
/usr/bin/time -v -o cost.txt timeout --kill-after=10s 230s \
  taskset -c "$A1_CPU_LIST" prlimit --as=4294967296:4294967296 -- \
  "$A1_PYTHON" probe.py > receipt.json
```

Compare planned sample, safetensor and source identities before comparing the
metrics. Timing and machine-dependent roundoff may differ. The recorded
attempt took 10.28 seconds including launcher overhead and 850,204 KiB peak
resident memory, with four permitted CPUs, no GPU, 8,192 forward input
positions and no training updates. The receipt also records the runner's
in-process timing.
