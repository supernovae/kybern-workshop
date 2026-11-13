# Devmind

Devmind is a 730M-parameter decoder trained from scratch with
[Kybern Model Lab](https://github.com/supernovae/model-lab), biased toward
software development: Python first, then JavaScript and TypeScript, GitHub
issues and pull requests, and reference documentation. It is meant to be a
complete demonstration of Lab, from pinned sources to a chat model, and a
baseline to change one thing at a time.

**Nothing has been trained from this recipe yet.** The declarations load with
Lab, the model shape has been measured on Arc Pro B70s for a handful of
updates, and the data has not been downloaded. The sections below say which
numbers were measured and which are plans.

## What it is

| | |
| --- | --- |
| Parameters | 729,709,856 (`klab inspect`); 28 layers, width 1,536, 24 heads, feed-forward 4,096 |
| Context | Pretrained at 4,096 tokens, then lengthened to 16,384 and 32,768 tokens in two short stages with YaRN RoPE scaling |
| Attention | Dense causal attention through flash SDPA, standard RoPE base during pretraining |
| Memory | Engram n-gram tables (orders 2 and 3, two hash heads) after blocks 1 and 14, from the first update |
| Tokenizer | 32,768-entry BPE fitted on the corpus, with the ChatML markers as single tokens |
| Pretraining | 12 billion tokens in ten strata, see [corpus](corpus/README.md); two cards, compiled blocks and loss, no activation recomputation |
| After pretraining | two long-context stages (750 million tokens), then chat tuning, then optional preference tuning, see [post-training](post-training/README.md) |

The earlier 340M model and its later variants are gone from this directory.
Their files are in Git history before this recipe was added.

## Files

- `model.yaml`, `attention.yaml`, `optimizer.yaml`: the model, its attention and
  the pretraining optimizer.
- `pretrain.yaml`, `long-context.yaml`, `long-context-32k.yaml`,
  `post-training/instruct.yaml`, `post-training/prefer.yaml`: one section per
  training stage. Each stage starts from the previous stage's run.
- `context-16k.yaml`, `context-32k.yaml`: the longer contexts (`max_seq_len`
  and YaRN RoPE scaling), composed into the long-context stages and every
  stage after them.
- `long-context-abf.yaml`: a `klab try` delta that compares a larger RoPE base
  with YaRN for the first long-context stage.
- `paths.example.yaml`, `long-context.paths.example.yaml`,
  `post-training/paths.example.yaml`: the local paths and measured counts each
  stage needs. Copy them outside Git and fill them in.
- `corpus/`: the corpus project (33 pinned sources), the release mixture, the
  tokenizer sampling plan, the pretraining and long-context token mixture
  templates and the base config `corpus export` needs.

## What was measured

Arc Pro B70 (32 GiB), bf16, this model with a 32,768-entry tokenizer, Python
source as text, Lab at `475b76d7`, PyTorch 2.15.0+xpu. One row per microbatch,
updates of 131,072 targets except where noted, 10 updates per run; targets/s is
the median of updates 4 to 10. Every run set `ZE_AFFINITY_MASK` so the process
saw only its own card, except the one marked (see below). The two-card row used
Lab at `cd5646e2` ([Lab #431](https://github.com/supernovae/model-lab/pull/431)),
which confines each process to its card itself. These runs used
`max_seq_len: 32768`; pretraining now sets 4,096, which changes no weight and
only the size of the RoPE tables.

| Rows | Attention and settings | Targets/s | Device peak |
| --- | --- | --- | --- |
| 4,096 | dense, compiled blocks and loss, no recomputation | **8,076** | 23.1 GiB |
| 4,096 | same, process sees both cards | 7,865 | 23.1 GiB |
| 4,096 | same, two processes at once, one per card | 7,781 + 8,203 = 15,984 | 23.1 GiB each |
| 4,096 | same, one run on both cards (`secondary_device_indices: [1]`) | **12,682** | 23.1 GiB each |
| 8,192 | dense, compiled, no recomputation | 5,493 | 28.6 GiB |
| 16,384 | dense, recomputation (compile is refused with it), 4-row updates | 2,348 | 21.2 GiB |
| 32,768 | dense, recomputation, 4-row updates | out of memory | |
| 32,768 | same plus `optimizer.state_offload: true` | 1,285 | 22.1 GiB |

The earlier version of this recipe used `local_selected` sparse attention with
recomputation on 8,192-token rows. It ran at 1,437 targets/s, and dense
attention with recomputation (which turns compile off) at 3,087. Sparse
attention pays at long contexts and at inference, not when pretraining a model
this size at short rows; DeepSeek added its sparse attention to an already
trained dense model.

What that means for the plan:

- **Pretrain on 4,096-token rows, on both cards.** They are 47% faster than
  8,192-token rows and leave 9 GiB of the card free; 8,192 fits with 3 GiB to
  spare. One run on both cards trained at 12,682 targets/s, so 12 billion
  tokens take about 11 days (17 on one card). Card 0 also drives the desktop:
  alone it ran at 6,773 targets/s against 8,124 on card 1, and every update
  waits for the slower card, so close GPU-heavy desktop applications during
  the run. Host RAM use for the two-card run was 20.9 GiB.
- **Lengthen the context at the end, in two short stages.** Almost all
  training stays at 4,096 tokens, where it is cheapest. Then stage 2 trains
  500 million tokens on 16,384-token rows and stage 3 250 million on
  32,768-token rows, about 6% of pretraining together. Each stage applies
  YaRN RoPE scaling from the 4,096-token original context, and its data puts
  every document of 4,096 tokens or more at the start of its own rows, with
  ordinary shorter text packed around them so short-context skill is kept.
  This is the pattern Code Llama, Qwen2.5 and DeepSeek-V3 used. Whether YaRN
  or a larger RoPE base works better for this model is an experiment:
  `long-context-abf.yaml` is the other arm (see
  [post-training](post-training/README.md#long-context)). On one card the
  stages take about 2.5 and 2.3 days; two cards are not measured at these
  lengths.
- **A larger model is not recommended on this hardware.** Doubling the
  parameters roughly halves the speed, and the card has little room left at
  4,096-token rows without recomputation.

Lab's memory planner estimates 31.9 GiB for the pretraining config, against
the 23.1 GiB measured, and would refuse it, so `pretrain.yaml` sets
`runtime.memory.estimate_policy: observe`. Keep the spill guard on (the
default): a run that outgrows the card on XPU slows to a stop instead of
failing, and the guard stops it.

## Run it

Every command is a Lab command; see Lab's `AGENTS.md` and
[corpus preparation](https://github.com/supernovae/model-lab/blob/main/docs/corpus-preparation.md).
`$WORK` is a directory on a disk with at least 400 GiB free (not `/tmp`), and
`$R` is this directory.

### 1. Corpus

```sh
klab --work-dir "$WORK" corpus acquire "$R/corpus/corpus.yaml" --plan
klab --work-dir "$WORK" corpus acquire "$R/corpus/corpus.yaml"
BUILD=$(klab --work-dir "$WORK" corpus build "$R/corpus/corpus.yaml" --offline)
RELEASE=$(klab --work-dir "$WORK" corpus freeze "$BUILD")
klab corpus audit "$RELEASE"
klab corpus finalize-family-inventory "$RELEASE" \
  --splits "$R/corpus/splits.yaml" --output "$WORK/family-inventory.jsonl"
```

`--plan` checks every declaration without the network. Acquisition downloads
about 43 GiB of dataset shards plus fifteen git repositories, and can be run
one source at a time with `--source-id`.

**Gate: cross-split near-duplicates.** The validation sources come from shards
no training source uses, but copied files, forked repositories and re-posted
pages can still put near-copies of validation text in training. Exact
duplicates are refused at build. Near-duplicates are not, and before any
pretraining run you must complete
[`corpus/near-duplicate-screen.md`](corpus/near-duplicate-screen.md).

The screen indexes the validation documents and streams the training split
past them, so the training side costs almost no memory and it covers the whole
release. It screens every document or stops with no report. Only the
validation index is bounded: `--max-heldout-documents` (default 1,000,000) and
`--max-heldout-shingles` (default 200,000,000). The index takes about 8 bytes
per validation shingle (roughly one per word) plus about 4 KB per validation
document.

This recipe's validation side is small: each of the six held-out sources keeps
one row in 200 of its shard (`hash_modulus: 200`), an estimated 40 MB of
Parquet together, well inside the default bounds. Expect one to two hours for
the 12 billion training tokens on one core, after the release is verified:

```sh
klab --work-dir "$WORK" corpus near-duplicates "$RELEASE" > "$WORK/near-duplicates.json"
```

If it stops at a bound, count the documents it indexes (every non-training row
of `documents.jsonl`, including dropped ones) and raise the bounds above them;
shingles are about one per word, typically bytes / 6, so bytes / 4 leaves
headroom:

```sh
jq -n 'reduce (inputs | select(.split != "train")) as $d
  ([0, 0]; [.[0] + 1, .[1] + ($d.text | utf8bytelength)])' \
  "$RELEASE/documents.jsonl"   # [documents, text bytes]
klab --work-dir "$WORK" corpus near-duplicates "$RELEASE" \
  --max-heldout-documents "$HELDOUT_DOCUMENTS" \
  --max-heldout-shingles "$((HELDOUT_BYTES / 4))" > "$WORK/near-duplicates.json"
```

Copy the report's `coverage`, `candidate_count` and `identical_text_count`
into the record and decide every pair. If `candidates_truncated` is true, the
report lists only the first `--max-candidates` pairs (default 20,000): rerun
with that raised until every pair is listed. Do not start pretraining on an
empty or unfilled record.

### 2. Tokenizer and mixture

```sh
EXPORT=$(klab --work-dir "$WORK" corpus export "$RELEASE" --view lm \
  --base-run-config "$R/corpus/export-base.yaml" --vocab-size 32768)
```

Copy `$EXPORT/tokenizer.yaml` to `$WORK/tokenizer.yaml` and add two things to
the copy: `chat_template: chatml`, and the contents of
`corpus/tokenizer-sampling.yaml` under `sampling:`. The template makes
`<|im_start|>` and `<|im_end|>` single tokens before any chat data exists.

```sh
klab tokenizer train "$WORK/tokenizer.yaml"
klab corpus describe "$RELEASE" --tokenizer "$WORK/tokenizer/tokenizer.json"
```

`describe` reports real token counts per source. Compare them with the quotas in
`corpus/mixture.template.yaml` before going on: the quotas for `reference` and
`practice` are guesses about how much text those repositories hold. If a
stratum is short, lower its quota and its weight in `corpus/release.yaml`
together (they must agree), and give the difference to `web`.

Fill the four `${...}` values in a copy of `corpus/mixture.template.yaml`, then:

```sh
klab corpus materialize-mixture "$WORK/mixture.yaml" --output "$WORK/mixture"
klab corpus verify-mixture "$WORK/mixture.yaml" --output "$WORK/mixture"
```

### 3. Pretrain

```sh
klab config compose "$R/pretrain.yaml" model="$R/model.yaml" \
  attention="$R/attention.yaml" optimizer="$R/optimizer.yaml" \
  "$WORK/paths.yaml" --output "$WORK/pretrain.yaml"
klab inspect "$WORK/pretrain.yaml"
klab data prepare "$WORK/pretrain.yaml"
klab stage "$WORK/pretrain.yaml" --runtime b70-xpu --through warmup \
  --output "$WORK/stages/pretrain"
klab train "$WORK/pretrain.yaml" --runtime b70-xpu --run-id devmind-pretrain \
  --require-prepared --stage-bundle "$WORK/stages/pretrain"
```

`pretrain.yaml` trains on cards 0 and 1. Do not set `ZE_AFFINITY_MASK`
yourself: Lab confines each of its processes to its own card, and a mask you
set is left alone, so `ZE_AFFINITY_MASK=0` would hide card 1 from the run. Read
the warmup's measured device peak and targets/s before committing weeks of
compute, and record them here.

### 4. After pretraining

[Post-training](post-training/README.md) covers the long-context stages, chat
tuning, preference tuning, checking the result and what can be published.

## Known gaps

Open in Lab:

| Gap | Effect here | Lab |
| --- | --- | --- |
| A mixture cannot select or upweight long documents, and its stratum shares must match the release | The long-context stages get only as many long documents as the corpus holds in pretraining's shares; read the share from the mixture receipt's `row_layout` | |
| Grouped-query attention is refused with SDPA | Full-width keys and values: about 5.3 GiB of generation cache per 32,768-token sequence | |
| The leakage screen covers probe items only | Nothing checks the corpus against HumanEval or MBPP | |

Now in Lab and not yet used by this recipe: remote-code Hugging Face export
(#415), chat and multi-field converters (#416), per-stratum `max_exposures`
(#418), archive, PDF and MediaWiki sources (#419), and executed code
benchmarks and weight quantization (#420). The long-context stages use RoPE
scaling (#427, #429), `document_start` packing (#418) and the long-context
measurements (#430); pretraining uses one process per card (#428, #431).

## Changing it

Change one setting with `klab try DELTA.yaml --vs "$WORK/pretrain.yaml"` on a
small budget and read the record. One comparison this recipe has not made and
should: `model.memory: none` against the n-gram tables. A change to the declarations after a result is recorded is a new recipe
beside this one.
