# DevMind Preparation Package Validation

[Back to Preparation Plan](README.md)

This record summarizes offline schema, manifest, and mocked-acquisition tests for the 84-shard preparation package in [`lab86/`](lab86/README.md).

## Validated Coverage

- **84-shard selection & ordering:** deterministic hash-ranked shard selection from the pinned Hugging Face Hub tree metadata (`smollm-corpus` and `github-code-clean`), totaling `85,077,359,484` compressed bytes (79.24 GiB) with the three pilot shards sorted first (`3,771,713,555` bytes below the 4 GiB initial gate).
- **24-phase plan compilation:** all 24 phase templates in `lab86/jobs/` and the 4 pilot jobs in `lab86/pilot-jobs/` render cleanly with `sparselab` and match their resource, offline/network, and storage ceilings.
- **Schema & policy checks:** `project-acquire.yaml`, `project-pilot-reuse.template.yaml`, `project-pre-freeze.template.yaml`, `project-build.template.yaml`, `resource-envelope.yaml`, `tokenizer-sampling.yaml`, `token-floors.yaml`, and `mixture.template.yaml` pass native `sparselab` schema validation.
- **Parquet timestamp & cold verification:** mocked acquisition tests verify ISO-8601 timestamp serialization, shard SHA-256 verification, canonical row hashing, and cold snapshot verification.
- **Package manifest integrity:** all files in `lab86/` match their SHA-256 digests in [`lab86/package-sha256.json`](lab86/package-sha256.json).
