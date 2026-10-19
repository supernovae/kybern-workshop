# TinyStories: build, inspect and improve a CPU learning baseline

This recipe completed a real native Lab run: 8,192 updates, 33,554,432 targets,
verified full-state checkpoints, evaluation and 27 final continuations. The owner
accepted publishing it as a working baseline to learn from. **The original
story-quality gate failed.** It is not a reliable story generator: repetition,
character/object drift and lost plots remain concrete improvement targets.

[Read the recorded result and every output](../../results/2026-10-19-tinystories-cpu/README.md)
before running anything. The evidence includes actual argv arrays, failures,
timings, configuration, digests and the complete fixed prompt panel. Model weights
are retained locally, not distributed by this repository. A fresh reproduction
trains its own model and creates new immutable identities.

The separate [40-update FFN microlab](../tinystories-microlab/README.md) teaches a
small controlled comparison; its smoke-sized budget is not this baseline.
Part 2 improvement experiments below are backlog, not completed or authorized runs.

## Recorded pins and workload

| Component | Executed identity |
| --- | --- |
| Lab | `7a517b2c065426748cd99702e82ea377877a7809` |
| CPU image | `ghcr.io/supernovae/tiny-sparse-lab@sha256:e3356de49998903e5f03ee2cb28a9b33a5270d380d65d1ceb6fe195531ea812c` |
| Workshop declarations | `e70d82b0c3262087ba5b1c546ebfd237f87a685d` |
| Optional external supervisor | Harness `b1c2efbd256eceeebdef7cf42b34165d01b8ccb6` |
| Source | `roneneldan/TinyStories`, revision `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`, default config; CDLA-Sharing-1.0 attribution in [source.json](source.json) |
| Runtime | Linux/WSL2, Python 3.14.4, Torch 2.14.1+cpu, CPU FP32, eight-CPU container quota, offline during training/inference |
| Model | Dense tied embeddings, 4 layers, width 256, FFN 768, 4 heads, vocab 4,096; 4,458,752 parameters |
| Data | 50,000 train / 512 validation stories; 11,370,444 / 104,675 packed tokens; train-only BPE |
| Training | Sequence 256 × microbatch 4 × accumulation 4 = 4,096 targets/update; 8,192 updates; seed 42 |
| Separate staging | Two smoke and five warmup updates; smoke remains a workflow check |
| Evaluation | 16 batches / 16,384 targets; final loss 1.7043116391, perplexity 5.4976000314 |
| Timing | Successful trainer lineage 11,861.47 seconds; final continuation 9,895.28 seconds; all 27 final inference processes 89.64 seconds including loading/startup |

Training covered about 2.95 passes over usable packed training positions. Exact
deduplication does not establish semantic train/validation separation. The 512-token
architectural context does not prove generalization beyond 256-token training.
All fixed prompts contain 14–20 tokens; adding 192 stays within training length.

The original [run.json](run.json) remains unchanged with checkpoint cadence 1,024.
Continuation changed only output location and checkpoint cadence to 256, preserving
the 8,192-update scheduler horizon. The recorded resolved configuration is included
with its path redaction explicitly disclosed. It is evidence, not a fresh binding.

## Reproduce through public Lab commands

Use a compatible installed runtime at the recorded pin. This guide does not install
packages or pull images automatically. Choose unused absolute `WORK` outside Git,
absolute `SOURCE` pointing to this directory, a fresh `INPUT` recipe directory and
unused `FIRST_RUN_ID` / `CONTINUED_RUN_ID`. Commands use Bash and `sparselab` from
that runtime; Windows users need a supported Linux runtime such as the measured WSL2
environment. Native Windows and GPU execution were not validated by this run.

Use unique stdout/stderr files and preserve each real exit status; `set -C` prevents
redirection overwrites. The [recorded argv ledger](../../results/2026-10-19-tinystories-cpu/commands.json)
is the historical execution record, including failed commands. Examples here are
the corrected reproducible path. They do not confer another person's resource
approval. Bind actual paths, limits and input admission for each new run.

The measured container used eight CPUs. Optional `OMP_NUM_THREADS=8`,
`MKL_NUM_THREADS=8`, `OPENBLAS_NUM_THREADS=8` and `TOKENIZERS_PARALLELISM=false`
configure libraries; those variables alone are not a hard CPU quota.

### 1. Lock, inspect and admit input

```sh
sparselab data lock "$SOURCE/source.json" --output "$WORK/source.lock.json" --cache-dir "$WORK/lock-cache" --json
```

Lock creation performs Hub metadata discovery. Acquisition byte/request ceilings
do not cover this command; resolve any required metadata transport limits before
running it. Copy `preparation-campaign.json`, `run.json`, `tokenizer.json` and the
actual `source.lock.json` into the fresh `INPUT` directory, then create the native
recipe inventory:

```sh
sparselab experiment recipe create "$INPUT" --profile preparation \
  --id tinystories-useful-preparation-v1 --entrypoint preparation-campaign.json \
  --file campaign:preparation-campaign.json --file run_config:run.json \
  --file tokenizer_config:tokenizer.json --file source_lock:source.lock.json \
  --output "$WORK/recipe"
```

