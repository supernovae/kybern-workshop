# DevMind: Tiny Sparse Lab Command Map

[Back to DevMind Overview](README.md)

Every stage of the **DevMind 340M Base** pipeline uses native [Tiny Sparse Lab](https://github.com/supernovae/tiny-sparse-lab) (`sparselab`) commands. Keep generated datasets, tokenizers, checkpoints, and run stores in an external workspace directory outside Git.

The ordinary experiment path is [bind → train → inspect → resume/evaluate → derive](run.md).
Preparation commands below are available when inputs are missing or changed.

## Pipeline Operations

| Stage | `sparselab` command | Required inputs |
| --- | --- | --- |
| **Preview preparation command** | `attempt phase-command --plan preparation/preparation.json --attempt-root ROOT --label LABEL --bindings-json JSON` | Phase-specific bindings JSON; prints the resolved command without executing it. |
| **Run preparation phase** | `attempt init` and `attempt run-phase` | Workspace baseline, attempt ledger, and resource envelope bindings. |
| **Corpus acquisition & budget gate** | `corpus budget-init`, `acquire`, `budget-status`, `budget-release-gate` | Pinned acquisition project (`preparation/lab86/project-acquire.yaml`). |
| **Admission & family splits** | `corpus admission-draft`, `inspect-admission`, `split-inventory`, `freeze-splits` | Acquired shard snapshots, application policy, and family cluster definitions. |
| **Corpus release & tokenizer** | `corpus build`, `freeze`, `audit`, `export`; `tokenizer train` | Frozen split bundle, export configuration, and 32,768-vocab BPE config. |
| **Mixture & token packing** | `corpus measure-tokens`, `materialize-mixture`, `verify-mixture`; `data prepared-inputs publish/verify` | Token floor verification, 60/20/20 mixture declaration, and full `RunConfig`. |
| **Validate model & optimizer** | `config validate SOURCE --kind model/optimizer/run --json` | Validates [`model.json`](model.json) and [`optimizer.json`](optimizer.json) sections. |
| **Train & resume** | `train CONFIG`, `train CONFIG --resume CHECKPOINT` | Complete `RunConfig`, verified prepared inputs, and target hardware backend. |
| **Checkpoint verification** | `checkpoint inspect`, `checkpoint verify` | Generated checkpoint directory from training. |
| **Evaluate & report** | `eval RUN_ID --checkpoint CHECKPOINT --panel PANEL --output OUTPUT`; `report` | Verified checkpoint, frozen evaluation panel, and local run store. |

## Validating the Model and Optimizer Sections

You can validate the standalone architecture and optimizer configurations right now:

```sh
sparselab config validate experiments/devmind/model.json --kind model --json
sparselab config validate experiments/devmind/optimizer.json --kind optimizer --json
```

Both return `schema_valid: true` and `executable: false`. Native schema validation always reports no execution evidence, including for a complete RunConfig. Binding can reuse existing artifacts; it does not require replaying preparation:

- `model.json` SHA-256: `47fe3e80dbe99abd53d083f8e0e558e691f102e7be64f247573a89aa61e42107` (341,885,952 parameters across 219 tensor specifications with tied embeddings)
- `optimizer.json` SHA-256: `5608094732838fa17570f9adab6786e2e2edaca42d2eb0d0f57a6e3ae6d64a0e`

## Compiling Preparation Phase Commands

The 25-leaf plan in [`preparation/preparation.json`](preparation/preparation.json) compiles deterministic argument arrays for each corpus preparation step:

```sh
sparselab attempt phase-command \
  --plan experiments/devmind/preparation/preparation.json \
  --attempt-root /tmp/devmind-preview \
  --label transport-init \
  --bindings-json '{"ACQUISITION_PROJECT":"/path/to/experiments/devmind/preparation/lab86/project-acquire.yaml"}'
```

Phases that depend on downstream artifacts (such as `pack`, which requires `RESOURCE_ENVELOPE` and `RUN_CONFIG`) refuse compilation until those bindings are supplied.
