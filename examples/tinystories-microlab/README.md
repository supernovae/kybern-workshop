# TinyStories microlab: is the LM head a gradient bottleneck?

[Workshop](../../README.md) · [Full experiment](../../experiments/tinystories/lm-head-bottleneck/README.md)

The [LM-head experiment](../../experiments/tinystories/lm-head-bottleneck/README.md)
at laptop size. A 1.5M-parameter model trains on 20,000 TinyStories stories on
CPU, and a sweep asks whether narrowing its output head to rank 8 to 128 makes
it worse, and how much of the logit gradient each head passes back to the
network. It teaches the whole Lab loop (snapshot, tokenizer, `try`, `sweep`,
`report`) on a question a published paper ([arXiv 2603.10145](https://arxiv.org/abs/2603.10145))
says matters.

## The model

| | |
| --- | --- |
| Data | 20,000 training and 500 validation stories from `roneneldan/TinyStories` (pinned), exact duplicates removed |
| Tokenizer | 4,096-token byte-level BPE fitted on the training stories |
| Model | 2 layers, width 128, 4 heads, SwiGLU 352, 128-token context, untied embeddings: 1.5M parameters, V/D = 32 |
| Training | 1,500 updates of 2,048 tokens (3.1M tokens), AdamW peak 2e-3 |
| Scored | held-out loss, bits per byte on 200 whole stories, and the gradient bottleneck |

## 1. Workspace

```sh
RECIPE="$PWD/examples/tinystories-microlab"   # in your kybern-workshop checkout
WORK="$HOME/klab-experiments/tinystories-microlab"
mkdir -p "$WORK" && cp -R "$RECIPE"/declarations "$RECIPE"/*.yaml "$WORK"/ && cd "$WORK"
export KLAB_WORK_DIR="$WORK/klab-state"
```

## 2. Data and tokenizer (about 15 seconds after the first download)

```sh
klab data lock declarations/source.yaml --output source.lock.json
klab data snapshot source.lock.json --output snapshot
klab tokenizer train declarations/tokenizer.yaml
```

The first snapshot downloads one Parquet shard of about 250 MB into the
Hugging Face cache.

## 3. One change: a rank-32 head

```sh
klab try rank-32.yaml --vs declarations/run.yaml --config policy.yaml --backend cpu
klab report TRY_ID
```

[`rank-32.yaml`](rank-32.yaml) sets `model.output_head_rank: 32`: the head
becomes two matrices, hidden → 32 → vocabulary, so the logits can have rank at
most 32. `try` trains both models (about 4 minutes each on a 48-thread CPU),
scores them on the same held-out stories and seals one record. Read it with
`klab report TRY_ID --json`: `arms.*.heldout.gradient_bottleneck` holds the
gradient measurement.

What we saw once, as a check that the recipe runs (seed 1, not a result):

| Head | Held-out loss | Bits per byte | Gradient norm lost in the head | Cosine kept |
| --- | --- | --- | --- | --- |
| Full (rank 128) | 2.615 | 0.941 | 97.7% | 0.21 |
| Rank 32 | 3.115 | 1.121 | 99.6% | 0.09 |

The paper reports 95 to 99% lost and cosines of 0.1 to 0.3 in models a thousand
times larger. One seed is a direction, not a finding.

## 4. Does it hold? Three seeds, five ranks

```sh
klab sweep rank-sweep.yaml --backend cpu    # about 75 minutes on 48 threads
klab report SWEEP_ID
```

The sweep trains the baseline once per seed and every rank against it at the
same seed. `report` shows the mean change in held-out loss with its standard
error, and a verdict: `HIGHER_LOSS` needs the mean more than two standard
errors above zero over the three seeds. Each point also has
`kernel_norm_fraction_mean`, the average share of the gradient norm lost. The
sealed record and a `series.csv` for plotting are in
`$KLAB_WORK_DIR/lab/sweeps/SWEEP_ID`.

Compare what you get with the [preregistered predictions](../../experiments/tinystories/lm-head-bottleneck/README.md#predictions).
At this size the whole vocabulary is only 4,096 tokens, so V/D is half the
full experiment's; that is a reason the effects may differ, and worth saying
when you report them.

## 5. Look inside

```sh
klab explore TRY_ID
klab generate RUN_ID --runs-dir "$KLAB_WORK_DIR/lab/runs" --checkpoint latest.json \
  --prompt "Once upon a time" --max-new-tokens 120 --seed 1
klab dashboard --lab-dir "$KLAB_WORK_DIR/lab"
```

## Keeping your result repeatable

Record next to anything you publish: the Lab commit (`klab --version`), the
backend, the seeds, and the `TRY_ID` or `SWEEP_ID`; the sealed records hold
the data, tokenizer and configuration digests. Do not edit probe items or
thresholds to make an idea pass.
