# After pretraining

Each stage is an ordinary run that names the previous stage's run directory as
`training.parent_checkpoint`. The tokenizer and every weight stay the same. The
only architecture change is the context: the long-context stages raise
`model.max_seq_len` and add RoPE scaling (`context-16k.yaml`, then
`context-32k.yaml`), and every later stage composes `context-32k.yaml` too,
because Lab refuses a child whose architecture differs from its parent's in
anything else, or whose context is shorter.

## Long context

Pretraining stays at 4,096 tokens. Two short stages then lengthen the context,
each from the one before: 500 million tokens at 16,384 (stage 2) and 250
million at 32,768 (stage 3). Neither has been run.

**Data.** Copy `corpus/long-context-mixture.template.yaml`, fill its four
`${...}` values as for the pretraining mixture, and materialize it:

```sh
klab corpus materialize-mixture "$WORK/long-context-mixture.yaml" \
  --output "$WORK/long-context-mixture"
klab corpus verify-mixture "$WORK/long-context-mixture.yaml" \
  --output "$WORK/long-context-mixture"
```

It keeps pretraining's stratum shares, which Lab requires, and starts every
document of 4,096 tokens or more on a row of its own, so long documents fill
whole rows in order while shorter text packs around them. The receipt's
`row_layout` gives, per stratum, how many rows belong wholly to one long
document. Lab cannot yet select or upweight long documents, so that share is
whatever the corpus holds; if it is small, the stages mostly train long rows
of packed short documents, and the long-context measurements below will show
it. Copy `long-context.paths.example.yaml` to `$WORK/long-context-paths.yaml`
and fill it in from the receipt.

**Stage 2.** Set `training.parent_checkpoint` in a copy of `long-context.yaml`
to the pretraining run directory, then:

```sh
klab config compose "$WORK/long-context.yaml" model="$R/model.yaml" \
  attention="$R/attention.yaml" "$R/context-16k.yaml" "$WORK/paths.yaml" \
  "$WORK/long-context-paths.yaml" --output "$WORK/stage2.yaml"
klab inspect "$WORK/stage2.yaml"
klab data prepare "$WORK/stage2.yaml"
klab stage "$WORK/stage2.yaml" --runtime b70-xpu --through warmup \
  --output "$WORK/stages/long"
klab train "$WORK/stage2.yaml" --runtime b70-xpu --run-id devmind-long-context \
  --require-prepared --stage-bundle "$WORK/stages/long"
```

About 2.5 days on one card at the measured 2,348 targets/s, less on two.

**YaRN or a larger RoPE base.** Stage 2 uses YaRN. Before committing its full
budget, compare it with a larger RoPE base (`long-context-abf.yaml`) as two
`klab try` arms from the same pretrained parent on a shortened budget. 50
million tokens is about 6 hours per arm on one card:

```sh
klab config derive "$WORK/stage2.yaml" --set training.max_tokens=50000000 \
  --set training.max_steps=382 --set optimizer.decay_steps=382 \
  --set optimizer.warmup_steps=20 --output "$WORK/stage2-short.yaml"
klab try "$R/long-context-abf.yaml" --vs "$WORK/stage2-short.yaml"
```

