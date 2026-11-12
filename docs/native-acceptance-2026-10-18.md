# Recipe Metadata Validation Summary

These are the checks we ran with `klab` (`7e306a96bcc617468d2a06493dab4562bff6beb0`, Python 3.14) on the configs in this repository. They load and validate files; nothing was trained.

## Checks Run

| Recipe | Command / Operation | Result |
| --- | --- | --- |
| **DevMind 340M Base** | `klab config validate model.json --kind model --json` and `--kind optimizer` | Valid. Reports `executable: false` until you fill in dataset and runtime paths. |
| **DevMind 340M Base** | `klab attempt phase-command` (`transport-init` with `project-acquire.yaml`) | Produced the exact `corpus budget-init` command arguments. |
| **DevMind 340M Base** | `klab attempt phase-command` (`pack` without generated inputs) | Refused, as it should, while `RESOURCE_ENVELOPE` and `RUN_CONFIG` were unset. |
| **TinyStories Microlab** | `klab config validate` on `run.yaml` and `tokenizer.yaml` | Valid. |
| **TinyStories Microlab** | `klab config derive` with `model.ffn_dim=384` | Wrote the candidate config and its derivation sidecar file. |
| **Synthetic CPU** | `klab experiment recipe create` & `preparation inspect` | Wrote a portable recipe file (`bb075a8e08db14b78990a28ae14a76a7489ee868d57a35073d86a922acf7dbe0`) and accepted the local path bindings. |
| **Synthetic CPU** | `klab experiment recipe export` | Exported all five recipe metadata files without errors. |

Tip: `klab attempt phase-command` takes `--bindings-json` as a JSON object string (for example, `'{"ACQUISITION_PROJECT":"/path/to/preparation/lab86/project-acquire.yaml"}'`).
