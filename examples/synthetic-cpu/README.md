# Basic Synthetic CPU Smoke Test

[Back to Workshop README](../../README.md) · [Offline Installation Check Guide (kybern.dev)](https://kybern.dev/models/cpu-smoke/)

A lightweight, offline end-to-end exercise for [Kybern Model Lab](https://github.com/supernovae/model-lab).
It prepares a tiny synthetic text dataset and BPE tokenizer, runs a single-step training attempt through an explicit approval gate, scores held-out validation loss, and generates a verified report—with no dataset or model downloads required.

- **Recorded run & metrics:** [2026-10-14 Synthetic CPU Result](../../results/2026-10-14-synthetic-cpu/README.md)
- **Current CLI recipe packaging:** [Running Workshop Recipes with Kybern Model Lab](../../docs/native-workflow.md)

---

## Quick Offline Smoke Check (Current CLI)

If you just installed [Kybern Model Lab](https://github.com/supernovae/model-lab) and want to verify your local CPU setup in one command, you can also run the built-in readiness check from your `model-lab` checkout (see the [kybern.dev guide](https://kybern.dev/models/cpu-smoke/)):

```sh
uv sync --locked --extra cpu --dev
export KLAB_WORK_DIR="$HOME/.local/share/klab"
uv run --locked --extra cpu klab readiness smoke --family dense \
  --output "$KLAB_WORK_DIR/first-run"
uv run --locked --extra cpu klab dashboard --runs-dir "$KLAB_WORK_DIR/first-run/runs"
```

To package and inspect the declarative files in this directory (`examples/synthetic-cpu`) with the latest `klab` CLI, see [Packaging and Inspecting a Recipe](../../docs/native-workflow.md#packaging-and-inspecting-a-recipe).

---

## Replicating the Recorded Campaign Run

The steps below document the exact pinned procedure used to produce the [2026-10-14 recorded result](../../results/2026-10-14-synthetic-cpu/README.md).

### Pins and Environment Setup

| Component | Pinned Identity |
| --- | --- |
| **Kybern Model Lab commit** | `b155cdcc1462cfbcbd5f0cf5261eb8aa197ef9dc` |
| **Installed source SHA-256** | `1f947cce513952bef88f9397e12bb3661efe97ece604cab04330f197e0a44a26` |
| **`uv.lock` SHA-256** | `2058fe5c126df074879648018c36288386190446b94b147b811671185958ac86` |
| **Runtime** | CPython 3.14.8, PyTorch 2.14.0+cpu, tokenizers 0.22.2, NumPy 2.5.3, datasets 4.8.5, PyArrow 25.0.1 |

> **Pinned before the Lab rename:** this procedure pins a Kybern Model Lab commit from before the CLI was renamed `klab`. To replay exactly at the recorded pin, use `sparselab` (and `SPARSELAB_*` variables) in place of `klab`; see [Records Pinned Before the Rename](../../docs/native-workflow.md#records-pinned-before-the-rename).

From a writable parent directory, clone Workshop and Kybern Model Lab at the recorded revisions:

```sh
git clone https://github.com/supernovae/kybern-workshop.git workshop
cd workshop
git checkout --detach e8250556412bc8535c029d80af3fa735b82c1ffa
git worktree add --detach ../workshop-preparation-a 28a01d69442c8b08e5ba78e4561ff4f69443e1e5
# B is the workshop path; A is the preparation worktree path.
cd ..
git clone https://github.com/supernovae/model-lab.git lab
git -C lab checkout --detach b155cdcc1462cfbcbd5f0cf5261eb8aa197ef9dc
```

Provision the locked CPU environment:

```sh
UV_PYTHON_INSTALL_DIR="$PYTHON_STORE" UV_CACHE_DIR="$UV_CACHE" \
  UV_PROJECT_ENVIRONMENT="$CPU_ENV" \
  uv sync --locked --extra cpu --no-dev --project "$LAB" --python 3.14.8
CPU_PYTHON="$CPU_ENV/bin/python"
```

### Model and Workload Specification

- **Model:** Dense decoder, 1 layer, hidden dimension 16, FFN dimension 32, 2 heads, context length 32, vocabulary size 260 (6,768 parameters).
- **Training:** Seed 7, PyTorch CPU FP32, sequence length 16, microbatch 1, gradient accumulation 1 (16 targets/update). Runs 2 smoke updates, 5 warmup updates, and 1 main update.
- **Synthetic data:** 8 training and 4 validation documents (token caps 256 and 128), tokenizer trained on up to 8 documents.
- **Resource monitor (`monitor.json`):** 600-second wall ceiling, 4 GiB process-tree RSS ceiling, and 1 GiB workspace growth ceiling, sampled every second.

### 1. Prepare Synthetic Inputs

Use an external `WORK` directory outside Git for all local bindings, receipts, logs, and generated payloads. Create `$WORK/preparation-bindings.json`:

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

Inspect the preparation recipe:

```sh
PREP="$A/examples/synthetic-cpu/preparation.json"
POLICY="$A/examples/synthetic-cpu/monitor.json"
"$CPU_PYTHON" -m klab experiment recipe preparation inspect "$PREP" \
  --bindings "$WORK/preparation-bindings.json" --json > "$WORK/preparation-inspect.json"
```

Create `$WORK/preparation-admission.json` with `preparation_admission_version: 1`, `A`'s full Git SHA as `reviewed_commit`, the exact `recipe_sha256` and `binding_sha256` from inspection, and your `CPU_PYTHON` path as `cpu_python`. Set `max_documents: 12`, `max_tokens: 384`, `max_vocab_size: 260`, `min_free_bytes: 268435456`, and `min_free_inodes: 128`. Then run preparation under the resource monitor:

```sh
"$CPU_PYTHON" -m klab --work-dir "$WORK" monitor-baseline "$WORK" \
  --output "$WORK/preparation-baseline.json" --json
"$CPU_PYTHON" -m klab --work-dir "$WORK" monitor --policy "$POLICY" \
  --baseline "$WORK/preparation-baseline.json" \
  --log-dir "$WORK/monitor/preparation-1" --workspace "$WORK" -- \
  "$CPU_PYTHON" -m klab experiment recipe preparation apply "$PREP" \
  --bindings "$WORK/preparation-bindings.json" \
  --admission "$WORK/preparation-admission.json" --work-dir "$WORK" --json \
  > "$WORK/preparation-monitor.json"
```

Both `train-tokenizer` and `pack-data` stages should report `COMPLETE`.

### 2. Seal Inputs and Run the Workflow

Bind the completed preparation's artifact identities into the workflow, then
inspect and resolve. The recorded run did this with a helper script that has
since been removed. By hand: for each `COMPLETE` stage in the preparation
result (`train-tokenizer`, `pack-data`), copy its output's `kind`, `identifier`
and `sha256` into the matching `artifact_reference` stage of `campaign.json`
and into `workflow.json`'s `artifacts`, refresh the member hashes in
`workflow.json`, and write the stage's `availability.path` into
`$WORK/workflow-bindings.json` under `artifacts`, with `logging_root` set to an
absolute run-store path. Never write an identity the preparation did not report.

```sh
RECIPE="$B/examples/synthetic-cpu"

"$CPU_PYTHON" -m klab experiment recipe workflow inspect "$RECIPE/workflow.json" \
  --bindings "$WORK/workflow-bindings.json" --json > "$WORK/workflow-inspect.json"
"$CPU_PYTHON" -m klab experiment recipe workflow resolve "$RECIPE/workflow.json" \
  --bindings "$WORK/workflow-bindings.json" --json > "$WORK/workflow-resolve.json"
```

Create `$WORK/workflow-admission.json`:

```json
{
  "workflow_admission_version": 1,
  "reviewed_commit": "FULL_B_COMMIT",
  "recipe_sha256": "FROM_WORKFLOW_INSPECT",
  "binding_sha256": "FROM_WORKFLOW_INSPECT",
  "cpu_python": "/absolute/cpu/environment/bin/python"
}
```

Set a writable local worker lease directory:

```sh
export KLAB_WORKER_LEASE_DIR="$WORK/worker-leases"
```

Run each workflow step (`workflow-plan`, `workflow-approve`, `workflow-run`, and `workflow-replay`) under the native monitor:

```sh
"$CPU_PYTHON" -m klab --work-dir "$WORK" monitor-baseline "$WORK" \
  --output "$WORK/$STEP-baseline.json" --json
"$CPU_PYTHON" -m klab --work-dir "$WORK" monitor \
  --policy "$RECIPE/monitor.json" --baseline "$WORK/$STEP-baseline.json" \
  --log-dir "$WORK/monitor/$STEP" --workspace "$WORK" -- \
  "$CPU_PYTHON" -m klab experiment recipe workflow apply "$RECIPE/workflow.json" \
  --bindings "$WORK/workflow-bindings.json" --admission "$WORK/workflow-admission.json" \
  --work-dir "$WORK" --json > "$WORK/$STEP-monitor.json"
```

1. **`workflow-plan`:** runs `apply` as shown above; reaches `AWAITING_APPROVAL` at `approve-model`.
2. **`workflow-approve`:** replaces `apply "$RECIPE/workflow.json"` with `approve "$RECIPE/workflow.json" approve-model --note "Approved synthetic CPU smoke run"`.
3. **`workflow-run`:** runs `apply` with `--execute-runs --max-wait-seconds 540` to execute training and held-out evaluation.
4. **`workflow-replay`:** runs `resume` (without `--execute-runs`) to verify idempotent replay with no new training attempt.

### 3. Generate the Verified Report

Using the `LOCK` and `EXPERIMENT_WORKSPACE` paths from `lock-plan` and the `INDEX` path from `collect-run`:

```sh
"$CPU_PYTHON" -m klab experiment recipe workflow report "$LOCK" \
  --workspace "$EXPERIMENT_WORKSPACE" --index "$INDEX" \
  --output "$WORK/report.json" --json
"$CPU_PYTHON" -m klab experiment recipe workflow report "$LOCK" \
  --workspace "$EXPERIMENT_WORKSPACE" --index "$INDEX" \
  --output "$WORK/report.md" --format markdown
```

See [`results/2026-10-14-synthetic-cpu/README.md`](../../results/2026-10-14-synthetic-cpu/README.md) for the recorded timings, memory observations, and generated report artifacts.
