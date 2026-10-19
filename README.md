# Kybern Workshop

Runnable projects and experiment recipes built with [Tiny Sparse Lab](https://github.com/supernovae/tiny-sparse-lab).
Choose a project, inspect its configuration, run it with the pinned Lab runtime,
and use its evidence to understand what happened. Workshop holds the project
recipes and results; Lab provides preparation, execution, evaluation and reporting.

Use the [native Lab workflow](docs/native-workflow.md) to author and inspect declarations
in any local directory or repository, then follow the selected recipe’s native
preparation and execution guide. Workshop, Harness and Notion are not runtime
requirements. The [internal operator reference](docs/operator.md) preserves an older
runner integration; its helpers are tracked in the [ownership audit](docs/ownership-boundaries.md).

## Projects

| Project | What you'll learn | Readiness | Start here |
| --- | --- | --- | --- |
| TinyStories microlab | Compare FFN width 256 versus 384 using native Lab commands; inspect a completed longer CPU learning baseline. | 40-update comparison remains unexecuted; the separate 8,192-update baseline completed with a failed story-quality gate. | [Native run guide](examples/tinystories-microlab/README.md) · [Historical smaller CPU smoke](results/2026-10-15-tinystories-smoke/README.md) |
| Synthetic CPU | Prepare synthetic text and a tokenizer, approve one tiny training attempt, evaluate it and verify a report. No corpus or model download. | Measured end to end at its recorded pins, including replay with no new attempt. Demonstrates workflow wiring, not model quality. | [Run guide](examples/synthetic-cpu/README.md) · [Recorded result](results/2026-10-14-synthetic-cpu/README.md) |

For a basic CPU introduction, start with [synthetic CPU](examples/synthetic-cpu/README.md)
and its [current metadata route](docs/native-workflow.md). For stories, use the [native TinyStories microlab](examples/tinystories-microlab/README.md).
Its 40-update teaching comparison is distinct from the measured width-32 CPU smoke.
The [longer CPU learning baseline](examples/tinystories-useful/README.md) now has
[all 27 recorded outputs](results/2026-10-19-tinystories-cpu/README.md), immutable
checkpoint/source identities and measured budgets. Its original story-quality gate
failed; it is published to support reproducible learning and future improvement.

## Authored experiments

[DevMind — DevMind 340M Base](experiments/devmind/README.md)
relocates the exact preparation declarations and records proposed model/training
science. It is not execution-ready: generated inputs, scientific review, native
portable bindings and runtime budgets remain outstanding. No weights are supplied.

## Before you run

- Have Git, a writable external work directory and the project's pinned Lab
  environment and matching backend image. The synthetic guide records Python 3.14.8, PyTorch 2.14.0+cpu,
  exact Lab/Workshop revisions and dependency setup.
- Read the project's workload, resource limits and approval steps before executing
  commands. Preparation, runtime probes and evaluation can do work beyond the main
  training budget; provision a runtime only when authorized.
- Keep generated data, checkpoints, bindings, admissions and local execution
  records outside Git. Reuse verified prepared inputs through writable copies when starting a fresh
  experiment; cloning a recipe does not include dataset payloads or checkpoints.

For a no-download introduction, use the [synthetic CPU setup](examples/synthetic-cpu/README.md#pins-and-setup),
then follow its preparation, approval, execution and reporting steps in order.
The example remains pinned to Lab `b155cdcc1462cfbcbd5f0cf5261eb8aa197ef9dc`;
its recorded validation does not establish compatibility with newer Lab contracts.

## Inspect and build on a project

Browse the [synthetic declarations](examples/synthetic-cpu), read the
[measured result and limitations](results/2026-10-14-synthetic-cpu/README.md), or
inspect the [historical command record](results/2026-10-14-synthetic-cpu/commands.md).
The project run guide retains setup details, monitoring instructions and failure
notes. Preserve earlier evidence when changing a recipe, and distinguish a
proposed configuration from a measured result.

## Scope and historical research

The active showcase contains three families: basic synthetic CPU, TinyStories,
and DevMind. Other experiments and imported old-run archives have been retired
from this tree. Their original bytes remain in Git history; see the
[retirement map](docs/retired-research.md). Future research ideas belong to the
coordinated Notion backlog as new experiments, not promises to resume old runs.

## Contributing

Read the [current-interface contribution policy](CONTRIBUTING.md) before adapting or reproducing an experiment. Historical evidence remains preserved; new reproductions use current interfaces and new identities.
