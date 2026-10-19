# TinyStories 8,192-Update Baseline Verification Summary

- **Executed declarations:** Workshop `e70d82b0c3262087ba5b1c546ebfd237f87a685d`
- **Tiny Sparse Lab engine:** `7a517b2c065426748cd99702e82ea377877a7809`
- **Container digest:** `ghcr.io/supernovae/tiny-sparse-lab@sha256:e3356de49998903e5f03ee2cb28a9b33a5270d380d65d1ceb6fe195531ea812c`

## Verification Checks

- All 36 public evidence files in [`results/2026-10-19-tinystories-cpu/`](../../results/2026-10-19-tinystories-cpu/README.md) match their recorded byte counts and SHA-256 digests in [`manifest.json`](../../results/2026-10-19-tinystories-cpu/manifest.json).
- All 27 exported generation JSON files in `outputs/` are valid `format: "raw"` envelopes (12 greedy × 192 tokens, 12 sampled × 192 tokens, and 3 baseline × 48 tokens) matching the 12 prompts in [`prompts.txt`](prompts.txt).
- `sparselab config validate --kind run` and `--kind tokenizer` pass against `run.json` and `tokenizer.json`.
- `sparselab config derive` with `model.ffn_dim=1024` produces a schema-valid `.yaml` candidate configuration for the Part 2 width-scaling exercise.
- Model weights and packed token arrays are kept outside Git; [`run-closure-index.json`](../../results/2026-10-19-tinystories-cpu/run-closure-index.json) records the SHA-256 digests of the full local checkpoint closure (`step_00008192_gen_000028`).
