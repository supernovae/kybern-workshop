# 50M performance calibration

These fresh calibration identities derive from the 50M recipe at Workshop `e186e42194bd69f2fb68318a79c51c9bbcc4e7c7`, using Lab `b3a1630ec09dbddae36301b0acef4122623ed939`. They preserve seed 42, architecture, data, optimizer schedule and the full horizon. Every configuration uses 4,096 targets per update.

| Configuration | Precision | Microbatch × accumulation | Attention |
| --- | --- | --- | --- |
| `50m-fp32-mb8-ga2.json` | FP32 | 8 × 2 | reference |
| `50m-fp32-mb16-ga1.json` | FP32 | 16 × 1 | reference |
| `50m-bf16-mb8-ga2.json` | BF16 | 8 × 2 | reference |
| `50m-fp32-sdpa-mb8-ga2.json` | FP32 | 8 × 2 | SDPA |

Bind paths with native `config derive`, publish a configuration-specific prepared-input bundle, stage through warmup, then train with `--stop-after-step 256`. Compare updates 17 through 256; record startup and full-command times separately. The native smoke and warmup pilots are disposable and excluded from calibration exposure. These 256-update segments are calibration only, not continuation or completion of the original scientific run.

Do not resume the original checkpoint using these changed configurations. Different floating-point reduction orders and precision do not establish trajectory equivalence. Preserve the original 50M step-256 checkpoint and budget. BF16 and SDPA are tested separately against FP32 8 × 2; their combination is untested. A full run of an alternative requires an explicit new scientific identity.

The default validation protocol uses 32 batches, so microbatch 4/8/16 evaluates 32,768/65,536/131,072 targets. Compare validation losses only within the same selection; these measurements do not establish a quality ranking across batch sizes.

See [measured results](../../../results/2026-10-31-tinystories-rocm/README.md), including a separately identified same-configuration reporting-fix comparison. No configuration here replaces `../run-50m.json`.
