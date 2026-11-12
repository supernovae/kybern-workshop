# DevMind Base Checkpoint & Evaluation Contract

[Back to DevMind Overview](README.md)

When **DevMind 340M Base** finishes training, publish its checkpoint record with the following metadata, so anyone can inspect or evaluate it with [Kybern Model Lab](https://github.com/supernovae/model-lab):

- **Checkpoint:** the checkpoint generation name, SHA-256 digests of the manifest and weights, the committed training target count, and the full-state recovery files.
- **Configuration & tokenizer:** the resolved `RunConfig`, the 32,768-token BPE tokenizer file and its SHA-256, and the exact `model-lab` and `kybern-workshop` commit SHAs.
- **Corpus:** the frozen corpus release manifest, the family split and deduplication records, the prepared 60/20/20 mixture manifest, and the training loss ledger.
- **Evaluation & licensing:** `klab` evaluation reports, and license metadata for any weights or tokenizers we distribute.

Keep binary files (model weights, optimizer states and packed token arrays) out of Git.

## Evaluation-Only Reuse

To evaluate a trained DevMind base checkpoint without retraining:

1. Check the checkpoint locally with `klab checkpoint inspect` and `klab checkpoint verify`.
2. Run the zero-shot benchmarks and completion panels from [`protocol.md`](protocol.md) with `klab eval` and `klab model exercise`.
3. Report the primary and supporting benchmark metrics with their standard errors.

Instruction fine-tuning (SFT) and conditional-memory experiments start from this base checkpoint as separate recipes, each with a matched baseline.
