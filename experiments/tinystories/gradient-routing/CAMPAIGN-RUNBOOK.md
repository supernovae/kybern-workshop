# Conditional 32k ROCm campaign

**This was the prospective runbook. The bounded scope was subsequently admitted; [live execution status](README.md) distinguishes completed and pending gates.** The [campaign proposal](CAMPAIGN-PROPOSAL.json)
sets the caps and admission gates. Schema validation neither verifies assets
nor reserves the device. Do not launch without the admitted native physical
claim, UTC deadline, watchdog, and verified input and ROCm gates below.

## Declarations and pairing

Use [campaign-32k-rocm.yaml](campaign-32k-rocm.yaml) for ordinary C0. Use the
existing [reference-c4.yaml](reference-c4.yaml) for C4: the only arm-specific
setting is `model.output_head_parameterization: identity_trainable`.
C4 starts at `A=W0, B=I` with both factors trainable; frozen identity is a
qualification control, never another efficacy arm. Compared with
[the original one-pass arm](../lm-head-bottleneck/arm.yaml), the model, untied
32,768-token vocabulary, source and packing declarations, context 512, batch
32 × 8, AdamW, LR schedule, clipping and the 2,961-step/388,104,192-target
scientific horizon are preserved. The checked-in seed 1 is the published
reference; bind each study seed explicitly as listed below.

Both arms use the same **single-device AMD BF16 eager SDPA** setting and
2,048-token chunked output loss. The original XPU-only compiled output loss
and block compilation are off. AMD must pass the 20-GiB native planning
ceiling and separately enforced measured-cap gates (no Intel observe waiver). Chunking and the eval
cadence are disclosed runtime/measurement adaptations; neither asserts AMD/XPU
arithmetic parity or reduces the batch. No mixed backend, tuning variants or
silent memory fallback.

Deploy the declaration inside `gradient-routing/` beneath the campaign data
workspace, adjacent to `snapshot/`, `tokenizer-32k/` and `data/`. Verify
the source revision and cleaned split inventory, tokenizer bytes and origin,
and prepared train/dev content digests against the proposal and any original
run identities. If only exact-settings reconstruction can be authenticated,
label it that way, not byte-identical replication. Require the already
verified prepared cache; missing assets stop the campaign arm rather than
causing on-device data preparation.

## Phases and equal evaluation

| Phase | Seed and arms | Absolute stop | Native development CE ticks |
| --- | --- | ---: | --- |
| Cost/shape calibration | 13, C0 and C4 | 40 (5,242,880 nominal targets/arm) | 0, 40; charge both. Discard updates 1–8 from steady-state timing, then four blocks of 8. All 40 are before warmup ends. |
| Full published-horizon comparison, provisional | C0 twice at 13 for jitter; C0/C4 at 17 for screen; fresh C0/C4 pairs at 101, 211, 307 | 2,961 (388,104,192/arm) | 0, 370, 740, 1110, 1480, 1850, 2220, 2590, 2960, 2961. Charge **10** evals; native fixed cadence also fires at 2960. Primary milestone ticks are integer floors of T/8, T/2, and terminal T. |
| **512-update post-warmup pilot**, only if explicitly accepted | Same phase seeds and pairings; separate named run IDs | 512 (67,108,864/arm) | 0, 256, 512. T/8=64 is inside warmup, so it is not scored. Derive `evaluation.every_steps: 256` identically for all pilot runs. |

All ticks use the same 64 batches of 32 rows × 512 positions on the verified
development split (up to 1,048,576 valid targets), with exact masks, target
counts and NLL numerator recorded. Preserve the 2,000-story BPB policy for an
explicitly charged standalone score. Development is not an untouched test.
Compare paired arms at matched **committed** labels, and separately at a
prespecified common measured-time cap using the last eligible tick at or
before it. Record its actual tick, labels and charged time; censor a missing
eligible score. Do not interpolate or compare unmatched terminal times as a
time-to-quality result.

