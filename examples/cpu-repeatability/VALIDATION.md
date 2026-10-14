# Static and unit qualification

No tokenizer fitting, training, runtime probe, evaluation, acquisition or acceptance
run was executed. Unit fixtures are authored report projections and tiny temporary
SQLite/filesystem records, not scientific evidence. No Lab test helper is imported.

Run the local tests without installing dependencies:

```sh
python -m unittest discover -s examples/cpu-repeatability/tests -v
python examples/cpu-repeatability/tests/mutation_check.py
```

The preserved first checker qualification passed 12 test methods and killed all
26 `_require` call-site removal mutations. The expanded local suite currently has
24 test methods. Subtests independently invalidate every material pin/refusal.
The mutation tool changes temporary copies only, uses the selected interpreter,
and runs only checker unit tests. It does not mutate Lab or the checked-in checker.
This is statement-removal qualification, not proof against every possible mutation.

| Refusal | Otherwise-valid counterexamples |
| --- | --- |
| Integrity and coverage | Each readiness field independently changed on both sides |
| Cell count/state/seed | Zero/two cells; pending state; wrong seed and non-integer types |
| Training/evaluation pins | Every individual field changed on both sides; missing/extra key shape; bool, string, float, null, NaN/infinity |
| Attempts | Zero/two attempts, failed attempt, empty attempt/run identity, selected-run mismatch |
| Reports | Missing and rejected counts independently changed, including numeric-type confusion |
| Diagnostic | Status and count independently wrong; cell/run linkage; stage; batches/targets |
| Metrics | Loss and perplexity independently bool/string/null/NaN/+infinity/-infinity |
| Mode and identities | Unknown mode; each scientific/source/config/input/suite mismatch; absent/malformed digests and plan identity |
| Replay | Provenance-only changes; attempt/receipt/result/metric changes |
| Fresh repeat | Reused attempt ID with fresh run; reused run ID with fresh attempt |
| Tolerance | Each metric separately at/just outside absolute and relative 1e-6 boundaries |
| Native verification | First and second native read independently refuse; exact triples checked; no output files written |

Redundancy is explicit: once both reports independently pass the fixed cell, seed,
training/evaluation-budget and diagnostic-stage requirements, comparing those fixed
values again adds no independent protection. Such duplicate equality guards were
removed; config/input/suite/scientific/source equality remains required. Replay's
whole-cell/evidence equality intentionally also covers fields compared earlier;
its isolated counterexamples change receipt/attempt/result data instead.
Plan and evidence-index identities must be valid in each fresh root, but are not
required equal across independently authored plans; replay requires all provenance
identical. No normalized/recomputed scientific identity substitutes for native hashes.

Additional tests cover every outer/inner CLI initialization root, independent
command-local work root, both fresh roots, five unique monitor log destinations,
one immutable baseline/root, no replay execution flag and reselected report index.
The command renderer prints JSON argv only; it cannot launch a process. Markdown
CLI examples are checked for both explicit environment root selectors.

Whole-root inventory tests retain all Controller rows, including hidden failed
attempts; refuse an extra Controller database/attempt, wrong run, failed/incomplete
ingestion, changed receipts and added run/pilot/evaluation/probe records. They
check byte-for-byte read-only behavior, exact new-audit allowlists, no changed old
file exceptions, root mismatch, symlinks and uncheckpointed WAL refusal. Inventory
comparison is conservative: operational churn may refuse, never silently pass.
Captured SQLite rows are not a substitute for native evidence verification.

Recipe tests cover inventory byte hashes, unchanged scientific declarations,
explicit absence of invented prepared identities, the nine-stage terminal graph,
and arithmetic of the proposed workloads/deadline reserve. They do not qualify
live wall/RSS/storage supervision: that capability is still missing.

The merged source was read at `d96b0aafda56c3a263a3be83d88e07839e17c3e6`.
A metadata-only check used the existing CPU interpreter with that source selected
solely for schema/parser validation, without installing or changing the runtime.
It loads run/tokenizer/preparation declarations and current admission shapes,
parses every rendered CLI command without calling handlers, and requires the
unprepared workflow template to be refused. This does not qualify an installed
runtime, execute the native verifier on real payloads, or count as acceptance.

