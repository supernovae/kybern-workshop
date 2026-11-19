# Output-head controls on CPU

These checks use one matched synthetic fixture for the native model (width 16,
vocabulary 512, seed 7, seven scored targets) and a separate biased affine
fixture for numerical derivatives. They use CPU PyTorch and no TinyStories
data or GPU time. They establish implementation behavior, not learning gains.

## Results

- **C1:** Full-width routing and coefficient zero both reproduced dense logits,
  CE, trunk and output-weight gradients, and one clipped AdamW step and moments
  at FP64 tolerances. The native head has no bias; an independent biased
  affine gradcheck covered the hidden state, weight and bias in both no-ops.
- **C2:** On the half-width affine fixture, the explicit VJP agreed with a
  separately formed truncated map to at most `8.9e-16`; the full-head
  weight and bias gradients were exactly unchanged. Against ordinary hidden
  gradient norm 2.170006, raw projection gave 2.157214 (cosine 0.994105).
  RMS matching restored the norm to 2.170006 at the same cosine. The
  scalar-only control kept the raw norm and ordinary direction (cosine 1).
  The FP32 native chunked-head step produced identical forward loss
  (43.628082 summed over seven targets), but shared clip cap 1.0 changed the
  actual head update (difference norm `1.81e-5`) and first moment
  (`0.01045`). Exact preclip head gradients do not imply exact head updates.
- **C3:** The existing `model.output_head_rank` changes the *forward* map.
  Compare this path at the same rank as C2; do not claim it starts at the
  same logits as the full-width arms.
- **C4:** Both identity-initialized factorizations had exactly matched logits,
  CE and trunk gradient initially. Frozen identity matched both the dense
  effective-weight update and trunk update exactly, with and without shared
  clipping. Relative to dense, the trainable factor changed effective-weight
  update norm by +0.479% under SGD and +1.423% under AdamW, at cosine 0.999574
  and 0.996763, respectively. AdamW cap 1.0 also made its trunk update differ
  by `1.48e-6` in norm despite equal preclip trunk gradients. These measured
  differences do not justify an LR calibration by themselves.

[Machine-readable measurements](results/head-routing-cpu.json).

## Reproduce

From the Model Lab checkout containing the C1/C2/C4 change, with its
provisioned CPU environment active (or `UV_PROJECT_ENVIRONMENT` already
pointing to that environment):

```sh
set -o pipefail
OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 UV_OFFLINE=1 PYTHONPATH="$PWD/src" \
  uv run --locked --no-sync python -m pytest -n 0 -q -s \
  tests/test_output_head_gradient.py tests/test_full_width_output_head.py \
  | sed -n 's/^\.*C[24]_RECEIPT //p'
```

Use the same command without the final pipe to see the test verdicts. The
local run used Python 3.14.4 and PyTorch 2.14.1+cpu. No packages were installed.

## Before using C2 on TinyStories

The native C2 path is an explicit single-device CPU/FP32 reference.
It recomputes the current weight's thin right SVD in FP64 for each microbatch;
caching a stale map was deliberately avoided here. Scaling this implementation
as-is to a 32K-vocabulary ROCm run is not qualified. Before that contrast:

1. Implement and cost an economical deterministic right-basis refresh on ROCm.
   If it is cached, define refresh cadence and staleness, and preserve or
   reconstruct exact refresh state on resume.
2. Verify the C1 null and C2 weight/trunk derivative contracts with actual
   ROCm precision, accumulation, overflow and clipping behavior; compare
   approximate bases against the FP64 reference.
3. Log raw and routed hidden norms, cap hits, realized head and trunk update
   norms and clip behavior with bounded overhead. The CPU fixture receipts
   show the raw, RMS-matched and scalar-only cases; the native trainer does not
   record these VJP norms per microbatch.
4. Register matched clipping and LR budgets before training C0/C2/C3. The
   current C4 controls support fresh matched starts; a trained-checkpoint
   conversion would need a symmetric head-state reset or a verified exact
   optimizer state mapping.
