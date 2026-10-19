# TinyStories reference audit — 2026-10-19

This audit checks the published Part One learning baseline after the documentation
cleanup. It does not add a training run or change the retained evidence.

## Revisions

- Workshop: `eb5fcb5ca4750712392916e85de403f17f82ab16`, the owner's README and
  project-guide cleanup, following the published baseline merge `d33ef31`.
- Website: `d680aecbda49e2ac98f03a182fcc2fbe93442327`, merged PR #3.
- Lab: `ecee107ad040ebbed425fc75bc68d9d08f799ac2`. Its prose cleanup was
  `f1db53f6eb493187a2620ca70a920d8250340dba`; PR #192 subsequently changed only
  a tokenizer test fixture and migration documentation.
- Published evidence pin: Workshop `1035a28ab96258e29232373aa1b04c35893fbb6c`.
- Recorded execution: Lab `7a517b2c065426748cd99702e82ea377877a7809` and
  Workshop declarations `e70d82b0c3262087ba5b1c546ebfd237f87a685d`.

## Checks

- All 36 files listed by the current result manifest match both SHA-256 and byte
  count. All 27 website output copies match Workshop bytes and the website's
  pinned provenance manifest. The 27 live public JSON responses also match.
- Output JSON, commands, resolved config, quality assessment, summary, generation
  metrics, loss trajectory and checkpoint closure index are unchanged from the
  published evidence pin. The cleanup changed result prose and updated its
  manifest; this audit changes neither.
- The useful-baseline JSON declarations and prompts are unchanged from the
  recorded declaration revision. Between the recorded Lab revision and current
  main, `src/` differs only in three dashboard files. The training, preparation,
  config, continuation, evaluation and generation implementations are unchanged.
- No missing relative targets in the root README, CONTRIBUTING, TinyStories
  useful/microlab Markdown guides, result Markdown, or Lab README/microlab guide.
  Nineteen linked GitHub revision/path targets exist in fetched Git history.
- Live website links from the TinyStories page and these Workshop guides return
  HTTP 200. `/tiny-stories-demo/` reaches the current TinyStories page and
  `/experiments/history/` reaches Experiments.
- Playwright with Microsoft Edge 155.0.4283.62 on Windows verified the live
  viewer: all 27 continuations and metadata, HTTP failure/recovery, clear,
  malformed/empty/oversized local imports, escaping, budget/prompt controls,
  mobile overflow, dark mode, no-JavaScript fallback and console checks.
- Established offline fixtures: 52 tests (one optional companion-checkout test
  skipped), plus all 27 ROCm recipe fixture tests passed. These are synthetic
  fixtures, not accelerator or training execution.

## Repairs and limits

The current README and replication guide now retain provisional assistant-score
provenance and the absence of distributed weights. The guide explicitly binds
`RUN_ID` to the completed continuation and explains how to select its immutable
checkpoint. Workshop holds active recipes; Notion holds backlog/coordination and
is not a runtime dependency.

No weights or corpus were downloaded, no dependencies installed, and no training,
generation or dashboard process was run or changed. A fresh schema-validation
attempt could not import PyYAML in the available bundled Python; this audit does
not claim a new CLI execution or full Lab environment test. Command compatibility
is supported by the unchanged source/declarations and retained execution record.
The checkpoint closure hashes are references to retained local files; their bytes
were not available for a fresh checkpoint verification. The accepted learning
baseline still failed its original quality target, with provisional assistant
scores and no audited train-disjoint prompt benchmark.
