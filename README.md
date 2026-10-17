# Kybern Workshop

Runnable projects and experiment recipes built with [Tiny Sparse Lab](https://github.com/supernovae/tiny-sparse-lab).
Choose a project, inspect its configuration, run it with the pinned Lab runtime,
and use its evidence to understand what happened. Workshop holds the project
recipes and results; Lab provides preparation, execution, evaluation and reporting.

Use the [Workshop operator entrypoint](docs/operator.md) to bind an approved native
Campaign to a stable Notion experiment ID and a fresh attempt, drive the existing
Harness session, and inspect execution, evidence and scientific assessment separately.
Notion owns scheduling; this entrypoint does not poll or queue work.

## Projects

| Project | What you'll learn | Readiness | Start here |
| --- | --- | --- | --- |
| TinyStories microlab | Compare FFN width 256 versus 384 using native Lab commands; inspect a separate usable-story validation proposal. | Declarations and metadata checks complete; this recipe and its story-quality proposal are unexecuted. | [Native run guide](examples/tinystories-microlab/README.md) · [Historical smaller CPU smoke](results/2026-10-15-tinystories-smoke/README.md) |
| Synthetic CPU | Prepare synthetic text and a tokenizer, approve one tiny training attempt, evaluate it and verify a report. No corpus or model download. | Measured end to end at its recorded pins, including replay with no new attempt. Demonstrates workflow wiring, not model quality. | [Run guide](examples/synthetic-cpu/README.md) · [Recorded result](results/2026-10-14-synthetic-cpu/README.md) |

Start with the [native TinyStories microlab](examples/tinystories-microlab/README.md).
Its 40-update teaching comparison is distinct from the measured width-32 CPU smoke.
The [usable-story proposal](examples/tinystories-microlab/usable-story-proposal.md)
requires verified retained model artifacts and fresh CPU quality evidence; neither
metadata checks nor a successful tiny run establish useful story generation.

The [CPU repeatability recipe](examples/cpu-repeatability/README.md) remains an
unexecuted scaffold. The older [TinyStories migration draft](https://github.com/supernovae/kybern-workshop/pull/3)
is not the current run guide.

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

## Active research portfolio

Browse the [experiment catalog](catalog/README.md) for preserved prior experiments, original evidence, and explicit resume/rebuild prerequisites. Active research intent is separate from historical execution and current runtime readiness.
