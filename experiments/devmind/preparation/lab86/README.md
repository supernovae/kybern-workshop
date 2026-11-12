# DevMind Corpus Preparation Package (`lab86`)

[Back to Preparation Plan](../README.md) · [Pilot Execution Guide (`PILOT.md`)](PILOT.md) · [Preparation Policy (`POLICY.md`)](POLICY.md)

This package prepares the **DevMind 340M Base** training corpus with [Tiny Sparse Lab](https://github.com/supernovae/tiny-sparse-lab). It holds the 84 pinned shard files (`sources/`), their SHA-256 digests, the filtering and licensing policies (`application-policy.json`, `POLICY.md`), the resource limits (`resource-envelope.yaml`), and the phase job templates (`pilot-jobs/` and `jobs/`).

## Candidate Catalog & Shard Selection

The candidate catalog in `evidence/candidate-catalog.json` is built from pinned Hugging Face Hub tree metadata:

| Upstream Dataset | Pinned Revision | Tree Metadata SHA-256 | Candidate Shards |
| --- | --- | --- | ---: |
| `HuggingFaceTB/smollm-corpus` (FineWeb-Edu & Cosmopedia-v2) | `3ba9d605774198c5868892d7a8deda78031a781f` | `a74e258a9b66b34d11e1f47de5309eed9e9b7ba75068edaed3f598db8b1b65a1` | 234 FineWeb + 104 Cosmopedia |
| `codeparrot/github-code-clean` | `c48d40f9e70f0196f8236901ee35807f7d6c44c0` | `e3bc4e6083600440a8b9b4562ba64bf81ce1b0a2b80c3cd2b6067a983d783db6` | 880 CodeParrot |

The 84 selected shards in [`shards.json`](shards.json) total **85,077,359,484 bytes (79.24 GiB)** across 48 GiB web, 16 GiB synthetic, and 16 GiB code compressed allocations, fitting within the 99 GiB source transfer cap and 100 GiB total transport budget.

## Three-Stream 4 GiB Pilot

[`project-pilot-acquire.json`](project-pilot-acquire.json) selects exactly three unchanged shard files (`000-web.yaml`, `001-synthetic.yaml`, `002-code.yaml`). The 4 GiB initial gate counts everything downloaded so far: source bodies, metadata and retry reservations.

| Stream | Pinned Shard | Compressed Bytes |
| --- | --- | ---: |
| **Web** (`000-web.yaml`) | `fineweb-edu-dedup/train-00068-of-00234.parquet` | `2,251,835,383` |
| **Synthetic** (`001-synthetic.yaml`) | `cosmopedia-v2/train-00000-of-00104.parquet` | `1,174,424,341` |
| **Code** (`002-code.yaml`) | `data/train-00570-of-00880.parquet` | `345,453,831` |
| **Pilot Total** | — | **`3,771,713,555` (~3.51 GiB)** |

Each shard file scans up to 5M rows and caps emitted JSONL at 8 GiB. See [`PILOT.md`](PILOT.md) for running the initial four-step pilot session (`attempt-init`, `transport-init`, `pilot-acquire`, and `pilot-budget-status`).

## Downstream Phases After Pilot Review

1. **Offline Pilot Inspection (`project-pilot-reuse.template.yaml`):** Reuses the three downloaded pilot snapshots with `reuse_only` source effects to inspect schema, license filtering, and family counts offline.
2. **Full Acquisition & Split Freeze:** Not ready yet. The full 84-source `project-acquire.yaml` is bound to a different ledger, and its projected expanded disk use exceeds the 300 GiB ceiling. Keep the pilot ledger as it is, and releasing the gate doesn't mean you can carry on. Full acquisition and the split freeze need a separately reviewed plan first, one that keeps the policy, the running totals and the deadline.
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
under `family_fields_by_source`. The full pre-freeze project uses this file;
the acquisition-only projects keep their original split file. Lab's inventory
puts the exact original prompt into a canonical UTF-8 JSON array as its only
element, hashes it with SHA-256, and prefixes the hash with
`synthetic_text-family:`. It doesn't trim whitespace, fold case, normalize
Unicode or extract quoted seed excerpts. Identical prompts group together across
shards, whatever dataset label `seed_data` carries.

The acquired source files and checksums are unchanged. We keep `seed_data`,
prompt, audience and format as they came from the source. In the Cosmopedia
records we inspected, `seed_data` was a dataset label and prompts contained
quoted seed excerpts; the schema has no separate ID for the original seed. This
prompt-family rule is the grouping we use for this experiment, and it is
reproducible. Different prompts can share an underlying seed, so the held-out
splits may still share original seeds.

If one qualified row is missing a selected family field, the whole freeze
refuses; Lab doesn't drop the row or regroup it by `seed_data`. Fix that row's
source information, or record a reviewed admission decision, before retrying.

The existing cross-split lexical screen is
`sparselab corpus near-duplicates RELEASE`. It holds rows and shingles in memory
and defaults to 100,000 documents / 128 MiB of text, so the defaults don't cover
this full corpus. Record what the screen actually covered and what it missed; a
cap refusal is not a clean result. Review and merge any overlap clusters it finds
before training. Neither the prompt grouping nor a lexical screen shows that
splits are independent by original seed or meaning.

Keep together: the exact Lab and Workshop commits, pinned upstream revisions and
shard checksums, acquisition and snapshot receipts, reviewed admission and
family merges, the inventory digest, and split seed `lab86-exp1-splits-v1`. The
98/1/1 split weights, 60/20/20 mixture and unique-target requirements stay as
configured. When Lab freezes the splits, it ranks families by the SHA-256 of
`[seed, stratum, family]`, breaks ties by family name, and assigns whole-number
counts the same way every time. Keep the frozen YAML, its assignment companion,
the family inventory and the commit receipt together; the frozen YAML carries
the same field rule so it can be replayed cold. Reproducing it requires the same
bytes to stay available and pass their digest checks.
