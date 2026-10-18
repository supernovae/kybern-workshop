# Useful story demo: current-interface reproduction backlog

Owner direction on 2026-10-17 is to reproduce or regenerate experiments using
current native interfaces. The old records below are scientific evidence only.
Do not build candidate-recovery tooling, backward v2/v3/v4 adapters, or a legacy
checkpoint compatibility path. This backlog does not authorize training,
acquisition, model generation, downloads or publication.

The website needs meaningful continuations. The 40-update microlab validates a
small workflow design; it is not evidence of useful story quality. A fresh
reproduction must specify its scientific configuration and current artifact
contracts before a separately approved run.

## Historical reference only

Historical source: Lab `eab014ef7ca92de89d37b47c30df2ebf021d9473`,
`experiments/research/history/tinystories-dense-30m-data-rich-v1/`.
See the [pinned result](https://github.com/supernovae/tiny-sparse-lab/blob/eab014ef7ca92de89d37b47c30df2ebf021d9473/experiments/research/history/tinystories-dense-30m-data-rich-v1/results.md)
and [endpoint receipt](https://github.com/supernovae/tiny-sparse-lab/blob/eab014ef7ca92de89d37b47c30df2ebf021d9473/experiments/research/history/tinystories-dense-30m-data-rich-v1/endpoint-receipt.json).

- Run `tinystories-dense-30m-data-rich-v1-seed42`.
- Generation `step_00024576_gen_000014`.
- Generation manifest SHA256 (`generation_manifest_sha256`) `1f090d8aaa2afc9ac38282917fdd8454fbf2682abca3aaa4ee9ab7e0e3abcdb1`.
- Separate checkpoint manifest SHA256 (`checkpoint_manifest_sha256`) `b02fe9910963677c606940af23367d0cdf83eaf95ccf58f1b78714a6eb797361`.
- Tokenizer SHA256 `4c351be179075c1d4884bf043303e113dd905edaaf398ac4d7842068496c3ac3`.
- 29,893,120 parameters, 512-token context, 100,663,296 training targets.

These labels follow the preserved [triage integrity fields](https://github.com/supernovae/kybern-workshop/tree/fd259e2cad4e9856d6d659e8df34728a98b32502/provenance/lab/experiments/research/history/tinystories-dense-30m-data-rich-v1/evidence.json)
and [endpoint receipt](https://github.com/supernovae/kybern-workshop/tree/fd259e2cad4e9856d6d659e8df34728a98b32502/provenance/lab/experiments/research/history/tinystories-dense-30m-data-rich-v1/endpoint-receipt.json).
The historical receipt also calls the generation-manifest value `checkpoint_digest`;
that label does not identify a verified weight file. Neither digest above is a
weight-file SHA256. The preserved historical verification claim is not a fresh availability or
integrity check. These identities are comparison evidence only, not instructions
to locate or restore the old weights.

The 2026-10-17 handoff reported weights absent on the chief VM and availability on
CPU/ROCm hosts unknown. This records a historical observation, not a recovery task
or current inventory guarantee. Reuse permission and publication rights remain
unverified. This was
an **unpromoted decoder-sensitive finding**, including repetitions and color
contradictions. Its held-out loss is not proof of usable stories. Preserve the
opened historical tests and failures; do not rebrand them as fresh evaluation.
The external TinyStories-33M model card describes GPT-Neo/MIT, but that model is
not a drop-in native DenseLM checkpoint. No model download is included here.

## Fresh reproduction backlog

1. Select reviewed current Lab and Workshop revisions and author a native
   preparation/training/evaluation recipe. Preserve the historical study's
   scientific settings where reproducible, and record every deliberate change
   instead of silently inheriting old runtime paths or formats.
2. Bind the currently supported source, tokenizer, prepared-data and checkpoint
   contracts. Record exact source revisions, licenses, train/validation selection,
   tokenizer fitting boundaries and generated artifact identities. No fabricated
   weights, hashes or model IDs may stand in for missing outputs.
3. Review a complete resource proposal for acquisition, preparation, training,
   checkpointing and evaluation. The old ROCm runtime is not a CPU estimate.
   No fresh training budget or execution permission is granted here.
4. After an approved fresh run produces verified artifacts, assess all frozen
   prompts below through current native generation/evaluation interfaces. Retain
   every output and failure with the new run/config/tokenizer/checkpoint identities.
   Do not point future commands at the historical run ID merely to complete a demo.

The historical 30M configuration is a reproduction starting point: eight layers,
hidden width 512, FFN 1408, vocabulary 8192, context 512, and
24,576 updates/100,663,296 targets. These settings are evidence from the old
experiment, not an approved fresh workload. Source availability, scientific
comparability, runtime compatibility, CPU capacity, disk, time and quality criteria
must be resolved in the new recipe. If a required current interface is missing,
record that gap; do not solve it with a legacy adapter or Workshop Python runner.

## Proposed evaluation after an approved reproduction

`story-greedy.json` and `story-sampled.json` preserve six fixed development prompts
and decoder settings: twelve continuations, at most 192 new tokens each. Their
historical `checkpoint_selection` is provenance from the original proposal and
must be explicitly rebound in a new reviewed declaration to the fresh artifact;
it is not a recovery target or executable binding for this backlog.

Native GenerationPanel is descriptive and does not judge quality automatically.
The currently inspected Campaign generation_panel route requires an authenticated
evaluation index and runtime/checkpoint bindings; the portable workflow profile
does not include those stages. Verify these public interfaces against the selected
current Lab revision when authoring the new recipe. No custom runner is proposed.

For a fresh artifact, retain native checkpoint inspect/verify JSON and raw generation
JSON (`format`, `prompt`, `response`, `identity`, `generation`, `prompt_tokens`, plus
all native fields). Keep strict context refusal visible within the 512-token total.
Retain stdout/stderr, selected and unselected continuations, failures, timing and
memory observations. A website may display authenticated captured JSON; do not
fabricate outputs or expose a private loopback server as a public endpoint.

The earlier inference-only proposal was four CPU threads, a 30-minute whole-job
deadline, a 4 GiB observed RSS stop target with headroom, and at most 64 MiB new
output. These remain unapproved proposals, not measured performance, hard memory
enforcement or a fresh training envelope. Storage estimates from the old record
(222,549,446 int32 IDs, about 890 MB; FP32 parameters about 120 MB) exclude optimizer
state, copies and temporary storage. Measure actual current artifacts before a
future approved job. There are no automatic retries.

Proposed human demo-quality gate: at least 10/12 longer outputs are relevant and
understandable, with consistent characters and event sequences; score repetition,
contradictions and endings separately. Freeze the rubric before results. This is
not a statistical general-quality claim. Prompts are development material, not
claimed train-disjoint holdout. Preserve failures and do not cherry-pick outputs.

The first three prompts match website draft kybern
`69139e888c0b9ece8a890dfcabc95f2c89077859`,
`assets/js/tinystories-story.mjs`. `story-website-baseline.json` preserves those
three prompts at 48 new tokens, greedy decoding and seed 42; its historical
checkpoint selection likewise requires fresh explicit rebinding. The other three
prompts remain additional development inputs. If both evaluation scopes are later
approved, retain all 15 outputs: three 48-token website baselines plus twelve
192-token outputs. The proposed 10/12 rubric applies only to the longer panel.
Do not equate the two budgets or claim one validates the other. The website viewer
accepts raw native JSON up to 1 MiB; preserve the actual decoder and budget.
These declarations contain prompts, not generated outputs. No website change is
made here.
