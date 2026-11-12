# TinyStories: 5M and 50M lifecycle study

[Workshop](../../README.md) · [Lifecycle and operations](lifecycle.md)

These two recipes train a 5M and a 50M model on the same TinyStories data, with
about 100M and 1B supervised training targets respectively. Both share the source
selection, tokenizer and prepared data. Use them to practice training,
checkpointing, resuming, evaluating and moving a run to another machine. The
included runtime is an example PyTorch/ROCm FP32 setup; pick a supported backend
and set local paths for your own system.

## Versioned validation

At Workshop revision `e186e42194bd69f2fb68318a79c51c9bbcc4e7c7`, native
`config validate` passed for both run configs and the tokenizer config. The native
source loader accepted `source.json` (Lab has no public validator for source
configs). Public `inspect` passed shape checks. Building the models separately on
CPU in FP32 gave **5,311,232** and **50,556,800** parameters, matching the
calculations below.

These checks passed on Lab `1b9fed431f7257007e2bdb931de05f63b8c19109` and on the
workflow reference, `b3a1630ec09dbddae36301b0acef4122623ed939`, with the Workshop
configs unchanged. The reference-pin repeat used clean checkouts and the existing
PyTorch `2.13.0+rocm10.0.0` dependencies. These checks covered configs, shapes
and CPU parameter counts; they did not test GPU fit or run the workflow. On the
reference pin and Workshop revision, the metadata-only dataset lock finished in 3.381
seconds (exit 0) and passed native verification:
`ce604a08b892e74669d62bbff1d90d0b04c0b0e522f605963c7c4e22f50558d5`. It pins source
`f54c09fd23315a6f9c86f9dc80f725de7d8f9c64` in standard Parquet format and lists
five upstream files totaling 1,000,775,442 bytes; the lock step did not download
the stories themselves.

Later, the [local ROCm results](../../results/2026-10-31-tinystories-rocm/README.md)
record the full download, shared preparation and reuse, both GPU pilots, the full
5M budget with signal and resume checks, short 50M performance comparisons, and a
full 50M BF16 run with tested recovery. Both 24-output fixed-prompt panels are
kept, failures included. The [Intel context comparisons](context/README.md) and
the [learning-rate study](learning-rate/README.md) came after that and have their
own protocols and limits. Moving a run to a remote machine or Colab, and carrying
optimizer state across devices, are still untested. The baseline recipes have not
changed; the batch and precision variants are separate calibration configs. The
[4.46M baseline](../../examples/tinystories-useful/README.md) has its own configs
and results.

## Definitions

| Setting | 5M tier | 50M tier |
| --- | --- | --- |
| Native config | [run-5m.json](run-5m.json) | [run-50m.json](run-50m.json) |
| Dense tied-embedding decoder | 5 layers, width 256, FFN 768, 4 heads | 9 layers, width 640, FFN 1,920, 10 heads |
| Calculated / CPU-verified parameters | 5,311,232 | 50,556,800 |
| Update budget | 24,415 | 244,141 |
| Supervised target exposure cap | 100,003,840 | 1,000,001,536 |
| Exposure / parameter | ~18.83 | ~19.78 |
| AdamW peak / floor | 0.0006 / 0.00006 | 0.0006 / 0.00006 |
| Warmup updates | 256 | 2,048 |
| Initial calibration | First 256 updates of unchanged full horizon | First 256 updates of unchanged full horizon |

Both tiers share: seed 42, train sequence 256, microbatch 4, accumulation 4 (4,096
nominal supervised targets per update), max context 512, 4,096 vocabulary, dense
attention, SwiGLU/RMSNorm/RoPE, deterministic PyTorch, and ROCm FP32 to start.
These are a clear starting point; we have not tuned hyperparameters or hardware
fit. Parameter totals use `V*h + L*(4*h*h + 3*h*f + 2*h) + h` for the current
tied, bias-free architecture. Native `inspect` checks shapes without building the
model, so we built each model on CPU separately and confirmed these totals on both
Lab revisions, including the workflow reference pin. Budgets are rounded up to
whole updates. Count exposure from the committed supervised targets in the native
records; leave out masked targets and skipped updates.

