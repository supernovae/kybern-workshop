# DevMind Base Checkpoint & Evaluation Contract

[Back to DevMind Overview](README.md)

Once **DevMind 340M Base** completes training, its released artifact record must include the following verifiable metadata so anyone can inspect or evaluate the checkpoint with [Tiny Sparse Lab](https://github.com/supernovae/tiny-sparse-lab):

- **Checkpoint identity:** immutable checkpoint generation name, manifest and weight SHA-256 digests, committed training target count, and full-state recovery files.
- **Configuration & tokenizer:** resolved `RunConfig`, 32,768-token BPE tokenizer file and SHA-256 digest, and the exact `tiny-sparse-lab` and `kybern-workshop` commit SHAs.
- **Corpus provenance:** frozen corpus release manifest, family split and deduplication receipts, prepared 60/20/20 mixture manifest, and training loss ledger.
- **Evaluation & licensing:** verified `sparselab` evaluation reports and explicit license metadata for any distributed weights or tokenizers.

Binary payloads (model weights, optimizer states, and packed token arrays) remain stored outside Git.

## Evaluation-Only Reuse

To evaluate a trained DevMind base checkpoint without retraining:

1. Verify the checkpoint closure locally with `sparselab checkpoint inspect` and `sparselab checkpoint verify`.
2. Run the frozen zero-shot benchmark and completion panels defined in [`protocol.md`](protocol.md) using `sparselab eval` and `sparselab model exercise`.
3. Report both primary and supporting benchmark metrics alongside standard errors.

Follow-up instruction fine-tuning (SFT) or conditional-memory experiments build on top of the verified base checkpoint as separate recipes with matched baseline controls.
