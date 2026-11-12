# DevMind corpus preparation policy

This policy sets the rules for handling data and keeping preparation
reproducible. Following it doesn't by itself give permission to download data,
accept source terms or release a review gate.

Use only the pinned candidate shards in shards.json. The first three make up the
feasibility pilot. The compressed byte allocations for the rest are operating
limits; they aren't token ratios, and the pilot isn't meant to represent the
whole corpus. Stop at the 4 GiB cumulative body gate and keep the receipts of
failed downloads. Continue only after a reviewed decision tied to the report,
using the same ledger. All metadata and retry response bodies count toward the
100 GiB. No automatic retries, budget resets, reweighting, source substitution or
repeated target exposure.

Keep everything private and quarantined until the admission review is done.
SmolLM's ODC-By card label doesn't license every underlying FineWeb page. Keep
the URL, dump/date, source ID, original row and shard hashes, and notices;
inspect source rights and exclusions. From Cosmopedia, use only the generated
text, not prompt extracts, and keep seed_data, prompt, audience and format with
each record. Group common seed families before splitting. A dataset-level seed
label is only a coarse family; don't invent document-level seeds from it. Reject
records with no source information.

Code needs repository, path and license attribution. The initial allowed labels
are MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause and ISC. Inspect file notices,
and exclude conflicts, missing licenses, vendored or generated content, and
secrets. Allowed languages: Python, JavaScript, TypeScript, Go, Rust, Shell, SQL
and Markdown. The loader's Apache-2.0 notice doesn't license the repository
content. Don't run external loaders or guess languages without a reviewed rule.

Use exact and canonical dedup plus reviewed cross-source near-duplicate clusters,
and keep code indentation intact. Group repositories, seed families and
duplicates before a frozen 98/1/1 train/validation/test split. Report how much
benchmark-contamination checking you did and what it missed; a corpus you haven't
checked isn't decontaminated. If a stratum has fewer than 100 eligible families,
the split refuses; don't loosen the grouping to get past it.

Fit one new 32768 byte-level BPE, with Lab's reserved special tokens, on TRAIN
only: at most 512 MiB, 60/20/20 bytes web/synthetic/code. Preserve whitespace,
case and byte coverage. Audit at least 1000 unseen TRAIN documents per stratum
where available, and report shortages, roundtrip/UNK, bytes per token,
identifiers, numbers, multilingual text and code whitespace. Never use
validation or test data for fitting. Measure unique usable TRAIN targets after
admission, dedup, splitting and tokenization. 7.2B/2.4B/2.4B are the floors a run
must meet, not how much supply we have. Shuffle mixtures deterministically
without replacement (max_exposures=1). Pack int32 tokens at sequence length
2048. Preparation doesn't train or run the model.

The 48 hours include operator waits and cleanup. Use at most eight CPU threads,
with library thread settings at one. The 16 GiB RSS figure is sampled and
triggers a stop; it isn't a hard cap. Measure RAM and disk headroom before you
start. The 300 GiB of extra disk covers retained inputs, intermediates, caches
and receipts. Lab can't measure expanded Parquet size, so don't assume it stays
within the compressed size. The 5M-row prefix and 8 GiB emitted JSONL ceiling
per shard are upper limits, not observed counts. Record any cutoff or shortfall,
and don't claim a whole shard was covered unless it was.
