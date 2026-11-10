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

## Continuation progress through 2.516B+ Engram targets and 160M / 95M segment staging

Subsequent finite continuations on the pinned nightly XPU runtime (`2.16.0.dev20261105+xpu`) advanced the campaign past **2.516B Engram-phase valid targets** (`4.597B` combined exposure targets including the `2,080,374,784` inherited dense-backbone targets):

- **Post-reboot 14M continuation:** Completed 107 optimizer updates (`14,005,146` valid targets) to step **31,422** / `2,429,314,666` Engram targets; cold-verified full-state checkpoint SHA-256 `b7d521277c4abe1cbec7a55b5658b3b2e135689ad2693c0fcbd1c8533526f717`, terminal validation loss **2.5700909473**.
- **Subsequent 7M bridge continuation:** Completed 54 optimizer updates (`7,004,505` valid targets: `2,450,694` FineWeb-Edu 4+, `2,102,033` notebooks, `1,051,449` FineMath 4+, `1,050,043` Tulu-3 instructions, `350,286` Cosmopedia v2) to step **31,476** / `2,436,319,171` Engram targets. Cold-verified initial state (`step 31,422`, SHA-256 `730161f5d5a7beb2ee7eedc51cbc2476289beb4b2ef2d8eafdf84b761191799b`), intermediate 5M save (`step 31,460`, SHA-256 `b1aa262959a72e1800a97a365e71e0b798a239bfaeff4d8dede71d12ef54196a`), and terminal full-state checkpoint (`step 31,476`, SHA-256 `ed793f4ab87d1bc61d192867338fb42cec0a4a857c26edb052ec5a913303ea23`), with terminal validation loss improving to **2.5687490960** (`21,887.7` optimizer valid targets/s).
- **Active 160M continuation (`devmind-engram-after7m-160m-131k-nvme-20261106-v1`):**
  - Bound to `step_00031476_gen_000003` (`ed793f4ab87d1bc61d192867338fb42cec0a4a857c26edb052ec5a913303ea23`); cold-verified initial child checkpoint `step_00031476_gen_000001` (`01fc86bfbc116b902a6184d90634a0a6e25cc2659dbc63ac9c624e7f61bde89b`).
  - Packs **160,002,769 new targets** (`162,913` whole documents / `1,213` optimizer updates $\to$ step **32,689** / **2,596,321,940** Engram targets): `56,000,151` FineWeb-Edu 4+ (35.0%), `48,000,026` notebooks (30.0%), `24,000,477` FineMath 4+ (15.0%), `2,000,208` OpenCodeInstruct + `22,000,905` Tulu-3 instructions (`24,001,113`, 15.0%), and `8,001,002` Cosmopedia v2 (5.0%).
  - Already passed **step 32,083 / 2,516,383,537 Engram targets** (`+80.06M` targets into the segment), with validation loss improving to **2.5684862384** at step 31,600 (`step_00031600_gen_000005`, SHA-256 `9d1a1aa2ed2170d7055ca7ab158f954646419c9932c781414f37042f6a147f83`) and end-to-end throughput reaching **20,254.9 valid targets/s (+6.9% vs 14M run)**.
- **Pre-staged 95M continuation (`after-160m-95m-append-4k-v1`):**
  - Pre-packed and verified on Tank (`native_data_manifest_sha256: 45164058035aa8830352efc2a9f7a17911bea74c30f2e1c8d6debe41937168c8`, `95,003,026` new targets / `96,718` documents / `721` updates $\to$ step **33,410** / **2,691,324,966** Engram targets; armed via `devmind-after160m-95m-handoff-20261106-v1.service` for immediate zero-idle handoff from step 32,689): `33,250,766` FineWeb-Edu 4+, `28,500,897` notebooks, `14,250,687` FineMath 4+, `1,350,196` OpenCodeInstruct + `12,900,065` Tulu-3 instructions, and `4,750,415` Cosmopedia v2, with `checkpoint.every_tokens` increased from `5,000,000` to `25,000,000` to eliminate 80% of periodic checkpoint pause overhead.

