# TinyStories CPU microlab

Prepare story inputs, change FFN width, and inspect a paired comparison using the
existing public lab CLI. This additive package preserves the upstream CPU lesson:
`source.yaml`, `tokenizer.yaml` and `run.yaml` are byte-identical copies at lab
commit `b155cdcc1462cfbcbd5f0cf5261eb8aa197ef9dc`. The delta comes from its walkthrough.
See [provenance.json](provenance.json) for source hashes, dependency pins and asset
relationships, and [LICENSE.upstream](LICENSE.upstream) for the lab MIT notice.
TinyStories is attributed to Ronen Eldan and Yuanzhi Li (synthetic stories from
GPT-3.5/GPT-4); the pinned source declares CDLA-Sharing-1.0. No dataset payload is
included.

**Status: static validation only; no Workshop TinyStories execution result.**
This is a workflow lesson, not evidence of model quality or an architecture win.
The synthetic example's measured proof and admissions do not cover this lesson.

## Scope and budget

| Setting | Baseline / candidate |
| --- | --- |
| Seed | 42 for both arms; unchanged from upstream |
| Model | Dense decoder, 2 layers, hidden 128, 4 heads, context 128 |
| Vocabulary / FFN width | 2,048 / 256 versus 384 |
| Runtime | PyTorch CPU FP32 |
| Training | Sequence 64, microbatch 2, accumulation 2; 256 targets/update |
| Main budget | 40 updates / 10,240 supervised targets per arm; 80 / 20,480 for two fresh arms |
| Native staging | Smoke 2 and warmup 5; optimizer warmup is separately 4 |
| Evaluation | Every 20 steps, at most 4 batches × 2 × 64 = 512 targets per scoring pass |
| Checkpoints | Every 20 steps, periodic generations retained |
| Selected source | Up to 2,000 train and 100 validation documents |
| Run preparation caps | 2,000,000 train / 200,000 validation tokens |

Tokenizer fitting uses training text only. Validation is selected first; the
source excludes whole-document duplicates and train/validation overlap. Its
resource limits bound selected processing, **not upstream downloads or Hub cache
size**, which can require several GB. Actual transfer has not been measured here.
The tokenizer declaration has separate 8,000,000/16,384 token caps; preserve these
upstream values rather than conflating preparation and training budgets.

`try` performs native preparation, staging/runtime probes, both training arms,
periodic evaluation, shared held-out scoring and an automatic fast probe battery.
These are additional work beyond the main update budget. Completed identical
baselines may be reused; read the actual executed/skipped records. Held-out scoring
uses run-owned validation, not an independent final test set.

Before future execution, obtain approval for dataset acquisition and the full
compute/disk scope, establish monitoring and stop ceilings for every runtime-bearing
command, and preserve failed receipts before diagnosing a retry. The earlier
synthetic 600-second/4-GiB/1-GiB envelope is not a validated TinyStories budget.
Nothing in this package authorizes provisioning, installation or a run.

## Future execution with an approved existing runtime

Use the pinned lab and dependency versions in `provenance.json`. Set `CPU_PYTHON`
to the absolute Python executable of that existing CPU installation, and
`WORKSHOP` to this Workshop checkout. Record both Git commits and the installed
lab source identity before acquisition; do not reinstall during an experiment.
These Bash commands are the native path to run after scope approval; they were
not executed to publish this package. No custom driver or scheduler is needed.

Choose a fresh absolute `SPARSELAB_WORK_DIR` outside every Git checkout. Do not
reuse or relocate earlier experiments. Run from the copied inputs so relative
paths resolve into the external work directory.

```sh
export SPARSELAB_WORK_DIR=/absolute/external/fresh-tinystories-work
WORK="$SPARSELAB_WORK_DIR/experiments/tinystories-microlab"
SAMPLE="$WORKSHOP/examples/tinystories-microlab"
mkdir -p "$WORK"
mkdir "$WORK/inputs"  # Stop if this exists; choose a fresh WORK.
cp "$SAMPLE/source.yaml" "$SAMPLE/tokenizer.yaml" "$SAMPLE/run.yaml" \
  "$SAMPLE/wider-ffn.yaml" "$WORK/inputs/"
cd "$WORK/inputs"
df -h "$WORK"
df -i "$WORK"
```

Do not run templates in place. Source locks, snapshots, tokenizer files, prepared
arrays, bindings, admissions, receipts, caches and checkpoints stay outside Git.
Confirm any pre-existing Hub cache location also lies outside Git without altering
credentials or account settings.

