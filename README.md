# Kybern Workshop

Self-contained examples for learning with [Tiny Sparse Lab](https://github.com/supernovae/tiny-sparse-lab).

The [synthetic CPU example](examples/synthetic-cpu) exercises native preparation,
an explicit approval gate, one training attempt, held-out evaluation and verified
reporting. It demonstrates wiring, not model quality. This preparation commit
precedes the workflow: artifact identities must come from successful native receipts.

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
