# Synthetic CPU smoke run: results

[Workshop README](../../README.md) · [Synthetic CPU recipe guide](../../examples/synthetic-cpu/README.md)

We ran the synthetic CPU workflow end to end and offline in [Kybern Model Lab](https://github.com/supernovae/model-lab): preparing synthetic text and a tokenizer, a one-step training attempt, held-out validation scoring, a verified report, and a replay that should change nothing.

## Pinned revisions and environment

| Component | Revision / Digest |
| --- | --- |
| **Kybern Model Lab** | `b155cdcc1462cfbcbd5f0cf5261eb8aa197ef9dc` |
| **Preparation commit (`A`)** | `28a01d69442c8b08e5ba78e4561ff4f69443e1e5` |
| **Workflow commit (`B`)** | `e8250556412bc8535c029d80af3fa735b82c1ffa` |
| **Installed source SHA-256** | `1f947cce513952bef88f9397e12bb3661efe97ece604cab04330f197e0a44a26` |
| **`uv.lock` SHA-256** | `2058fe5c126df074879648018c36288386190446b94b147b811671185958ac86` |
| **Runtime** | CPython 3.14.8, PyTorch 2.14.0+cpu, tokenizers 0.22.2, NumPy 2.5.3, datasets 4.8.5, PyArrow 25.0.1 |

## Model and training

- Model: dense decoder, 1 layer, hidden dim 16, FFN dim 32, 2 heads, context 32, vocab 260 (6,768 parameters).
- Settings: seed 7, CPU FP32, sequence length 16, microbatch 1, accumulation 1, AdamW (`lr=3e-4`, floor `3e-5`).
- Synthetic data caps: 8 train / 4 validation documents (256 / 128 token caps); tokenizer trained on up to 8 documents.

| Stage | Verified Updates | Target Positions | Update Timing |
| --- | ---: | ---: | ---: |
| **Smoke** | 2 | 32 | 0.402239 s |
| **Warmup** | 5 | 80 | 0.088141 s |
| **Main** | 1 | 16 | 0.047268 s |

## Command timings and resources

We ran every step under the `sparselab` resource monitor (`600s` wall limit, `4 GiB` process-tree RSS limit, `1 GiB` workspace growth limit, 1s sampling):

| Monitored Command | Status | Seconds | Peak Tree RSS (Bytes) | Added Workspace (Bytes) | Samples |
| --- | --- | ---: | ---: | ---: | ---: |
| Preparation | `COMPLETE` | 9.587894 | 437,280,768 | 73,736 | 10 |
| Preparation replay | `COMPLETE` | 6.452063 | 430,981,120 | 23,824 | 7 |
| Cold workflow resolution | `COMPLETE` | 6.515828 | 430,206,976 | 11,540 | 7 |
| Plan / acceptance | `COMPLETE` | 14.273060 | 445,087,744 | 127,667 | 13 |
| Explicit approval | `COMPLETE` | 8.426039 | 436,744,192 | 47,329 | 9 |
| First traced invocation (`strace`) | `MONITOR_ERROR` | 140.834523 | 1,090,207,744 | 1,015,803 | 138 |
| Traced continuation (`strace`) | `MONITOR_ERROR` | 121.038262 | 1,172,439,040 | 655,900 | 115 |
| Untraced continuation | `COMPLETE` | 291.320703 | 1,984,081,920 | 3,213,741 | 275 |
| Verified report | `COMPLETE` | 9.558889 | 440,287,232 | 21,702 | 10 |
| Completed replay | `COMPLETE` | 8.947403 | 444,030,976 | 56,586 | 9 |

Running the worker under `strace` made its transport time out during the precision probes. Resuming without `strace` (`SPARSELAB_WORKER_LEASE_DIR="$WORK/worker-leases"`) finished cleanly in 291.3s with a peak RSS of 1.85 GiB (`1,984,081,920` bytes).

## IDs, digests and evaluation

- Verified report ([`report.json`](report.json)): SHA-256 `95fb40744a653b3bde13af9dd078239ddb9b7d4357be0ac1fdc4e0f6aef2a4c8`
- Attempt ID: `00b3938a-611f-4af8-bb4b-411e1b44e9d6`
- Run ID: `1632259c-9aa4-45bc-965f-de87d7fadb2c`
- Final checkpoint: `step_00000001_gen_000002` (`010d3d137dd6943b2dc7317223d36fffd60ca1a3ded0680e86a62bf8f76ec81f`)
- Held-out evaluation ([`evaluation-excerpt.json`](evaluation-excerpt.json)): 1 batch / 16 targets, loss `5.441391`, perplexity `230.763060`
- Replay ([`replay-excerpt.json`](replay-excerpt.json)): `resume` without `--execute-runs` showed all 8 campaign stages still `COMPLETE`, with no new training attempts.

## Files in this directory

- [`summary.json`](summary.json): full timings, probe results and metrics
- [`report.json`](report.json): the native `sparselab` workflow report
- [`evaluation-excerpt.json`](evaluation-excerpt.json): held-out evaluation output
- [`replay-excerpt.json`](replay-excerpt.json): the replay check
- [`monitor-excerpts.json`](monitor-excerpts.json) and [`receipt-excerpts.json`](receipt-excerpts.json): monitor and stage records, with private details removed
- [`cleanup-excerpt.json`](cleanup-excerpt.json): process cleanup check
- [`evidence-index.json`](evidence-index.json): SHA-256 list of every JSON file in this directory
- [`commands.md`](commands.md): the exact CLI commands run
