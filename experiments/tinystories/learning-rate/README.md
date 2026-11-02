# TinyStories 50M learning-rate comparison

Question: can a tenfold lower learning-rate schedule improve story consistency while preserving useful prediction quality after 100,003,840 additional supervised targets? Both arms use the original verified 50M parent, not either context child. Context 512 was chosen from the completed comparison; see [the selection receipt](context-selection.json).

[Low](run-low.json) and [high](run-high.json) are native RunConfig declarations. Both use 50,556,800 parameters, seed 42, BF16, reference attention, sequence 512, microbatch 4, accumulation 2, 4,096 targets/update, fresh AdamW moments/RNG/cursor, and 24,415 updates. AdamW betas 0.9/0.95, epsilon 1e-8, weight decay 0.1 and gradient clipping 1.0 match. The existing snapshot, 4,096-vocabulary tokenizer and packed arrays are reused unchanged.

| Arm | Peak LR | Floor LR | Warmup updates | Total updates |
| --- | ---: | ---: | ---: | ---: |
| Low | 0.00006 | 0.000006 | 2048 | 24415 |
| High | 0.0006 | 0.00006 | 2048 | 24415 |

This is a tenfold scale change of the complete native `warmup_cosine_v1` schedule, with the same normalized shape and floor/peak ratio 0.1. It is not a peak-only test with an identical absolute floor. The [schedule policy](schedule-policy.json) was frozen before either candidate started. Apart from names and this LR scale, typed configurations must match.

Use pinned Lab `903ad2f0bb261935132dee53295aba6b66f8e792` and the existing ROCm runtime on one device for both arms. Bind physical paths through native `config derive`, publish/verify configuration-specific prepared inputs without re-tokenizing or repacking, stage through warmup, then train with native weights-only promotion from parent `c72d7d0283de2c6008f1b80d855bad6cb6ebc497f0094957a8982bd58a049110`. Stop after 256 updates once, verify the full checkpoint and exact resume state, then finish the original budget. Keep checkpoint cadence 256 / `keep_periodic: false` and inline validation 1024 / 32 batches. Record actual preparation, startup, optimizer, reporting, checkpoint, evaluation, generation and total command costs. No architecture, attention, data-curation or runtime changes belong to this comparison.

Score both existing context-256/context-512 held-out panels unchanged. Separately use the frozen [story panel](story-panel.json): the first 12 eligible validation stories from ordinal 2048 onward, selected by declared length rules before candidate training. A single streaming membership pass over 500,000 selected training documents found no exact full-story duplicate or prompt substring match. This does not establish semantic near-duplicate independence or make the reused validation corpus an untouched final test. The prompts reflect this source slice and are not balanced for character names or themes.

Generate greedy and temperature-0.7/top-k-40 outputs for every prompt, seed 42, strict 512 context, at most 256 new tokens, no stop sequences. Use the existing public `generate_with_token_ids` API with native verified `load_run` and registered-runtime authorization. Returned completion IDs exclude EOS: fewer than 256 means EOS, exactly 256 means the token limit. Preserve all tokens, outputs, errors and timing. Do not infer stopping by re-tokenizing decoded text.

Apply the frozen [rubric](story-rubric.json) to character consistency, object/state continuity, causal resolution and repetition. Each prompt/mode pair has randomly assigned A/B labels; the [assignment commitment](blind-assignment-receipt.json) predates training, while the mapping remains concealed until scores are saved. Score without run, checkpoint or LR identities, then release the mapping and paired results. The reviewer is one assistant, not an independent human panel. Token-limited causal endings are censored rather than scored as failed EOS endings; report censoring, failures and all criterion distributions separately. Do not discard weak outputs or claim a general quality win from this small one-seed comparison.

## Completed comparison

Both arms completed on 2026-11-02 from the same original parent with exactly **24,415 updates / 100,003,840 additional targets each**. Native full-state checkpoint verification and the step-256 resume comparisons passed for model, optimizer, RNG, scaler, schedule, counters and data cursor. Applied-update audits found every step exactly once, 4,096 targets per update, finite losses and zero overflow retries. The experiment used Workshop recipe commit `8be366dc53e09928fe978dfbdf520bb15a44e844` and the Lab pin above throughout.

