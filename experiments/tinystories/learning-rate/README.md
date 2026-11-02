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

Status: declarations and evaluation protocol prepared; candidate training has not started. Results will be added with exact checkpoints, full accounting and limitations.
