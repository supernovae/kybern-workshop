# DevMind — DevMind 340M Base

[Back to Workshop README](../../README.md) · [DevMind Pilot Status (kybern.dev)](https://kybern.dev/models/devmind/)

**DevMind 340M Base** is our 341,885,952-parameter dense base model experiment.
Start with the [editable experiment and native run loop](run.md).
This directory contains the declarative model and optimizer specifications, the 25-leaf corpus preparation plan, and the pinned upstream dataset shard definitions to be executed with [Tiny Sparse Lab](https://github.com/supernovae/tiny-sparse-lab).

> **Current status (2026-10-29, operator-reported):** Retained corpus R36 and the 32K tokenizer R40 are complete. Another 49 code shards were acquired but are not admitted. The scientific 12B unique-target 60/20/20 mixture is incomplete. Production/model execution remains stopped pending integrated verification and owner review; no DevMind trained baseline or weights are published. These progress facts do not substitute for verifying the actual artifacts when binding.

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

## Architecture Summary

| Parameter | Value |
| --- | --- |
| **Architecture** | Dense causal transformer with SwiGLU, RMSNorm, RoPE, and tied input/output embeddings |
| **Layers / Width / Heads** | 24 layers, hidden dim 1,024, FFN intermediate dim 2,816, 16 attention heads |
| **Context & Vocabulary** | 2,048 tokens, 32,768 byte-level BPE vocabulary |
| **Total Parameters** | **341,885,952** (33.55M embeddings + 100.66M attention + 207.62M FFN + 50.2K norms) |
| **Target Corpus Mixture** | 60% educational web (`smollm-corpus` FineWeb-Edu), 20% synthetic (`cosmopedia-v2`), 20% code (`github-code-clean`) |
