# CPU repeatability recipe — not yet executed

Exercise the current Lab preparation → approval → training → diagnostic evaluation
→ terminal evidence → verified reporting path, then check replay and an independent
repeat. This small project tests that Workshop experiments can run reproducibly
through public Lab interfaces. It is not a model-quality benchmark.

**Readiness: authored scaffold and unit-tested checks; launch blocked.** No current
preparation, training, evaluation or replay has run. The historical synthetic proof
is separate and unchanged. [Workshop projects](../../README.md).

## Pins and prerequisites

[ pins.json ](pins.json) records merged Lab commit
`d96b0aafda56c3a263a3be83d88e07839e17c3e6` (PR133, reviewed head
`8ce8f04a02bd8a5e687bb661c07efa4e05bc1fb2`), the lock-file digest and exact declared
file hashes. Merge status was verified through GitHub. The previously inspected
candidate `596c0f6e…` differs from this merge only in acquisition tests.
The project starts at Workshop `a0f6f95ba67a1127d0d5404aba5113233e0c1fd5`.
Record the eventual reviewed Workshop preparation and workflow commits separately.

The existing installed CPU environment still targets historical Lab `b155cdcc…`.
It is **not ready for this run**. No runtime was installed or changed here. Before
execution, obtain approval for any environment change, verify the clean merged
source and installed package/lock versions, and freeze its native installed-source
identity and exact Python executable (`P`). Do not substitute `PYTHONPATH` source
selection for a qualified installed runtime in the actual experiment.

