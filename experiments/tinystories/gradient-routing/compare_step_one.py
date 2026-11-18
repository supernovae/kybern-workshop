"""Offline CPU reading of four explicit, verified native step-0/1 generations."""

import argparse
import hashlib
import json
import math
import re
import sqlite3
from pathlib import Path

import torch

from klab.canonical import canonical_digest, canonical_json
from klab.config.models import RunConfig
from klab.training.checkpoints import CheckpointManager
from klab.training.manifest import read_manifest

CHUNK = 65_536
HEAD_A = "output.weight"
HEAD_B = "output_down.weight"
GENERATION = re.compile(r"step_(\d{8})_gen_\d{6}\Z")


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def open_generation(path, step):
    # Never follow moving latest/best pointers or inspect a later generation.
    path = path.absolute()
    m = GENERATION.fullmatch(path.name)
    require(
        m and int(m[1]) == step and path.parent.name == "checkpoints"
        and path.is_dir() and path.resolve() == path,
        f"expected one explicit, unsymlinked step-{step} generation",
    )
    run = path.parent.parent
    manifest = read_manifest(run / "manifest.json")
    digest = canonical_digest(manifest)
    snap = CheckpointManager(run, manifest_sha256=digest).load(path)
    require(snap.step == step and snap.run_id == run.name and snap.engine == "pytorch",
            "native checkpoint does not match the declared PyTorch generation")
    require(snap.manifest_sha256 == digest, "checkpoint differs from bound manifest")
    return run, manifest, snap


def digest_named(state, names):
    digest = hashlib.sha256()
    for name in sorted(names):
        x = state[name]
        require(x.is_contiguous(), "noncontiguous native tensor")
        digest.update(canonical_json([name, list(x.shape), str(x.dtype)]))
        for tile in x.view(-1).split(CHUNK):
            digest.update(memoryview(tile.view(torch.uint8).numpy()))
    return digest.hexdigest()


def equal_tree(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, torch.Tensor):
        return a.dtype == b.dtype and torch.equal(a, b)
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(equal_tree(a[k], b[k]) for k in a)
    if isinstance(a, (tuple, list)):
        return len(a) == len(b) and all(equal_tree(v, w) for v, w in zip(a, b))
    return a == b


def compare_blocks(pairs):
    c0, c4, diff, dot, max_abs, elements = 0., 0., 0., 0., 0., 0
    for a, b in pairs:
        require(a.shape == b.shape, "comparison block shapes differ")
        x, y = a.reshape(-1).double(), b.reshape(-1).double()
        if x.numel() == 0:
            continue
        d = y - x
        c0 += float(torch.dot(x, x))
        c4 += float(torch.dot(y, y))
        diff += float(torch.dot(d, d))
        dot += float(torch.dot(x, y))
        max_abs = max(max_abs, float(d.abs().max()))
        elements += x.numel()
    require(all(map(math.isfinite, (c0, c4, diff, dot, max_abs))), "nonfinite tensor statistic")
    a, b = math.sqrt(c0), math.sqrt(c4)
    return {
        "elements": elements, "c0_norm": a, "c4_norm": b,
        "c4_to_c0_norm_ratio": b / a if a else None,
        "difference_norm": math.sqrt(diff), "max_abs_difference": max_abs,
        "cosine": max(-1., min(1., dot / (a * b))) if a and b else None,
    }


def update_blocks(a0, a1, b0, b1, names):
    for name in sorted(names):
        q = [state[name] for state in (a0, a1, b0, b1)]
        require(all(value.shape == q[0].shape and value.is_contiguous() for value in q),
                "common update tensor shapes/layout differ")
        for x0, x1, y0, y1 in zip(*(v.view(-1).split(CHUNK) for v in q), strict=True):
            yield x1.double() - x0.double(), y1.double() - y0.double()


