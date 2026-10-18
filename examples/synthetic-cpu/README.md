# Synthetic CPU project

[Back to Workshop projects](../../README.md)

A tiny end-to-end exercise using the pinned Tiny Sparse Lab CLI.

The [synthetic CPU example](.) exercises native preparation,
an explicit approval gate, one training attempt, held-out evaluation and verified
reporting. It demonstrates wiring, not model quality. Workflow artifact identities come from successful native preparation receipts.

The completed [2026-10-14 measured result](../../results/2026-10-14-synthetic-cpu/README.md)
includes failed invocations, verified reporting and no-new-attempt replay.

## Historical procedure; current metadata entrypoint

This guide preserves the historical Lab `b155cdcc1462cfbcbd5f0cf5261eb8aa197ef9dc`
procedure and its measured evidence. Its setup, bindings and admissions below
belong to that revision; they are not current execution instructions or fresh
runtime qualification.

Current Lab rejects `preparation_bindings_version`,
`preparation_admission_version` and `workflow_admission_version`. Current workflow
admission also requires explicit `limits` with `max_training_updates`,
`max_target_positions` and `max_eval_batches`. Those values require the actual
reviewed run declaration; this guide does not supply current budgets or admission.
Do not partially modernize the historical procedure by removing individual fields.

For current non-executing authoring and inspection, use
[the native workflow guide](../../docs/native-workflow.md). New execution needs
separate source/runtime selection and approval; the historical results below do
not authorize it. Historical procedure restored and scope clarified 2026-10-18.

## Pins and setup

Use Tiny Sparse Lab commit `b155cdcc1462cfbcbd5f0cf5261eb8aa197ef9dc`
(PR128; reviewed head `45230f446bde5d88b26857630c9b7a53eaaf602e`). Its native
installed-source SHA-256 is
`1f947cce513952bef88f9397e12bb3661efe97ece604cab04330f197e0a44a26`.
Its `uv.lock` SHA-256 is
`2058fe5c126df074879648018c36288386190446b94b147b811671185958ac86`.
The provisioned environment uses CPython 3.14.8, PyTorch 2.14.0+cpu,
tokenizers 0.22.2, NumPy 2.5.3, datasets 4.8.5, PyArrow 25.0.1,
Pydantic 2.13.5, PyYAML 6.0.3, huggingface-hub 0.36.2 and psutil 7.2.2.
All dependency pins are in the lab lock. Tiny Sparse Lab is MIT licensed; see
its pinned LICENSE. The example uses generated synthetic text, with no corpus
or model downloads. Workshop's new declarations are independently authored.

An ordinary clone and pinned checkout is sufficient; no remote-fetch framework is
needed. From a writable parent directory, preserve separate A and B worktrees:

```sh
git clone https://github.com/supernovae/kybern-workshop.git workshop
cd workshop
git checkout --detach e8250556412bc8535c029d80af3fa735b82c1ffa
git worktree add --detach ../workshop-preparation-a 28a01d69442c8b08e5ba78e4561ff4f69443e1e5
# B is the absolute workshop path; A is the absolute preparation worktree path.
# Do not advance either checkout while its admission is in use.
cd ..
git clone https://github.com/supernovae/tiny-sparse-lab.git lab
git -C lab checkout --detach b155cdcc1462cfbcbd5f0cf5261eb8aa197ef9dc
# LAB is the absolute lab path. Read this updated guide from the results revision.
```

The historical workflow references locally retained prepared inputs; cloning does
not download those payloads or create admission. A fresh reproduction must prepare
its own inputs, author/commit their identities, inspect and obtain approval for its
own exact workflow commit. Do not borrow this run's admission or claim its receipts.

Provisioning requires authorization and precedes measurement:

```sh
# LAB is a clean checkout at the exact commit above; other paths are outside Git.
UV_PYTHON_INSTALL_DIR="$PYTHON_STORE" UV_CACHE_DIR="$UV_CACHE" \
  UV_PROJECT_ENVIRONMENT="$CPU_ENV" \
  uv sync --locked --extra cpu --no-dev --project "$LAB" --python 3.14.8
CPU_PYTHON="$CPU_ENV/bin/python"
```

