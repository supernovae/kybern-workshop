# Train a model with an attention kind Lab does not ship

`model.yaml` sets `attention.kind: cosine`. That kind comes from
[`components/`](../../components/README.md) in this repository; Lab is not
edited. The corpus and tokenizer settings are Lab's small CC0
`build-local-text` example.

Install the component package into the Lab environment once, then copy this
directory out of the checkout so `work/` is created outside Git:

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

Without the package installed, `klab` refuses the config and names the entry
point it looked for. The run's events record
`kybern-workshop-components 0.1.0` as the source of the kind.

This proves the extension path on a 131K-parameter model and a 600-sentence
corpus. It says nothing about whether cosine attention is better than dense
attention.
