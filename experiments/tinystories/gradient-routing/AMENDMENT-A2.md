# Amendment A2: check whether M1 needs contextual pairing

Frozen 2026-11-18 14:51 UTC, after A1 and before any A2 outcome. One
exploratory falsification of the H4 interpretation, prompted by the A1 excess
over its matched-drift null. [Cho et al. (COLING 2025)](https://aclanthology.org/2025.coling-main.708/)
found early corpus-frequency information in output embeddings. That motivates
a control; it does not say what explains the excess in this archive.

## Fixed inputs and endpoints

Replay the same authenticated archived TinyStories run, steps 0 and 256, same
centered numerical bases, and exact 128 A1 source-training prefixes and targets.
Verify source, checkpoint, tokenizer, packed train, selection, context/target
IDs and A1 result before analyzing A2. Freeze each context's step-0 vector
p0 and both bases throughout. No development/final scores and no new training.
Exposure to each sampled story at step 256 remains unknown.

* Primary: pooled actual capture minus pooled uniform-predictor capture.
  Substitute uniform vocabulary probabilities 1/V for p0, retaining each
  original target and the exact observed class histogram. This frequency-only
  proxy still uses the true target rows and measured output drift.
* Secondary: percentile of the actual pooled fraction among 999 uniform random
  permutations of the 128 target slots (NumPy PCG64, seed 18121). Each
  re-pairs intact p0 rows with permuted targets and preserves the exact
  histogram. Percentile is count(permuted <= actual) / 999. Report median,
  central 95% linear-quantile reference interval and a 95% Wilson Monte Carlo
  interval for this percentile. The pairing exchangeability assumption is a
  diagnostic null, not a formal hypothesis test about training.
* Report a 95% percentile interval for paired actual-minus-uniform by
  resampling the 128 stories with replacement (1,999 PCG64 draws, seed
  18122, linear quantiles). Recompute both pooled ratios after each paired
  resample. This conditions on the observed ordered-prefix sample and the
  fixed checkpoints; it is not a population or between-run confidence claim.

For all conditions, form G_i = p_i - e_(y_i), R_i = G_i(I-Q0 Q0^T), and report
sum_i ||R_i Q256||^2 / sum_i ||R_i||^2. Use FP64 and precompute an exact
128-by-128 table of numerator and denominator row contributions for every
pairing of the 128 p0 rows and the 128 original target slots. Gather one entry
per row per permutation; do not construct 999 dense vocabulary residuals.
Cross-check actual, uniform, and the first seeded permutation against direct
FP64 dense residual sums (absolute tolerance 1e-12, relative 1e-12). Recover
A1's centered fraction to absolute 1e-12 and retain the A1 self-capture checks.
Refuse results on failed checks or provenance mismatch.

A near-zero or negative excess over the frequency-only proxy, or an ordinary
position in the permutation reference, weakens the interpretation that
the A1 excess needs real prediction/target pairing. If actual exceeds both
controls, that is evidence about this fixed retrospective pairing, not useful
context learning or better updates. At initialization any context-specific
signal is not learned by this run. These two controls do not identify a causal
mechanism or eliminate all vocabulary effects.

One attempt on CPU, no GPU. A1 used 10.28 wall seconds; A2 has a 210s soft limit
and a 220s hard limit so the combined maximum stays below 240s. At most four
allowed CPUs and a hard 4 GiB process address-space limit. Source archive
and run store are read-only. Report all actual resource use and failures.