Bind every typed path in [bindings.template.json](bindings.template.json) to the
chosen work directory as ordinary JSON, then inspect:

```sh
sparselab experiment recipe preparation inspect "$WORK/recipe/recipe.json" --bindings "$WORK/bindings.json" --json
```

Fill [admission.template.json](admission.template.json) from the real inspection,
descriptor and native lock identities. The unbound template deliberately refuses;
approval prose and copied hashes do not create authority. Respect the declaration's
selected rows, source rights and cumulative transport limits. If the real inventory
does not fit, preserve the refusal and review a new plan rather than raising caps.

### 2. Prepare, stage and train

Native preparation owns `dataset_snapshot`, `tokenizer_train` and `data_prepare`:

```sh
sparselab experiment recipe preparation apply "$WORK/recipe/recipe.json" --bindings "$WORK/bindings.json" --admission "$WORK/admission.json" --work-dir "$WORK" --json
```

Require complete receipts for all three phases. The bindings here place outputs
at `WORK/tokenizer`, `WORK/data` and `WORK/snapshot`; the recorded container used
equivalent mounted paths. Bind locations through `config derive` (string values
are JSON). Use simple paths without embedded quotes/backslashes in this example:

```sh
sparselab config derive "$SOURCE/run.json" \
  --set "tokenizer.path=\"$WORK/tokenizer/tokenizer.json\"" \
  --set "dataset.cache_dir=\"$WORK/data\"" \
  --set "dataset.train_path=\"$WORK/snapshot/train.jsonl\"" \
  --set "dataset.validation_path=\"$WORK/snapshot/validation.jsonl\"" \
  --set "dataset.source_manifest_path=\"$WORK/snapshot/manifest.json\"" \
  --set "logging.root_dir=\"$WORK/runs\"" --output "$WORK/train.yaml" --json
sparselab config validate "$WORK/train.yaml" --kind run --json
sparselab tokenizer verify "$WORK/train.yaml" --json
sparselab data prepared-inputs publish "$WORK/train.yaml" --output "$WORK/prepared"
sparselab data prepared-inputs verify "$WORK/train.yaml" "$WORK/prepared"
sparselab stage "$WORK/train.yaml" --through warmup --prepared-inputs "$WORK/prepared" --cold-verify --output "$WORK/stages"
sparselab train "$WORK/train.yaml" --backend cpu --runs-dir "$WORK/runs" --run-id "$FIRST_RUN_ID" --stage-bundle "$WORK/stages" --stop-after-step 1024
```

The first train command deliberately stops at update 1,024 under the full
8,192-update horizon. Its `stop_after_step` interruption is an expected checkpoint
boundary, not full completion. Inspect the actual run checkpoint inventory, resolve
the immutable directory as `FIRST_GENERATION` and its basename as `FIRST_CHECKPOINT`:

```sh
sparselab checkpoint inspect "$WORK/runs/$FIRST_RUN_ID/checkpoints/latest.json" --json
sparselab checkpoint inspect "$FIRST_GENERATION" --json
sparselab checkpoint verify "$FIRST_GENERATION" --json
sparselab report "$FIRST_RUN_ID" --kind run --runs-dir "$WORK/runs" --json
```

Run the following once for each of the first six development lines in `prompts.txt`:

```sh
sparselab generate "$FIRST_RUN_ID" --runs-dir "$WORK/runs" --checkpoint "$FIRST_CHECKPOINT" --backend cpu --prompt "$DEVELOPMENT_PREFIX" --max-new-tokens 192 --temperature 0 --top-k 0 --seed 42 --strict-context --show-prompt --json
```

Review those outputs and the time/resource forecast before continuation. Preserve
the last six prompts for final evaluation. The actual run needed an explicitly
approved continuation with more frequent checkpoints:

```sh
sparselab config derive "$WORK/runs/$FIRST_RUN_ID/resolved_config.yaml" \
  --set checkpoint.every_steps=256 --set "logging.root_dir=\"$WORK/runs\"" \
  --output "$WORK/continued.yaml" --json
sparselab config validate "$WORK/continued.yaml" --kind run --json
sparselab train "$WORK/continued.yaml" --backend cpu --runs-dir "$WORK/runs" --run-id "$CONTINUED_RUN_ID" --resume "$FIRST_GENERATION"
```

Native resume restores optimizer/RNG/cursor/counters into a fresh child run ID.
The source parent must permit its native lease; do not bypass a hold or steal a
lock. The recorded lineage also paused deliberately at update 1,406, then resumed
full state into a third execution identity. It retained the original scheduler
horizon and cumulative budget. A new reproduction need not manufacture that pause.

### 3. Verify, evaluate and generate

Set `RUN_ID` to the completed child run, resolve its actual immutable generation
directory as `GENERATION`, and use the basename as `CHECKPOINT`. Do not predict
the recorded `gen_000028` suffix for a new run. `latest.json` is a supported pointer;
bare `latest` is not. Retain inspection and verification before generating:

