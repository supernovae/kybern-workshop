# 50M performance calibration

These calibration configs are new runs built from the 50M recipe at Workshop `e186e42194bd69f2fb68318a79c51c9bbcc4e7c7`, using Lab `b3a1630ec09dbddae36301b0acef4122623ed939`. They keep seed 42, the architecture, data, optimizer schedule and full horizon. Every config uses 4,096 targets per update.

| Configuration | Precision | Microbatch × accumulation | Attention |
| --- | --- | --- | --- |
| `50m-fp32-mb8-ga2.json` | FP32 | 8 × 2 | reference |
| `50m-fp32-mb16-ga1.json` | FP32 | 16 × 1 | reference |
| `50m-bf16-mb8-ga2.json` | BF16 | 8 × 2 | reference |
| `50m-fp32-sdpa-mb8-ga2.json` | FP32 | 8 × 2 | SDPA |

Set paths with native `config derive`, publish a prepared-input bundle for each config, stage through warmup, then train with `--stop-after-step 256`. Compare updates 17 through 256, and record startup and whole-command times separately. The native smoke and warmup pilots are throwaway and don't count toward calibration exposure. These 256-update segments only measure speed and memory; they don't continue or complete the original training run.

Don't resume the original checkpoint with these changed configs: different precision and floating-point reduction order would put it on a different trajectory. Keep the original 50M step-256 checkpoint and budget. BF16 and SDPA were each tested against FP32 8 × 2 on their own, not together. A later [BF16 context-512 attention comparison](../context/rocm-attention-performance.json) on Lab `903ad2f0bb261935132dee53295aba6b66f8e792` tests the two together. To run any of these alternatives in full, set it up as a new, separately named run.

Validation uses 32 batches by default, so microbatch 4/8/16 evaluates 32,768/65,536/131,072 targets. Compare validation losses only on the same selection, which rules out ranking quality across batch sizes.

See the [measured results](../../../results/2026-10-31-tinystories-rocm/README.md), which also include a separate same-config comparison of a reporting fix. `../run-50m.json` remains the 50M recipe; these configs sit alongside it.
