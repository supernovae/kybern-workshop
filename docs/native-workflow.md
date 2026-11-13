# Running Workshop Recipes with Kybern Model Lab

Every experiment in this repository runs with [Kybern Model Lab](https://github.com/supernovae/model-lab) (`klab`).
This repository holds the configs, dataset pins and result records. Lab does the data preparation, training, evaluation,
probes and reporting. Run a recipe from a clone of this repository, or copy its directory into your own project.
For a guided introduction, see [Run the Lab on kybern.dev](https://kybern.dev/learn/lab/).

## Choosing a workflow

| Goal | `klab` commands | Used by |
| --- | --- | --- |
| **Check every config** | `config validate DIR` | CI runs it on this repository against Lab `main`. |
| **Check a model fits** | `inspect CONFIG` | Reports parameters and a memory estimate without training. |
| **Compare one change** | `config derive`, `try`, `report` | [TinyStories microlab](../examples/tinystories-microlab/README.md) |
| **Confirm it across seeds or values** | `sweep`, `report` | [TinyStories microlab](../examples/tinystories-microlab/README.md) |
| **Build a model end to end** | `data lock`, `data snapshot`, `tokenizer train`, `data prepare`, `stage`, `train`, `eval`, `probe`, `generate`, `chat` | [Synthetic CPU](../examples/synthetic-cpu/README.md), [TinyStories baseline](../examples/tinystories-useful/README.md) |
| **Continue or extend a run** | `train --resume`, `--extend-budget`, `--promote` | [Checkpointing](https://github.com/supernovae/model-lab/blob/main/docs/checkpointing.md) |
| **Bind sections and local paths** | `config compose` | [Devmind](../experiments/devmind/README.md) |
| **Queue independent runs** | `experiment submit`, `list`, `cancel`, `resume`, `collect`, plus `worker` | [Workers](https://github.com/supernovae/model-lab/blob/main/docs/workers.md) |

Lab no longer has campaigns, experiment plans, training programs or recipe workflows
(`klab campaign`, `klab experiment recipe`). Recipes here are plain declarations plus the commands in their READMEs.

## Making a run repeatable

- Pin the dataset revision and keep the lock file with your records.
- Put the seed in the declaration. For a comparison, use `sweep` with `seeds: [1, 2, 3]` rather than a single seed.
- Use `repeat_baseline: true` in a `try` policy to see run-to-run drift next to the candidate's effect.
- Run `klab probe` so held-out items are screened for leakage into the training data.
- Record the Lab commit, backend, precision, and the `TRY_ID`, `SWEEP_ID` or run ID with anything you publish.

## Records Pinned Before the Rename

Kybern Model Lab used to be `supernovae/tiny-sparse-lab`, with a `sparselab` CLI. It is now [supernovae/model-lab](https://github.com/supernovae/model-lab): the CLI and import package are `klab`, environment variables start with `KLAB_`, and versioned format IDs use `klab-*`.

Commit SHAs and pull-request numbers carried over to the renamed repository unchanged. If you replay a recipe at a Lab commit from before the rename, three old names still apply:

- The CLI and import package at those commits are `sparselab`, and environment variables use `SPARSELAB_`. Substitute those names when replaying at the recorded commit; use `klab` on current `main`.
- Pinned container digests stay under their original package, `ghcr.io/supernovae/tiny-sparse-lab@sha256:...`. New images publish to `ghcr.io/supernovae/model-lab`.
- Recorded files keep their original bytes, old names included: the JSON records under `results/` and the host paths they mention.

## Further Reading

- [Kybern Model Lab Documentation](https://github.com/supernovae/model-lab/tree/main/docs) — CLI guides for `try`, `report`, `probe`, `explore`, and `dashboard`.
- [TinyStories Training Guide (kybern.dev)](https://kybern.dev/models/tinystories-training/) — Interactive walkthrough of the TinyStories baseline and microlab comparison.
- [Matched Comparisons (kybern.dev)](https://kybern.dev/learn/lab/matched-comparisons/) — How to design controlled experiments with paired seeds.
