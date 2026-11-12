# Run and revise DevMind

[`experiment.json`](experiment.json) is the experiment you edit. It references
[`run.json`](run.json), [`model.json`](model.json) and
[`optimizer.json`](optimizer.json). It keeps the full 341,885,952-parameter
architecture and defines the 12B unique-target 60/20/20 baseline. Run the
preparation phases only to produce inputs you are missing; you do not need all
25 steps for every iteration. Reuse artifacts that haven't changed.

This page covers the dense 12B baseline and how to bind it. For what happened
after training stopped on October 29, see the
[Engram campaign record](engram-campaign-20261106.md). The
[B70 performance notes](b70-performance-20261106.md#completed-finite-100m-target-nightly-validation)
describe the finished 100M-target nightly validation, including a GPU resume in a
fresh process and a cold full-state check at the end. The dense 12B baseline
itself has not been completed, and passing the schema checks below doesn't mean
a run is ready to launch.

## Bind once to real inputs

Run from a Workshop checkout, in the Python environment where Lab is installed.
Set `EXPERIMENT_DIR` to a working directory outside the repository. Copy
`binding.example.json` there and replace every null with a real value:

- `dataset`: the materialized mixture file and its output, a writable cache,
  measured document and token limits, and the actual license information. Keep
  the whole validation split. The 12B mixture is not finished yet; the retained
  R36 data and newly acquired shards don't add up to it.
- `tokenizer.path`: the retained 32K tokenizer (R40), or a tokenizer you have
  deliberately revised. You don't need to fit a tokenizer just to bind a run.
- `runtime`: the engine, backend and precision. The example uses BF16,
  transformer-block activation checkpointing and `estimate_policy: observe`, so
  memory estimates are reported but not enforced; real resource limits and
  runtime failures still apply. The example doesn't change the model or batch or add
  a CPU-derived limit.
  Pick the backend you actually have rather than leaving `auto` in place.
- `logging.root_dir`: the run store, outside the recipe repository.

Use absolute paths for everything you bind, so moving the config doesn't change
its inputs. Neither the example nor the unbound experiment runs as-is.

```sh
cp experiments/devmind/binding.example.json "$EXPERIMENT_DIR/bindings.json"
# Edit bindings.json with actual artifacts, measured counts and selected runtime.
klab config compose experiments/devmind/run.json \
  model=experiments/devmind/model.json \
  optimizer=experiments/devmind/optimizer.json \
  "$EXPERIMENT_DIR/bindings.json" --output "$EXPERIMENT_DIR/run.yaml"
klab inspect "$EXPERIMENT_DIR/run.yaml" --json
```

`config compose` merges the run section, the model and optimizer sections and
your bindings. If the result isn't a complete, valid RunConfig it refuses and
names the unbound `null`. Otherwise it writes a new file with the digest of each
part. It checks structure only; Lab's mixture, tokenizer and prepared-input
checks are what confirm the artifacts themselves. To reuse prepared inputs, pass
them with `train --stage-bundle` and bind them the way Lab expects rather than
from a supervisor log. Check the runtime and the available data on the machine
that will run the job. We don't commit host paths or hashes here.

## Run, inspect, resume, evaluate

Pick new `RUN_ID` and `CHILD_ID` values and set `RUNS_DIR` to the bound
`logging.root_dir`. Lab keeps the run records, checkpoints, errors and
cancellations. Keep the plan revision, bound config, runtime details and run ID
next to the results. Editing the next plan never changes a finished attempt.

```sh
klab train "$EXPERIMENT_DIR/run.json" --run-id "$RUN_ID"
# CHECKPOINT is a real immutable generation path emitted by Lab, not a run ID.
klab checkpoint inspect "$CHECKPOINT" --json
klab checkpoint verify "$CHECKPOINT" --config "$EXPERIMENT_DIR/run.json" --json
# Only for an interrupted run with unchanged scientific config and budget:
klab train "$EXPERIMENT_DIR/run.json" --resume "$CHECKPOINT" --run-id "$CHILD_ID"
klab eval "$CHILD_ID" --checkpoint "$CHILD_CHECKPOINT" --runs-dir "$RUNS_DIR"
```

If the run wasn't interrupted, evaluate `RUN_ID` and its checkpoint instead.
Resume creates a child run and keeps the parent. A runtime failure is still a
failure, but any checkpoint it finished is there to inspect, even if stdout was
lost. The `eval` above measures held-out loss only. The protocol's benchmark
suite and fixed English and technical panels still need to be run: bind the
frozen panels first, then use `eval --panel PANEL --output NEW_RESULT.json`.

## Derive the next iteration

Use `config derive` to create a new config with the change recorded. For
example, a separate first full-model iteration of 32 updates:

```sh
klab config derive "$EXPERIMENT_DIR/run.json" \
  --set 'name="devmind-340m-first32"' \
  --set training.max_steps=32 --set training.max_tokens=4194304 \
  --set optimizer.warmup_steps=4 --set optimizer.decay_steps=32 \
  --set checkpoint.every_steps=4 --set evaluation.every_steps=32 \
  --output "$EXPERIMENT_DIR/first32.yaml"
```

The architecture, tokenizer and batch stay the same. Only the budget and
schedule change, so this is its own experiment iteration, and you don't need it
before other runs. If the baseline's data isn't available, bind it to a matching
unique mixture; a smaller budget doesn't create the missing data.
[`first32/`](first32/README.md) records the older retained-subset recipe and the
limits of that one attempt. Start a new run for any scientific change; use
`--resume` only to continue a compatible checkpoint.

## Verification and remaining bindings

Reviewed against Lab `9d4c840ef1f102becf27532c2548c505c2ed35a6`. To check these
configs against the Lab you have installed, run
`klab config validate experiments/devmind` for the sections and
`klab inspect "$EXPERIMENT_DIR/run.yaml"` for the composed config's parameter
inventory and memory plan. Neither command allocates the model or reads training
data.

Still to decide on the machine that runs it: where the mixture and tokenizer
live, actual data counts, runtime and device, cache and run store, checkpoint
storage, and the frozen evaluation panels. The baseline caps training at 91,553
steps, which is 12B targets at 131,072 per update; Lab stops at the target budget
and records the actual counts. If data runs short, report it. Don't shrink the
model or quietly repeat data to fill the gap. The run is done when it meets the
goal and `definition_of_done` in the experiment, whether or not every
preparation leaf ran.