Freeze the installed source identity before preparation. Do not reinstall or
update it between preparation and workflow execution. A new source identity
needs fresh preparation evidence; keep earlier receipts unchanged.

## Workload and limits

Run seed and synthetic-data seed are integer 7. The dense model has one layer,
hidden width 16, FFN width 32, two heads, context 32 and vocabulary 260.
Runtime is PyTorch CPU FP32. Sequence 16, microbatch 1 and accumulation 1 give
16 targets per update. The main budget is one update; native smoke 2 and warmup 5
remain enabled. Optimizer warmup is separately zero. Evaluation reads at most
one validation batch. Runtime probes are additional work, not training updates.

Preparation declares eight training and four validation documents, token caps
256 and 128, and tokenizer training on at most eight documents. These are caps,
not observed counts. Compared with the lab contract fixture, this example keeps
model dimensions, seeds, sequence/batch settings and native staging counts, but
changes vocabulary (260 versus 512; the preparation execution fixture uses 264),
token caps (256/128 versus 129/81), evaluation batches (1 versus 4), optimizer
settings and main budget. The token caps are larger, despite the smaller
vocabulary/evaluation budget. This is not exact reproduction. The historical
149.486-second/1.50-GiB proof is not this example's measurement.

Wrap every runtime-bearing command with `monitor.json`: 600-second wall ceiling,
4-GiB process-tree RSS ceiling and 1-GiB added-workspace ceiling, sampled every
second, with five-second termination grace. These are stop ceilings, not
predictions or instantaneous kernel quotas. Preserve native failed receipts,
monitor samples/completion and descendant-cleanup evidence; diagnose before
retrying and stop if scope must expand.

## Preparation at commit A

Use an absolute `WORK` directory outside every Git repository for all bindings,
admissions, receipts, logs and payloads. Preserve a detached checkout `A` at the
preparation commit. Never advance A to workflow commit B: any HEAD change
invalidates A's admission. The descriptor directory is the recipe root; inventory
hashes cover exact member bytes without replacing native scientific hashes.

Create `$WORK/preparation-bindings.json`, replacing `/absolute/work` with `WORK`:

```json
{
  "preparation_bindings_version": 1,
  "artifacts": {},
  "config_paths": {
    "tokenizer-config.json": {
      "output_dir": "/absolute/work/payload/tokenizer",
      "dataset.cache_dir": "/absolute/work/payload/cache"
    },
    "run.json": {
      "tokenizer.path": "/absolute/work/payload/tokenizer/tokenizer.json",
      "dataset.cache_dir": "/absolute/work/payload/cache",
      "logging.root_dir": "/absolute/work/payload/runs"
    }
  }
}
```

Inspect committed A:

```sh
PREP="$A/examples/synthetic-cpu/preparation.json"
POLICY="$A/examples/synthetic-cpu/monitor.json"
"$CPU_PYTHON" -m sparselab experiment recipe preparation inspect "$PREP" \
  --bindings "$WORK/preparation-bindings.json" --json > "$WORK/preparation-inspect.json"
```

Author `$WORK/preparation-admission.json` with `preparation_admission_version: 1`,
A's full Git SHA as `reviewed_commit`, the inspection's exact `recipe_sha256` and
`binding_sha256`, and the running interpreter's exact `sys.executable` as
`cpu_python`. Set `max_documents: 12`, `max_tokens: 384`, `max_vocab_size: 260`,
`min_free_bytes: 268435456` and `min_free_inodes: 128`. Admission asserts review
of committed bytes; it does not replace native verification.

```sh
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor-baseline "$WORK" \
  --output "$WORK/preparation-baseline.json" --json
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor --policy "$POLICY" \
  --baseline "$WORK/preparation-baseline.json" \
  --log-dir "$WORK/monitor/preparation-1" --workspace "$WORK" -- \
  "$CPU_PYTHON" -m sparselab experiment recipe preparation apply "$PREP" \
  --bindings "$WORK/preparation-bindings.json" \
  --admission "$WORK/preparation-admission.json" --work-dir "$WORK" --json \
  > "$WORK/preparation-monitor.json"
```

The monitor retains child stdout/stderr in its log directory. Require COMPLETE
`train-tokenizer` and `pack-data` stages, not just exit zero. Use their native
`outputs` identities and `availability.path` locations; never invent an identity
or adopt unreceipted output. For replay use `resume` with preserved A and unchanged
bindings/admission, writing into a fresh monitor log directory.

