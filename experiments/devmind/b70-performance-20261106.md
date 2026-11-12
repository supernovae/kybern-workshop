# DevMind B70 performance follow-up — 2026-11-06

This page collects dated performance measurements from the DevMind Engram run. For the current state, see the dual-B70 section at the end and the [campaign record](engram-campaign-20261106.md). These are observations from a run in progress. The early padding, nightly-runtime and vectorization comparisons don't record the exact Lab revision they ran on, so they can't be rerun exactly; don't fill that gap with the later prepared-append pin.

We ran a short A/B/A comparison of padding multiples 128 and 64, with the training state, data and target groups held fixed. All three arms finished, and their full optimizer and RNG checkpoints reloaded cleanly on CPU. Production training resumed afterwards.

Padding 64 sped up the fixed steady update window by about 1.4–1.5% against both baseline arms. Over the whole training call, the gain against the warm repeated baseline was only 0.57%; cache warming accounts for much of the bigger gap against the first, cold baseline. Loss differences were about the size of the variation between the two baseline runs. Production stays on padding 128 until a longer paired run confirms the gain.

A separate XPU trace showed fused attention and compiled loss running as expected. Embedding backward has host waits worth looking into, but most of that wait overlapped useful GPU work, so it isn't time we could simply win back. [Intel PR #5725](https://github.com/intel/torch-xpu-ops/pull/5725) removes the host segment-count dependency in the dense embedding-backward helper, following [PyTorch CUDA PR #70943](https://github.com/pytorch/pytorch/pull/70943). Before adopting it, an isolated runtime comparison has to check numerical behavior, dense Adam semantics, peak scratch memory and end-to-end throughput. When we first looked, no runtime upgrade had been deployed; the nightly validation below came later.

We stopped the trace run safely when profiler aggregation went over its host-memory allowance. The captured update could still be analyzed by streaming it offline. Next time, export the trace only while holding the GPU lease, aggregate offline, and stop at the planned checkpoint boundary. Traced timings are left out of the speed comparison.

The detailed records and large artifacts stay with the operator; this summary includes no checkpoint binaries or corpus content. Later sections repeat run IDs, device IDs and storage paths already in the record. Fresh-data preparation and sequential training kept running alongside this investigation.

## Isolated nightly runtime comparison