### Qualified dataset inventory and 16-worker parallel screening pipeline

All newly acquired and qualified shards preserve the unchanged **35% Web / 30% Notebooks / 15% FineMath / 15% Instructions / 5% Cosmopedia** mixture, whole-document 4K (`<=4096` tokens with EOS, no truncation), `NORMALIZER_V3` structure cleaning, permissive license gates, 40-pool prior-index MinHash LSH ($\ge 0.65$) deduplication, and 1,406,036-query protected benchmark/heldout screening:

| Pillar | Dataset & Pinned Revision | Shard / Interval | Raw SHA-256 (prefix) | Qualified Docs | Qualified Targets |
|---|---|---|---|---:|---:|
| **Web (35%)** | `HuggingFaceTB/smollm-corpus` (`3ba9d605...`) | `fineweb-edu-dedup/train-00080-of-00234.parquet` `[150000, 812684)` | `abbe6bc1260630c1...` | 74,685 | 61,041,985 |
| **Web (35%)** | `HuggingFaceTB/smollm-corpus` (`3ba9d605...`) | `fineweb-edu-dedup/train-00081-of-00234.parquet` | `02d188d2c0b3eb29...` | 91,633 | 76,659,215 |
| **Web (35%)** | `HuggingFaceTB/smollm-corpus` (`3ba9d605...`) | `fineweb-edu-dedup/train-00082-of-00234.parquet` | `54b19f880cc23347...` | 91,951 | 76,809,281 |
| **Notebooks (30%)** | `codeparrot/github-jupyter` (`495a499a...`) | `data/file-000000000000.json.gz`..`file-000000000024.json.gz` (25 files) | `1d948daa...`..`be628258...` | 47,273 | 59,295,033 |
| **Notebooks (30%)** | `codeparrot/github-jupyter` (`495a499a...`) | `data/file-000000000025.json.gz`..`file-000000000032.json.gz` (8 files) | `70e6b9f5...`..`bd88c857...` | 14,119 | 17,344,378 |
| **FineMath (15%)** | `HuggingFaceTB/finemath` (`e92b25a6...`) | `finemath-4plus/train-00004-of-00064.parquet` (+ shards 5–6 acquired) | `9644be6589159f9a...` | 91,364 | 95,726,331 |
| **Instructions (15%)** | `nvidia/OpenCodeInstruct` (`8f3ba5ba...`) | `data/train-00000-of-00050.parquet` (`[0, 100000)`) | `342757e0c6b706c8...` | 6,736 | 2,815,235 |
| **Instructions (15%)** | `nvidia/OpenCodeInstruct` (`8f3ba5ba...`) | `data/train-00001` & `train-00002-of-00050.parquet` | `2e822b1c...`, `3fe342d7...` | 3,494 | 1,397,137 |
| **Instructions (15%)** | `nvidia/OpenCodeInstruct` (`8f3ba5ba...`) | `data/train-00003`..`train-00010-of-00050.parquet` (8 shards) | `19aed4cc...`..`c887eb84...` | 26,744 | 11,092,182 |
| **Instructions (15%)** | `allenai/tulu-3-sft-mixture` (`b14afda6...`) | `data/train-00000-of-00006.parquet` (`oasst1` + `wildchat`) | `41d4524345443ccc...` | 42,701 | 49,309,394 |
| **Instructions (15%)** | `allenai/tulu-3-sft-mixture` (`b14afda6...`) | `data/train-00001-of-00006.parquet` (`oasst1` + `wildchat`) | `c612164eabfacb99...` | 36,218 | 46,767,808 |

### DevMind v2 Recipe & Data-Flow Blueprint

For **DevMind v2**, the data flows, screening optimizations, and kernel improvements developed during this continuation should be integrated from step 0 rather than bolted on mid-campaign:

