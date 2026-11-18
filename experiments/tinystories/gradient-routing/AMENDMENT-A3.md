# Amendment A3: mature-checkpoint test of contextual temporal capture

Frozen 2026-11-18 15:19 UTC, after A2 and checkpoint integrity checks but
before any A3 model forward or outcome. This is one exploratory test of H4
on a later checkpoint pair from the same historical tied, 4,096-vocabulary
TinyStories lineage. It is not an additional training configuration or a test
of the published 32k recipe.

Use only archived run tinystories-50m-bf16-resume-2, steps 243968 and 244141,
chosen as the latest consecutive archived mature generations and the smallest
distance from the early 256-update gap among the available mature pairs.
Their gap is 173 updates (708,608 token positions). Manifest content SHA-256s
are 6fc016d116fbef56d73b89b81612e9f11bb54be3bb4ef288be56d1e6513db2a3
and c72d7d0283de2c6008f1b80d855bad6cb6ebc497f0094957a8982bd58a049110,
respectively. Verify the source, safetensors and run-owned data via the
archived native loader on CPU; also check the recorded byte hashes. Reuse the
exact first 128 distinct A1 train story contexts, targets, sample digests and
zero-based indexing, matching packed train prefixes as before. Step-specific
story exposure remains unknown; no development or final examples are scored.
Use the first mature checkpoint's actual probabilities, not initialization
or future predictions. Forward only that mature checkpoint, using the final
checkpoint for its head matrix alone.

## Estimands and decision

Use centered effective head matrices, compact FP64 SVD and the A1 threshold
sigma_max * max(V,d) * eps(float32). Require equal proper nonzero numerical
rank, orthonormal and zero-sum bases, self-capture no greater than 1e-20,
and a consistent complement drift calculation. Explicit self and later
capture, both denominators/numerators, ranks, spectra, overlap, drift,
centered principal-angle matched-drift null and excess are recorded.

Hold both bases fixed. Use the exact pooled residual energy definition in A2
for actual, uniform-predictor (same original targets), and 999 PCG64 target
slot permutations with seed 18121. The pairwise shape and permutation and
paired-bootstrap draw index SHA-256s must match A2. Use 1,999 paired
resampled-story draws with seed 18122 for actual minus uniform. Report
conditional 95% percentile interval, the central 95% permutation reference
interval, empirical actual percentile and its 95% Wilson Monte Carlo
interval. Secondary: substitute the same in-probe mean of all 128 mature
probability vectors for every context while preserving each true target.
This preserves the sampled mean predictive distribution but removes per-context
variation. It is not a fitted out-of-sample predictor or a decision endpoint.

A3 warrants prioritizing GPU M2 only if all gates hold:
1. Actual is strictly above the upper central 95% permutation reference limit.
2. The lower paired 95% story-resampling bound for actual minus uniform is positive.
3. Actual exceeds the centered drift null, and the uniform proxy leaves at
   least 10% of that positive excess unexplained:
   (actual - uniform) / (actual - drift_null) >= 0.10.
This is a local prioritization screen, not a proof of useful context learning
or a population p-value. If any gate fails, do not prioritize GPU M2 based on A3.
Permutation exchangeability is only a conditional diagnostic assumption.

## Numerics and resources

Precompute the 128-by-128 exact row-pair numerator and denominator table as in
A2, with a stable FP64 fallback for a candidate target with probability above
0.99, a near-zero denominator (<=1e-10), or negative rounding. Explicitly
set the target gradient coordinate to minus the sum of non-target probability
mass rather than subtracting near-one probabilities. Cross-check actual,
uniform, mean-predictor and first permutation against direct stable dense
residuals (absolute 1e-12 and relative 1e-12 for row components; verify all
pooled fractions to absolute 1e-12 and report errors). Permit exactly zero
row energy if a gradient is represented as zero, but refuse a zero pooled
denominator or failed provenance or numeric check. Report stable-fallback
counts and both reduction denominators.

One CPU-only attempt, at most four allowed CPUs, 4 GiB hard address-space
limit, 170-second soft and 180-second hard wall cap. A1 and A2 including
preflight used 16.84 seconds, so their combined maximum with A3 is 196.84
seconds. Do not run concurrently with active GPU qualification/training.
No state changes, source downloads or archive writes; hash weights, data
and state files read-only, with no optimizer state deserialization.
