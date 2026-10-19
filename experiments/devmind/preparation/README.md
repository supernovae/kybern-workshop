# DevMind Corpus Preparation Plan (24 Phases)

[Back to DevMind Overview](../README.md) · [Shard Package (`lab86/README.md`)](lab86/README.md)

[`preparation.json`](preparation.json) defines the 24-phase native [Tiny Sparse Lab](https://github.com/supernovae/tiny-sparse-lab) corpus preparation workflow for **DevMind 340M Base**. The pinned candidate shard declarations, filtering policies, and job templates live in [`lab86/`](lab86/README.md).

## Inspecting Phase Commands

Use `sparselab attempt phase-command` to compile and inspect the command arguments for any phase before running:

```sh
sparselab attempt phase-command \
  --plan experiments/devmind/preparation/preparation.json \
  --attempt-root /tmp/devmind-preview \
  --label transport-init \
  --bindings-json '{"ACQUISITION_PROJECT":"/path/to/experiments/devmind/preparation/lab86/project-acquire.yaml"}'
```

## Preparation Sequence

1. **Pinned Upstream Sources:**
   - `HuggingFaceTB/smollm-corpus` (`3ba9d605774198c5868892d7a8deda78031a781f`) — FineWeb-Edu and Cosmopedia-v2 shards
   - `codeparrot/github-code-clean` (`c48d40f9e70f0196f8236901ee35807f7d6c44c0`) — permissively licensed code shards
   - The three pilot shards (one web, one synthetic, one code) sort first (`000-web.yaml`, `001-synthetic.yaml`, `002-code.yaml`) so the initial 4 GiB pilot samples all three streams.
2. **Initial 4 GiB Pilot Gate:**
   - `transport-init` initializes the transport budget (`initial_body_bytes: 4294967296`, `max_total_body_bytes: 107374182400`).
   - `pilot-acquire` downloads the first three shards (`3,771,713,555` bytes total) and stops at the fourth shard reservation across the 4 GiB gate.
   - `pilot-reuse` materializes the three pilot snapshots locally (`reuse_only`) for offline admission inspection and split inventory without additional network transfers.
3. **Pilot Review & Full Acquisition:**
   - Review pilot schema, license filtering, family counts, and token yield projections.
   - Release the transport gate with `sparselab corpus budget-release-gate` and run `continue-acquire` against the same transport ledger.
4. **Admission & Frozen Splits (98/1/1):**
   - Draft and inspect corpus admission using `application-policy.json`, `POLICY.md`, and `inspection-selection.json`.
   - Group duplicate, repository, and seed families (`family-clusters.template.json`) and freeze the `98/1/1` train/validation/test split (requiring at least 100 families per stratum).
5. **Corpus Build, Release & Audit:**
   - Build the offline corpus release (`corpus build`), freeze (`corpus freeze`), and audit (`corpus audit`).
6. **LM Export & 32,768-Vocab BPE Tokenizer:**
   - Export LM sequences (`sequence_length: 2048`, `int32` tokens) and fit a byte-level BPE tokenizer (`vocab_size: 32768`) on up to 512 MiB of `TRAIN` data sampled at `60/20/20` (`tokenizer-sampling.yaml`).
7. **Token Floor Verification & Mixture Packing:**
   - Verify unique token supply against [`token-floors.yaml`](lab86/token-floors.yaml) (12B target: 7.2B web, 2.4B synthetic, 2.4B code with `max_exposures: 1`).
   - Materialize and verify the mixture (`mixture.template.yaml`), then publish and cold-verify the packed training arrays.

## Resource Envelope (`lab86/resource-envelope.yaml`)

- **Transport budget:** 4 GiB initial pilot gate; 100 GiB total cap (99 GiB shard bodies + 1 GiB metadata).
- **Workspace & compute bounds:** up to 300 GiB additional disk space, 8 CPU threads, 16 GiB observed RSS target, and 48-hour wall ceiling for full preparation.
