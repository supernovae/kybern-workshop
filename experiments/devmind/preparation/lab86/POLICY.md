# DevMind Corpus Preparation & Filtering Policy

[Back to Package Overview](README.md)

This policy governs source selection, licensing, deduplication, splitting, and tokenization for the **DevMind 340M Base** corpus preparation package (`preparation/lab86/`).

## 1. Source Scope & Transport Gate

- Acquire only the 84 pinned candidate shards declared in [`shards.json`](shards.json).
- The first three shards (`000-web.yaml`, `001-synthetic.yaml`, `002-code.yaml`) form the 4 GiB feasibility pilot.
- Acquisition stops automatically at the 4 GiB cumulative response-body gate so pilot yields, schemas, and license metadata can be reviewed before continuing up to the 100 GiB total cap.

## 2. Licensing & Provenance Filtering

- **Educational Web (`smollm-corpus` FineWeb-Edu):** Retain URL, crawl dump/date, source ID, row/shard hashes, and attribution notices.
- **Synthetic Text (`smollm-corpus` Cosmopedia-v2):** Use generated text (`text`) only; preserve `seed_data`, `prompt`, `audience`, and `format` metadata for family grouping. Reject rows missing provenance fields.
- **Code (`codeparrot/github-code-clean`):** Require repository, path, and license attribution. Allowed licenses: `MIT`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`, and `ISC`. Allowed languages: `Python`, `JavaScript`, `TypeScript`, `Go`, `Rust`, `Shell`, `SQL`, and `Markdown`. Exclude vendored/generated files, license conflicts, and secrets.

## 3. Deduplication & 98/1/1 Family Split

- Perform exact and canonical deduplication plus cross-source near-duplicate clustering while preserving code indentation.
- Group repositories, seed families, and near-duplicate clusters prior to freezing a **98% train / 1% validation / 1% test** split.
- Require at least **100 distinct families per stratum** before freezing splits.

## 4. Tokenizer & 12B Unique Mixture

- Fit a single 32,768-token byte-level BPE tokenizer on `TRAIN` data only (up to 512 MiB sampled at 60% web / 20% synthetic / 20% code), preserving whitespace, case, and byte fallback.
- Audit the tokenizer on at least 1,000 unseen `TRAIN` documents per stream; never use validation or test splits for tokenizer fitting or auditing.
- Verify unique usable `TRAIN` token floors (`7.2B` web, `2.4B` synthetic, `2.4B` code = `12.0B` total) and pack deterministic 2,048-token `int32` sequences without replacement (`max_exposures: 1`).

## 5. Resource Limits

- **Wall time:** 48 hours maximum across preparation.
- **Compute & RAM:** Up to 8 CPU threads (single-threaded numeric libraries) and 16 GiB observed RSS ceiling.
- **Storage:** 300 GiB maximum additional workspace usage; per-shard scan capped at 5M rows and 8 GiB emitted JSONL.
