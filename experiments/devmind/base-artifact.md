# Base artifact and derivative evaluation contract

No base checkpoint currently exists. This document specifies the required native
artifact closure; it is not a manifest with invented hashes or a new Workshop
artifact format. Use Lab's native checkpoint/config/report verification.

A released base reference must identify:

- Immutable checkpoint location and SHA256 (or authenticated native manifest),
  checkpoint generation, actual committed targets, and full-state recovery files.
- Exact model RunConfig, tokenizer bytes/hash and vocabulary, producer Lab revision,
  dependency/runtime identity, and Workshop recipe revision/content identity.
- Corpus release, family split/admission, prepared mixture and packing identities;
  actual training ledger and checkpoint lineage, including interruptions.
- Verified native evaluation/report references and limits; access/retrieval method,
  license and permission to publish checkpoint and tokenizer separately.

Payloads stay outside Git. Locations, credentials and machine mounts are local
bindings; no secrets belong here. Imported private-quarantine data does not confer
model publication rights. Public release requires separate authorization.

## Derivative: evaluate the retained base without rebuilding

The first derivative is evaluation-only: consume one verified base checkpoint,
its matching model configuration and tokenizer, and the frozen public-benchmark
protocol from `protocol.md`. Hold model weights and evaluation settings fixed;
report separate primary/supporting scores and per-item uncertainty. This establishes
reusable artifact consumption, not a causal architecture improvement.

Execution must verify the supplied artifact closure, use native Lab evaluation and
report functions, and record producer/consumer identities. There is no preparation
or training phase in this derivative. A missing checkpoint/tokenizer/protocol or
unapproved dataset acquisition must refuse, not trigger base training, downloads
or an automatic fallback. No executable derivative declaration is supplied until
the native portable artifact-input interface is agreed in Lab #158; inventing a
Workshop-only schema would hide this gap.

Later SFT or memory variants require a separately reviewed concrete configuration,
matched baseline/evaluation and explicit budget. They cannot overwrite this base.
