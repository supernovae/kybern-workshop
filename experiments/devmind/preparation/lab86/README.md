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
