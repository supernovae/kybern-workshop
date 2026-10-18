# Retained operator dependencies

The current showcase scope is recorded in [the retirement map](retired-research.md).
The JSON ownership audit is an unchanged historical snapshot, not a current file
inventory. CPU-repeatability helpers are retired with that scaffold; their personal
repeat policy is not a prerequisite for the three retained families. All remaining
operator and TinyStories helpers/tests are preserved byte-for-byte.

The public entrypoint is [native Lab](native-workflow.md). This audit inventories
all 27 tracked Workshop Python files at
`0f1bbaec53540c7d2b6ed23d7306d352ad83a7c4`; exact paths, byte lengths and SHA256 are
in [the machine-readable map](ownership-boundaries.json). The retired repeatability group is available in Git history; the remaining helper
bytes are unchanged. No claim of a completed generic capability migration is made.

| Existing group | Guarantees that must survive | Existing native evidence to inspect | Small next slice / blocker |
| --- | --- | --- | --- |
| TinyStories worker handoff and tests | Pinned source selection, generated tokenizer/prepared-data identities, fresh paths, aggregate pair/pilot/evaluation budgets | Lab `test_workflow_pair` limits and graph connections, preparation and artifact verification; native bind-inputs/inspect/resolve | Remove one binding step only after proving the native path preserves actual identity checks; the pinned recipe’s counters are scientific declarations, not reusable Lab defaults |
| ROCm handoff/binding/checks and tests | Prepared-source closure, bounded safe copy, cgroup/approval binding, same-owner deadline, report paths | Native artifact/checkpoint verifiers and Campaign validation; Harness policy/session binding and owned-cleanup tests | CPU metadata coverage does not replace ROCm runtime qualification or prove native/Harness staging equivalence; keep the existing helper bytes until the particular boundary is covered |
| `scripts/handoff.py`, `seal-inputs.py`, `workshop.py`, root tests | Safe copy/no-clobber, real output identity binding, gate separation, single deadline, failed outcomes, report capture integrity | Lab native preparation/workflow/report functions; Harness `test_preparation_profile`, `test_docker_session`, `test_campaign_session`, `test_session` | Public documentation is corrected now. Separate reusable supervisor guarantees into internal coverage only when necessary; do not move this experiment adapter wholesale into Harness |

The candidate modules above are in Lab main
`7e306a96bcc617468d2a06493dab4562bff6beb0` and Harness main
`b1c2efbd256eceeebdef7cf42b34165d01b8ccb6`. This turn reads their coverage and checks
metadata authoring; it does not run their model/runtime suites or prove every
helper assertion redundant. Each removal needs an explicit old-guarantee → retained
neutral-test map and a preservation decision. No per-experiment Python should be
added to Workshop or merely moved into Lab/Harness under another name.

Harness supports generated file identities in later committed jobs only when
predeclared argv/environment stay unchanged. A helper requiring a changed slot
must stop at that boundary; a fresh owner/deadline is not an accounting workaround.
Approval references, historical pins and successful schema validation grant no new
workload authority.

The historical synthetic/CPU results stay intact. Imported Lab records now live
in the immutable history linked by the retirement map.
Existing scripts are migration inventory, not a promise of current compatibility.
New reproduction uses current native interfaces and new identities. This retirement does not authorize deleting the retained helpers, choosing budgets,
activating a runtime or executing a new experiment.

## Retirement ownership and order

Lab #157 owns the retirement, preservation decisions and documentation. Lab #158
owns demonstrated gaps in generic native authoring and verification, with neutral
regression coverage. Harness #21 owns reusable internal policy, deadline and
process-cleanup guarantees. These assignments do not establish a second supported
Workshop execution workflow or promise a compatibility adapter.

Before removing a helper, map each existing guarantee to retained coverage, close
any demonstrated generic gap in its owning repository, and preserve the original
evidence. Retire the helper and its active callers and documentation together
through review, with the parent coordinating review and merge order. This work
does not promise a new workload; actual execution still requires separate approval.
