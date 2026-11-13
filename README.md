<p align="center">
  <img src="docs/assets/workshop-banner.svg" alt="Kybern Workshop — Small models. Shareable experiments." width="100%">
</p>

<p align="center">
  <a href="https://github.com/supernovae/kybern-workshop/actions/workflows/declarations.yml"><img src="https://github.com/supernovae/kybern-workshop/actions/workflows/declarations.yml/badge.svg" alt="Declarations CI"></a>
  <a href="https://github.com/supernovae/model-lab"><img src="https://img.shields.io/badge/Workbench-Kybern%20Model%20Lab-7ceac4" alt="Kybern Model Lab"></a>
  <a href="https://github.com/supernovae/model-lab"><img src="https://img.shields.io/badge/Python-3.14-3776AB?logo=python&amp;logoColor=white" alt="Python 3.14"></a>
  <a href="docs/native-workflow.md"><img src="https://img.shields.io/badge/Recipes-YAML%20%26%20JSON-a7a2ff" alt="Declarative Recipes"></a>
  <a href="https://kybern.dev"><img src="https://img.shields.io/badge/Learn-kybern.dev-0d1726?labelColor=17243a&amp;color=7ceac4" alt="kybern.dev"></a>
</p>

<p align="center">
  <a href="experiments/tinystories/README.md">TinyStories Base</a> ·
  <a href="experiments/tinystories/lm-head-bottleneck/README.md">LM-Head Experiment</a> ·
  <a href="examples/synthetic-cpu/README.md">Basic CPU Smoke</a> ·
  <a href="components/README.md">Custom Components</a> ·
  <a href="experiments/devmind/README.md">Devmind</a> ·
  <a href="#community-experiments--forks">Community Experiments</a> ·
  <a href="https://kybern.dev/experiments/">Kybern Research</a>
</p>

