# DevMind — DevMind 340M Base

[Back to Workshop README](../../README.md) · [DevMind Pilot Status (kybern.dev)](https://kybern.dev/models/devmind/)

**DevMind 340M Base** is our 341,885,952-parameter dense base model experiment.
Start with the [editable experiment and native run loop](run.md).
This directory contains the declarative model and optimizer specifications, the 25-leaf corpus preparation plan, and the pinned upstream dataset shard definitions to be executed with [Kybern Model Lab](https://github.com/supernovae/model-lab).

> **Historical snapshot (2026-11-10, operator-observed):** Training was continuing on **2x Intel Arc Pro B70 GPUs** (`~36,660 valid targets/s`, **+68.5%** steady speedup) in the Engram phase. Completed Segments 1 through 16 reached step `64,315` / `6,766,391,105` Engram targets (`8,846,765,889` combined exposure targets using the `2,080,374,784` nominal dense-backbone reference, or `8,847,422,540` with the `2,081,031,435` packed dense-backbone tokens; validation loss **`2.5383300`**), and the active **300M-target Segment 17** (`devmind-engram-after4550m-300m-131k-nvme-20261110-v1`, step `64,315` $\to$ `66,591` / `7,066,393,582` Engram targets) has already passed **step `65,832` / `6,966,400,849` Engram targets** (`85.20%` of the `8,176,203,776` Engram reference target) with validation loss improving to a new campaign-best **`2.5370861`** at step `65,800`. Stage 18 (`+300M` $\to$ `7,366,396,471` Engram targets) is packed and verified on `/tank`, and Stages 19–21 ($\to$ `~8,176,396,471` Engram targets / `10.257B` combined targets) are staged in `campaign_orchestrator.py`. See the [current campaign record & v2 blueprint](engram-campaign-20261106.md) and [B70 performance follow-up](b70-performance-20261106.md). No model weights are published.

---

## Documentation Guide

1. **[Run and revise (`run.md`)](run.md)** — Bind editable intent to real inputs, then use native train, checkpoint inspection, resume, evaluation and derivation.
2. **[Scientific Protocol (`protocol.md`)](protocol.md)** — Architecture dimensions, 60/20/20 corpus mixture (educational web, synthetic text, code), training hyperparameters, and zero-shot evaluation benchmarks.
3. **[Kybern Model Lab Commands (`native-commands.md`)](native-commands.md)** — How to validate the model/optimizer sections and compile preparation phase commands with `klab`.
4. **[Base Checkpoint & Evaluation Contract (`base-artifact.md`)](base-artifact.md)** — Required artifact closure and evaluation-only reuse specification once the base model is trained.
5. **[Corpus Preparation Plan (`preparation/README.md`)](preparation/README.md)** — 25-leaf preparation workflow (`preparation/preparation.json`) and the 84 pinned shard declarations in [`preparation/lab86/`](preparation/lab86/README.md).

## Quick Validation with `klab`

You can validate the model and optimizer configuration sections directly from a [Kybern Model Lab](https://github.com/supernovae/model-lab) environment:

```sh
klab config validate experiments/devmind/model.json --kind model --json
klab config validate experiments/devmind/optimizer.json --kind optimizer --json
```

To compile and inspect a corpus preparation phase command without creating an attempt directory or downloading data:

```sh
klab attempt phase-command \
  --plan experiments/devmind/preparation/preparation.json \
  --attempt-root /tmp/devmind-preview \
  --label transport-init \
  --bindings-json '{"ACQUISITION_PROJECT":"/path/to/experiments/devmind/preparation/lab86/project-acquire.yaml"}'
```

## Architecture Summary — Original Dense Recipe

| Parameter | Value |
| --- | --- |
| **Architecture** | Dense causal transformer with SwiGLU, RMSNorm, RoPE, and tied input/output embeddings |
| **Layers / Width / Heads** | 24 layers, hidden dim 1,024, FFN intermediate dim 2,816, 16 attention heads |
| **Context & Vocabulary** | 2,048 tokens, 32,768 byte-level BPE vocabulary |
| **Total Parameters** | **341,885,952** (33.55M embeddings + 100.66M attention + 207.62M FFN + 50.2K norms) |
| **Target Corpus Mixture** | 60% educational web (`smollm-corpus` FineWeb-Edu), 20% synthetic (`cosmopedia-v2`), 20% code (`github-code-clean`) |

