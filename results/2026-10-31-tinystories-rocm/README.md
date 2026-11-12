# TinyStories on Ryzen 9 5900X / Radeon RX 7900 XTX

Lab `b3a1630ec09dbddae36301b0acef4122623ed939`, Workshop recipe `e186e42194bd69f2fb68318a79c51c9bbcc4e7c7`, existing Python 3.14 / PyTorch 2.13.0+rocm10.0.0 / ROCm 7.15.26333, with no new installs or runtime fixes. We keep the native command records and binary artifacts privately. This directory holds the configs and measurements for review; it has no downloadable weights.

## 5M completion and recovery

We trained the original 5,311,232-parameter recipe for exactly 24,415 updates / 100,003,840 targets across three segments. A check of the run lineage found no gaps and no update applied twice. At both resume points, optimizer tensors, RNG, cursor, schedule and counters matched the parent state exactly. A SIGTERM sent after the verified step-512 checkpoint stopped the run cleanly at step 544, and training continued from that checkpoint. We did not compare against an uninterrupted run.

Final fixed-selection held-out loss was 1.45059 (perplexity 4.26563), versus initial 8.38268. The full-state checkpoint is `6f04800d221f81074c507cdef4e6ec882345f62d78dc222e34880819993cb873`. Command time across segments was 53m 5s, including resume/signal handling; optimizer work was 34m 34s, reporting 871s and checkpoints 49s. See [completion evidence](5m-completion.json).

All [24 fixed-prompt continuations](generation-panel-5m.json) are saved with their exact text and settings: 12 prompts, greedy and sampled, 192 new-token cap, seed 42. The model learned recognizable prose, dialogue and endings, but it often repeats itself, swaps characters or loses the problem the prompt set up. Examples include a forgotten red ball, Eli becoming Lily, repeated apple accusations and a boat hole that never gets fixed. These notes come from one assistant reading the outputs, and the prompts were not checked against the training data. The loss figure says nothing reliable about story quality on its own.

## 50M bounded calibration

Every candidate used the same initial weights SHA `8990e1a7cbc8859f916238fce7fb31272e5b35aced1e5e00c10d2b340ab73ab7`, prepared data, seed, full schedule, and 4,096 targets/update. Each stopped at 256 updates / 1,048,576 targets. Throughput uses updates 17–256; optimizer/reporting seconds below cover all 256 updates.

| Candidate | Steady targets/s | Peak reserved GiB | Optimizer seconds | Reporting seconds |
| --- | ---: | ---: | ---: | ---: |
| baseline-fp32-mb4-ga4 | 10,616 | 1.65 | 98.77 | 9.67 |
| 50m-fp32-mb8-ga2 | 11,150 | 2.28 | 94.08 | 4.34 |
| 50m-fp32-mb16-ga1 | 10,949 | 3.36 | 95.81 | 9.97 |
| 50m-bf16-mb8-ga2 | 46,203 | 2.18 | 23.11 | 9.21 |
| 50m-fp32-sdpa-mb8-ga2 | 11,140 | 2.11 | 94.27 | 9.91 |

Every candidate logged finite losses and zero overflow retries, passed native smoke and warmup with full-state reload checks, and wrote a verified full-state final checkpoint. That shows the short runs were healthy; it says nothing about convergence. See [hashes, timings and checks](50m-calibration.json) and the [configs](../../experiments/tinystories/calibration/README.md).

BF16 8 × 2 is the one worth taking forward: about 4.35× the optimizer throughput of the original FP32 4 × 4, and 4.14× FP32 8 × 2. Larger FP32 batches help only a little. FP32 SDPA made essentially no difference here, and we didn't check which kernel it actually used. We did not test BF16 and SDPA together. On the same selection, BF16 8 × 2 validation loss (4.374565) is close to FP32 8 × 2 (4.374460). Microbatch size changes how many validation targets are scored, so don't rank losses across batch sizes.

The original FP32 50M step-256 checkpoint is unchanged. At this point no full 50M run had started; the later fresh BF16 run is recorded below. At the measured BF16 rate, the billion-target budget needs about 6 hours of optimizer work, plus reporting, checkpoints and other costs that need measuring over a longer run. Each candidate ran once, in sequence, so there are no confidence intervals. Native driver allocation, GPU utilization and data-loader stall counters were not available.

Remote and Colab handoffs and copying across machines are still untested. No Devmind work was resumed.

## Reviewed reporting fix: same-configuration host comparison

