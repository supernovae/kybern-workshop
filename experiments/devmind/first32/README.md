# DevMind first-run retained subset

This is the profile from one earlier attempt. Its caps and pins belong to that
attempt; they are not lab-wide defaults. For new iterations, use the
[run guide](../run.md). Production and model runs on this profile are stopped
until integrated checks and owner review are done. The steps below describe the
profile as it was written and don't lift that hold.

The profile keeps the 341,885,952-parameter model, 2048 context, microbatch 2,
accumulation 32, seed 42, and a 32-update checkpoint/restore exercise. It trains
on 4,194,304 unique targets split 60/20/20 across web, synthetic and code. Its
purpose was to test recent code changes. Once it passes, a larger run on
unchanged code doesn't need another small rehearsal. It needs no downloads,
spending or extra resources.

Fill the source templates with the three original retained snapshot paths, their
snapshot SHA256s and exact manifest SHA256s. Treat the historical parents as
read-only. Use Kybern Model Lab commit `c5961c44bc9ea563a7ea552975321183b22c1ba2`
(merged PR #204). `corpus acquire project-acquire.yaml` takes its retained-subset
path; `--offline` checks an existing acquisition without creating a new one.
The selector uses the 1% hash rule from the config, leaves original rows
unchanged, excludes rows over 256 KiB, and refuses to go past 30,000 rows or
100 MiB in total. You only learn the selected counts, qualification, family
supply and token floors by measuring them. Never change seeds, truncate a
failing selection or quietly loosen caps.

The selected-byte allowances are 50 MiB web, 30 MiB synthetic and 20 MiB code,
the same 100 MiB in total. Row allowances stay at 18,000 / 6,000 / 6,000. The
earlier 60/20/20 MiB split stopped at the synthetic source's combined row/byte
limit, after web had selected 8,133 rows / 43,361,852 bytes. The new split moves
spare web headroom to synthetic. We don't yet know the full synthetic total, so
this may still fall short. The fixed selection inputs and original parent pins
are unchanged. Changing the limits produces a new acquisition and snapshot with
new hashes; keep the earlier refusal and child snapshot as they are.

Run the admission draft and inspection with `application-policy.json` and
POLICY.md. Record the inspection and review you actually did, and list any
restricted rows. Fill in the reviewed release template, create the split
inventory, review duplicate and family merges, and freeze the 98/1/1 family
splits. Each stratum needs at least 100 eligible families. Build
`project-build.yaml` offline, then freeze, finalize the family inventory and
audit.

Export the LM data using `base-run.yaml` only as the export base. It is not a
training config, and it points at unbound tokenizer and data paths. Write a
separate TokenizerTrainConfig that uses the exported dataset and
`tokenizer-sampling.yaml`; leave the frozen export alone. Fit and audit a
TRAIN-only 32,768-vocabulary BPE, and report any fit or audit quotas you
couldn't fill. Measure `token-floors.yaml`, materialize the mixture, and run the
cold check with the Lab commands. Each token is used at most once.

The held-out limits in `profile.json` are **operator stops** that you check by
hand; Lab doesn't enforce them. After `measure-tokens`, and before
`materialize-unique` or `pack`, write a held-out inspection record tied to the
release ID, tokenizer SHA256, split-freeze receipt and these limits. Stop if any
value is missing or out of range:

- Validation and test each hold at most 1,000 LM records and 2 MiB of normalized
  UTF-8 text. Count the full release's `lm/validation.jsonl` and
  `lm/test.jsonl` by adding up the UTF-8 bytes of each parsed `text` value, not
  the JSON file size or the character count. Use a JSON reader you already have
  installed, and don't trim anything.
- Validation needs at least 65,537 token positions in total. Test needs at least
  2,049 token positions in **each** of web, synthetic and code. Run the census
  below with the fitted tokenizer on the full release, including its held-back
  test split. In `measurement.views.lm`, read each split's `records` and
  `actual_tokens`, and test's
  `dimensions.source_domain.{web,synthetic,code}.actual_tokens`. These counts
  leave out the appended EOS, so applying the same position floors to them errs
  on the safe side. If a count is missing or null, or a stratum is missing, stop.
- Check the realized family counts in the split-freeze receipt. Every stratum
  needs validation and test families, with no family or exact-content leakage.

```sh
klab corpus describe "$RELEASE" --tokenizer "$TOKENIZER" \
  > "$ATTEMPT/held-out-census.json"
```

`token-measurements.json` from `measure-tokens` counts distinct TRAIN source
supply; it doesn't include this held-out census. `token-floors.yaml` checks only
its own training-token floors. `pack`, `verify-prepared` and `verify-mixture`
don't read `profile.json` and won't check these limits for you. Keep the byte
census, family review and your pass/stop decision next to the Lab reports. If a
check fails, stop this profile; don't resample, trim or raise caps.

Keep the whole validation split: mixture verification checks its actual count and
byte budget, so you can't substitute a prefix. Test stays untouched for model
evaluation; the census only measures preparation supply and runs no model.

Bind the final RunConfig to the actual mixture's train count and tokens, the full
validation count and byte budget, the tokenizer, the cache and run paths, and
`source: local_token_mixture`. Publish the prepared inputs and run their cold
check. The model and training settings must match the base and the profile;
nothing runs the model during preparation. Hand the approved runner the exact
Lab, Workshop, Harness and runtime pins, the hashes, resource measurements,
remaining cumulative budget and current worker claim. The runner trains to step
4, checks the full-state checkpoint and resumes to 32. Both run stores share the
32 GiB limit on new files, and per-run retention alone doesn't show that both
fit. RSS and VRAM are sampled and trigger a stop; they aren't hard limits.

If validation succeeds, a larger run can follow without another GPU approval or
small rehearsal, as long as the measured unique supply, the scientific intent and
the remaining approved time and storage allow it. The original 84-source/12B case
still doesn't fit this no-download profile. If data, time or capacity fall short,
report the exact gap; don't redefine the case or add repeated exposures. This page
schedules no GPU work.

`preparation.json` is the phase map. Compile its leaves and run them through the
existing preparation supervisor. It has no network allocation phase and no
training command. Fill review-dependent templates only after the real inspection;
the phase map doesn't stand in for review or approval.

Write the working recipe into the same fresh directory you use as the phase map's
attempt root. Its split-freeze leaf is `splits-reviewed.yaml`, matching
`project-build.yaml`; keep the freeze receipt and family candidates with it. The
reviewed release's admission path is relative to that recipe directory.

Check these configs against the Lab you have installed with
`klab config validate experiments/devmind/first32`. Lab's own test suite covers
this preparation path end to end on small generated inputs. The production values
stay at 98/1/1, 32,768 vocabulary, 32 MiB fit and 4,194,304 targets.

To create the supervised subset, bind both `acquisition_project_sha256` (the
filled-in project file) and `preparation_acquisition_identity_sha256` (Lab's
resolved acquisition hash), together with `preparation_normalizer`. If a source
file changes after binding, the run refuses before reserving anything. Keep the
parent replay scratch inside the accounted work area. Validation and test come
from this subset's own family split; never use a separately selected subset and
assume it doesn't overlap.

The resolved acquisition hash also feeds the downstream split inventory, split
freeze and build supervision. So all three project files keep the same project ID
and source entries; only the reviewed release, split and transform references
change. Cold replay of the retained data needs writable scratch in the accounted
snapshot work area.
