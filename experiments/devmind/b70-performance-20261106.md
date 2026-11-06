# DevMind B70 performance follow-up — 2026-11-06

A short operator-observed A/B/A comparison tested padding multiples of 128 versus 64 while keeping the training state, data and effective target groups fixed. All three arms completed and their full optimizer/RNG checkpoints passed cold CPU reload. Production resumed after the test.

Padding 64 improved the fixed steady update window by approximately 1.4–1.5% against both baselines. The whole-training improvement against the warm repeated baseline was only 0.57%. Cache warming explains much of the larger comparison with the initial cold baseline. Loss differences were comparable to baseline-repeat numerical variation. Production remains on padding 128 pending a longer paired confirmation; no quality improvement or large speedup is claimed.

A separate XPU capture showed fused attention and compiled loss execution. Host waits inside embedding backward warrant further investigation, but most of that wait overlapped useful GPU work and cannot be counted as recoverable elapsed time. [Intel PR #5725](https://github.com/intel/torch-xpu-ops/pull/5725) removes host segment-count dependencies in the dense embedding-backward helper, following [PyTorch CUDA PR #70943](https://github.com/pytorch/pytorch/pull/70943). An isolated runtime comparison must establish numerical behavior, dense Adam semantics, peak scratch memory and end-to-end throughput before adoption. At that initial investigation, no runtime upgrade had been deployed; the later finite nightly validation is reported below.

The trace branch was interrupted safely after profiler aggregation exceeded its host-memory allowance. The captured update remained analyzable using bounded offline streaming. Future captures should export only while holding the GPU lease, aggregate offline, and stop at the intended native checkpoint boundary. Traced timing is excluded from the speed comparison.

The detailed experiment record and large artifacts remain with the operator. This summary does not publish checkpoints, corpus content, internal paths or private run identifiers. Ongoing fresh-data preparation and sequential training continue independently of this performance investigation.

## Isolated nightly runtime comparison

A subsequent old/nightly/old comparison tested official PyTorch `2.16.0.dev20261105+xpu` against `2.15.0+xpu`. The candidate [PyTorch revision](https://github.com/pytorch/pytorch/commit/084f8661f5bb5de149860f74d82f5313766f4256) pins XPU operations to [bd009050](https://github.com/intel/torch-xpu-ops/commit/bd00905057982d19369a9a558f2b41eff6de8da4), which includes PR5725. No local PyTorch source build was needed. The nightly also changes other components, so this comparison does not isolate that patch's causal contribution.

Each arm applied the same 15 updates and approximately 1.98M supervised targets from identical full state and data, with matching target counts and microbatch shapes. Existing block/head compilation, 4K sequences, microbatch at most four, 131072-target grouping policy and dense AdamW settings stayed fixed.

| Arm | Steady valid targets/s, updates 9–15 | Native training wall seconds |
|---|---:|---:|
| Old A1 | 19,795.70 | 173.921 |
| Nightly B | 22,656.82 | 160.498 |
| Old A2 | 19,796.84 | 154.270 |

The nightly's steady advantage is about **14.45% against both old-runtime arms**. Independent review recomputed alternative windows and found consistent gains. Whole-call wall throughput was 8.36% higher than cold A1 and 3.88% lower than cache-warm A2. Startup, compilation, validation and saves are included in that wall measurement; separate diagnostic passes are excluded. This short comparison does not establish an unqualified whole-run gain.

Nightly peak allocation/reservation was 14.32/15.18 GiB, comparable to the baselines. Loss and final parameter differences were within the observed old-versus-old variation. All three terminal model/Adam/RNG/cursor/scheduler states passed native cold CPU reload. Separate synchronized backward diagnostics measured median whole backward near 205 ms on nightly versus 253 ms on old. Operation event durations and enclosing host waits overlap and must not be added.

Every arm explicitly called `torch.use_deterministic_algorithms(False)`. Global and Inductor deterministic flags were already false before the call; compiler batch-invariant mode was also false. The historical attention gain from switching math SDPA to flash is already incorporated. The old embedding helper's deterministic name does not indicate that the global flag was accidentally enabled.

The old runtime failed an additional empty-input embedding backward case; the nightly passed it, repeated-index and padding cases. Production uses nonempty lookups. The failed attempt and successful recovery evidence were retained, and the production trainer resumed on its known-good runtime, applied updates and saved a verified post-update checkpoint.

## Completed finite 100M-target nightly validation

The recommended nightly validation has now completed **100,003,922 fresh valid targets across 759 applied optimizer updates**. After eight updates, the trainer saved full state, exited cleanly, and resumed from that nightly-written checkpoint in a fresh GPU process. The resumed process completed the remaining 751 updates and exited successfully. Terminal model, Adam, RNG, cursor and scheduler state passed native cold CPU verification. The established training configuration and learning-rate floor were preserved.

| Measurement boundary | Fresh valid targets/s | Wall duration |
|---|---:|---:|
| Initial launch-request publication through final cold-verification receipt | 20,992.33 | 4,763.83 s |
| Final sustained window, including checkpoint/evaluation pauses | 21,704.56 | 603.14 s |
| Longer final sustained window, including checkpoint/evaluation pauses | 21,957.27 | 1,203.23 s |

The whole-phase envelope includes initial startup, the early save/exit/cold-load/fresh restart, resumed training, validation, saves, exit and final verification. Its starting timestamp is the recorded launch-request publication immediately before process launch, not an independently recorded OS process-start time. The shorter steady wall windows exclude that initial startup and restart; they are not optimizer-only rates. These are measurements of this continuation, not a matched long-run speedup against the old runtime.

Recorded training losses remained finite, and recorded optimizer overflow retries were zero. Validation loss changed from approximately 2.5838 at entry to **2.5825** at completion, with intermediate fluctuations. This is descriptive health evidence, not proof of learning equivalence, improved quality or runtime superiority. Allocator counters are not a measurement of total physical driver residency.

The old runtime remains available as fallback and was not needed during this validation. Fresh-process GPU resume and terminal cold full-state reload are now demonstrated for this finite nightly continuation. **100M targets do not establish stability over billions of targets**; continued monitoring and further training evidence remain necessary. No permanent runtime promotion or subsequent segment outcome is claimed here.

## Campaign progress through 2.516B+ Engram targets (160M active continuation)

Subsequent finite continuations on the same nightly runtime (`2.16.0.dev20261105+xpu`) completed through optimizer step **31,476** (`2,436,319,171` Engram targets), and the active **160,002,769-target continuation (`devmind-engram-after7m-160m-131k-nvme-20261106-v1`, step 31,476 $\to$ 32,689 / `2,596,321,940` Engram targets)** has passed **step 32,083 / 2,516,383,537 Engram targets** (`4,596,758,321` combined exposure targets including the `2,080,374,784` inherited dense-backbone targets):

| Milestone / Segment | Cumulative Engram targets | Step | Validation loss | End-to-end valid targets/s | Optimizer-only valid targets/s |
|---|---:|---:|---:|---:|---:|
| First 100M nightly validation | 1,715,287,502 | 26,005 | 2.5825059 | — | — |
| Following 200M continuation | 1,915,291,338 | 27,522 | 2.5787988 | — | — |
| Pre-reboot 25M continuation | 2,415,309,520 | 31,315 | 2.5706154 | 19,396.0 | 21,765.0 |
| Post-reboot 14M continuation | 2,429,314,666 | 31,422 | 2.5700909 | 18,948.0 | 21,511.0 |
| Subsequent 7M bridge continuation | 2,436,319,171 | 31,476 | 2.5687491 | 19,312.4 | 21,887.7 |
| **Active 160M continuation (at +80.1M)** | **2,516,383,537** | **32,083** | **2.5684862** (step 31,600) | **20,254.9 (+6.9%)** | **21,626.8** (16 CPU cores busy) |

Every segment bound to its predecessor's cold-verified CPU full-state checkpoint, preserved model/Adam/RNG/cursor/schedule state and the `1e-5` learning-rate floor (`5e-5` memory-table floor), and verified bit-exact initial state before applying updates.
## Vectorized Engram diagnostics and padding A/B/A comparison

A follow-up operator-observed A/B/A comparison on the B70 XPU (4 steady updates / 532,612 valid targets per arm after warmup, starting from the verified step 31,422 state) evaluated vectorizing `TokenNgramMemory` multi-stream diagnostics and reusing shifted input slices ([Tiny Sparse Lab PR #335](https://github.com/supernovae/tiny-sparse-lab/pull/335)), reducing per-microbatch `/proc` host-memory syscalls during native device peak tracking, and combining those changes with `padding_multiple=64` and `padding_multiple=32`:

| Arm | Steady valid targets/s | Steady wall seconds | Gain vs mean baseline | Max loss difference vs A1 |
|---|---:|---:|---:|---:|
| A1: baseline (`padding_multiple=128`) | 21,561.51 | 24.7020 | — | 0.0 |
| B1: vectorized Engram + light monitor (`pad128`) | **21,840.27** | 24.3867 | **+1.64%** | $4.61 \times 10^{-5}$ |
| B2: vectorized Engram + light monitor (`pad64`) | **22,171.84** | 24.0220 | **+3.18%** | $3.23 \times 10^{-5}$ |
| B3: vectorized Engram + light monitor (`pad32`) | 22,075.48 | 24.1269 | +2.73% | $1.00 \times 10^{-5}$ |
| A2: baseline repeat (`padding_multiple=128`) | 21,416.08 | 24.8697 | — | $6.30 \times 10^{-5}$ |

Key findings and negative results:

- **Vectorized multi-stream Engram diagnostics ([PR #335](https://github.com/supernovae/tiny-sparse-lab/pull/335)):** Previously, `TokenNgramMemory` recomputed shifted token slices per `(order, head)` stream and launched separate per-stream `torch.bincount`, `.norm(dim=-1)`, `gate.mean()`, and `hidden.norm(dim=-1)` reductions at each Engram site. Precomputing shifted slices once up to `max(ngram_orders)` and batching all streams into a single `[num_streams, table_size]` `bincount` and batched norm reduction preserves exact forward outputs, gradients, and diagnostic tensors while improving steady throughput at unchanged `padding_multiple=128` by **+1.64%**.
- **Padding granularity (`64` vs `128` vs `32`):** Combining the vectorized Engram path with `padding_multiple=64` reached **22,171.84 valid targets/s (+3.18%)** even while 16 host CPU cores were concurrently executing corpus screening. `padding_multiple=64` outperformed `padding_multiple=32` (`22,075.48` targets/s), consistent with 64-token alignment matching B70 XMX systolic/FlashAttention tile sizes while avoiding excessive shape buckets.
- **Negative results retained:**
  - Compiling `F.conv1d(..., groups=hidden.shape[-1])` inside a standalone helper across variable microbatch sequence lengths hit Dynamo's `recompile_limit (8)` due to shape guards on the depthwise convolution input.
  - Enabling `AdamW(foreach=True)` on XPU across the model's heterogeneous parameter groups measured slightly slower (`21,652.81` vs `21,799.14` targets/s in an earlier 3-update screen) than `foreach=False`.
- **Production deployment in the 160M run & checkpoint cadence optimization:**
  - Deploying the vectorized Engram diagnostics + light `MemoryMonitor` path (`B1`, keeping `padding_multiple=128` for exact microbatch-group prefix parity) increased end-to-end valid-target throughput in the active 160M run to **20,254.9 valid targets/s (+6.9% over the 14M run)** and sustained **21,626.8 optimizer-only valid targets/s** (`21,117.8–21,348.4 /s` across recent 5M spans) even while 16 host CPU cores concurrently executed 41-pool SQLite/MinHash qualification across `FineMath`, `Jupyter`, `OpenCodeInstruct`, `FineWeb-Edu`, and `Tulu-3` shards.
  - Stage-timing inspection of the 160M run showed that `checkpoint.every_tokens = 5,000,000` (~every 38 steps / 4 minutes) pauses training for `~6.5–9.0 seconds` per save+cold-verification (`~3.5%` wall-clock overhead). Increasing `checkpoint.every_tokens` to `25,000,000` in the pre-staged 95M successor (`after-160m-95m-append-4k-v1`) eliminates 80% of periodic checkpoint pauses (`+2.8%` end-to-end wall-clock gain) while retaining milestone and recovery saves.

## Remaining experiments and reusable improvements

- Broader forward/loss compilation captures token and Engram lookups in CPU checks, but source inspection indicates XPU embedding backward still lowers to the native fallback. Its numerical behavior, memory and speed need a separate GPU comparison.
- Padding-index changes require care: this path fills with EOS, also a legitimate learned token. SparseAdam changes untouched-row moment/update semantics and belongs in a separate learning experiment or v2, not an equivalent optimizer switch.
- [Lab PR #335](https://github.com/supernovae/tiny-sparse-lab/pull/335) (all CI checks passing) contributes the vectorized multi-stream `TokenNgramMemory` diagnostics and shared shifted-input buffers upstream. [Lab PR #334](https://github.com/supernovae/tiny-sparse-lab/pull/334) merged verified prepared-prefix reuse, and [Retention PR #333](https://github.com/supernovae/tiny-sparse-lab/pull/333) merged retention-policy preservation during budget-extension comparisons.

These are aggregate operator-observed findings. Detailed local evidence and failed artifacts are retained without publishing corpus content, checkpoints, private identifiers or filesystem paths.
