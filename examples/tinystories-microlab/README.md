# TinyStories microlab: learn a controlled FFN-width comparison

This **native Lab recipe is runnable by design but unexecuted**. It selects 2,000 training and 100 validation
stories, fits a train-only 2,048-token BPE, and compares FFN width 256 with 384.
Both arms use seed 42, two layers, hidden width 128, four attention heads,
64-token training sequences and at most 40 main updates / 10,240 targets.
It teaches the workflow; it is not evidence of a useful story model.

The recipe is declarative YAML plus documentation. All loading, preparation,
training, evaluation and reporting are native Tiny Sparse Lab functions. No
Workshop Python, Harness, bot, Notion account or website is required. The
[usable-story validation proposal](usable-story-proposal.md) is a separate path
for the website's meaningful model requirement; do not promote this teaching
run merely because its commands succeed.

## Runtime and provenance

Use an existing installed Lab environment compatible with the recorded source
revision. The exact imported declarations come from Lab
`eab014ef7ca92de89d37b47c30df2ebf021d9473`; [migration.json](migration.json)
records all 11 source/destination hashes. The original metadata validation used Lab PR162
`408835184bf7020c10bdd2e8b7115e196322cf2b`; that interface is now merged.
[Current metadata acceptance](../../docs/native-acceptance-2026-10-18.md) uses Lab
`7e306a96bcc617468d2a06493dab4562bff6beb0` without executing the recipe. Bind the
separately reviewed source/runtime and dependency lock before execution. No install or image pull is
part of these instructions. Existing CPU support is the reference; GPU changes
need separate runtime qualification and budget.

The imported `declarations/README.md` and `acceptance.md` retain original bytes
and historical references. This guide is the current public entrypoint. The
advanced campaign expects its own `inputs/` layout; do not run that campaign
from this directory without following its native layout contract. The primary
route below needs only source, tokenizer and run declarations plus the delta.

## Create a fresh external workspace

Bash example from a Workshop checkout. Choose an unused absolute directory
outside Git. An existing destination is refused; earlier evidence is preserved.

```sh
RECIPE=examples/tinystories-microlab
WORK="$HOME/sparselab-experiments/tinystories-microlab-001"
mkdir -p "$(dirname "$WORK")"
mkdir "$WORK"
cp -R "$RECIPE/declarations" "$WORK/declarations"
cp "$RECIPE/wider-ffn.yaml" "$RECIPE/try.yaml" "$WORK/"
mkdir "$WORK/evidence"
```

Native config paths resolve relative to `declarations/`: `../snapshot`,
`../tokenizer`, `../data` and `../runs` stay in WORK. `try.yaml` instead selects
WORK/lab for native paired runs and sealed records. Keep output/cache roots
writable; do not use symlinks to old evidence. These files can be copied into
any user repository/local directory; our repository URL is provenance only.

## Inspect before doing work

These native schema/derivation commands neither acquire inputs nor train:

```sh
sparselab config validate "$WORK/declarations/run.yaml" --kind run --json
sparselab config validate "$WORK/declarations/tokenizer.yaml" --kind tokenizer --json
sparselab config derive "$WORK/declarations/run.yaml"   --set 'model.ffn_dim=384' --output "$WORK/candidate-preview.yaml" --json
```

The candidate preview and its `.derivation.json` sidecar bind the proposed
change. It is not a trained artifact. Inspect the delta to confirm that width
is the only scientific intervention. Native validation reports unavailable
runtime/artifact evidence honestly; it does not make downloads or execution safe
by itself. Use the installed Lab command's help to inspect supported options.

## Prepare once, then run the comparison

The following commands do real work and require the applicable owner approval
and a finite resource allocation on our runners. Public users choose their own
permitted environment. Nothing was executed while authoring this recipe.

The source pins `roneneldan/TinyStories` revision
`f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`, CDLA-Sharing-1.0, with explicit
attribution. Selection prioritizes validation and excludes exact duplicates and
overlap. Review access/terms before acquisition. Selecting 2,100 stories and
limiting snapshot text to 16 MiB does **not** cap upstream Parquet/network/cache
bytes; budget the actual source file inventory before downloading.

```sh
sparselab data lock "$WORK/declarations/source.yaml"   --output "$WORK/source.lock.json"
sparselab data snapshot "$WORK/source.lock.json" --output "$WORK/snapshot"
sparselab tokenizer train "$WORK/declarations/tokenizer.yaml"
sparselab try "$WORK/wider-ffn.yaml" --vs "$WORK/declarations/run.yaml"   --config "$WORK/try.yaml" --backend cpu --json
```

Snapshot output includes train/validation JSONL and an authenticated manifest.
Tokenizer output includes `tokenizer.json` and `tokenizer_manifest.json`. `try`
performs native data preparation, model work, and shared held-out scoring;
`probe_tier: none` deliberately excludes optional probe work. Smoke/warmup stages
are still separate native work: the 40-update figure is the main-run cap, not a
promise of total work across all stages. Preserve actual counters and failures.
The 2,000,000-token prepared train cap is not the 10,240-target training budget.

Record the returned try ID and both run IDs. Read the sealed result, including
failed/interrupted outcomes, with:

```sh
sparselab report TRY_ID --lab-dir "$WORK/lab" --json
```

Expected evidence: source lock, snapshot/tokenizer manifests, native prepared
cache, baseline/candidate configurations and checkpoints, and the sealed try
record under WORK/lab. Save stdout/stderr and real exit statuses through your
chosen terminal or supervisor. No automatic retry or cleanup script is provided.
A fresh invocation is not a promise of replay; native identity/reuse rules apply.

## Interpret and extend

Compare actual targets, identical tokenizer/split/seed and held-out scoring
before interpreting loss. One seed and short training do not establish a width
advantage or story quality. Increase both arms' budgets together under a separate
reviewed allocation; use `config derive` to make an explicit new configuration.
Keep previous results and avoid selecting repeatedly against final holdout data.

For a generation example from an actual completed run, supply its real run ID,
checkpoint and native run-store path to `generate`; see the separate proposal.
Missing checkpoints are a blocker, not a reason to fabricate story output.

## Reconciliation with earlier work

- Paused [PR3](https://github.com/supernovae/kybern-workshop/pull/3) packaged this
  original microlab. This destination preserves all 11 native declarations and
  records; it does not silently revive or close that historical PR.
- Merged [PR13](https://github.com/supernovae/kybern-workshop/pull/13) and
  [PR17](https://github.com/supernovae/kybern-workshop/pull/17) describe a distinct
  64/16-story, vocabulary-512, one-layer width-32, FFN64-to96 smoke. Its recorded
  CPU result is not this recipe's measured result or GPU validation.
- The hosted accelerator sample and historical data-rich 30M study are separate
  identities. Their Lab retirement requires matching destinations, not this copy.

[Validation](VALIDATION.md) records metadata-only evidence. The coordinated Lab
retirement removes the matching current sample only after this destination is
verified; Git history retains provenance. No new corpus, tokenizer or model
execution is claimed by migration.
