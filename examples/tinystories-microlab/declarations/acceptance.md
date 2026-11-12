# Campaign engineering check, 2026-10-06

On 2026-10-06 we ran the full teaching Campaign with Lab's dataset and
Campaign commands: acquisition, tokenizer fitting, preparation, locking, three
selected training cells, ingestion, held-out evaluation, and a descriptive
generation panel. All 17 selected Campaign stages finished `COMPLETE`. All
three controller entries reported both execution and ingestion `COMPLETE`, with
no ingestion errors. This shows the small teaching workflow runs end to end; it
says nothing about model quality or about running on the full corpus. To try it
yourself, follow the
[walkthrough](https://github.com/supernovae/model-lab/blob/main/docs/tinystories-microlab.md) in a new workspace.

## What ran and where the records are

We launched from commit `fd5b4d501e84d98308faa2fb4e7ba484f57df5b3`, with clean
tracked source; an unrelated untracked research directory was already there
and we left it alone. The final pilots and training used the package source
hash `1a41cd5276a7f4624b273b00aff10d4f57286597402c443d218c7edb751cb0e2`.
Work ran outside the checkout, so the worker manifests have null Git commit and
dirty fields. The launch commit above is our own note and doesn't fill those
fields. For the same reason, the copied teaching configs have their source
recorded as `UNKNOWN`, which we accepted for this run.

Below, `$WORK` means the
`experiments/dataset-contract-acceptance-20261006/` directory under the
persistent root. The generated files stay there and don't ship with this
sample. The config that succeeded was `$WORK/campaign-phased.yaml`, which uses
`inputs/plan-phased.yaml`; the different names keep an earlier failed config
separate. Both mean the same thing as the teaching Campaign and plan checked in
here.

| File | SHA-256 |
| --- | --- |
| Campaign config | `b77744111465b51439ebba3534fb57390f1ef9cb2be6b8e1896e3636b06947bf` |
| ExperimentPlan lock | `8a5362601e82c3dc861d2009d6567463bc58af1d72aad1c47a5a99c0b1460db5` |
| Snapshot manifest | `d29cda007eaad1fefbefb1473a595ee7fefd9b09ba3633d7107d3dbe96e472e5` |
| Frozen tokenizer bytes | `0a68c68df31f793fb8d0bf215f2392d6ab6dd78b3abed636a1b5e6e3b52d2357` |
| Prepared manifest | `fac9d86904fa87556b972f40fa6af5a490bef26d1bd40bdd58716119a0bdc914` |

Campaign receipts are under `$WORK/campaigns/stories-learning/<declaration>/`.
Inside it, `experiments/plan-stories-program/controller/` holds each run, its
checkpoints, and the evaluation and panel indexes; `locks/<lock>.json` ties
them to the resolved plan. `$WORK/acceptance/` keeps Lab's final JSON reports
(Campaign, controller, coverage, budget, runtime doctor, evidence, triage, and
full-checkpoint verification) along with test and orchestration logs.
`stages/{cpu-final,mps-final}/` keeps the pilot bundles and reports, and
`readiness-reviewed/readiness.json` keeps the dense readiness check.

## Inputs and coverage

The source is `roneneldan/TinyStories` on the Hub, default configuration,
pinned to `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`. The configs took 2,000
training and 100 validation documents. Both splits stopped when they reached
their target, with `source_exhausted: false`. This selection had no
duplicates, overlaps, empty or null documents to drop. The 2,048-token
vocabulary was fitted on training documents only. Preparation kept every
document whole.

| Split | Packed tokens | Complete 64-target blocks | Usable supervised targets | Dropped tail targets |
| --- | ---: | ---: | ---: | ---: |
| Train | 470,200 | 7,346 | 470,144 | 55 |
| Validation | 19,015 | 297 | 19,008 | 6 |

Each split also has one initial token with no target. Lab's coverage check
correctly reported a bounded selection with full-source coverage unproven.
We ran `data budget` with an explicit bounded-source override, which wrote
`inputs/bounded-pass-final.yaml`: one pass, 1,837 updates, 470,144 supervised
targets, effective batch four, and two blocks in the final update. We didn't
train that proposal. By default Lab requires full-source coverage, and the
teaching selection doesn't meet it.

## Choosing a device

We staged the same tiny baseline config on the PyTorch CPU and MPS devices of a
macOS arm64 machine, with PyTorch 2.14.0 and Python 3.14.8. Both finished two
smoke updates and five warmup updates. The model and training settings were the
same on both: FP32, sequence length 64, microbatch two, accumulation two, seed
42, hidden width 128, two layers, four heads, and FFN width 256.

| Execution device | Warmup targets/s | Update time after first update (four observations) | Sampled host peak | Sampled device peak |
| --- | ---: | --- | ---: | ---: |
| CPU | 23,959 | 7.73–8.33 ms | 471,187,456 bytes | unavailable |
| MPS | 8,149 | 16.71–27.72 ms | 613,072,896 bytes | 37,519,360 bytes |

These numbers come from five-update pilots, so they don't tell you end-to-end
throughput. Memory peaks were sampled and are lower bounds. Host and device
figures are measured separately; on unified memory, don't add them together as
if they were separate allocations. We picked CPU for this small config; that
choice says nothing about CPU versus GPU in general. The runtime API didn't
expose physical device identifiers, so those fields are null. Preflight
reported enough free storage.

## The training cells

| Cell | Run ID | Cumulative updates | Cumulative targets | Terminal heldout loss |
| --- | --- | ---: | ---: | ---: |
| Baseline | `17a51c67-51be-411e-b3f8-94917fff84b1` | 40 | 10,240 | 7.084726 |
| Exposure child | `16fb47e6-fc5a-4417-9a47-e1c0aabcaac4` | 80 | 20,480 | 6.993053 |
| Fresh wider FFN | `e7533dc2-0d2c-43dd-887c-eb09a6c62e2e` | 40 | 10,240 | 7.027953 |

The child resumed from the baseline's full optimizer state, which had been
verified, and kept the 40-update decay horizon. Its counts include the parent's.
The fresh contrast changed FFN width from 256 to 384 at the baseline budget.
The plan also defines a wider child, but this Campaign didn't select or run it.
We ran one seed only.

Full checkpoint verification passed for every selected final checkpoint,
including the baseline's, which was unchanged after the child continued from it:

| Cell | Terminal checkpoint SHA-256 |
| --- | --- |
| Baseline | `b907b0c6ba660c987f8bf313289186961562acc6ffeb2c086d27acd99aa73480` |
| Exposure child | `1365103b5fc181ede4f892079397fd57c7eca318371ad6575ec225f05a5c38fe` |
| Fresh wider FFN | `ac98642172074185afc65363281e6094a571d126e086ea4796836af6c4c58380` |

Every endpoint used the same held-out suite (four batches, 512 valid targets)
and the same three-prompt descriptive panel (greedy, at most 32 new tokens,
seed 42). That suite is a small sample of the validation snapshot. Lab's
evidence report shows `checkpointed_held_out`, verified checkpoints, and no
missing or rejected reports. Finishing the panel doesn't promote a model.

Lab's triage counted cumulative optimizer time of 0.32149 seconds for the
baseline, 0.64217 for the child (including its parent), and 0.34616 for the
fresh contrast. Those counters leave out preparation, orchestration,
evaluation, and checkpoint time, so don't read them as total workflow time or
add them up as if the runs were independent. The raw triage notes on these
limits are kept with the evidence and checkpoint verification reports.

## Problems we hit, and what's left

- Earlier snapshot commands on the small selection wrote valid outputs but
  hung while Arrow shut down. Switching to the generic synchronous Parquet
  reader fixed process exit; a later live acquisition exited cleanly and
  produced the same bytes. We kept the earlier outputs and attempts.
- The first Campaign config failed before training because its comparison
  named whole config sections instead of the individual settings Lab supports
  holding fixed. The corrected config names valid settings and limits the
  fresh-width comparison to pretraining. The failed config and its receipts are
  kept under their original name.
- On the successful config, the first `apply` returned while the baseline was
  still running, after the controller's wait limit, and the log kept an RPC
  warning. Resuming picked up the same attempt and finished the remaining
  stages without creating a replacement baseline.
- Tests: source acquisition passed (46), the corrected serial integration
  regressions passed (59), and the final comparison/legacy-submission/authority
  tests passed (56). These sets overlap. An earlier broad run had 623 passes,
  one skip, and five failures; we fixed the failures and reran them in focused
  sets, but didn't rerun the complete broad command. Ruff and the dense
  readiness check on the final source passed. Offline Campaign tests cover
  reconciliation, unchanged parent hashes, and reapplying without dispatching
  again.
- Rechecking the snapshot from scratch each time adds a lot of orchestration
  time. [Lab's backlog](https://github.com/supernovae/model-lab/blob/main/ROADMAP.md)
  has a task to reuse verification safely, with checks that catch changes and
  invalidate stale results.
- We didn't try full-source acquisition or training, larger models, more seeds,
  or CUDA, ROCm, XPU or MLX. Each needs its own runtime, storage and
  experiment checks. This run doesn't support any claim about model quality or
  portability.
