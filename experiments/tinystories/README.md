# TinyStories: 5M and 50M lifecycle study

[Workshop](../../README.md) · [Lifecycle and operations](lifecycle.md)

Two native recipes share source selection, tokenizer and prepared data, with
approximately 100M and 1B supervised training-token exposure. Use them to train,
checkpoint, resume, evaluate and check operational portability. The included
runtime is an example PyTorch/ROCm FP32 configuration; select a supported backend
and bind local paths for your system.

**Validation status:** native schema validation, instantiated parameter counts,
training results, preparation reuse and remote/Colab handoffs are not yet verified
for these recipes. The [4.46M baseline](../../examples/tinystories-useful/README.md)
has separate configurations and results.

## Definitions

| Setting | 5M tier | 50M tier |
| --- | --- | --- |
| Native declaration | [run-5m.json](run-5m.json) | [run-50m.json](run-50m.json) |
| Dense tied-embedding decoder | 5 layers, width 256, FFN 768, 4 heads | 9 layers, width 640, FFN 1,920, 10 heads |
| Calculated parameters | 5,311,232 | 50,556,800 |
| Update budget | 24,415 | 244,141 |
| Supervised target exposure cap | 100,003,840 | 1,000,001,536 |
| Exposure / parameter | ~18.83 | ~19.78 |
| AdamW peak / floor | 0.0006 / 0.00006 | 0.0006 / 0.00006 |
| Warmup updates | 256 | 2,048 |
| Initial calibration | First 256 updates of unchanged full horizon | First 256 updates of unchanged full horizon |

Shared: seed 42, train sequence 256, microbatch 4, accumulation 4 (4,096 nominal
supervised targets/update), max context 512, 4,096 vocabulary, dense attention,
SwiGLU/RMSNorm/RoPE, deterministic PyTorch, initial ROCm FP32. These choices make a
clear starting baseline, not a claim of optimal hyperparameters or hardware fit.
Parameter totals use `V*h + L*(4*h*h + 3*h*f + 2*h) + h` for the current tied,
bias-free architecture. Confirm the instantiated totals with native `inspect`;
these are calculated, not measured. Budgets are rounded up to whole updates.
Actual committed supervised targets from native records are authoritative; masked
targets or skipped updates must not be counted as exposure.

Shared preparation uses [source.json](source.json): pinned TinyStories revision,
500,000 retained train and 4,096 validation documents, exact-text dedup with
validation priority. This is a bounded selection, not a full-corpus claim.
[tokenizer.json](tokenizer.json) fits BPE only on the first 50,000 selected train
documents. Both models reuse its exact bytes and identical prepared data.
Preparation limits are 160M train and 2,097,152 validation tokens; these are caps,
not measured unique supply. If selected whole documents exceed the caps, fail and
revise preparation identity explicitly; do not silently truncate. Use the supported source bounds and measure residual Hub cache growth as
described in the lifecycle guide. Generate a source lock and preparation artifacts
in your external workspace.

After preparation record retained documents, unique selected/packed token-position
supply, usable supervised targets per pass `U`, boundary/tail losses and exclusions.
“Unique tokens” means positions in the selected corpus, not vocabulary types or
proof of semantic uniqueness. Exact-text dedup does not remove all near duplicates.
Report `E/U` as effective passes and `max(0, E-U)` as repeated-position exposure
when the loader cycles all usable blocks. If it samples differently, report actual
coverage and repeats instead. Never describe 1B exposure as 1B unique corpus tokens.
This study permits repetition; report the measured supply and effective passes.

## Runbook

The command reference is Lab
`b3a1630ec09dbddae36301b0acef4122623ed939`. Use the
[installed supported Lab environment](../../docs/native-workflow.md) (currently
Python 3.14), record the actual version pin, and validate again if it changes.

Set `STUDY` to this directory's absolute path, `WORK` to a fresh external persistent
root, and `TIER` to `5m` or `50m`. Set `RUN_ID`, `CHILD_ID` and subsequent IDs to
fresh meaningful native run names. Never reuse an existing run directory. The
following uses current path bindings; the lifecycle guide explains reuse and
transfer limitations. All generated files and binaries stay outside Git.

### 1. Bind once, prepare once

After checking actual available capacity, make `$WORK`. Copy `tokenizer.json` to
`$WORK/tokenizer.json` and edit only its path fields to absolute destinations:
`output_dir=$WORK/tokenizer`, `dataset.cache_dir=$WORK/data`,
`dataset.train_path=$WORK/snapshot/train.jsonl`,
`dataset.validation_path=$WORK/snapshot/validation.jsonl`, and
`dataset.source_manifest_path=$WORK/snapshot/manifest.json`. Substitute the real
root in the JSON strings; `$WORK` is not expanded inside config files. Current
`config derive` accepts run configs only; edit the copied tokenizer JSON directly.
Validate the edited tokenizer and derive **both** run declarations:

