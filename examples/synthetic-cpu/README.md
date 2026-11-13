# Basic Synthetic CPU Smoke Test

[Back to Workshop README](../../README.md) · [Offline installation check on kybern.dev](https://kybern.dev/models/cpu-smoke/)

A small offline exercise that takes [Kybern Model Lab](https://github.com/supernovae/model-lab) through every stage once:
a synthetic text dataset, a BPE tokenizer, one training step, held-out evaluation and a run report. It downloads nothing and
needs no accelerator.

It is the quickest way to find out whether your install works. It says nothing about model quality.

## Option 1: Lab's built-in readiness check

From your `model-lab` checkout:

```sh
uv sync --locked --extra cpu --dev
export KLAB_WORK_DIR="$HOME/.local/share/klab"
uv run --locked --extra cpu klab readiness smoke --family dense --output "$KLAB_WORK_DIR/first-run"
uv run --locked --extra cpu klab dashboard --runs-dir "$KLAB_WORK_DIR/first-run/runs"
```

## Option 2: Run this recipe's declarations

| File | Purpose |
| --- | --- |
| [`tokenizer-config.json`](tokenizer-config.json) | Fits a 260-token BPE tokenizer on 8 synthetic documents |
| [`run.json`](run.json) | A 6,768-parameter dense decoder: 1 layer, hidden 16, FFN 32, 2 heads, context 32, seed 7 |

The run trains one update (16 targets) on CPU in FP32 and evaluates on 4 synthetic validation documents.
Paths are relative to each file, so outputs land in `payload/` and `runs/` beside your copies.

```sh
WORK="$HOME/klab-experiments/synthetic-cpu-001"
mkdir -p "$WORK" && cp examples/synthetic-cpu/{run,tokenizer-config}.json "$WORK/" && cd "$WORK"
export KLAB_WORK_DIR="$WORK/klab-state"

klab config validate run.json --kind run
klab config validate tokenizer-config.json --kind tokenizer
klab tokenizer train tokenizer-config.json
klab data prepare run.json
klab train run.json --backend cpu --runs-dir runs --run-id synthetic-cpu-001
klab eval synthetic-cpu-001 --runs-dir runs --backend cpu
klab report synthetic-cpu-001 --kind run --runs-dir runs
```

Expect each step to finish in seconds. `report` prints the run's verified evidence and its post-training triage. With a
single update the triage correctly reports `trend=insufficient_history`; that is a pass for this smoke test, not a defect.

## Recording your result

Note the Lab commit, Python and PyTorch versions, the run ID and the `report` output. An earlier record of this recipe came from a campaign workflow Lab has since removed and was retired with it; Git history keeps it.
