# Devmind

Devmind is a 730M-parameter decoder trained from scratch with
[Kybern Model Lab](https://github.com/supernovae/model-lab), biased toward
software development: Python first, then JavaScript and TypeScript, GitHub
issues and pull requests, and reference documentation. It is meant to be a
complete demonstration of Lab, from pinned sources to a chat model, and a
baseline to change one thing at a time.

**Nothing has been trained from this recipe yet.** The declarations load with
Lab, the model shape has been measured on one Arc Pro B70 for a handful of
updates, and the data has not been downloaded. The sections below say which
numbers were measured and which are plans.

## What it is

| | |
| --- | --- |
| Parameters | 729,709,856 (`klab inspect`); 28 layers, width 1,536, 24 heads, feed-forward 4,096 |
| Context | `max_seq_len: 32768` |
| Attention | [`local_selected`](https://github.com/supernovae/model-lab/blob/main/docs/sparse-attention.md): the 512 tokens before each position, 16 selected earlier 64-token blocks, learned block summaries, and 384-wide latent keys and values |
| Memory | Engram n-gram tables (orders 2 and 3, two hash heads) after blocks 1 and 14, from the first update |
| Tokenizer | 32,768-entry BPE fitted on the corpus, with the ChatML markers as single tokens |
| Pretraining | 12 billion tokens in ten strata, see [corpus](corpus/README.md) |
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

One Arc Pro B70 (32 GiB), bf16, activation recomputation on, synthetic text,
this model with a 32,768-entry tokenizer, one row per microbatch, Lab at
`c1cbe3a2` plus [#414](https://github.com/supernovae/model-lab/pull/414).

| Row length | Attention | Device peak | Targets/s | Updates |
| --- | --- | --- | --- | --- |
| 8,192 | this recipe | 15.4 GiB | 1,437 (median of updates 4 to 10) | 10 |
| 8,192 | dense `sdpa`, same model | 15.8 GiB | 3,087 | 10 |
| 32,768 | this recipe, before #414 | out of memory at the output head | | 0 |
| 32,768 | this recipe, with #414 | 26.9 GiB | 1,401 | 1, then stalled |

What that means for the plan:

- **8,192-token rows train.** That is the pretraining row.
- **32,768-token rows do not train on a 32 GiB card yet.** After its first
  update the run stopped making progress and host memory fell by about 40 GiB,
  so it was stopped. Until that is fixed
  ([Lab #417](https://github.com/supernovae/model-lab/issues/417)), the model can
  read 32,768 tokens but has only been trained on rows up to the long-context
  stage's length. Treat anything beyond that length as untested.
- **It is slow.** At 1,437 targets/s per device, and if four devices scale as
  well as two did for the earlier model (1.69 times for two), 12 billion tokens
  is on the order of four to five weeks. Four-device throughput has not been
  measured. Sparse attention costs about half the speed of dense at this row
  length; it pays back at longer rows and at inference, where a user's cache
  holds 384-wide latents and each new token reads about 1,600 positions.
- **A larger model is not recommended on this hardware.** Doubling the
  parameters roughly halves the speed and leaves less room for long rows.

Do not set `runtime.memory.estimate_policy: observe` to get past a refusal on
XPU. A run that outgrows the card does not fail; it fills host memory.

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
klab corpus near-duplicates "$RELEASE"
klab corpus finalize-family-inventory "$RELEASE" \
  --splits "$R/corpus/splits.yaml" --output "$WORK/family-inventory.jsonl"
```

`--plan` checks every declaration without the network. Acquisition downloads
about 43 GiB of dataset shards plus fifteen git repositories, and can be run
one source at a time with `--source-id`.

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

`pretrain.yaml` names four devices. With fewer, shorten
`runtime.secondary_device_indices`; an update is still 16 rows. Read the warmup's
measured device peak and targets/s before committing weeks of compute, and
record them here.

### 4. After pretraining

[Post-training](post-training/README.md) covers the long-context stage, chat
tuning, preference tuning, checking the result and what can be published.

## Known gaps

These are open in Lab and limit what this recipe can do today.

| Gap | Effect here | Lab |
| --- | --- | --- |
| Output head held every logit of a row | 32k rows failed immediately | [#414](https://github.com/supernovae/model-lab/pull/414) (open; `pretrain.yaml` uses its setting) |
| 32k rows spill on a 32 GiB card; no spill guard; `local_selected` speed | Long-context stage uses 12,288-token rows | [#417](https://github.com/supernovae/model-lab/issues/417) |
| Export covers Llama-shaped models only | The trained model cannot be published to Hugging Face | [#415](https://github.com/supernovae/model-lab/issues/415) |
| No converter for chat or multi-field datasets | Chat data must be converted by hand; commits and instruction pairs are left out of pretraining | [#416](https://github.com/supernovae/model-lab/issues/416) |
| Mixtures cut long documents across rows; one repeat count for all strata | Long rows hold mostly short documents | [#418](https://github.com/supernovae/model-lab/issues/418) |
| No archive or PDF sources | No RFCs, NIST, NASA or accident reports yet | [#419](https://github.com/supernovae/model-lab/issues/419) |
| No executed code benchmarks; no quantized inference | No HumanEval or MBPP score; no int8 serving | [#420](https://github.com/supernovae/model-lab/issues/420) |

## Changing it

Change one setting with `klab try DELTA.yaml --vs "$WORK/pretrain.yaml"` on a
small budget and read the record. Three comparisons this recipe has not made
and should: `selector: mean_key` against `learned`; dense attention against
`local_selected` at a matched budget; `model.memory: none` against the n-gram
tables. A change to the declarations after a result is recorded is a new recipe
beside this one.
