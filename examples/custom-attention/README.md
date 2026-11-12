# Train a model with a custom attention kind

`model.yaml` sets `attention.kind: cosine`, a kind supplied by the package in
[`components/`](../../components/README.md). The corpus and tokenizer settings
come from Lab's small CC0 `build-local-text` example.

Install the component package into your Lab environment once. Then copy this
directory out of the checkout, so `work/` ends up outside Git:

```sh
uv pip install -e /path/to/kybern-workshop/components

cp -r examples/custom-attention "$KLAB_WORK_DIR/custom-attention"
cd "$KLAB_WORK_DIR/custom-attention"
klab tokenizer train tokenizer.yaml
klab inspect model.yaml
klab data prepare model.yaml
klab train model.yaml --run-id cosine
klab generate cosine --runs-dir work/runs --prompt "The baker counts"
```

If the package isn't installed, `klab` rejects the config and names the entry
point it looked for. When it is, the run's events record
`kybern-workshop-components 0.1.0` as the source of the kind.

This shows that a custom kind can be plugged in and trained, using a
131K-parameter model and a 600-sentence corpus. It's too small to tell you
whether cosine attention beats dense attention.