## Workflow handoff

After preparation, author a one-cell native plan, diagnostic `heldout_lm` suite,
Campaign and workflow descriptor with the successful native identities and exact
inventory hashes. Commit B before its inspection and admission; keep artifact
locations only in local bindings. Review B's admission before the model attempt.

The public operations are `experiment recipe workflow apply`, `approve`,
`apply --execute-runs --max-wait-seconds 540`, `resume` and `report`.
Even `apply` without `--execute-runs` may execute acceptance probes; monitor it.
Select the plan-stage lock/workspace and collect-stage evidence index explicitly
for reporting, retaining the separate evaluation index. Require a completed and
ingested native attempt, checkpoint-bound evaluation, verified report, then
completed replay with no new attempt. Report executed/skipped stages, update and
probe counts, time, RSS, workspace growth and cleanup separately. Successful
rendering does not establish scientific effectiveness.

## Author and admit workflow B

The [stdlib helper](../../scripts/seal-inputs.py) only copies the two COMPLETE native
preparation outputs into the authored Campaign ports and workflow descriptor,
then hashes member bytes for the inventory. It writes local bindings separately.
It is not a verifier: use native `resolve` to cold-verify the payloads. Preserve
old declarations/receipts before authoring a new identity.

```sh
RECIPE="$B/examples/synthetic-cpu"
"$CPU_PYTHON" "$B/scripts/seal-inputs.py" \
  --receipt "$WORK/monitor/preparation-1/command.stdout.log" \
  --recipe "$RECIPE" --bindings "$WORK/workflow-bindings.json" \
  --logging-root "$WORK/workflow-runs"
# Commit the authored declarations at B before inspection/admission.
"$CPU_PYTHON" -m sparselab experiment recipe workflow inspect "$RECIPE/workflow.json" \
  --bindings "$WORK/workflow-bindings.json" --json > "$WORK/workflow-inspect.json"
"$CPU_PYTHON" -m sparselab experiment recipe workflow resolve "$RECIPE/workflow.json" \
  --bindings "$WORK/workflow-bindings.json" --json > "$WORK/workflow-resolve.json"
```

For this already authored example, do not rerun the helper against an existing
bindings output; it refuses that overwrite. A fresh reproduction must prepare its
own inputs and commit the resulting declarations before admitting them.

Create `$WORK/workflow-admission.json` with exactly:

```json
{
  "workflow_admission_version": 1,
  "reviewed_commit": "FULL_B_COMMIT",
  "recipe_sha256": "FROM_WORKFLOW_INSPECT",
  "binding_sha256": "FROM_WORKFLOW_INSPECT",
  "cpu_python": "/absolute/cpu/environment/bin/python"
}
```

Replace all placeholders with the reviewed commit, native inspection digests
and exact running interpreter. Keep this document outside Git. Review these
fields and the preparation identities before starting the following steps.

Before workflow commands, select a writable local lease namespace for this CPU
session. Use the same namespace consistently across all commands; do not create
isolated namespaces to bypass another worker's lease. This example owns one CPU
worker and allocates no accelerators. This is a per-session environment variable,
not a change to the scientific declaration or global machine configuration:

```sh
export SPARSELAB_WORKER_LEASE_DIR="$WORK/worker-leases"
```

Use the ordinary native monitor without `strace`; tracing caused worker transport
timeouts in the recorded attempt. Passive process observation may corroborate
probe counts but must disclose sampling gaps and distinguish observed lifetimes
from exact timings. Preserve failures, diagnose before continuing the same attempt,
and never submit a replacement merely because transport or ingestion is pending.

For each runtime command below, use a unique `STEP`, capture a fresh baseline
and wrap the command with the native monitor. Do not reuse a log directory:

```sh
# Set STEP to workflow-plan, workflow-approve, workflow-run or workflow-replay.
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor-baseline "$WORK" \
  --output "$WORK/$STEP-baseline.json" --json
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor \
  --policy "$RECIPE/monitor.json" --baseline "$WORK/$STEP-baseline.json" \
  --log-dir "$WORK/monitor/$STEP" --workspace "$WORK" -- \
  "$CPU_PYTHON" -m sparselab experiment recipe workflow apply "$RECIPE/workflow.json" \
  --bindings "$WORK/workflow-bindings.json" --admission "$WORK/workflow-admission.json" \
  --work-dir "$WORK" --json > "$WORK/$STEP-monitor.json"
```