Shared preparation uses [source.json](source.json): a pinned TinyStories revision,
500,000 training and 4,096 validation documents, and exact-text dedup that keeps
the validation copy. This is a subset of the corpus.
[tokenizer.json](tokenizer.json) fits BPE on the first 50,000 selected training
documents only. Both models use the same tokenizer bytes and the same prepared
data. Preparation caps are 160M training and 2,097,152 validation tokens; these are
upper limits, so measure the real supply. If the selected whole documents go over
a cap, let preparation fail and change the preparation settings on purpose, rather
than truncating. Use the supported source bounds and measure Hub cache growth as
the lifecycle guide describes. Create the source lock and prepared data in your
external workspace.

After preparation, record the retained documents, the unique selected and packed
token positions, usable supervised targets per pass `U`, boundary and tail losses,
and exclusions. "Unique tokens" here means positions in the selected corpus, not
vocabulary types. Exact-text dedup leaves near duplicates in place. If the loader
cycles through all usable blocks, report `E/U` as effective passes and
`max(0, E-U)` as repeated-position exposure. If it samples differently, report the
actual coverage and repeats. 1B exposure means 1B training targets, many of them
repeats, so never describe it as 1B unique tokens. Repetition is allowed in this
study; report the measured supply and effective passes.

## Runbook

Commands follow Lab `b3a1630ec09dbddae36301b0acef4122623ed939`. Use the
[installed Lab environment](../../docs/native-workflow.md) (currently Python
3.14), write down the exact version, and validate again if it changes.

Set `STUDY` to this directory's absolute path, `WORK` to a fresh persistent
directory outside the repo, and `TIER` to `5m` or `50m`. Give `RUN_ID`, `CHILD_ID`
and later IDs fresh, meaningful run names, and never reuse an existing run
directory. The steps below use the current path settings; the lifecycle guide
covers reuse and transfer limits. Keep all generated files and binaries out of
Git.

### 1. Bind once, prepare once

Check how much space you actually have, then create `$WORK`. Copy `tokenizer.json`
to `$WORK/tokenizer.json` and change only its path fields to absolute paths:
`output_dir=$WORK/tokenizer`, `dataset.cache_dir=$WORK/data`,
`dataset.train_path=$WORK/snapshot/train.jsonl`,
`dataset.validation_path=$WORK/snapshot/validation.jsonl`, and
`dataset.source_manifest_path=$WORK/snapshot/manifest.json`. Write the real
directory into the JSON strings, because config files do not expand `$WORK`.
`config derive` only accepts run configs today, so edit the copied tokenizer JSON
by hand. Validate the edited tokenizer and derive **both** run configs:

```sh
klab config validate "$WORK/tokenizer.json" --kind tokenizer --json

# Repeat this derivation for TIER=5m and TIER=50m.
klab config derive "$STUDY/run-$TIER.json" \
  --set "tokenizer.path=\"$WORK/tokenizer/tokenizer.json\"" \
  --set "dataset.cache_dir=\"$WORK/data\"" \
  --set "dataset.train_path=\"$WORK/snapshot/train.jsonl\"" \
  --set "dataset.validation_path=\"$WORK/snapshot/validation.jsonl\"" \
  --set "dataset.source_manifest_path=\"$WORK/snapshot/manifest.json\"" \
  --set "logging.root_dir=\"$WORK/runs\"" \
  --output "$WORK/run-$TIER.yaml" --json
klab config validate "$WORK/run-$TIER.yaml" --kind run --json
```

Run download and preparation once, measuring each phase and using the supported
source bounds. Copy `source.json` out of Git. Before you lock that local copy, set
its `resources.min_free_bytes` margin from the space you actually have and the
growth you still expect. The template uses zero because no single reserve suits
every disk. The snapshot work bound leaves out Hub caches, so measure cache growth
separately. If you don't know the peak, watch the first real stretch of
preparation. Keep incomplete attempts, and stop if you are about to run out of
space.

```sh
klab data lock "$WORK/source.json" --output "$WORK/source.lock.json" --json
klab data snapshot "$WORK/source.lock.json" --output "$WORK/snapshot" --json
klab tokenizer train "$WORK/tokenizer.json"
klab tokenizer verify "$WORK/run-5m.yaml" --json
klab data prepare "$WORK/run-5m.yaml"
```

