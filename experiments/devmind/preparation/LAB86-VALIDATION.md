# DevMind Preparation Package Validation

[Back to Preparation Plan](README.md)

These are the offline schema, manifest and mocked-acquisition tests we ran on the 84-shard preparation package in [`lab86/`](lab86/README.md).

## Validated Coverage

- **84-shard selection & ordering:** shards are selected by hash rank from the pinned Hugging Face Hub tree metadata (`smollm-corpus` and `github-code-clean`), always in the same order. They total `85,077,359,484` compressed bytes (79.24 GiB). The three pilot shards sort first and come to `3,771,713,555` bytes, under the 4 GiB initial gate.
- **24-phase plan compilation:** all 24 phase templates in `lab86/jobs/` and the 4 pilot jobs in `lab86/pilot-jobs/` render cleanly with `klab` and stay within their resource, network and storage limits.
- **Schema & policy checks:** `project-acquire.yaml`, `project-pilot-reuse.template.yaml`, `project-pre-freeze.template.yaml`, `project-build.template.yaml`, `resource-envelope.yaml`, `tokenizer-sampling.yaml`, `token-floors.yaml` and `mixture.template.yaml` pass `klab` schema validation.
- **Parquet timestamps & cold checks:** mocked acquisition tests cover ISO-8601 timestamp serialization, shard SHA-256 checks, canonical row hashing and cold snapshot checks.
- **Package manifest:** every file in `lab86/` matches its SHA-256 digest in [`lab86/package-sha256.json`](lab86/package-sha256.json).
