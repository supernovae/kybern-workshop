# TinyStories: 8,192-Update CPU Learning Baseline

[Back to Workshop README](../../README.md) · [Interactive Guide & Output Viewer (kybern.dev)](https://kybern.dev/models/tinystories-training/) · [Recorded Results & 27 Outputs](../../results/2026-10-19-tinystories-cpu/README.md)

This recipe documents a completed [Tiny Sparse Lab](https://github.com/supernovae/tiny-sparse-lab) training run on CPU: **8,192 updates (33,554,432 target tokens)** on a 4.46M-parameter dense transformer, including verified full-state checkpoints, held-out evaluation, and 27 generated story continuations.

**Why this baseline is interesting:** Validation loss dropped smoothly from `8.369` to `1.704` (perplexity `5.498`), and 17 of 24 full-length outputs reach a recognizable story ending—yet **only 2 of 24 pass our strict story-quality rubric**. The model frequently falls into repetition loops, swaps character names, or drifts away from the opening prompt. We publish the full configuration and all 27 unedited outputs as a concrete, reproducible baseline you can inspect and improve.

For a fast 40-update starter comparison, see the [TinyStories microlab](../tinystories-microlab/README.md).

---

## Baseline Specifications & Recorded Metrics

| Component | Recorded Specification |
| --- | --- |
| **Tiny Sparse Lab commit** | `7a517b2c065426748cd99702e82ea377877a7809` |
| **CPU container image** | `ghcr.io/supernovae/tiny-sparse-lab@sha256:e3356de49998903e5f03ee2cb28a9b33a5270d380d65d1ceb6fe195531ea812c` |
| **Dataset** | `roneneldan/TinyStories` (`f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`, CDLA-Sharing-1.0) |
| **Data split & tokens** | 50,000 train / 512 validation stories; 11,370,444 train / 104,675 validation packed tokens (~2.95 epochs) |
| **Tokenizer** | Train-only BPE, 4,096 vocabulary |
| **Model architecture** | Dense decoder with tied embeddings: 4 layers, hidden dim 256, FFN dim 768, 4 heads, 4,458,752 parameters |
| **Training schedule** | Sequence 256 × microbatch 4 × accumulation 4 = 4,096 targets/update; 8,192 updates; seed 42 |
| **Runtime environment** | Linux/WSL2, Python 3.14.4, PyTorch 2.14.1+cpu, FP32, 8-CPU container quota |
| **Held-out evaluation** | 16 batches (16,384 targets): **loss `1.7043`**, **perplexity `5.4976`** |
| **Measured wall time & RAM** | ~3.3 hours total training time (929 MiB peak RSS); 89.6s total for all 27 inference runs (429 MiB peak RSS) |

---

## How to Replicate This Run with `sparselab`

Choose a fresh external workspace directory `WORK` outside Git, set `SOURCE` to this directory (`examples/tinystories-useful`), and pick unique run IDs (`FIRST_RUN_ID` and `CONTINUED_RUN_ID`).

### 1. Lock the Dataset and Package the Preparation Recipe

```sh
sparselab data lock "$SOURCE/source.json" \
  --output "$WORK/source.lock.json" --cache-dir "$WORK/lock-cache" --json
```

Copy `preparation-campaign.json`, `run.json`, `tokenizer.json`, and the generated `source.lock.json` into a fresh `$INPUT` directory, then create and inspect the preparation recipe:

```sh
sparselab experiment recipe create "$INPUT" --profile preparation \
  --id tinystories-useful-preparation-v1 --entrypoint preparation-campaign.json \
  --file campaign:preparation-campaign.json --file run_config:run.json \
  --file tokenizer_config:tokenizer.json --file source_lock:source.lock.json \
  --output "$WORK/recipe"

# Fill local output paths in $WORK/bindings.json using bindings.template.json
sparselab experiment recipe preparation inspect "$WORK/recipe/recipe.json" \
  --bindings "$WORK/bindings.json" --json
```

Populate `$WORK/admission.json` from [`admission.template.json`](admission.template.json) using the hashes reported by `inspect` and your `source.lock.json`.

### 2. Prepare Data, Stage, and Train

Run dataset snapshotting, tokenizer training, and token packing:

```sh
sparselab experiment recipe preparation apply "$WORK/recipe/recipe.json" \
  --bindings "$WORK/bindings.json" --admission "$WORK/admission.json" \
  --work-dir "$WORK" --json
```

Bind the prepared paths into your training configuration, verify inputs, run smoke/warmup staging, and train through step 1,024:

```sh
sparselab config derive "$SOURCE/run.json" \
  --set "tokenizer.path=\"$WORK/tokenizer/tokenizer.json\"" \
  --set "dataset.cache_dir=\"$WORK/data\"" \
  --set "dataset.train_path=\"$WORK/snapshot/train.jsonl\"" \
  --set "dataset.validation_path=\"$WORK/snapshot/validation.jsonl\"" \
  --set "dataset.source_manifest_path=\"$WORK/snapshot/manifest.json\"" \
  --set "logging.root_dir=\"$WORK/runs\"" --output "$WORK/train.yaml" --json

sparselab config validate "$WORK/train.yaml" --kind run --json
sparselab tokenizer verify "$WORK/train.yaml" --json
sparselab data prepared-inputs publish "$WORK/train.yaml" --output "$WORK/prepared"
sparselab data prepared-inputs verify "$WORK/train.yaml" "$WORK/prepared"
sparselab stage "$WORK/train.yaml" --through warmup --prepared-inputs "$WORK/prepared" --cold-verify --output "$WORK/stages"
sparselab train "$WORK/train.yaml" --backend cpu --runs-dir "$WORK/runs" --run-id "$FIRST_RUN_ID" --stage-bundle "$WORK/stages" --stop-after-step 1024
```

Inspect and verify the step-1,024 checkpoint (`FIRST_GENERATION`) before continuing to step 8,192:

```sh
sparselab checkpoint inspect "$WORK/runs/$FIRST_RUN_ID/checkpoints/latest.json" --json
sparselab checkpoint inspect "$FIRST_GENERATION" --json
sparselab checkpoint verify "$FIRST_GENERATION" --json
sparselab report "$FIRST_RUN_ID" --kind run --runs-dir "$WORK/runs" --json
```

To continue training from `FIRST_GENERATION` to the full 8,192 updates with checkpoints saved every 256 steps:

```sh
sparselab config derive "$WORK/runs/$FIRST_RUN_ID/resolved_config.yaml" \
  --set checkpoint.every_steps=256 --set "logging.root_dir=\"$WORK/runs\"" \
  --output "$WORK/continued.yaml" --json
sparselab config validate "$WORK/continued.yaml" --kind run --json
sparselab train "$WORK/continued.yaml" --backend cpu --runs-dir "$WORK/runs" \
  --run-id "$CONTINUED_RUN_ID" --resume "$FIRST_GENERATION"
```

### 3. Verify, Evaluate, and Generate Stories

Once training completes at step 8,192, verify the final checkpoint (`GENERATION` / basename `CHECKPOINT`), run held-out evaluation, and generate continuations across the 12 prompts in [`prompts.txt`](prompts.txt):

```sh
sparselab checkpoint inspect "$WORK/runs/$RUN_ID/checkpoints/latest.json" --json
sparselab checkpoint inspect "$GENERATION" --json
sparselab checkpoint verify "$GENERATION" --json
sparselab eval "$RUN_ID" --runs-dir "$WORK/runs" --checkpoint "$CHECKPOINT" --backend cpu
sparselab report "$RUN_ID" --kind run --runs-dir "$WORK/runs" --json
```

Run generation for each prompt in [`prompts.txt`](prompts.txt) using both greedy decoding (`TEMPERATURE=0 TOP_K=0`) and sampled decoding (`TEMPERATURE=0.7 TOP_K=40`):

```sh
sparselab generate "$RUN_ID" --runs-dir "$WORK/runs" --checkpoint "$CHECKPOINT" \
  --backend cpu --prompt "$PREFIX" --max-new-tokens 192 \
  --temperature "$TEMPERATURE" --top-k "$TOP_K" --seed 42 \
  --strict-context --show-prompt --json
```

You can also chat interactively with your verified checkpoint locally:

```sh
sparselab surface chat --cell "candidate=$GENERATION" --backend cpu --seed 42 --port 8502
```

---

## Ideas to Beat This Baseline

Want to run a follow-up experiment and submit a PR? Here are four concrete directions to test:

1. **Inspect the loss vs. generation gap:** Compare [`loss-trajectory.csv`](../../results/2026-10-19-tinystories-cpu/loss-trajectory.csv) and [`review.md`](../../results/2026-10-19-tinystories-cpu/review.md) to see why lower validation NLL did not prevent sentence loops or character drift.
2. **Test decoding settings:** Using a verified checkpoint, evaluate different temperature or top-k schedules on a fresh prompt panel to see how much repetition comes from decoding versus model capacity.
3. **Scale one architectural axis:** Use `sparselab config derive run.json --set model.ffn_dim=1024 --output wider.yaml` (or test deeper layers / conditional memory) at the same 33.5M-token budget and compare both held-out loss and story coherence.
4. **Increase unique story exposure:** Train on a larger slice of `roneneldan/TinyStories` (>50,000 stories) so the model sees 33.5M tokens in a single pass rather than repeating the same stories ~3 times.
