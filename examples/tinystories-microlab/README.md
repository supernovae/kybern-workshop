# TinyStories Microlab: FFN Width, Tried Properly

[Back to Workshop README](../../README.md) · [Interactive guide on kybern.dev](https://kybern.dev/models/tinystories-training/)

A small, fast recipe for the two comparison commands in [Kybern Model Lab](https://github.com/supernovae/model-lab):
`klab try` for one change, and `klab sweep` to find out whether the answer holds across seeds.
It takes 2,000 training and 100 validation stories from `roneneldan/TinyStories`, fits a 2,048-token BPE tokenizer on the
training stories, and compares tiny dense decoders that differ only in **FFN width** (256 baseline vs. 384 and 512).
Each arm trains 40 updates (10,240 targets). That is a teaching budget: it shows the workflow, not model quality.

This recipe ships no recorded results. Run it yourself and keep the sealed records Lab writes.

## What is in this directory

| File | Purpose |
| --- | --- |
| [`declarations/source.yaml`](declarations/source.yaml) | Pinned dataset revision and the bounded, deduplicated selection |
| [`declarations/tokenizer.yaml`](declarations/tokenizer.yaml) | Train-only BPE tokenizer |
| [`declarations/run.yaml`](declarations/run.yaml) | Baseline run config (2 layers, hidden 128, FFN 256, ~590K parameters) |
| [`declarations/continued.yaml`](declarations/continued.yaml) | Same model with an 80-update budget, for the continuation exercise |
| [`wider-ffn.yaml`](wider-ffn.yaml) | The `try` delta: `model.ffn_dim: 384` |
| [`try.yaml`](try.yaml) | `try` policy: fixed seed, fast probes, and a repeated baseline to show run-to-run drift |
| [`sweep.yaml`](sweep.yaml) · [`sweep-policy.yaml`](sweep-policy.yaml) | FFN 384 and 512 against the baseline at seeds 1, 2 and 3 |
| [`prompts.txt`](prompts.txt) | Twelve story prefixes for generating from a checkpoint |

## 1. Set up a workspace

Work outside your Git checkout. Paths in the declarations are relative, so the snapshot, tokenizer, data and records land beside them.

```sh
RECIPE=examples/tinystories-microlab
WORK="$HOME/klab-experiments/tinystories-microlab-001"
mkdir -p "$WORK"
cp -R "$RECIPE/declarations" "$RECIPE"/{wider-ffn,try,sweep,sweep-policy}.yaml "$RECIPE/prompts.txt" "$WORK/"
cd "$WORK"
export KLAB_WORK_DIR="$WORK/klab-state"   # keeps this experiment's runs and records together
```

## 2. Validate before you download anything

```sh
klab config validate declarations/run.yaml --kind run
klab config validate declarations/tokenizer.yaml --kind tokenizer
klab config derive declarations/run.yaml --set model.ffn_dim=384 --output candidate-preview.yaml
klab inspect candidate-preview.yaml
```

Open `candidate-preview.yaml` and its `.derivation.json` sidecar and check that `model.ffn_dim` is the only change.

## 3. Prepare the data

```sh
klab data lock declarations/source.yaml --output source.lock.json
klab data snapshot source.lock.json --output snapshot
klab tokenizer train declarations/tokenizer.yaml
```

> **Disk:** the snapshot keeps 2,100 stories (at most 16 MiB), but the first Hugging Face download caches a whole Parquet shard (about 250 MB).

## 4. One change: `klab try`

```sh
klab try wider-ffn.yaml --vs declarations/run.yaml --config try.yaml --backend cpu
klab report TRY_ID
```

`try` trains both arms, scores them on the same held-out split, screens the training data for
held-out probe items (leakage), runs the fast probe tier and seals one record. `repeat_baseline: true`
trains the baseline a second time with identical inputs, so the record shows how much two identical
runs differ next to the candidate's effect. Read that number before you read the verdict.

A single-seed result is a direction to follow up, not a finding.

## 5. Does it hold? `klab sweep`

```sh
klab sweep sweep.yaml --backend cpu
klab report SWEEP_ID
```

The sweep trains the baseline once per seed, compares each width to it at the same seed, and reports the mean change in
held-out loss with its standard error. A `LOWER_LOSS` or `HIGHER_LOSS` verdict needs two or more seeds and a mean more than
two standard errors from zero; otherwise it says `WITHIN_SEED_NOISE`. The sealed record and a `series.csv` are under
`$KLAB_WORK_DIR/lab/sweeps/SWEEP_ID`.

## 6. Look inside and generate

```sh
klab explore TRY_ID
klab dashboard --lab-dir "$KLAB_WORK_DIR/lab"
klab generate RUN_ID --runs-dir "$KLAB_WORK_DIR/lab/runs" --checkpoint latest.json --prompt "$(head -1 prompts.txt)" \
  --max-new-tokens 192 --seed 42 --strict-context
klab chat RUN_ID --runs-dir "$KLAB_WORK_DIR/lab/runs" --checkpoint latest.json
```

Candidate run IDs are in the `try` record (`klab report TRY_ID --json`). Forty updates will not produce good stories; use
them to check that the commands work.

## Keeping your result repeatable

Record these next to anything you publish: the Lab commit (`klab --version` and `git -C model-lab rev-parse HEAD`), the
backend and precision, the seeds, the `TRY_ID` or `SWEEP_ID`, and the dataset revision. Do not edit probe items or thresholds
to make an idea pass. Weights stay local; a reproduction trains its own model.

## Next steps

- **Longer budget:** `declarations/continued.yaml` doubles the budget. Continue a finished run with
  `klab train CONFIG --extend-budget` (see [checkpointing](https://github.com/supernovae/model-lab/blob/main/docs/checkpointing.md)).
- **Bigger baseline:** [`examples/tinystories-useful`](../tinystories-useful/README.md) trains a 4.46M-parameter model for 8,192 updates.
- **Other axes:** change `vary` in `sweep.yaml` to `model.num_layers`, `optimizer.peak` or `training.seq_len`.
