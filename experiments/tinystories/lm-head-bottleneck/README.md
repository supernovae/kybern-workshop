# Is the LM head a gradient bottleneck on TinyStories?

[TinyStories base model](../README.md) · [Paper](https://arxiv.org/abs/2603.10145)

Godey and Artzi, *Lost in Backpropagation: The LM Head is a Gradient
Bottleneck* (COLM 2026), argue that the output head limits more than what a
model can express. The gradient for the logits has one entry per vocabulary
token (V of them), but the rest of the network only receives the part of it
that lies in the head's column space, at most D directions. They report:

1. **Gradient compression.** In GPT-2, Pythia, Llama 3, OLMo 2 and Qwen3, 95 to
   99% of the logit gradient's norm is lost in the head, and the cosine between
   the full gradient and what is kept is 0.1 to 0.3. Less is lost as D/V grows.
2. **Head rank slows training.** With a 2B-parameter backbone on FineWeb-Edu,
   heads of rank D = 32 to 4096 (W = A·B) give consistent validation-loss gaps;
   D = 4096 reaches D = 32's final loss in about 1/16 of the tokens.
3. **Trivial patterns become unlearnable.** On SpamLang (each sequence repeats
   one symbol), a 106M model with D = 576 learns easily at small V but becomes
   learning-rate sensitive as V grows, and at V = 131,072 no tested learning
   rate converges.

This experiment asks whether the same effects appear in a model three orders of
magnitude smaller, trained on simple stories, where they are cheap to measure
with paired seeds. **It is preregistered: the predictions below were written
before any experiment run, and the results section is filled in afterwards
without editing them.**

## Setup

Every arm starts from the [base recipe](../README.md): width 512, 8 layers,
untied embeddings, a 32,768-token tokenizer (V/D = 64, the ratio of GPT-2
small), trained from scratch on the cleaned TinyStories training split. Only
the setting under test changes. Scores are on the held-out validation split
the base recipe uses: loss per token where the tokenizer is fixed, bits per
byte where it changes. The Lab capabilities used:

| Need | Lab setting |
| --- | --- |
| Head of rank D | `model.output_head_rank` ([architecture](https://github.com/supernovae/model-lab/blob/main/docs/architecture.md#output-head-rank)) |
| Gradient compression | `evaluation.gradient_bottleneck` ([evaluation](https://github.com/supernovae/model-lab/blob/main/docs/evaluation.md#gradient-bottleneck)) |
| Scores across tokenizers | `evaluation.text_documents`, bits per byte ([evaluation](https://github.com/supernovae/model-lab/blob/main/docs/evaluation.md#bits-per-byte)) |
| SpamLang | `dataset.synthetic_task: repeat_token` ([datasets](https://github.com/supernovae/model-lab/blob/main/docs/datasets.md#repeated-symbols)) |
| Paired seeds | `klab sweep` with `seeds: [1, 2, 3]` |

## Predictions

Written before any run. A prediction is supported when a sweep's verdict is
`LOWER_LOSS` or `HIGHER_LOSS` in the predicted direction (mean more than two
standard errors from zero over three seeds), contradicted when it is in the
other direction, and inconclusive on `WITHIN_SEED_NOISE`.

| # | Paper's claim | Prediction here | Test |
| --- | --- | --- | --- |
| P1 | 95–99% of the gradient norm is lost | The base model loses 90–99% (`kernel_norm_fraction` 0.90–0.99) on held-out stories. A random gradient would lose 99.2% at D/V = 1/64, so a trained head keeps several times its share | `klab eval` with `gradient_bottleneck` on the base model |
| P2 | Less is lost as D grows | `kernel_norm_fraction` falls monotonically from D = 16 to D = 512 | Rank sweep, every arm measured |
| P3 | A lower-rank head trains worse | Every D below 512 has higher held-out loss than the full head, and the gap grows as D shrinks | Rank sweep, loss per token |
| P4 | The gap is an optimization effect, not a limit on what can be expressed | D = 512 factored as A·B scores within noise of the unfactored head | Rank sweep, point D = 512 |
| P5 | SpamLang becomes hard as V grows | At D = 512, final SpamLang loss rises with V across the 4k, 8k, 16k and 32k tokenizers, and the range of learning rates that converge narrows | SpamLang sweep |
| P6 | Less is lost as D/V grows | At fixed D = 512, `kernel_norm_fraction` rises with V across the 4k to 32k tokenizers | Vocabulary sweep, every arm measured |

We also record one competing expectation. TinyStories uses a small working
vocabulary: most of a 32,768-token vocabulary is rare in it, so the errors the
model makes may occupy far fewer than V directions. If so, heads well below
D = 512 could lose little (P3 contradicted above some D), even while P1 holds.
That would mean the bottleneck depends on how much of the vocabulary the data
actually uses, which the paper's web-scale data cannot show.

## Arms

Every arm is [`arm.yaml`](arm.yaml): the base model trained from scratch for
one pass over the training tokens (2,961 updates, 388.1M tokens), scored on held-out loss, bits per byte over 2,000 whole stories and the
gradient bottleneck. (The runs below used one card each; see
[How it was run](#how-it-was-run).) One pass keeps 50 runs affordable; the base model's four
passes are the reference for how far training continues.

| Sweep | File | Points × seeds | Estimated time on two B70s |
| --- | --- | --- | --- |
| Head rank (P2–P4) | [`rank-sweep.yaml`](rank-sweep.yaml) | D = 16, 32, 64, 128, 256, 512 against the full head × 3 | 21 runs, about 9 hours |
| Vocabulary (P6) | [`vocab-sweep.yaml`](vocab-sweep.yaml) | 4,096, 8,192, 16,384 against 32,768 × 3 | 12 runs, about 5 hours |
| SpamLang (P5) | [`spamlang-sweep.yaml`](spamlang-sweep.yaml) | 4 vocabularies × 4 peak learning rates × 1 | 16 runs, about 1 hour |

Times are estimates from 278,600 tokens a second, measured on two cards for a
300-update rank-64 arm; record the real ones. Each run holds its own copy of
the prepared data (1.6 GB for the 32k tokenizer) and keeps two checkpoints, so
the three sweeps need about 130 GB of disk. P1 needs no new training: it is
measured on the base model.

## Run it

From the workspace of the [base recipe](../README.md), after its data and
tokenizer steps (`cd "$WORK"`):

```sh
# The three smaller tokenizers, for the vocabulary and SpamLang sweeps.
for k in 4k 8k 16k; do klab tokenizer train lm-head-bottleneck/tokenizer-$k.yaml; done

cd lm-head-bottleneck
klab sweep rank-sweep.yaml --runtime b70-xpu
klab sweep vocab-sweep.yaml --runtime b70-xpu
klab sweep spamlang-sweep.yaml --runtime b70-xpu
klab report SWEEP_ID            # once per sweep
```

P1, on the trained base model and on each kept checkpoint along its training:

```sh
klab eval tinystories-base --runs-dir ../runs --runtime b70-xpu
klab eval tinystories-base --runs-dir ../runs --runtime b70-xpu --checkpoint CHECKPOINT   # each in runs/tinystories-base/checkpoints
```

The tokenizers have measured SpamLang symbol counts (whole-word tokens that
encode back to themselves) of 2,800, 5,937, 11,785 and 22,245 for V = 4,096,
8,192, 16,384 and 32,768: 68 to 72% of V. The prepared data records them as
`repeat_token_symbols`.

SpamLang data is synthetic, but its tokenizers were fitted on the TinyStories
snapshot, so [`spamlang.yaml`](spamlang.yaml) and each SpamLang sweep point name
their tokenizer's `origin`: its digests and the snapshot it was fitted on. Lab
checks both before preparing the data. Fitting the tokenizers from the pinned
snapshot reproduces those digests byte for byte (checked by refitting the 4k
tokenizer), so the declarations work in any workspace built from this recipe.
This needs Lab with [model-lab#438](https://github.com/supernovae/model-lab/pull/438) and, for the vocabulary and SpamLang sweeps,
[model-lab#439](https://github.com/supernovae/model-lab/pull/439).

## What to record

For each sweep, the sealed sweep record and `series.csv` (in
`$KLAB_WORK_DIR/lab/sweeps/SWEEP_ID`), copied next to this README with the Lab
commit and the Workshop commit. For every prediction, the verdict (supported,
contradicted or inconclusive) with the numbers behind it. Keep runs that
failed or did not converge; a SpamLang arm that does not learn is a result.

## Results

Run 2026-11-13 to 2026-11-14 on four Intel Arc Pro B70s. The `series.csv` of each of
the seven sweeps is in [`results/`](results/), with the pooled tables
[`pooled-rank.csv`](results/pooled-rank.csv) and
[`pooled-vocab.csv`](results/pooled-vocab.csv). The sweep records themselves
(they hold local paths) and every try stay in the run store; the IDs below name them.
Predictions above are unedited. Δ is candidate minus baseline at the same seed,
in held-out loss (nats per token) for the rank sweep and in bits per byte for
the vocabulary sweep; positive means the candidate is worse. "×SE" is the mean
over three seeds divided by its standard error.

### Verdicts

| # | Verdict | Evidence |
| --- | --- | --- |
| P1 | **Supported** | The base model loses 97.8% of the gradient norm in the head, inside 90–99% ([base results](../README.md)). It keeps 4.4% of the squared norm against 1.6% for a random 512-dimensional subspace (2.8×). Each of the six baseline arms of the sweeps measured 98.1%. Not measured along the base model's training checkpoints. |
| P2 | **Supported** | `kernel_norm_fraction` falls monotonically as D grows, 0.9993 → 0.9882, with a standard error under 0.0001 at every point. |
| P3 | **Supported** | Every D below 512 has higher held-out loss than the full head, 6 to 23 standard errors from zero, and the gap grows as D shrinks (table below). The competing expectation (little loss above some D because TinyStories uses a small working vocabulary) is **not** what happened: even D = 256 costs 0.089 nats. |
| P4 | **Contradicted** | D = 512 factored as A·B is **0.043 ± 0.003** nats worse than the unfactored head (13.5 SE). The prediction was "within noise". The gap is far above the seed-to-seed baseline scatter (below). The paper's reading that the gap is an optimization effect is not ruled out: a factored head at full rank has the same expressivity as the plain head, so this gap is a training effect of the factorization. Why it costs loss here (initialization, learning rate for the two factors) was not tested. |
| P5 | **Supported on loss; inconclusive on the learning-rate range** | One seed per arm by design, so no standard errors and every try is `NOT_COMPARABLE` (the tokenizers differ). Final loss rises with V at every learning rate, by two orders of magnitude (below). The rule "range of converging rates narrows" needs a threshold the preregistration did not set; with loss under 0.1 as a post-hoc threshold, 4k converges at 4 of 4 rates, 8k at 3 of 4, 16k and 32k at none. The best rate was the highest tried (2e-3) at every V of 8k and above, so the grid does not bracket the optimum for the larger vocabularies, and the paper's "no rate converges" at V = 131,072 was not tested. |
| P6 | **Supported** | At D = 512 the kernel fraction rises with V: 0.9382 (4k), 0.9676 (8k), 0.9796 (16k), 0.9812 (32k). |

### Head rank (P2–P4), three seeds

Baseline (full head): loss 1.4548 mean over seeds, kernel fraction 0.9812,
kept cosine 0.19. "Random" is the kernel fraction of a random D-dimensional
subspace, √(1 − D/V).

| D | Δ loss | ± SE | ×SE | Mean loss | Kernel fraction | Random | Kept cosine |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | +0.842 | 0.132 | 6.4 | 2.2965 | 0.9993 | 0.9998 | 0.037 |
| 32 | +0.351 | 0.051 | 6.9 | 1.8061 | 0.9985 | 0.9995 | 0.054 |
| 64 | +0.229 | 0.010 | 23.3 | 1.6838 | 0.9968 | 0.9990 | 0.080 |
| 128 | +0.137 | 0.009 | 15.8 | 1.5918 | 0.9943 | 0.9980 | 0.107 |
| 256 | +0.089 | 0.008 | 11.0 | 1.5441 | 0.9914 | 0.9961 | 0.131 |
| 512 | +0.043 | 0.003 | 13.5 | 1.4982 | 0.9882 | 0.9922 | 0.153 |

The same baseline seed trained twice (once for the rank sweep, once for the
vocabulary sweep) differed by 0.0003, 0.0025 and 0.0061 nats, so repeat-run
scatter on this hardware is up to about 0.006. Only the D = 512 row is within a
factor of ten of that scatter, and it clears it by about seven times.

### Vocabulary at D = 512 (P6), three seeds

| V | Δ bits per byte | ± SE | ×SE | Kernel fraction | Random | Kept cosine |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4,096 | +0.0075 | 0.0011 | 7.0 | 0.9382 | 0.9354 | 0.346 |
| 8,192 | +0.0009 | 0.0011 | 0.8 | 0.9676 | 0.9682 | 0.252 |
| 16,384 | −0.0012 | 0.0010 | −1.2 | 0.9796 | 0.9843 | 0.201 |
| 32,768 (baseline) | 0 | – | – | 0.9812 | 0.9922 | 0.193 |

Only the 4k tokenizer costs bits per byte; 8k and 16k are within noise of 32k.
The fraction lost tracks the random-subspace value at 4k and 8k and falls below
it at 16k and 32k, so a trained head keeps more than its geometric share only
where V/D is large.

### SpamLang (P5), one seed

Final held-out loss per token of each arm. The 32,768 column's 5e-4 cell is the
baseline arm.

| Peak learning rate | V = 4,096 | 8,192 | 16,384 | 32,768 |
| ---: | ---: | ---: | ---: | ---: |
| 2.5e-4 | 0.0467 | 0.2999 | 2.5133 | 5.8734 |
| 5e-4 | 0.0331 | 0.0758 | 1.2065 | 4.6532 |
| 1e-3 | 0.0309 | 0.0408 | 0.6077 | 3.9766 |
| 2e-3 | 0.0309 | 0.0352 | 0.4167 | 3.9479 |

### How it was run

- **Hardware and software.** Four B70s, one arm per card (`ZE_AFFINITY_MASK`
  with `device_index: 0`). Lab `main` at `827a4ef8` for the rank sweeps. The
  vocabulary and SpamLang sweeps ran from
  [model-lab#439](https://github.com/supernovae/model-lab/pull/439)
  (`82c015e5`), which lets a sweep vary `tokenizer.path`; they crashed before
  their first try on `main`. The try records carry the source digest. Workshop
  at `d7721b3`.
- **One card per arm.** [`arm.yaml`](arm.yaml) and [`spamlang.yaml`](spamlang.yaml)
  no longer declare `secondary_device_indices: [1]`, which the first launch
  used. Batch, accumulation, seed and data are unchanged, and the earlier
  two-card measurements matched one card's losses. The edit makes a new baseline,
  so none from the first launch was reused.
- **One sweep per seed.** To use the cards in parallel, each seed ran as its own
  sweep (a copy of the sweep file with `seeds: [N]`), so no single sweep record
  pools three seeds and `klab report` shows n = 1. I pooled
  the three seeds of each point with a short local script (Lab has no command for
  pooling separate sweeps; [model-lab#441](https://github.com/supernovae/model-lab/issues/441)) and
  applied the preregistered rule by hand.
  Rank sweeps: `sweep-20261113T230505Z-` `8c046567` (seed 1), `a2a5f28f` (2),
  `be6c7739` (3). Vocabulary: `sweep-20261114T041310Z-` `94a2f210` (1),
  `fcc4e248` (2), `c5daea0a` (3). SpamLang: `sweep-20261113T230505Z-b5757929`.
- **Cost.** A rank arm took 35 to 72 minutes on one B70 (the low-rank arms are
  slower); a SpamLang arm 4 to 9 minutes. Host RAM stayed between 62 and 85 GiB
  free with four jobs running and showed no growth; scratch used the NVMe and
  `/tmp` never passed 122 MB. All sweeps and tries used 100 GB of disk.
- **Kept, not counted.** A first launch on two cards was cut short at update
  539 of 2,961 when a GPU hung (kernel Xe GuC timeout, device wedged) and took
  the desktop down; its completed baseline was not reused. A second launch
  failed twelve tries at once because `arm.yaml` still named a second card; I
  stopped it, and those twelve `failed` try records and four `interrupted`
  sweeps stay in the lab store. A third failed all three vocabulary sweeps on
  the path bug above. Sweeps that crash leave their record at `started`
  ([model-lab#442](https://github.com/supernovae/model-lab/issues/442)), so
  several such records remain.

### What this does and does not say

At 42M parameters on TinyStories the head-rank and vocabulary effects point the
way the paper reports, and the gap from a low-rank head is large and graded in
D. It is a one-pass (388M token) comparison with one architecture: it cannot say
what happens with longer training, and P4's contradiction says the factorization
itself costs loss at this budget. The SpamLang grid is one seed with its optimum
at the grid's edge. Nothing here tests the paper's 2B-parameter result.
