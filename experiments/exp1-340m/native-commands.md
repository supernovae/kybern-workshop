# Native Lab operation map

All commands are Lab functions. This is a map of supported interfaces and missing
bindings, not an instruction to launch them now. No Workshop Python or runner is
required. Keep generated data, native stores and approvals outside this recipe.

| Boundary | Native interface | Inputs still required |
| --- | --- | --- |
| Inspect preparation argv | `attempt phase-command --plan preparation/preparation.json --attempt-root ROOT --label LABEL --bindings-json JSON` | Only phase-specific explicit bindings; does not execute the returned command |
| Supervised preparation | `attempt init`, `attempt run-phase`, native monitor/receipt verification | Reviewed zero-model contract, baseline, ledger, resource/approval bindings |
| Transfer and gate | `corpus budget-init`, `acquire`, `budget-status`, `budget-release-gate` | Pinned project; actual report-bound continuation approval |
| Rights and splits | `corpus admission-draft`, `inspect-admission`, `split-inventory`, `freeze-splits` | Real retained inputs, reviewed admission and family clusters |
| Release and tokenizer | `corpus build`, `freeze`, `audit`, `export`; `tokenizer train` | Valid frozen release, export configuration and fresh fit/audit evidence |
| Unique targets and packing | `corpus measure-tokens`, `materialize-mixture`, `verify-mixture`; `data prepared-inputs publish/verify` | Real token counts, complete RunConfig and envelope |
| Shape and configuration | `config validate SOURCE --kind model/optimizer/run --json` (Lab PR162) | Native model/optimizer section validation; full run bindings still missing |
| Train/recover | `train CONFIG`, `train CONFIG --resume RUN_ID`; native Campaign operations | Full reviewed RunConfig, prepared inputs, admission, finite training budget and supported runtime |
| Inspect/verify checkpoint | `checkpoint inspect`, `checkpoint verify` | Actual native checkpoint/store identities |
| Evaluate retained base | `eval RUN_ID --checkpoint CHECKPOINT --panel PANEL --output OUTPUT`; `model exercise RUN_ID --checkpoint CHECKPOINT --prompt-panel PANEL` | Real matching checkpoint, frozen panel, local native run store, separately authorized evaluation |
| Report | Native `report`, `experiment workflow report` | Verified native evidence; a report cannot manufacture absent measurements |

Inspect the pinned Lab command's `--help` before creating local bindings. Native
preparation compilation refuses unresolved placeholders. Its 24-phase plan uses
exact argv arrays and generated output references; shell evaluation is unnecessary.

## Interface limits

Current portable recipe/workflow descriptors require concrete RunConfig and input
artifact identities. Do not invent release/checkpoint hashes to make a descriptor
parse. The current portable workflow execution contract is CPU-bounded and excludes
continuation/expanded evaluation; native training/evaluation capabilities already
exist but still need portable composition appropriate to this recipe. Lab #158
owns demonstrated generic interface gaps, including generation in arbitrary local
directories. No Workshop-only descriptor, launcher or scheduler fills those gaps.

Public derivative `eval` currently consumes a native run store as well as its
checkpoint. A generic independently retrieved base-artifact admission path must be
verified before promising checkpoint-only reproduction. This recipe records the
required artifact closure in `base-artifact.md`, without claiming it exists.

## Validation performed

2026-10-17, existing Python 3.14.4, Lab checkout
`7ad529a1a6aaccde37603a82fe0a1a210fb12604`:

- Native `attempt phase-command` for `transport-init`, bound to relocated
  `preparation/lab86/project-acquire.yaml`, returned exit 0 and exact
  `corpus budget-init PROJECT` argv.
- The same native command for `pack` without generated bindings returned exit 1:
  `missing preparation bindings: ['RESOURCE_ENVELOPE', 'RUN_CONFIG']`.
- The inspection attempt-root did not exist afterward. No ledger, receipt,
  acquisition, corpus, tokenizer, model or runtime execution was created.
- Every imported byte is checked against source commit
  `8975c5abcaefb1d3e595a9f1f466db97f9ab7682` and recorded in `migration.json`.

These checks establish relocation of the inspected declaration and an honest
missing-input refusal. They do not establish complete-plan execution, 340M
training, usable-token yield, resource capacity, model quality or published
weights. No new Workshop Python test suite was added. Pure native configuration validation was then repeated at Lab PR162 head
`92e8e428a1df3f06d1b0fb451a824fb38f14fda9` using:

```sh
sparselab config validate model.json --kind model --json
sparselab config validate optimizer.json --kind optimizer --json
```

Both exit 0 with `schema_valid: true`, `executable: false`. Input SHA256:

- model: `47fe3e80dbe99abd53d083f8e0e558e691f102e7be64f247573a89aa61e42107`
- optimizer: `5608094732838fa17570f9adab6786e2e2edaca42d2eb0d0f57a6e3ae6d64a0e`

This verifies each native section, not cross-section RunConfig compatibility or
artifact contents. PR162 remains subject to independent review/merge; this does
not activate a run pin. At the earlier inspected Lab revision, the existing native
`model.inspection.named_tensor_inventory` also returned 341885952 parameters,
219 tensor specifications and one tied alias without model/tensor allocation.
Native optimizer source grouping was inspected; no optimizer state was allocated.
