# Fresh v2 experiment protocol

## Scientific proposal, not admitted capacity

The recipe retains the 24-layer/1,024-wide/2,816-FFN dense backbone with 16 heads,
32,768 vocabulary, tied embeddings, RoPE and 4K context. Its Engram memory uses
context-key injection after blocks 1 and 14, 2/3-grams with two hash heads, eight
prime-sized tables and a causal width-4 convolution. Engram starts at step zero;
this is neither a dense warm start nor a conversion of a v1 checkpoint.

The proposed budget is 10,256,578,560 unique supervised targets. Proposed quotas:
web 5,128,289,280; notebooks 1,538,486,784; math 2,051,315,712; instruction
1,025,657,856; reference 512,828,928. These are requirements, not counts. Source
selection and usable inventories remain deferred until code qualification. Do not
publish screened counts as admitted capacity, fill missing quotas with duplicates,
or silently rebalance the recipe. Change its identity when its scientific settings
change. Prior training exposure alone does not disqualify data for fresh weights;
heldout, benchmark and duplicate-family protections still apply across all pillars.

Native preparation must preserve document IDs, cross-pillar content clusters,
source and shard revisions, tokenizer identity and exact target/EOS accounting.
Keep repository/family split separation for notebooks without collapsing every
notebook in a repository to one document. Review quality and truncated/incomplete
outputs before admission. Reuse immutable raw data when valid; never reuse v1
cursors. Keep validation and final-test families untouched by training and selection.

## Updates, optimizer and storage

Use whole-document story groups targeted at 131,072 targets/update. Padded document
microbatches have size four, padding multiple 64, maximum 8,192 padded slots and
16,777,216 attention cells. The engine, not nominal arithmetic, determines actual
group totals. No historical frozen update boundaries or regrouping transition is
present. Final schedule authoring must read verified packed groups.

AdamW peak 6e-4, floor 6e-5, 1,000 warmup steps, betas 0.9/0.95, epsilon 1e-8,
weight decay 0.1, gradient clip 1.0; memory table LR multiplier 5 and table decay
zero. These are starting hypotheses, not validated stability settings. Record
finite loss/gradients and actual LR through warmup before committing a long run.
Do not inherit an old short decay horizon or already-decayed floor.

Checkpoint every 25M committed targets. Native bounded retention keeps latest,
previous, best and terminal with no periodic archive growth. The current storage
proposal allows four generations of at most 5 GiB each, 20 GiB retained, 25 GiB peak
write headroom, and 100 GiB reserve free. Measure full-state sizes (weights,
optimizer, RNG and metadata) on the chosen model and devices before launch. Raise
limits explicitly if necessary; never omit optimizer state to fit the estimate.
Terminal targets and steps come from the native measured schedule. There are no
milestones in the default keep-set; adding one requires increasing all related
retention bounds. Independent backups are outside the active retention budget.

## Evaluation and acceptance

The native fixed validation declaration binds one independently authenticated
panel per pillar: web, notebooks, math, instruction and reference. The proposed
panel size is 64 blocks × 4,096 positions, evaluated in batch one, every 100 updates.
Fill exact measured supervised targets rather than assuming every position is a
label. Preserve panel/tokenizer identities across comparisons; do not use aggregate
loss to conceal a failing pillar. The engine reports each panel and the combined
loss separately. Source-family split verification happens before publication.

`probe-standard.json` runs native heldout loss, degeneration, calibration, fact
recall and needle screening. `probe-full.json` additionally specifies LAMBADA,
HellaSwag, ARC-Easy, PIQA and SciQ at 100 examples each. This bounded slice is a
screen, not a paper-level benchmark. `probe-final.json` selects the native untouched
final split, once, for the already-selected candidate. Keep task/sample/version,
checkpoint and tokenizer identities in the native records. Missing evidence never
passes. Do not execute generated code without a separately qualified sandbox.

Before interpreting usefulness, freeze a separate generation assessment covering:
executable Python completions with tests, simple arithmetic with exact answers,
format-sensitive instruction following, factual reference answers, and repetition.
Native standard probes do not measure all these tasks. Until a reviewed task suite,
scorer and baseline are bound, those capability claims remain **unmeasured**. No
synthetic pass criteria or invented baseline is included here. Use compatible native generation, controlled benchmark or optional code-work
facilities rather than a Workshop scorer. The specialized `model exercise` dense
reference contract requires memory disabled and fixed batch accounting; it is not
a v2 Engram evaluator. Optional code-work needs its separately provisioned sandbox
and reviewed task/scoring declaration; it is not enabled by this scaffold.

Hard engineering stops: nonfinite loss or gradients, prepared/tokenizer/panel hash
mismatch, exhausted unique data, failed full-state checkpoint verification, failed
resume equivalence, storage envelope violation or unowned accelerator. Runtime
throughput and finite-gradient observations require separately authorized actual
work, not these offline fixture tests. Native probe failures require investigation;
threshold changes require a new suite identity, never tuning the gate to pass.

## Recovery closure

A fresh run has a new run ID, output directory, initialized weights, optimizer,
random state and counters. Recovery resumes only a verified generation from that
same v2 lineage. Preserve the terminal and best full-state generations, tokenizer,
resolved config, code revision and local source changes, environment/dependency
manifest, prepared arrays, source release/split/family/selection closure and checksums.
Keep interrupted and negative evidence. Verify restart equivalence in native engine
fixtures and validate operational recovery separately on the chosen runtime.

Before any drive reset, copy the entire dependency closure to physically independent
storage, verify destination bytes, restore it and test recovery. A separate mountpoint
is not evidence of a separate physical device. No cleanup/reset command is provided
and no backup is presumed complete by this package.