1. **Cluster-level notebook deduplication instead of repository-name collapse:**
   - Earlier `codeparrot/github-jupyter` screening scripts grouped union-find components by `family_id` (`repo_name`), which collapsed multi-notebook educational/data-science repositories (`10–50+` distinct notebooks per repo) down to a single notebook and discarded `91–94%` of valid targets (`51.07M` encoded $\to$ `2.79M` retained).
   - Deduplicating by **exact content + within-shard/cross-shard MinHash LSH ($\ge 0.65$) cluster** while still blocking any cluster that hits a prior pool, protected query, heldout repository, or content-review hold retains **~75% (`76.64M` targets across files 0–32)** of distinct, high-quality notebooks.
   - For v2, combine `HuggingFaceTB/issues-kaggle-notebooks` (`kaggle` config, 11 shards, `~654M` clean targets), `codeparrot/github-jupyter` (all 33 files `0–32`, `~76.6M` clean targets), and `jupyter-agent/jupyter-agent-dataset` (`10a8dd461bb6c580fa25b83cd3b2f6810f1d6385`, Apache-2.0 executable notebook agentic traces with `tool_calls`) from the start of the corpus build.
2. **Execution-verified Python coding & agentic trajectories in the Instruction pillar:**
   - `nvidia/OpenCodeInstruct` (`8f3ba5bafe4d6e8db46082cf7ae6741bc370604d`, 50 shards, CC-BY-4.0) enforces `average_test_score == 1.0`, 10 passing unit tests with 10 distinct AST-parsed `assert` statements, balanced code fences, and 5/5 LLM judgements across `requirement_conformance`, `logical_correctness`, and `edge_case_consideration`. Scaling across all 50 shards in v2 provides **~70M+ execution-verified Python coding targets**.
3. **16-worker parallel SQLite/MinHash qualification & pre-sharded protected query cache:**
   - Replacing single-worker sequential `screen_queries` over 40 prior SQLite indexes and 1.41M protected queries with a 16-worker `ProcessPoolExecutor` (`mp_context='spawn'`) and pre-sharded `queries-{0..15}.jsonl` reduced whole-shard qualification wall time from **3–4 hours to 3–9 minutes per shard** on Threadripper, enabling continuous multi-hundred-million-token runway preparation ahead of GPU training.
