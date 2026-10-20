# DevMind first-run retained subset

This separate profile keeps the 341,885,952-parameter model, 2048 context,
microbatch 2, accumulation 32, seed 42 and 32-update checkpoint/restore exercise.
Its 4,194,304 unique training targets use 60/20/20 web/synthetic/code quotas.
It validates recent code changes; do not require another small rehearsal for an
unchanged-code larger run. No downloads, spend or resource expansion is implied.

Render source templates with the three original retained snapshot paths, snapshot
SHA256s and exact manifest SHA256s. Historical parents remain read-only. Native
`corpus acquire project-acquire.yaml` needs the reviewed retained-subset Lab change;
`--offline` verifies an existing acquisition and does not create a derivative.
The selector uses the declared 1% hash rule, unchanged original rows, explicit
256 KiB long-row exclusion and aggregate 30,000-row/100 MiB refusal limits. Actual
selected counts, qualification, family supply and token floors are unknown until
measured. Never change seeds, truncate a failing selection or relax caps silently.

Run native admission draft/inspection with `application-policy.json` and POLICY.md;
record actual inspection/review and explicit restricted rows. Render the reviewed
release declaration, create split inventory, review duplicate/family merges and
freeze 98/1/1 family splits. Each stratum requires at least 100 eligible families.
Build `project-build.yaml` offline, freeze, finalize family inventory and audit.

Export LM using `base-run.yaml` only as an export base; it is NOT a training-ready
config and references unbound tokenizer/data paths. Create a separate native
TokenizerTrainConfig using the verified export dataset and `tokenizer-sampling.yaml`;
do not edit the sealed export. Fit/audit TRAIN-only 32,768-vocabulary BPE and report
unfilled fit/audit quotas. Measure `token-floors.yaml`, materialize the rendered
mixture and cold-verify it with native commands. No exposures beyond one.

Gate validation/test to at most 1,000 documents and 2 MiB text each; require 65,537
validation positions and at least 2,049 test positions from each stratum. Preserve
the complete validation split: native mixture verification binds its actual count
and rendered-byte budget, not an arbitrary prefix. Test remains sealed.

Bind the final RunConfig to actual mixture train count/tokens, full validation
count/byte budget, tokenizer, cache and run paths, with `source: local_token_mixture`.
Publish and cold-verify native prepared inputs. The fixed model and training settings
must match the base and profile; there is no model execution during preparation.
Hand off exact Lab/Workshop/Harness/runtime pins, hashes, resource measurements,
remaining cumulative budget and current worker claim to the authorized runner.
It trains to 4, verifies the immutable full-state checkpoint and resumes to 32.
The two run stores share the 32 GiB new-file stop; per-run retention does not prove
aggregate fit. RSS/VRAM are sampled stops, not hard limits.

A larger run follows successful validation without another GPU approval or small
rehearsal, provided measured unique supply, unchanged scientific intent and remaining
approved time/storage allow it. The original 84-source/12B case still cannot fit this
no-download profile. Report an exact data/time/capacity mismatch instead of silently
redefining that case or increasing exposures. No GPU scheduling is done here.

`preparation.json` is the native phase map: compile and run its leaves through
the existing preparation supervisor. It contains no network allocation phase and
no training command. Render review-dependent declarations only after their real
inspection; a phase map does not supply review or approval evidence.

Render the working recipe into the same fresh directory used as the phase map's
attempt root. Its native split-freeze leaf is `splits-reviewed.yaml`, matching
`project-build.yaml`; keep the accompanying freeze receipt and family candidates.
The reviewed release's admission path is relative to that recipe directory.

Offline contract checks use an already installed subset-capable Lab checkout:

```sh
WORKSHOP_LAB_CHECKOUT=/absolute/path/to/tiny-sparse-lab python -m unittest discover -s tests -v
```

The connected test substitutes generated rows, 8/1/1 family weights, a 260-token
BPE vocabulary, 6,000 fit bytes and 300 training targets, then reaches a cold
prepared bundle. It performs no model execution and proves no real-data capacity
or model quality. The production values remain 98/1/1, 32,768 vocabulary,
32 MiB fit and 4,194,304 targets.

The generated-fixture test also hides all original parent, recipe, mixture and
cache paths before cold-verifying and copying the sealed prepared bundle. This
checks the runner handoff boundary without executing a model.

For supervised subset creation, bind both `acquisition_project_sha256` (the
rendered project file) and `preparation_acquisition_identity_sha256` (the native
resolved acquisition identity), paired with `preparation_normalizer`. Source-file
changes after binding must refuse before reservation. Parent replay scratch belongs
inside the accounted work area. Validation/test come from this subset's native
family split, never an independently selected subset presumed disjoint.