Set `PREPARED` to the prepared-array directory that `data prepare` reports (use
the reported path, not a guess or a staged bundle), then record coverage for each
tier:

```sh
klab data coverage --prepared-root "$PREPARED" --config "$WORK/run-$TIER.yaml" --json
klab inspect "$WORK/run-$TIER.yaml" --json
```

Asking for the same preparation again should reuse the finished arrays, and
changing model width or depth should not tokenize again. If Lab refuses to reuse
them, keep the error and check which input it says changed before you rerun an
expensive preparation.

### 2. Publish inputs, stage and measure each real model

Publish an input bundle for each tier's full config. Publishing or staging may copy
data today, so measure that space and plan for it. Both tiers must use the same
underlying prepared data; check that rather than assuming nothing was copied. Each
tier needs its own stage bundle, so don't hand the 5M stage to the 50M config.

```sh
klab data prepared-inputs publish "$WORK/run-$TIER.yaml" --output "$WORK/prepared-$TIER"
klab data prepared-inputs verify "$WORK/run-$TIER.yaml" "$WORK/prepared-$TIER"
klab stage "$WORK/run-$TIER.yaml" --through warmup \
  --prepared-inputs "$WORK/prepared-$TIER" --cold-verify --output "$WORK/stages-$TIER"
klab train "$WORK/run-$TIER.yaml" --backend rocm --runs-dir "$WORK/runs" \
  --run-id "$RUN_ID" --stage-bundle "$WORK/stages-$TIER" --stop-after-step 256
```

Staging runs on the device, so choose your hardware and runtime first. Where
needed, pick an installed runtime with `stage --runtime` or `--runtime-profile`;
the recipe doesn't assume any runtime ID. Check the resolved runtime before
training. Record warmup on its own, because staging updates don't count toward the
tier's training exposure. Keep the full training horizon during calibration so you
can resume from the checkpoint it writes. Record throughput spread, RSS/VRAM, I/O,
preparation reuse, checkpoint time and size, and forecast versus actual costs, as
the lifecycle guide describes. If you hit an OOM, keep the failure output and
start any smaller-batch settings as a new run instead of quietly shrinking the
batch.

### 3. Checkpoint, interrupt, resume and finish

Inspect the pointer the run writes, then set `GENERATION` to the immutable
generation path it reports. Use that path rather than guessing a filename.

```sh
klab checkpoint inspect "$WORK/runs/$RUN_ID/checkpoints/latest.json" --json
klab checkpoint inspect "$GENERATION" --json
klab checkpoint verify "$GENERATION" --json
klab report "$RUN_ID" --kind run --runs-dir "$WORK/runs" --json
klab train "$WORK/run-$TIER.yaml" --backend rocm --runs-dir "$WORK/runs" \
  --run-id "$CHILD_ID" --resume "$GENERATION"
```

Once the child run has written and verified at least one new periodic checkpoint,
send that process one normal Ctrl-C/SIGTERM, wait for it to exit cleanly, and keep
its status and log. Inspect and verify its last saved generation, pick a fresh
child ID, and run the same `train --resume` again to completion. Don't kill the
process while it is writing a checkpoint, and don't delete a run, change the
budget or restart from zero. If you need recovery, use `train --recover RUN_DIR`
with a fresh ID and record which generation it picked; an explicit `--resume` of a
corrupt checkpoint should be refused. Keep a running total of committed targets
across the parent and children without counting the parent twice. Finish 5M before
the full 50M run, and calibrate 50M on its own.

Set `FINAL_RUN_ID` to the finished child, `CHECKPOINT` to its immutable generation
name, and `GENERATION` to its full path:

```sh
klab checkpoint verify "$GENERATION" --json
klab eval "$FINAL_RUN_ID" --runs-dir "$WORK/runs" --checkpoint "$CHECKPOINT" --backend rocm
klab report "$FINAL_RUN_ID" --kind run --runs-dir "$WORK/runs" --json
klab generate "$FINAL_RUN_ID" --runs-dir "$WORK/runs" --checkpoint "$CHECKPOINT" \
  --backend rocm --prompt "$PREFIX" --max-new-tokens 192 \
  --temperature 0.7 --top-k 40 --seed 42 --strict-context --show-prompt --json
```

