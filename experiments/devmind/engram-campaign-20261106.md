# DevMind Engram continuation — operator evidence, 2026-11-06

This ongoing private research run supersedes the October 29 “execution stopped” status. No weights or source-text corpus are published here. Validation loss is a limited training-health observation, not evidence of reliable reasoning or factual accuracy.

## Budget and lineage

The original EXP-1 manifest specifies 341,885,952 backbone parameters and 10,256,578,560 training targets (30× backbone size). The inherited dense checkpoint had already consumed 2,080,374,784 targets. The Engram counter is additional: the recovered original exposure target corresponds to 8,176,203,776 Engram targets. The subsequent memory-first design did not establish a separate final Engram budget. These counters must not be conflated; 12B was a corpus-preparation goal, not an additional training budget.

The latest completed 50,003,192-target phase ended at step 22,932 / 1,310,272,432 Engram targets. Its final full-state checkpoint is `step_00022932_gen_000013`, manifest SHA-256 `4131a159164aadf1346afbf2aea95ea4d1f86dcddf9e205e5e182ef3b9e31e86`, validation loss 2.587253632462752. The following 100,003,501-target phase has applied optimizer updates; its endpoint is step 23,691 / 1,410,275,933 targets. Terminal outcome remains pending.

## Observed execution configuration

- Tiny Sparse Lab commit `a2fdb25ed82519f3c65f1a9752aa86bbdedd2bcc`.
- Intel B70, private Intel 26.40 stack, PyTorch 2.15.0+xpu, Python 3.14, bf16.
- 4,096-token context; microbatch at most four documents; 131,072-target effective optimizer groups.
- Compiled transformer blocks and output-head/loss, dynamic shapes; activation checkpointing off; optimizer foreach disabled.
- Per-microbatch shape bounds: 8,192 padded slots and 16,777,216 attention cells.
- Adam/RNG, consumed token/document/group prefix and frozen segment boundaries preserved. Trunk LR floor 1e-5, memory-table multiplier 5; no warmup restart or reheating.
- One native GPU lease/writer. Active data and checkpoints on NVMe; historical generations archived separately.
- Recent sustained windows measured roughly 18.4–18.8K real supervised targets/s including saves. This is observed throughput, not an isolated causal speedup claim.

## Current data and next queue

The current phase retains 35% FineWeb-Edu score-4+, 30% notebooks, 15% FineMath, 15% instructions and 5% Cosmopedia. Its exact targets are 35,000,626 / 30,001,127 / 15,000,211 / 15,000,600 / 5,000,937 respectively. Instructions in this phase are entirely the already approved Smol-SmolTalk source; the instruction pillar is unchanged. All-token continued pretraining and native role serialization remain unchanged.

Native packing verified identical historical tokens, identical historical optimizer-group boundaries, zero consumed-family overlap, and full-state continuation binding. The 100M phase has 96,764 fresh documents and 759 new optimizer updates. A 25,005,482-target bridge is packed from already-screened supply, followed by an installed 180M-ceiling phase waiting for notebook 7, web 76 and Cosmopedia 1 screening. The bridge replaced an unselected 60M ceiling to avoid waiting for the larger Cosmopedia pool. Installed supervisors are not claims of actual training.

Pinned replenishment sources:

| Source | Revision | Current acquisitions |
|---|---|---|
| HuggingFaceTB/smollm-corpus, FineWeb-Edu dedup | `3ba9d605774198c5868892d7a8deda78031a781f` | Web 75 screened; web 76 acquired and preparing |
| HuggingFaceTB/issues-kaggle-notebooks | `ef882ad1ed8274340e8fc9bac087c903f2f75396` | Notebooks 6 and 7 screened |
| HuggingFaceTB/finemath | `e92b25a616738fe95dc186b64dfb19f9c8525594` | FineMath-4plus shard 2 screened |
| HuggingFaceTB/smollm-corpus, Cosmopedia-v2 | `3ba9d605774198c5868892d7a8deda78031a781f` | Shard 1 acquired; screening pending |

