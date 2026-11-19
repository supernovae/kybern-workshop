# Does historical temporal capture need the actual context-target pairing?

The frequency-only control reproduced **99.95% of the A1 excess** above its
matched-drift expectation. It used the same targets and class counts, but a
uniform prediction at every context.

| Centered comparison | Fixed initial residual energy captured at step 256 |
| --- | ---: |
| Actual step-0 predictions and targets | 0.37727827% |
| Uniform predictions, same targets | 0.37712904% |
| Shuffled targets, same step-0 predictions (median) | 0.37724825% |
| A1 drift-null expectation | 0.08541900% |

Actual minus uniform was **+0.00014923 percentage points**. The paired
story-resampling 95% conditional interval was +0.00008268 to +0.00021880
percentage points. Actual was at the 90.89th percentile of the 999 shuffled
target pairings. The 95% Monte Carlo interval for that percentile was
88.95 to 92.52; actual falls inside the central 95% shuffle reference
range (0.37720733% to 0.37729305%). The first interval only quantifies
resampling of these stories; the second only quantifies simulation uncertainty.
Neither is a statement about variation across runs.

These controls weaken the interpretation that the A1 result needed the real
context-target pairing. The geometry of which target rows enter the sample,
and with what counts, suffices to recover almost all of the excess with the
two measured head subspaces held fixed. The control does **not** establish
why the head moved, whether corpus token frequency caused the motion, or
whether movements improve predictions or updates. The predictions here come
from initialization; this is not evidence about learned context use at
mature checkpoints. The ordered-prefix training sample is small, context
exchangeability is only a diagnostic assumption, and step-256 story exposure
remains unknown.

[Frozen A2 amendment](AMENDMENT-A2.md) | [A1](historical-m1.md) |
[Receipt](results/historical-m1-a2.json) | [Plot](results/historical-m1-a2.svg)

## Reproduce

Set the same input variables and use the same archived CPU environment as
[A1](historical-m1.md). Set `A2_STUDY` to the local path of this study
directory, and work in a disposable directory outside the archive and
checkouts. The output is the raw A2 process receipt; the tracked JSON adds
outer launcher time and the command hash. The wrapper verifies both frozen
documents and all original sample/checkpoint hashes. It reuses A1's native
loader and step-0 forward pass, and loads the step-256 head without forwarding
that model. A1's centered result reproduced exactly on this host. No optimizer
updates or held-out model scores were computed.

