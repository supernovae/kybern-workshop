# TinyStories on Ryzen 9 5900X / Radeon RX 7900 XTX

Lab `b3a1630ec09dbddae36301b0acef4122623ed939`, Workshop recipe `e186e42194bd69f2fb68318a79c51c9bbcc4e7c7`, existing Python 3.14 / PyTorch 2.13.0+rocm10.0.0 / ROCm 7.15.26333. No dependency installs or runtime repairs. Native command receipts and original binary artifacts are retained privately. This directory contains reviewable declarations and observations, not downloadable weights.

## 5M completion and recovery

The original 5,311,232-parameter recipe completed exactly 24,415 updates / 100,003,840 targets across three segments. The lineage audit found no gaps or duplicate applied updates. At both resume boundaries, optimizer tensors, RNG, cursor, schedule and counters matched the parent state exactly. SIGTERM after a verified step-512 checkpoint stopped cleanly at step 544, and training continued from that generation. This does not claim equivalence to an independently run uninterrupted trajectory.

Final fixed-selection held-out loss was 1.45059 (perplexity 4.26563), versus initial 8.38268. The full-state checkpoint is `6f04800d221f81074c507cdef4e6ec882345f62d78dc222e34880819993cb873`. Command time across segments was 53m 5s, including resume/signal handling; optimizer work was 34m 34s, reporting 871s and checkpoints 49s. See [completion evidence](5m-completion.json).

All [24 fixed-prompt continuations](generation-panel-5m.json) are retained with exact text and policy: 12 prompts, greedy and sampled, 192 new-token cap, seed 42. The model learned recognizable prose, dialogue and endings, but frequently repeats, substitutes characters or loses the opening problem. Examples include a forgotten red ball, Eli becoming Lily, repeated apple accusations and a boat hole never repaired. These are provisional assistant observations, not independent human scoring or a train-disjoint benchmark. Loss alone does not demonstrate reliable story quality.

## 50M bounded calibration

Every candidate used the same initial weights SHA `8990e1a7cbc8859f916238fce7fb31272e5b35aced1e5e00c10d2b340ab73ab7`, prepared data, seed, full schedule, and 4,096 targets/update. Each stopped at 256 updates / 1,048,576 targets. Throughput uses updates 17–256; optimizer/reporting seconds below cover all 256 updates.

| Candidate | Steady targets/s | Peak reserved GiB | Optimizer seconds | Reporting seconds |
| --- | ---: | ---: | ---: | ---: |
| baseline-fp32-mb4-ga4 | 10,616 | 1.65 | 98.77 | 9.67 |
| 50m-fp32-mb8-ga2 | 11,150 | 2.28 | 94.08 | 4.34 |
| 50m-fp32-mb16-ga1 | 10,949 | 3.36 | 95.81 | 9.97 |
| 50m-bf16-mb8-ga2 | 46,203 | 2.18 | 23.11 | 9.21 |
| 50m-fp32-sdpa-mb8-ga2 | 11,140 | 2.11 | 94.27 | 9.91 |

All candidates had finite logged losses, zero overflow retries, completed native smoke/warmup with full-state reload checks, and verified full-state final checkpoints. These checks establish bounded execution health, not convergence or trajectory equivalence. See [full identities, timings and checks](50m-calibration.json) and [explicit configurations](../../experiments/tinystories/calibration/README.md).

BF16 8 × 2 is the worthwhile next recipe candidate: about 4.35× the original FP32 4 × 4 optimizer throughput, and 4.14× FP32 8 × 2. Larger FP32 batches improve only modestly. FP32 SDPA is effectively unchanged in this measurement; do not infer its underlying kernel dispatch. BF16 and SDPA together were not tested. The BF16 8 × 2 validation loss (4.374565) is close to FP32 8 × 2 (4.374460) on the same selection. Validation target counts differ across microbatch sizes; cross-batch loss rankings are invalid.

The original FP32 50M step-256 checkpoint remains unchanged. At this calibration stage no full 50M budget had been launched; the later fresh BF16 completion is recorded below. The measured BF16 rate suggests about 6 hours of optimizer work for the billion-target budget; reporting, checkpoints and other costs remain additional and must be remeasured over longer operation. One sequential measurement per candidate does not establish a confidence interval. Native driver allocation, GPU utilization and data-loader stall counters were unavailable.

Remote/Colab handoffs and cross-machine replication remain unvalidated. No Devmind work was resumed.

## Reviewed reporting fix: same-configuration host comparison