Next we ran an old/nightly/old comparison of official PyTorch `2.16.0.dev20261105+xpu` against `2.15.0+xpu`. The candidate [PyTorch revision](https://github.com/pytorch/pytorch/commit/084f8661f5bb5de149860f74d82f5313766f4256) pins XPU operations to [bd009050](https://github.com/intel/torch-xpu-ops/commit/bd00905057982d19369a9a558f2b41eff6de8da4), which includes PR5725, so we didn't need a local PyTorch build. The nightly changes other components too, so this comparison can't single out that patch's effect.

Each arm started from the same full state and data and applied the same 15 updates, about 1.98M supervised targets, with matching target counts and microbatch shapes. Everything else stayed fixed: block and head compilation, 4K sequences, at most four documents per microbatch, 131072-target grouping and the dense AdamW settings.

| Arm | Steady valid targets/s, updates 9–15 | Native training wall seconds |
|---|---:|---:|
| Old A1 | 19,795.70 | 173.921 |
| Nightly B | 22,656.82 | 160.498 |
| Old A2 | 19,796.84 | 154.270 |

In the steady window the nightly was about **14.45% faster than both old-runtime arms**. An independent review recomputed other windows and found the same gain. Whole-call wall throughput was 8.36% higher than the cold A1 run and 3.88% lower than the cache-warm A2 run. That wall figure includes startup, compilation, validation and saves, but not the separate diagnostic passes. A run this short doesn't tell us the gain over a whole training run.

Nightly peak allocation/reservation was 14.32/15.18 GiB, close to the baselines. Loss and final-parameter differences were within the variation between the two old-runtime runs. All three final model/Adam/RNG/cursor/scheduler states reloaded cleanly on CPU. Separate synchronized diagnostics put median whole backward at about 205 ms on nightly versus 253 ms on old. Operation event durations overlap with the host waits around them, so don't add them together.

Every arm called `torch.use_deterministic_algorithms(False)`. The global and Inductor deterministic flags were already false before that call, and compiler batch-invariant mode was off. The earlier attention gain from switching math SDPA to flash is already included. The old embedding helper has "deterministic" in its name, but that doesn't mean the global flag was on.

The old runtime failed one extra test, an empty-input embedding backward; the nightly passed it along with the repeated-index and padding cases. Production never does empty lookups. We kept the records of the failed attempt and the recovery. The production trainer then resumed on its known-good runtime, applied updates and saved a checked post-update checkpoint.

## Completed finite 100M-target nightly validation

The recommended nightly validation finished **100,003,922 fresh valid targets across 759 applied optimizer updates**. After eight updates, the trainer saved full state, exited cleanly, and resumed from that checkpoint in a fresh GPU process. The resumed process ran the remaining 751 updates and exited successfully. The final model, Adam, RNG, cursor and scheduler state passed a cold CPU check. The training config and learning-rate floor stayed the same.

| Measurement boundary | Fresh valid targets/s | Wall duration |
|---|---:|---:|
| Initial launch-request publication through final cold-verification receipt | 20,992.33 | 4,763.83 s |
| Final sustained window, including checkpoint/evaluation pauses | 21,704.56 | 603.14 s |
| Longer final sustained window, including checkpoint/evaluation pauses | 21,957.27 | 1,203.23 s |

The whole-phase figure covers everything: startup, the early save, exit, cold load and restart, resumed training, validation, saves, exit and the final check. Its start time is when the launch request was recorded, just before the process launched, rather than an OS process-start time. The shorter steady windows leave out startup and the restart, but they still include checkpoint and evaluation pauses, so they aren't optimizer-only rates. These numbers describe this run; they aren't a matched long-run comparison with the old runtime.

Training losses stayed finite and there were no optimizer overflow retries. Validation loss went from about 2.5838 at the start to **2.5825** at the end, with some ups and downs in between. Allocator counters don't measure total physical driver memory.

We kept the old runtime as a fallback and didn't need it. This run shows that GPU resume in a fresh process and a cold full-state reload at the end both work on the nightly. It covers 100M targets; stability over billions of targets still has to be watched as training continues.

## Historical campaign snapshot through 2.516B+ Engram targets (November 6)

Later finite continuations on the same nightly runtime (`2.16.0.dev20261105+xpu`) finished through optimizer step **31,476** (`2,436,319,171` Engram targets). The active **160,002,769-target continuation (`devmind-engram-after7m-160m-131k-nvme-20261106-v1`, step 31,476 $\to$ 32,689 / `2,596,321,940` Engram targets)** had passed **step 32,083 / 2,516,383,537 Engram targets**. With the `2,080,374,784` inherited dense-backbone targets, that is `4,596,758,321` combined.

| Milestone / Segment | Cumulative Engram targets | Step | Validation loss | End-to-end valid targets/s | Optimizer-only valid targets/s |
|---|---:|---:|---:|---:|---:|
| First 100M nightly validation | 1,715,287,502 | 26,005 | 2.5825059 | — | — |
| Following 200M continuation | 1,915,291,338 | 27,522 | 2.5787988 | — | — |
| Pre-reboot 25M continuation | 2,415,309,520 | 31,315 | 2.5706154 | 19,396.0 | 21,765.0 |
| Post-reboot 14M continuation | 2,429,314,666 | 31,422 | 2.5700909 | 18,948.0 | 21,511.0 |
| Subsequent 7M bridge continuation | 2,436,319,171 | 31,476 | 2.5687491 | 19,312.4 | 21,887.7 |
| **Active 160M continuation (at +80.1M)** | **2,516,383,537** | **32,083** | **2.5684862** (step 31,600) | **20,254.9 (+6.9%)** | **21,626.8** (16 CPU cores busy) |

Every segment started from its predecessor's cold-checked CPU full-state checkpoint. Each carried over the model, Adam, RNG, cursor and schedule state and the `1e-5` learning-rate floor (`5e-5` for the memory table), and confirmed a bit-exact starting state before applying updates.

## Vectorized Engram diagnostics and padding A/B/A comparison

We ran another A/B/A comparison on the B70 XPU, starting from the checked step 31,422 state, with 4 steady updates (532,612 valid targets) per arm after warmup. It tested three changes, alone and together:

- vectorizing the `TokenNgramMemory` multi-stream diagnostics and reusing shifted input slices ([Kybern Model Lab PR #335](https://github.com/supernovae/model-lab/pull/335));
- cutting per-microbatch `/proc` host-memory syscalls while device peak tracking is on;
- `padding_multiple=64` and `padding_multiple=32`.

| Arm | Steady valid targets/s | Steady wall seconds | Gain vs mean baseline | Max loss difference vs A1 |
|---|---:|---:|---:|---:|
| A1: baseline (`padding_multiple=128`) | 21,561.51 | 24.7020 | — | 0.0 |
| B1: vectorized Engram + light monitor (`pad128`) | **21,840.27** | 24.3867 | **+1.64%** | $4.61 \times 10^{-5}$ |
| B2: vectorized Engram + light monitor (`pad64`) | **22,171.84** | 24.0220 | **+3.18%** | $3.23 \times 10^{-5}$ |
| B3: vectorized Engram + light monitor (`pad32`) | 22,075.48 | 24.1269 | +2.73% | $1.00 \times 10^{-5}$ |
| A2: baseline repeat (`padding_multiple=128`) | 21,416.08 | 24.8697 | — | $6.30 \times 10^{-5}$ |

What we found, including what didn't work:

- **Vectorized multi-stream Engram diagnostics ([PR #335](https://github.com/supernovae/model-lab/pull/335)):** `TokenNgramMemory` used to recompute shifted token slices for each `(order, head)` stream and launch separate per-stream `torch.bincount`, `.norm(dim=-1)`, `gate.mean()` and `hidden.norm(dim=-1)` reductions at every Engram site. Now it computes the shifted slices once, up to `max(ngram_orders)`, and batches all streams into one `[num_streams, table_size]` `bincount` and one batched norm. Forward outputs, gradients and diagnostic tensors are exactly the same, and steady throughput at `padding_multiple=128` rose **+1.64%**.
- **Padding granularity (`64` vs `128` vs `32`):** With the vectorized Engram path, `padding_multiple=64` reached **22,171.84 valid targets/s (+3.18%)**, even with 16 host CPU cores busy screening corpus data. It beat `padding_multiple=32` (`22,075.48` targets/s). That fits 64-token alignment matching the B70 XMX systolic and FlashAttention tile sizes without creating too many shape buckets.
- **What didn't work:**
  - Compiling `F.conv1d(..., groups=hidden.shape[-1])` in a standalone helper across variable microbatch sequence lengths hit Dynamo's `recompile_limit (8)`, because of shape guards on the depthwise convolution input.
  - `AdamW(foreach=True)` on XPU, across the model's mixed parameter groups, was slightly slower than `foreach=False` (`21,652.81` vs `21,799.14` targets/s in an earlier 3-update screen).
- **Deployed in the 160M run, plus a checkpoint cadence change:**
  - We deployed the vectorized Engram diagnostics and the lighter `MemoryMonitor` (`B1`), keeping `padding_multiple=128` so microbatch-group prefixes still match exactly. End-to-end throughput in the active 160M run rose to **20,254.9 valid targets/s (+6.9% over the 14M run)**, with **21,626.8 optimizer-only valid targets/s** sustained (`21,117.8–21,348.4 /s` across recent 5M spans). Meanwhile 16 host CPU cores were running 41-pool SQLite/MinHash qualification on `FineMath`, `Jupyter`, `OpenCodeInstruct`, `FineWeb-Edu` and `Tulu-3` shards.
  - Stage timings from the 160M run showed that `checkpoint.every_tokens = 5,000,000` (about every 38 steps, or 4 minutes) paused training for `~6.5–9.0 seconds` per save and cold check, about `~3.5%` of wall-clock time. Raising `checkpoint.every_tokens` to `25,000,000` in the next 95M run (`after-160m-95m-append-4k-v1`) removes 80% of those pauses (`+2.8%` end-to-end wall-clock gain) and still keeps milestone and recovery saves.

## Remaining experiments and reusable improvements

- Broader forward/loss compilation does capture the token and Engram lookups in CPU checks, but the source suggests XPU embedding backward still falls back to the native kernel. Its numerical behavior, memory use and speed need their own GPU comparison.
- Be careful changing the padding index: this path pads with EOS, which is also a real learned token. SparseAdam changes how untouched rows' moments and updates behave, so test it as a separate learning experiment or in v2 rather than treating it as a drop-in optimizer swap.
- [Lab PR #335](https://github.com/supernovae/model-lab/pull/335) (merged) brings the vectorized multi-stream `TokenNgramMemory` diagnostics and shared shifted-input buffers upstream. [Lab PR #334](https://github.com/supernovae/model-lab/pull/334) merged prepared-prefix reuse, and [Retention PR #333](https://github.com/supernovae/model-lab/pull/333) merged keeping the retention policy during budget-extension comparisons.

The detailed local records and failed artifacts are kept, without publishing corpus content or checkpoint binaries.

## Dual Intel Arc Pro B70 (`2x B70`) microbatch-parallel scaling and 96 GB RAM upgrade (2026-11-09)

Segment 11 finished at `step 54,458 / 5,466,370,911` Engram targets, with best validation loss **2.5426250** at step `53,800`. Segment 12 then reached step `54,690` (`5,496,976,964` Engram targets, checkpoint SHA-256 `be152cd1d92792d0c38a238f57b28c105653a4b5cf5bf422fd5dcc8dea768dd4`). At that point we added a **second Intel Arc Pro B70 GPU** (`868023e2-0000-0000-2300-000000000000` at PCI `0000:23:00.0`, `31.89 GiB`, next to `868023e2-0000-0000-e300-000000000000` at PCI `0000:e3:00.0`, `31.89 GiB`) and **96 GB system RAM**.

### Architecture and scientific equivalence invariants

We split the work across both B70 GPUs without changing the pinned `b70-prepared-append` checkout (`93841d0541c45547104991356d450c56ed26bd78`), the `RunConfig`, the update grouping (`131,072` valid targets/update), `allow_runtime_drift=False` or the checkpoint format:

1. **Device affinity and leases on both GPUs:** The main trainer runs with `ZE_AFFINITY_MASK=1`, so its `xpu:0` is physical UUID `868023e2-0000-0000-e300-000000000000`, the same device as every earlier checkpoint and manifest. It takes exclusive `DeviceLease` locks on both physical B70 UUIDs. A long-lived co-worker process runs with `ZE_AFFINITY_MASK=0` (`xpu:0` = `868023e2-0000-0000-2300-000000000000`). Separate processes keep `torch._dynamo` / `torch.compile` state apart while sharing the same on-disk Inductor/Triton/SYCL `cache_scope`.
2. **Interleaved microbatches and exact gradient reduction:** `collate_document_update` sorts documents by length, shortest first, into `~20–45` microbatches per step. `PyTorchEngine._train_update` scales every microbatch loss by the whole update's `valid_targets` (`backward_loss = (ce_sum + auxiliary * chunk_valid) / valid_targets`). So sending `microbatches[0::2]` to GPU 0 and `microbatches[1::2]` to GPU 1 balances sequence lengths across the two. Partial FP32 gradients, loss sums and additive document-scoped Engram diagnostics are summed onto GPU 0, followed by a single `clip_grad_norm_` (`foreach=False`) and `AdamW.step()`. The updated FP32 weights are copied to GPU 1 asynchronously between steps.

### Isolated numerical equivalence and throughput comparison (`1x B70` vs `2x B70`)

We compared one matched 16-microbatch update (`131,072` supervised targets at `seq_len=4096`), from the same model weights and optimizer state, on the pinned nightly runtime (`2.16.0.dev20261105+xpu`):

| Configuration | Step wall seconds | Valid targets/s | Speedup vs 1x B70 | Loss difference | Grad-norm difference | Max parameter difference |
|---|---:|---:|---:|---:|---:|---:|
| 1x B70 (`PyTorchEngine.train_update`) | 6.280 s | 20,873 | 1.000× | — | — | — |
| 2x B70 (`DualB70Coordinator`, cold weight sync) | 3.849 s | 34,054 | **1.632× (+63.2%)** | $0.0$ | $7.99 \times 10^{-6}$ | $9.72 \times 10^{-5}$ |
| 2x B70 (`DualB70Coordinator`, steady preloaded weights) | **3.728 s** | **35,163** | **1.685× (+68.5%)** | $0.0$ | — | — |

### Live production verification (`devmind-engram-after3200m-300m-resume-131k-nvme-20261109-v1`)

- The run resumed from the cold-checked `step_00054690_gen_000003` (`5,496,976,964` Engram targets) and passed a cold check of its starting state (`step_00054690_gen_000001`, SHA-256 `d6d1c585a2675821d16b0ace4387e13d7228643be992e88504bfec65f7b4769c`). It applied step `54,691` and saved a checked full-state checkpoint, **`step_00054700_gen_000002`** (`5,498,297,748` Engram targets, validation loss **2.5446576**, SHA-256 `1fef0d1a0894d8956e348d46d49e9f867cfeab3a4876cfc8f668ae3fefe48e11`).
- Live optimizer throughput reached **34,274.5 valid targets/s (+60.5% over the 1x B70 rate of `21,350.1 /s` before the upgrade)**, while host CPU cores were also running Stage 13 (`225M` target) corpus selection and cross-screening.