```sh
"$CPU_PYTHON" -m sparselab data lock "$WORK/inputs/source.yaml" \
  --output "$WORK/inputs/source.lock.json"
# Network acquisition; selection bounds are not a download quota.
"$CPU_PYTHON" -m sparselab data snapshot "$WORK/inputs/source.lock.json" \
  --output "$WORK/snapshot"
# CPU tokenizer fitting; monitor this and the following model work.
"$CPU_PYTHON" -m sparselab tokenizer train "$WORK/inputs/tokenizer.yaml"
"$CPU_PYTHON" -m sparselab try "$WORK/inputs/wider-ffn.yaml" \
  --vs "$WORK/inputs/run.yaml"
```

`try` prints a try ID and separate baseline/candidate run IDs. Its runs and sealed
records live under `SPARSELAB_WORK_DIR/lab`, independently of the direct-training
`logging.root_dir` in `run.yaml`. Substitute the printed try ID below:

```sh
"$CPU_PYTHON" -m sparselab report TRY_ID
"$CPU_PYTHON" -m sparselab compare TRY_ID --references
```

These read saved records; reference comparison does not require model downloads.
Report actual targets, loss delta and probe verdict, including `missing_evidence`
or `not_comparable`. An incomplete probe is not a pass. Retain negative results.
Record elapsed time, peak process-tree RSS, workspace growth, descendant cleanup,
all commands, pins and executed/skipped work before claiming completion.

## Native path and migration boundary

The authenticated portable preparation/workflow executors at this lab pin accept
synthetic inputs only (workflow also requires CPU PyTorch). This TinyStories
package uses the existing snapshot/tokenizer/`try` path; it has no portable
workflow admission, synthetic seal helper, or claimed portable replay proof.
Supporting authenticated TinyStories workflows would require an explicit native
snapshot-input/admission contract and execution qualification beyond this package.

Upstream samples, docs, tests and historical evidence remain intact. In particular,
`tests/test_dataset_cli.py` reads the CPU sample for retired-source rejection;
`tests/test_experiment_comparison_phases.py` uses the CPU declarations for phase,
budget and lock coverage. Those tests were inspected, not run for this packaging.
No lab test helper is imported.

All links below freeze the same lab source pin:

- [Original CPU walkthrough](https://github.com/supernovae/tiny-sparse-lab/blob/b155cdcc1462cfbcbd5f0cf5261eb8aa197ef9dc/docs/tinystories-microlab.md) and [advanced CPU declarations / historical acceptance](https://github.com/supernovae/tiny-sparse-lab/tree/b155cdcc1462cfbcbd5f0cf5261eb8aa197ef9dc/experiments/samples/tinystories-microlab): continuation, matrices and Campaigns are separate exercises. Old acceptance retains its original launch/source identities; it is not a new Workshop run.
- [Hosted CUDA/T4 lesson](https://github.com/supernovae/tiny-sparse-lab/tree/b155cdcc1462cfbcbd5f0cf5261eb8aa197ef9dc/experiments/samples/hosted-tinystories): distinct six-layer, hidden-256, FFN-704, CUDA FP16 model with hosted enrollment and relay concerns. Its source/tokenizer companions match the CPU sample; its runtime and budget do not.
- [Dense 30M research history](https://github.com/supernovae/tiny-sparse-lab/tree/b155cdcc1462cfbcbd5f0cf5261eb8aa197ef9dc/experiments/research/history/tinystories-dense-30m-data-rich-v1): a much larger historical ROCm/BF16 experiment with different vocabulary, source coverage and budget. Its evidence stays attached to its original execution.

## Packaging validation (2026-10-14)

Static checks passed with the existing runtime recorded in `provenance.json`:
all three copied file bytes and SHA-256 values match the pinned upstream;
`load_source`, `load_tokenizer_config`, `load_config` and `read_candidate` accept
copies in temporary external `inputs/`; native `derive_config` produces a valid
candidate differing only in FFN width. Resolved snapshot/tokenizer paths point
outside Git, and CPU/FP32, seed 42 and the 40-update/10,240-target budget match.
Installed package versions match the manifest. `git diff --check` passed.

These were data-only checks through native loaders/derivation, with no lab test
helpers. Temporary validation copies were removed. Dataset acquisition, tokenizer
fitting, training, runtime probes, evaluation, reporting and replay were all
**not executed**; no new runtime measurement or verified result is asserted.
