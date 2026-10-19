# Running Workshop Recipes with Tiny Sparse Lab

Every experiment in this repository is designed to run with [Tiny Sparse Lab](https://github.com/supernovae/tiny-sparse-lab) (`sparselab`).
Workshop stores the declarative configurations, dataset pins, and result records; Tiny Sparse Lab handles data preparation, training, evaluation, behavioral probes, and reporting.

You can run these recipes from a clone of this repository or copy any recipe directory into your own project. For a guided introduction to the workbench, see [Run the Lab on kybern.dev](https://kybern.dev/learn/lab/).

## Choosing a Workflow

| Goal | `sparselab` workflow | Notes |
| --- | --- | --- |
| **Compare a single change** | `config validate`, `config derive`, then `try` and `report` | Trains baseline and candidate arms on shared data and scores held-out loss + probes. Used by [TinyStories microlab](../examples/tinystories-microlab/README.md). |
| **Train & inspect a full baseline** | `data lock`, `experiment recipe preparation apply`, `stage`, `train`, `eval`, `generate` | Step-by-step pipeline with checkpoint continuation and prompt-panel generation. Used by [TinyStories CPU baseline](../examples/tinystories-useful/README.md). |
| **Package a shareable recipe** | `experiment recipe create` and `experiment recipe export` | Bundles configs and metadata with content hashes so another developer can inspect and bind local paths. |
| **Prepare a corpus & tokenizer** | `experiment recipe preparation inspect` and `apply` | Validates output paths before running dataset snapshot, tokenizer training, and token packing. Used by [Synthetic CPU](../examples/synthetic-cpu/README.md). |
| **Run a staged campaign** | `experiment recipe workflow inspect`, `resolve`, `apply`, `approve`, and `report` | End-to-end campaign pipeline with explicit approval gates and verified reporting. |

## Packaging and Inspecting a Recipe

You can package any recipe directory into a verified inventory and inspect its path bindings before running a single training step.

For example, using the declarations in [`examples/synthetic-cpu`](../examples/synthetic-cpu/README.md):

```sh
INPUT="/path/to/kybern-workshop/examples/synthetic-cpu"
DEST="/path/to/work/synthetic-cpu-recipe"

sparselab experiment recipe create "$INPUT" --profile preparation \
  --id workshop-synthetic-cpu-preparation --entrypoint preparation-campaign.json \
  --file campaign:preparation-campaign.json --file run_config:run.json \
  --file tokenizer_config:tokenizer-config.json --file metadata:monitor.json \
  --output "$DEST"

sparselab experiment recipe preparation inspect "$DEST/recipe.json" \
  --bindings /path/to/work/local-bindings.json --json
```

Where `local-bindings.json` maps the recipe's outputs to your local workspace directory outside Git:

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

`inspect` checks that all configuration schemas and path bindings are valid without creating output directories or starting a run. See the [metadata validation record](native-acceptance-2026-10-18.md) for example CLI checks across the active Workshop recipes.

## Further Reading

- [Tiny Sparse Lab Documentation](https://github.com/supernovae/tiny-sparse-lab/tree/main/docs) — CLI guides for `try`, `report`, `probe`, `explore`, and `dashboard`.
- [TinyStories Training Guide (kybern.dev)](https://kybern.dev/models/tinystories-training/) — Interactive walkthrough of the TinyStories baseline and microlab comparison.
- [Matched Comparisons (kybern.dev)](https://kybern.dev/learn/lab/matched-comparisons/) — How to design controlled experiments with paired seeds.