1. `workflow-plan`: use the command above unchanged. Require `approve-model` to
   be AWAITING_APPROVAL and no model attempt.
2. `workflow-approve`: replace `apply "$RECIPE/workflow.json"` with
   `approve "$RECIPE/workflow.json" approve-model`, adding
   `--note "Owner approved one bounded synthetic CPU attempt"`. This is the
   explicit native approval; no helper implicitly approves.
3. `workflow-run`: use `apply`, adding `--execute-runs --max-wait-seconds 540`.
   Require every stage COMPLETE and exactly one COMPLETE/ingested attempt.
4. `workflow-replay`: replace `apply` with `resume`, without `--execute-runs`.
   Require every stage COMPLETE and unchanged attempt/receipt identities.

The selected no-profile CPU acceptance stage checks storage/runtime declarations;
its source does not itself call a runtime probe. Execution is expected to perform
six one-update precision probes: Controller candidate validation, worker dispatch
validation, staging validation, and each of smoke, warmup and main trainer
initialization. Each dense FP32 probe updates a 4-by-4 parameter once; these are
not 16-target training updates. The source paths are `workers/controller.py`,
`workers/execution.py`, `staging.py`, `training/trainer.py`, `engines/pytorch.py`
and `runtime_probe.py`. Verify observed counts/timings from execution evidence;
this is a source-derived expectation, not a measured result. PyTorch held-out
inference loads the verified checkpoint directly and does not call that optimizer
probe. Continue monitoring every apply/approval/replay because command flags alone
do not establish that no runtime work occurs.

## Verified report

From the COMPLETE `lock-plan` stage take `availability.path` as `LOCK` and
`availability.workspace` as `EXPERIMENT_WORKSPACE`. From `collect-run` take
`availability.path` as `INDEX`. Preserve the separate `evaluate-heldout` index.

```sh
"$CPU_PYTHON" -m sparselab experiment recipe workflow report "$LOCK" \
  --workspace "$EXPERIMENT_WORKSPACE" --index "$INDEX" \
  --output "$WORK/report.json" --json
"$CPU_PYTHON" -m sparselab experiment recipe workflow report "$LOCK" \
  --workspace "$EXPERIMENT_WORKSPACE" --index "$INDEX" \
  --output "$WORK/report.md" --format markdown
```

Reporting verifies the selected snapshot; it neither recollects nor silently
chooses a newer evaluation. The Campaign collects before evaluation, so retain
both the report and evaluation evidence rather than implying the earlier index
contains the later evaluation. Report files are exclusively created; identical
replay is allowed. Changed evidence needs an explicitly selected new snapshot.

## Measured preparation status

Preparation A is `28a01d69442c8b08e5ba78e4561ff4f69443e1e5`. Both native stages
completed on 2026-10-14 with one preparation attempt each. The monitored command
measured 9.587894 seconds, 437,280,768 bytes peak process-tree RSS and 73,736 bytes
peak/final added workspace. Ten samples reported no violations; the owned-process
receipt reported zero living descendants. Preparation ran no model updates or
runtime optimizer probes. Full machine-local records remain outside Git.

The first monitor launch failed before spawning preparation because its default
work directory was read-only. That failed launch record and empty stdout were
preserved. The corrected command specifies global `--work-dir` and a persisted
growth baseline; no native failed preparation attempt was overwritten or retried.
The environment also briefly disconnected while editing the guide, before any
experiment was running; runtime metadata and remote refs were rechecked.

Workflow execution, ingestion, diagnostic evaluation, verified reporting and
completed replay are now measured. See the [complete result](../../results/2026-10-14-synthetic-cpu/README.md),
including both failed invocations and their cleanup evidence.

Preparation replay completed in 6.452063 seconds, with 430,981,120 bytes peak tree RSS and 23,824 bytes final added workspace. Both stage receipts, artifact identities and one-attempt histories were unchanged. Its owned-process receipt also reported zero living descendants.
