# Fresh v2 experiment protocol

## Model and data budget

The recipe keeps the dense backbone: 24 layers, 1,024 wide, 2,816 FFN, 16 heads,
32,768 vocabulary, tied embeddings, RoPE and 4K context. Engram memory uses
context-key injection after blocks 1 and 14, 2- and 3-grams with two hash heads,
eight prime-sized tables and a causal width-4 convolution. Engram is there from
step zero. v2 starts from fresh weights; it doesn't warm-start from the dense
model or convert a v1 checkpoint.

The proposed budget is 10,256,578,560 unique supervised targets, with these
quotas: web 5,128,289,280; notebooks 1,538,486,784; math 2,051,315,712;
instruction 1,025,657,856; reference 512,828,928. These are what the run needs,
not what we have. We choose sources and count usable inventory after code
qualification. Don't publish screened counts as available capacity, fill missing
quotas with duplicates, or quietly rebalance the recipe. If the scientific
settings change, give the recipe a new name. Data that v1 trained on can still be
used for fresh weights, but held-out, benchmark and duplicate-family protections
still apply across all pillars.

Preparation must keep document IDs, cross-pillar content clusters, source and
shard revisions, the tokenizer hash and exact target/EOS counts. Keep notebooks
split by repository/family, but don't collapse every notebook in a repository to
one document. Review quality and truncated or incomplete outputs before
admission. Reuse raw data when it is still valid; never reuse v1 cursors. Keep
validation and final-test families out of training and selection.

## Updates, optimizer and storage

Group whole documents into updates of about 131,072 targets. Padded document
microbatches hold four documents, use padding multiple 64, and are capped at
8,192 padded slots and 16,777,216 attention cells. The engine sets the actual
group totals; don't compute them from nominal sizes. There are no historical
frozen update boundaries or regrouping step. The final schedule must be built
from the checked packed groups.

AdamW peak 6e-4, floor 6e-5, 1,000 warmup steps, betas 0.9/0.95, epsilon 1e-8,
weight decay 0.1, gradient clip 1.0; memory table LR multiplier 5 and table decay
zero. These are starting guesses that we haven't yet tested for stability. Record
finite loss and gradients and the actual LR through warmup before committing to a
long run. Don't carry over an old short decay horizon or an already-decayed floor.

Checkpoint every 25M committed targets. Bounded retention keeps the latest,
previous, best and terminal checkpoints, with no growing periodic archive. The
current storage plan allows four generations of at most 5 GiB each, 20 GiB
retained, 25 GiB peak write headroom and 100 GiB reserve free space. Measure
full-state sizes (weights, optimizer, RNG and metadata) on the chosen model and
devices before launch. Raise the limits explicitly if needed; never drop
optimizer state to make the numbers fit. The terminal target and step come from
Lab's measured schedule. The default keep-set has no milestones; adding one means
raising every related retention limit. Independent backups sit outside the active
retention budget.

## Evaluation and acceptance

The fixed validation config binds one separately checked panel per pillar: web,
notebooks, math, instruction and reference. Each proposed panel is 64 blocks ×
4,096 positions, evaluated at batch size one every 100 updates. Fill in the exact
measured supervised targets; not every position is a label. Keep the same panel
and tokenizer hashes across comparisons, and don't let the aggregate loss hide a
failing pillar. The engine reports each panel and the combined loss separately.
Check the source-family split before publishing anything.

`probe-standard.json` runs held-out loss, degeneration, calibration, fact recall
and needle screening. `probe-full.json` adds LAMBADA, HellaSwag, ARC-Easy, PIQA
and SciQ at 100 examples each. That is a quick screen; for paper-level numbers
you'd need the full benchmarks. `probe-final.json` runs on the untouched final
split, once, for the candidate you've already picked. Keep task, sample and
version, checkpoint and tokenizer hashes in the Lab records. A missing result
counts as a fail. Don't execute generated code without a separately qualified
sandbox.

Before judging whether the model is useful, freeze a separate generation
assessment that covers: executable Python completions with tests, simple
arithmetic with exact answers, format-sensitive instruction following, factual
reference answers, and repetition. The standard probes don't measure all of
these. Until a reviewed task suite, scorer and baseline are in place, treat those
capabilities as **unmeasured**. We haven't included any made-up pass criteria or
baselines here. Use Lab's generation, controlled benchmark or optional code-work
tools rather than a Workshop scorer. The `model exercise` command is built for
the dense reference model: it requires memory disabled and fixed batch
accounting, so it can't evaluate v2 Engram. Optional code-work needs its own
sandbox and a reviewed task and scoring config, and this scaffold doesn't turn it
on.

Stop the run on any of these: nonfinite loss or gradients, a prepared, tokenizer
or panel hash mismatch, running out of unique data, a failed full-state
checkpoint check, a failed resume-equivalence check, going over the storage
limits, or an accelerator the run doesn't own. Throughput and finite-gradient
checks need a real, separately approved run; the offline fixture tests don't
cover them. If a probe fails, investigate. Changing a threshold means a new suite
name; never tune the gate until it passes.

## Recovery

A fresh run gets a new run ID, output directory, initialized weights, optimizer,
random state and counters. Recovery resumes only a checked generation from the
same v2 run. Keep the terminal and best full-state generations, the tokenizer,
resolved config, code revision and local source changes, the environment and
dependency manifest, prepared arrays, and the source release, split, family and
selection records with their checksums. Keep interrupted runs and negative
results. Lab's engine fixtures test restart equivalence; test real recovery
separately on the runtime you chose.

Before resetting any drive, copy everything recovery depends on to physically
separate storage, check the copied bytes, restore from the copy and test
recovery. A separate mountpoint can still be the same physical device. This
package has no cleanup or reset command and doesn't assume any backup is
complete.
