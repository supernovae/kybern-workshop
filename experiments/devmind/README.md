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
| Context | Pretrained on 4,096-token rows, then a short long-context stage on 16,384-token rows; `max_seq_len: 32768` |
| Attention | Dense causal attention through flash SDPA, standard RoPE base |
| Memory | Engram n-gram tables (orders 2 and 3, two hash heads) after blocks 1 and 14, from the first update |
| Tokenizer | 32,768-entry BPE fitted on the corpus, with the ChatML markers as single tokens |
| Pretraining | 12 billion tokens in ten strata, see [corpus](corpus/README.md); compiled blocks and loss, no activation recomputation |
| After pretraining | longer rows, then chat tuning, then optional preference tuning, see [post-training](post-training/README.md) |

The earlier 340M model and its later variants are gone from this directory.
Their files are in Git history before this recipe was added.

## Files

- `model.yaml`, `attention.yaml`, `optimizer.yaml`: the model, its attention and
  the pretraining optimizer.
- `pretrain.yaml`, `long-context.yaml`, `post-training/instruct.yaml`,
  `post-training/prefer.yaml`: one section per training stage. Each stage starts
  from the previous stage's run.
- `paths.example.yaml`, `post-training/paths.example.yaml`: the local paths and
  measured counts each stage needs. Copy them outside Git and fill them in.
- `corpus/`: the corpus project (33 pinned sources), the release mixture, the
  tokenizer sampling plan, the token mixture template and the base config
  `corpus export` needs.

## What was measured

Arc Pro B70 (32 GiB), bf16, this model with a 32,768-entry tokenizer, Python
source as text, Lab at `475b76d7`, PyTorch 2.15.0+xpu. One row per microbatch,
updates of 131,072 targets except where noted, 10 updates per run; targets/s is
the median of updates 4 to 10. Every run set `ZE_AFFINITY_MASK` so the process
saw only its own card, except the one marked (see below).

| Rows | Attention and settings | Targets/s | Device peak |
| --- | --- | --- | --- |
| 4,096 | dense, compiled blocks and loss, no recomputation | **8,076** | 23.1 GiB |
| 4,096 | same, process sees both cards | 7,865 | 23.1 GiB |
| 4,096 | same, two processes at once, one per card | 7,781 + 8,203 = 15,984 | 23.1 GiB each |
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

- **Pretrain on 4,096-token rows.** They are 47% faster than 8,192-token rows
  and leave 9 GiB of the card free; 8,192 fits with 3 GiB to spare. At 8,076
  targets/s, 12 billion tokens take about 17 days on one card.
- **Lengthen the context afterwards.** The long-context stage trains 500
  million tokens on 16,384-token rows (about 2.5 days on one card). It should
  also raise the RoPE base or apply YaRN, as Code Llama and Qwen2.5 did; Lab
  cannot change RoPE in a child stage yet
  ([Lab #427](https://github.com/supernovae/model-lab/issues/427)).
- **One card per process.** A process that can see both cards also holds its
  device memory in host RAM: the run that saw both cards took about 37 GiB of
  host RAM and stalled the desktop at its final checkpoint, against about
  8 GiB with one card visible. Lab's `secondary_device_indices` run every
  device in one process, so they are left out until Lab runs one process per
  card ([Lab #428](https://github.com/supernovae/model-lab/issues/428)). Two
  masked processes ran side by side at 1.98 times one card's throughput, so
  two cards should bring pretraining to about 9 days once that lands; gradient
  exchange is not included in that figure.
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

This recipe's validation side is not small. The six held-out sources are whole
shards, about 7.9 GB of Parquet together, which we estimate at several billion
words: several times the default bounds, and tens of GB of RAM. Count the
documents the screen will index (every non-training row of `documents.jsonl`,
including dropped ones) before running:

```sh
jq -n 'reduce (inputs | select(.split != "train")) as $d
  ([0, 0]; [.[0] + 1, .[1] + ($d.text | utf8bytelength)])' \
  "$RELEASE/documents.jsonl"   # [documents, text bytes]
```

Shingles are about one per word, typically bytes / 6. Set
`--max-heldout-documents` just above the document count and
`--max-heldout-shingles` to bytes / 4 for headroom, then expect an index of
about 8 bytes × bytes / 6 plus 4 KB per document:

```sh
klab --work-dir "$WORK" corpus near-duplicates "$RELEASE" \
  --max-heldout-documents "$HELDOUT_DOCUMENTS" \
  --max-heldout-shingles "$((HELDOUT_BYTES / 4))" > "$WORK/near-duplicates.json"
```

If the index would not fit in host RAM with headroom, take fewer or smaller
held-out shards and rebuild the release, rather than screening part of it.
Expect one to two hours per 12 billion training tokens on one core after the
release is verified.

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
export ZE_AFFINITY_MASK=0   # this process sees only the first card
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

`pretrain.yaml` uses one device; see above for why. Read the warmup's measured
device peak and targets/s before committing weeks of compute, and record them
here.

### 4. After pretraining

[Post-training](post-training/README.md) covers the long-context stage, chat
tuning, preference tuning, checking the result and what can be published.

## Known gaps

Open in Lab:

| Gap | Effect here | Lab |
| --- | --- | --- |
| A child stage cannot change RoPE; no YaRN or NTK scaling | The long-context stage trains longer rows on the pretraining RoPE base | [#427](https://github.com/supernovae/model-lab/issues/427) |
| Several devices share one process, which holds device memory in host RAM on Arc | Pretraining uses one card | [#428](https://github.com/supernovae/model-lab/issues/428) |
| Grouped-query attention is refused with SDPA | Full-width keys and values: about 5.3 GiB of generation cache per 32,768-token sequence | |
| The leakage screen covers probe items only | Nothing checks the corpus against HumanEval or MBPP | |

Now in Lab and not yet used by this recipe: remote-code Hugging Face export
(#415), chat and multi-field converters (#416), `document_start` packing and
per-stratum `max_exposures` (#418), archive, PDF and MediaWiki sources (#419),
and executed code benchmarks and weight quantization (#420).

## Changing it

Change one setting with `klab try DELTA.yaml --vs "$WORK/pretrain.yaml"` on a
small budget and read the record. One comparison this recipe has not made and
should: `model.memory: none` against the n-gram tables. A change to the declarations after a result is recorded is a new recipe
beside this one.
