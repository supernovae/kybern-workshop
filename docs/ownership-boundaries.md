# Repository Structure & Helper Scripts

Workshop is organized around declarative recipes that run on [Tiny Sparse Lab](https://github.com/supernovae/tiny-sparse-lab). For everyday usage, follow the [Tiny Sparse Lab workflow guide](native-workflow.md).

## Active Recipe Directories

- [`examples/synthetic-cpu/`](../examples/synthetic-cpu/README.md) — Offline synthetic CPU smoke test for verifying data preparation, training, evaluation, and reporting.
- [`examples/tinystories-microlab/`](../examples/tinystories-microlab/README.md) — Starter TinyStories FFN width comparison (`256` vs. `384`) using `sparselab try`.
- [`examples/tinystories-useful/`](../examples/tinystories-useful/README.md) — Completed 8,192-update TinyStories CPU learning baseline and improvement exercises.
- [`examples/tinystories-worker/`](../examples/tinystories-worker/README.md) and [`examples/tinystories-rocm/`](../examples/tinystories-rocm/README.md) — Staged campaign and container handoff recipes for TinyStories smoke runs.
- [`experiments/devmind/`](../experiments/devmind/README.md) — **DevMind 340M Base** model architecture proposal and 24-phase corpus preparation recipes.

- [`experiments/tinystories/`](../experiments/tinystories/README.md) — 5M/50M recipes with shared preparation, tier budgets and a lifecycle/operations guide. Execution and portability remain unverified.

## Helper Scripts Inventory

While all model training, data preparation, and evaluation happen inside Tiny Sparse Lab, this repository includes a small set of standard-library Python helpers for binding paths and staging inputs in containerized runs:

| Path | Purpose |
| --- | --- |
| `scripts/seal-inputs.py` | Copies completed `sparselab` preparation output hashes into a workflow descriptor and writes local path bindings. |
| `scripts/handoff.py` & `scripts/workshop.py` | Binds campaign templates (`examples/operator/`) and stages prepared inputs for supervised container sessions. |
| `examples/tinystories-worker/handoff.py` | Generates CLI command lists and path bindings for the paired TinyStories CPU smoke workflow. |
| `examples/tinystories-rocm/handoff.py` & `bind_session.py` | Verifies prepared input manifests and binds container session templates for ROCm smoke testing. |

File hashes for these tracked Python scripts and tests are recorded in [`ownership-boundaries.json`](ownership-boundaries.json). New experiments should use declarative `sparselab` configurations rather than custom Python wrappers.
