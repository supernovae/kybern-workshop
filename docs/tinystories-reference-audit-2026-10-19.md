# TinyStories reference audit — 2026-10-19

After the documentation cleanup, we rechecked the published Part One learning
baseline. We didn't train anything or change the recorded results.

## Revisions

- Workshop: `eb5fcb5ca4750712392916e85de403f17f82ab16`, the owner's README and
  project-guide cleanup, following the published baseline merge `d33ef31`.
- Website: `d680aecbda49e2ac98f03a182fcc2fbe93442327`, merged PR #3.
- Lab: `ecee107ad040ebbed425fc75bc68d9d08f799ac2`. Its prose cleanup was
  `f1db53f6eb493187a2620ca70a920d8250340dba`; PR #192 then changed only
  a tokenizer test fixture and migration documentation.
- Published results: Workshop `1035a28ab96258e29232373aa1b04c35893fbb6c`.
- The run itself: Lab `7a517b2c065426748cd99702e82ea377877a7809` and
  Workshop configs `e70d82b0c3262087ba5b1c546ebfd237f87a685d`.

## Checks

- All 36 files in the current result manifest match their SHA-256 and byte
  count. All 27 output copies on the website match the Workshop files and the
  website's own hash manifest. The 27 live public JSON responses also match.
- Output JSON, commands, resolved config, quality assessment, summary,
  generation metrics, loss trajectory and `run-closure-index.json` are the
  same as at the published-results commit. The cleanup changed the result prose
  and updated its manifest; this audit changed neither.
- The useful-baseline JSON configs and prompts are the same as at the commit
  the run used. Between the Lab commit the run used and current main, `src/`
  differs only in three dashboard files. Training, preparation, config,
  continuation, evaluation and generation code is unchanged.
- Every relative link resolves in the root README, CONTRIBUTING, the
  TinyStories useful and microlab guides, the result Markdown, and Lab's README
  and microlab guide. Nineteen linked GitHub revision/path targets exist in the
  fetched Git history.
- Live website links from the TinyStories page and these Workshop guides return
  HTTP 200. `/tiny-stories-demo/` reaches the current TinyStories page and
  `/experiments/history/` reaches Experiments.
- We tested the live viewer with Playwright and Microsoft Edge 155.0.4283.62 on
  Windows: all 27 continuations and their metadata, HTTP failure and recovery,
  clear, malformed/empty/oversized local imports, escaping, budget and prompt
  controls, mobile overflow, dark mode, the no-JavaScript fallback, and the
  console.
- Offline fixtures: 52 tests passed (one optional test that needs a companion
  checkout was skipped), and all 27 ROCm recipe fixture tests passed. These
  fixtures are synthetic; they don't run training or use an accelerator.

## Repairs and limits

The README and replication guide now say that the story scores are provisional
assistant scores and that we don't distribute weights. The guide sets `RUN_ID`
to the completed continuation run and explains how to pick its fixed
checkpoint. Workshop holds the active recipes; Notion holds the backlog and
coordination, and running a recipe doesn't need it.

We didn't download weights or corpora, install dependencies, or run or change
any training, generation or dashboard process. A fresh config check couldn't
run because the bundled Python couldn't import PyYAML, so this audit makes no
claim of a new CLI run or a full Lab environment test. We believe the commands
still work because the source and configs are unchanged and the original run
record is intact. The hashes in `run-closure-index.json` refer to files kept locally;
those files weren't available, so we couldn't verify the checkpoints again. The
accepted learning baseline still failed its original quality target. Its scores
are provisional assistant scores, and there is no audited prompt benchmark
that is disjoint from the training data.