```sh
sparselab config validate "$WORK/tokenizer.json" --kind tokenizer --json

# Repeat this derivation for TIER=5m and TIER=50m.
sparselab config derive "$STUDY/run-$TIER.json" \
  --set "tokenizer.path=\"$WORK/tokenizer/tokenizer.json\"" \
  --set "dataset.cache_dir=\"$WORK/data\"" \
  --set "dataset.train_path=\"$WORK/snapshot/train.jsonl\"" \
  --set "dataset.validation_path=\"$WORK/snapshot/validation.jsonl\"" \
  --set "dataset.source_manifest_path=\"$WORK/snapshot/manifest.json\"" \
  --set "logging.root_dir=\"$WORK/runs\"" \
  --output "$WORK/run-$TIER.yaml" --json
sparselab config validate "$WORK/run-$TIER.yaml" --kind run --json
```

Run acquisition and preparation once, with real per-phase measurements and the
supported source bounds. Copy `source.json` outside Git and choose its
`resources.min_free_bytes` margin from actual available capacity and estimated
remaining growth before locking that local copy. The template value is zero;
there is no universal disk reserve. The snapshot work bound excludes Hub caches,
so measure residual cache growth separately. Unknown peaks call for observing the
initial real preparation segment.
Preserve incomplete attempts and stop if actual capacity is threatened.

```sh
sparselab data lock "$WORK/source.json" --output "$WORK/source.lock.json" --json
sparselab data snapshot "$WORK/source.lock.json" --output "$WORK/snapshot" --json
sparselab tokenizer train "$WORK/tokenizer.json"
sparselab tokenizer verify "$WORK/run-5m.yaml" --json
sparselab data prepare "$WORK/run-5m.yaml"
```

Set `PREPARED` to the actual prepared-array directory reported by `data prepare`
(not a guessed path or a staged bundle), then record coverage for each tier:

```sh
sparselab data coverage --prepared-root "$PREPARED" --config "$WORK/run-$TIER.yaml" --json
sparselab inspect "$WORK/run-$TIER.yaml" --json
```

A repeated same-input preparation request must reuse completed artifacts. Changing
model width/depth must not tokenize again. If native identity/binding prevents
this, preserve the diagnostic and inspect the reported identity mismatch before
repeating expensive preparation.

### 2. Publish inputs, stage and measure each real model

Publish a tier-specific input bundle for its full-config binding. Publication or
staging may currently copy assets; measure and admit that space explicitly. A
single underlying prepared-data identity is required, not zero-copy assumed by fiat.
Do not give the 5M sealed stage to the 50M config and call it verified reuse.

```sh
sparselab data prepared-inputs publish "$WORK/run-$TIER.yaml" --output "$WORK/prepared-$TIER"
sparselab data prepared-inputs verify "$WORK/run-$TIER.yaml" "$WORK/prepared-$TIER"
sparselab stage "$WORK/run-$TIER.yaml" --through warmup \
  --prepared-inputs "$WORK/prepared-$TIER" --cold-verify --output "$WORK/stages-$TIER"
sparselab train "$WORK/run-$TIER.yaml" --backend rocm --runs-dir "$WORK/runs" \
  --run-id "$RUN_ID" --stage-bundle "$WORK/stages-$TIER" --stop-after-step 256
```

Staging performs device work; select the intended hardware and runtime first.
Select a provisioned runtime using the documented `stage --runtime` or
`--runtime-profile` where needed; no existing runtime ID is assumed. Inspect the
resolved runtime before training. Record warmup separately; staging updates do not
count toward the tier's training exposure. Keep the full training horizon during
calibration so the verified generation can resume it. Capture throughput dispersion,
RSS/VRAM, I/O, preparation reuse, checkpoint latency/size and forecast vs observed
costs as defined in the lifecycle guide. If there is an OOM, do not silently shrink the
batch: preserve failure evidence and declare any revised settings as a new run.

### 3. Checkpoint, interrupt, resume and finish

Inspect the emitted pointer, then set `GENERATION` to its actual immutable generation
path. Use the reported generation rather than an inferred filename.

```sh
sparselab checkpoint inspect "$WORK/runs/$RUN_ID/checkpoints/latest.json" --json
sparselab checkpoint inspect "$GENERATION" --json
sparselab checkpoint verify "$GENERATION" --json
sparselab report "$RUN_ID" --kind run --runs-dir "$WORK/runs" --json
sparselab train "$WORK/run-$TIER.yaml" --backend rocm --runs-dir "$WORK/runs" \
  --run-id "$CHILD_ID" --resume "$GENERATION"
```

