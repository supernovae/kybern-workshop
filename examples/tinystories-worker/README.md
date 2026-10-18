# TinyStories CPU workflow reference

For the question, GPU setup, local experiment and interpretation, start with
[the TinyStories experiment guide](https://github.com/supernovae/kybern-workshop/tree/fd259e2cad4e9856d6d659e8df34728a98b32502/examples/tinystories/README.md). This page preserves
the advanced CPU Campaign/handoff contract and its original authoring context.
It is not the GPU execution interface.

The [first CPU container smoke](../../results/2026-10-15-tinystories-smoke/README.md)
completed on 2026-10-15 at Lab `66ff9d71423e961ee15aed2267902164f04514c6` with
fresh writable prepared-cache reuse. These checked-in templates were originally
authored against Lab `d96b0aafda56c3a263a3be83d88e07839e17c3e6`; the measured run used
separately committed preparation/workflow declarations linked in that result.
The original owner reference `Sentinel:2b90fc486d3081918878ba99285a8a14` is historical
provenance for LAB-80, not authorization for a reader's new execution.

The dataset is `roneneldan/TinyStories` at
`f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`. No model download is needed.

## Exact scope

| Item | Limit |
| --- | --- |
| Dataset bodies / cache | 314572800 bytes each (300 MiB), two transfers, two cache files, zero shard retries |
| Selected stories | 64 train, 16 validation; native deduplication |
| Tokenizer | vocabulary 512, at most 64 training documents |
| Pair | seed 7, CPU fp32, one layer, hidden 32, two heads, FFN 64 versus 96 |
| Training | sequence 32, batch 1, accumulation 1; each arm smoke 2 + warmup 5 + main 1 = 16 total updates, 512 target positions |
| Evaluation | one batch per evaluation; 12 batches per arm including pilot/initial/main/heldout = 24 total, 768 target positions |
| Whole assignment | 3600 seconds including helpers, waits, cleanup and evidence; 4 GiB observed tree RSS; 2 GiB aggregate retained output |

The dataset scan ceiling is 1024 records per split; selected text is at most 1 MiB,
with 64 KiB per record. Token packing ceilings are 262144 train and 65536 validation
tokens; these bound prepared input, not training. Packing refuses if it would cut
a selected story. Smaller/insufficient/duplicate data is a failed preparation,
not permission to expand selection or fetch additional shards.

Native `max_eval_batches=1` is **per evaluation pass**, not an aggregate counter.
The 24-batch total follows this exact graph and pilot schedule. Do not add `try`,
extra probes, evaluations, repeatability arms, or retries. This is an integration
diagnostic, not a quality comparison with useful statistical power.

## Original supervisor requirements (historical)

At initial authoring, harness `ac45e7aea69169cc6854bc14745ac57ffeca1391` had a session
validator that requires 26 ordered slots for two separate repeatability roots.
Its Workshop adapter accepts the older offline `python -m sparselab` argv shape.
That version cannot directly consume this single-preparation, two-cell acquisition handoff.
The later CPU result used a later supervisor; the constraints below
explain the original handoff rather than a current blanket launch blocker.
Do not pad it with a second experiment or bypass it with independent per-command
timeouts. `monitor.json` alone also does not enforce one clock across commands
and operator waits.

For a new managed execution, qualify an existing compatible reviewed supervisor on
the selected CPU worker. It must retain
the same origin/deadline, observe all roots/caches/receipts and helper processes,
preserve real exit/signal/partial evidence, and verify descendant cleanup. It must
honor the fresh native lease/claim and existing holds. No runtime installation,
host change, GPU use, stale-claim stealing, or local 5900x execution is authorized
by these files. Worker Python/package/source pins and filesystem capabilities
must be verified there; local fixture validation is not worker qualification.

RSS and retained-storage observation can overshoot between samples. Neither is a
hard quota; unsupported requested hard guarantees must refuse. Native acquisition
counts HTTP response bodies, not all wire bytes. Source-lock discovery uses Hub
metadata without dataset bodies; it does not inherit the bounded acquisition
metadata ledger. Its cache, time and memory still belong to the shared supervised
envelope. Refuse if the requested guarantees cannot be provided.

## Author and review, then hand off

`handoff.py` never launches Lab. It copies JSON declarations into **fresh** output
directories, copies native identities, authors admissions, or prints exact argv
arrays. It neither implements Lab's engine nor posts to any external service.
Keep all runtime bindings, admissions and payloads outside source checkouts. Only
the generated recipe declarations/identities belong in their review branches.
Place each generated recipe in its own review checkout beneath the charged work
root (for example `work/preparation-review/recipe`); keep the work root itself
outside Git. The upcoming LAB-80 harness profile supplies the bounded commit helper
and one-clock binding procedure. This does not release launch before its review.
Any failed authoring leaves its partial output for inspection; choose a new path.

The following are argument arrays, not shell scripts. Replace the illustrative
absolute `/worker/...` paths with chief's qualified paths. Supply the same venv
entry point throughout; do not resolve it to the system Python. Collect stdout
and stderr separately through the supervisor. Never concatenate argv into a shell.

1. Render the native command list with the reviewed helper:

```json
["/worker/venv/bin/python", "-B", "/worker/reviewed/examples/tinystories-worker/handoff.py", "commands", "--python", "/worker/venv/bin/python", "--recipe", "/worker/reviewed/examples/tinystories-worker", "--work", "/worker/lab80"]
```

The renderer returns `{steps: [{step, argv}], execution_enabled: false, ...}`.
This is a manual handoff, not an executable batch or the older harness adapter's
input format. Do not pipe it to an executor. Chief first binds the real reviewed
runtime, work paths, approval and one-hour supervisor spec, and commits those job
specs. All subsequent work and review waits count against that same deadline.

2. Submit only `source-lock` through that supervisor. It calls native `data lock`,
which discovers metadata without dataset bodies. Use its real `source.lock.json`:

```json
["/worker/venv/bin/python", "-B", "/worker/reviewed/examples/tinystories-worker/handoff.py", "bind-preparation", "--recipe", "/worker/reviewed/examples/tinystories-worker", "--source-lock", "/worker/lab80/source.lock.json", "--destination", "/worker/lab80/preparation-review/recipe", "--work", "/worker/lab80", "--bindings", "/worker/lab80/preparation-bindings.json"]
```

The helper verifies the native lock, the exact source declaration, first-file size
sum, content digests, and **exactly one validation file**. Native traversal visits
validation first. With one validation file and two total transfers/cache files,
only the first training file can then be fetched; a second training file refuses.
If this proof does not hold for the actual lock, stop. Never edit or trim the native
inventory to make it pass. `first-files.json` pins both exact paths, sizes and LFS SHA256 values from the
[primary Hub metadata](https://huggingface.co/api/datasets/roneneldan/TinyStories/tree/f54c09fd23315a6f9c86f9dc80f725de7d8f9c64/data?recursive=false&expand=false)
relayed by the owner coordinator. Their total is 258720238 bytes. No payload was
downloaded; the worker must verify the actual native lock against these pins.

3. Commit the generated preparation recipe on a normal review branch and obtain
external review. Re-render with `--recipe /worker/lab80/preparation-review/recipe`.
Run `preparation-inspect`. Author its admission using the **actual reviewed SHA**:

```json
["/worker/venv/bin/python", "-B", "/worker/reviewed/examples/tinystories-worker/handoff.py", "admission", "--phase", "preparation", "--recipe", "/worker/lab80/preparation-review/recipe", "--reviewed-commit", "REPLACE_WITH_EXTERNALLY_REVIEWED_40_HEX_COMMIT", "--bindings", "/worker/lab80/preparation-bindings.json", "--output", "/worker/lab80/preparation-admission.json"]
```

The helper requires a clean checkout at that SHA and uses native inspection hashes
and native admission validation. It does not attest that review actually happened.
Commit the resulting operational job spec with runtime pins before submission.
Only after chief's fresh authorization check submit `preparation-apply`, which
performs snapshot acquisition, tokenizer fitting and packing. Require all three
native stages COMPLETE, not merely process exit zero. Preserve acquisition counters
and actual file identities. Do not submit preparation `resume` after a failure.

4. Save the genuine native preparation JSON as `/worker/lab80/preparation-result.json`.
Author the paired workflow in another fresh review location:

```json
["/worker/venv/bin/python", "-B", "/worker/reviewed/examples/tinystories-worker/handoff.py", "seal-workflow", "--recipe", "/worker/lab80/preparation-review/recipe", "--receipt", "/worker/lab80/preparation-result.json", "--destination", "/worker/lab80/workflow-review/recipe", "--work", "/worker/lab80", "--bindings", "/worker/lab80/workflow-bindings.json"]
```

Commit and externally review the generated recipe with native artifact identities.
Re-render against `/worker/lab80/workflow-review/recipe`; submit `workflow-inspect` and
`workflow-resolve`. Author `admission --phase workflow` using that reviewed SHA,
the workflow bindings and `/worker/lab80/workflow-admission.json`. Native resolution
cold-verifies prepared artifacts; no placeholder digest is admission evidence.
The helper checks both resolved cells' exact smoke/warmup/main and per-pass
evaluation schedule and refuses any projection other than 16 updates, 512 training
targets and 24 evaluation batches. Native admission still uses its real per-pass
limit of one batch. There is no native aggregate-evaluation counter; retain actual
runtime counts and fail the acceptance audit if they exceed the approved total.

5. Submit `workflow-apply`; inspect the exact native pending gate and plan. Only
with chief's confirmed assignment/approval submit `workflow-approve`, then
`workflow-run`. This is one serial native pair, not two separate `try` jobs. The
native wait ceiling is 3600, but the outer supervisor must impose the **remaining**
shared allowance including shutdown reserve. If it cannot fit, stop; do not reset
the clock. Every retry requires a fresh authorized job.

6. Obtain the actual experiment lock path, workspace and evidence index from
native receipts. Render again with all three options `--lock`, `--experiment`,
`--index`, then submit `workflow-report`. The report writes `/worker/lab80/report.json`.
Retain native outputs, acquisition/preparation receipts, both attempt outcomes,
stdout/stderr, actual training/evaluation counts, and the supervisor's cleanup,
resource and artifact evidence. Stop on any native FAILED/INTERRUPTED/BLOCKED state;
preserve partial evidence. No automatic replay, resubmission or external posting.

## Local verification

Tested with the already installed Lab d96 runtime, Python 3.14.4 on Ubuntu 26.04
WSL2. Sixteen tests cover native JSON/config/CLI inspection, serial pair metadata,
lock/budget refusals, reviewed-pin mismatch, incomplete receipts, path refusal,
no-clobber, unsupported hard limits and literal argument bytes/exit status in tiny
fake children. Tests mock source metadata and do not import Lab test helpers.
They do not acquire data, fit a tokenizer, dispatch a model, or certify cleanup
behavior of an as-yet unqualified external supervisor.

```text
/existing/pinned/python -B -m unittest discover -s examples/tinystories-worker -p test_handoff.py -v
```
