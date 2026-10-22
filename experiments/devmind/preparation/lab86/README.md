# DevMind Corpus Preparation Package (`lab86`)

[Back to Preparation Plan](../README.md) · [Pilot Execution Guide (`PILOT.md`)](PILOT.md) · [Preparation Policy (`POLICY.md`)](POLICY.md)

This package contains the 84 pinned shard declarations (`sources/`), content SHA-256 digests, filtering and licensing policies (`application-policy.json`, `POLICY.md`), resource envelope (`resource-envelope.yaml`), and phase job templates (`pilot-jobs/` and `jobs/`) for preparing the **DevMind 340M Base** training corpus with [Tiny Sparse Lab](https://github.com/supernovae/tiny-sparse-lab).

## Candidate Catalog & Shard Selection

The candidate catalog in `evidence/candidate-catalog.json` is built from pinned Hugging Face Hub tree metadata:

| Upstream Dataset | Pinned Revision | Tree Metadata SHA-256 | Candidate Shards |
| --- | --- | --- | ---: |
| `HuggingFaceTB/smollm-corpus` (FineWeb-Edu & Cosmopedia-v2) | `3ba9d605774198c5868892d7a8deda78031a781f` | `a74e258a9b66b34d11e1f47de5309eed9e9b7ba75068edaed3f598db8b1b65a1` | 234 FineWeb + 104 Cosmopedia |
| `codeparrot/github-code-clean` | `c48d40f9e70f0196f8236901ee35807f7d6c44c0` | `e3bc4e6083600440a8b9b4562ba64bf81ce1b0a2b80c3cd2b6067a983d783db6` | 880 CodeParrot |

The 84 selected shards in [`shards.json`](shards.json) total **85,077,359,484 bytes (79.24 GiB)** across 48 GiB web, 16 GiB synthetic, and 16 GiB code compressed allocations, fitting within the 99 GiB source transfer cap and 100 GiB total transport budget.

## Three-Stream 4 GiB Pilot

[`project-pilot-acquire.json`](project-pilot-acquire.json) selects exactly three unchanged declarations (`000-web.yaml`, `001-synthetic.yaml`, `002-code.yaml`). The 4 GiB initial gate counts cumulative source bodies, metadata, and retry reservations:

| Stream | Pinned Shard | Compressed Bytes |
| --- | --- | ---: |
| **Web** (`000-web.yaml`) | `fineweb-edu-dedup/train-00068-of-00234.parquet` | `2,251,835,383` |
| **Synthetic** (`001-synthetic.yaml`) | `cosmopedia-v2/train-00000-of-00104.parquet` | `1,174,424,341` |
| **Code** (`002-code.yaml`) | `data/train-00570-of-00880.parquet` | `345,453,831` |
| **Pilot Total** | — | **`3,771,713,555` (~3.51 GiB)** |

Each shard declaration scans up to 5M rows and caps emitted JSONL at 8 GiB. See [`PILOT.md`](PILOT.md) for running the initial four-step pilot session (`attempt-init`, `transport-init`, `pilot-acquire`, and `pilot-budget-status`).

## Downstream Phases After Pilot Review

1. **Offline Pilot Inspection (`project-pilot-reuse.template.yaml`):** Reuses the three downloaded pilot snapshots with `reuse_only` source effects to inspect schema, license filtering, and family counts offline.
2. **Full Acquisition & Split Freeze:** Not enabled by the pilot correction. The full 84-source `project-acquire.yaml` has a different ledger binding and its projected expanded disk bound exceeds the 300 GiB ceiling. Do not retarget the pilot ledger or treat gate release as permission to continue. A separately reviewed continuation design must preserve the policy, cumulative accounting, and deadline before full acquisition and split freeze can run.
3. **Tokenizer & 12B Unique Mixture:** Exports 2,048-token sequences, fits a 32,768-token byte-level BPE tokenizer on up to 512 MiB of `60/20/20` training bytes (`tokenizer-sampling.yaml`), verifies token floors (`token-floors.yaml`), and packs the unique training mixture (`mixture.template.yaml`, `max_exposures: 1`).

## Resource Bounds

- **Memory:** 24 GiB available host RAM required at start (4 GiB minimum free floor); 16 GiB observed RSS limit.
- **Disk:** 310 GiB free disk space and 100,000 free inodes required at start; 300 GiB retained workspace ceiling (including a 64 MiB shared evidence reserve).
- **CPU:** Up to 8 CPU threads, single-threaded BLAS/OpenMP library settings, no GPU required for corpus preparation.


## Reproducing the synthetic split families

Use Tiny Sparse Lab commit `7ac454c67b2571d42406454043c1569a725c1d3b`
([PR #216](https://github.com/supernovae/tiny-sparse-lab/pull/216)) for this rule.
Record the exact Lab and Workshop commits in each new preparation receipt.

`splits-pre-freeze.yaml` maps each of the 14 synthetic source IDs to `[prompt]`
under `family_fields_by_source`. The full pre-freeze project selects this file;
acquisition-only declarations keep their original split declaration. The native
inventory hashes the exact original prompt
as the sole element of a canonical UTF-8 JSON array and prefixes its SHA-256
with `synthetic_text-family:`. It does not trim whitespace, fold case, normalize
Unicode or extract quoted seed excerpts. Identical prompts group together across
shards, regardless of the dataset label in `seed_data`.

The acquired source declarations and checksums remain unchanged. `seed_data`,
prompt, audience and format stay retained as original provenance. In inspected
Cosmopedia records, `seed_data` was a dataset label and prompts contained quoted
seed excerpts; the retained schema has no separate authenticated source-seed ID.
This explicit prompt-family rule is the reproducible grouping used for this
experiment. Different prompts can share an underlying seed, so these held-out
splits do not establish original-seed independence.

One qualified row missing a selected family field makes the entire native
freeze refuse; it is not silently dropped or regrouped by `seed_data`. Correct
its provenance or record an explicit reviewed admission decision before retrying.

The existing cross-split lexical screen is
`sparselab corpus near-duplicates RELEASE`. It retains rows and shingles in memory and defaults to 100,000
documents / 128 MiB of text, so those defaults do not cover this full corpus.
Record actual screening coverage and gaps; a cap refusal is not a clear result.
Any discovered overlap clusters need reviewed merges before training. The prompt
proxy and a lexical screen do not prove original-seed or semantic independence.

Keep the exact Lab and Workshop commits, pinned upstream revisions and shard
checksums, acquisition/snapshot receipts, reviewed admission and family merges,
inventory digest, and split seed `lab86-exp1-splits-v1`. The existing 98/1/1 split
weights, 60/20/20 mixture and unique-target requirements stay declared. Native
freezing ranks families by SHA-256 of `[seed, stratum, family]`, with the family
name breaking ties, and allocates deterministic integer counts. Preserve its
frozen YAML, assignment companion, family inventory and commit receipt together;
the frozen YAML carries the same field rule for cold replay. Reproduction
requires the same bytes to remain available and pass their digest checks.
