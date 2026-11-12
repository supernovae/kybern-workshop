# Running Workshop Recipes with Kybern Model Lab

Every experiment in this repository runs with [Kybern Model Lab](https://github.com/supernovae/model-lab) (`klab`).
This repository holds the configs, dataset pins, and result records. Lab does the data preparation, training, evaluation, probes, and reporting.

Run a recipe from a clone of this repository, or copy its directory into your own project. For a guided introduction to Lab, see [Run the Lab on kybern.dev](https://kybern.dev/learn/lab/).

## Choosing a Workflow

| Goal | `klab` workflow | Notes |
| --- | --- | --- |
| **Check every config** | `config validate DIR` | Checks each run, tokenizer, model, and optimizer config under a directory against your installed Lab, and exits non-zero if any fail. CI runs it on this repository. |
| **Bind sections and local paths** | `config compose` | Merges a run section, model and optimizer sections, and a file of local paths into one checked run config. Used by [DevMind](../experiments/devmind/run.md). |
| **Compare a single change** | `config validate`, `config derive`, then `try` and `report` | Trains a baseline and a candidate on the same data, then scores held-out loss and probes. Used by [TinyStories microlab](../examples/tinystories-microlab/README.md). |
| **Train & inspect a full baseline** | `data lock`, `experiment recipe preparation apply`, `stage`, `train`, `eval`, `generate` | Runs each step yourself, including continuing from a checkpoint and generating from a prompt panel. Used by [TinyStories CPU baseline](../examples/tinystories-useful/README.md). |
| **Package a shareable recipe** | `experiment recipe create` and `experiment recipe export` | Bundles configs and metadata with content hashes, so someone else can inspect them and fill in their own local paths. |
| **Prepare a corpus & tokenizer** | `experiment recipe preparation inspect` and `apply` | Checks output paths, then takes the dataset snapshot, trains the tokenizer, and packs tokens. Used by [Synthetic CPU](../examples/synthetic-cpu/README.md). |
| **Run a staged campaign** | `experiment recipe workflow inspect`, `resolve`, `apply`, `approve`, and `report` | Runs a campaign end to end, stopping at each approval gate until you approve, and writes a report. |

## Packaging and Inspecting a Recipe

Package a recipe directory and check its paths before you train anything.

For example, with the files in [`examples/synthetic-cpu`](../examples/synthetic-cpu/README.md):

```sh
INPUT="/path/to/kybern-workshop/examples/synthetic-cpu"
DEST="/path/to/work/synthetic-cpu-recipe"

klab experiment recipe create "$INPUT" --profile preparation \
  --id workshop-synthetic-cpu-preparation --entrypoint preparation-campaign.json \
  --file campaign:preparation-campaign.json --file run_config:run.json \
  --file tokenizer_config:tokenizer-config.json --file metadata:monitor.json \
  --output "$DEST"

klab experiment recipe preparation inspect "$DEST/recipe.json" \
  --bindings /path/to/work/local-bindings.json --json
```

`local-bindings.json` points the recipe's outputs at a workspace directory outside Git:

```json
{
  "artifacts": {},
  "config_paths": {
    "tokenizer-config.json": {
      "output_dir": "/path/to/work/tokenizer",
      "dataset.cache_dir": "/path/to/work/cache"
    },
    "run.json": {
      "tokenizer.path": "/path/to/work/tokenizer/tokenizer.json",
      "dataset.cache_dir": "/path/to/work/cache",
      "logging.root_dir": "/path/to/work/runs"
    }
  }
}
```

`inspect` checks every config and path binding. It doesn't create output directories or start a run. The [validation record](native-acceptance-2026-10-18.md) shows example checks across the current recipes.

## Records Pinned Before the Rename

Kybern Model Lab used to be `supernovae/tiny-sparse-lab`, with a `sparselab` CLI. It is now [supernovae/model-lab](https://github.com/supernovae/model-lab): the CLI and import package are `klab`, environment variables start with `KLAB_`, and versioned format IDs use `klab-*`.

Commit SHAs and pull-request numbers carried over to the renamed repository unchanged. If you replay a recipe at a Lab commit from before the rename, three old names still apply:

- The CLI and import package at those commits are `sparselab`, and environment variables use `SPARSELAB_`. Substitute those names when replaying at the recorded commit; use `klab` on current `main`.
- Pinned container digests stay under their original package, `ghcr.io/supernovae/tiny-sparse-lab@sha256:...`. New images publish to `ghcr.io/supernovae/model-lab`.
- Recorded files keep their original bytes, old names included: the hashed LAB86 preparation package (`experiments/devmind/preparation/lab86/`), the JSON records under `results/`, and the host paths they mention.

## Further Reading

- [Kybern Model Lab Documentation](https://github.com/supernovae/model-lab/tree/main/docs) — CLI guides for `try`, `report`, `probe`, `explore`, and `dashboard`.
- [TinyStories Training Guide (kybern.dev)](https://kybern.dev/models/tinystories-training/) — Interactive walkthrough of the TinyStories baseline and microlab comparison.
- [Matched Comparisons (kybern.dev)](https://kybern.dev/learn/lab/matched-comparisons/) — How to design controlled experiments with paired seeds.
