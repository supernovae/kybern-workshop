# TinyStories base model

[Workshop](../../README.md) · [LM-head experiment](lm-head-bottleneck/README.md) · [CPU microlab](../../examples/tinystories-microlab/README.md)

A 58.9M-parameter story model trained from scratch with
[Kybern Model Lab](https://github.com/supernovae/model-lab) on every unique
TinyStories story, in about two hours on two Intel Arc Pro B70s. It is the
starting point for experiments that need a model people actually build at this
size, beginning with a test of whether the LM head is a gradient bottleneck.

Every step below is a Lab command, and every number in this page was measured
unless it says otherwise. Anyone can repeat it and get the same data,
tokenizer and configuration digests.

## Why this shape

The most carefully tuned public TinyStories models are Andrej Karpathy's
llama2.c models. We match their shape rather than invent one, and we do not
use their weights: this model is trained from scratch.

| Model | Width D | Layers | Vocabulary V | V/D | Context | Parameters |
| --- | --- | --- | --- | --- | --- | --- |
| llama2.c 15M | 288 | 6 | 32,000 | 111 | 256 | 15M |
| llama2.c 42M | 512 | 8 | 32,000 | 62 | 1,024 | 42M |
| llama2.c 110M | 768 | 12 | 32,000 | 42 | 1,024 | 110M |
| `roneneldan/TinyStories-33M` | 768 | 4 | 50,257 | 65 | 2,048 | named 33M |
| **This model** | **512** | **8** | **32,768** | **64** | **512** | **58.9M** |

The vocabulary matters for the experiments built on this model: the ratio of
vocabulary to width (V/D) decides how much of the output layer's gradient can
reach the rest of the network. Public models sit between 30 and 110 (GPT-2
small 65, Llama 3 8B 31). A small 4,096-token tokenizer would put V/D near 8,
a setting nobody trains for real. Our earlier recipes did exactly that.

Differences from llama2.c 42M, each on purpose:

- **Untied embeddings** (16.8M extra parameters), so the model is the control
  arm of the [LM-head experiment](lm-head-bottleneck/README.md), whose
  rank-limited heads need them.
- **Our own tokenizer**, fitted on the training stories, not Llama 2's.
- **512-token context:** held-out stories average 211 tokens and 97% fit in
  512; longer ones continue in the next row, as in llama2.c.
- **Clean data:** see below.

## What you need

- Lab installed as described in [native workflow](../../docs/native-workflow.md),
  and a registered runtime for your accelerator. The commands below use
  `b70-xpu`; on one card, drop `runtime.secondary_device_indices`.
- About 20 GB of free disk for the base model: 3.5 GB of snapshot, 1.6 GB of
  prepared tokens, the run's own 1.6 GB copy of them, and twelve kept
  checkpoints of 670 MB. The [LM-head experiment](lm-head-bottleneck/README.md)
  needs about 130 GB more. Put the workspace on a disk that has it.
- About two hours of two B70s, or two and a half on one (estimated from the
  speeds measured below).

## 1. Workspace

```sh
RECIPE="$PWD/experiments/tinystories"   # in your kybern-workshop checkout
WORK="$HOME/klab-experiments/tinystories"   # or any disk with room, see above
mkdir -p "$WORK" && cp -R "$RECIPE"/. "$WORK"/ && cd "$WORK"
export KLAB_WORK_DIR="$WORK/klab-state"
klab config validate tokenizer.yaml --kind tokenizer
klab inspect base.yaml
```

Paths in the declarations are relative to the files, so everything lands in
`$WORK`.

## 2. Data

```sh
klab data lock source.yaml --output source.lock.json
klab data snapshot source.lock.json --output snapshot
```

This takes about 5 minutes. [`source.yaml`](source.yaml) pins `roneneldan/TinyStories`
at revision `f54c09fd…` and keeps every story once. Measured on that revision:

| | Stories | |
| --- | --- | --- |
| Training split as published | 2,119,719 | |
| Exact duplicates within training | 320,241 | removed |
| Training stories that also appear in validation | 6,601 | removed |
| Empty | 230 | removed |
| **Training, kept** | **1,792,647** | 1.6 GB of text |
| **Validation** | **21,990** | 19.2 MB, all kept |

So 15% of the published training split is repeated stories, and 6,601
validation stories appear verbatim in training. Models trained on the
published split have seen part of its validation set; this one has not.

## 3. Tokenizer and prepared data

```sh
klab tokenizer train tokenizer.yaml     # about 3.5 minutes
klab data prepare base.yaml             # about 1.5 minutes
```

The tokenizer is byte-level BPE with 32,768 tokens, fitted on every kept
training story. Preparation measured 388,198,157 training tokens and 4,647,305
validation tokens, about 4.1 bytes of text per token.

## 4. Learning rate (optional: how we chose it)

The peak learning rate was chosen by a sweep, not copied. Each point trains
the model for 1,526 updates (200M tokens, about half a pass) with 150 warmup
updates and cosine decay to a tenth of the peak, on one card, one seed. To
repeat it (seven trainings of about 20 minutes, 2.4 hours on one B70):

```sh
klab sweep calibration/lr-sweep.yaml --runtime b70-xpu
klab report SWEEP_ID
```

What we measured (Lab `c74b88ad`, sweeps `sweep-20261113T164056Z-def99d23` and
`sweep-20261113T184534Z-9690f975`, which together are the points in
`lr-sweep.yaml`):

| Peak | Held-out loss | Bits per byte |
| --- | --- | --- |
| 3e-4 | 1.786 | 0.599 |
| 6e-4 | 1.646 | 0.550 |
| 1e-3 (baseline) | 1.586 | 0.528 |
| 2e-3 | 1.550 | 0.516 |
| **3e-3** | **1.546** | **0.514** |
| 4e-3 | 1.550 | 0.516 |
| 6e-3 | 1.758 | 0.588 |

Loss is flat from 2e-3 to 4e-3 and much worse at 6e-3. We use 3e-3, the middle
of the flat region and half the peak that fails. The differences inside the
flat region (0.005) are smaller than seed noise is likely to be; the choice
does not depend on them.

## 5. Train

```sh
klab train base.yaml --runtime b70-xpu --run-id tinystories-base --require-prepared
```

[`base.yaml`](base.yaml): 11,846 updates of 131,072 tokens (four passes over
the training tokens, 1.55B in all), AdamW peak 3e-3 (chosen above) with 300
warmup updates and cosine decay to a tenth, weight decay 0.1, gradient clipping
1.0, bf16 with compiled blocks and loss. Each update's eight microbatches are
split between cards 0 and 1, and the update is the same as on one card.

Measured at this shape: 195,000 tokens a second on one B70 with 4.6 GB of the
card in use, and 278,600 on two (an experiment arm, 300 updates, Lab
`246072ab`). Two cards are 1.43 times one, not twice: card 0 also drives the
desktop on our host and took 0.44 seconds per update against card 1's 0.32.
Close GPU-heavy applications during the run. With more cards, list them in
`runtime.secondary_device_indices` and keep `gradient_accumulation` a multiple
of the card count.

Watch it with `klab dashboard`. Every 500 updates Lab scores held-out loss on
64 batches; a checkpoint is kept every 1,000 updates.

## 6. Check the model

```sh
klab eval tinystories-base --runs-dir runs --runtime b70-xpu
klab probe tinystories-base --runs-dir runs --runtime b70-xpu --config standard
klab generate tinystories-base --runs-dir runs --runtime b70-xpu --checkpoint latest.json \
  --prompt "Once upon a time, there was a little girl named Lily." \
  --max-new-tokens 200 --seed 1
```

`eval` reports held-out loss, bits per byte on 2,000 whole validation stories
and how much of the logit gradient the head passes back. Record
them in the table below with the run ID, the Lab commit (`klab --version`),
and the data and tokenizer digests from the run manifest.

| Measure | Value |
| --- | --- |
| Held-out loss (nats per token) | not run yet |
| Bits per byte | not run yet |
| Gradient norm lost in the head | not run yet |
| Wall time, two B70s | not run yet |

Loss per token cannot be compared with llama2.c's published numbers (0.847 for
42M): their tokenizer and their copy of the data differ. Bits per byte on our
held-out stories is the number to compare across tokenizers.

## Experiments on this model

- [Is the LM head a gradient bottleneck?](lm-head-bottleneck/README.md):
  a preregistered test of arXiv 2603.10145 at this scale.
- [CPU microlab](../../examples/tinystories-microlab/README.md): the same
  experiment on CPU, about 75 minutes on 48 threads.

Earlier TinyStories recipes and results are in Git history at
[`884eae8`](https://github.com/supernovae/kybern-workshop/tree/884eae8).