Recipe-specific expectations and checks live here; Lab remains responsible for
native execution, locking, cold verification, ingestion, diagnostics and reporting.
The recovered proposal/checker came from Lab `4f703c7a…`; attribution is retained in
[LICENSE.upstream](LICENSE.upstream). The [review](https://github.com/supernovae/tiny-sparse-lab/pull/133#pullrequestreview-5521617890)
identified unqualified refusal paths; see [validation](VALIDATION.md).

## Authored science and identities

The run, tokenizer, plan, suite, preparation graph/descriptor and monitor bytes
match the historical synthetic declarations. Their internal IDs remain unchanged;
isolated work roots distinguish executions. Keeping these bytes does not reuse
historical payloads, native hashes, admissions or receipts.

`campaign.json` now has nine stages: `token`, `packed`, `lock-plan`, `accept-cpu`,
`approve-model`, `train-once`, `collect-run`, `evaluate-heldout`, **`final-evidence`**.
The terminal collection depends on the plan, training and evaluation, and names
`evaluations: [evaluate-heldout]`. Reporting selects this terminal index, not the
pre-evaluation collection index.

**Intentional incomplete inputs:** `campaign.json` has null artifact references
and `workflow.json` has an empty artifact map. These are not valid admitted native
workflow documents yet. No placeholder hash masquerades as prepared evidence.
After successful native preparation, the existing [seal helper](../../scripts/seal-inputs.py)
copies the two COMPLETE native identities and regenerates workflow inventory bytes.
Native inspect/resolve must then cold-verify them. The helper is not a verifier.
The preparation descriptor is complete for review; the workflow must be authored
and committed after fresh preparation before admission.

The checker records/compares native scientific, source, config, tokenizer, prepared
input and diagnostic-suite identities. Each plan and evidence-index digest must
be present and valid. Plan/index digests can differ between independently authored
fresh roots; replay requires exact provenance equality. No scientific hash is
recomputed to force equality. Each root needs its own reviewed workflow commit.

## Proposed workload and finite limits

[envelope.json](envelope.json) is a proposal, not authorization.

| Work | Per fresh root | Two sequential roots |
| --- | ---: | ---: |
| Main training | 1 update / 16 positions | 2 / 32 |
| Smoke and warmup | 2 + 5 updates / 112 positions | 14 / 224 |
| Total training | 8 updates / 128 positions | 16 / 256 |
| Training validation | 3 smoke + 6 warmup + 2 main batches / 176 targets | 22 / 352 |
| Held-out diagnostic | 1 batch / 16 targets | 2 / 32 |
| Total evaluation | 12 batches / 192 targets | 24 / 384 |
| Tiny optimizer probes | Expected 6 | Expected 12 |
| Native model attempts | Exactly 1 | Exactly 2, distinct IDs |
| Monitored commands | 5 | 10 |

Seed 7; synthetic data seed 7; one layer, hidden 16, FFN 32, two heads, context 32,
vocabulary 260, dense CPU PyTorch FP32, no memory; sequence 16, microbatch 1,
accumulation 1. Preparation caps: 8 train/4 validation documents, 256/128 tokens;
train-only tokenizer fitting uses at most 8 documents. Native smoke/warmup remain
2/5; optimizer warmup is separately zero. Validation runs initially and after each
update. The tiny runtime probe updates a 4×4 parameter once; count it separately
from training positions. Expected current probe sites are worker validation, stage
validation, smoke/warmup/main initialization and diagnostic engine validation.
Actual observed counts must match; expectations are not evidence.

Preparation admission uses `max_documents: 12`, `max_tokens: 384`,
`max_vocab_size: 260`, `min_free_bytes: 1073741824`, `min_free_inodes: 128`.
No snapshot limits or acquisition grants. Current workflow admission uses
`limits: {max_training_updates: 8, max_target_positions: 128, max_eval_batches: 1}`.
The evaluation limit is per pass, not a cumulative ledger. Preparation bindings and
admission have no obsolete version field. Workflow admission has `limits`, not
`workflow_admission_version` or `pair_limits`; workflow **bindings** still use
`workflow_bindings_version: 1` as generated by the helper.

One whole window starts immediately before the **first** baseline: 3,600 elapsed
seconds including operator waits, metadata, authoring/review, reporting and shutdown.
Stop work by 3,590; zero descendants by 3,600. Never begin a 600-second command unless
600 seconds plus the 10-second reserve fit before 3,600 (start at elapsed ≤2,990).
Five monitored commands/root: preparation, plan, approval, execution, replay.
No retries or parallel roots. Replay adds zero training, evaluation or probes.
Concurrent tree RSS ceiling: 4 GiB. Retained totals: 1 GiB/root, 2 GiB aggregate,
including baseline, payload, state, logs, inventory and reporting artifacts.
No deletion, shrinking, rebaseline or movement of files replenishes limits.

**Missing enforcement mechanism:** the merged public `monitor` applies limits to
one child process tree and added bytes against one baseline. It cannot maintain
this cross-command deadline through waits, refuse the next launch against that
deadline, jointly account retained bytes in two roots, or own shutdown while no
command is running. A baseline per command would hide cumulative growth; this
recipe requires one immutable baseline/root, but that still does not enforce
retained totals. Integration with the owner-designated
[lab-harness](https://github.com/supernovae/lab-harness) is pending its stable public
interface. That separate project owns launch/timeout/logging/manifest plumbing;
Workshop must not implement a competing supervisor.
Required interface: persistent monotonic session deadline; two fixed roots;
immutable storage origin; retained byte/RSS observations; prelaunch allowance plus
shutdown reserve; stop propagation and descendant cleanup receipt. This project
has no second scheduler or execution engine. Its read-only inventories are not
that enforcement mechanism. No finite-envelope acceptance may be claimed yet.

## Preparing each fresh root (future approved execution only)

Use sequential external roots `W_A` and `W_B`, outside all Git repositories, with
no symlink/overlap or existing operational stores. Use separate committed recipe
worktrees per repetition. Preserve preparation checkout A while authoring workflow
checkout B: changing HEAD invalidates the preparation admission. Preserve both
repetitions' histories and all failures. No copying caches or prepared payloads.

For the selected root, `W` is absolute; `R` is its committed recipe directory;
`P` is the approved absolute CPU interpreter; `WORKSHOP` is its reviewed checkout.
Keep all generated paths below W. Check free bytes/inodes before the timed window.
Use the same per-root lease namespace throughout; first establish that no other
worker owns work, rather than using another namespace to bypass leases.
Set OMP/MKL/OpenBLAS threads to 1, hide CUDA, and enable HF/Transformers/UV offline
flags; the command renderer includes these exact per-command environment values.
No corpus or model acquisition is part of this project.

Author external `preparation-bindings.json` mapping:

```json
{
  "artifacts": {},
  "config_paths": {
    "tokenizer-config.json": {
      "output_dir": "/absolute/W/payload/tokenizer",
      "dataset.cache_dir": "/absolute/W/payload/cache"
    },
    "run.json": {
      "tokenizer.path": "/absolute/W/payload/tokenizer/tokenizer.json",
      "dataset.cache_dir": "/absolute/W/payload/cache",
      "logging.root_dir": "/absolute/W/payload/runs"
    }
  },
  "acquisitions": {}
}
```

Native inspect provides recipe/binding digests. Admit only exact committed bytes,
the exact interpreter, and the ceilings above; never guess inspection identities.
Every CLI invocation needs both initialization-root and worker-lease selectors.
Positional `monitor-baseline` root and `monitor --workspace` do **not** select CLI
initialization scratch. Keep recipe operation `--work-dir` independently.
For example, with the renderer's offline/thread settings also applied:

```sh
env SPARSELAB_WORK_DIR="$W" SPARSELAB_WORKER_LEASE_DIR="$W/worker-leases" \
  "$P" -m sparselab monitor-baseline "$W" --output "$W/storage-baseline.json" --json
env SPARSELAB_WORK_DIR="$W" SPARSELAB_WORKER_LEASE_DIR="$W/worker-leases" \
  "$P" -m sparselab experiment recipe preparation inspect "$R/preparation.json" --bindings "$W/preparation-bindings.json" --json
```

[tools/commands.py](tools/commands.py) prints the exact argv/environment sequence
without executing anything. It covers the single persistent baseline, inspect,
five monitored commands, resolve, JSON/Markdown reports and replay. It always
sets both root selectors on outer monitor and inner Lab commands. Print a proposed
command list (the lock/index arguments are not known until native output exists):

```sh
"$P" "$R/tools/commands.py" --python "$P" --recipe "$R" --work "$W" \
  --lock "$LOCK" --experiment "$EXPERIMENT" --index "$INDEX"
```

This is not an executable batch: stop between phases for native identities,
commits and actual approval. Prelaunch supervision is a prerequisite even for the
baseline. Require preparation's two stages COMPLETE; use
`$W/logs/preparation/command.stdout.log` as the native preparation receipt, not the
monitor completion summary. In the workflow authoring checkout:

```sh
"$P" "$WORKSHOP/scripts/seal-inputs.py" \
  --receipt "$W/logs/preparation/command.stdout.log" --recipe "$R" \
  --bindings "$W/workflow-bindings.json" --logging-root "$W/payload/runs"
```

Commit workflow B before inspect/resolve and admission, retain A, and update R to B
in the command list. Current workflow admission fields are `reviewed_commit`,
`recipe_sha256`, `binding_sha256`, `cpu_python`, `limits`. First apply must stop at
`approve-model`; review its exact lock/runtime evidence before explicit approval.
Only execution uses `--execute-runs --max-wait-seconds 540`. Require all nine stages
COMPLETE and one completed, ingested attempt. Derive `LOCK` and `EXPERIMENT` from
`lock-plan` availability and `INDEX` from **final-evidence** availability. Render
report argv using those exact paths. Reports are evidence-only; retain JSON and
Markdown. Do not overwrite any existing report or receipt.

## Replay, full inventories and fresh repeat

Selected native snapshots cannot establish that no unselected attempt exists.
At quiescent boundaries with zero descendants, [inventory.py](tools/inventory.py)
hashes **every** file/directory and reads **every** SQLite table, including every
Controller attempt without joins or state filters. It refuses symlinks, changing
files and uncheckpointed WAL/journal databases; it never checkpoints, repairs or
modifies the store. If native shutdown leaves a nonempty WAL, stop and request a
supported stable read-only export; do not force a checkpoint or ignore the WAL.

Prepare the audit directory before capture. Capture output in memory so shell
redirection does not create an empty self-inventoried file during traversal:

```sh
BEFORE=$("$P" "$R/tools/inventory.py" capture "$W")
printf '%s\n' "$BEFORE" > "$W/audit/before.json"
```

Take before capture after the before-replay reports and retain all pilots/main
manifests, Controller rows, Campaign receipts, checkpoint/evaluation files and
monitor/probe observations. Execute the fifth monitored command, `resume` **without**
`--execute-runs`. Retrieve returned lock/workspace/terminal index again. Re-render
post-replay report commands with these returned paths—do not feed the old index
twice as a substitute for observation. Then capture after inventory similarly:

```sh
AFTER=$("$P" "$R/tools/inventory.py" capture "$W")
printf '%s\n' "$AFTER" > "$W/audit/after.json"
"$P" "$R/tools/inventory.py" single-attempt "$W/audit/before.json" --attempt-id "$ATTEMPT" --run-id "$RUN"
"$P" "$R/tools/inventory.py" single-attempt "$W/audit/after.json" --attempt-id "$ATTEMPT" --run-id "$RUN"
```

`ATTEMPT` and `RUN` come from the native verified report. Require exactly one
COMPLETE/COMPLETE-ingested row across **all** Controller tables both times. Compare
full inventory with `inventory.py replay BEFORE AFTER`. Supply repeated
`--new-audit-path` only for exact new audit/report and replay-monitor paths (including
new directories) produced by the documented commands. No globs, deleted/changed
old files, database mutations or new run/pilot/evaluation/receipt files are allowed.
`audit/before.json` is one such new file; the after capture predates its own output.
The after output and all later check outputs still count toward retained limits.
Operational state churn can conservatively refuse this strict check; stop for
native interpretation, never broaden exclusions just to get a pass.

The inventory check proves unchanged persisted state. Combine it with the reviewed
pinned Lab code path: cold-project the actual portable workflow context before
replay, require all nine stages COMPLETE and next_action none, and stop on incomplete
or corrupt evidence. Verified completion returns before dispatch. Compare full native
attempts, receipts, Controller and evaluation records before/after, using newly
returned report identities. No continuous tracing or pre-existing COMPLETE fixture
is required: the first approved genuine run supplies evidence. See AUTHORING.md
for the preflight API and remaining bounded helper mapping. The absence of
--execute-runs alone is not a no-dispatch guarantee for incomplete state.

Run the native-verifying selected-snapshot checker as well:

```sh
"$P" "$R/tools/check_repeat.py" replay \
  --left "$LOCK_BEFORE" "$EXPERIMENT_BEFORE" "$INDEX_BEFORE" \
  --right "$LOCK_AFTER" "$EXPERIMENT_AFTER" "$INDEX_AFTER"
```

After an independent approved fresh-root sequence in B, compare A's and B's
terminal native snapshots with `repeat` (same triples, independently selected).
`check_repeat.py` reopens locks and selected evidence through Lab's
`build_publication_report`; it does not accept caller-authored reports at the CLI,
collect work or weaken native refusal. Require different attempt **and** run IDs,
matching scientific/source/config/input/suite identities, and finite diagnostic
loss and perplexity each within fixed **absolute OR relative 1e-6** tolerance.
`PASS` is explicitly scoped to selected verified snapshots, never whole-run
acceptance. Retain the full inventories and observed workload accounting too.

## Completion and remaining scope

Deliver exact Lab/Workshop/runtime pins, clean status, both sets of admissions,
preparation identities, command argv/environments, all native attempts/pilots,
terminal indices, reports, checker results, before/after full inventories,
whole-window and per-command wall/RSS/retained-byte observations, probe counts and
zero-descendant receipts. Preserve failed outcomes; no retry in this envelope.
This branch does not launch work, install dependencies, repair hosts or alter holds.

Still outstanding even after a successful synthetic repeat: controlled snapshot
pairs; acquisition/reuse/cancellation; interrupted continuation lineage/accounting;
real TinyStories CPU/GPU portability; staged retirement of old references/tests.
The held TinyStories draft and every historical result remain unchanged.

## External harness metadata authoring follow-up

[AUTHORING.md](AUTHORING.md) documents the four recipe-specific metadata operations
in `tools/author_inputs.py`, their exact approval/identity inputs, and the eight
per-root helper slots they close. The helper does not launch or approve native
work. End-to-end acceptance remains unexecuted. The first approved genuine run
supplies evidence for the cold verified-completion replay gate; no pre-existing
COMPLETE fixture is required. See AUTHORING.md for sequencing and remaining mapping.
