# Contributing to Kybern Workshop

We welcome pull requests from anyone running small language-model experiments with [Tiny Sparse Lab](https://github.com/supernovae/tiny-sparse-lab)—whether you are replicating an existing recipe on your own hardware, testing an improvement to one of our baselines, or sharing a new experiment from your fork.

## Ways to Contribute

1. **Link your fork or experiment in the README**  
   Running an experiment in your own repository or fork? Open a PR to add it to the **Community Experiments & Forks** section of the [main README](README.md#community-experiments--forks). Include your repository link, the question you are testing, model size/backend, and a brief summary of what you found.
2. **Replicate or improve an active recipe**  
   Run the [Basic CPU smoke test](examples/synthetic-cpu/README.md), compare architectures in the [TinyStories microlab](examples/tinystories-microlab/README.md), or try to beat our [8,192-update TinyStories baseline](examples/tinystories-useful/README.md) (where validation loss dropped to `1.704`, but free generation still loops and drifts).
3. **Share a new declarative recipe**  
   Add a self-contained experiment recipe under `examples/` or `experiments/` using native Tiny Sparse Lab YAML/JSON declarations.

## How Workshop and Tiny Sparse Lab Fit Together

- **Workshop owns recipes and evidence:** declarative configs (`RunConfig`, tokenizer configs, dataset locks, `try` deltas, and campaign definitions), walkthrough documentation, and compact result records.
- **Tiny Sparse Lab owns the engine:** data preparation, training, behavioral probes, checkpoint verification, reporting, and the web dashboard live in [supernovae/tiny-sparse-lab](https://github.com/supernovae/tiny-sparse-lab).
- **Keep recipes declarative:** avoid adding custom Python training loops or per-recipe runner frameworks to Workshop. If an experiment needs a new model mechanism or CLI feature, contribute that capability upstream to Tiny Sparse Lab first.

## Guidelines for Reproducible Submissions

We follow the evidence practices described in the [Kybern Community Lab](https://kybern.dev/research/community-lab/) and [Experiment Methods](https://kybern.dev/experiments/methods/):

- **Pin your environment:** record the `tiny-sparse-lab` commit SHA, Python and PyTorch/MLX versions, hardware backend (`cpu`, `cuda`, `rocm`, `xpu`, `mps`, or `metal`), and dataset revision.
- **Use fresh run identities:** every reproduction or follow-up experiment generates new run and checkpoint IDs. Link to the baseline you are comparing against rather than overwriting historical result records.
- **Keep large binaries out of Git:** never commit raw dataset downloads, packed token arrays, or model weight files (`.pt`, `.safetensors`, etc.). Commit the declarative configs, SHA-256 manifests, loss curves, and representative generation JSONs so others can inspect your results and replicate the run locally.
- **Publish negative and inconclusive results:** a clean negative result—or a model that lowers loss while failing a generation rubric—is just as valuable as a win. Keep failed checks and limitations visible alongside the metrics.
