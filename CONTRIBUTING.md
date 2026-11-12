# Contributing to Kybern Workshop

We welcome pull requests from anyone running small language-model experiments with [Kybern Model Lab](https://github.com/supernovae/model-lab). You might be repeating one of our recipes on your own hardware, trying to improve one of our baselines, or sharing a new experiment from your fork.

## Ways to Contribute

1. **Link your fork or experiment in the README**  
   Running an experiment in your own repository or fork? Open a PR that adds it to the **Community Experiments & Forks** section of the [main README](README.md#community-experiments--forks). Include the repository link, the question you're testing, the model size and backend, and a short summary of what you found.
2. **Repeat or improve a recipe**  
   Run the [basic CPU smoke test](examples/synthetic-cpu/README.md), compare architectures in the [TinyStories microlab](examples/tinystories-microlab/README.md), or try to beat our [8,192-update TinyStories baseline](examples/tinystories-useful/README.md). Its validation loss dropped to `1.704`, but its free generation still loops and drifts.
3. **Share a new recipe**  
   Add a self-contained recipe under `examples/` or `experiments/`, written as Kybern Model Lab YAML or JSON configs.

## How Workshop and Kybern Model Lab Fit Together

- **Workshop holds recipes and records:** configs (`RunConfig`, tokenizer configs, dataset locks, `try` changes, and campaign definitions), walkthroughs, and compact result records.
- **Kybern Model Lab does the work:** data preparation, training, probes, checkpoint verification, reporting, and the web dashboard all come from [supernovae/model-lab](https://github.com/supernovae/model-lab).
- **Keep recipes to configs:** don't add helper scripts, launchers, validators, or per-recipe tests; CI rejects them. If an experiment needs something Lab can't do yet, add it to Kybern Model Lab. A new model part or training objective can go in a component package under `components/`.
- **Check your configs:** `klab config validate .` checks every run, tokenizer, model, and optimizer config against the Lab you have installed. CI runs the same check against Lab `main`.
- **Working with an AI agent:** point it at [`AGENTS.md`](AGENTS.md), which lists the Lab command for each job and what to keep out of this repository.

## Making a Run Others Can Repeat

These follow the practices in the [Kybern Community Lab](https://kybern.dev/research/community-lab/) and [Experiment Methods](https://kybern.dev/experiments/methods/) guides:

- **Record your environment:** the `model-lab` commit SHA, Python and PyTorch/MLX versions, the backend (`cpu`, `cuda`, `rocm`, `xpu`, `mps`, or `metal`), and the dataset revision.
- **Use new run IDs:** every reproduction or follow-up gets its own run and checkpoint IDs. Link to the baseline you compared against instead of editing its result record.
- **Keep large files out of Git:** don't commit raw dataset downloads, packed token arrays, or model weights (`.pt`, `.safetensors`, and so on). Do commit the configs, SHA-256 manifests, loss curves, and sample generation JSON files so others can check your results and repeat the run.
- **Publish negative and inconclusive results:** a clean negative result, or a model whose loss improves while it fails a generation rubric, is as useful as a win. Keep failed checks and limitations next to the metrics.
