# TinyStories Microlab: Controlled FFN-Width Comparison

[Back to Workshop README](../../README.md) · [Interactive Guide on kybern.dev](https://kybern.dev/models/tinystories-training/)

This starter recipe teaches the main [Kybern Model Lab](https://github.com/supernovae/model-lab) comparison workflow, `klab try`.
It takes 2,000 training and 100 validation stories from `roneneldan/TinyStories`, fits a 2,048-token BPE tokenizer on the training stories, and compares two tiny dense decoders with **FFN width 256 and 384**. Both use the same seed (`42`), the same data split, and the same 40-update (10,240-target) training budget.

- **Want a longer-trained baseline?** See the [8,192-update TinyStories CPU baseline](../tinystories-useful/README.md) and its [27 recorded story outputs](../../results/2026-10-19-tinystories-cpu/README.md).
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

Create a fresh workspace directory outside your Git checkout and copy the recipe files into it:

```sh
RECIPE=examples/tinystories-microlab
WORK="$HOME/klab-experiments/tinystories-microlab-001"
mkdir -p "$WORK"
cp -R "$RECIPE/declarations" "$WORK/declarations"
cp "$RECIPE/wider-ffn.yaml" "$RECIPE/try.yaml" "$WORK/"
mkdir "$WORK/evidence"
```

The configs in `declarations/` use relative paths, so their outputs land in `$WORK/snapshot`, `$WORK/tokenizer`, `$WORK/data`, and `$WORK/runs`. `try.yaml` keeps the comparison records in `$WORK/lab`.

## 2. Validate Configurations and Preview the Delta

Before you download data or train, check the baseline config and preview the candidate:

```sh
klab config validate "$WORK/declarations/run.yaml" --kind run --json
klab config validate "$WORK/declarations/tokenizer.yaml" --kind tokenizer --json
klab config derive "$WORK/declarations/run.yaml" \
  --set 'model.ffn_dim=384' --output "$WORK/candidate-preview.yaml" --json
```

Open `$WORK/candidate-preview.yaml` and its `.derivation.json` sidecar file and check that `model.ffn_dim` is the only setting that changed.

## 3. Prepare Inputs and Run the Comparison

Lock and snapshot the dataset, train the tokenizer, and run the paired comparison with `klab try`:

```sh
klab data lock "$WORK/declarations/source.yaml" \
  --output "$WORK/source.lock.json"
klab data snapshot "$WORK/source.lock.json" --output "$WORK/snapshot"
klab tokenizer train "$WORK/declarations/tokenizer.yaml"
klab try "$WORK/wider-ffn.yaml" --vs "$WORK/declarations/run.yaml" \
  --config "$WORK/try.yaml" --backend cpu --json
```

> **Disk space:** the snapshot keeps only 2,100 stories (at most 16 MiB of text), but the first Hugging Face Hub download caches the whole Parquet shard (~250 MB+).

`klab try` tokenizes the dataset, trains the baseline (`ffn_dim=256`) and the candidate (`ffn_dim=384`), and evaluates both on the same held-out validation batches.

## 4. Inspect Results

Use the `TRY_ID` that `klab try` printed to read the report or open the dashboard:

```sh
klab report TRY_ID --lab-dir "$WORK/lab" --json
klab explore TRY_ID --lab-dir "$WORK/lab"
klab dashboard --lab-dir "$WORK/lab"
```

## Next Steps

- **Try more seeds:** one 40-update run shows you how a comparison works. To learn whether a wider FFN reliably helps, repeat promising changes across paired seeds (`seed: 7`, `seed: 17`, and so on) with `--config`.
- **Explore the 8,192-update baseline:** [`examples/tinystories-useful`](../tinystories-useful/README.md) shows how a 4.46M-parameter model behaves after 33.5M training tokens. Its exercises suggest ways to fix the repetition and plot drift.
- **File hashes and checks:** [`migration.json`](migration.json) lists the hash of each config file, and [`VALIDATION.md`](VALIDATION.md) lists the CLI checks we ran on this recipe.
