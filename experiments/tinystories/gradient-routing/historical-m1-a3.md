# Mature-checkpoint temporal capture (A3)

The mature model captured more of its initial centered residual with the real
context-target pairing than with every one of 999 shuffled target pairings.
But the paired actual-minus-uniform interval spanned zero. The registered
rule required all three gates, so **A3 does not prioritize GPU M2**.

| Centered comparison | Fraction of residual squared energy captured |
| --- | ---: |
| Actual step-243968 probabilities and targets | 0.04687071% |
| Uniform probabilities, same targets | 0.04582651% |
| In-probe mean probability vector, same targets | 0.04588035% |
| Shuffled targets, actual probability rows (median) | 0.04542322% |
| Matched-drift expectation | 0.04352489% |

Actual minus uniform was +0.00104420 percentage points; the paired
story-resampling 95% conditional interval was [-0.00013449, +0.00228634]
percentage points. The central 95% conditional shuffle reference range was
0.04502304% to 0.04583232%; actual exceeded all 999 draws. The 95% Monte Carlo
interval for its empirical percentile was 99.62 to 100.00. This is neither
a zero population p-value nor uncertainty across trained models. The uniform
proxy left 31.21% of positive actual-minus-drift-null excess unexplained,
above the registered 10% gate. Two gates passed; the paired interval did not.

The mature result is more compatible with a role for pairing than the
[initialization pair](historical-m1-a2.md), but it only describes geometry
in the trained checkpoint and these 128 fixed training prefixes. It neither
proves useful contextual learning nor justifies a GPU continuation. The
in-probe mean predictor is a descriptive control, not an external fit.
Story-level exposure is unverified. No held-out stories were scored.

[Frozen A3 amendment](AMENDMENT-A3.md) | [Completion amendment](AMENDMENT-A3.1.md)
| [Receipt](results/historical-m1-a3.json) | [Plot](results/historical-m1-a3.svg)

## Reproduce

Use the same frozen A1 source-training snapshot and CPU environment documented
in [A1](historical-m1.md). Change `A1_RUN` to the local archived
`tinystories-50m-bf16-resume-2` run directory. Set `A3_STUDY` to this
study directory in a local checkout, and work in a disposable directory outside
both checkouts and the archive. The method pins A1 and A2 receipts and sample
identities, the A3 plan, and both mature checkpoint manifests and weight hashes.
It forwards only step 243968. No training state is deserialized. The code below
is the successful A3.1 wrapper; it differs from the original only by the
name of a digest helper, as detailed in the completion amendment.

