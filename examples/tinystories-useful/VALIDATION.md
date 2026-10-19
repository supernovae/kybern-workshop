# Completed baseline and publication checks

Executed declarations: Workshop `e70d82b0c3262087ba5b1c546ebfd237f87a685d`.
Training: Lab `7a517b2c065426748cd99702e82ea377877a7809` and the immutable CPU
image in the [result summary](../../results/2026-10-19-tinystories-cpu/summary.json).
Later documentation/evidence revisions are not retroactively the executed source.

Native preparation, tokenizer verification, prepared-input publication/verification,
staging, training, full-state continuation, checkpoint inspection/verification,
evaluation, reporting and generation produced retained evidence. The final session
completed 35/35 slots with zero exits, complete logs and verified cleanup. The
successful lineage finished 8,192 updates / 33,554,432 targets. Earlier failures,
host interruption and deliberate pause are preserved in the result history and
[executed argv ledger](../../results/2026-10-19-tinystories-cpu/commands.json).
The crashed trainer's missing terminal report is represented explicitly rather
than filled with a fabricated exit code.

The original story-quality rubric failed: provisional assistant assessment found
2/24 passing continuations, 1/12 held-out passes and 17/24 endings. Publication is
accepted as a learning baseline with those limitations. No self-review clearance,
human quality clearance or claim that later improvement work ran is made.

Publication verification on 2026-10-19:

- All 36 indexed public evidence files match their SHA256 and byte counts.
- All 27 exported JSON envelopes match retained originals exactly after restoring
  the single disclosed private run-directory value and removing `_publication`.
  All are valid `format: raw` envelopes below the website's 1 MiB limit.
- All 24 fixed-panel prompts match the frozen 12-line prompt file; each uses 192
  new tokens and remains within 256 total prompt-plus-generation tokens.
- 44 relative Markdown links resolve and 15 Bash blocks pass syntax-only checking.
- Public evidence scans contain no private account paths, host name, approval
  identifiers or private Notion links. Public derivatives have their own manifest;
  original raw hashes remain explicitly distinguished.
- Native public `config validate --kind run` and `--kind tokenizer` pass using the
  installed metadata-check runtime at Lab
  `fb9bb3db871db5dbe87eb6c493de65364da12261`, Python 3.14.4. These checks do not
  rerun the training pin or establish runtime/model quality.
- The future `model.ffn_dim=1024` exercise passes native `config derive` and
  `config validate --kind run` with a `.yaml` destination. The initial `.json`
  destination was refused with exit 2 and corrected; its local evidence remains.
  No future-exercise training, generation or input acquisition was performed.

Remaining boundaries: external exact-head review and coordinated merge are still
required. Weights/tokenizer/prepared arrays are retained locally, not distributed
in this repository; the public closure index is not a loadable model. A reader
must produce or obtain and verify a real closure. Native Windows/GPU execution,
cache parity, longer-context quality and Part 2 improvements are unclaimed.
The 40-update FFN comparison remains separate and unexecuted.