Then compare the arms the way Lab's
[context extension guide](https://github.com/supernovae/model-lab/blob/main/docs/evaluation.md#comparing-context-extensions)
describes: held-out loss by position on a long-document panel, and
`klab probe TRY_ID --vs BASELINE --config full` for `long_needle` retrieval at
each length and the short-context probes that show what the extension costs.
Train the full stage with whichever wins; it is one comparison on one seed, so
record it as such.

**Stage 3.** Copy the long-context mixture again with `row_tokens: 32768` and
every quota halved (the shares stay the same), materialize it to its own
output, and point a second copy of the paths file at it. Set
`training.parent_checkpoint` in a copy of `long-context-32k.yaml` to the stage
2 run, then compose and train as above with `"$R/context-32k.yaml"` in place of
`context-16k.yaml` and `--run-id devmind-long-context-32k`. About 2.3 days on
one card at the measured 1,285 targets/s; it needs optimizer state offload,
which the stage sets.

## Chat

`instruct.yaml` tunes on conversations rendered with the ChatML template, with
only the assistant's replies as targets. Lab reads conversations as JSONL
(`local_chat`, [format](https://github.com/supernovae/model-lab/blob/main/docs/post-training.md#conversation-data))
and [converts](https://github.com/supernovae/model-lab/blob/main/docs/datasets.md#convert-chat-instruction-and-multi-field-rows)
chat, instruction and multi-field datasets into it. This stage has no data yet.

Recommended sources, all checked on the Hub on 2026-11-12:

| Dataset | Revision | License | Use |
| --- | --- | --- | --- |
| `HuggingFaceTB/smoltalk2` (`SFT`) | `fc6cc2103c066455aade5d7fbb346039ae36ca5e` | per subset | The Qwen3 and DeepSeek-generated subsets. Skip the OpenHermes subset and the summarization subset. |
| `nvidia/OpenCodeInstruct` | `8f3ba5bafe4d6e8db46082cf7ae6741bc370604d` | CC-BY-4.0 | Rows whose unit tests all pass (`average_test_score == 1.0`) |
| `bigcode/self-oss-instruct-sc2-exec-filter-50k` | `356bb069eee815daa6e23e9a282eeefe1490ad44` | ODC-By | Execution-checked Python tasks |
| `bigcode/commitpackft` | `fc56fe33c030c6daa414c2b112c932b8eed085e6` | MIT | Real commits as edit instructions |
| `OpenAssistant/oasst2` | `179dd21fc55192153d94adb0e0ce8f69e222bf75` | Apache-2.0 | English, top-ranked replies only |
| `Agent-Ark/Toucan-1.5M` | `0df3cf37f2abefb380370cfb02eabea2a35ae782` | Apache-2.0 | A small sample for tool use |

Tool calls are written into the transcript as text by Lab; nothing in the
exported template or `klab serve` handles tools yet.

This is also where the engineering-practice material should do most of its
work: a few tens of thousands of question-and-answer and summarization
conversations grounded in the `practice` and `reference` documents. One percent
of pretraining gives a model this size the vocabulary; it will not recall the
content reliably without this.

```sh
klab config compose "$R/post-training/instruct.yaml" model="$R/model.yaml" \
  attention="$R/attention.yaml" "$R/context-32k.yaml" "$WORK/chat-paths.yaml" \
  --output "$WORK/instruct.yaml"
klab data prepare "$WORK/instruct.yaml"
klab data budget --prepared-root "$PREPARED" --config "$WORK/instruct.yaml" \
  --passes 2 --output "$WORK/instruct-budget.yaml"
klab train "$WORK/instruct-budget.yaml" --runtime b70-xpu --run-id devmind-instruct
klab chat devmind-instruct --message 'Write a function that parses an ISO 8601 date.'
```

## Preferences (optional)

`prefer.yaml` runs direct preference optimization on one device. No public
preference set is both clean and about code. The practical source is the model
itself: sample the instruct checkpoint on the execution-checked prompts, run the
shipped tests, and pair a passing reference (chosen) with a failing sample
(rejected). `nvidia/When2Call` (`train_pref`, CC-BY-4.0) adds pairs about when
not to call a tool.

## Check the result

```sh
klab probe devmind-instruct --config standard
klab compare RESULT --references
klab eval devmind-instruct
```

Probes cover held-out loss, calibration, recall and four multiple-choice tasks.
[`klab bench`](https://github.com/supernovae/model-lab/blob/main/docs/probes.md#code-benchmarks-klab-bench) runs HumanEval and
MBPP in a sandbox. Nothing yet checks this corpus for copies of their problems.

## Publish

[`klab weights export`](https://github.com/supernovae/model-lab/blob/main/docs/post-training.md#export-for-hugging-face) writes a
Hugging Face directory; a model with n-gram memory is exported with Lab's
modeling code. [`klab weights quantize`](https://github.com/supernovae/model-lab/blob/main/docs/post-training.md#quantize-weights)
writes int8 or int4 weights for serving; training keeps FP32 weights and
optimizer state.