```sh
export A1_RUN=/path/to/archived/runs/tinystories-50m-bf16-resume-2
export A3_STUDY=/path/to/workshop/experiments/tinystories/gradient-routing
cat > a3-1.py <<'PY'
import hashlib
import json
import os
from pathlib import Path

def a3_sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()

study = Path(os.environ["A3_STUDY"]).resolve(strict=True)
pins = {
    "results/historical-m1.json": "9c1939c4fc7941ea0ee13f4fd8a4b9c2265ecb61d2986ea58c857bb9acf235a2",
    "results/historical-m1-a2.json": "c68541a1d8b939ecce3b4d5ad7bd4cc1fb765072bbbcb82172dd4d60b2da4fb1",
    "AMENDMENT-A3.md": "2558b3837cd737479ba9cdb5a840db610acd100c8b720fc30c831333081403db",
}
pinned = {path: (study/path).read_bytes() for path in pins}
assert {path: a3_sha256_bytes(content) for path, content in pinned.items()} == pins
a1 = json.loads(pinned["results/historical-m1.json"])
a2 = json.loads(pinned["results/historical-m1-a2.json"])
a1_method = (study/"historical-m1.md").read_text().split("cat > probe.py <<'PY'\n", 1)[1].split("\nPY\n", 1)[0]+"\n"
assert a3_sha256_bytes(a1_method.encode()) == a1["reproduction_probe_sha256"]
prefix, matched, _ = a1_method.partition("\nwith torch.inference_mode():\n    g = ")
assert matched
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
    print(f"A3 obtained authenticated inputs at step {step}", file=sys.stderr, flush=True)"""
for source, patch in ((old,new), ("steps = (0, 256)", "steps = (243968, 244141)"),
                      ("zip(steps, (1, 2),", "zip(steps, (952, 953),")):
    assert prefix.count(source) == 1
    prefix = prefix.replace(source, patch)
prefix = prefix.replace('print("A1 ', 'print("A3 ').replace('print(f"A1 ', 'print(f"A3 ')

analysis = r"""
assert run.name == "tinystories-50m-bf16-resume-2"
assert run_manifest["sha256"] == "f39228067ce466c57d505fa23b8a4ca0784a10bc7a72e22225fbae9cd64fdef1"
assert run_manifest["parent_run_id"] == "tinystories-50m-bf16-resume-1"
assert run_manifest["checkpoint_sha256"] == "78e06a144b31f1406de7b42bfb0ec8a945d9e037aeefe2390efefc299eac3e1b"
late = [
    (243968, 999292928, "6fc016d116fbef56d73b89b81612e9f11bb54be3bb4ef288be56d1e6513db2a3",
     "2078299893b06e546a44d2dfb0f18013fb09f596430f6042a86fe32ad2c26c27",
     "19ffde5f1d8d042c533f948f2e1a0cd61174920c75fbf20b6976923758505507"),
    (244141, 1000001536, "c72d7d0283de2c6008f1b80d855bad6cb6ebc497f0094957a8982bd58a049110",
     "48aca0e3d19a86caf1314e43ee1214efd06fe99201f112585085b0126ad2a608",
     "59a5b29d86846a8ac11e24bf220740b6aae28dfb1ae5021fdaaff4c98df97dcf"),
]
for current, expected in zip(stats, late, strict=True):
    assert (
        current["step"], current["tokens_seen"], current["checkpoint_manifest_content_sha256"],
        current["checkpoint_manifest_file_sha256"], current["safetensors"][0]["sha256"],
    ) == expected, current["step"]
    for key in ("tokenizer_file_sha256", "packed_train_file_sha256"):
        assert current[key] == a1["checkpoints"][0][key], key
assert len(logits) == 1 and "train_probe_nll_nats" in stats[0] and "train_probe_nll_nats" not in stats[1]
sample_identity = {
    "selection_sha256": canonical_digest(sample),
    "context_and_target_ids_sha256": a3_sha256_bytes(rows.numpy().astype("<i8",copy=False).tobytes()),
    "source_train_file_sha256": train_sha,
    "prepared_data_manifest_file_sha256": digest(run/"data/manifest.json"),
    "source_snapshot_manifest_file_sha256": digest(snapshot_file),
}
assert all(a1["sample"][key]==value for key,value in sample_identity.items())
assert source["sha256"] == a1["verified_source_identity_sha256"]
assert digest(Path(geometry.__file__)) == a1["temporal_metric_code_sha256"]

def row_sq(matrix):
    return np.einsum("ij,ij->i",matrix,matrix)

P = logits[0].softmax(-1).numpy()
labels = y.numpy()
n,V = P.shape
assert n == 128 and V == 4096
indices = np.arange(n)
heads = [W-W.mean(axis=0) for W in heads]
bases,ranks,tolerances,spectra = [],[],[],[]
for W in heads:
    U,s,_ = torch.linalg.svd(torch.from_numpy(W),full_matrices=False)
    tol = float(s[0])*max(W.shape)*torch.finfo(torch.float32).eps
    rank = int((s>tol).sum())
    Q = U[:,:rank].contiguous().numpy()
    np.testing.assert_allclose(Q.T@Q,np.eye(rank),rtol=0,atol=1e-10)
    np.testing.assert_allclose(Q.sum(axis=0),np.zeros(rank),rtol=0,atol=1e-10)
    ranks.append(rank); tolerances.append(tol); spectra.append(s.tolist()); bases.append(Q)
assert 0<ranks[0]==ranks[1]<V-1
qt,qs = bases
D = qt.T@qs
complement_rows = qs-qt@D
overlap = float(np.square(D).sum())
drift = float(np.square(complement_rows).sum())
np.testing.assert_allclose(drift,ranks[1]-overlap,rtol=1e-10,atol=1e-10)
null = geometry.matched_drift_null(qt,qs,ambient_dimension=V-1)

def dense(p,target):
    g = p.copy()
    i = np.arange(len(target))
    g[i,target] = 0
    g[i,target] = -g.sum(axis=1)
    assert float(np.abs(g.sum(axis=1)).max())<=1e-12
    r = geometry.residual_component(g,qt)
    return row_sq(r@qs), row_sq(r), r, row_sq(g)

def table(p):
    # c_i is p_i's projected residual coordinate; e_j is the target's.
    old_c = p@qt
    c = p@qs-old_c@D
    e = complement_rows[labels]
    q = qt[labels]
    num = row_sq(c)[:,None]+row_sq(e)-2*(c@e.T)
    den = (row_sq(p)-row_sq(old_c))[:,None]+(1-row_sq(q))-2*p[:,labels]+2*(old_c@q.T)
    assert np.isfinite(num).all() and np.isfinite(den).all()
    fragile = (p[:,labels]>0.99)|(den<=1e-10)|(num<0)
    ri,cj = np.nonzero(fragile)
    for start in range(0,len(ri),128):
        ii,jj = ri[start:start+128],cj[start:start+128]
        num[ii,jj],den[ii,jj],_,_ = dense(p[ii],labels[jj])
    assert num.min()>=0 and den.min()>=0 and (num-den).max()<=1e-12
    return num,den,len(ri)

def pooled(num,den):
    a,b = float(num.sum()),float(den.sum())
    assert b>0
    return {"numerator":a,"denominator":b,"fraction":a/b}

def check(estimate,direct):
    en,ed = estimate
    dn,dd,_,_ = direct
    np.testing.assert_allclose(en,dn,rtol=1e-12,atol=1e-12)
    np.testing.assert_allclose(ed,dd,rtol=1e-12,atol=1e-12)
    error = abs(pooled(en,ed)["fraction"]-pooled(dn,dd)["fraction"])
    assert error<=1e-12
    return {"maximum_absolute_numerator_row_error":float(np.abs(en-dn).max()),
            "maximum_absolute_denominator_row_error":float(np.abs(ed-dd).max()),
            "absolute_pooled_fraction_error":error}

uniform = np.full_like(P,1/V)
mean_p = np.broadcast_to(P.mean(axis=0),P.shape)
stats_by,counts_by,checks,rows_by = {},{},{},{}
for name,p in (("actual",P),("uniform",uniform),("in_probe_mean",mean_p)):
    num,den,counts_by[name] = table(p)
    if name=="actual":
        pair_num,pair_den = num,den
    estimated = num[indices,indices],den[indices,indices]
    direct = dense(p,labels)
    stats_by[name] = pooled(*estimated)
    checks[name] = check(estimated,direct)
    rows_by[name] = estimated
    if name=="actual":
        self_check = pooled(row_sq(direct[2]@qt),direct[1])
        total_energy = float(direct[3].sum())
        assert self_check["fraction"]<=1e-20
        np.testing.assert_allclose(self_check["denominator"],stats_by[name]["denominator"],rtol=1e-12,atol=1e-12)
assert sum(counts_by.values())>0 or float(P[:,labels].max())<=0.99

rng = np.random.Generator(np.random.PCG64(18121))
perms = np.stack([rng.permutation(n) for _ in range(999)])
perm_sha = a3_sha256_bytes(perms.astype("<i8",copy=False).tobytes())
assert perm_sha == a2["permuted_targets"]["row_permutation_indices_sha256_le_int64"]
assert np.all(np.sort(labels[perms],axis=1)==np.sort(labels))
pn,pd = pair_num[indices,perms].sum(axis=1),pair_den[indices,perms].sum(axis=1)
assert np.all(pd>0)
shuffles = pn/pd
first = perms[0]
checks["first_permutation"] = check((pair_num[indices,first],pair_den[indices,first]),dense(P,labels[first]))

actual = stats_by["actual"]["fraction"]
base = stats_by["uniform"]["fraction"]
delta = actual-base
excess = actual-null
unexplained = delta/excess if excess>0 else None
le = int((shuffles<=actual).sum())
q025,med,q975 = np.quantile(shuffles,[.025,.5,.975],method="linear").tolist()
m,cdf = len(shuffles),le/len(shuffles)
z = 1.959963984540054
wilson_den = 1+z*z/m
wc = (cdf+z*z/(2*m))/wilson_den
wr = z*np.sqrt(cdf*(1-cdf)/m+z*z/(4*m*m))/wilson_den
boot = np.random.Generator(np.random.PCG64(18122)).integers(n,size=(1999,n))
boot_sha = a3_sha256_bytes(boot.astype("<i8",copy=False).tobytes())
assert boot_sha == a2["paired_story_bootstrap"]["draw_indices_sha256_le_int64"]
an,ad = rows_by["actual"]
un,ud = rows_by["uniform"]
assert np.all(ad[boot].sum(axis=1)>0) and np.all(ud[boot].sum(axis=1)>0)
diff = an[boot].sum(axis=1)/ad[boot].sum(axis=1)-un[boot].sum(axis=1)/ud[boot].sum(axis=1)
interval = np.quantile(diff,[.025,.975],method="linear").tolist()
gates = {
    "actual_above_central_permutation_upper":actual>q975,
    "positive_lower_paired_story_bound":interval[0]>0,
    "uniform_unexplained_fraction_at_least_0_10":unexplained is not None and unexplained>=0.10,
}
uclasses,ucounts = np.unique(labels,return_counts=True)
usage = resource.getrusage(resource.RUSAGE_SELF)
receipt = {
    "protocol":"AMENDMENT-A3","input_pins":pins,
    "classification":"exploratory_retrospective_mature_checkpoint_pair_not_training",
    "archive_run_id":run.name,"verified_source_identity_sha256":source["sha256"],
    "archived_run_manifest_file_sha256":digest(run/"manifest.json"),
    "checkpoints":stats,"sample":{"split":"source_train","n":n,"exposure":"unknown",**sample_identity},
    "target_histogram":list(zip(uclasses.tolist(),ucounts.tolist(),strict=True)),
    "centered_ranks":ranks,"absolute_rank_tolerances":tolerances,"singular_values":spectra,
    "centered_ambient_dimension":V-1,"total_actual_gradient_squared_energy":total_energy,
    "self_capture":self_check,"subspace_overlap_squared_frobenius":overlap,
    "future_basis_drift_into_complement_squared_frobenius":drift,
    "centered_head_relative_frobenius_change":float(np.linalg.norm(heads[1]-heads[0])/np.linalg.norm(heads[0])),
    "captures":stats_by,"matched_drift_null":null,"actual_minus_matched_drift_null":excess,
    "actual_minus_uniform":delta,"uniform_unexplained_fraction":unexplained,
    "uniform_target_proxy_precision_guard":0.10,"gpu_m2_prioritization_gates":gates,
    "prioritize_gpu_m2":all(gates.values()),
    "paired_story_bootstrap":{"seed":18122,"draws":len(boot),"conditional_percentile_95_interval":interval,
        "draw_indices_sha256_le_int64":boot_sha},
    "permuted_targets":{"seed":18121,"draws":m,"count_less_or_equal_actual":le,
        "actual_empirical_cdf":cdf,"central_95_reference_interval":[q025,q975],"median_fraction":med,
        "monte_carlo_wilson_95_interval":[max(0,wc-wr),min(1,wc+wr)],
        "row_permutation_indices_sha256_le_int64":perm_sha,
        "numerator_total":pn.tolist(),"denominator_total":pd.tolist(),"capture_fraction":shuffles.tolist()},
    "stable_fallback_pairs":counts_by,"table_pairs":n*n,
    "max_probability_on_actual_targets":float(P[indices,labels].max()),
    "arithmetic_checks":checks,
    "runtime":{"backend":"cpu","forward_dtype":"float32","geometry_dtype":"float64",
        "torch":str(torch.__version__),"numpy":np.__version__,"python":sys.version.split()[0]},
    "cost":{"a1_a2_seconds_including_preflight":a2["cost"]["combined_wall_seconds_including_preflight"],
        "a3_seconds_inside_process":time.monotonic()-started,"a3_cpu_user_seconds":usage.ru_utime,
        "a3_cpu_sys_seconds":usage.ru_stime,"a3_peak_rss_kib":usage.ru_maxrss,
        "wall_limit_seconds":180,"address_space_limit_bytes":4*2**30,"allowed_cpus":len(os.sched_getaffinity(0)),
        "optimizer_updates":0,"gpu_used":False,"a3_forward_input_positions":n*32,"attempts":1},
}
print(json.dumps(receipt,sort_keys=True,separators=(",",":"),allow_nan=False))
"""
code = compile(prefix + "\n" + analysis, "<a3-historical-probe>", "exec")
if os.environ.get("A3_CODE_CHECK_ONLY") != "1":
    exec(code)
PY
A3_CODE_CHECK_ONLY=1 "$A1_PYTHON" a3-1.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$A1_ARCHIVE_SRC:$A1_CURRENT_SRC" \
CUDA_VISIBLE_DEVICES=-1 HIP_VISIBLE_DEVICES=-1 ROCR_VISIBLE_DEVICES=-1 \
TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 \
OPENBLAS_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4 MALLOC_ARENA_MAX=2 PYTHONHASHSEED=0 \
/usr/bin/time -v -o retry-cost.txt timeout --kill-after=10s 160s \
  taskset -c "$A1_CPU_LIST" prlimit --as=4294967296:4294967296 -- \
  "$A1_PYTHON" a3-1.py > retry-receipt.json 2> retry-stderr.txt
```

The first A3 attempt stopped after authentication and the first forward,
before SVD or outcomes; it used 9.91 seconds and 851,124 KiB RSS. The single
approved non-adaptive completion used 11.30 seconds and 849,348 KiB RSS.
A1, A2, the A2 preflight and both A3 attempts took 38.05 seconds total.
No GPU or optimizer updates. The mature scores exercised the FP64 stable
fallback on 26 row/target pairs; all pooled checks matched direct dense
calculation within 6e-19, and self-capture was 5.51e-30.
