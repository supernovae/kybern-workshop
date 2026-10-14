# Kybern Workshop

Runnable projects and experiment recipes built with [Tiny Sparse Lab](https://github.com/supernovae/tiny-sparse-lab).
Choose a project, inspect its configuration, run it with the pinned Lab runtime,
and use its evidence to understand what happened. Workshop holds the project
recipes and results; Lab provides preparation, execution, evaluation and reporting.

## Projects

| Project | What you'll learn | Readiness | Start here |
| --- | --- | --- | --- |
| Synthetic CPU | Prepare synthetic text and a tokenizer, approve one tiny training attempt, evaluate it and verify a report. No corpus or model download. | Measured end to end at its recorded pins, including replay with no new attempt. Demonstrates workflow wiring, not model quality. | [Run guide](examples/synthetic-cpu/README.md) · [Recorded result](results/2026-10-14-synthetic-cpu/README.md) |

The synthetic CPU project is currently the only project on main. The
[TinyStories migration draft](https://github.com/supernovae/kybern-workshop/pull/3)
is unfinished scaffolding, not a runnable or execution-validated Workshop project.
It still needs alignment with generic Lab interfaces and an end-to-end Workshop proof.

## Before you run

- Have Git, a writable external work directory and the project's pinned Lab CPU
  environment. The synthetic guide records Python 3.14.8, PyTorch 2.14.0+cpu,
  exact Lab/Workshop revisions and dependency setup.
- Read the project's workload, resource limits and approval steps before executing
  commands. Preparation, runtime probes and evaluation can do work beyond the main
  training budget; provision a runtime only when authorized.
- Keep generated data, checkpoints, bindings, admissions and local execution
  records outside Git. Fresh runs need their own prepared inputs and reviewed
  identities; cloning a recipe does not supply those payloads or approval.

Start with the [synthetic CPU setup](examples/synthetic-cpu/README.md#pins-and-setup),
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
