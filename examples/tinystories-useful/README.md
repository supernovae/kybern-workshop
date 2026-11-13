# TinyStories: 8,192-Update CPU Learning Baseline

[Back to Workshop README](../../README.md) · [Interactive Guide & Output Viewer (kybern.dev)](https://kybern.dev/models/tinystories-training/) · [Recorded Results & 27 Outputs](../../results/2026-10-19-tinystories-cpu/README.md)

We trained a 4.46M-parameter dense transformer on CPU with [Kybern Model Lab](https://github.com/supernovae/model-lab) for **8,192 updates (33,554,432 target tokens)**. This recipe covers the whole run: full-state checkpoints, held-out evaluation, and 27 generated story continuations.

**Why it's worth a look:** validation loss fell smoothly from `8.369` to `1.704` (perplexity `5.498`), and 17 of 24 full-length outputs reach a recognizable story ending. Yet only 2 of 24 pass our story-quality rubric. The model often repeats itself in loops, swaps character names, or drifts away from the prompt. We publish the full config and all 27 unedited outputs so you can read them and try to do better.

The 24 scored outputs come from 12 prompts, each decoded greedily and with sampling. An AI assistant scored them against the rubric; no independent human review has been done yet. The [per-output assessment](../../results/2026-10-19-tinystories-cpu/quality-assessment.json) includes the rubric and its limitations. We kept the held-out prompts out of model selection, but haven't checked whether they overlap the training stories. The run history includes some failed setup steps and one host interruption. Those results were recorded with an earlier Lab; you will re-record them with the steps below.

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

You need [Kybern Model Lab](https://github.com/supernovae/model-lab) installed for your backend (see the [setup steps](../../README.md#running-workshop-experiments-with-kybern-model-lab)).
The table above describes the environment of our original run. With current Lab you train a new model of your own and get your own run and checkpoint IDs, not our checkpoint bytes.

### 1. Set up a workspace

Work outside Git. The declarations use relative paths, so everything lands beside them.

```sh
SOURCE=examples/tinystories-useful
WORK="$HOME/klab-experiments/tinystories-useful-001"
mkdir -p "$WORK" && cp "$SOURCE"/{source,tokenizer,run}.json "$SOURCE/prompts.txt" "$WORK/" && cd "$WORK"
export KLAB_WORK_DIR="$WORK/klab-state"
klab config validate run.json --kind run
klab config validate tokenizer.json --kind tokenizer
```

### 2. Prepare the data

```sh
klab data lock source.json --output source.lock.json
klab data snapshot source.lock.json --output snapshot
klab tokenizer train tokenizer.json
klab tokenizer verify run.json
klab inspect run.json
klab data prepare run.json --cold-verify
```

`klab inspect` reports the parameter count (4,458,752) and a memory estimate before you spend any time training.

### 3. Train

```sh
klab stage run.json --through warmup --output stages
klab train run.json --backend cpu --runs-dir runs --run-id tinystories-useful-001 --stage-bundle stages
```

`stage` runs the 2-update smoke and 5-update warmup gates first. `train` then goes to step 8,192, saving a full-state
checkpoint every 1,024 updates. If the run stops, continue it with the same command plus
`--resume runs/tinystories-useful-001/checkpoints/latest.json`. On 8 CPU cores the original run took about 3.3 hours.

### 4. Verify, evaluate, probe and generate

```sh
RUN=tinystories-useful-001
klab checkpoint verify "runs/$RUN/checkpoints/latest.json"
klab eval "$RUN" --runs-dir runs --backend cpu
klab report "$RUN" --kind run --runs-dir runs
klab probe "runs/$RUN" --config standard
```

`probe` screens the held-out probe items for leakage into the training stories. The original run never checked this, so run it before you trust a comparison between prompts and checkpoints. Then generate from each prompt in [`prompts.txt`](prompts.txt), once greedy and once sampled:

```sh
klab generate "$RUN" --runs-dir runs --checkpoint latest.json --backend cpu \
  --prompt "$PREFIX" --max-new-tokens 192 --temperature 0 --top-k 0 --seed 42 --strict-context
klab generate "$RUN" --runs-dir runs --checkpoint latest.json --backend cpu \
  --prompt "$PREFIX" --max-new-tokens 192 --temperature 0.7 --top-k 40 --seed 42 --strict-context
```

To talk to the checkpoint, use `klab chat "$RUN" --runs-dir runs --checkpoint latest.json`, or browse everything with `klab dashboard --runs-dir runs`.

### Keep your run repeatable

Record the Lab commit, backend and precision, seed, dataset revision and run ID with anything you publish. A single seed is one sample: to claim an architecture change helps, compare it with `klab try` or `klab sweep` over paired seeds, as in the [microlab](../tinystories-microlab/README.md).

---

## Ideas to Beat This Baseline

Want to run a follow-up and send a PR? Here are four directions to try:

1. **Inspect the loss vs. generation gap:** Compare [`loss-trajectory.csv`](../../results/2026-10-19-tinystories-cpu/loss-trajectory.csv) and [`review.md`](../../results/2026-10-19-tinystories-cpu/review.md) to see why lower validation NLL still left sentence loops and character drift.
2. **Test decoding settings:** On a checkpoint you've verified, try other temperature or top-k schedules on a fresh prompt panel, to see how much of the repetition comes from decoding and how much from the model.
3. **Scale one architectural axis:** Use `klab config derive run.json --set model.ffn_dim=1024 --output wider.yaml` (or try more layers or conditional memory) at the same 33.5M-token budget, and compare both held-out loss and story coherence.
4. **Increase unique story exposure:** Train on a larger slice of `roneneldan/TinyStories` (>50,000 stories) so the model sees its 33.5M tokens in a single pass instead of reading the same stories about 3 times.
