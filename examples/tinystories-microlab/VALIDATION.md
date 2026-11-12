# TinyStories Microlab: Config Checks

Checked with Python 3.14 and Kybern Model Lab (`klab`):

- All 11 config files in `declarations/` match their SHA-256 digests in [`migration.json`](migration.json).
- Copied into a temporary workspace outside the repository, the configs pass `klab config validate --kind run` and `--kind tokenizer`, both returning `schema_valid: true`.
- `klab config derive --set model.ffn_dim=384` writes a valid candidate `RunConfig` and `.derivation.json` sidecar. `model.ffn_dim` changes to `384`, and every dataset and tokenizer path stays the same.
- The prompt-panel files (`story-greedy.json`, `story-sampled.json`, and `story-website-baseline.json`) validate against the `GenerationPanel` schema (6 greedy × 192 tokens, 6 sampled × 192 tokens, and 3 baseline × 48 tokens).
