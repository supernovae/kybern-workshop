# Recipe Metadata Validation Summary

This record summarizes schema and configuration validation checks run with `sparselab` (`7e306a96bcc617468d2a06493dab4562bff6beb0`, Python 3.14) against the declarations in this repository.

## Validated Operations

| Recipe | Command / Operation | Result |
| --- | --- | --- |
| **DevMind 340M Base** | `sparselab config validate model.json --kind model --json` and `--kind optimizer` | Schema-valid (`executable: false` until dataset and runtime paths are bound). |
| **DevMind 340M Base** | `sparselab attempt phase-command` (`transport-init` with `project-acquire.yaml`) | Compiles exact `corpus budget-init` command arguments. |
| **DevMind 340M Base** | `sparselab attempt phase-command` (`pack` without generated inputs) | Refuses as expected when `RESOURCE_ENVELOPE` and `RUN_CONFIG` are unbound. |
| **TinyStories Microlab** | `sparselab config validate` on `run.yaml` and `tokenizer.yaml` | Schema-valid. |
| **TinyStories Microlab** | `sparselab config derive` with `model.ffn_dim=384` | Produces candidate config and provenance sidecar. |
| **Synthetic CPU** | `sparselab experiment recipe create` & `preparation inspect` | Produces portable recipe descriptor (`bb075a8e08db14b78990a28ae14a76a7489ee868d57a35073d86a922acf7dbe0`) and validates local bindings. |
| **Synthetic CPU** | `sparselab experiment recipe export` | Exports the five recipe metadata files cleanly. |

Note: when invoking `sparselab attempt phase-command`, pass `--bindings-json` as a JSON object string (for example, `'{"ACQUISITION_PROJECT":"/path/to/preparation/lab86/project-acquire.yaml"}'`).
