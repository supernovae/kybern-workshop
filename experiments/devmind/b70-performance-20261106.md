# DevMind B70 performance follow-up — 2026-11-06

A short operator-observed A/B/A comparison tested padding multiples of 128 versus 64 while keeping the training state, data and effective target groups fixed. All three arms completed and their full optimizer/RNG checkpoints passed cold CPU reload. Production resumed after the test.

Padding 64 improved the fixed steady update window by approximately 1.4–1.5% against both baselines. The whole-training improvement against the warm repeated baseline was only 0.57%. Cache warming explains much of the larger comparison with the initial cold baseline. Loss differences were comparable to baseline-repeat numerical variation. Production remains on padding 128 pending a longer paired confirmation; no quality improvement or large speedup is claimed.

A separate XPU capture showed fused attention and compiled loss execution. Host waits inside embedding backward warrant further investigation, but most of that wait overlapped useful GPU work and cannot be counted as recoverable elapsed time. [Intel PR #5725](https://github.com/intel/torch-xpu-ops/pull/5725) removes host segment-count dependencies in the dense embedding-backward helper, following [PyTorch CUDA PR #70943](https://github.com/pytorch/pytorch/pull/70943). An isolated runtime comparison must establish numerical behavior, dense Adam semantics, peak scratch memory and end-to-end throughput before adoption. No runtime upgrade has been deployed.

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

Independent review recommends a planned finite 100M-target nightly validation, not yet started, with an early fresh-process GPU resume from a nightly-written checkpoint and the old runtime available as fallback. That GPU resume and long-run learning behavior remain unverified at this report's publication; no permanent runtime promotion is claimed.

## Remaining experiments and reusable improvements

- Broader forward/loss compilation captures token and Engram lookups in CPU checks, but source inspection indicates XPU embedding backward still lowers to the native fallback. Its numerical behavior, memory and speed need a separate GPU comparison.
- Padding-index changes require care: this path fills with EOS, also a legitimate learned token. SparseAdam changes untouched-row moment/update semantics and belongs in a separate learning experiment or v2, not an equivalent optimizer switch.
- [Lab PR334](https://github.com/supernovae/tiny-sparse-lab/pull/334) merged verified prepared-prefix reuse after independent review and passing CI, reducing repeated preparation work. Retention PR333 remains open with a failing check; it is not presented as merged.

These are aggregate operator-observed findings. Detailed local evidence and failed artifacts are retained without publishing corpus content, checkpoints, private identifiers or filesystem paths.