```sh
sparselab checkpoint inspect "$WORK/runs/$RUN_ID/checkpoints/latest.json" --json
sparselab checkpoint inspect "$GENERATION" --json
sparselab checkpoint verify "$GENERATION" --json
sparselab eval "$RUN_ID" --runs-dir "$WORK/runs" --checkpoint "$CHECKPOINT" --backend cpu
sparselab report "$RUN_ID" --kind run --runs-dir "$WORK/runs" --json
```

For **every** literal line in [prompts.txt](prompts.txt), run twice with
`TEMPERATURE=0 TOP_K=0` and `TEMPERATURE=0.7 TOP_K=40`, keeping seed 42 fixed:

```sh
sparselab generate "$RUN_ID" --runs-dir "$WORK/runs" --checkpoint "$CHECKPOINT" --backend cpu --prompt "$PREFIX" --max-new-tokens 192 --temperature "$TEMPERATURE" --top-k "$TOP_K" --seed 42 --strict-context --show-prompt --json
```

Save all 24 outputs, including empty responses or failures. For the first three
prompts, also run with `--max-new-tokens 48 --temperature 0 --top-k 0` for the
separate website baseline. These three shorter outputs are excluded from scoring.
Do not silently truncate or resample. Retain the run config/manifest, weights,
checkpoint manifest, tokenizer and required prepared arrays/sidecars together;
the native verifier/loader is authoritative for that closure.

For optional local interaction with a verified checkpoint:

```sh
sparselab surface chat --cell "candidate=$GENERATION" --backend cpu --seed 42 --port 8502
```

This local UI does not make the model instruction-tuned. Public websites import
generation JSON; they cannot call the intentionally loopback-only native service.

## Read the result honestly

The frozen rubric required 20/24 relevant, readable, consistent continuations,
including 10/12 held-out outputs and 18/24 understandable endings. Provisional
assistant assessment found **2/24, 1/12 and 17/24**, respectively. Repeated-sentence
loops and identity contradictions fail an output even when it has a closing line.
The full panel is public; these are not selected success stories or a human review
clearance. Authored prompts were withheld from model selection but are not proven
absent from training. Publication acceptance changed to a learning baseline; the
failed quality result did not change.

The website accepts UTF-8 native JSON up to 1 MiB with `format: "raw"`, strings
`prompt`/`response`, objects `identity`/`generation`, and preserves additional fields.
Our public derivatives disclose one private run-path redaction and the original
SHA256 in `_publication`. Prompts, responses, settings and identity hashes are
unchanged. The importer displays identities; it does not validate checkpoint bytes.

## Resource evidence and remaining boundaries

The recorded supervisor retained stdout/stderr, actual outcomes and explicit
continuation accounting. All 35 final-session slots completed, evidence was
complete, descendants were cleaned up and the training container exited zero.
Earlier failures and the host crash remain in the published history; no automatic
retry is implied. No training job is active.

Peak sampled RSS was 929.14 MiB for final continuation and 429.29 MiB for inference.
The 16 GiB RSS and 20 GiB storage observations/stop thresholds were **not hard caps**.
Per-command native monitors do not implement a cumulative session deadline. The
recorded external session preserved a single deadline and conservative aggregate
charges; remaining budget is historical accounting, not authority for another job.
No Workshop engine, downloader, trainer or execution helper is required: public Lab
owns all experiment semantics; optional supervision belongs outside this recipe.

## Part 2: concrete improvement exercises (not executed)

1. **Explain the baseline.** Inspect the published loss trajectory alongside all
   outputs. With a retained closure, use `checkpoint inspect`, `checkpoint verify`,
   `report --kind run` and `eval` above to confirm identities and metrics before
   comparing behavior. Falling validation loss alone did not establish story quality.
2. **Measure decoding tradeoffs.** On the same verified checkpoint, declare a new
   fixed prompt panel and seed/settings budget before running public `generate`.
   Compare greedy and sampled repetition/continuity, retaining every result and
   actual timing. Keep prompt plus generation within trained context. Do not tune
   against the already-scored held-out panel and call it unseen validation.
3. **Change one model variable.** For a separately approved fresh experiment, use
   `sparselab config derive run.json --set model.ffn_dim=1024 --output wider.yaml --json`
   and `sparselab config validate wider.yaml --kind run --json`; then follow the
   native preparation/stage/train/eval/generate route with new identities. Confirm
   the pinned schema accepts the field before any workload. Compare at equal target
   budgets and report parameter count, time and memory; do not resume incompatible
   weights or promise improvement from added capacity.
4. **Study data/exposure.** Declare a fresh input selection or training-budget
   experiment using native configuration and acquisition admission. Keep tokenizer,
   data and source hashes explicit; use fresh held-out evaluation and preserve
   failed runs. More steps on the same small data are not automatically better.

These are future controlled experiments, not additional work included in this
published run. [Validation and review status](VALIDATION.md) records the checks
behind this documentation and the remaining external review boundary.