```sh
export A2_STUDY=/path/to/workshop/experiments/tinystories/gradient-routing
cat > a2.py <<'PY'
import hashlib
import json
import os
from pathlib import Path

study = Path(os.environ["A2_STUDY"]).resolve(strict=True)
reference_bytes = (study / "results/historical-m1.json").read_bytes()
reference_sha = hashlib.sha256(reference_bytes).hexdigest()
assert reference_sha == "9c1939c4fc7941ea0ee13f4fd8a4b9c2265ecb61d2986ea58c857bb9acf235a2"
amendment_sha = hashlib.sha256((study / "AMENDMENT-A2.md").read_bytes()).hexdigest()
assert amendment_sha == "eac460e85b8116265de01c4a888e4a8a368988d51c88baaa6c4a728a584a13bd"
reference = json.loads(reference_bytes)
a1_method = (study / "historical-m1.md").read_text().split(
    "cat > probe.py <<'PY'\n", 1
)[1].split("\nPY\n", 1)[0] + "\n"
assert hashlib.sha256(a1_method.encode()).hexdigest() == reference["reproduction_probe_sha256"]
# Reuse A1's native verification, exact sample, and step-0 logits.
# Step-256 only needs the head weight, not a forward pass.
prefix, found, _ = a1_method.partition("\nwith torch.inference_mode():\n    g = ")
assert found
old = """        z = torch.cat([loaded.model(part)[:, -1].double() for part in x.split(8)])
        assert torch.isfinite(z).all()
        stats[-1]["train_probe_nll_nats"] = float(F.cross_entropy(z, y))
        heads.append(weight)
        logits.append(z)
    del loaded
    print(f"A1 evaluated 128 contexts at step {step}", file=sys.stderr, flush=True)"""
new = """        heads.append(weight)
        if step == steps[0]:
            z = torch.cat([loaded.model(part)[:, -1].double() for part in x.split(8)])
            assert torch.isfinite(z).all()
            stats[-1]["train_probe_nll_nats"] = float(F.cross_entropy(z, y))
            logits.append(z)
    del loaded
    print(f"A2 obtained authenticated inputs at step {step}", file=sys.stderr, flush=True)"""
assert prefix.count(old) == 1
prefix = prefix.replace(old, new).replace('print("A1 ', 'print("A2 ').replace('print(f"A1 ', 'print(f"A2 ')
body = r"""
for current, prior in zip(stats, reference["checkpoints"], strict=True):
    for key in current:
        if key != "train_probe_nll_nats":
            assert current[key] == prior[key], key
    if "train_probe_nll_nats" in current:
        np.testing.assert_allclose(current["train_probe_nll_nats"], prior["train_probe_nll_nats"], rtol=0, atol=1e-12)
selection_sha = canonical_digest(sample)
context_sha = hashlib.sha256(rows.numpy().astype("<i8", copy=False).tobytes()).hexdigest()
assert selection_sha == reference["sample"]["selection_sha256"]
assert context_sha == reference["sample"]["context_and_target_ids_sha256"]
assert train_sha == reference["sample"]["source_train_file_sha256"]
assert digest(run / "manifest.json") == reference["archived_run_manifest_file_sha256"]
assert source["sha256"] == reference["verified_source_identity_sha256"]
assert digest(Path(geometry.__file__)) == reference["temporal_metric_code_sha256"]
assert digest(run / "data/manifest.json") == reference["sample"]["prepared_data_manifest_file_sha256"]
assert digest(snapshot_file) == reference["sample"]["source_snapshot_manifest_file_sha256"]

def row_sq(matrix):
    return np.einsum("ij,ij->i", matrix, matrix)

centered = [W - W.mean(0) for W in heads]
bases, ranks, tolerances, spectrum_errors = [], [], [], []
for W, expected in zip(centered, reference["geometry"]["centered"]["singular_values"], strict=True):
    U, s, _ = torch.linalg.svd(torch.from_numpy(W), full_matrices=False)
    tolerance = float(s[0]) * max(W.shape) * torch.finfo(torch.float32).eps
    rank = int((s > tolerance).sum())
    Q = U[:, :rank].contiguous().numpy()
    np.testing.assert_allclose(Q.T @ Q, np.eye(rank), rtol=0, atol=1e-10)
    np.testing.assert_allclose(Q.sum(0), np.zeros(rank), rtol=0, atol=1e-10)
    np.testing.assert_allclose(s.numpy(), expected, rtol=1e-12, atol=1e-12)
    bases.append(Q)
    ranks.append(rank)
    tolerances.append(tolerance)
    spectrum_errors.append(float(np.abs(s.numpy() - expected).max()))
assert ranks == reference["geometry"]["centered"]["numerical_ranks"]
np.testing.assert_allclose(tolerances, reference["geometry"]["centered"]["absolute_rank_tolerances"], rtol=1e-12, atol=1e-12)
a, b = bases
D = a.T @ b
future_complement_rows = b - a @ D
P = logits[0].softmax(-1).numpy()
n, vocab = P.shape
target = y.numpy()
slots = np.arange(n)

def table(p):
    # For row p_i and label slot j, residual coordinates in Q256 are
    # p_i Q256 - (p_i Q0)D - (Q256-Q0 D)[y_j].
    p0 = p @ a
    c = p @ b - p0 @ D
    e = future_complement_rows[target]
    num = row_sq(c)[:, None] + row_sq(e) - 2 * c @ e.T
    q = a[target]
    den = (
        (row_sq(p) - row_sq(p0))[:, None]
        + (1 - row_sq(q))
        - 2 * p[:, target]
        + 2 * p0 @ q.T
    )
    assert np.isfinite(num).all() and np.isfinite(den).all()
    assert np.min(num) >= 0 and np.min(den) > 0 and np.max(num-den) <= 1e-12
    return num, den

def dense(p, labels):
    g = p.copy()
    g[slots, labels] -= 1
    assert float(np.abs(g.sum(axis=1)).max()) <= 1e-12
    r = geometry.residual_component(g, a)
    return row_sq(r @ b), row_sq(r), r

def check_rows(table_rows, dense_rows):
    tnum, tden = table_rows
    dnum, dden, _ = dense_rows
    np.testing.assert_allclose(tnum, dnum, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(tden, dden, rtol=1e-12, atol=1e-12)
    return {
        "max_absolute_numerator_row_error": float(np.max(np.abs(tnum-dnum))),
        "max_absolute_denominator_row_error": float(np.max(np.abs(tden-dden))),
        "absolute_pooled_numerator_error": float(abs(tnum.sum()-dnum.sum())),
        "absolute_pooled_denominator_error": float(abs(tden.sum()-dden.sum())),
    }

def pooled(num, den):
    sn, sd = float(num.sum()), float(den.sum())
    return {"numerator": sn, "denominator": sd, "fraction": sn/sd}

numerators, denominators = table(P)
uniform = np.full_like(P, 1/vocab)
uniform_nums, uniform_dens = table(uniform)
a_rows = numerators[slots, slots], denominators[slots, slots]
u_rows = uniform_nums[slots, slots], uniform_dens[slots, slots]
actual, frequency = pooled(*a_rows), pooled(*u_rows)
dense_actual = dense(P, target)
dense_uniform = dense(uniform, target)
self_capture = geometry.captured_residual_energy(dense_actual[2], a)
assert self_capture <= 1e-20
assert abs(actual["fraction"] - reference["geometry"]["centered"]["A_0_256"]) <= 1e-12
for key, ref_key in (
    ("numerator", "captured_squared_energy_0_256"),
    ("denominator", "fixed_initial_residual_squared_energy"),
):
    np.testing.assert_allclose(actual[key], reference["geometry"]["centered"][ref_key], rtol=1e-12, atol=1e-12)
checks = {"actual": check_rows(a_rows, dense_actual), "uniform": check_rows(u_rows, dense_uniform)}

rng = np.random.Generator(np.random.PCG64(18121))
permutations = np.stack([rng.permutation(n) for _ in range(999)])
pn = numerators[slots, permutations].sum(1)
pd = denominators[slots, permutations].sum(1)
control = pn / pd
first = permutations[0]
checks["first_permutation"] = check_rows(
    (numerators[slots, first], denominators[slots, first]), dense(P, target[first])
)
assert np.all(np.sort(target[permutations], axis=1) == np.sort(target))
n_le = int((control <= actual["fraction"]).sum())
n_mc = len(control)
cdf = n_le/n_mc
z95 = 1.959963984540054
wilson_denom = 1 + z95**2/n_mc
wilson_center = (cdf + z95**2/(2*n_mc))/wilson_denom
wilson_radius = z95*np.sqrt(cdf*(1-cdf)/n_mc + z95**2/(4*n_mc**2))/wilson_denom
q_perm = np.quantile(control, [.025, .5, .975], method="linear")

bootstrap = np.random.Generator(np.random.PCG64(18122)).integers(n, size=(1999, n))
difference_draws = (
    a_rows[0][bootstrap].sum(1) / a_rows[1][bootstrap].sum(1)
    - u_rows[0][bootstrap].sum(1) / u_rows[1][bootstrap].sum(1)
)
lo_hi = np.quantile(difference_draws, [.025, .975], method="linear").tolist()
classes, counts = np.unique(target, return_counts=True)
prefix_wall = reference["cost"]["wall_seconds_including_launcher"]
usage = resource.getrusage(resource.RUSAGE_SELF)
receipt = {
    "protocol": "AMENDMENT-A2",
    "amendment_sha256": amendment_sha,
    "classification": "one_historical_run_conditional_exploratory_diagnostic",
    "a1_receipt_sha256": reference_sha,
    "a1_context_target_ids_sha256": context_sha,
    "a1_sample_selection_sha256": selection_sha,
    "archive_run_id": run.name,
    "verified_source_identity_sha256": source["sha256"],
    "checkpoints": stats,
    "a1_reproduced_centered_self_capture": self_capture,
    "a1_reproduced_centered_fraction_error": actual["fraction"]-reference["geometry"]["centered"]["A_0_256"],
    "centered_ranks": ranks,
    "centered_rank_tolerances": tolerances,
    "centered_spectrum_max_absolute_errors": spectrum_errors,
    "target_histogram": [[int(cls), int(count)] for cls, count in zip(classes, counts, strict=True)],
    "actual": actual,
    "uniform_predictor": frequency,
    "matched_drift_null_reference": reference["geometry"]["centered"]["equal_rank_matched_drift_null"],
    "primary_actual_minus_uniform": actual["fraction"]-frequency["fraction"],
    "paired_story_bootstrap": {
        "seed": 18122, "draws": len(bootstrap), "conditional_percentile_95_interval": lo_hi,
        "draw_indices_sha256_le_int64": hashlib.sha256(bootstrap.astype("<i8", copy=False).tobytes()).hexdigest(),
    },
    "permuted_targets": {
        "seed": 18121, "draws": n_mc, "count_less_or_equal_actual": n_le, "actual_empirical_cdf": cdf,
        "monte_carlo_wilson_95_interval_for_empirical_cdf": [
            max(0, wilson_center-wilson_radius), min(1, wilson_center+wilson_radius)
        ],
        "median_fraction": float(q_perm[1]), "central_95_reference_interval": [float(q_perm[0]), float(q_perm[2])],
        "row_permutation_indices_sha256_le_int64": hashlib.sha256(permutations.astype("<i8", copy=False).tobytes()).hexdigest(),
        "numerator_total": pn.tolist(), "denominator_total": pd.tolist(), "capture_fraction": control.tolist(),
    },
    "arithmetic_checks": checks,
    "runtime": {
        "python": sys.version.split()[0], "torch": str(torch.__version__), "numpy": np.__version__,
        "backend": "cpu", "forward_dtype": "float32", "geometry_dtype": "float64",
    },
    "cost": {
        "a1_wall_seconds_including_launcher": prefix_wall,
        "a2_wall_seconds_inside_process": time.monotonic()-started,
        "a2_cpu_user_seconds": usage.ru_utime, "a2_cpu_sys_seconds": usage.ru_stime,
        "a2_peak_process_rss_kib": usage.ru_maxrss,
        "a2_cpu_affinity_slots": len(os.sched_getaffinity(0)),
        "address_space_limit_bytes": 4 * 2**30,
        "a2_wall_limit_seconds": 220,
        "combined_wall_limit_seconds": 240,
        "a2_forward_contexts": n, "a2_forward_input_positions": 32*n,
        "gpu_used": False, "optimizer_updates": 0, "attempts": 1,
    },
}
print(json.dumps(receipt, separators=(",", ":"), sort_keys=True, allow_nan=False))
"""
exec(compile(prefix + "\n" + body, "<a2-historical-probe>", "exec"))
PY
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$A1_ARCHIVE_SRC:$A1_CURRENT_SRC" \
CUDA_VISIBLE_DEVICES=-1 HIP_VISIBLE_DEVICES=-1 ROCR_VISIBLE_DEVICES=-1 \
TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 \
OPENBLAS_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4 MALLOC_ARENA_MAX=2 PYTHONHASHSEED=0 \
/usr/bin/time -v -o cost.txt timeout --kill-after=10s 210s \
  taskset -c "$A1_CPU_LIST" prlimit --as=4294967296:4294967296 -- \
  "$A1_PYTHON" a2.py > receipt.json
```

A transcription error in a SHA literal stopped a 0.03 s preflight before any
archived source/model was imported or archive data accessed. No analysis
parameters changed. The single scientific A2 attempt then took 6.53 seconds
and peaked at 846,612 KiB RSS. A1 plus A2 plus preflight took 16.84 seconds,
peaking at 850,204 KiB RSS, under a four-CPU and 4 GiB address-space cap.
