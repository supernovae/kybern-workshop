# Run and revise DevMind

[`experiment.json`](experiment.json) is the editable experiment intent. It references
[`model.json`](model.json) and [`optimizer.json`](optimizer.json), keeps the full
341,885,952-parameter architecture and defines the 12B unique-target 60/20/20 baseline.
The preparation phase maps are tools for producing missing inputs, not a mandatory
25-step prerequisite for every iteration. Reuse unchanged native artifacts.

Production/model execution is currently stopped pending integrated Harness/Lab/
Workshop verification and owner review. The commands below are the execution path
once that hold is lifted; authoring and schema checks do not lift it.

## Bind once to real inputs

Run from a Workshop checkout using the Python environment where Lab is installed.
Set `EXPERIMENT_DIR` to your external working experiment directory. Copy
`binding.example.json` there and replace every null with actual values:

- `dataset`: the native authenticated materialized mixture declaration/output,
  writable cache, measured document/token limits and real license provenance.
  Preserve the complete validation split. The 12B scientific mixture is not yet
  complete; retained R36 data or newly acquired shards do not establish it.
- `tokenizer.path`: the retained, verified 32K tokenizer artifact (R40), or an
  explicitly revised tokenizer. No fitting is required merely to bind a run.
- `runtime`: the chosen engine, backend and precision. The example specifies BF16,
  transformer-block activation checkpointing and `estimate_policy: observe`.
  Memory estimates remain observations; actual resource limits, cancellation and
  runtime failures still apply. No model/batch change or CPU-derived ceiling is
  introduced. Choose the actual supported backend; do not leave `auto` as an
  accidental hardware choice.
- `logging.root_dir`: the native run store, outside the recipe repository.

All bound paths must be absolute so moving the authored config does not redirect
its inputs. Neither the example nor the unbound intent is a runnable config.

```sh
cp experiments/devmind/binding.example.json "$EXPERIMENT_DIR/bindings.json"
# Edit bindings.json with actual artifacts, measured counts and selected runtime.
python scripts/bind-experiment.py experiments/devmind/experiment.json \
  --bindings "$EXPERIMENT_DIR/bindings.json" \
  --output "$EXPERIMENT_DIR/run.json"
sparselab config validate "$EXPERIMENT_DIR/run.json" --kind run --json
sparselab inspect "$EXPERIMENT_DIR/run.json" --json
```

Binding writes a fresh file and validates the native RunConfig schema. It does not
verify artifact contents or claim readiness. Lab's native mixture/tokenizer and
prepared-input verification remain authoritative. Existing prepared inputs may be
supplied through native `train --stage-bundle`; bind that artifact using Lab's own
contract, not a supervisor log. Confirm runtime availability and measured supply
at the execution site. No invented host paths or hashes are committed here.

## Run, inspect, resume, evaluate

Use fresh `RUN_ID` and `CHILD_ID` values and set `RUNS_DIR` to the bound
`logging.root_dir`. Native Lab owns run records, checkpoint identity, errors and
cancellation. Retain the plan revision, bound config, runtime provenance and native
run ID beside the results. Editing the next plan never rewrites a completed attempt.

```sh
sparselab train "$EXPERIMENT_DIR/run.json" --run-id "$RUN_ID"
# CHECKPOINT is a real immutable generation path emitted by Lab, not a run ID.
sparselab checkpoint inspect "$CHECKPOINT" --json
sparselab checkpoint verify "$CHECKPOINT" --config "$EXPERIMENT_DIR/run.json" --json
# Only for an interrupted run with unchanged scientific config and budget:
sparselab train "$EXPERIMENT_DIR/run.json" --resume "$CHECKPOINT" --run-id "$CHILD_ID"
sparselab eval "$CHILD_ID" --checkpoint "$CHILD_CHECKPOINT" --runs-dir "$RUNS_DIR"
```

For an uninterrupted run, evaluate `RUN_ID` and its checkpoint instead. Resume
creates a child run and preserves the parent. A runtime failure remains a failure,
with any completed native checkpoint available for inspection; missing stdout does
not turn an intact checkpoint into nonexistent work. Evaluation above measures
native held-out loss; it does not claim the protocol's external benchmark suite or
fixed English/technical panels have been run. Bind actual frozen panels before
using `eval --panel PANEL --output NEW_RESULT.json`. Those panels and benchmark
results remain outstanding scientific deliverables.

## Derive the next iteration

Use native `config derive` to create a new editable config with a recorded delta.
For example, an explicitly separate first full-model 32-update iteration:

```sh
sparselab config derive "$EXPERIMENT_DIR/run.json" \
  --set 'name="devmind-340m-first32"' \
  --set training.max_steps=32 --set training.max_tokens=4194304 \
  --set optimizer.warmup_steps=4 --set optimizer.decay_steps=32 \
  --set checkpoint.every_steps=4 --set evaluation.every_steps=32 \
  --output "$EXPERIMENT_DIR/first32.yaml"
```

The architecture, tokenizer and batch stay unchanged. This explicit budget and
schedule change is a separate experiment iteration, not completion of the 12B
baseline or a universal prerequisite. Bind it to a matching verified unique mixture
if the baseline's data is unavailable; changing only the training budget does not
create missing data. [`first32/`](first32/README.md) records the older retained-subset
recipe and its attempt-specific limits, not permanent lab limits. Scientific
changes start new runs; `--resume` is for compatible checkpoint continuation.

## Verification and remaining bindings

Reviewed against Lab `9d4c840ef1f102becf27532c2548c505c2ed35a6`.
`tests/test_devmind_experiment.py` checks authoring, missing binding refusal and
exclusive output. Its optional native integration checks validate the full model's
RunConfig and parameter inventory, compile actual train/resume/eval CLI arguments,
and exercise native derivation. They never allocate/train the full model or access
production data. Run with Lab installed:

```sh
WORKSHOP_LAB_CHECKOUT=/absolute/path/to/tiny-sparse-lab \
  python -m unittest discover -s tests -p test_devmind_experiment.py -v
```

Execution-site decisions still needed: verified mixture and tokenizer locations,
actual data counts, runtime/device, cache/run store, checkpoint retention capacity,
and frozen evaluation panels. The baseline uses 91,553 as a step ceiling for 12B
training targets at 131,072/update; Lab stops at the declared target budget and
records actual counters. Do not replace the baseline with a smaller model or
silently increase exposures to satisfy supply. Success means the goal and
`definition_of_done` in the experiment are met, not that all preparation leaves ran.
