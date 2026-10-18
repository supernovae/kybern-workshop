# Current native metadata acceptance

Date: 2026-10-18. Lab source: `7e306a96bcc617468d2a06493dab4562bff6beb0`.
Workshop input tree: `0f1bbaec53540c7d2b6ed23d7306d352ad83a7c4`.
Existing Python 3.14.4 interpreter; current source selected explicitly with
`PYTHONPATH` for these checks. This is source-level CLI acceptance, not a qualified
installation/runtime or execution recommendation. No package was installed.

Copies of the actual synthetic, microlab and DevMind declarations were placed in
one fresh temporary directory outside both checkouts. Every CLI call ran from a
separate unrelated subdirectory, with CPU library threads set to one and Hub
access offline. Stdout, stderr and nonzero outcomes were retained.

| Executed native operation | Observed result |
| --- | --- |
| DevMind `config validate model.json --kind model --json` and optimizer equivalent | Both schema-valid, executable false; scientific fields unchanged |
| Microlab run/tokenizer section validation | Both schema-valid, executable false |
| Microlab `config derive` with its existing FFN384 delta | Metadata candidate and provenance sidecar only |
| Synthetic `recipe create` using its four actual selected members | Descriptor plus four byte-identical members; executable false |
| Synthetic preparation inspect, move directory, inspect again | Same recipe fingerprint; bound future paths; executable false; no output payload directory |
| Synthetic recipe export | Five authenticated metadata files; no payload copied |
| DevMind `attempt phase-command` transport-init with actual relocated acquisition-project binding | Exact `corpus budget-init PROJECT` argv; no attempt directory created |
| DevMind pack without generated inputs | Expected refusal: missing `RESOURCE_ENVELOPE`, `RUN_CONFIG` |
| Microlab inventory creation followed by matrix inspection | Creation succeeds; inspection explicitly refuses `evaluation_suite` as unsupported in that profile |

Synthetic recipe fingerprint:
`bb075a8e08db14b78990a28ae14a76a7489ee868d57a35073d86a922acf7dbe0`.
The DevMind compiler’s `--bindings-json` takes a JSON object string, not a filename.
An initial filename invocation failed JSON parsing; the corrected invocation used
`{"ACQUISITION_PROJECT":"/absolute/relocated/preparation/lab86/project-acquire.yaml"}`.
That failed attempt is retained; it was not a missing domain capability.

No preparation execution, acquisition, tokenizer fitting, payload verification,
model allocation/training, generation, runtime probing, approval, lock publication
or report generation was executed. Missing artifact hashes were not invented.
The microlab’s advanced plan was not weakened to make inspection pass. Its native
simple comparison guide remains a different route; broader portable composition
is still Lab #158 work, not a reason to add Workshop Python.

Existing generic regression coverage belongs in Lab: `test_recipe_authoring.py`,
`test_preparation_recipe.py`, `test_portable_recipe.py`,
`test_preparation_commands.py` and `test_portable_authoring.py`. This record adds no per-experiment validator or test suite.
Historical validation/results files and all imported scientific declarations remain
unchanged. These checks do not close Lab #157/#158 or prove 340M readiness, useful
stories, current installed-runtime compatibility or accelerator support.

## Regression and preservation checks

`python -m pytest -q tests/test_portable_authoring.py tests/test_recipe_authoring.py`
at the pinned Lab source: **55 passed in 2.44 seconds**. These existing tests use
neutral metadata fixtures; no experiment-specific tests were added. All 159
imported microlab/DevMind files were compared to their original Git objects and
manifest SHA256 values. The 27 inventoried helper files remained byte-identical;
34 local documentation links resolved and whitespace checks passed.
