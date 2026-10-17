# DevMind

Recipe: **DevMind 340M Base** — approximately 340M dense base model.

EXP-1 and LAB86 remain historical planning/attempt identifiers and provenance
aliases. This is the fresh 340M recipe: the public DevMind name does not imply
reuse of historical DevMind corpora, tokenizer or checkpoints.

Status: **authored preparation and proposed scientific configuration; not trained,
not execution-ready**. There are no published base weights or completed corpus
receipts in this repository. The 4 GiB preparation pilot is not a model build.

This project contains declarations, documentation and artifact references only.
Use installed Tiny Sparse Lab directly from this directory or a copy in your own
repository. GitHub, Notion, bots and lab-harness are not runtime dependencies.

## Read in order

1. [Scientific protocol](protocol.md): proposed architecture, exposure, evaluation
   and unresolved review decisions.
2. [Native operation map](native-commands.md): preparation through training,
   evaluation, reporting and the known portable interface gaps.
3. [Base artifact and derivative](base-artifact.md): required verified outputs,
   access policy and evaluation-only reuse without retraining.
4. [Migration provenance](migration.json): 148 files copied byte-for-byte from
   Lab `8975c5abcaefb1d3e595a9f1f466db97f9ab7682`.

`model.json` and `optimizer.json` use native Lab configuration section fields.
They are **proposals**, not full RunConfig files or launch instructions. In
particular, optimizer decay horizon, dataset/tokenizer identities, exact target
and step limits, evaluation inputs, and finite checkpoint/storage/runtime limits
must be bound before a full runnable configuration exists.

## Preparation and preserved internal records

`preparation/preparation.json` is the native 24-phase preparation plan.
`preparation/lab86/` contains exact pinned source declarations and scientific
policies, alongside the original internal job/session templates and documentation.
The original bytes are preserved for migration verification. Their historical
mentions of required Harness image allowlists, host bindings and operator job
submission apply **only to that internal deployment**, not public reproduction.
Do not treat their old Python-test claims as Workshop validation or use their
old command-rendering snippets as a new Workshop implementation. Native Lab is
responsible for validation, rendering and execution.

The migration must retire the corresponding active Lab paths after the mapped
copy is accepted; this is not permission to maintain two active recipe owners.
The original source commit retains the historical evidence and Python tests.

## Pins and scope

The imported source declarations pin upstream datasets and shard hashes. The
reference Lab revision above includes the reusable Parquet timestamp support;
its main CI had an independently diagnosed archive inventory race, so it is a
provenance reference, not a cleared execution/runtime recommendation. Bind the
reviewed replacement Lab revision and its dependency lock when native portable
interfaces and the CI fix are accepted. No image digest is activated here.

Python/runtime dependencies follow that Lab revision's lock and supported
platform contract. Runtime fit is unmeasured. The old local preparation envelope
(48 hours, 300 GiB additional disk, observed 16 GiB RSS, eight threads) is an
approval-specific internal deployment limit, not a universal machine requirement.
No GPU training, benchmark/model acquisition, publication or spend is approved
by these files. Approval text is provenance, never fresh authority.