| ROCm checkpoint | 256-context loss | 512-context loss |
| --- | ---: | ---: |
| Original parent | 1.075286 | 1.933697 |
| Low LR | **1.035381** | **0.971255** |
| High LR | 1.094438 | 1.028807 |

Each column is a separate frozen protocol over 65,536 supervised targets. All candidate/parent comparisons match the native comparison group within that column. Inference was FP32 on the same ROCm runtime; training was BF16. The Intel context results are a separate runtime comparison and are not pooled here.

All 48 generations completed and terminated with EOS before the 256-token limit. There were no generation errors or censored endings. Scores and notes were frozen at `2026-11-02T05:04:39.631515+00:00`, with digest `bbd698d926beab66323871855c56e23d18e91acf4b3ddafe6c5ba5551970ce5d`; the committed assignment was revealed afterward at `2026-11-02T05:04:57.179839+00:00`.

| Blind criterion (0–2; higher is better) | Low mean | High mean | Low higher / tied / high higher |
| --- | ---: | ---: | ---: |
| Character consistency | 1.917 | 1.917 | 1 / 21 / 2 |
| Object/state continuity | **1.417** | 0.958 | 14 / 4 / 6 |
| Causal resolution | **1.208** | 0.875 | 12 / 6 / 6 |
| Repetition control | **1.625** | 1.375 | 10 / 10 / 4 |

The lower schedule is the better candidate in this bounded comparison: it improves both validation panels and three blind-review means. Character-consistency means tie. This supports testing gentler continuation within the existing 50M model before treating parameter growth as necessary. It does not establish general quality significance: there is one parent, one seed, twelve short source-slice openings, two generation modes and one assistant reviewer. The reused validation corpus remains development data, and exact training disjointness does not exclude semantic near-duplicates.

Every output is retained, including counterexamples. In `story-04-greedy`, low LR uses a doctor/rest/recovery sequence while high LR cures the lion by bringing a tree. In `story-09-greedy`, low LR keeps the knee-injury episode focused while high LR adds a toy episode that swaps actor and ownership. Low LR still fails: `story-07-sampled` draws with a camera and unexpectedly returns home; `story-08-sampled` resets a planted bulb's state; `story-12-greedy` rewards secret exploration and then asserts a safety lesson. Seven low-LR outputs and eleven high-LR outputs received causal-resolution score zero. Short-opening performance does not establish long-story coherence or long-prompt factual memory.

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

The small timing difference is observational: execution order was low then high, without counterbalancing. Native phase totals exclude some outer command startup; full command timings and residual accounting are preserved separately. Reporting and checkpoint costs remain material. The live progress rate uses elapsed-time samples and should not be substituted for optimizer-only throughput.

The existing snapshot, tokenizer and packed arrays were reused. Configuration-specific prepared-input publication took 36.47 / 35.26 seconds, and staging through warmup took 77.19 / 82.74 seconds. No corpus acquisition, tokenizer fit or packing was repeated. All timed preparation, training, held-out evaluation and generation commands totaled about 1h 58m 44s; their wall span was about 2h 1m 14s, including gaps for checks. Reviewer scoring, source checkout, CI and publication are outside that execution cost.

Final checkpoints:

- Low: `085adc01f1512dc41570be869d471b184d84decb3a80e453bb83d3bef43ccc89`
- High: `bbed7f0dcbac4aa0cefa2a0e3e7c35ad6415836b9d7dfe6b31938be47cb37f82`

Both final run directories retain the final generation and the preceding generation under the unchanged retention policy. The original parent, Intel context results and prior calibration artifacts remain intact. No additional training is part of this results publication.

[Execution and validation receipts](results.json) · [All low-LR outputs and token IDs](generation-low.json) · [All high-LR outputs and token IDs](generation-high.json) · [Anonymous review packet](blind-panel.json) · [Frozen scores and notes](blind-scores.json) · [Assignment reveal](assignment-reveal.json) · [Complete paired comparison](story-comparison.json)

Native checkpoint/source/data hashes identify original artifacts. These files are sanitized summaries with private paths and machine identifiers omitted. Native prepared-bundle reuse and earlier Intel handoff are exercised; unified topology placement, Colab and cross-device optimizer-state continuation remain unproven.
