# TinyStories: build a model that can tell a story

**Queued proposal, unexecuted.** [PR3](https://github.com/supernovae/kybern-workshop/pull/3)
stays open until real evidence is reviewed. This is a fresh single-model recipe,
separate from the 40-update FFN teaching comparison. No old 30M weights are reused.
A successful pipeline is insufficient: users must get recognizable, coherent
stories from a model they build through Lab. Quality is not guaranteed in advance.

## Candidate pins and unresolved bindings

- Lab: `3860be8f15af9a0d16433fee03d8a172a62dc8d4`.
- CPU image: `ghcr.io/supernovae/tiny-sparse-lab@sha256:6d0172d1c24a049e3b42eaafff203d7ac423d8c9f8ed2149e4b57ac576ee7bf8`.
  [Existing smoke/publication](https://github.com/supernovae/tiny-sparse-lab/actions/runs/39149272632)
  passed. Cache presence, installed runtime, host capacity and job approval are
  unverified. Do not pull/install or activate this candidate from these docs.
- Workshop base: `1f9a5415c8e2eee808a7680f71ef4ee6799efbe6`; use this proposal's
  exact reviewed PR head as the recipe pin, never a moving branch.
- Input: `roneneldan/TinyStories`, revision
  `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`, default config, train/validation,
  CDLA-Sharing-1.0 with attribution in `source.json`.
- **Not yet bound:** native source lock and ordered authenticated Parquet file
  inventory, lock identity, descriptor/inspection digests, selected interpreter,
  fresh work/run IDs, owner approval, host admission and all generated outputs.
  No compatible existing payload has been established; reuse is not assumed.
  The exact Parquet filenames and aggregate file bytes are unknown. Original
  text-file or V2 text-file sizes are not substitutes for the selected inventory.

`admission.template.json` is deliberately invalid until actual identities are
bound and reviewed. It is a proposal, not approval. Input revision alone does not
prove selected file sizes, scalar decoder compatibility or payload availability.

## Proposed finite workload

| Item | Proposed value; not authorization or measured performance |
| --- | --- |
| Model | Dense tied-embedding model; 4 layers, width 256, FFN 768, 4 heads, vocabulary 4096, context 512; 4,458,752 unique parameters, including 3,410,176 nonembedding parameters (source-derived; runtime inventory pending) |
| Data | First 50,000 admitted training stories and 512 validation stories; validation-first exact dedup/overlap exclusion; BPE fitted only on training, at most 50,000 documents |
| Prepared tokens | At most 16,000,000 train and 131,072 validation tokens; these are input caps, not training targets |
| Main training | Seed 42; CPU PyTorch FP32, deterministic; sequence 256 × microbatch 4 × accumulation 4 = 4,096 targets/update; 8,192 updates / 33,554,432 targets; planned stop/review at update 1,024 |
| Separate staging | Two smoke and five warmup updates; record actual work separately; no extra tuning trials |
| Validation | 16 batches at step zero and each 1,024 updates; one final native `eval`; retain actual counts, losses and failures |
| Checkpoints | Every 1,024 steps, no retained periodic history; preserve native latest/best/predecessor and all closure files required by the terminal generation |
| Generation | Six early development outputs x 192 tokens; final 24 x 192 plus 3 x 48 baseline outputs = at most 5,904 new tokens; no resampling |
| CPU/RAM | Eight library threads proposed, not a hard quota; no GPU; native monitor 16 GiB observed process-tree RSS stop; actual capacity pending |
| Disk | Preparation admission proposes 40 GiB free and 100,000 free inodes; native monitor proposes 20 GiB added workspace stop, including both run closures |
| Whole session | Proposed aggregate cap 24 hours including waits and cleanup; cumulative enforcement remains unbound. Sub-allowances: metadata 10 min, preparation 2 h, train/stage 21 h, eval/generation 40 min, cleanup 10 min |
| Acquisition | 2 GiB charged source bodies, 16 MiB charged acquisition metadata, 128 requests, 8 transfers, zero retries/shard; private cache 2 GiB / 16 files; 1M scanned rows; 16 GiB logical verification charges; persistent 2 h deadline |
| Snapshot | 128 MiB selected UTF-8 text, 50,512 selected records, 1 MiB/record; source declaration allows ≤1M records/split; cumulative transport scan ≤1M; snapshot work cap 1 GiB |
| Retry/stop | No automatic retry, extension, model change or second training attempt. Preserve partial receipts, exit/signal and charged ledger; parent reviews any failure before new authority |

The 24-hour bound is a stop condition, not an ETA or promise of completing 33M
training targets. Native staging timing and the early development tranche inform whether
the fixed attempt is feasible; if not, stop and report, without silently reducing
the quality goal or switching to a GPU. RSS/storage observations can overshoot;
there is no hard RAM/disk guarantee. A native monitor records each command. Independent monitor invocations do not
enforce a cumulative deadline. Before launch, bind an existing supported accounting
route or explicitly revise the proposed aggregate limit to supported per-command
bounds. Do not build a bespoke supervisor for this example.
End users need only Lab and a permitted runtime; Harness is not a recipe dependency.

## Native workflow (only after the missing bindings and approval)

Choose an unused absolute `WORK` outside Git, an absolute `SOURCE` pointing here,
unused `FIRST_RUN_ID` and `CONTINUED_RUN_ID` values, and the pinned installed
`sparselab` command. Final `RUN_ID` selects the continued child. Preserve stdout,
stderr and real exit codes for every command in unique files; `set -C` prevents
shell redirection clobber. Do not pipe failures into commands that hide status.
All commands below are future work except the recorded metadata checks.

Before any child launch, propose these library settings in the selected Linux CPU
runtime (they do not enforce a CPU quota or process-wide thread cap):

```sh
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
export OPENBLAS_NUM_THREADS=8
export NUMEXPR_NUM_THREADS=8
export TOKENIZERS_PARALLELISM=false
```

### 1. Select and authenticate data

```sh
sparselab data lock "$SOURCE/source.json" --output "$WORK/source.lock.json" --cache-dir "$WORK/lock-cache" --json
```

**Stop for review of the real lock.** This command does Hub metadata discovery;
its CLI does not expose the acquisition authority's byte/request caps. A proposed
metadata-only discovery allowance is 600 seconds, 16 MiB of response bodies and
128 requests with no retries; this is a planning preference, not implemented
enforcement or an owner requirement. Discovery
therefore needs its own explicit bounded authorization/transport arrangement
before it runs. A strict enforced metadata-body cap for this command is an open
capability boundary; the acquisition limits below must not be advertised as
covering lock creation. No lock has been generated or fabricated for this proposal.

Copy the four JSON declarations and the resulting native lock into a fresh local
recipe directory `INPUT` using ordinary file copies. Copying metadata supplies no
experiment semantics. Use native inventory creation, not a hashing helper:

```sh
sparselab experiment recipe create "$INPUT" --profile preparation \
  --id tinystories-useful-preparation-v1 --entrypoint preparation-campaign.json \
  --file campaign:preparation-campaign.json --file run_config:run.json \
  --file tokenizer_config:tokenizer.json --file source_lock:source.lock.json \
  --output "$WORK/recipe"
```

Bind `bindings.template.json` as ordinary JSON data to the chosen absolute WORK;
no `eval`, Python renderer or automatic host selection is required. All typed
paths are listed. Inspect with the public native loader:

```sh
sparselab experiment recipe preparation inspect "$WORK/recipe/recipe.json" --bindings "$WORK/bindings.json" --json
```

Review every inventory member and fill `admission.template.json` using the actual
inspection and native lock identities. Use native content admission for the exact
descriptor bytes (`reviewed_descriptor_sha256`); record the separate reviewed
Workshop commit. There is no fake lock or ready-made admission in this checkout.
The snapshot record admission is 2,000,000 (the native sum of 1,000,000 declared
source records × two splits), while the transport scan ceiling remains the
stricter cumulative 1,000,000. Selected output stays at 50,512 stories. The 2 GiB
ceiling may refuse the real inventory; do not increase it silently.

### 2. Prepare snapshot, train tokenizer, pack data

The native Campaign stages are `dataset_snapshot → tokenizer_train → data_prepare`.
They run under the bounded public preparation admission, not custom Python:

```sh
sparselab experiment recipe preparation apply "$WORK/recipe/recipe.json" --bindings "$WORK/bindings.json" --admission "$WORK/admission.json" --work-dir "$WORK" --json
```

Require all three COMPLETE receipts and actual verified output identities. Keep
source/metadata reservations, native snapshot journal and output provenance.
No preparation `resume` is queued; interruption is evidence for review, not automatic retry.

### 3. Bind verified inputs and train

Use `config derive` to bind locations explicitly without changing science. Its
`--set` values are JSON; the escaped quotes below are required for string paths.
Use simple absolute paths without embedded quotes/backslashes in this Bash example.

```sh
sparselab config derive "$SOURCE/run.json" \
  --set "tokenizer.path=\"$WORK/tokenizer/tokenizer.json\"" \
  --set "dataset.cache_dir=\"$WORK/data\"" \
  --set "dataset.train_path=\"$WORK/snapshot/train.jsonl\"" \
  --set "dataset.validation_path=\"$WORK/snapshot/validation.jsonl\"" \
  --set "dataset.source_manifest_path=\"$WORK/snapshot/manifest.json\"" \
  --set "logging.root_dir=\"$WORK/runs\"" --output "$WORK/train.yaml" --json
sparselab tokenizer verify "$WORK/train.yaml" --json
sparselab data prepared-inputs publish "$WORK/train.yaml" --output "$WORK/prepared"
sparselab data prepared-inputs verify "$WORK/train.yaml" "$WORK/prepared"
sparselab stage "$WORK/train.yaml" --through warmup --prepared-inputs "$WORK/prepared" --cold-verify --output "$WORK/stages"
sparselab train "$WORK/train.yaml" --backend cpu --runs-dir "$WORK/runs" --run-id "$FIRST_RUN_ID" --stage-bundle "$WORK/stages" --stop-after-step 1024
```

Stage, publish and verification are real bounded preparation/runtime work, not
metadata checks. Use the retained native stage bundle to avoid a second staging
pass. A throughput forecast that cannot complete within the remaining allowance
is a stop/review result, not permission to change model, budget or hardware.

### Development review and explicit continuation

The first training invocation stops at update 1,024 / 4,194,304 targets while the
configured scheduler horizon remains 8,192. Native source confirms 256 updates of
linear warmup to 0.0006, followed by cosine decay to 0.00006 at update 8,192.
The native planned stop is recorded as `interrupted`, reason `stop_after_step`,
with terminal evaluation and a checkpoint; it is not full-budget completion.

Resolve the actual immutable generation and verify its full closure:

```sh
sparselab checkpoint inspect "$WORK/runs/$FIRST_RUN_ID/checkpoints/latest.json" --json
sparselab checkpoint inspect "$FIRST_GENERATION" --json
sparselab checkpoint verify "$FIRST_GENERATION" --json
sparselab report "$FIRST_RUN_ID" --kind run --runs-dir "$WORK/runs" --json
```

For each of the first six development prompts only, retain one output:

```sh
sparselab generate "$FIRST_RUN_ID" --runs-dir "$WORK/runs" --checkpoint "$FIRST_CHECKPOINT" --backend cpu --prompt "$DEVELOPMENT_PREFIX" --max-new-tokens 192 --temperature 0 --top-k 0 --seed 42 --strict-context --show-prompt --json
```

Keep the final six evaluation prompts unused until final scoring. Review actual
elapsed time, sustained throughput, evaluation/checkpoint overhead, finite losses,
resource observations and all six outputs. These early stories are diagnostics,
not a final-quality gate. If outputs are wholly uninterpretable/repetitive, or a
conservative completion forecast does not fit the remaining approved bounds,
stop for diagnosis. There is no measured forecast margin or guaranteed completion.
No automatic recovery follows an interruption before the planned boundary.

Only after explicit continuation approval:

```sh
sparselab train "$WORK/train.yaml" --backend cpu --runs-dir "$WORK/runs" --run-id "$CONTINUED_RUN_ID" --resume "$FIRST_GENERATION"
```

Native resume creates a fresh child run ID, preserving the first run; it does not
reopen that directory. It restores optimizer/RNG/cursor/step/target state and
continues updates 1,025 through 8,192 under the unchanged scheduler. Do not use
extend-budget, promotion, recovery, runtime drift, or a second staging pass.
This is one scientific training lineage with two execution identities. Preserve
both closures and cumulative resource evidence. Use `CONTINUED_RUN_ID` as `RUN_ID`
for final evaluation. Review waits and continuation must not reset an approved
aggregate budget. All early and final generation share the evaluation allowance.

### Why this is a first attempt, not a quality prediction

The modest dense model and 33.55M-target budget are a finite exploratory CPU
candidate, not an empirically established recipe for the quality gate. Required
throughput is 388.36 targets/second over 24 hours or 443.84 over the proposed
21-hour training allowance, before overhead; neither rate has been measured.
The first 4.19M-target tranche supplies actual timing and development outputs
before authorizing the remainder. Seven staging updates alone cannot do that.

Training length is 256 while architectural context is 512. Strict context guards
architectural capacity, not learned quality beyond training length. Propose keeping
scored outputs within 256 total prompt-plus-generation tokens. The actual tokenizer
and a supported native token-count/admission route must establish whether each
prompt plus 192 tokens fits; this has not been checked. Do not silently truncate
or change the panel. A different evaluation length is a review decision, not an
invented mandatory host control. Longer-context quality remains unproven.

### 4. Verify terminal generation, evaluate and report

Resolve the exact terminal generation from native checkpoint inspection; do not
continue using a moving latest pointer. Set `GENERATION` to its real immutable
directory and `CHECKPOINT` to the corresponding selector accepted by this run.

```sh
sparselab checkpoint inspect "$WORK/runs/$RUN_ID/checkpoints/latest.json" --json
sparselab checkpoint inspect "$GENERATION" --json
sparselab checkpoint verify "$GENERATION" --json
sparselab eval "$RUN_ID" --runs-dir "$WORK/runs" --checkpoint "$CHECKPOINT" --backend cpu
sparselab report "$RUN_ID" --kind run --runs-dir "$WORK/runs" --json
```

Retain weights and checkpoint manifest, resolved config and run manifest,
run-owned tokenizer, required prepared arrays/sidecars, stage/preparation receipts
and source/runtime identities. Checkpoint bytes must verify; the website viewer
only displays identity and cannot authenticate those bytes.

### 5. Generate stories people can inspect

For **each** literal line in `prompts.txt`, invoke the following twice, with
`TEMPERATURE=0 TOP_K=0` and `TEMPERATURE=0.7 TOP_K=40`, seed 42. Save each stdout
JSON and stderr in a unique file; no best-of resampling. Plain shell iteration
may enumerate the fixed lines; it must not implement generation or filtering.

```sh
sparselab generate "$RUN_ID" --runs-dir "$WORK/runs" --checkpoint "$CHECKPOINT" --backend cpu --prompt "$PREFIX" --max-new-tokens 192 --temperature "$TEMPERATURE" --top-k "$TOP_K" --seed 42 --strict-context --show-prompt --json
```

For the first three prompts, also retain the website baseline with 48 new tokens,
temperature 0, top-k 0 and seed 42. Do not treat 48 tokens as the story-quality
budget. Strict context must refuse overflow instead of silently truncating.
After validation, users can try a new prefix using the same native `generate`
command; interactive `surface chat` is optional local UI, not proof of a chat model.

## Meaningful-story acceptance and website contract

Freeze this recipe and all 12 prompts before the run. First six prompts are
published development examples; last six are evaluation prompts withheld from
checkpoint/model selection and tuning. They are newly authored, but their absence
from training data is **not proven**; do not claim a train-disjoint benchmark.
Use the final scheduled checkpoint once. No training adjustment based on these
outputs occurs within this proposal. Additional user-entered prefixes are welcome
for demonstration after scoring, but never replace failed fixed outputs.

Retain all 24 longer outputs, three website baselines, empty outputs, failures and
interruptions. Human scoring records prompt relevance, readable sentence flow,
character/object consistency, event continuity, repetition, and an understandable
ending separately. Proposed demo gate: at least 20/24 longer outputs are relevant,
understandable and consistent, including at least 10/12 outputs from the six
withheld evaluation prompts; at least 18/24 reach an understandable ending within
the budget. An obvious repeated-sentence loop or identity contradiction fails that
output. All operational/artifact checks must pass too. This is a practical demo
criterion, not a general language benchmark or an automatic quality claim.
If it fails, leave PR3/website acceptance open and preserve every result.

The website imports native UTF-8 raw generation JSON ≤1 MiB:
`format: "raw"`, strings `prompt`/`response`, objects `identity`/`generation`, plus
`text`, `prompt_tokens` and all additional native fields unchanged. Preserve
checkpoint/source/tokenizer/data digests, config, step, tokens_seen and exact
settings/context. Use both the three 48-token files and the full scored output
set as evidence; publish examples only with their complete panel and limitations.
Do not fabricate output, imply conversational instruction tuning, or expose a
private loopback service to the public site.

## Monitoring, ownership and helper audit

For example, the future preparation invocation is wrapped as follows; use the
training/evaluation policy and a fresh log directory for those phases:

```sh
sparselab monitor-baseline "$WORK" --output "$WORK/baseline.json" --json
sparselab monitor --policy "$SOURCE/monitor-preparation.json" --baseline "$WORK/baseline.json" --log-dir "$WORK/logs/preparation" --workspace "$WORK" -- sparselab experiment recipe preparation apply "$WORK/recipe/recipe.json" --bindings "$WORK/bindings.json" --admission "$WORK/admission.json" --work-dir "$WORK" --json
```

Use native `monitor-baseline` once for the full workspace and native `monitor`
with the appropriate `monitor-*.json`, unchanged baseline, unique log directory
and exact argv after `--`. Record training and inference time/memory separately.
Use the same storage baseline across phases. Cumulative 24-hour accounting is
pending; per-command monitors alone do not provide it. Resolve this with existing
supported Lab/Harness capabilities or review supported per-command limits instead.
No separate log-size cap, CPU affinity policy, extra free-resource stop floors or
bespoke supervisor is required by this proposal. Timeout/signal/pressure stops preserve
real outcomes and partial evidence. Require verified owned-descendant cleanup;
uncertain cleanup retains its hold. No automatic deletion, stale-lock stealing,
new owner clock, or ledger reset is allowed.

No Python helper is required by this route. Existing `scripts/seal-inputs.py`,
`scripts/workshop.py`, `scripts/handoff.py`, TinyStories worker `handoff.py`, and
ROCm `handoff.py`/`bind_session.py`/`check_native.py` belong to other historical or
operator routes; none is invoked here. Public Lab owns selection/locking,
bounded snapshot acquisition, tokenizer fitting, packing, staging, training,
evaluation, checkpoint verification, generation and reporting. Ordinary file
copies/JSON authoring and optional host supervision do not replace those semantics.
If this native path refuses a required operation, retain the refusal and implement
only a demonstrated generic Lab gap with neutral tests, never a Workshop engine.

## Current validation and blockers

Public `config validate` accepts run/tokenizer declarations at the candidate Lab
pin and reports `executable: false`. Public help confirms the train, eval,
checkpoint, generation/report and preparation commands; `evaluate` and
`corpus render` were rejected during discovery and are not used here.
Full recipe inspection waits for the real native source lock; no input hash was
invented to manufacture a passing result. No model, snapshot, tokenizer or story
has been produced. No runtime/host admission was attempted.

Remaining before launch: approve the scientific/resource proposal; resolve bounded
lock-time metadata discovery; authenticate/select actual file inventory; verify
supported scalar decoder and source rights; finish native recipe inspection and
admission; bind reviewed recipe/runtime/host/owner identity and cumulative
supervision; obtain explicit approval. If the current `data lock` discovery lacks
required enforcement, that is a focused generic Lab capability gap, not permission
to use an unbounded downloader. Parent owns that decision and actual execution.
