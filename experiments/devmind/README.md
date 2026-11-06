# DevMind — DevMind 340M Base

[Back to Workshop README](../../README.md) · [DevMind Pilot Status (kybern.dev)](https://kybern.dev/models/devmind/)

**DevMind 340M Base** is our 341,885,952-parameter dense base model experiment.
Start with the [editable experiment and native run loop](run.md).
This directory contains the declarative model and optimizer specifications, the 25-leaf corpus preparation plan, and the pinned upstream dataset shard definitions to be executed with [Tiny Sparse Lab](https://github.com/supernovae/tiny-sparse-lab).

> **Current status (2026-11-06, operator-observed):** Training continues in the Engram phase. Completed segments reached step 31,476 / `2,436,319,171` Engram targets (validation loss `2.568749`), and the active **160M-target continuation** (`devmind-engram-after7m-160m-131k-nvme-20261106-v1`, step 31,476 $\to$ 32,689 / `2,596,321,940` Engram targets) has already passed **step 32,083 / 2,516,383,537 Engram targets** (`4,596,758,321` combined exposure targets) with validation loss improving to **2.568486** and end-to-end throughput increasing to **20,254.9 valid targets/s (+6.9%)**. A subsequent **95M-target segment** ($\to$ `2,691,321,940` Engram targets) is pre-packed from newly qualified supply. See the [current campaign record & v2 blueprint](engram-campaign-20261106.md) and [B70 performance follow-up](b70-performance-20261106.md) for preserved lineage, the 35/30/15/15/5 mixture, Python/coding/agentic data expansion, exact shard SHA-256s, and v2 data-flow architecture. No model weights are published.

---

## Documentation Guide

1. **[Run and revise (`run.md`)](run.md)** — Bind editable intent to real inputs, then use native train, checkpoint inspection, resume, evaluation and derivation.
2. **[Scientific Protocol (`protocol.md`)](protocol.md)** — Architecture dimensions, 60/20/20 corpus mixture (educational web, synthetic text, code), training hyperparameters, and zero-shot evaluation benchmarks.
3. **[Tiny Sparse Lab Commands (`native-commands.md`)](native-commands.md)** — How to validate the model/optimizer sections and compile preparation phase commands with `sparselab`.
4. **[Base Checkpoint & Evaluation Contract (`base-artifact.md`)](base-artifact.md)** — Required artifact closure and evaluation-only reuse specification once the base model is trained.
5. **[Corpus Preparation Plan (`preparation/README.md`)](preparation/README.md)** — 25-leaf preparation workflow (`preparation/preparation.json`) and the 84 pinned shard declarations in [`preparation/lab86/`](preparation/lab86/README.md).

## Quick Validation with `sparselab`

You can validate the model and optimizer configuration sections directly from a [Tiny Sparse Lab](https://github.com/supernovae/tiny-sparse-lab) environment:

```sh
sparselab config validate experiments/devmind/model.json --kind model --json
sparselab config validate experiments/devmind/optimizer.json --kind optimizer --json
```

To compile and inspect a corpus preparation phase command without creating an attempt directory or downloading data:

```sh
sparselab attempt phase-command \
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

