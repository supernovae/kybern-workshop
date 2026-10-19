# TinyStories 8,192-Update CPU Baseline — Recorded Results

[Back to Workshop README](../../README.md) · [Walkthrough & Replication Guide](../../examples/tinystories-useful/README.md) · [Interactive Viewer on kybern.dev](https://kybern.dev/models/tinystories-training/)

This directory contains the complete public evidence package for our **8,192-update (33,554,432-target)** TinyStories CPU baseline run on a 4.46M-parameter dense transformer.

**Key takeaway:** The model trained smoothly to a validation loss of **`1.7043`** (perplexity **`5.4976`**), and **17 of 24** full-length continuations reach a story ending—yet **only 2 of 24** pass our strict story-coherence rubric (1 of 12 on the held-out prompt subset). Sentence repetition loops, character swaps, and plot drift remain common, making this a practical baseline for testing architecture, data, or decoding improvements.

## Contents of This Directory

- **[Full Quality Review & All 27 Prompt/Response Pairs (`review.md`)](review.md)** — Loss trajectory, failure analysis, and every unedited story continuation.
- **[Run Summary (`summary.json`)](summary.json)** — Pinned commits, container digest, timings, and evaluation metrics.
- **[Per-Output Quality Assessment (`quality-assessment.json`)](quality-assessment.json)** — Rubric scores for all 24 full-length outputs.
- **[Loss Trajectory (`loss-trajectory.csv`)](loss-trajectory.csv)** & **[Generation Timings (`generation-metrics.json`)](generation-metrics.json)** — Step-by-step training loss curve and inference resource measurements.
- **[Executed CLI Commands (`commands.json`)](commands.json)** — Exact `sparselab` command arguments and exit statuses.
- **[Resolved Configuration (`resolved-config.json`)](resolved-config.json)** & **[Checkpoint Closure Index (`run-closure-index.json`)](run-closure-index.json)** — Model/training hyperparameters and SHA-256 digests for checkpoint `step_00008192_gen_000028` (`d5ba0e06c91d7a864264c5af411ced1c1b1c4e136632d71cd0a7b4309a728149`).
- **[Raw Generation Envelopes (`outputs/`)](outputs/)** — `final-greedy-1.json` through `12.json` (192 tokens, greedy), `final-sampled-1.json` through `12.json` (192 tokens, `temp=0.7, top_k=40`), and `website-baseline-1.json` through `3.json` (48 tokens, greedy).

## Runtime & Resource Summary

- **Environment:** Linux/WSL2 CPU FP32, Python 3.14.4, PyTorch 2.14.1+cpu, 8-CPU container quota (`ghcr.io/supernovae/tiny-sparse-lab@sha256:e3356de49998903e5f03ee2cb28a9b33a5270d380d65d1ceb6fe195531ea812c`).
- **Training wall time & memory:** 11,861.47 seconds (~3.3 hours) across the completed trainer lineage (9,895.28 seconds in the final continuation), with 929.14 MiB peak sampled RSS.
- **Inference wall time & memory:** 89.64 seconds total across all 27 generation processes (including startup and checkpoint verification), with 429.29 MiB peak sampled RSS.
- **Artifact verification:** [`manifest.json`](manifest.json) records the SHA-256 and byte size of every file in this directory.
