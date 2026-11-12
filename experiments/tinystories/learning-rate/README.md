# TinyStories 50M learning-rate comparison

Question: after another 100,003,840 supervised targets, does a learning-rate schedule ten times lower make stories more consistent without hurting prediction quality? Both arms start from the original verified 50M parent; neither context child is used. We picked context 512 from the finished context comparison; see [the selection record](context-selection.json).

[Low](run-low.json) and [high](run-high.json) are native RunConfig files. Both use 50,556,800 parameters, seed 42, BF16, reference attention, sequence 512, microbatch 4, accumulation 2, 4,096 targets/update, fresh AdamW moments/RNG/cursor, and 24,415 updates. AdamW betas 0.9/0.95, epsilon 1e-8, weight decay 0.1 and gradient clipping 1.0 match. Both reuse the existing snapshot, 4,096-vocabulary tokenizer and packed arrays as they are.

| Arm | Peak LR | Floor LR | Warmup updates | Total updates |
| --- | ---: | ---: | ---: | ---: |
| Low | 0.00006 | 0.000006 | 2048 | 24415 |
| High | 0.0006 | 0.00006 | 2048 | 24415 |

The low arm scales the whole native `warmup_cosine_v1` schedule down by ten, keeping the same shape and a floor/peak ratio of 0.1. Both the peak and the floor drop, so the floors differ between arms. We froze the [schedule policy](schedule-policy.json) before either arm started. Apart from names and this LR scale, the two configs must match.

Run both arms on pinned Lab `903ad2f0bb261935132dee53295aba6b66f8e792` with the existing ROCm runtime on one device. Set physical paths with native `config derive`, then publish and verify prepared inputs for each config without retokenizing or repacking. Stage through warmup, then train with native weights-only promotion from parent `c72d7d0283de2c6008f1b80d855bad6cb6ebc497f0094957a8982bd58a049110`. Stop once after 256 updates, verify the full checkpoint and that the resume state matches exactly, then finish the original budget. Keep checkpoints every 256 updates with `keep_periodic: false`, and inline validation every 1024 updates on 32 batches. Record the actual cost of preparation, startup, optimizer, reporting, checkpoint, evaluation, generation and each whole command. Keep architecture, attention, data curation and runtime the same in both arms.

Score both existing held-out panels (context 256 and 512) unchanged. Then use the frozen [story panel](story-panel.json): the first 12 validation stories from ordinal 2048 onward that meet the length rules, chosen before either arm trained. One streaming pass over the 500,000 selected training documents found no exact copy of any full story and no prompt appearing as a substring. Near-duplicates could still exist, and this validation set has been used before, so treat it as development data. The prompts come from one slice of the source and are not balanced for character names or themes.

For every prompt, generate a greedy and a temperature-0.7/top-k-40 output with seed 42, strict 512 context, at most 256 new tokens and no stop sequences. Use the public `generate_with_token_ids` API with native verified `load_run` and a registered runtime. The returned completion IDs leave out EOS, so fewer than 256 means the model emitted EOS and exactly 256 means it hit the token limit. Keep all tokens, outputs, errors and timings. Tell how a generation stopped from the token count, not by retokenizing the decoded text.

Score each output with the frozen [rubric](story-rubric.json) for character consistency, object/state continuity, causal resolution and repetition. Each prompt/mode pair gets random A/B labels. We committed to the [assignment](blind-assignment-receipt.json) before training and kept the mapping hidden until the scores were saved. Score without knowing the run, checkpoint or learning rate, then reveal the mapping and the paired results. The reviewer is one assistant. If a story hits the token limit before its ending, mark the causal-resolution score as censored instead of scoring a failed ending; report censored outputs, failures and every criterion's distribution separately. Keep weak outputs, and with one seed and a small panel, don't claim a general quality win.

## Completed comparison

Both arms completed on 2026-11-02 from the same original parent with exactly **24,415 updates / 100,003,840 additional targets each**. Full-state checkpoint verification and the step-256 resume comparisons passed for model, optimizer, RNG, scaler, schedule, counters and data cursor. Every step was applied exactly once with 4,096 targets per update, finite losses and zero overflow retries. The experiment used Workshop recipe commit `8be366dc53e09928fe978dfbdf520bb15a44e844` and the Lab pin above throughout.

| ROCm checkpoint | 256-context loss | 512-context loss |
| --- | ---: | ---: |
| Original parent | 1.075286 | 1.933697 |
| Low LR | **1.035381** | **0.971255** |
| High LR | 1.094438 | 1.028807 |