For `PREFIX`, run each of the 12 [prompt-panel entries](../../examples/tinystories-useful/prompts.txt)
with the sampled settings above and with greedy decoding (`--temperature 0 --top-k 0`).
Keep all 24 outputs per tier, including poor or unfinished ones. The panel is a
fixed set of prompts for reading outputs side by side; the prompts were not
re-checked against the training data. Score repetition, character consistency and
endings with the baseline rubric. The lifecycle checks pass or fail on their own;
better stories are not required.

### 4. Transfer to remote and Colab

**Moving these runs to another machine end to end is still untested.** Recipe
export copies the configs, but not all prepared inputs or everything a full-state
checkpoint needs. The [lifecycle guide](lifecycle.md#checkpoint-recovery-and-transfer)
explains what to copy and what to check on the receiving machine. There is no
tested command sequence for this handoff yet.

For each tier on each target, derive a separately named 320-update handoff config
with `training.max_steps=320`, `training.max_tokens=1310720` and
`optimizer.warmup_steps=16`, keeping the full tier model, tokenizer, data and
batch. Set the target's absolute paths and supported backend with `config derive`.
Stage on the real hardware, train through 256, checkpoint and verify, interrupt
and resume there, and finish 320 updates. These short runs test the handoff
mechanics; they don't replace either full-budget tier. To warm-start from a
checkpoint on a different backend, use `train --promote GENERATION` with a
compatible model and tokenizer, then an ordinary same-backend `--resume` after an
interruption. Record the original and new exposure separately. For a
same-backend full-state transfer, use an interrupted full-budget checkpoint with
the config and budget unchanged, and check compatibility. You **cannot**
strict-resume a full-budget checkpoint under the 320-step config. A different
device may still need explicit best-effort handling of runtime drift.

## Acceptance and evidence

Operational acceptance is still **incomplete**. The linked result record shows the
5M and 50M BF16 runs finished and verified, with the remote and Colab checks still
to do. After each run, write a short record in `results/`; keep data and
checkpoint binaries out of Git.

| Gate | Required evidence |
| --- | --- |
| Shared preparation | Real source lock/content inventory, train-only tokenizer, coverage `U`, tails/exclusions, enforced caps, peak costs; repeat requests and both models reuse without refitting/repacking |
| 5M completion | Native actual parameter count; 100,003,840 committed targets / 24,415 updates unless counters expose a discrepancy; verified final generation, held-out finite loss and all outputs |
| 50M completion | Same, for 1,000,001,536 targets / 244,141 updates; independent measured calibration and fit |
| Recovery (both) | Ordered stop and signal interruption; parent/child run IDs, counters/cursor/state restored, last durable point and observed lost work; no duplicated target accounting |
| Handoffs (both tiers × remote/Colab) | Same prepared data on the receiver, root relocation, partial/corrupt upload refusal, actual hardware staging, 256+64 update segment completed, verified persistent export and receiver checkpoint load/eval |
| Cheap inspection | Metadata listing does not read/hash corpus payload; cold verification is explicit and measured |
| Performance | Serial-stage and CPU/GPU/I/O audit; measured bounded-concurrency comparisons where useful; correctness/reuse/recovery preserved; material avoidable bottlenecks resolved and end-to-end costs remeasured before readiness |
| Predictable costs | Forecast vs actual phase times/bytes/peaks, reforecast explanations, cache/temporary/durable separation, no hidden repeated preparation |

Judge model quality separately from these checks. A finished run with finite loss
can still produce poor stories, so record the starting and final held-out loss on
the same fixed selection and keep the poor outputs, without changing the criteria
afterward. Keep failures and note missing measurements. Handoff acceptance needs
the actual handoff commands and checks on the receiving machine. Matching step
counters alone don't show that a resumed run follows the same trajectory; that
would need matching native full-state readings and a comparison of further updates
on the same deterministic runtime.
