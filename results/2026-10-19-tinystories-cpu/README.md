# Recorded TinyStories CPU learning baseline

The native workflow completed 8,192 updates / 33,554,432 targets and produced verified checkpoints and actual continuations. The owner accepted publishing this as a baseline to learn from. **The original story-quality gate failed:** provisional assistant scoring found 2/24 passing outputs (required 20), 1/12 held-out outputs (required 10), and 17/24 endings (required 18). No claim of human quality clearance is made. Part 2 improvement work is backlog only.

- [Full review and all 27 unedited prompt/response pairs](review.md)
- [Result, source/runtime pins and timing](summary.json)
- [All per-output scores](quality-assessment.json), [generation timings](generation-metrics.json), [loss trajectory](loss-trajectory.csv)
- [Executed native argv and outcomes](commands.json)
- [Recorded configuration](resolved-config.json), [retained closure inventory](run-closure-index.json)
- [Public native walkthrough](../../examples/tinystories-useful/README.md)

`outputs/final-greedy-1.json` through `final-greedy-12.json` and `final-sampled-1.json` through `final-sampled-12.json` are the complete fixed 192-token panel. `outputs/website-baseline-1.json` through `website-baseline-3.json` contain the separate 48-token website baselines, excluded from scoring. No output was selected away, resampled or rewritten.

Each output remains a `format: raw` native envelope usable by the website importer. Only `identity.config.logging.root_dir` is replaced by `${RUNS}`; `_publication` discloses the edit and original file SHA256. Original hashes authenticate retained originals, not these sanitized derivatives. The viewer displays provenance; it does not verify checkpoint bytes. `manifest.json` hashes the public files.

Weights, training state, tokenizer and prepared arrays remain retained locally and are **not distributed here**. The closure inventory is evidence, not a downloadable model. A fresh reproduction creates its own run/checkpoint identity and must verify its own bytes. The actual checkpoint is `step_00008192_gen_000028`, SHA256 `d5ba0e06c91d7a864264c5af411ced1c1b1c4e136632d71cd0a7b4309a728149`.

Training used Linux/WSL2 CPU FP32, Python 3.14.4, Torch 2.14.1+cpu, an eight-CPU quota and an offline pinned container. Final continuation took 9,895.28 seconds; successful trainer lineage took 11,861.47 seconds. All 27 inference processes took 89.64 seconds total, including startup/loading/verification. Peak sampled RSS was 929.14 MiB for continuation and 429.29 MiB for inference. The 16 GiB RSS and 20 GiB retained-storage thresholds were observations/stop policies, not hard caps. All 35 final-session jobs completed with exit zero, complete evidence and verified cleanup; no training job remains active.

Earlier acquisition/lease/path/selector failures and a host crash remain part of the history. The first acquisition encountered a descriptor leak fixed in the pinned Lab image; a first trainer crashed before update 1,024 and its uncheckpointed updates were not resumed. Later read-only-parent and stale-path attempts refused. `--checkpoint latest` failed; the supported pointer is `latest.json`. One config validation omitted required `--kind run` and failed. A successful 1,024-update run was resumed, deliberately paused at 1,406 with full state, then continued to 8,192 in a fresh session. Retries were explicit new jobs, not automatic recovery or erased history.
