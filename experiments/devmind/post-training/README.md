# After pretraining

Each stage is an ordinary run that names the previous stage's run directory as
`training.parent_checkpoint`. The model and attention sections and the tokenizer
stay exactly the same; Lab refuses a parent with a different architecture or
tokenizer.

## Long context

```sh
klab config compose "$R/long-context.yaml" model="$R/model.yaml" \
  attention="$R/attention.yaml" "$WORK/paths.yaml" --output "$WORK/long-context.yaml"
klab inspect "$WORK/long-context.yaml"
klab data prepare "$WORK/long-context.yaml"
klab stage "$WORK/long-context.yaml" --runtime b70-xpu --through warmup \
  --output "$WORK/stages/long"
klab train "$WORK/long-context.yaml" --runtime b70-xpu --run-id devmind-long-context \
  --require-prepared --stage-bundle "$WORK/stages/long"
```

500 million tokens on 16,384-token rows of the same mixture, about 2.5 days on
one card at the measured 2,348 targets/s. This stage has not been run. It should
also raise the RoPE base or apply YaRN for the longer context; Lab cannot change
RoPE in a child stage yet
([Lab #427](https://github.com/supernovae/model-lab/issues/427)). 32,768-token
rows also train, with `optimizer.state_offload: true`, at 1,285 targets/s.

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
  attention="$R/attention.yaml" "$WORK/chat-paths.yaml" --output "$WORK/instruct.yaml"
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
