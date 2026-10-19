# TinyStories Microlab: Controlled FFN-Width Comparison

[Back to Workshop README](../../README.md) · [Interactive Guide on kybern.dev](https://kybern.dev/models/tinystories-training/)

This starter recipe teaches the core [Tiny Sparse Lab](https://github.com/supernovae/tiny-sparse-lab) comparison workflow (`sparselab try`).
It selects 2,000 training and 100 validation stories from `roneneldan/TinyStories`, fits a train-only 2,048-token BPE tokenizer, and compares two tiny dense decoders—**FFN width 256 vs. 384**—under the exact same seed (`42`), data split, and 40-update (10,240-target) training budget.

- **Looking for a longer trained baseline?** See the [8,192-update TinyStories CPU baseline](../tinystories-useful/README.md) and its [27 recorded story outputs](../../results/2026-10-19-tinystories-cpu/README.md).
- **Interactive walkthrough:** Follow [TinyStories: build, read and improve a small story model](https://kybern.dev/models/tinystories-training/) on `kybern.dev`.

---

## Recipe Overview

| Setting | Value |
| --- | --- |
| **Dataset** | `roneneldan/TinyStories` (`f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`, CDLA-Sharing-1.0) |
| **Subset** | 2,000 train / 100 validation stories (deduplicated, overlap excluded) |
| **Tokenizer** | 2,048-token BPE fitted on training text only |
| **Baseline architecture** | 2 layers, hidden dimension 128, 4 attention heads, FFN dimension 256, context 128 (~590K parameters) |
| **Candidate intervention** | `model.ffn_dim: 384` (defined in [`wider-ffn.yaml`](wider-ffn.yaml)) |
| **Training budget** | Sequence length 64, microbatch 2, accumulation 2 (256 targets/update); 40 updates / 10,240 targets per arm |

## 1. Set Up an External Workspace

Create a fresh workspace directory outside your Git checkout and copy the recipe declarations into it:

```sh
RECIPE=examples/tinystories-microlab
WORK="$HOME/sparselab-experiments/tinystories-microlab-001"
mkdir -p "$WORK"
cp -R "$RECIPE/declarations" "$WORK/declarations"
cp "$RECIPE/wider-ffn.yaml" "$RECIPE/try.yaml" "$WORK/"
mkdir "$WORK/evidence"
```

Relative paths inside `declarations/` resolve to `../snapshot`, `../tokenizer`, `../data`, and `../runs` within `$WORK`, while `try.yaml` stores paired experiment records under `$WORK/lab`.

## 2. Validate Configurations and Preview the Delta

Before downloading data or starting training, validate the baseline config and preview the candidate derivation:

```sh
sparselab config validate "$WORK/declarations/run.yaml" --kind run --json
sparselab config validate "$WORK/declarations/tokenizer.yaml" --kind tokenizer --json
sparselab config derive "$WORK/declarations/run.yaml" \
  --set 'model.ffn_dim=384' --output "$WORK/candidate-preview.yaml" --json
```

Inspect `$WORK/candidate-preview.yaml` and its `.derivation.json` sidecar to verify that `model.ffn_dim` is the only modified hyperparameter.

## 3. Prepare Inputs and Run the Comparison

Lock and snapshot the dataset, train the tokenizer, and run the paired comparison with `sparselab try`:

```sh
sparselab data lock "$WORK/declarations/source.yaml" \
  --output "$WORK/source.lock.json"
sparselab data snapshot "$WORK/source.lock.json" --output "$WORK/snapshot"
sparselab tokenizer train "$WORK/declarations/tokenizer.yaml"
sparselab try "$WORK/wider-ffn.yaml" --vs "$WORK/declarations/run.yaml" \
  --config "$WORK/try.yaml" --backend cpu --json
```

> **Note on disk space:** Although the snapshot selects 2,100 stories (capped at 16 MiB of extracted text), the initial Hugging Face Hub download caches the upstream Parquet shard (~250 MB+).

`sparselab try` prepares the tokenized dataset, trains both the baseline (`ffn_dim=256`) and candidate (`ffn_dim=384`) arms, and evaluates both checkpoints on the same held-out validation batches.

## 4. Inspect Results

Use the `TRY_ID` printed by `sparselab try` to view the experiment report or open the interactive dashboard:

```sh
sparselab report TRY_ID --lab-dir "$WORK/lab" --json
sparselab explore TRY_ID --lab-dir "$WORK/lab"
sparselab dashboard --lab-dir "$WORK/lab"
```

## Next Steps

- **Test across multiple seeds:** A single 40-update run teaches the mechanics of a controlled comparison, not whether a wider FFN reliably improves story generation. Repeat promising changes across paired seeds (`seed: 7`, `seed: 17`, etc.) using `--config`.
- **Explore the 8,192-update baseline:** Check out [`examples/tinystories-useful`](../tinystories-useful/README.md) to see how a 4.46M-parameter model behaves after 33.5M training tokens—and try the improvement exercises to fix its repetition and plot-drift issues.
- **Provenance:** [`migration.json`](migration.json) and [`VALIDATION.md`](VALIDATION.md) record the declaration hashes and CLI schema checks for this recipe.
