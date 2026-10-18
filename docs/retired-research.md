# Retired research and current showcase

The owner's 2026-10-18 scope replaces the earlier active-portfolio migration:
Workshop now showcases basic synthetic CPU, TinyStories and DevMind only.
Retirement removes current-tree copies, not Git history or host data. No run,
checkpoint, lease, hold or external receipt was deleted. No old result is a
current guarantee or authority to rerun it. Fresh, somewhat larger experiments
using current frameworks belong to the parent-coordinated Notion backlog.

Historical snapshot: [Workshop fd259e2](https://github.com/supernovae/kybern-workshop/tree/fd259e2cad4e9856d6d659e8df34728a98b32502/). Its catalog, manifests and
acceptance records retain original identities; they are not current obligations.

| Backlog family | Retired current-tree paths (relative to historical snapshot) |
| --- | --- |
| Memory injection / fact swaps (EXP3) | `experiments/memory_injection_v1/`, `acceptance/memory-injection-identity/`, archived `configs/memory_injection*`, `artifacts/studies/memory_injection_v1/` |
| Context | `experiments/context_engram/`, corresponding archived configs/data/cards/reports |
| Path-domain allocation | `experiments/path_domain/`, `experiments/memory-allocation-curve-v1/`, corresponding archived corpus/configs/reports |
| Kernel Memory Lab | `experiments/kernel-memory-lab/`, archived current and historical `experiments/research/kernel-memory-lab/` |
| Dense-LM controls | `experiments/dense-lm-{v1,decoding-v1,scale-v1,token-budget-v1}/`, corresponding archived configs, acceptance and reports |
| Engram portability, controlled/learned | `experiments/engram-portability-v1/`, `experiments/learned-engram-portability-v1/`, corresponding archived resources |
| Engram architecture and budget ablations | `experiments/engram-{ffn-substitution,mla-compression,moe-capacity,placement,sparse-budget}-v1/`, `experiments/lexical-memory-heavy-v1/`, corresponding archived resources |
| Historical DevMind context (EXP1) | `experiments/devmind-pretrain-v0/` through `v5/`, archived historical experiments and `corpora/devmind*`; current `experiments/devmind/` remains intact |
| Historical TinyStories context | `experiments/tinystories-dense-30m-data-rich-v1/`, archived old experiment/sample assets and redundant landing pages; current microlab, worker and ROCm recipes remain |
| Other scaffolds | `examples/cpu-repeatability/`, `examples/lab-job-try/`, `examples/tiny-campaign/`, `examples/training-program/` |

All `provenance/` imports (1,292 files), `catalog/` (8 files), personal
`acceptance/` (14 files), legacy experiment landings/resources (35 files), and
retired example scaffolds/landings (41 files) are removed: 1,390 files total.
These counts describe this retirement only; the pinned snapshot is the exact
file inventory and recovery source. Historical provenance subpaths above are
relative to `provenance/lab/`.

## Retained dependencies and evidence

`examples/synthetic-cpu/`, `examples/tinystories-microlab/`,
`examples/tinystories-worker/`, `examples/tinystories-rocm/`, all of
`experiments/devmind/`, both `results/` directories, `scripts/`, `tests/`,
`examples/operator/` and the offline CI fixtures remain. Their operational
records and safety checks are not replaced by historical links. In particular,
LAB86 sources, controls and pilot templates retain merged PR38. This cleanup
only adds the full-session limitation pointer to its README and refreshes that
README hash. The old TinyStories entry URL remains a short redirect so recorded
result documents stay byte-identical.

The synthetic CPU example remains measured at its historical pin and supported
for current native metadata authoring/inspection. The current metadata route is
not a claim of a newly executed end-to-end run. Its original monitored workflow,
limits, failures and replay evidence remain available. No runtime was provisioned
or workload executed for retirement.

The personal memory-study per-candidate acceptance obligation is retired with
that collection. Lab's neutral identity, provenance, refusal and verification
regressions remain Lab-owned and unchanged. Historical acceptance/audit JSON is
not rewritten to suggest new acceptance. The prior ownership audit is a dated
snapshot; its retired repeatability entries are no longer a migration blocker.

## Focused validation

At Lab `0af1683188edacecf0856baa3520354363358f0d`, native recipe creation and
preparation inspection of the retained synthetic CPU declarations passed using
the documented current bindings. No payload directory was created. Existing
Python 3.14.4 was used; no packages or models were installed.

Offline retained fixtures: root suite 52 tests (51 passed, one explicit companion
Harness integration skip), ROCm helpers 27 passed, TinyStories worker 16 passed.
These exercise metadata/adapters with tiny fixtures, not accelerator work.
All 145 LAB86 manifest hashes match. Retained scripts/tests, operator templates,
synthetic declarations, result records and non-document TinyStories/DevMind inputs
retain their bytes; the pilot template matches merged PR38.

Current navigation has no unresolved local links. Eight pre-existing Lab-relative
links inside the byte-authenticated copied microlab `declarations/README.md` and
`declarations/acceptance.md` retain their original meaning: read them in the
[original Lab tree](https://github.com/supernovae/tiny-sparse-lab/tree/eab014ef7ca92de89d37b47c30df2ebf021d9473/experiments/samples/tinystories-microlab).
Their `migration.json` hashes are unchanged; they are historical source documents,
not the current run guide. The ownership JSON is also an unchanged dated audit.
