# TinyStories: 8,192-Update CPU Learning Baseline

[Back to Workshop README](../../README.md) · [Interactive Guide & Output Viewer (kybern.dev)](https://kybern.dev/models/tinystories-training/) · [Recorded Results & 27 Outputs](../../results/2026-10-19-tinystories-cpu/README.md)

We trained a 4.46M-parameter dense transformer on CPU with [Kybern Model Lab](https://github.com/supernovae/model-lab) for **8,192 updates (33,554,432 target tokens)**. This recipe covers the whole run: full-state checkpoints, held-out evaluation, and 27 generated story continuations.

**Why it's worth a look:** validation loss fell smoothly from `8.369` to `1.704` (perplexity `5.498`), and 17 of 24 full-length outputs reach a recognizable story ending. Yet only 2 of 24 pass our story-quality rubric. The model often repeats itself in loops, swaps character names, or drifts away from the prompt. We publish the full config and all 27 unedited outputs so you can read them and try to do better.

The 24 scored outputs come from 12 prompts, each decoded greedily and with sampling. An AI assistant scored them against the rubric; no independent human review has been done yet. The [per-output assessment](../../results/2026-10-19-tinystories-cpu/quality-assessment.json) includes the rubric and its limitations. We kept the held-out prompts out of model selection, but haven't checked whether they overlap the training stories. The run history includes some failed setup steps and one host interruption.

We kept the weights locally and don't distribute them; the checkpoint hashes in the records describe those local files. If you reproduce the run, you train your own model and get your own run and checkpoint IDs.

For a fast 40-update starter comparison, see the [TinyStories microlab](../tinystories-microlab/README.md).

---

## Baseline Specifications & Recorded Metrics

| Component | Recorded Value |
| --- | --- |
| **Kybern Model Lab commit** | `7a517b2c065426748cd99702e82ea377877a7809` |
| **CPU container image** | `ghcr.io/supernovae/tiny-sparse-lab@sha256:e3356de49998903e5f03ee2cb28a9b33a5270d380d65d1ceb6fe195531ea812c` |
| **Dataset** | `roneneldan/TinyStories` (`f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`, CDLA-Sharing-1.0) |
| **Data split & tokens** | 50,000 train / 512 validation stories; 11,370,444 train / 104,675 validation packed tokens (~2.95 epochs) |
| **Tokenizer** | Train-only BPE, 4,096 vocabulary |
| **Model architecture** | Dense decoder with tied embeddings: 4 layers, hidden dim 256, FFN dim 768, 4 heads, 4,458,752 parameters |
| **Training schedule** | Sequence 256 × microbatch 4 × accumulation 4 = 4,096 targets/update; 8,192 updates; seed 42 |
| **Runtime environment** | Linux/WSL2, Python 3.14.4, PyTorch 2.14.1+cpu, FP32, 8-CPU container quota |
| **Held-out evaluation** | 16 batches (16,384 targets): **loss `1.7043`**, **perplexity `5.4976`** |
| **Measured wall time & RAM** | ~3.3 hours total training time (929 MiB peak RSS); 89.6s total for all 27 inference runs (429 MiB peak RSS) |

> **Pinned before the Lab rename:** this procedure uses a Kybern Model Lab commit from before the CLI was renamed `klab`. To replay it at that commit, use `sparselab` (and `SPARSELAB_*` variables) in place of `klab`; see [Records Pinned Before the Rename](../../docs/native-workflow.md#records-pinned-before-the-rename).

---

## How to Replicate This Run with `klab`

Before you start:

- Create a fresh workspace directory outside Git and set `WORK` to its absolute path.
- Set `SOURCE` to the absolute path of this directory (`examples/tinystories-useful`).
- Pick two unique run IDs, `FIRST_RUN_ID` and `CONTINUED_RUN_ID`.
- Install Lab for your backend, following the [setup steps](../../README.md#running-workshop-experiments-with-kybern-model-lab).

The table above describes the environment of our original run. With current Lab you train a new model of your own; you won't get our checkpoint bytes back.

### 1. Lock the Dataset and Package the Preparation Recipe

```sh
klab data lock "$SOURCE/source.json" \
  --output "$WORK/source.lock.json" --cache-dir "$WORK/lock-cache" --json
```

Copy `preparation-campaign.json`, `run.json`, `tokenizer.json`, and the new `source.lock.json` into a fresh `$INPUT` directory. Then create and inspect the preparation recipe:

```sh
klab experiment recipe create "$INPUT" --profile preparation \
  --id tinystories-useful-preparation-v1 --entrypoint preparation-campaign.json \
  --file campaign:preparation-campaign.json --file run_config:run.json \
  --file tokenizer_config:tokenizer.json --file source_lock:source.lock.json \
  --output "$WORK/recipe"

# Fill local output paths in $WORK/bindings.json using bindings.template.json
klab experiment recipe preparation inspect "$WORK/recipe/recipe.json" \
  --bindings "$WORK/bindings.json" --json
```

Fill in `$WORK/admission.json` from [`admission.template.json`](admission.template.json), using the hashes that `inspect` printed and your `source.lock.json`.

### 2. Prepare Data, Stage, and Train

Snapshot the dataset, train the tokenizer, and pack the tokens:

```sh
klab experiment recipe preparation apply "$WORK/recipe/recipe.json" \
  --bindings "$WORK/bindings.json" --admission "$WORK/admission.json" \
  --work-dir "$WORK" --json
```

Write the prepared paths into your training config, check the inputs, run the smoke and warmup stages, and train through step 1,024:

```sh
klab config derive "$SOURCE/run.json" \
  --set "tokenizer.path=\"$WORK/tokenizer/tokenizer.json\"" \
  --set "dataset.cache_dir=\"$WORK/data\"" \
  --set "dataset.train_path=\"$WORK/snapshot/train.jsonl\"" \
  --set "dataset.validation_path=\"$WORK/snapshot/validation.jsonl\"" \
  --set "dataset.source_manifest_path=\"$WORK/snapshot/manifest.json\"" \
  --set "logging.root_dir=\"$WORK/runs\"" --output "$WORK/train.yaml" --json

klab config validate "$WORK/train.yaml" --kind run --json
klab tokenizer verify "$WORK/train.yaml" --json
klab data prepared-inputs publish "$WORK/train.yaml" --output "$WORK/prepared"
klab data prepared-inputs verify "$WORK/train.yaml" "$WORK/prepared"
klab stage "$WORK/train.yaml" --through warmup --prepared-inputs "$WORK/prepared" --cold-verify --output "$WORK/stages"
klab train "$WORK/train.yaml" --backend cpu --runs-dir "$WORK/runs" --run-id "$FIRST_RUN_ID" --stage-bundle "$WORK/stages" --stop-after-step 1024
```

Inspect and verify the step-1,024 checkpoint (`FIRST_GENERATION`) before you continue to step 8,192:

```sh
klab checkpoint inspect "$WORK/runs/$FIRST_RUN_ID/checkpoints/latest.json" --json
klab checkpoint inspect "$FIRST_GENERATION" --json
klab checkpoint verify "$FIRST_GENERATION" --json
klab report "$FIRST_RUN_ID" --kind run --runs-dir "$WORK/runs" --json
```

Continue from `FIRST_GENERATION` to the full 8,192 updates, saving a checkpoint every 256 steps:

```sh
klab config derive "$WORK/runs/$FIRST_RUN_ID/resolved_config.yaml" \
  --set checkpoint.every_steps=256 --set "logging.root_dir=\"$WORK/runs\"" \
  --output "$WORK/continued.yaml" --json
klab config validate "$WORK/continued.yaml" --kind run --json
klab train "$WORK/continued.yaml" --backend cpu --runs-dir "$WORK/runs" \
  --run-id "$CONTINUED_RUN_ID" --resume "$FIRST_GENERATION"
```

### 3. Verify, Evaluate, and Generate Stories

When training reaches step 8,192:

1. Set `RUN_ID="$CONTINUED_RUN_ID"` and inspect its `latest.json`.
2. Set `CHECKPOINT` to the generation name that inspection reports, and `GENERATION="$WORK/runs/$RUN_ID/checkpoints/$CHECKPOINT"`. Use the name from your own run; ours won't exist in your workspace.
3. Verify that checkpoint, run held-out evaluation, and generate continuations for the 12 prompts in [`prompts.txt`](prompts.txt):

```sh
klab checkpoint inspect "$WORK/runs/$RUN_ID/checkpoints/latest.json" --json
klab checkpoint inspect "$GENERATION" --json
klab checkpoint verify "$GENERATION" --json
klab eval "$RUN_ID" --runs-dir "$WORK/runs" --checkpoint "$CHECKPOINT" --backend cpu
klab report "$RUN_ID" --kind run --runs-dir "$WORK/runs" --json
```

Generate from each prompt in [`prompts.txt`](prompts.txt) twice: once greedy (`TEMPERATURE=0 TOP_K=0`) and once sampled (`TEMPERATURE=0.7 TOP_K=40`):

```sh
klab generate "$RUN_ID" --runs-dir "$WORK/runs" --checkpoint "$CHECKPOINT" \
  --backend cpu --prompt "$PREFIX" --max-new-tokens 192 \
  --temperature "$TEMPERATURE" --top-k "$TOP_K" --seed 42 \
  --strict-context --show-prompt --json
```

You can also chat with your checkpoint locally:

```sh
klab surface chat --cell "candidate=$GENERATION" --backend cpu --seed 42 --port 8502
```

---

## Ideas to Beat This Baseline

Want to run a follow-up and send a PR? Here are four directions to try:

1. **Inspect the loss vs. generation gap:** Compare [`loss-trajectory.csv`](../../results/2026-10-19-tinystories-cpu/loss-trajectory.csv) and [`review.md`](../../results/2026-10-19-tinystories-cpu/review.md) to see why lower validation NLL still left sentence loops and character drift.
2. **Test decoding settings:** On a checkpoint you've verified, try other temperature or top-k schedules on a fresh prompt panel, to see how much of the repetition comes from decoding and how much from the model.
3. **Scale one architectural axis:** Use `klab config derive run.json --set model.ffn_dim=1024 --output wider.yaml` (or try more layers or conditional memory) at the same 33.5M-token budget, and compare both held-out loss and story coherence.
4. **Increase unique story exposure:** Train on a larger slice of `roneneldan/TinyStories` (>50,000 stories) so the model sees its 33.5M tokens in a single pass instead of reading the same stories about 3 times.
