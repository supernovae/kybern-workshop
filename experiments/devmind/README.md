# DevMind — DevMind 340M Base

[Back to Workshop README](../../README.md) · [DevMind Pilot Status (kybern.dev)](https://kybern.dev/models/devmind/)

**DevMind 340M Base** is our dense base model experiment, with 341,885,952 parameters.
Start with the [run guide](run.md).
This directory holds the model and optimizer configs, the 25-leaf corpus preparation plan, and the pinned upstream dataset shards. You run them with [Kybern Model Lab](https://github.com/supernovae/model-lab).

> **Snapshot from 2026-11-10:** Training was continuing in the Engram phase on **2x Intel Arc Pro B70 GPUs**, at `~36,660 valid targets/s` (a **+68.5%** steady speedup).
>
> Segments 1 through 16 finished at step `64,315` with `6,766,391,105` Engram targets and validation loss **`2.5383300`**. Counting the dense backbone phase as well, that is `8,846,765,889` combined targets using the `2,080,374,784`-target nominal reference, or `8,847,422,540` using the `2,081,031,435` packed dense-backbone tokens.
>
> The **300M-target Segment 17** (`devmind-engram-after4550m-300m-131k-nvme-20261110-v1`) runs from step `64,315` to `66,591`, ending at `7,066,393,582` Engram targets. It had passed **step `65,832` / `6,966,400,849` Engram targets**, which is `85.20%` of the `8,176,203,776` Engram reference target. Validation loss reached a new campaign best of **`2.5370861`** at step `65,800`.
>
> Stage 18 (`+300M`, ending at `7,366,396,471` Engram targets) is packed and checked on `/tank`. Stages 19–21 (ending at `~8,176,396,471` Engram targets, `10.257B` combined) are queued in `campaign_orchestrator.py`.
>
> See the [campaign record and v2 plan](engram-campaign-20261106.md) and the [B70 performance notes](b70-performance-20261106.md). We have not published model weights.

---

## Documentation Guide

1. **[Run and revise (`run.md`)](run.md)** — Bind the experiment to real inputs, then train, inspect checkpoints, resume, evaluate and derive the next iteration.
2. **[Scientific Protocol (`protocol.md`)](protocol.md)** — Architecture, the 60/20/20 corpus mixture (educational web, synthetic text, code), training hyperparameters and zero-shot benchmarks.
3. **[Kybern Model Lab Commands (`native-commands.md`)](native-commands.md)** — How to validate the model and optimizer configs and preview preparation commands with `klab`.
4. **[Base Checkpoint & Evaluation (`base-artifact.md`)](base-artifact.md)** — What a trained base checkpoint must ship with, and how to evaluate it without retraining.
5. **[Corpus Preparation Plan (`preparation/README.md`)](preparation/README.md)** — The 25-leaf preparation workflow (`preparation/preparation.json`) and the 84 pinned shard files in [`preparation/lab86/`](preparation/lab86/README.md).

## Quick Validation with `klab`

From a [Kybern Model Lab](https://github.com/supernovae/model-lab) environment, validate the model and optimizer configs:

```sh
klab config validate experiments/devmind/model.json --kind model --json
klab config validate experiments/devmind/optimizer.json --kind optimizer --json
```

To print a preparation phase command without creating an attempt directory or downloading data:

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
