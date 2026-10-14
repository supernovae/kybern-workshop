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
and file modes, and rejects unrelated/untracked/ignored files. This is authoring
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

## Replay regression remains blocked on a faithful fixture

The required criterion remains: all nine stages verified COMPLETE, a reviewed
no-dispatch test, and unchanged native receipts/attempts/Controller/evaluation
records. It is a pinned-code-path argument, not continuous tracing or RSS sampling.

At Lab d96b0aaf, CampaignEngine._project_once cold-verifies COMPLETE rows and leaves
next_action=none; apply returns before dispatch. Invalid completed evidence raises.
But --execute-runs absent alone is insufficient: a submitted incomplete run can
reach Controller.tick and a ready evaluation can call run_suite.

No faithful completed-nine-stage regression was added or claimed in this change.
The existing tests/test_workflow_recipe.py native_workflow fixture calls
train_tokenizer and prepare_data. The complete publication fixture in
tests/test_publication_report.py calls trainer.train. Existing static contract
JSONs are not a complete authenticated nine-stage Campaign/checkpoint/evaluation
snapshot. Reusing those setup routines would exceed the no-workload test scope;
stubbing cold verification would not establish the requested guarantee.

Minimal next step: the Lab owner supplies a reviewed, tiny self-contained COMPLETE
fixture that cold-verifies without workload setup (or separately authorizes its
creation). A fixture test can then call the actual pinned apply(resume=True,
execute_runs=False) with dispatch, Controller submit/tick and run_suite fenced to
fail, assert next_action=none and unchanged records, and corrupt completed evidence
to assert refusal with zero dispatch. Until that is reviewed, end-to-end acceptance
remains unexecuted and the no-dispatch-regression prerequisite remains open.