4. **Runtime & checkpoint cadence defaults for v2:**
   - Adopt `padding_multiple=64` (measured **+3.18%** steady throughput on B70 XPU when paired with vectorized `TokenNgramMemory` diagnostics in [Tiny Sparse Lab PR #335](https://github.com/supernovae/tiny-sparse-lab/pull/335)), skip redundant per-microbatch `/proc` RSS/meminfo syscalls inside `MemoryMonitor.sample()` when native XPU/CUDA peak counters are active, and set `checkpoint.every_tokens` to `25,000,000–50,000,000` (`+2.8%` end-to-end wall-clock gain over 5M checkpointing).

## Continuation progress through 6.766B Engram targets (8.847B combined) and 2x B70 multi-GPU upgrade (2026-11-10)

Subsequent finite continuations completed Segments 1 through 16 (`step 31,422 -> 64,315`, reaching **6,766,391,105 Engram targets** / **8,847,422,540 combined exposure targets** — **82.76%** of the `8,176,203,776` Engram reference target — and a new campaign-best validation loss of **2.5383300** at step `64,315`), including a host hardware upgrade adding a **second Intel Arc Pro B70 GPU** (`868023e2-0000-0000-2300-000000000000` alongside `868023e2-0000-0000-e300-000000000000`) and **96 GB system RAM**:

| Stage / Segment | Run ID | Step Range ($\Delta$ Steps) | New Targets | Cumulative Engram Targets | Best Val Loss (Step) | Terminal / Latest Checkpoint SHA-256 |
|---|---|---|---:|---:|---|---|
| Bridge B (`after7m-160m`) | `devmind-engram-after7m-160m-131k-nvme-20261106-v1` | `31,476 -> 32,689` (`1,213`) | `160,002,769` | `2,596,321,940` | `2.5664236` (`32,500`) | `29e07b27daad9be7768df6415b90d53d7acc0d422e5816154beaea8af1faa74a` |
| Bridge C (`after160m-95m`) | `devmind-engram-after160m-95m-131k-nvme-20261106-v2` | `32,689 -> 33,410` (`721`) | `95,003,026` | `2,691,324,966` | `2.5641917` (`33,410`) | `d64ee2aa3a73f5141d53e74e2ea84a22c47754cd5273ae0327cdb4fcbed1076e` |
| Segment 1 (`after95m-300m`) | `devmind-engram-after95m-300m-131k-nvme-20261106-v3` | `33,410 -> 35,685` (`2,275`) | `300,004,270` | `2,991,329,236` | `2.5617812` (`35,500`) | `7d3cf04da619b65e176ea9f31f67cf1975318298f75225098c66e6fc41d68190` |
| Segment 2 (`after300m-300m`) | `devmind-engram-after300m-300m-resume-131k-nvme-20261107-v3` | `35,685 -> 37,961` (`2,276`) | `300,004,789` | `3,291,334,025` | `2.5602396` (`37,900`) | `54c0382285861f76bfd9bcac2a595296b6b202ae651f9dfc8e40af4989f0904f` |
| Segment 3 (`after600m-300m`) | `devmind-engram-after600m-300m-131k-nvme-20261106-v1` | `37,961 -> 40,237` (`2,276`) | `300,005,751` | `3,591,339,776` | `2.5596509` (`38,300`) | `d7dea3df7b5a6199fb0e18da6e594d8afcf0d4db6e95e18a2ac20557cb61c6a2` |
| Segment 4 (`after900m-300m`) | `devmind-engram-after900m-300m-131k-nvme-20261107-v1` | `40,237 -> 42,513` (`2,276`) | `300,005,332` | `3,891,345,108` | `2.5564988` (`42,513`) | `a642f8d5dd4b1a71e4fe0bc1edf4b6839d10c6863b451fc19403de89ca844019` |
| Segment 5 (`after1200m-300m`) | `devmind-engram-after1200m-300m-131k-nvme-20261108-v1` | `42,513 -> 44,789` (`2,276`) | `300,004,286` | `4,191,349,394` | `2.5536102` (`43,100`) | `8e375578b5a9aaf21d9df671718bd7bbc8dd1a1d87b8451e31871d0e5f459265` |
| Segment 6 (`after1500m-300m`) | `devmind-engram-after1500m-300m-131k-nvme-20261108-v1` | `44,789 -> 47,064` (`2,275`) | `300,002,788` | `4,491,352,182` | `2.5497895` (`46,600`) | `c4b0ba141375ba653d61424f9acf496f07fbc33548906f033f4d9565d02ad195` |
| Segment 7 (`after1800m-300m`) | `devmind-engram-after1800m-300m-131k-nvme-20261108-v1` | `47,064 -> 48,581` (`1,517`) | `200,004,450` | `4,691,356,632` | `2.5490339` (`48,581`) | `72c4b989c2d782bf5e2ec570534b7843b24a0191d40d51af88d0f47027613607` |
| Segment 8 (`after2000m-300m`) | `devmind-engram-after2000m-300m-131k-nvme-20261109-v1` | `48,581 -> 50,856` (`2,275`) | `300,002,903` | `4,991,359,535` | `2.5444357` (`50,400`) | `91a44b0a8c745f74c31f752ecd0c8c2b81457b728c48099fa6541158a8ad03e3` |
| Segment 9 (`after2300m-300m`) | `devmind-engram-after2300m-300m-131k-nvme-20261109-v1` | `50,856 -> 52,183` (`1,327`) | `175,001,690` | `5,166,361,225` | `2.5444605` (`51,100`) | `a535c18d8721300da7a0f5ceaf7251791a0deaaab9cef512abeb7c502f48c9ac` |
| Segment 10 (`after2600m-300m`) | `devmind-engram-after2600m-300m-131k-nvme-20261109-v1` | `52,183 -> 53,131` (`948`) | `125,004,791` | `5,291,366,016` | `2.5439336` (`52,800`) | `35c7331464307f2a5696bd1a96c4bc94b810999e5df0628ffa479491460792d4` |
| **Segment 11 (`after2900m-300m`)** | `devmind-engram-after2900m-300m-131k-nvme-20261109-v1` | `53,131 -> 54,458` (`1,327`) | `175,004,895` | `5,466,370,911` | **`2.5426250`** (`53,800`) | `619c7b56950146b5816db2eac55cc27bd07c69353e6eb800b9a78c483bbcf858` |
| Segment 12 att. 1 (`after3200m-300m`) | `devmind-engram-after3200m-300m-131k-nvme-20261109-v1` | `54,458 -> 54,690` (`232` ckpt) | `30,606,053` | `5,496,976,964` | `2.5436645` (`54,500`) | `be152cd1d92792d0c38a238f57b28c105653a4b5cf5bf422fd5dcc8dea768dd4` |
| **Segment 12 2x B70 resume** | `devmind-engram-after3200m-300m-resume-131k-nvme-20261109-v1` | `54,690 -> 56,353` (`1,663`) | `219,398,805` | `5,716,375,769` | `2.5435451` (`56,353`) | `2bda8216b9859775f9d7a127cb1313a2a862dc2c0b543fae66667f8035d9bc8e` |
| **Segment 13 (`after3500m-300m`, 2x B70)** | `devmind-engram-after3500m-300m-131k-nvme-20261109-v1` | `56,353 -> 58,058` (`1,705`) | `225,002,571` | `5,941,378,340` | **`2.5425144`** (`56,800`) | `a87d31bc5c7931dd956339aed70167e11e4c3b7c76265b00147ebf8613dfd8ef` |
| Segment 14 att. 1 (`after3725m-300m`) | `devmind-engram-after3725m-300m-131k-nvme-20261110-v1` | `58,058 -> 58,100` (`42` ckpt) | `5,537,370` | `5,946,915,710` | `2.5425456` (`58,100`) | `c637cc5adcf83242202f5bfa6eb4bd5a94a7e5f2fc778a92c1c1526b089f8109` |
| **Segment 14 2x B70 resume** | `devmind-engram-after3725m-300m-resume-131k-nvme-20261110-v1` | `58,100 -> 60,333` (`2,233`) | `294,465,003` | `6,241,380,713` | **`2.5414132`** (`58,900`) | `6c4330314af24aafc3040bcb95a4c76d8fd5b55d68dca151f624261fb0cf5bee` |
| **Segment 15 (`after4025m-300m`, 2x B70)** | `devmind-engram-after4025m-300m-131k-nvme-20261110-v1` | `60,333 -> 62,039` (`1,706`) | `225,007,165` | `6,466,387,878` | **`2.5392119`** (`61,700`) | `af7d1dee76ae0dc9e2063809ac347707ef9d1a35b86c29ef0256d766001bab19` |
| Segment 16 att. 1 (`after4250m-300m`) | `devmind-engram-after4250m-300m-131k-nvme-20261110-v1` | `62,039 -> 62,400` (`361` ckpt) | `47,611,902` | `6,513,999,780` | `2.5400154` (`62,400`) | `d6093b3674e2ec6df35f4badf087ff6ab0d04a03c9ae11b40e03990ab1a7515d` |
| **Segment 16 2x B70 resume** | `devmind-engram-after4250m-300m-resume-131k-nvme-20261110-v1` | `62,400 -> 64,315` (`1,915`) | `252,391,325` | `6,766,391,105` | **`2.5383300`** (`64,315`) | `efa5b61f28bef79a8b06395ec328dbe63c391674b1dd1f2539e5f73ece1bd980` |

- **Additional qualified source expansions supporting Segments 1–21 (`8.176B` Engram / `10.257B` combined targets):**
  - **Notebooks (`30%` in Stages 1–15, `1.888B` total unique notebook tokens):** `HuggingFaceTB/issues-kaggle-notebooks` (`ef882ad1ed8274340e8f9bac087c903f2f75396`, shards `0–10`), `codeparrot/github-jupyter` (`a9be1d2d9b8bf5cf1fb7f8ffab9dc431fb0fd031`, files `0–32`), `bigcode/the-stack-jupyter-parsed-filtered` (`bigcode/jupyter-parsed`, `eed65c314469b51419d08fb2ff7ee41e448774d4`, shards `0–45`), `secmlr/starcoderdata` (`0a11b2a003eb39252c919f3d28f3d26f412bc3d7`, `jupyter-structured-clean-dedup` & `jupyter-scripts-dedup-filtered`), `jordangong/jupyter-scripts-smollm3` (`98dcfd99ae3c6cf0f43e3d07d6a10a570d0da262`, shards `0–419`), and `MetaKaggle Code v184` (`trial1000-v1`).
  - **Web (`35%` in Stages 1–15, `50%` in Stages 16–21):** `HuggingFaceTB/smollm-corpus` (`fineweb-edu-dedup`, `3ba9d605774198c5868892d7a8deda78031a781f`, shards `69–112`, `int_score >= 4`, English) and `HuggingFaceFW/finewiki` (`en`, `20261106-v1`).
  - **FineMath (`15%` in Stages 1–15, `20%–35%` in Stages 16–21):** `HuggingFaceTB/finemath` (`finemath-4plus`, `e92b25a616738fe95dc186b64dfb19f9c8525594`, shards `0–15`, `int_score >= 4`).
  - **Instructions (`15%` in Stages 1–15, `18%` in Stages 16–21):** `nvidia/OpenCodeInstruct` (`8f3ba5bafe4d6e8db46082cf7ae6741bc370604d`, shards `0–49`, `generic_python_verified_tests`), `HuggingFaceH4/ultrachat_200k` (`8ebe7fc305c02c2adca58c8bf303b1451be2f97f`, `train_sft` & `train_gen`), `HuggingFaceTB/smoltalk` (`smol-magpie-ultra`, `5feaf2fd3ffca7c237fc38d1861bc30365d48ffa`, shards `0–5`), `allenai/tulu-3-sft-mixture` (`8ab293f29a8f14e2e0e7fd97a63e2f5b4a13d920`, Permissive-2.0 subset, shards `0–1`), and `gretelai/synthetic_text_to_sql` (`Apache-2.0`).
  - **Cosmopedia & Technical Reference (`5%` in Stages 1–15, `12%` in Stages 16–21):** `HuggingFaceTB/smollm-corpus` (`cosmopedia-v2`, `3ba9d605774198c5868892d7a8deda78031a781f`), Python 3.14 Official Documentation (`PSF-2.0`), IETF RFCs (`rfc0001–rfc9699`), and PostgreSQL 17.2 Official Documentation (`PostgreSQL License`).
- **Checkpoint retention & NVMe storage policy:**
  - Pruned 404 of 449 intermediate archived checkpoints on `/tank`, retaining 45 checkpoints (`10.0%`, evenly spaced every `~120M` tokens from `2.47M` to `5.442B` tokens) plus all run-terminal checkpoints on NVMe, freeing **1,695.92 GiB** on `/tank`.
  - Completed grandparent runs on NVMe (`prior_run_to_trim`) replace their local `data/train.npy` copy with a symlink to the immutable SHA-256-verified `/tank` cache while keeping the immediate `parent_run / 'data/train.npy'` as a regular file for `load_continuation` verification, maintaining **370–410 GiB free on NVMe** throughout the `6.4B -> 8.2B` target range.
- **Prospective Final-Phase Mixture (`devmind-engram-final-rebalanced-phase-20261110-v1`, `6.466B -> 8.176B` Engram targets):**
  - At `step 62,039` (`6,466,387,878` Engram targets / `8,547,419,313` combined exposure targets), all bulk permissive notebook sources under the strict whole-document 4K and no-image gates reached exhaustion (`1,883,203,267` unique notebook tokens consumed; `5,489,113` unreserved targets remaining).
  - Authorized prospective final-phase identity **`devmind-engram-final-rebalanced-phase-20261110-v1`** consumes the final `5.0M` unreserved notebook targets in Stage 16 (`after-4250m-300m-append-4k-v1`, completed at `step 64,315` / `6,766,391,105` Engram targets with a new campaign-best validation loss of **`2.5383300`**) and reallocates the `30%` notebook quota across `web_4plus`, `finemath`, `instruction_ultrachat`, and `cosmopedia_v2` for Stages 16–21 (`6.466B -> 8.176B` Engram targets / `10.257B` combined exposure targets; **Segment 17** reached **`2.5382118` validation loss at `step 64,400`**):

| Final-Phase Stage | Run ID | Target Addition | Cumulative Engram Targets | Combined Exposure Targets | Status |
|---|---|---:|---:|---:|---|
| **Stage 16 (`after-4250m-300m`)** | `devmind-engram-after4250m-300m-resume-131k-nvme-20261110-v1` | `300,003,227` | `6,766,391,105` (`82.76%`) | `8,847,422,540` | **Completed (`step 64,315`, val loss `2.5383300`)** |
| **Stage 17 (`after-4550m-300m`)** | `devmind-engram-after4550m-300m-131k-nvme-20261110-v1` | `300,002,477` | `7,066,393,582` (`86.43%`) | `9,147,425,017` | **Training on 2x B70 GPUs (`step 64,790+`, val loss `2.5382118` at `64,400`)** |
| **Stage 18 (`after-4850m-300m`)** | `devmind-engram-after4850m-300m-131k-nvme-20261110-v1` | `300,002,889` | `7,366,396,471` (`90.10%`) | `9,447,427,906` | **Packed & verified on `/tank`; queued for zero-idle GPU handoff** |
| **Stage 19 (`after-5150m-300m`)** | `devmind-engram-after5150m-300m-131k-nvme-20261110-v1` | `~300,000,000` | `~7,666,396,471` (`93.76%`) | `~9,747,427,906` | **Staged in `campaign_orchestrator.py`** |
| **Stage 20 (`after-5450m-300m`)** | `devmind-engram-after5450m-300m-131k-nvme-20261110-v1` | `~300,000,000` | `~7,966,396,471` (`97.43%`) | `~10,047,427,906` | **Staged in `campaign_orchestrator.py`** |
| **Stage 21 (`after-5750m-210m`)** | `devmind-engram-after5750m-210m-131k-nvme-20261110-v1` | `~210,000,000` | **`~8,176,396,471` (`100.00%`)** | **`~10,257,427,906` (`100.01%`)** | **Staged in `campaign_orchestrator.py` (terminal cold verification)** |

### Upstream Tiny Sparse Lab PRs Enabling DevMind v2

- **[PR #333](https://github.com/supernovae/tiny-sparse-lab/pull/333) (merged):** Preserve checkpoint retention policy during budget-extension comparisons.
- **[PR #334](https://github.com/supernovae/tiny-sparse-lab/pull/334) (merged):** Native `PreparedPrefix` verified prefix reuse for incremental corpus tail-appends without re-encoding historical prefix tokens.
- **[PR #335](https://github.com/supernovae/tiny-sparse-lab/pull/335) (merged):** Vectorized multi-stream `TokenNgramMemory` diagnostics and shared shifted-input buffers (**+1.64%** steady throughput at `padding_multiple=128`, **+3.18%** with `padding_multiple=64`).
- **[PR #338](https://github.com/supernovae/tiny-sparse-lab/pull/338) & [PR #340](https://github.com/supernovae/tiny-sparse-lab/pull/340) (merged):** Native multi-GPU microbatch-parallel `PyTorchEngine` execution and fail-closed `MultiDeviceLease` physical device lock enforcement.
- **[PR #342](https://github.com/supernovae/tiny-sparse-lab/pull/342) (open):** Multi-GPU device index enumeration (`0..device_count()-1`) and XPU/CUDA/ROCm physical UUID discovery in `discover_runtimes()`.
