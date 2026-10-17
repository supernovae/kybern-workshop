# Native metadata validation — no workload execution

2026-10-17; existing Python 3.14.4, Lab
`408835184bf7020c10bdd2e8b7115e196322cf2b` (PR162, review/merge pending).

- All 11 imported files match exact source bytes at Lab
  `eab014ef7ca92de89d37b47c30df2ebf021d9473`; migration.json records SHA256.
- Copied the recipe to a fresh temporary directory outside both repositories,
  changed invocation CWD to /tmp, then used native config loaders. Snapshot,
  tokenizer and cache paths remained under the copied workspace. `load_try_config`
  anchored lab_dir to that workspace/lab, independent of CWD.
- Public `config validate --kind run` and `--kind tokenizer` both returned
  schema_valid:true and executable:false.
- Public `config derive --set model.ffn_dim=384` wrote only a metadata candidate
  and derivation sidecar in that temporary directory. Native loading confirmed
  FFN384 and unchanged source paths.
- Native GenerationPanel schema accepted all three declarations:6 greedy × 192,
  6 sampled × 192,3 website baseline × 48. No generation function was called. Panels are
  descriptive declarations requiring real native evaluation/runtime bindings;
  schema acceptance is not a quality score or executable Campaign admission.
- Actual public parser accepts data lock/snapshot, tokenizer train, try/report,
  config validate/derive, checkpoint verify and generate arguments documented
  here. No acquisition, training or generation handler was dispatched.
- No snapshot/tokenizer/lab output directory was created during validation.

No Workshop Python implementation or test suite is added. One-off metadata
inspection calls existing Lab functions; regression coverage remains in Lab.
This demonstrates native declaration parsing, derivation and path relocation.
It does not verify source payload availability, actual snapshot/fit/train/replay,
CPU capacity or usable stories. The earlier completed CPU smoke and historical
30M study retain their distinct identities and limitations. Website PR2 UI tests
are also separate from model-quality evidence.

No downloads, installation, GPU activity, runner launch, publication or merge.