A separate BF16 8 × 2 calibration used Lab `6c31d7f9be516f2adc3ed92849bf4e8057a9169e` (PR 288) through an isolated checkout and process-local source selection. No runtime install, registry edit or host patch was performed. The configuration, initial weights and training/validation array hashes match the earlier candidate exactly.

| Measured phase | Before (`b3a1630`) | After (`6c31d7f`) |
| --- | ---: | ---: |
| Reporting | 9.206 s | 5.472 s |
| Optimizer updates | 23.115 s | 22.792 s |
| Full command | 57.980 s | 52.986 s |
| Steady targets/s | 46,203 | 46,599 |

Reporting decreased about 41% and command time about 9% in this single pair. Final validation loss was identical (4.374564543366432), with zero overflow retries and a verified full-state checkpoint. This does not attribute or eliminate all 871 seconds observed during the longer 5M run. See [exact comparison evidence](reporting-comparison.json).

The first new-pin stage correctly refused the old executable-bound input bundle. Republishing through the public command unexpectedly retokenized into a new packed cache (about 122 seconds preparation, 127 seconds publication), despite unchanged corpus and tokenizer. Both output arrays have exactly the original hashes. The original cache remained intact. This is a failed reuse expectation, not a successful reuse claim, and is excluded from training-phase timings.

The interval also includes PR 286, which changes `data/sources.py`. The preparation fingerprint includes all `data/*.py` and `config/models.py`; PR 288's reporting-only files do not themselves enter that fingerprint. This explains why the acquisition change invalidated the existing prepared-cache identity. Generic compatibility needs an explicit verified contract; no identity bypass or ad hoc cache rewrite was applied.

## Fresh 50M BF16 completion and generation

The [explicit BF16 recipe](../../experiments/tinystories/run-50m-bf16.json), published at Workshop `7aa2d54d3fc5beead7e80f158fc3b2a9e3366277`, completed on reviewed Lab `903ad2f0bb261935132dee53295aba6b66f8e792`. This was fresh seed-42 initialization, not a continuation of FP32 or calibration weights. The 50,556,800-parameter model used reference attention, BF16, microbatch 8, accumulation 2 and sequence length 256. Snapshot and tokenizer were reused; the new Lab pin required one fresh packing, whose token arrays matched the existing bytes.

Exactly 244,141 applied updates committed 1,000,001,536 targets across three segments, with no gaps or duplicates. After the initial 256 updates, full state was restored; an orderly SIGTERM stopped the next segment at step 543, and another exact restore continued to the original horizon. Optimizer tensors, RNG, cursor, schedule and counters matched at both boundaries. This does not establish equivalence to an independently trained uninterrupted trajectory.

The final full-state checkpoint verified successfully: `c72d7d0283de2c6008f1b80d855bad6cb6ebc497f0094957a8982bd58a049110`. Final held-out loss was 1.075294 (perplexity 2.930855); best loss was 1.074736 at step 240,640. Evaluation covers 65,536 targets, versus 32,768 for 5M: these are different protocols, so do not rank their losses as matched quality. See [complete sanitized receipt](50m-bf16-completion.json).

Training commands totaled 9h 14m 43s, averaging 30,046 targets/s including overhead. Optimizer work averaged 45,362 targets/s and took 22,045 seconds; reporting took 6,861 seconds and checkpoints 2,845 seconds. The full run therefore still exposes substantial reporting cost despite the earlier bounded improvement. Peak reserved VRAM was 2.18 GiB, with zero overflow retries and observed swap. Native driver utilization and loader-starvation counters were unavailable. Preparation/staging and later generation are excluded from training command time.

The [matching 24-output panel](generation-panel-50m.json) uses the final checkpoint, the same 12 prompts in greedy and sampled modes, seed 42 and a 192-new-token cap. All commands succeeded and every output is retained. Simple red-ball, bird-rescue and apple-sharing continuations preserve details lost in the 5M panel; Eli also keeps his name. Failures remain: Noah becomes Mah, the boat hole and power outage can go unresolved, the absent neighbor reappears, and repetition or arbitrary conflicts persist. These are provisional assistant observations, not independent scoring or a train-disjoint benchmark. Model size, training budget, precision, schedule and source pin differ, so this is not a controlled parameter-count comparison. No reliable-quality or remote/Colab portability claim is made.

## Public evidence representation

This review copy replaces local filesystem paths, interpreter paths and runtime registry identifiers with placeholders. It omits unnecessary machine-specific fields and exact wall-clock timestamps. Command arrays are templates. Native configuration, source and checkpoint hashes retain their original meaning; they are not hashes of the sanitized excerpts. Hardware class, software versions, model settings, measurements, limitations and all 48 generated texts across the two panels are retained. The full native receipts and binaries remain private.