We ran a separate BF16 8 × 2 calibration on Lab `6c31d7f9be516f2adc3ed92849bf4e8057a9169e` (PR 288) from its own checkout, pointing only that process at the new source. We installed nothing, edited no registry and patched nothing on the host. The config, initial weights and training/validation array hashes match the earlier candidate exactly.

| Measured phase | Before (`b3a1630`) | After (`6c31d7f`) |
| --- | ---: | ---: |
| Reporting | 9.206 s | 5.472 s |
| Optimizer updates | 23.115 s | 22.792 s |
| Full command | 57.980 s | 52.986 s |
| Steady targets/s | 46,203 | 46,599 |

In this one pair, reporting time fell about 41% and command time about 9%. Final validation loss was identical (4.374564543366432), with zero overflow retries and a verified full-state checkpoint. This fix doesn't explain or remove all 871 seconds of reporting seen in the longer 5M run. See the [comparison details](reporting-comparison.json).

On the new pin, the first stage correctly refused the old input bundle, which was tied to the old code. Republishing with the public command then unexpectedly retokenized into a new packed cache (about 122 seconds preparation, 127 seconds publication), even though the corpus and tokenizer had not changed. Both output arrays have exactly the original hashes, and the original cache was left alone. We expected reuse here and didn't get it. These times are not in the training-phase timings.

The same range of commits includes PR 286, which changes `data/sources.py`. The preparation fingerprint covers every `data/*.py` file and `config/models.py`, while PR 288 touches only reporting files outside it. So the download change is what made Lab treat the existing prepared cache as different. Reusing caches across such changes needs a deliberate, tested compatibility rule in Lab; we did not bypass the check or rewrite the cache by hand.

## Fresh 50M BF16 completion and generation

The [BF16 recipe](../../experiments/tinystories/run-50m-bf16.json), published at Workshop `7aa2d54d3fc5beead7e80f158fc3b2a9e3366277`, ran to completion on reviewed Lab `903ad2f0bb261935132dee53295aba6b66f8e792`. It started from a fresh seed-42 initialization, separate from the FP32 and calibration weights. The 50,556,800-parameter model used reference attention, BF16, microbatch 8, accumulation 2 and sequence length 256. We reused the snapshot and tokenizer; the new Lab pin needed one fresh packing, and its token arrays matched the existing bytes.

Exactly 244,141 updates committed 1,000,001,536 targets across three segments, with no gaps or duplicates. After the first 256 updates we restored the full state; an orderly SIGTERM stopped the next segment at step 543, and another exact restore carried on to the original horizon. Optimizer tensors, RNG, cursor, schedule and counters matched at both resume points. We did not compare against an uninterrupted run.

The final full-state checkpoint verified: `c72d7d0283de2c6008f1b80d855bad6cb6ebc497f0094957a8982bd58a049110`. Final held-out loss was 1.075294 (perplexity 2.930855); the best was 1.074736 at step 240,640. This evaluation covers 65,536 targets against 32,768 for 5M, so don't rank the two losses against each other. See the [full cleaned-up record](50m-bf16-completion.json).

Training commands totaled 9h 14m 43s, averaging 30,046 targets/s including overhead. Optimizer work averaged 45,362 targets/s and took 22,045 seconds; reporting took 6,861 seconds and checkpoints 2,845 seconds. So reporting still costs a lot over a full run, even after the earlier fix. Peak reserved VRAM was 2.18 GiB, with zero overflow retries and no swap seen. Native driver utilization and loader-starvation counters were not available. Training command time leaves out preparation, staging and the later generation.

The [matching 24-output panel](generation-panel-50m.json) uses the final checkpoint, the same 12 prompts in greedy and sampled modes, seed 42 and a 192-new-token cap. All commands succeeded and every output is kept. The simple red-ball, bird-rescue and apple-sharing stories keep details the 5M model lost, and Eli keeps his name. Failures remain: Noah becomes Mah, the boat hole and the power outage can go unresolved, the absent neighbor comes back, and repetition and random conflicts persist. These notes come from one assistant reading the outputs. The 5M and 50M runs differ in model size, training budget, precision, schedule and source pin, so this comparison doesn't isolate the effect of size. The 50M model still isn't reliably good at stories, and moving it to remote machines or Colab is untested.

## What this public copy includes

In this public copy, local file paths, interpreter paths and runtime registry IDs are replaced with placeholders, and machine-specific fields and exact wall-clock timestamps are left out. Command arrays are templates. The native config, source and checkpoint hashes are those of the original files, not of these cleaned-up excerpts. Hardware class, software versions, model settings, measurements, limitations and all 48 generated texts from the two panels are included. The full native records and binaries stay private.
