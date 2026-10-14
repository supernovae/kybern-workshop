# Metadata authoring for this recipe

`tools/author_inputs.py` supplies four explicit operations for the external harness.
It does not schedule commands, launch Campaign handlers, approve model gates,
train, evaluate, probe devices, install packages or fetch remote sources. Run it
with the already qualified pinned Lab Python. Native admission operations use
metadata/cold-verification APIs, including re-resolving existing prepared inputs.
That authenticates existing bytes; it does not prepare new payloads.

Each operation requires `--base`, `--commit` (full SHA), and `--authorization`
pointing to an operator-provided JSON document:

```json
{"owner": null, "reference": null, "source_commit": null, "limits": {}}
```

This template refuses. Supply an actual approval reference and matching source
commit only after authorization. Text is provenance, not new authority; the helper
cannot authenticate approval offline. Pin the authorization file in the harness
job's required_files. It never substitutes for a later identity-specific native
approve-model decision or external review of a newly sealed workflow commit.

| Operation | Additional arguments | Result |
| --- | --- | --- |
| `author-preparation-admission` | `--bindings`, `--inspection`, `--output` | Exclusive native preparation admission |
| `author-workflow` | `--destination` | Exclusive detached local checkout of exact base commit |
| `commit-workflow` | `--destination`, `--receipt`, `--bindings`, `--logging-root`, `--author-name`, `--author-email` | Local sealed workflow commit requiring external review |
| `author-workflow-admission` | `--bindings`, `--inspection`, `--resolution`, `--output` | Exclusive native workflow admission |

All paths are absolute and nonsymlinked. `--base` is the repository root; the recipe
is fixed at `examples/cpu-repeatability`. Admission outputs stay outside that
checkout. The base must be clean at the supplied commit. Authoring checkout
creation uses only a local fetch from that base, not the network or a shared
object alternate. It preserves a partial destination on failure rather than
deleting evidence or reusing its name. All generated checkout/Git/temp bytes
belong beneath the selected charged work root.

After `author-workflow`, invoke the existing `scripts/seal-inputs.py` with the fresh
COMPLETE preparation receipt. Then `commit-workflow` allows changes only to
campaign.json and workflow.json, reproduces expected bytes through that same
sealer, checks the full supplied artifact identities, generated inventory/bindings
and file modes, and rejects unrelated/untracked/ignored files. The index must be clean before verification and before staging; the staged set must contain exactly the two verified files. Staged/worktree divergence refuses before any commit or index/worktree modification. This is authoring
validation against the supplied receipt, not a replacement for native cold artifact
verification. The commit preserves science/config files and reports
`review_required: true`, `gate_approved: false`. No push or gate approval occurs.
Git identity/hooks/signing options are process-scoped; persistent configuration is
not changed. No locking or concurrency framework is added: use the existing
harness claim and trusted single-writer contract.

For preparation admission the authorization limits must exactly be:

```json
{"max_documents":12,"max_tokens":384,"max_vocab_size":260,"min_free_bytes":1073741824,"min_free_inodes":128}
```

For workflow admission they must exactly be:

```json
{"max_training_updates":8,"max_target_positions":128,"max_eval_batches":1}
```

The last limit is per evaluation pass, not the cumulative 24-batch pair budget.
Checkout/commit operations require an explicit limits object but grant no compute.
Inspection JSON must exactly match current native inspection (normalized to CLI
JSON representation). Workflow resolution JSON must match a fresh native resolution
of the same inputs. The public resolution output contains plan/scientific hashes,
not recipe/binding hashes; therefore merely trusting two captured hash strings
would be insufficient. The reviewed commit, actual `sys.executable` and native
identities are placed in the admission and validated by native admission models.

The external planning bundle's eight helper slots map one-to-one to these four
operations for roots A and B. Activate those argv only after this helper's exact
commit is reviewed, the helper/code/authorization bytes are pinned, and all dynamic
native inputs exist. No acceptance run has occurred.

## Genuine-run evidence gates bounded replay

The first explicitly approved run supplies genuine COMPLETE evidence. A pre-existing
COMPLETE fixture is not a prerequisite for that first run. Before replay, cold-verify
the exact nine stages and actual identities, require all COMPLETE and next_action
none, then compare full native attempts, receipts, Controller and evaluation records
before/after. Incomplete or corrupt evidence must stop replay.

At pinned Lab d96b0aaf, projection cold-verifies COMPLETE rows; apply returns before
dispatch when next_action is none. The flag --execute-runs absent alone is insufficient:
submitted incomplete runs may reach Controller.tick and ready evaluations may call
run_suite. This is a reviewed code-path argument, not RSS sampling or continuous
tracing. No mocked cold verification is evidence for this guarantee.

The read-only preflight must use WorkflowExecution with the exact source, bindings,
work root and admission, then its cold-verifying engine.inspect("next"). Plain
Campaign CLI inspection lacks portable workflow context; inspect("status") can
return persisted state and is not a substitute. Assert the exact nine stage IDs,
all COMPLETE and next_action.action == "none", without calling apply or adapters.
Place this preflight, inventory-before and single-attempt-before ahead of replay.
Pin verified state/receipt bytes in the replay job and keep the trusted single-writer
boundary. Re-select returned native identities for post-replay reports. Any failed
check stops acceptance without retry.

The command is tools/replay_ready.py, using the qualified Python and exact
--source Rflow/workflow.json --bindings W/workflow-bindings.json --work-dir W
--admission W/workflow-admission.json. It prints a readiness envelope containing
the verified native projection, and exits nonzero on incomplete/corrupt evidence.
It neither writes work files nor calls apply, resume, dispatch, tick or run_suite.
The session declares one 60-second readiness slot per root, before inventory-before
and single-attempt-before, all inside the existing 3600-second clock. The gate and
its author_inputs.py import must be pinned in the job. A fenced regression
may derive from the first genuine COMPLETE evidence inside declared bounded helpers.
Existing native fixture setup prepares/trains workloads, so no completed-nine-stage
regression was run or claimed in this change. It is additional qualification, not
a circular prerequisite for the first run. No run approval has been recorded.

Gate unit qualification uses an explicitly mocked inspector boundary. It covers
each incomplete stage, missing/duplicate/unknown stage IDs, bad next actions,
propagated native-corruption refusal with no readiness output, unchanged fixture
files and the exact cold-next API call. It is not faithful completed native
execution and does not claim real payloads were cold-verified during tests.
