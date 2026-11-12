# Workshop components

This package adds model parts to
[Kybern Model Lab](https://github.com/supernovae/model-lab) from outside Lab.
Lab looks up each attention, feed-forward and memory layer by its kind, and
this package registers extra kinds through the `klab.components` entry-point
group. Lab's
[component guide](https://github.com/supernovae/model-lab/blob/main/docs/components.md)
explains what a component has to provide.

| Kind | Slot | What it is |
| --- | --- | --- |
| `cosine` | attention | Scores are scaled cosine similarities of rotary-encoded queries and keys, and each head learns one scale. Supports incremental decoding. |

## Install

Install into the environment that runs `klab`, from the Lab checkout:

```sh
uv pip install -e /path/to/kybern-workshop/components
```

A config can then name the kind:

```yaml
attention:
  kind: cosine
  params: {initial_scale: 8, learned_scale: true}
```

[`examples/custom-attention`](../examples/custom-attention/README.md) trains a
small model with it.

## Add another kind

1. Write a module file like `src/workshop_components/cosine.py`: a params model,
   a `build(model, attention, params)` function that imports Torch inside it,
   and a `COMPONENT`.
2. Add one line to `[project.entry-points."klab.components"]` in
   `pyproject.toml`, named `SLOT.KIND` (`attention.*`, `ffn.*` or `memory.*`).
3. Reinstall the package so the new entry point is visible.

Each run records the package name and version that supplied each kind. Bump
`version` whenever a kind's behaviour changes, so you can tell apart two runs
of the same config.