def effective_blocks(a0, a1, b0, b1):
    B0, B1 = b0[HEAD_B].double(), b1[HEAD_B].double()
    v, d = a0[HEAD_A].shape
    require(a1[HEAD_A].shape == b0[HEAD_A].shape == b1[HEAD_A].shape == (v,d)
            and B0.shape == B1.shape == (d,d), "unexpected full-width effective head")
    rows = max(1, CHUNK // d)
    for lo in range(0, v, rows):
        sl = slice(lo, lo + rows)
        yield (
            a1[HEAD_A][sl].double() - a0[HEAD_A][sl].double(),
            b1[HEAD_A][sl].double() @ B1 - b0[HEAD_A][sl].double() @ B0,
        )


def first_moments(snap):
    names = snap.optimizer_parameter_names
    require(isinstance(names, dict), "native AdamW named parameter map unavailable")
    states = snap.optimizer["state"]
    result = {}
    for group in snap.optimizer["param_groups"]:
        beta1 = group["betas"][0]
        require(0 <= beta1 < 1, "invalid beta1")
        for i in group["params"]:
            if i not in states:
                continue
            step = states[i]["step"]
            moment = states[i]["exp_avg"]
            require(float(step) == 1 and moment.dtype == torch.float32 and moment.is_contiguous(),
                    "first-step moment interpretation requires ordinary FP32 AdamW slots")
            result[names[i]] = (moment, beta1)
    return result


def moment_blocks(a, b, names, *, normalized):
    for name in sorted(names):
        x, xb = a[name]
        y, yb = b[name]
        require(x.shape == y.shape, "common moment tensor shapes differ")
        for v, w in zip(x.view(-1).split(CHUNK), y.view(-1).split(CHUNK), strict=True):
            yield v.double() / (1-xb) if normalized else v, w.double() / (1-yb) if normalized else w


def scalar_norm(tensor):
    return math.sqrt(sum(float(tile.double().square().sum()) for tile in tensor.view(-1).split(CHUNK)))


def native_grad_norm(run, run_id, tokens):
    # Read only the specific step-1 non-loss metric, after terminal ownership.
    # Immutable mode cannot create WAL sidecars. A present WAL means stop here,
    # not an excuse to report an absent row as zero.
    path = run.parent / "experiments.sqlite3"
    wal = Path(str(path) + "-wal")
    if not path.is_file() or (wal.exists() and wal.stat().st_size > 0):
        return None
    with sqlite3.connect(path.as_uri() + "?mode=ro&immutable=1", uri=True) as con:
        rows = con.execute(
            "SELECT value,tokens_seen FROM metrics WHERE run_id=? AND step=1 AND name=?",
            (run_id, "optimizer/grad_norm"),
        ).fetchall()
    if not rows:
        return None
    require(len(rows) == 1 and rows[0][1] == tokens and math.isfinite(rows[0][0]),
            "native step-1 gradient norm has unexpected counters")
    return float(rows[0][0])


def norm_receipt(moments, native, cap):
    sum_sq = sum((scalar_norm(t)/(1-beta))**2 for t, beta in moments.values())
    recovered = math.sqrt(sum_sq)
    return {
        "native_global_preclip_norm": native,
        "declared_global_clip_cap": cap,
        "moment_implied_postclip_norm": recovered,
        "postclip_norm_over_native_preclip": recovered/native if native else None,
        "approximately_expected_postclip_norm": min(native, cap) if native is not None else None,
        "tensors_with_first_moments": len(moments),
    }


def compare(args):
    arun, aman, a0 = open_generation(args.c0_initial, 0)
    arun1, _, a1 = open_generation(args.c0_step_one, 1)
    brun, bman, b0 = open_generation(args.c4_initial, 0)
    brun1, _, b1 = open_generation(args.c4_step_one, 1)
    require(arun == arun1 and brun == brun1 and arun != brun, "one run per arm required")
    cfg0, cfg4 = [RunConfig.model_validate(s.config) for s in (a0, b0)]
    require(a0.config == a1.config and b0.config == b1.config, "config changed across a step")
    require(a0.source_identity_sha256 == a1.source_identity_sha256 == b0.source_identity_sha256
            == b1.source_identity_sha256, "paired checkpoint source identities differ")
    require(all(s.parent_checkpoint_sha256 is None for s in (a0,a1,b0,b1)),
            "first-step diagnostic requires scratch runs rather than promotions/resumes")
    require(all(getattr(cfg0,f) == getattr(cfg4,f) for f in
                ("seed","training","optimizer","runtime","tokenizer","dataset","attention","evaluation")),
            "paired scientific, runtime, or input declarations differ")
    base_model, factor_model = cfg0.model.model_dump(), cfg4.model.model_dump()
    require(not cfg0.model.tie_embeddings and not cfg4.model.tie_embeddings
            and factor_model.pop("output_head_parameterization",None) == "identity_trainable"
            and factor_model == base_model, "requires ordinary C0 and identity-trainable C4 only")
    require(cfg0.optimizer.name == "adamw" and cfg0.optimizer.state_dtype == "fp32"
            and cfg0.runtime.gradient_dtype == "fp32"
            and not cfg0.runtime.parallel.sharded and not cfg0.runtime.secondary_device_indices
            and cfg0.runtime.precision in {"bf16","fp32"} and a1.scaler is None and b1.scaler is None,
            "moment interpretation needs ordinary single-device AdamW FP32 slots")
    require(a0.tokens_seen == b0.tokens_seen == 0 and a0.cursor == b0.cursor == (0,0)
            and a1.tokens_seen == b1.tokens_seen > 0 and a1.cursor == b1.cursor,
            "paired native token/cursor counters differ")
    require(not a0.optimizer["state"] and not b0.optimizer["state"], "step-0 moment state is nonempty")
    require(all(s.schedule["completed_updates"] == s.step for s in (a0,a1,b0,b1)),
            "native schedule counters differ")
    def packed_artifacts(m):
        return {x["relative_path"]: x["sha256"] for x in m["artifacts"]
                if x["relative_path"].startswith("data/") or x["relative_path"] == "tokenizer.json"}
    ad, bd = packed_artifacts(aman), packed_artifacts(bman)
    require({"data/train.npy","data/validation.npy","tokenizer.json"} <= set(ad) and ad == bd,
            "paired tokenizer/prepared artifact checksums differ")
    require(a0.model.keys() == a1.model.keys() and b0.model.keys() == b1.model.keys()
            and set(b0.model) == set(a0.model) | {HEAD_B} and HEAD_A in a0.model and HEAD_B not in a0.model,
            "unexpected parameter inventory for the matched-head comparison")
    backbone = set(a0.model)-{HEAD_A}
    a_back, b_back = [digest_named(s.model, backbone) for s in (a0,b0)]
    a_head, b_head = [digest_named(s.model, {HEAD_A}) for s in (a0,b0)]
    matrix = b0.model[HEAD_B]
    identity = bool(matrix.ndim == 2 and matrix.shape[0] == matrix.shape[1]
                    and torch.count_nonzero(matrix) == matrix.shape[0] and (matrix.diag()==1).all())
    require(a_back == b_back and a_head == b_head and identity,
            "paired initialization is not exactly shared or C4 B is not identity")
    m0, m4 = first_moments(a1), first_moments(b1)
    require(set(m4) == set(m0)|{HEAD_B} and HEAD_A in m0 and set(m0) <= set(a0.model),
            "native moments could not be paired over common updated parameters")
    native0, native4 = native_grad_norm(arun,a1.run_id,a1.tokens_seen), native_grad_norm(brun,b1.run_id,b1.tokens_seen)
    return {
        "classification": "native step-0/1 mechanism receipt; no efficacy scores read from metrics",
        "checkpoints": {
            "c0_initial": a0.checkpoint_sha256, "c0_step_one":a1.checkpoint_sha256,
            "c4_initial": b0.checkpoint_sha256, "c4_step_one":b1.checkpoint_sha256,
        },
        "config_sha256": {"c0":a0.config_sha256,"c4":b0.config_sha256},
        "source_identity_sha256": a0.source_identity_sha256,
        "initial": {
            "trunk_tensor_count":len(backbone), "trunk_raw_sha256_shared":a_back,
            "head_a_and_dense_w_raw_sha256_shared":a_head,
            "effective_w_exact": True, "c4_b_exact_identity": identity,
            "rng_state_exact": equal_tree(a0.rng,b0.rng),
            "native_initial_validation_equal": (
                a0.validation_loss == b0.validation_loss
                if a0.validation_loss is not None and b0.validation_loss is not None else None
            ),
        },
        "valid_targets_step_one": a1.tokens_seen,
        "cursor_step_one_equal": True,
        "prepared_artifacts_match": True,
        "prepared_train_sha256": ad["data/train.npy"],
        "realized_step_one": {
            "effective_head": compare_blocks(effective_blocks(a0.model,a1.model,b0.model,b1.model)),
            "trunk": compare_blocks(update_blocks(a0.model,a1.model,b0.model,b1.model,backbone)),
            "c4_b_update_frobenius_norm": math.sqrt(sum(
                float((a.double()-b.double()).square().sum())
                for a,b in zip(b1.model[HEAD_B].view(-1).split(CHUNK),matrix.view(-1).split(CHUNK),strict=True)
            )),
        },
        "optimizer_first_moment_step_one": {
            "raw_exp_avg_common_trunk": compare_blocks(moment_blocks(m0,m4,backbone & set(m0),normalized=False)),
            "raw_exp_avg_dense_w_vs_a": compare_blocks(moment_blocks(m0,m4,{HEAD_A},normalized=False)),
            "c4_b_raw_exp_avg_norm": scalar_norm(m4[HEAD_B][0]),
            "c0_clipping_context": norm_receipt(m0,native0,cfg0.training.grad_clip_norm),
            "c4_clipping_context": norm_receipt(m4,native4,cfg4.training.grad_clip_norm),
        },
        "limitations": [
            "Checkpoint-derived moments are not raw BF16 gradients; m1/(1-beta1) approximates the postclip optimizer input only.",
            "Norm ratios are global; equal initial model tensors do not directly verify native logits or derivatives.",
            "The native grad norm is a recorded global preclip scalar, not a parameter-wise gradient or magnitude.",
            "No post-step-1 checkpoint, held-out metric rows, or loss values are exported.",
        ],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("c0-initial","c0-step-one","c4-initial","c4-step-one"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--cpu-threads",type=int,default=2,choices=(1,2,3,4))
    args = p.parse_args()
    torch.set_num_threads(args.cpu_threads)
    with torch.inference_mode():
        print(json.dumps(compare(args),indent=2,sort_keys=True,allow_nan=False))


if __name__ == "__main__":
    main()
