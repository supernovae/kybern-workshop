# Contributing to Workshop

This policy applies until a production release tag establishes a reviewed
compatibility contract. It records the owner's 2026-10-17 direction and the
[canonical portable experiment plan](https://app.notion.com/p/3f83b68cca2281f59998c5b285816910).

Adapt plans, recipes and model definitions to current supported Lab interfaces.
Do not change Lab to emulate old experiment behavior, introduce backward-version
adapters, or build candidate-recovery machinery for historical runs. Report a
missing current capability explicitly for coordinated native implementation.

New experiment authoring belongs in declarative Lab schemas, configuration and
documentation. Generic scientific implementations and validators belong in Lab;
process supervision belongs in Harness. Do not add Workshop Python engines,
launchers or per-recipe test frameworks. Existing procedural helpers remain
migration inventory, not a precedent for new engines.

The active showcase is basic synthetic CPU, TinyStories and DevMind. Retired
families remain in immutable Git history, not an active compatibility backlog.
Preserve original historical bytes, hashes and IDs when citing that history. Historical claims
in Workshop describe their original evidence and conditions; they are not current
Lab guarantees. Reading, interpreting and hash-verifying old evidence is allowed
without recreating its runtime or changing the archive to fit new interfaces.

A fresh reproduction is a new experiment with new run/artifact identities and
explicit lineage to its historical reference. Never reuse an old identity to
imply that new outputs reproduce old bytes. Record changed scientific choices,
current source/runtime pins, generated bindings, budgets and limitations.

Keep active research intent, historical execution, metadata validation and current
runtime readiness separate. A reproduction backlog, valid schema or reviewed PR
is not workload approval. Acquisition, training, generation and publication still
require their applicable explicit authorization; do not infer it from old receipts.

For review, state the exact head, native interfaces checked, preserved origins,
actual validation performed and remaining blockers. Reviewers should reread this
policy and the canonical plan. Preserve failures and distinguish unexecuted
proposals from actual results; do not claim self-review clearance.
