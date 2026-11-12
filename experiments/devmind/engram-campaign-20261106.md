# DevMind Engram continuation — operator evidence, 2026-11-06

After training stopped on October 29, we resumed DevMind as a private research run with Engram memory added. This page is our dated notebook for that run. We publish no weights or source text here.

## Reading this historical record

Each section records what we saw at the time it was written. These are observations from a run in progress: validation loss tracks training health, not reasoning or factual accuracy, and the later stages in the final-phase table are plans unless marked completed.

The latest training snapshot is from November 10. Segment 16 had finished at 6,766,391,105 Engram targets, and Segment 17 was running at step 65,832.

The notebook dataset revision is [the March 19, 2025 Hub commit](https://huggingface.co/datasets/HuggingFaceTB/issues-kaggle-notebooks/commit/ef882ad1ed8274340e8fc9bac087c903f2f75396) listed in the original source table. A later catalog entry dropped one character of the hash; we fixed the typo, and the source we used is unchanged.

## Budget and lineage

Several counters appear below. Keep them apart:

- **Backbone and original budget.** The original EXP-1 manifest specifies 341,885,952 backbone parameters and 10,256,578,560 training targets (30× backbone size).
- **Dense backbone phase.** The nominal reference is 2,080,374,784 targets (15,872 steps × 131,072). The actual packed count was 2,081,031,435 tokens. Totals using that second number are labeled separately.
- **Engram phase.** Engram targets are counted on top of the dense phase. Reaching the original exposure target means 8,176,203,776 Engram targets. The later memory-first design never set a separate final Engram budget.
- **12B** was the corpus-preparation goal, not an extra training budget.

On the first November 6 check, the 50,003,192-target phase had finished at step 22,932 / 1,310,272,432 Engram targets. Its last full-state checkpoint is `step_00022932_gen_000013` (manifest SHA-256 `4131a159164aadf1346afbf2aea95ea4d1f86dcddf9e205e5e182ef3b9e31e86`), with validation loss 2.587253632462752. The next phase, 100,003,501 targets, had started applying updates and ends at step 23,691 / 1,410,275,933 targets. Its outcome was still open at that point; later progress is recorded below.

## Observed execution configuration

- Kybern Model Lab commit `a2fdb25ed82519f3c65f1a9752aa86bbdedd2bcc`.
- Intel B70, private Intel 26.40 stack, PyTorch 2.15.0+xpu, Python 3.14, bf16.
- 4,096-token context; at most four documents per microbatch; 131,072-target optimizer groups.
- Compiled transformer blocks and output head/loss, with dynamic shapes. Activation checkpointing off; optimizer foreach off.
- Per-microbatch shape limits: 8,192 padded slots and 16,777,216 attention cells.
- Adam and RNG state, the consumed token/document/group prefix and the frozen segment boundaries all carry over. Trunk LR floor 1e-5, memory-table multiplier 5. No warmup restart or reheating.
- One GPU lease and one writer. Active data and checkpoints on NVMe; older generations archived separately.
- Recent sustained windows ran at roughly 18.4–18.8K real supervised targets/s, including saves. This is the rate we observed on this run.

## November 6 data and next queue (historical)

The current phase keeps the mixture at 35% FineWeb-Edu score-4+, 30% notebooks, 15% FineMath, 15% instructions and 5% Cosmopedia. In exact targets that is 35,000,626 / 30,001,127 / 15,000,211 / 15,000,600 / 5,000,937. All instructions in this phase come from Smol-SmolTalk, which was already approved, so the instruction pillar is unchanged. We still train on all tokens and keep the same role serialization.

Packing confirmed that the historical tokens and optimizer-group boundaries are identical, that no consumed family overlaps, and that the phase continues from full state. The 100M phase adds 96,764 fresh documents and 759 optimizer updates.

Next in the queue:

- A 25,005,482-target bridge, packed from data we had already screened. We chose it over a 60M ceiling so we wouldn't wait on the larger Cosmopedia pool.
- A 180M-ceiling phase, waiting for notebook 7, web 76 and Cosmopedia 1 screening.

Both are installed as supervisors; neither had trained at this point.

Pinned replenishment sources:

| Source | Revision | Current acquisitions |
|---|---|---|
| HuggingFaceTB/smollm-corpus, FineWeb-Edu dedup | `3ba9d605774198c5868892d7a8deda78031a781f` | Web 75 screened; web 76 acquired and preparing |
| HuggingFaceTB/issues-kaggle-notebooks | `ef882ad1ed8274340e8fc9bac087c903f2f75396` | Notebooks 6 and 7 screened |
| HuggingFaceTB/finemath | `e92b25a616738fe95dc186b64dfb19f9c8525594` | FineMath-4plus shard 2 screened |
| HuggingFaceTB/smollm-corpus, Cosmopedia-v2 | `3ba9d605774198c5868892d7a8deda78031a781f` | Shard 1 acquired; screening pending |

Usable supply after protected screening: web 75 = 76,099,829 targets; notebook 6 = 64,808,539; math 2 = 98,221,774. These are pool sizes before selection, and some of each is already reserved. Count usable fresh targets, not raw encoded totals.

One math-screening attempt failed because it pointed at the wrong held-out file. We kept its artifacts and reran all 556,041 protected queries against the correct held-out file; the rerun finished. We kept the screening standard the same. Web 74 yielded only 18,829 targets because nearly all its candidate families were already protected, and we kept that rejection on record.

## Storage and recovery

A copy job is moving 76 older generations from three finished phases to tank (343,410,076,650 logical bytes). Both the source and the archive copy get a full-state check. The latest, best and three most recent generations stay where they are. Copying alone frees no NVMe space; switching over to the archive is a separate, checked step.

The user then asked for a sensible periodic history instead of every intermediate snapshot. We set a new retention policy for the bridge and later phases only, none of which had started: keep the latest, previous, best and terminal checkpoints, plus roughly every tenth 5M-target boundary (every 50M). The milestone counters come from the packed group offsets. Existing phase configs and old generations are untouched. This keeps the normal recovery cadence but stops history from growing without limit. The retention and recovery logic passed nine CPU test cases and schema validation; we'll see how it behaves at runtime once that phase runs.

## Supply expansion and v2 work

The notebook dataset has 11 shards. A census of one pinned shard found 78,247,136 raw targets in documents longer than 4K, plus 73,817,785 targets in shorter documents. The long-document count is before deduplication and protected screening. Any policy that splits long documents into contiguous pieces must still exclude source families, never repeat a target position, respect the 4K shape limits and record where each piece came from.

We already have the codeparrot/github-code-clean corpus locally, built and qualified per row for license and language. It may overlap data we already used or protected, so we need to reconcile that before training on it. More shards of the same source could stand in once notebooks run out. If we shift the notebook-to-code ratio, that becomes a new mixture in a later segment; we won't change the active phase.

We are acquiring and reviewing new candidate areas separately: NASA systems engineering, NIST community resilience, Census reference data, and a small train-only PG-19 book pilot. The PG-19 maintainers warn against general-purpose use because of historical style and bias, so we treat those books as a capped cultural component and never as a source of current scientific facts. Cynefin material comes with attribution and share-alike terms, so we are reviewing its rights separately. None of these new domains has entered training yet.

Priorities for v2:

1. Append new data by reusing the already-prepared prefix, instead of re-tokenizing everything each segment.
2. Prepare enough fresh data ahead of the GPU. Track raw, qualified, screened, reserved, packed and consumed inventory separately.
3. When target-group size changes, keep optimizer-update counting explicit and carry Adam step and scheduler state forward.
4. Measure padding and reporting costs in controlled comparisons. Don't estimate speedups from peak FLOPs, or from length sorting the collator already does.
5. Keep validation loss separate from behavioral, factual and n-gram-memory evaluations on untouched data. Keep source-level held-out sets for each new domain.
6. Write down checkpoint cadence and retention choices, and test real checkpoint recovery, archive switchovers and final outcomes.
7. Keep failures, low-yield source decisions, exact source revisions, exclusions, actual instruction proportions and any future mixture changes.

Primary source references: [PG-19](https://github.com/google-deepmind/pg19), [NASA handbook record](https://ntrs.nasa.gov/citations/20170001761), [NIST resilience guide](https://www.nist.gov/publications/community-resilience-planning-guide-buildings-and-infrastructure-systems-volume-i), [NIST reuse terms](https://www.nist.gov/open/license), [Census state codes](https://www.census.gov/library/reference/code-lists/ansi/ansi-codes-for-states.html), [Cynefin terms](https://cynefin.io/wiki/Terms_of_Use).

## Verified handoff update, 00:18 UTC

The 100M phase reached step 22,987 / 1,317,523,826 targets. Its first full-state checkpoint after updates began is step 22,970 / generation 2 (manifest SHA-256 `5e01918d7113295844958209d0d801ac056d2766dbf5976a69a0db0d0ee00256`), saved at 00:15:56 UTC and checked. A 315-second window ran at 18,823 targets/s including saves. The only trainer process was PID 2032776. The phase was still running.

## Subsequent preparation update

The bridge selected 25,005,482 fresh targets: web 8,752,741; notebooks 7,501,724; math 3,750,619; Smol instructions 3,750,101; Cosmopedia 1,250,297. It was still packing at this check (the 00:36 update records it as packed) and had applied no updates. The 180M phase after it still depends on screened replenishment.

We acquired the NASA text, the Census state codes and 16 primary PG-19 training books, all with hashes; the books date from 1849–1916. Both NIST downloads returned HTTP 403, so we don't have NIST. We acquired codeparrot/github-code-clean shard 50 at revision `c48d40f9e70f0196f8236901ee35807f7d6c44c0` (SHA-256 `50f2550c8e19ad69b335212ed36be071fc8e01eff95a9d4901feae96c081156f`) and are qualifying and screening it. The existing row checks allow only MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause and ISC licenses, keep the allowed languages, and reject rows with credentials or notice exceptions. Its first screening record carried a phrase inherited from the web-score filter; the final-stage metadata corrects it, and the filter that actually ran was the code policy. No new domain or code source has entered training.

### 00:36 UTC operational follow-up

The midnight phase reached step 23,141 / 1,337,833,198 Engram targets at 00:35:58 UTC. Its latest checked full-state checkpoint was step 23,122, generation 6. The latest 315-second window ran at 18,835 targets/s. NVMe had 328.7 GiB free.

The predawn bridge is packed: 25,005,482 fresh targets over 190 updates, with identical historical tokens and groups and no consumed-family overlap. Its supervisor is waiting for the midnight phase's final checkpoint. The sunrise phase is still an unselected 180M ceiling, waiting on final web and Cosmopedia protection screening.

The archive copy has checked 36 of the 76 generations from finished runs; no source space has been freed yet. The supervised switchover waits until every copy is checked, then makes sure no file is open before deleting only the NVMe copies that have a checked duplicate. The archive mapping is `checkpoint-copy-20261106-v1/original-to-archive.json`. Leave it as written, and keep it distinct from the earlier 187-generation mapping.

The original 12B-token mixture record allows each token once, but scheduled token positions are not the same as targets the model actually trained on. The unused tail of that mixture might be recoverable, but we can't count it yet. Recovering it needs an exact map from the dense checkpoint cursor, exclusion of every family consumed or scheduled since, and full held-out protection. Until then we keep the current conservative exclusion of baseline families; capacity arithmetic alone isn't a reason to loosen it.

Code shard 50 yielded 2,243,703 candidate targets before its final protected-query pass. The screening metadata it reused has the wrong source label (web). The code document IDs, pinned acquisition, rows and repository families are all still intact. Keep the original records and attach the correction before anything is selected from this shard. No code or cultural pilot data is in the pinned training mix.

At 00:36:43 UTC, step 23,148 reached 1,338,752,554 Engram targets. With the inherited dense phase that is 3,419,127,338 targets, just past 10× the backbone parameter count. That counts both phases together; it is not 10× in Engram targets alone, and it says nothing about model quality.

## Performance follow-up

See the [B70 performance summary](b70-performance-20261106.md) for the padding comparison, the trace limits, the return to production and the next upstream kernel idea. Detailed run artifacts stay local.

## Continuation progress through 2.516B+ Engram targets and 160M / 95M segment staging

Further finite continuations on the pinned nightly XPU runtime (`2.16.0.dev20261105+xpu`) took the campaign past **2.516B Engram-phase valid targets**. With the `2,080,374,784` inherited dense-backbone targets, that is `4.597B` combined.

- **Post-reboot 14M continuation:** 107 optimizer updates (`14,005,146` valid targets) to step **31,422** / `2,429,314,666` Engram targets. Cold-checked full-state checkpoint SHA-256 `b7d521277c4abe1cbec7a55b5658b3b2e135689ad2693c0fcbd1c8533526f717`; final validation loss **2.5700909473**.
- **7M bridge continuation:** 54 optimizer updates to step **31,476** / `2,436,319,171` Engram targets. The `7,004,505` valid targets were `2,450,694` FineWeb-Edu 4+, `2,102,033` notebooks, `1,051,449` FineMath 4+, `1,050,043` Tulu-3 instructions and `350,286` Cosmopedia v2. We cold-checked three checkpoints: the starting state (`step 31,422`, SHA-256 `730161f5d5a7beb2ee7eedc51cbc2476289beb4b2ef2d8eafdf84b761191799b`), an intermediate 5M save (`step 31,460`, SHA-256 `b1aa262959a72e1800a97a365e71e0b798a239bfaeff4d8dede71d12ef54196a`) and the final full state (`step 31,476`, SHA-256 `ed793f4ab87d1bc61d192867338fb42cec0a4a857c26edb052ec5a913303ea23`). Final validation loss improved to **2.5687490960**, at `21,887.7` optimizer valid targets/s.
- **Active 160M continuation (`devmind-engram-after7m-160m-131k-nvme-20261106-v1`):**
  - Starts from `step_00031476_gen_000003` (`ed793f4ab87d1bc61d192867338fb42cec0a4a857c26edb052ec5a913303ea23`). Its first child checkpoint, `step_00031476_gen_000001` (`01fc86bfbc116b902a6184d90634a0a6e25cc2659dbc63ac9c624e7f61bde89b`), passed a cold check.
  - Packs **160,002,769 new targets** in `162,913` whole documents and `1,213` optimizer updates, ending at step **32,689** / **2,596,321,940** Engram targets. The mix is `56,000,151` FineWeb-Edu 4+ (35.0%), `48,000,026` notebooks (30.0%), `24,000,477` FineMath 4+ (15.0%), `2,000,208` OpenCodeInstruct + `22,000,905` Tulu-3 instructions (`24,001,113`, 15.0%), and `8,001,002` Cosmopedia v2 (5.0%).
  - Had passed **step 32,083 / 2,516,383,537 Engram targets** (`+80.06M` targets into the segment). Validation loss improved to **2.5684862384** at step 31,600 (`step_00031600_gen_000005`, SHA-256 `9d1a1aa2ed2170d7055ca7ab158f954646419c9932c781414f37042f6a147f83`). End-to-end throughput reached **20,254.9 valid targets/s (+6.9% vs 14M run)**.
- **Next: 95M continuation (`after-160m-95m-append-4k-v1`):**
  - Packed ahead of time and checked on Tank (`native_data_manifest_sha256: 45164058035aa8830352efc2a9f7a17911bea74c30f2e1c8d6debe41937168c8`). It holds `95,003,026` new targets in `96,718` documents and `721` updates, ending at step **33,410** / **2,691,324,966** Engram targets.
  - The mix is `33,250,766` FineWeb-Edu 4+, `28,500,897` notebooks, `14,250,687` FineMath 4+, `1,350,196` OpenCodeInstruct + `12,900,065` Tulu-3 instructions, and `4,750,415` Cosmopedia v2.
  - `devmind-after160m-95m-handoff-20261106-v1.service` starts it as soon as the 160M run reaches step 32,689, so the GPU doesn't sit idle.
  - We raised `checkpoint.every_tokens` from `5,000,000` to `25,000,000`, which removes 80% of the periodic checkpoint pauses.

### Qualified dataset inventory and 16-worker parallel screening pipeline

Every newly acquired shard goes through the same processing and keeps the **35% Web / 30% Notebooks / 15% FineMath / 15% Instructions / 5% Cosmopedia** mixture:

- whole documents up to 4K (`<=4096` tokens with EOS, no truncation);
- `NORMALIZER_V3` structure cleaning;
- permissive license checks;
- MinHash LSH deduplication ($\ge 0.65$) against 40 prior index pools;
- screening against 1,406,036 protected benchmark and held-out queries.

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

For **DevMind v2**, build the data flows, screening speedups and kernel improvements from this continuation in from step 0, instead of adding them mid-campaign:

1. **Deduplicate notebooks by content cluster, not by repository name:**
   - Earlier `codeparrot/github-jupyter` screening scripts grouped union-find components by `family_id` (`repo_name`). That collapsed educational and data-science repositories with `10–50+` distinct notebooks down to one notebook each, and threw away `91–94%` of valid targets (`51.07M` encoded $\to$ `2.79M` kept).
   - Deduplicating by **exact content plus a within-shard and cross-shard MinHash LSH ($\ge 0.65$) cluster** keeps **~75% (`76.64M` targets across files 0–32)** of distinct, good notebooks. It still blocks any cluster that matches a prior pool, a protected query, a held-out repository or a content-review hold.
   - For v2, combine three sources from the start of the corpus build: `HuggingFaceTB/issues-kaggle-notebooks` (`kaggle` config, 11 shards, `~654M` clean targets), `codeparrot/github-jupyter` (all 33 files `0–32`, `~76.6M` clean targets) and `jupyter-agent/jupyter-agent-dataset` (`10a8dd461bb6c580fa25b83cd3b2f6810f1d6385`, Apache-2.0 executable notebook agent traces with `tool_calls`).
2. **Add execution-tested Python coding and agent trajectories to the Instruction pillar:**
   - `nvidia/OpenCodeInstruct` (`8f3ba5bafe4d6e8db46082cf7ae6741bc370604d`, 50 shards, CC-BY-4.0). Our filter requires `average_test_score == 1.0`, 10 passing unit tests with 10 distinct AST-parsed `assert` statements, balanced code fences, and 5/5 LLM judgements on `requirement_conformance`, `logical_correctness` and `edge_case_consideration`. Using all 50 shards in v2 gives **~70M+ execution-tested Python coding targets**.
3. **Parallel SQLite/MinHash qualification with a pre-sharded query cache:**
   - We replaced single-worker sequential `screen_queries` (over 40 prior SQLite indexes and 1.41M protected queries) with a 16-worker `ProcessPoolExecutor` (`mp_context='spawn'`) and pre-sharded `queries-{0..15}.jsonl`. Qualifying a whole shard dropped from **3–4 hours to 3–9 minutes** on the Threadripper, which lets us prepare several hundred million tokens of runway ahead of GPU training.
4. **Runtime and checkpoint defaults for v2:**
   - Use `padding_multiple=64`. It measured **+3.18%** steady throughput on the B70 XPU together with the vectorized `TokenNgramMemory` diagnostics from [Kybern Model Lab PR #335](https://github.com/supernovae/model-lab/pull/335).
   - Skip the per-microbatch `/proc` RSS/meminfo syscalls in `MemoryMonitor.sample()` when XPU/CUDA peak counters are available.
   - Set `checkpoint.every_tokens` to `25,000,000–50,000,000`, which gave a `+2.8%` end-to-end wall-clock gain over checkpointing every 5M.

## Continuation progress through 6.766B Engram targets (8.847B combined) and 2x B70 multi-GPU upgrade (2026-11-10)

By November 10, Segments 1 through 16 had finished (`step 31,422 -> 64,315`).

- They reached **6,766,391,105 Engram targets**, **82.76%** of the `8,176,203,776` Engram reference target.
- Combined with the dense phase, that is **8,846,765,889** targets using the `2,080,374,784`-target nominal 15,872-step reference, or **8,847,422,540** using the `2,081,031,435` actual packed dense-backbone tokens.
- Validation loss was **2.5383300** at step `64,315`, then **2.5370861** at step `65,800` in Segment 17, which was still running.

Along the way we upgraded the host with a **second Intel Arc Pro B70 GPU** (`868023e2-0000-0000-2300-000000000000`, next to `868023e2-0000-0000-e300-000000000000`) and **96 GB system RAM**.

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

- **Extra qualified sources for Segments 1–21 (`8.176B` Engram / `10.257B` combined targets):**
  - **Notebooks (`30%` in Stages 1–15, `1.888B` total unique notebook tokens):** `HuggingFaceTB/issues-kaggle-notebooks` (`ef882ad1ed8274340e8fc9bac087c903f2f75396`, shards `0–10`), `codeparrot/github-jupyter` (`495a499ae501478e2e934c453964d9bf5cd103eb`, files `0–32`), `bigcode/the-stack-jupyter-parsed-filtered` (`bigcode/jupyter-parsed`, `eed65c314469b51419d08fb2ff7ee41e448774d4`, shards `0–45`), `secmlr/starcoderdata` (`0a11b2a003eb39252c919f3d28f3d26f412bc3d7`, `jupyter-structured-clean-dedup` & `jupyter-scripts-dedup-filtered`), `jordangong/jupyter-scripts-smollm3` (`98dcfd99ae3c6cf0f43e3d07d6a10a570d0da262`, shards `0–419`), and `MetaKaggle Code v184` (`trial1000-v1`).
  - **Web (`35%` in Stages 1–15, `50%` in Stages 16–21):** `HuggingFaceTB/smollm-corpus` (`fineweb-edu-dedup`, `3ba9d605774198c5868892d7a8deda78031a781f`, shards `69–112`, `int_score >= 4`, English) and `HuggingFaceFW/finewiki` (`en`, `20261106-v1`).
  - **FineMath (`15%` in Stages 1–15, `20%` in Stages 16–21):** `HuggingFaceTB/finemath` (`finemath-4plus`, `e92b25a616738fe95dc186b64dfb19f9c8525594`, shards `0–15`, `int_score >= 4`).
  - **Instructions (`15%` in Stages 1–15, `18%` in Stages 16–21):** `nvidia/OpenCodeInstruct` (`8f3ba5bafe4d6e8db46082cf7ae6741bc370604d`, shards `0–49`, `generic_python_verified_tests`), `HuggingFaceH4/ultrachat_200k` (`8ebe7fc305c02c2adca58c8bf303b1451be2f97f`, `train_sft` & `train_gen`), `HuggingFaceTB/smoltalk` (`smol-magpie-ultra`, `5feaf2fd3ffca7c237fc38d1861bc30365d48ffa`, shards `0–5`), `allenai/tulu-3-sft-mixture` (`b14afda60f1bbebe55d5d2fa1e4df5042f97f8be`, Permissive-2.0 subset, shards `0–1`), and `gretelai/synthetic_text_to_sql` (`Apache-2.0`).
  - **Cosmopedia & Technical Reference (`5%` in Stages 1–15, `12%` in Stages 16–21):** `HuggingFaceTB/smollm-corpus` (`cosmopedia-v2`, `3ba9d605774198c5868892d7a8deda78031a781f`), Python 3.14 Official Documentation (`PSF-2.0`), IETF RFCs (`rfc0001–rfc9699`), and PostgreSQL 17.2 Official Documentation (`PostgreSQL License`).
- **Checkpoint retention and NVMe storage:**
  - We pruned 404 of 449 intermediate archived checkpoints on `/tank`. We kept 45 (`10.0%`, evenly spaced about every `~120M` tokens from `2.47M` to `5.442B` tokens) plus every run's final checkpoint on NVMe. This freed **1,695.92 GiB** on `/tank`.
  - For finished grandparent runs on NVMe (`prior_run_to_trim`), we replace the local `data/train.npy` with a symlink to the SHA-256-checked copy on `/tank`. The immediate parent's `parent_run / 'data/train.npy'` stays a regular file, because `load_continuation` checks it. This kept **370–410 GiB free on NVMe** across the `6.4B -> 8.2B` target range.
- **Planned final-phase mixture (`devmind-engram-final-rebalanced-phase-20261110-v1`, `6.466B -> 8.176B` Engram targets):**
  - At `step 62,039` (`6,466,387,878` Engram targets; `8,547,419,313` combined using the actual packed dense-backbone count), we had used up every bulk permissive notebook source that passes the strict whole-document 4K and no-image rules. That is `1,883,203,267` unique notebook tokens consumed, with `5,489,113` unreserved targets left.
  - The approved final phase, **`devmind-engram-final-rebalanced-phase-20261110-v1`**, spends the last `5.0M` unreserved notebook targets in Stage 16 (`after-4250m-300m-append-4k-v1`). Stage 16 finished at `step 64,315` / `6,766,391,105` Engram targets with validation loss **`2.5383300`**.
  - For Stages 16–21 (`6.466B -> 8.176B` Engram targets), it moves the `30%` notebook share to `web_4plus`, `finemath`, `instruction_ultrachat` and `cosmopedia_v2`. **Segment 17** reached a new campaign best of **`2.5370861` validation loss at `step 65,800`**.

| Final-Phase Stage | Run ID | Target Addition | Cumulative Engram Targets | Combined Targets (`+2,080,374,784` ref) | Status |
|---|---|---:|---:|---:|---|
| **Stage 16 (`after-4250m-300m`)** | `devmind-engram-after4250m-300m-resume-131k-nvme-20261110-v1` | `300,003,227` | `6,766,391,105` (`82.76%`) | `8,846,765,889` | **Completed (`step 64,315`, val loss `2.5383300`)** |
| **Stage 17 (`after-4550m-300m`)** | `devmind-engram-after4550m-300m-131k-nvme-20261110-v1` | `300,002,477` | `7,066,393,582` (`86.43%`) | `9,146,768,366` | **Training on 2x B70 GPUs (`step 65,832+`, val loss `2.5370861` at `65,800`)** |
| **Stage 18 (`after-4850m-300m`)** | `devmind-engram-after4850m-300m-131k-nvme-20261110-v1` | `300,002,889` | `7,366,396,471` (`90.10%`) | `9,446,771,255` | **Packed & verified on `/tank`; queued for zero-idle GPU handoff** |
| **Stage 19 (`after-5150m-300m`)** | `devmind-engram-after5150m-300m-131k-nvme-20261110-v1` | `~300,000,000` | `~7,666,396,471` (`93.76%`) | `~9,746,771,255` | **Staged in `campaign_orchestrator.py`** |
| **Stage 20 (`after-5450m-300m`)** | `devmind-engram-after5450m-300m-131k-nvme-20261110-v1` | `~300,000,000` | `~7,966,396,471` (`97.43%`) | `~10,046,771,255` | **Staged in `campaign_orchestrator.py`** |
| **Stage 21 (`after-5750m-210m`)** | `devmind-engram-after5750m-210m-131k-nvme-20261110-v1` | `~210,000,000` | **`~8,176,396,471` (`100.00%`)** | **`~10,256,771,255` (`100.00%`)** | **Staged in `campaign_orchestrator.py` (terminal cold verification)** |

### Upstream Kybern Model Lab PRs Enabling DevMind v2

- **[PR #333](https://github.com/supernovae/model-lab/pull/333) (merged):** Keep the checkpoint retention policy when comparing budget extensions.
- **[PR #334](https://github.com/supernovae/model-lab/pull/334) (merged):** `PreparedPrefix` reuse, which selects a smaller prefix without re-tokenizing. The later `PreparedAppend` tail-append API is a separate change.
- **[PR #335](https://github.com/supernovae/model-lab/pull/335) (merged):** Vectorized multi-stream `TokenNgramMemory` diagnostics and shared shifted-input buffers (**+1.64%** steady throughput at `padding_multiple=128`, **+3.18%** with `padding_multiple=64`).
- **[PR #338](https://github.com/supernovae/model-lab/pull/338) & [PR #340](https://github.com/supernovae/model-lab/pull/340) (merged):** Multi-GPU microbatch-parallel `PyTorchEngine` execution, and a `MultiDeviceLease` lock that refuses to run unless it holds every physical device.
- **[PR #342](https://github.com/supernovae/model-lab/pull/342) (merged):** Multi-GPU device index enumeration (`0..device_count()-1`) and XPU/CUDA/ROCm physical UUID discovery in `discover_runtimes()`.