Protected-screened usable supply: web 75 = 76,099,829 targets; notebook 6 = 64,808,539; math 2 = 98,221,774. These are pre-selection pool counts, not all unreserved capacity. Raw encoded totals must not be substituted for usable fresh targets.

A math-screening attempt failed on a mistaken heldout filename. Its artifacts were preserved; the correct immutable heldout was used in a completed rerun of all 556,041 protected queries. No screening standard was relaxed. Web 74 yielded only 18,829 targets because almost all candidate families were already protected; that rejection was preserved.

## Storage and recovery

A bounded copy job is moving 76 older generations from three completed phases to tank (343,410,076,650 logical bytes). Both source and archive receive native full-state verification. Latest, best and the three most recent generations are excluded. Copying alone does not reclaim NVMe; cutover remains a separately verified step.

The user subsequently requested a sensible periodic history rather than every intermediate snapshot. Only the not-yet-started bridge and subsequent phases have a prospective native retention policy staged: keep latest, previous, best, terminal and approximately every tenth 5M-target periodic boundary (50M). Actual milestone counters come from native packed group offsets. Existing phase configurations and historical generations are unchanged. This keeps the normal recovery cadence while bounding historical retention. Native retention/recovery checks passed nine CPU test cases; schema validation also passed. Actual future runtime retention remains unobserved until that phase runs.

## Supply expansion and v2 work

The current notebook dataset contains 11 shards. A census of one pinned shard found 78,247,136 raw targets in documents longer than 4K, in addition to 73,817,785 short-document targets. Long-document totals are not deduplicated or protected-screened usable supply. Any contiguous segmentation policy must explicitly preserve source-family exclusion, no repeated target positions, 4K shape limits and new provenance.

The previously acquired codeparrot/github-code-clean corpus is locally present, with a completed build and per-row license/language qualification; it is not automatically fresh. Its prior consumption/protection must be reconciled before admission. Further shards of the same source offer a candidate alternative to exhausting notebooks. A notebook-to-code proportion change would be recorded as a new mixture in a later segment, not slipped into the active phase.

New authorized candidate areas are being acquired/reviewed separately: NASA systems engineering, NIST community resilience, Census factual reference data, and a bounded train-only PG-19 cultural-book pilot. The primary PG-19 provider cautions against general-purpose use because of historical style/bias; historical books should be a capped cultural component, not a source of current scientific facts. Cynefin material carries attribution/share-alike obligations and remains separate for rights/provenance review. No new domain source has yet been admitted to training.

Priorities for v2:

1. Native append preparation that authenticates and reuses the immutable prefix instead of re-tokenizing all accumulated data each segment.
2. Prepare enough verified fresh data ahead of the GPU; distinguish raw, qualified, screened, reserved, packed and consumed inventories.
3. Keep optimizer-update semantics explicit when changing target-group size; preserve Adam step and scheduler lineage.
4. Measure padding and reporting costs in controlled comparisons; do not infer speedups from peak FLOPs or sorting already present in the collator.
5. Separate validation-loss health from untouched behavioral/factual and n-gram-memory evaluations. Preserve source-level heldouts for added domains.
6. Record cadence/retention decisions and verify real checkpoint recovery, archive cutovers and terminal outcomes.
7. Preserve failures, low-yield source decisions, exact source revisions, exclusions, actual instruction proportions and any future mixture changes.