To reproduce the optional native metadata check, select a clean checkout of the
exact merged Lab pin as `LAB` and the existing compatible CPU interpreter as `P`:

```sh
PYTHONPATH="$LAB/src" "$P" examples/cpu-repeatability/tests/check_native_metadata.py
```

This is metadata validation only. The actual run must use a qualified installed
runtime at that pin; the command above does not install or qualify one.

## Metadata authoring follow-up, 2026-10-14

The full suite now passes **47 tests in 2.881s** under the existing qualified
Python 3.14.4 CPU venv. See [authoring-test-evidence.txt](authoring-test-evidence.txt).
Eight added tests cover exclusive local checkout and base preservation; wrong
commit/dirty source/missing authority; real native preparation metadata and exact
limits; changed inspection/bindings; exact sealed commit and later-review status;
unrelated changes, identity/binding drift and incomplete receipts; workflow
inspection/resolution matching; and symlink/duplicate-JSON refusal.

Workflow admission unit fixtures stub only the metadata resolver boundary and use
explicit synthetic identities; they do not claim actual payload authentication.
Preparation admission tests use the pinned native metadata API without calling a
CLI handler, tokenizer fitting, preparation, training, probes or evaluation.
The existing checker mutation suite is also retained. No dependencies were added.

The staged/worktree-divergence regression stages an unrelated tracked change and
restores its worktree bytes to HEAD. Refusal preserves HEAD, the index, worktree
bytes and file inventory. The helper requires a clean index before verification
and staging and validates the exact staged set.

No completed-nine-stage regression is claimed, but a pre-existing fixture is not
a run prerequisite. The first approved genuine run supplies evidence; cold verified
completion gates replay with full native records compared before/after. See
AUTHORING.md for the implemented bounded pre-replay helper. No acceptance execution,
or model gate approval occurred in this change. Owner run approval is conditional
on external review and owner-controlled Workshop merge; it does not activate work here.

Five read-only replay-gate test methods cover the explicitly mocked inspector
boundary: complete projection pass/no writes, every incomplete stage/bad next
action, malformed/missing/duplicate/unknown stages, propagated native corruption,
and exact WorkflowExecution.engine(cold_verify=True).inspect("next") selection.
These tests do not run a completed native workflow or stub cold verification while
claiming scientific evidence. Actual first-run evidence supplies that verification.


## Review regression coverage

Review 5524037413 targeted older head 104ebb3. Its six material test gaps are
now independently covered: sealed-file modes (both files), ignored files with a
committed ignore rule, missing/invalid commit authority, admission output inside
the checkout, authoring destination inside the base, and base-as-commit-destination.
Each asserts the specific refusal, avoiding an earlier guard masking the result.
Commit refusal tests also preserve HEAD and the index; ignored evidence is retained.

Independent authority tests cover extra keys, a mismatched approval pin, blank
owner/reference, non-object limits, and boolean limits. Small input tests cover
size, absolute/non-parent paths, full SHA, repository root and submodules.
The existing index-divergence and cold replay gate regressions remain intact.

The native workflow inspection test calls actual pinned inspect_workflow on
synthetically sealed declarations, checks one cell and explicitly unverified
artifact identities, unknown runtime capability, non-executable status and no new
files. It does not call resolve_workflow: real resolution authenticates payloads
which these synthetic identities cannot provide. The admission resolver-boundary
test remains explicitly mocked. Genuine artifact verification comes from the
first approved run, without making a pre-existing COMPLETE fixture a prerequisite.

Run the focused mutation qualification with the same existing interpreter:

```sh
"$P" -B examples/cpu-repeatability/tests/mutation_authoring.py
```

All **16/16 targeted guard mutations** were killed by assertion failures in
disposable temporary copies. See authoring-guard-mutation-evidence.txt. The runner
rejects import/fixture errors as evidence and limits each mutant to 15 seconds.
These are distinct from the existing 26/26 checker mutations, whose evidence is
retained. No production helper changed in this review follow-up.

Concurrent replacement and post-operation race injection remain deferred defense
in depth: exclusive open/mkdir, checkout rechecks and the sanitized Git environment
remain in place, but these tests do not claim adversarial race coverage. The
trusted single-writer boundary remains required. Additional redundant guard
mutations are not a substitute for the isolated material refusal tests above.