**Kybern Workshop** holds the experiment recipes we run with **[Kybern Model Lab](https://github.com/supernovae/model-lab)**: dataset locks, tokenizer configs, model `RunConfig` files, `try` changes, and the recorded outputs of each run. Use them to see exactly what we ran, repeat a run on your own hardware, or copy a recipe and test your own idea.

We publish everything we record, including negative and inconclusive results: an experiment's predictions are written before it runs, and its results are filled in afterwards whichever way they go. Small models are easier to understand when you can see where they go wrong.

A few things to know before you start:

- You only need this repository and Lab to run the recipes.
- We don't publish model weights. A reproduction trains its own model and gets its own run IDs.

---

## Active Experiments & Recipes

| Experiment | What it tests | Status & Evidence | Links |
| --- | --- | --- | --- |
| **TinyStories Base (58.9M)** | A from-scratch story model shaped like llama2.c's 42M (width 512, 8 layers, 32,768-token tokenizer, V/D = 64), trained for four passes over every unique TinyStories story on two Arc Pro B70s. | **Trained.** Held-out loss 1.329, 0.438 bits per byte, in 93 minutes on two B70s (one run, Lab `827a4ef8`). The README records the data cleaning, tokenizer, learning-rate sweep, loss curve and a sample story. | [Recipe](experiments/tinystories/README.md) · [Results](experiments/tinystories/README.md#6-check-the-model) |
| **Is the LM Head a Gradient Bottleneck?** | A preregistered test of [arXiv 2603.10145](https://arxiv.org/abs/2603.10145) on the TinyStories base: head rank, vocabulary size and SpamLang sweeps over three seeds, with the share of the logit gradient lost in the head measured on every arm. | **Running.** Prediction P1 is measured on the base model: 97.8% of the gradient norm is lost in the head, inside the paper's 95–99%. The rank, vocabulary and SpamLang sweeps started 2026-11-13. | [Experiment](experiments/tinystories/lm-head-bottleneck/README.md) |
| **TinyStories Microlab** | The same experiment on CPU: a 1.5M-parameter model on 20,000 stories, heads of rank 8 to 128 against the full head, three seeds. | **Ready to run.** One recipe check recorded (seed 1); no sweep result yet. | [Microlab Guide](examples/tinystories-microlab/README.md) |
| **Basic Synthetic CPU** | An offline end-to-end check: synthetic text, BPE tokenizer, one training step, evaluation and a run report. | **Ready to run.** Offline on CPU, no downloads. | [Recipe Guide](examples/synthetic-cpu/README.md) · [Offline Check (kybern.dev)](https://kybern.dev/models/cpu-smoke/) |
| **Devmind (730M)** | A from-scratch, development-leaning decoder with dense attention, pretrained at 4,096 tokens and extended to 32,768, with n-gram memory from the first update: pinned sources, a 12B-token mixture, pretraining, long-context, chat and preference stages. | **Defined, not trained.** Declarations load with Lab; the model shape was measured for a few updates on one Arc Pro B70. The README lists the measured numbers and the open Lab gaps. | [Recipe](experiments/devmind/README.md) · [Corpus](experiments/devmind/corpus/README.md) · [Post-training](experiments/devmind/post-training/README.md) |

---

## Running Workshop Experiments with Kybern Model Lab

Every recipe here runs with **[Kybern Model Lab](https://github.com/supernovae/model-lab)**.
Install **Python 3.14** and [uv](https://docs.astral.sh/uv/), then clone both repositories side by side:

```sh
git clone https://github.com/supernovae/model-lab.git
git clone https://github.com/supernovae/kybern-workshop.git

cd model-lab
uv sync --locked --extra cpu --dev
export KLAB_WORK_DIR="$HOME/.local/share/klab"
```

### 1. Run a Quick Offline CPU Smoke Test

Check that your install works end to end. This downloads nothing (more in the [offline installation check on kybern.dev](https://kybern.dev/models/cpu-smoke/)):

```sh
uv run --locked --extra cpu klab readiness smoke --family dense \
  --output "$KLAB_WORK_DIR/first-run"
uv run --locked --extra cpu klab dashboard --runs-dir "$KLAB_WORK_DIR/first-run/runs"
```

To run the same stages from declarations, follow [`examples/synthetic-cpu/README.md`](examples/synthetic-cpu/README.md).

### 2. Run Your First Controlled Comparison (`TinyStories Microlab`)

The [TinyStories microlab](examples/tinystories-microlab/README.md) prepares
20,000 stories and a 4,096-token tokenizer, then tests on CPU whether a rank-32
output head trains a worse model than the full head, and how much of the logit
gradient each passes back:

```sh
# From the model-lab checkout:
KLAB="uv run --project $PWD --locked --extra cpu klab"
WORK="$KLAB_WORK_DIR/experiments/tinystories-microlab"
mkdir -p "$WORK"
cp -R ../kybern-workshop/examples/tinystories-microlab/{declarations,policy.yaml,rank-32.yaml,rank-sweep.yaml} "$WORK"/
cd "$WORK"
$KLAB data lock declarations/source.yaml --output source.lock.json
$KLAB data snapshot source.lock.json --output snapshot
$KLAB tokenizer train declarations/tokenizer.yaml
$KLAB try rank-32.yaml --vs declarations/run.yaml --config policy.yaml --backend cpu
```

When `try` finishes, it prints a `TRY_ID`. Use it to read the verdict, dig into the runs, or open the dashboard:

```sh
$KLAB report TRY_ID
$KLAB explore TRY_ID
$KLAB dashboard
```

### 3. Train the TinyStories Base Model on a GPU

The [base recipe](experiments/tinystories/README.md) walks through every step on a
registered accelerator runtime: pinning and cleaning the data, fitting the
32,768-token tokenizer, the learning-rate sweep and the four-pass training run.
It needs about 24 GB of disk and took 93 minutes on two Intel Arc Pro B70s; on
other hardware, register your own runtime with Lab's
[runtime guide](https://github.com/supernovae/model-lab/blob/main/docs/runtime.md).
The [LM-head experiment](experiments/tinystories/lm-head-bottleneck/README.md)
then runs three sweeps from the same workspace.

### The Everyday Experiment Loop

| Goal | Kybern Model Lab Command | What it does |
| --- | --- | --- |
| **Validate a config** | `klab config validate run.yaml --kind run` | Checks YAML or JSON configs before you spend time on data or training. |
| **Test one change** | `klab try DELTA.yaml --vs BASELINE.yaml` | Trains the baseline and the candidate (or reuses a baseline it already checked), scores held-out loss, and runs quick probes. |
| **Confirm across seeds** | `klab sweep SWEEP.yaml` | Trains the baseline once per seed, compares every value of a setting at each seed, and reports the mean change with its standard error. |
| **Read the verdict** | `klab report TRY_ID` | Prints the comparison report, the change in metrics, and a probe summary. |
| **Inspect weights & loss** | `klab explore TRY_ID` | Computes per-token loss, attention maps, and weight statistics. |
| **Generate text** | `klab generate RUN_ID --checkpoint CHECKPOINT --prompt "..."` | Writes greedy or sampled continuations from a checkpoint. |
| **Browse visually** | `klab dashboard` | Opens a local web UI for runs, Pareto frontiers, probes, and checkpoints. |

---

## Community Experiments & Forks

This is where we list experiments people run in their own forks and repositories: replications, new baselines, and changes to our recipes.

| Project / Fork | Author | Question / Experiment | Model & Backend | Summary / Findings |
| --- | --- | --- | --- | --- |
| *Nothing listed yet.* | — | Repeat a recipe, test an architecture change, or run the [LM-head experiment](experiments/tinystories/lm-head-bottleneck/README.md) on your hardware. | CPU / GPU / MLX | [Open a PR](CONTRIBUTING.md) to add yours. |

If you've run something with these recipes, we'd like to hear about it. That could be a recipe repeated on different hardware (CUDA, ROCm, Intel XPU, or Apple Silicon with MLX), a replication of the LM-head experiment, or a clean negative result. Open a pull request that adds a row to the table. [CONTRIBUTING.md](CONTRIBUTING.md) explains what to include.

---

## Learn & Explore on [kybern.dev](https://kybern.dev)

The website walks through these recipes in more detail:

- **[Offline CPU Installation Check](https://kybern.dev/models/cpu-smoke/)** — A quick way to check a new Kybern Model Lab install.
- **[Experiments & Research Roadmap](https://kybern.dev/experiments/)** — Planned studies on conditional memory, fact swaps, and context overrides, plus ideas you can test on your own hardware.
- **[Matched Comparisons](https://kybern.dev/learn/lab/matched-comparisons/) & [Inspecting Runs](https://kybern.dev/learn/lab/inspect-runs/)** — How to set up a fair comparison with paired seeds and read probe verdicts.
- **[Free 18-Lesson Curriculum](https://kybern.dev/learn/)** — Hands-on lessons, from tensors and autograd to building a causal decoder and running your own comparisons.

---

## Repository Structure

```text
kybern-workshop/
├── components/                # Python package for custom model parts (the only Python here)
├── examples/
│   ├── custom-attention/      # Train with an attention kind from components/
│   ├── synthetic-cpu/         # Offline synthetic CPU smoke recipe
│   └── tinystories-microlab/  # The LM-head experiment on CPU: try, then a rank sweep
├── experiments/
│   ├── devmind/               # Devmind: model, corpus, training stages and post-training
│   └── tinystories/           # TinyStories base model, calibration and the LM-head experiment
└── docs/
    └── native-workflow.md     # Which klab command to use for each job
```

## Contributing

We welcome pull requests for replications, new recipes, improvements to a baseline, and links to your forks. Start with [CONTRIBUTING.md](CONTRIBUTING.md) and the [Kybern Community Lab guide](https://kybern.dev/research/community-lab/).

## License

Workshop's recipes, configs, and documentation are [MIT licensed](LICENSE). Datasets, upstream model sources and any recorded third-party text keep their own licenses.