For each arm retain the full scientific schedule, even when selecting stop 40
or 512; never derive `training.max_steps` or `max_tokens`. Issue explicit
absolute `--stop-after-step`, `--require-prepared`, exact `--runtime`,
`--resource-envelope` and a unique run ID only through the admitted runner.
Those flags do not by themselves enforce the overall device claim and deadline.
Use equal `keep_periodic: false`, `save_on_new_best: false`, and routine
1,000-step checkpoint cadence with native initial/final saves. The manager
may additionally protect latest, previous and best state; budget transient and
protected generations. Do not presume old checkpoint bytes can be deleted.

During calibration use the proposal's 2 × 20 minute arms plus 5 minutes
cleanup, 20 GiB device/16 GiB process-tree RAM/32 GiB new files and its update
caps. Cost independently charged startup, update blocks, validation, saves
and probes; each arm's quote is the rounded 1.25× padded sum in the proposal.
Before a screen, reserve the two baseline-only repeats, all six fresh
confirmation arms, and cleanup/recovery inside the 18-hour claim, 2-hour
per-efficacy-arm, 30-hour overall, 64-GiB disk and invocation/step caps. Stamp
real UTC limits. Seal the calibration treatment outcome while setting the
practical effect using C0 repeats and intended use. If the full plan cannot
fit, use only the explicitly accepted, named 512-update pilot and recompute
the gate; otherwise report the shortfall and stop. Do not use the 4k/tied
qualifier or Intel timings as AMD 32k estimates.

## Validation and diagnostic gates

1. Validate the base and per-phase/seed typed variants. For example, in a
   deployed workspace, derive a **declaration only** outside Git:
   ```sh
   klab config validate campaign-32k-rocm.yaml --kind run
   klab config derive campaign-32k-rocm.yaml --set seed=17 \
     --set evaluation.every_steps=256 --output "$PLAN/c0-pilot-s17.yaml"
   klab config derive "$PLAN/c0-pilot-s17.yaml" \
     --set model.output_head_parameterization='"identity_trainable"' \
     --output "$PLAN/c4-pilot-s17.yaml"
   ```
   The second derive applies the single setting declared by the C4 delta;
   check its native sidecar. Offline canonical validation and shape inventory
   do not open data, initialize ROCm, or qualify execution.
2. Use the native calibration runs themselves for the device measurements below.
3. Legacy inline gradient observation stays off for both arms: the chunked
   training evaluator rejects full-logits observers. An optional sparse
   standalone checkpoint projection on the final matched screen pair only
   (first 2,048 valid dev rows per arm, same order) must be independently
   budgeted and use the effective head, not the last factor. The current
   `klab eval --gradient-projection-targets 2048` path bounds the projection
   sample, **not** its whole development scoring pass or 2,000-story BPB
   work; it can materialize full logits even for a chunked training run.
   Precheck memory and charge the whole diagnostic, or mark it unmeasured.
   Do not add it inside timed training updates or infer raw gradient retention
   from per-update scalar loss. Preserve native final checkpoints and receipts
   according to [retention policy](RETENTION.md).

**Operational guard before any 32k GPU run (16:15 UTC):** All arms now explicitly set the native PyTorch allocator ceiling to 0.72 of device memory, in addition to the 20 GiB planner/whole-card cap and host monitor. The original declaration had only the planner budget; the default 0.90 allocator fraction alone would allow more than 20 GiB on this device. This amendment tightens every arm equally. It does not alter model, token, seed, precision, loss, LR, evaluation, or stopping schedule. Native allocator limits do not cover all device allocations or other users, so the whole-card preflight and live guard remain mandatory. No GPU run had started.

### Actual device measurements

**16:22 UTC, before the first 32k model run.** Rather than add a separate
parity launcher, use the ordinary C0 and C4 calibration runs. For both, record
each update and request the native step-1 checkpoint. Compare initial tensors,
initial validation CE, and the first realized effective-head and trunk update
where native artifacts allow. Report what was directly recorded, what can
be derived from optimizer state, and what remains unmeasured. The frozen
identity raw-derivative comparison already has a CPU fixture; that does not
establish device-level raw tensor parity. No third model run and no new build
gate. This updates the execution method in the original numerical plan;
it does not change treatment, seeds, thresholds or either efficacy endpoint.