Primary source references: [PG-19](https://github.com/google-deepmind/pg19), [NASA handbook record](https://ntrs.nasa.gov/citations/20170001761), [NIST resilience guide](https://www.nist.gov/publications/community-resilience-planning-guide-buildings-and-infrastructure-systems-volume-i), [NIST reuse terms](https://www.nist.gov/open/license), [Census state codes](https://www.census.gov/library/reference/code-lists/ansi/ansi-codes-for-states.html), [Cynefin terms](https://cynefin.io/wiki/Terms_of_Use).

## Verified handoff update, 00:18 UTC

The 100M successor reached step 22,987 / 1,317,523,826 targets. Its first verified post-update full-state checkpoint is step 22,970 / generation 2, manifest SHA-256 `5e01918d7113295844958209d0d801ac056d2766dbf5976a69a0db0d0ee00256`, saved at 00:15:56 UTC. A 315-second window measured 18,823 targets/s including saves. The sole trainer PID is 2032776. These are operator-observed results, not a terminal report.

## Subsequent preparation update

The bridge selected 25,005,482 fresh targets (web 8,752,741; notebooks 7,501,724; math 3,750,619; Smol instructions 3,750,101; Cosmopedia 1,250,297). It was packing at that observation; the later 00:36 update records completed packing. No bridge optimizer update is claimed. The following 180M ceiling remains dependent on screened replenishment.

NASA text, Census state codes and 16 primary PG-19 train books were acquired with hashes; all selected book dates are 1849–1916. Both NIST download attempts returned HTTP 403, so NIST is not acquired. Codeparrot/github-code-clean shard 50 at revision `c48d40f9e70f0196f8236901ee35807f7d6c44c0` was acquired with SHA-256 `50f2550c8e19ad69b335212ed36be071fc8e01eff95a9d4901feae96c081156f` and is being qualified/screened. Existing native row checks restrict licenses to MIT/Apache-2.0/BSD-2-Clause/BSD-3-Clause/ISC, retain allowed languages and reject credential/notice exceptions. The inherited web-score phrase in its initial receipt is explicitly corrected in final-stage metadata; executed filtering is the native code policy. No new domain or code source has entered training.

### 00:36 UTC operational follow-up

The midnight phase reached applied step 23,141 / 1,337,833,198 Engram targets at 00:35:58 UTC. Its verified full-state checkpoint was step 23,122, generation 6; the latest 315-second wall window yielded 18,835 targets/s. NVMe had 328.7 GiB free. The predawn bridge is packed with 25,005,482 fresh targets over 190 updates, with identical historical tokens/groups and zero consumed-family overlap; its supervisor still waits for the midnight terminal checkpoint. Sunrise remains an unselected 180M ceiling waiting for final web/Cosmopedia protection screening.

Archive copying has verified 36 of 76 completed-run generations; no source space has yet been reclaimed. The supervised cutover waits for completed copy verification and checks open-file access before releasing only verified duplicate NVMe copies. The archive mapping is `checkpoint-copy-20261106-v1/original-to-archive.json`; do not rewrite or confuse it with the previous 187-generation mapping.

The original 12B-token mixture receipt records a single maximum exposure, but scheduled token positions are not the same as applied supervised targets. Recovering its unused tail is an opportunity, not verified usable inventory: it requires exact dense checkpoint cursor mapping, subsequent consumed/scheduled family exclusions and all heldout protection. Do not relax the present conservative baseline-family exclusion based on capacity arithmetic.

Code shard 50 yielded 2,243,703 candidate targets before its final explicit protected-query pass. Its reused screening metadata contains an incorrect web source label; code document IDs, pinned acquisition, row and repository-family identities remain available. Preserve the original receipts and attach the explicit correction record before any future selection. No code or cultural pilot has been admitted to the pinned training mix.

At 00:36:43 UTC, applied step 23,148 reached 1,338,752,554 Engram targets. Including the inherited dense phase, this is 3,419,127,338 targets, just beyond 10× backbone parameters; it is not 10× Engram-only exposure or a model-quality milestone.

## Performance follow-up

See the [B70 performance summary](b70-performance-20261106.md) for the bounded padding comparison, trace limitations, verified return to production and the next upstream kernel hypothesis. Detailed operator artifacts remain local.
