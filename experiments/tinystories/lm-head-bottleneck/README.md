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
one pass over the training tokens (2,961 updates, 388.1M tokens), on both
cards, scored on held-out loss, bits per byte over 2,000 whole stories and the
gradient bottleneck. One pass keeps 50 runs affordable; the base model's four
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
This needs Lab with [model-lab#438](https://github.com/supernovae/model-lab/pull/438).

## What to record

For each sweep, the sealed sweep record and `series.csv` (in
`$KLAB_WORK_DIR/lab/sweeps/SWEEP_ID`), copied next to this README with the Lab
commit and the Workshop commit. For every prediction, the verdict (supported,
contradicted or inconclusive) with the numbers behind it. Keep runs that
failed or did not converge; a SpamLang arm that does not learn is a result.

## Results

Not run yet.