During the child run, once at least one new periodic generation is verified, issue
one normal Ctrl-C/SIGTERM to that process, wait for orderly exit, and preserve its
status/log. Inspect/verify its last durable generation, choose a fresh child ID and
repeat `train --resume` unchanged to completion. Do not kill during checkpoint
publication, delete a run, modify the budget or restart at zero. If recovery is
needed, use documented `train --recover RUN_DIR` with a fresh ID and record the
selected generation; explicit corrupt `--resume` must refuse. Keep cumulative
committed targets across lineage, without adding parent counters twice. Complete
5M before full 50M, and calibrate 50M independently.

Set `FINAL_RUN_ID` to the finished child, `CHECKPOINT` to its immutable generation
basename, and `GENERATION` to that actual path:

```sh
sparselab checkpoint verify "$GENERATION" --json
sparselab eval "$FINAL_RUN_ID" --runs-dir "$WORK/runs" --checkpoint "$CHECKPOINT" --backend rocm
sparselab report "$FINAL_RUN_ID" --kind run --runs-dir "$WORK/runs" --json
sparselab generate "$FINAL_RUN_ID" --runs-dir "$WORK/runs" --checkpoint "$CHECKPOINT" \
  --backend rocm --prompt "$PREFIX" --max-new-tokens 192 \
  --temperature 0.7 --top-k 40 --seed 42 --strict-context --show-prompt --json
```

For `PREFIX`, use each of the 12 [prompt-panel entries](../../examples/tinystories-useful/prompts.txt)
with both sampled settings above and greedy (`--temperature 0 --top-k 0`). Preserve
all 24 outputs per tier, including poor or incomplete ones. This is a fixed
qualitative panel, not a newly train-disjoint benchmark. Report repetition,
character consistency and endings with the baseline rubric and its limitations;
no story-quality improvement is promised or required to pass lifecycle acceptance.

### 4. Transfer to remote and Colab

**End-to-end transfer is unvalidated for these recipes.** Recipe export alone
transfers declarations, not all prepared inputs and full-state checkpoint
dependencies. The [lifecycle guide](lifecycle.md#checkpoint-recovery-and-transfer)
describes completeness and receiving-system verification requirements. A validated
public command sequence for this handoff is not yet provided.

For each tier on each target, derive a separately named 320-update handoff config
with `training.max_steps=320`, `training.max_tokens=1310720` and
`optimizer.warmup_steps=16`, retaining the full tier model, tokenizer, data and
batch. Bind target absolute paths and explicit supported backend with `config derive`.
Stage on actual hardware, train through 256, checkpoint/verify, interrupt/resume
there, and finish 320 updates. These deliberately smaller, separately scheduled
runs are operational acceptance, not scientific completion; they do not replace
either full-budget tier. For a cross-backend
checkpoint warm-start use native `train --promote GENERATION` with the compatible
model and tokenizer, then ordinary same-backend `--resume` after interruption.
Record original and new exposure separately. For same-backend full-state transfer,
use an interrupted full-budget generation with unchanged config/budget and verify
compatibility; the separate 320-step config is **not** a valid strict-resume target.
A changed device may still require explicit best-effort runtime-drift handling.

## Acceptance and evidence

All acceptance results are **unverified** for these recipes. Record actual results
in a compact `results/` record after execution; keep data and checkpoint binaries
outside Git.

| Gate | Required evidence |
| --- | --- |
| Shared preparation | Real source lock/content inventory, train-only tokenizer, coverage `U`, tails/exclusions, enforced caps, peak costs; repeat requests and both models reuse without refitting/repacking |
| 5M completion | Native actual parameter count; 100,003,840 committed targets / 24,415 updates unless counters expose a discrepancy; verified final generation, held-out finite loss and all outputs |
| 50M completion | Same, for 1,000,001,536 targets / 244,141 updates; independent measured calibration and fit |
| Recovery (both) | Ordered stop and signal interruption; parent/child identities, counters/cursor/state restored, last durable point and observed lost work; no duplicated target accounting |
| Handoffs (both tiers × remote/Colab) | Data identity retained, root relocation, partial/corrupt upload refusal, actual hardware staging, 256+64 update segment completed, verified persistent export and receiver checkpoint load/eval |
| Cheap inspection | Metadata listing does not read/hash corpus payload; cold verification is explicit and measured |
| Performance | Serial-stage and CPU/GPU/I/O audit; measured bounded-concurrency comparisons where useful; correctness/reuse/recovery preserved; material avoidable bottlenecks resolved and end-to-end costs remeasured before readiness |
| Predictable costs | Forecast vs actual phase times/bytes/peaks, reforecast explanations, cache/temporary/durable separation, no hidden repeated preparation |

Scientific quality and operational acceptance are separate. Finite loss and a
completed run do not establish a useful model; record initial/final held-out loss
on the same frozen selection and poor outputs without changing the criteria.
Preserve failures and missing measurements. Operational acceptance requires
the actual handoff commands and receiver-side verification. Strict trajectory equivalence is not claimed from matching
step counters; any such claim needs matching native full-state observations and
continued-update comparisons on the same supported deterministic runtime.
