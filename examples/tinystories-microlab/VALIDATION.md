# TinyStories Microlab Schema & Metadata Validation

Validated with Python 3.14 and Tiny Sparse Lab (`sparselab`):

- All 11 declaration files in `declarations/` match their SHA-256 digests in [`migration.json`](migration.json).
- When copied to an external temporary workspace, `sparselab config validate --kind run` and `--kind tokenizer` both return `schema_valid: true`.
- `sparselab config derive --set model.ffn_dim=384` generates a valid candidate `RunConfig` and `.derivation.json` sidecar with `model.ffn_dim` updated to `384` and all dataset/tokenizer paths preserved.
- The prompt-panel files (`story-greedy.json`, `story-sampled.json`, and `story-website-baseline.json`) validate against the `GenerationPanel` schema (6 greedy × 192 tokens, 6 sampled × 192 tokens, and 3 baseline × 48 tokens).
