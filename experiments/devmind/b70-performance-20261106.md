# DevMind B70 performance follow-up — 2026-11-06

A short operator-observed A/B/A comparison tested padding multiples of 128 versus 64 while keeping the training state, data and effective target groups fixed. All three arms completed and their full optimizer/RNG checkpoints passed cold CPU reload. Production resumed after the test.

Padding 64 improved the fixed steady update window by approximately 1.4–1.5% against both baselines. The whole-training improvement against the warm repeated baseline was only 0.57%. Cache warming explains much of the larger comparison with the initial cold baseline. Loss differences were comparable to baseline-repeat numerical variation. Production remains on padding 128 pending a longer paired confirmation; no quality improvement or large speedup is claimed.

A separate XPU capture showed fused attention and compiled loss execution. Host waits inside embedding backward warrant further investigation, but most of that wait overlapped useful GPU work and cannot be counted as recoverable elapsed time. [Intel PR #5725](https://github.com/intel/torch-xpu-ops/pull/5725) removes host segment-count dependencies in the dense embedding-backward helper, following [PyTorch CUDA PR #70943](https://github.com/pytorch/pytorch/pull/70943). An isolated runtime comparison must establish numerical behavior, dense Adam semantics, peak scratch memory and end-to-end throughput before adoption. No runtime upgrade has been deployed.

The trace branch was interrupted safely after profiler aggregation exceeded its host-memory allowance. The captured update remained analyzable using bounded offline streaming. Future captures should export only while holding the GPU lease, aggregate offline, and stop at the intended native checkpoint boundary. Traced timing is excluded from the speed comparison.

The detailed experiment record and large artifacts remain with the operator. This summary does not publish checkpoints, corpus content, internal paths or private run identifiers. Ongoing fresh-data preparation and sequential training continue independently of this performance investigation.
