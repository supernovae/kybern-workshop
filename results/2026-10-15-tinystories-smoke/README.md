# TinyStories CPU smoke: first completed pair

The 2026-10-15 CPU container run completed the native preparation-to-paired-workflow
path. It supports the [TinyStories experiment guide](../../examples/tinystories/README.md);
it is execution evidence, not a model-quality result or GPU qualification.

The worker result was independently read on media-pc by the owner coordinator.
Attempt `LAB80-cpu-20261015f` ran from 19:44:38 to 19:50:51 UTC, before its 20:14
assignment deadline. All 12 workflow stages completed; process/container exits
were zero, no OOM was reported, and cleanup found zero remaining containers.
Each arm reached main evaluation at step 1 with one batch / 32 targets.
Scientific comparability was `not_assessed`; no automatic promotion occurred.
The follow-up audit confirmed 16 training updates (2 smoke + 5 warmup + 1 main
per arm), totaling 512 training target positions. Six evaluation batches are
directly evidenced: main step 0/1 for both arms plus one Campaign evaluation per
arm. Twenty-four was the allocation cap, not a measured executed count.

## Reproduction inputs

- Lab source: `66ff9d71423e961ee15aed2267902164f04514c6`.
- CPU image: `ghcr.io/supernovae/tiny-sparse-lab@sha256:553eefba27b7069ba17fb92c5734b2b53548ad3b40f868b1ad39dc3e3ad82ea4`.
- Runtime: Python 3.14.4, PyTorch 2.14.1+cpu.
- Dataset: `roneneldan/TinyStories`, revision `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`.
- Preparation declaration: Workshop `25a6093aacf115d4be19170a76a621912f587c00` ([admission-only PR #15](https://github.com/supernovae/kybern-workshop/pull/15)).
- Workflow declaration: Workshop `3659786f9506c25d4d13088d0726cd990be7f0cc` ([admission-only PR #16](https://github.com/supernovae/kybern-workshop/pull/16)). Neither PR should be merged as a reusable execution state.
- Original preparation selected 64 train / 16 validation records, fitted a 512-token vocabulary and packed 23,673 tokens. Two acquired files totaled 258,720,238 bytes.

This summary records coordinator-inspected worker evidence; full sanitized native
receipts are not yet archived in this repository. It does not claim all possible evaluation passes were independently accounted
for, or identify a baseline/candidate winner. The GPU `try` walkthrough
is a separate, unexecuted local experiment path and includes its own fast probes.

## Reuse lesson

Earlier attempts stopped before training: one hit a null Parquet-loader-default
compatibility bug, one external check expected `packing` instead of native
`pack-data`, and one mounted the prepared cache read-only. Their evidence remains
separate; this result does not turn those attempts into successes.

The successful continuation used a fresh writable copy of the prepared cache,
new local bindings/admission and fresh execution state, retaining original input
identities. Even a cache hit needs a writable cache parent for `.cleanup.lock`
and `<id>.preparation.json`. See the experiment guide's reuse instructions.

The reuse audit matched prepared artifact `b7af269e44c026cd` / native hash
`dfc008bd34c09fabf8ebc204f300277080735a49d5bedff7d0f8a99eb394d458`,
the original snapshot manifest identity
`efd5e6924cb04e0bad0d2bad50b1863f1630b5bb6d3c58eb93879d8c20003239`,
and the split hashes. The offline environment and existing bindings support reuse
without redownload. Final admission selected workflow commit
`3659786f9506c25d4d13088d0726cd990be7f0cc` and binding SHA256
`4628e9110c9c4a2196c9bc61fe071556bcdf4095e5e9af9be8ad8ff90a579e03`.