Each column is its own frozen protocol over 65,536 supervised targets, and every row in a column uses the same native comparison group. Training was BF16; evaluation ran in FP32 on the same ROCm runtime. The Intel context results ran on a different runtime and are reported separately.

All 48 generations finished with EOS before the 256-token limit, with no errors and no censored endings. Scores and notes were frozen at `2026-11-02T05:04:39.631515+00:00`, with digest `bbd698d926beab66323871855c56e23d18e91acf4b3ddafe6c5ba5551970ce5d`; the committed assignment was revealed afterward at `2026-11-02T05:04:57.179839+00:00`.

| Blind criterion (0–2; higher is better) | Low mean | High mean | Low higher / tied / high higher |
| --- | ---: | ---: | ---: |
| Character consistency | 1.917 | 1.917 | 1 / 21 / 2 |
| Object/state continuity | **1.417** | 0.958 | 14 / 4 / 6 |
| Causal resolution | **1.208** | 0.875 | 12 / 6 / 6 |
| Repetition control | **1.625** | 1.375 | 10 / 10 / 4 |

The lower schedule did better here: it improved both validation panels and three of the four blind-review means, and tied on character consistency. That makes gentler continued training of the existing 50M model worth trying before reaching for a bigger model. The comparison is small: one parent, one seed, twelve short openings from one source slice, two generation modes and one assistant reviewer. The validation set has been used before and may hold near-duplicates of training stories.

Every output is kept, including the counterexamples. In `story-04-greedy`, low LR uses a doctor/rest/recovery sequence while high LR cures the lion by bringing a tree. In `story-09-greedy`, low LR keeps the knee-injury episode focused while high LR adds a toy episode that swaps actor and ownership. Low LR still fails: `story-07-sampled` draws with a camera and unexpectedly returns home; `story-08-sampled` resets a planted bulb's state; `story-12-greedy` rewards secret exploration and then asserts a safety lesson. Seven low-LR outputs and eleven high-LR outputs scored zero on causal resolution. These are short openings, so they tell us little about coherence over long stories or recall from long prompts.

## Cost and artifacts

| Measured cost | Low LR | High LR |
| --- | ---: | ---: |
| Training commands, including startup/recovery | 3,361.20 s | 3,368.61 s |
| Optimizer work, both segments | 2,390.47 s | 2,386.77 s |
| Optimizer targets/s | 41,834 | 41,899 |
| Reporting, both segments | 540.26 s | 538.57 s |
| Checkpointing, both segments | 289.87 s | 299.69 s |
| Peak reserved VRAM | 2,678,063,104 bytes | 2,678,063,104 bytes |
| Maximum sampled process swap | 0 bytes | 0 bytes |

The arms ran in one order, low then high, so read the small timing difference loosely. Native phase totals leave out some outer command startup; the full command timings and the unaccounted remainder are saved separately. Reporting and checkpointing still cost a noticeable share of the time. The live progress rate comes from elapsed-time samples, so don't use it as optimizer-only throughput.

We reused the existing snapshot, tokenizer and packed arrays, with no new download, tokenizer fit or packing. Publishing each config's prepared inputs took 36.47 / 35.26 seconds, and staging through warmup took 77.19 / 82.74 seconds. All timed preparation, training, held-out evaluation and generation commands added up to about 1h 58m 44s; from first to last they spanned about 2h 1m 14s, including gaps for checks. Review scoring, source checkout, CI and publishing are not included.

Final checkpoints:

- Low: `085adc01f1512dc41570be869d471b184d84decb3a80e453bb83d3bef43ccc89`
- High: `bbed7f0dcbac4aa0cefa2a0e3e7c35ad6415836b9d7dfe6b31938be47cb37f82`

Under the unchanged retention policy, each final run directory keeps the final generation and the one before it. The original parent, the Intel context results and the earlier calibration artifacts are untouched. No further training was done for this write-up.

[Execution and validation records](results.json) · [All low-LR outputs and token IDs](generation-low.json) · [All high-LR outputs and token IDs](generation-high.json) · [Anonymous review packet](blind-panel.json) · [Frozen scores and notes](blind-scores.json) · [Assignment reveal](assignment-reveal.json) · [Complete paired comparison](story-comparison.json)

The native checkpoint, source and data hashes refer to the original artifacts. These files are cleaned-up summaries with private paths and machine identifiers removed. Prepared-bundle reuse and the earlier Intel handoff have been tried. Unified placement across machines, Colab, and continuing optimizer state on a different device are still untested.
