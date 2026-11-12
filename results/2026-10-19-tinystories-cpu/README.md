# TinyStories 8,192-update CPU baseline: results

[Workshop README](../../README.md) · [Walkthrough and replication guide](../../examples/tinystories-useful/README.md) · [Interactive viewer on kybern.dev](https://kybern.dev/models/tinystories-training/)

This directory holds the public results of our TinyStories CPU baseline: a 4.46M-parameter dense transformer trained for 8,192 updates (33,554,432 targets) on CPU.

Validation loss fell steadily to `1.7043` (perplexity `5.4976`), and 17 of 24 full-length continuations reach a story ending. Only 2 of 24 pass our strict story-coherence rubric (1 of 12 on the held-out prompts). Repeated sentences, swapped characters and plot drift are still common. That makes this a useful starting point for testing changes to architecture, data or decoding.

## What's here

- [Quality review and all 27 prompt/response pairs (`review.md`)](review.md): the loss curve, what went wrong, and every story continuation, unedited.
- [Run summary (`summary.json`)](summary.json): pinned commits, container digest, timings and evaluation metrics.
- [Per-output quality scores (`quality-assessment.json`)](quality-assessment.json): rubric scores for all 24 full-length outputs.
- [Loss curve (`loss-trajectory.csv`)](loss-trajectory.csv) and [generation timings (`generation-metrics.json`)](generation-metrics.json): training loss by step, and inference time and memory.
- [Commands run (`commands.json`)](commands.json): the exact `sparselab` command arguments and exit codes.
- [Resolved config (`resolved-config.json`)](resolved-config.json) and [checkpoint file index (`run-closure-index.json`)](run-closure-index.json): model and training hyperparameters, and SHA-256 digests for checkpoint `step_00008192_gen_000028` (`d5ba0e06c91d7a864264c5af411ced1c1b1c4e136632d71cd0a7b4309a728149`).
- [Raw generation output (`outputs/`)](outputs/): `final-greedy-1.json` through `12.json` (192 tokens, greedy), `final-sampled-1.json` through `12.json` (192 tokens, `temp=0.7, top_k=40`), and `website-baseline-1.json` through `3.json` (48 tokens, greedy).

## Runtime and resources

- Environment: Linux/WSL2, CPU, FP32, Python 3.14.4, PyTorch 2.14.1+cpu, 8-CPU container quota (`ghcr.io/supernovae/tiny-sparse-lab@sha256:e3356de49998903e5f03ee2cb28a9b33a5270d380d65d1ceb6fe195531ea812c`).
- Training: 11,861.47 seconds (~3.3 hours) of wall time across all the training runs in the lineage (9,895.28 seconds in the final continuation), with 929.14 MiB peak sampled RSS.
- Inference: 89.64 seconds in total across all 27 generation processes (including startup and checkpoint verification), with 429.29 MiB peak sampled RSS.
- File checks: [`manifest.json`](manifest.json) lists the SHA-256 and byte size of every file in this directory.
