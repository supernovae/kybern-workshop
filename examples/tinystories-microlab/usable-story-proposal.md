# Useful story demo: proposed CPU validation, not executed

The website needs meaningful continuations, not merely a compiled recipe. The
40-update microlab is not evidence of that quality. Prefer an already trained,
permitted native artifact before proposing fresh CPU training.

## Candidate retained artifact

Historical source: Lab `eab014ef7ca92de89d37b47c30df2ebf021d9473`,
`experiments/research/history/tinystories-dense-30m-data-rich-v1/`.
See the [pinned result](https://github.com/supernovae/tiny-sparse-lab/blob/eab014ef7ca92de89d37b47c30df2ebf021d9473/experiments/research/history/tinystories-dense-30m-data-rich-v1/results.md)
and [endpoint receipt](https://github.com/supernovae/tiny-sparse-lab/blob/eab014ef7ca92de89d37b47c30df2ebf021d9473/experiments/research/history/tinystories-dense-30m-data-rich-v1/endpoint-receipt.json).

- Run `tinystories-dense-30m-data-rich-v1-seed 42`.
- Generation `step_00024576_gen_000014`.
- Checkpoint digest `1f090d8aaa2afc9ac38282917fdd8454fbf2682abca3aaa4ee9ab7e0e3abcdb1`.
- Tokenizer SHA256 `4c351be179075c1d4884bf043303e113dd905edaaf398ac4d7842068496c3ac3`.
- 29,893,120 parameters, 512-token context, 100,663,296 training targets.

Availability, reuse permission and publication rights are unverified. This was
an **unpromoted decoder-sensitive finding**, including repetitions and color
contradictions. Its held-out loss is not proof of usable stories. Preserve the
opened historical tests and failures; do not rebrand them as fresh evaluation.
The external TinyStories-33M model card describes GPT-Neo/MIT, but that model is
not a drop-in native DenseLM checkpoint. No model download is included here.

Native inference requires the authenticated run config/manifest/checkpoint,
tokenizer and `data/manifest.json`, `data/train.npy`, `data/validation.npy` (plus
any declared sidecars). Bare weights are insufficient. The chief must locate and
verify the complete retained closure and approved CPU runtime, without rewriting
its identities or repairing missing evidence. No new runtime/image pin is selected.

## Proposed bounded verification and generation

First retain native `checkpoint inspect --json` and `checkpoint verify --json`
for the selected checkpoint directory.
Then generate six fixed prompts using the two declarations `story-greedy.json`
and `story-sampled.json`: twelve outputs, at most 192 new tokens each. The native
GenerationPanel schema is descriptive only; it does not automatically judge
quality. Native Campaign generation_panel stages can persist panel evidence when
bound to a real evaluation index. The portable workflow profile does not yet
include those stages. Do not substitute Workshop Python to run them.

A direct native command for a single selected prompt is:

```sh
sparselab checkpoint inspect "$CHECKPOINT_DIRECTORY" --json
sparselab checkpoint verify "$CHECKPOINT_DIRECTORY" --json
sparselab generate tinystories-dense-30m-data-rich-v1-seed 42   --runs-dir "$RUNS_DIRECTORY" --checkpoint step_00024576_gen_000014   --backend cpu --prompt "$FIXED_PROMPT" --max-new-tokens 192   --context-length 512 --strict-context --temperature 0.8 --top-k 40   --seed 42 --json
```

For the greedy declaration use temperature 0 and top-k 0. Check actual prompt
lengths against the 512-token total; strict-context refusal must stay visible.
`generate --json` returns `{format: "raw", prompt, response, identity, generation,
prompt_tokens}` plus native fields. It does not itself persist panel timing or
supervisor resource evidence. Retain raw stdout/stderr, every selected and
unselected candidate continuation, failures, identities, elapsed time and memory
observations. A website may display authenticated captured JSON; do not fabricate
outputs or expose a private loopback server as a public endpoint. Native serve
has no general cross-origin public-site contract.

Proposed budget for review: four CPU threads, 30-minute whole-job deadline,
4 GiB observed RSS stop target with verified headroom, at most 64 MiB new output.
These are proposals, not measurements, approved limits or hard enforcement claims.
Measure closure bytes before any copy. Recorded arrays contain 222,549,446 IDs,
about 890 MB at int32; FP32 parameters alone are about 120 MB. Full optimizer
state, verification, temporary files and copies add storage. CPU latency remains
unknown; the first generation measures it inside the same bounded job. Historical
ROCm training time is not a CPU forecast. No automatic retries or extra ladders.

Runtime acceptance: exact authenticated identity, successful native execution,
complete evidence and owned cleanup. Proposed human demo-quality gate: at least
10/12 outputs are relevant, understandable continuations with a consistent
character/event sequence; score repetition, contradictions and ending separately.
Review/freeze this rubric before results. It is not a statistical general-quality
claim. These fresh authored prompts are development material, not claimed
train-disjoint final holdout. Preserve all failures and never cherry-pick a single
nice story as the only result.

## If the closure is unavailable

Stop and report which native artifact is missing. Do not silently download a
replacement or rerun training. The historical 30M configuration provides a
concrete longer-training starting proposal (8 layers, hidden512, FFN1408,
vocabulary8192, context512, 24,576 updates/100,663,296 targets), but CPU capacity,
time, source availability and meaningful quality criteria need a separately
approved plan. Hosted/GPU work and publication remain separate. This document
neither approves retraining nor guarantees that the old endpoint passes the rubric.

The first three prompts match the website draft exactly at kybern
`69139e888c0b9ece8a890dfcabc95f2c89077859`,
`assets/js/tinystories-story.mjs`; the other three remain additional unselected
development prompts. The website command currently requests 48 tokens, while
this separate model-quality proposal allows 192: do not equate those budgets or
claim the longer proposal has validated the shorter UI setting. Captured native
JSON preserves the actual budget. No website change is made by this recipe.

`story-website-baseline.json` separately preserves the exact three website prompts
with 48 new tokens, greedy decoding and seed 42. If both scopes are approved, the
proposal is **15 outputs total**: three website-baseline outputs plus twelve
longer outputs. The proposed 10/12 quality rubric applies only to the latter.
Retain all 15 with the actual budget and decoder in each JSON record; the website
viewer accepts raw native JSON up to 1 MiB. Use `--show-prompt` for the baseline to
retain prompt diagnostics on stderr. These authored prompts are not outputs.
