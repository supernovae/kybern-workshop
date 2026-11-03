# TinyStories versus SimpleStories at 50.6M

**Declared, not run.** This matched-source experiment asks how the training
dataset changes a fresh model under the existing TinyStories tokenizer. No new
dataset payload, trained model, quality result or ROCm fit is claimed here.
It builds on [TinyStories PR #60](https://github.com/supernovae/kybern-workshop/pull/60),
without changing that branch or its historical evidence.

## Frozen comparison

Use [TinyStories](run-tinystories.json) and [SimpleStories](run-simplestories.json)
with the same model, seed, tokenizer bytes, reference attention, optimizer,
packing semantics, context, batch, schedule and runtime. The declarations differ
only in names and dataset identity/paths. Native Lab owns preparation, training,
checkpoint retention, evaluation and generation; Workshop supplies declarations
and the supplementary read-only contamination audit.

| Setting | Both arms |
| --- | --- |
| Model | 9 layers, width 640, FFN 1,920, 10 heads; tied embeddings; 50,556,800 parameters in the inherited recipe |
| Initialization | Fresh seed 42; no promotion of any pretrained parent |
| Tokenizer | Existing 4,096-vocabulary train-only TinyStories BPE; exact hashes in [protocol.json](protocol.json) |
| Runtime | PyTorch / ROCm / BF16, reference attention, deterministic setting |
| Training context / microbatch / accumulation | 512 / 4 / 2 = 4,096 supervised targets per update |
| AdamW | Peak 0.0006, floor 0.00006, warmup 2,048, cosine horizon 244,141; betas 0.9/0.95, epsilon 1e-8, decay 0.1, clipping 1.0 |
| Terminal budget | 244,141 updates / 1,000,001,536 processed supervised targets per arm |
| Recovery checkpoints | Every 256 updates; bounded native milestone retention |
| Quality checkpoints | 24,415 / 122,071 / 244,141 updates = 100,003,840 / 500,002,816 / 1,000,001,536 targets |
| Inline validation | Every 1,024 updates, 32 batches on the arm's own development split |

The intermediate checkpoints share the **1B-target learning-rate horizon**. They
are not separate optimally scheduled 100M/500M training runs. Initial step zero
and pilot step 256 are also retained. Check step-zero model tensor equality
before interpreting a pair; whole checkpoint hashes differ because data and run
identities differ. Staging warmups do not count toward scientific exposure.

Native retention reserves at most eight 1-GiB generations per arm, with 9 GiB
write headroom. These are provisional caps, not measured sizes or a statement of
available space. Before locking local configs, set the same reserve from actual
host capacity and measure a full-state checkpoint at the pilot. Account for both
arms, ancestry, prepared bundles, Hub caches and scratch separately. If a cap is
insufficient, preserve the failure and explicitly revise both declarations before
the scientific run. Do not silently drop quality milestones.

## Sources and evidence boundary

| Source declaration | Immutable revision | Upstream text / splits | Declared license |
| --- | --- | --- | --- |
| [TinyStories](source-tinystories.json) | `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64` | `text`; train / validation | CDLA-Sharing-1.0 |
| [SimpleStories](source-simplestories.json) | `e63b8adc3b1a1bdc7cac5b500d150b71346b0628` | `story`; train / test mapped to local validation | MIT |

Metadata was inspected on 2026-11-03: the
[TinyStories pinned card](https://huggingface.co/datasets/roneneldan/TinyStories/blob/f54c09fd23315a6f9c86f9dc80f725de7d8f9c64/README.md),
[SimpleStories card](https://huggingface.co/datasets/SimpleStories/SimpleStories/blob/main/README.md)
and [SimpleStories commit](https://huggingface.co/datasets/SimpleStories/SimpleStories/commit/e63b8adc3b1a1bdc7cac5b500d150b71346b0628).
The SimpleStories card declares `story`, train/test and MIT; the commit link
resolves the full revision. These are metadata observations, **not native source
locks, license-file archives, download checksums or verified corpus contents**.
Archive the pinned cards/license evidence and native locked file inventories at
preparation time. Preserve attribution and source-specific license records; do not
relabel a combined corpus under a single license.

Both select at most 500,000 retained train and 4,096 development documents in
native source order, with exact-text deduplication and validation priority.
SimpleStories annotations are excluded from model text. No quality filtering or
theme balancing is introduced. The remaining upstream heldout records stay
unused; this experiment consumes part of SimpleStories' test split as development
data, so do not describe it as an untouched final test afterward.

The 160M train-token cap and 2,097,152 validation-token cap are preparation bounds,
not promises of supply. If a source exceeds them or cannot fill the requested
selection, stop and record the native diagnostic; revise and refreeze the pair
before training. Source-order slices may be unrepresentative. Equal documents do
not mean equal text length, token supply or vocabulary coverage.

## Prepare on an authorized host

Use Lab `903ad2f0bb261935132dee53295aba6b66f8e792`, the inspected lifecycle pin,
in its Python 3.14 environment. Record the actual Lab/Workshop commits and locked
dependencies. A pin change requires native schema and command revalidation for
both arms. No GPU or dataset preparation belongs in the cloud authoring session.
ROCm execution is owned by a separate authorized host task; this authoring task
does not access it. Coordinate recipe pins and receipts with that task before
starting either arm. Devmind's production machine is outside this experiment.

Set `STUDY` to this recipe directory and `WORK` to a new persistent directory
outside Git. Set `ARM` to each source name in turn. Inspect available storage,
current processes and the registered ROCm runtime before acquiring or staging.
Reuse the verified existing tokenizer bytes at `$WORK/shared/tokenizer.json`;
do not refit a same-sized replacement. If those bytes are unavailable, the
experiment is blocked pending retrieval or an explicitly revised tokenizer study.

**Host preparation blocker:** the native tokenizer-origin check currently requires
the consuming dataset to match the tokenizer's training dataset. This rejects the
intended cross-source reuse even with identical tokenizer bytes. A separate Lab
task owns explicit provenance binding. Preserve that failure; do not change the
tokenizer's recorded origin or fit a replacement to bypass it. Before either
scientific arm starts, record the resulting Lab fix revision and revalidate both
configs and the shared-tokenizer path. The pin above is the inspected authoring
baseline, not evidence that this cross-source preparation succeeds on that pin.

Copy the source declarations to `$WORK/inputs/` and bind their free-space reserve
to actual capacity. Lock and snapshot each source using native commands:

```sh
sparselab data lock "$WORK/inputs/source-$ARM.json" \
  --output "$WORK/inputs/source-$ARM.lock.json" --json
sparselab data snapshot "$WORK/inputs/source-$ARM.lock.json" \
  --output "$WORK/$ARM/snapshot" --json
sparselab config derive "$STUDY/run-$ARM.json" \
  --set "tokenizer.path=\"$WORK/shared/tokenizer.json\"" \
  --set "dataset.cache_dir=\"$WORK/$ARM/data\"" \
  --set "dataset.train_path=\"$WORK/$ARM/snapshot/train.jsonl\"" \
  --set "dataset.validation_path=\"$WORK/$ARM/snapshot/validation.jsonl\"" \
  --set "dataset.source_manifest_path=\"$WORK/$ARM/snapshot/manifest.json\"" \
  --set "logging.root_dir=\"$WORK/runs\"" \
  --output "$WORK/run-$ARM.yaml" --json
sparselab tokenizer verify "$WORK/run-$ARM.yaml" --json
```

The checked-in source configs are JSON, but native `config derive` requires a
`.yaml` or `.yml` output filename. All subsequent commands consume that derived
YAML file.

Verify both snapshots with native `sparselab.data.sources.verify_snapshot` before
the supplementary audit. Native within-source dedup does **not** check the other
dataset. Audit the full selected training snapshots against both holdouts and all
fixed prompts (also covering the tokenizer's training slice when reusing the
original selected TinyStories snapshot):

```sh
python3 "$STUDY/../../scripts/audit-story-splits.py" \
  --tinystories "$WORK/tinystories/snapshot" \
  --simplestories "$WORK/simplestories/snapshot" \
  --prompts "$STUDY/prompts.json" --output "$WORK/split-audit.json"
```

Any overlap, missing input or empty split blocks admission. Preserve that report;
resolve contamination through a new native preparation identity before training,
then rerun to a fresh report path. Never silently edit a verified snapshot or
remove inconvenient evaluation outputs. The audit checks exact decoded text and
case-sensitive full-prompt substrings only, not semantic near-duplicates.

```sh
sparselab data prepare "$WORK/run-$ARM.yaml"
# PREPARED is the actual directory reported by prepare, not a guessed cache key.
sparselab data coverage --prepared-root "$PREPARED" --config "$WORK/run-$ARM.yaml" --json
sparselab inspect "$WORK/run-$ARM.yaml" --json
sparselab data prepared-inputs publish "$WORK/run-$ARM.yaml" --output "$WORK/prepared-$ARM"
sparselab data prepared-inputs verify "$WORK/run-$ARM.yaml" "$WORK/prepared-$ARM"
```

Save native counts, corpus/manifest/tokenizer identities, exclusions, block tails,
and usable supervised targets per pass `U` for each arm. Check normalizer,
concatenated next-token packing and EOS policy match. Report processed targets
`T` and `T/U` separately at each checkpoint. `T/U` is exposure-equivalents, not
necessarily observed complete passes under the loader's sampling/cursor policy.
Unique supply means corpus positions, not distinct vocabulary IDs. A billion
processed targets does not mean a billion unique training tokens. Different `U`
and repetition are part of this bounded-source treatment; an equal-unique-supply
study would be a separate experiment.

## Train and evaluate

After input/panel admission, use the existing [native lifecycle](../tinystories/README.md#runbook):
stage each configuration through warmup on the authorized ROCm runtime, train a
fresh run through 256 updates, verify its full-state generation, then resume with
a fresh child ID to completion under the unchanged full schedule. Run sequentially
in declared order TinyStories then SimpleStories. Stop at the quality milestones
with `--stop-after-step` when useful for inspection; retain and resume native full
state. Do not promote pretrained weights or reset the schedule between checkpoints.
Record preparation, warmup, optimizer, checkpoint, evaluation, generation and
whole-command time separately, plus VRAM/RSS, failures and energy only if metered.
Order is not counterbalanced, so timing differences are observational.

Before training, bind **two immutable native heldout panels**, one per source,
using [protocol.json](protocol.json)'s selection and the `HeldoutPanel` schema in
Lab `sparselab.evaluation.panels`. Required bindings are `prepared_path`,
`prepared_manifest_sha256`, and the tokenizer file/canonical hashes. Set
`schema_version=1`, `purpose=development`, and names `source-tinystories` /
`source-simplestories`. Bind `checkpoint_sha256` only when each checkpoint is
available. Freeze all other selection fields and digests beforehand. If fewer
than 65,536 usable targets are available, stop rather than evaluating a shorter
panel. No invented placeholder digest is a valid panel.

For both arms at each of the three quality checkpoints (and initial checkpoints
as a sanity check), evaluate on **both** panels with native commands:

```sh
sparselab checkpoint verify "$GENERATION" --json
sparselab eval "$RUN_ID" --runs-dir "$WORK/runs" --checkpoint "$CHECKPOINT" \
  --backend rocm --panel "$BOUND_PANEL" --output "$NEW_RESULT"
sparselab report "$RUN_ID" --kind run --runs-dir "$WORK/runs" --json
```

Keep inference runtime/precision identical. Require native complete evidence,
65,536 valid targets and matching native comparison groups **within each panel**.
Publish a 2×2 train-source/eval-source matrix at each budget. Compare arms within
columns; do not compare or pool the absolute losses of different corpora, or use
each arm's own inline loss as the A/B verdict. If a native comparison refuses,
preserve the reason and fix the protocol rather than calculating an unofficial win.

## Surface the stories, including failures

The [12 fixed authored openings](prompts.json) are new development prompts;
their training disjointness is pending the audit, not assumed. Check each prompt
tokenizes within 256 tokens so 256 new tokens fit strict 512 context. At each
quality checkpoint generate greedy and temperature-0.7/top-k-40 continuations,
seed 42: **24 outputs per arm per checkpoint, 144 total**. Use the existing public
`load_run` / `generate_with_token_ids` API as in the
[learning-rate study](../tinystories/learning-rate/README.md). Preserve prompt and
completion IDs, checkpoint identity, stopping reason, timing, errors and full
decoded text. Use native termination evidence; do not infer EOS by retokenizing.

Before training, an operator creates independent random A/B permutations per
prompt/mode/checkpoint pair and publishes a digest commitment, keeping its mapping
out of the review packet. Freeze [rubric](rubric.json) scores before revealing
dataset/run identities. Report reviewer type, missing/censored scores and paired
criterion distributions. The same reviewer who inspects named training outputs
cannot claim independent blinding. If blinding fails, label the assessment unblinded.

Publish compact sanitized evidence under a new dated `results/` directory:

- Native run/checkpoint IDs, input hashes, actual processed and unique-supply
  accounting, loss matrices and phase timings; no private host names or paths.
- All 144 generation records, blind packet, commitment/reveal, scores and errors.
- A short findings page at each milestone. Include the first largest paired
  continuity/causal-score gap (ties by prompt ID/mode), a failure from each arm,
  and any coherent unusual continuation, with links into the complete output set.
  Explain highlight selection and distinguish reviewer impressions from metrics.

No new outputs exist yet. Existing learning-rate examples are historical evidence
only and must not be presented as results of this source comparison.

## Interpretation and local validation

This is one paired seed, bounded source-order slices, one small prompt panel and
a tokenizer fitted on TinyStories. Tokenization efficiency, repetition and source
coverage may mediate observed differences; it is not a tokenizer-neutral dataset
ranking. Do not claim creativity or general superiority from loss alone. Confirm
promising effects with additional paired seeds and fresh evaluation in a later
declared study, without changing this study after seeing outputs.

Offline checks (no corpus, training or GPU):

```sh
python3 -m unittest discover -s tests -p 'test_story_source_comparison.py' -v
WORKSHOP_LAB_CHECKOUT=/path/to/pinned/lab \
  python3 -m unittest discover -s tests -p 'test_story_source_comparison.py' -v
```

The native check validates both RunConfig declarations and rejects mismatched
retention boundaries. It requires Pydantic and the pinned Lab source, not Torch.
The stdlib fixtures verify matching controls, budget arithmetic and rejection of
contaminated/empty snapshots. These tests establish declaration/audit behavior;
source locking, native source-loader validation, corpus checks, host resource
measurements, training and inference remain pending.
