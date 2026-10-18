# Memory-injection identity acceptance

Workshop owns this fixed declarative [expectation record](expected.json) and the
[immutable input map](inputs.json). Lab owns native planning, historical identity
selection, verification and neutral tests. There is no Workshop Python checker.

The original archive remains unchanged at
`b74dff53259343aafd336cd00e3480246d70133b`. Seven planning inputs plus the original
receipt and collected report retain all original bytes and relative references.
The expected matrix/study hashes and nine ordered config hashes are copied from
the original receipt, never regenerated from a candidate. The receipt-selection
expectation remains `legacy_default_fields`.

## Explicit candidate acceptance

Use the reviewed candidate Lab source/interpreter. Set `ARCHIVE` to this
checkout's absolute `provenance/lab` path, `EXPECTED` to this directory's absolute
`expected.json`, and `NEW_OUTPUT` to an unused external report root. Run from any
working directory:

```sh
sparselab study report "$ARCHIVE/configs/memory_injection_v1.study.yaml" \
  "$ARCHIVE/artifacts/studies/memory_injection_v1/receipt.json" \
  --evidence "$ARCHIVE/artifacts/studies/memory_injection_v1/study-report.json" \
  --output "$NEW_OUTPUT" --identity-expectations "$EXPECTED" \
  --candidate-commit FULL_CANDIDATE_LAB_COMMIT
```

The native command verifies the supplied report/receipt, checks every fixed
expectation and refuses drift before writing the output bundle. Its emitted
`identity_acceptance` records the actual candidate checkout commit and package
source hash. Retain that report for each candidate accepted. The commit alone is
not proof of installed-runtime equivalence; compare the actual source hash too.
No training, inference, model loading or payload reconstruction occurs.

[Candidate 3fa477a evidence](candidate-3fa477a.json) records the explicit pass at
`3fa477a71c97820f15bc3e9edb7550cc099cceba` and a reversed-config-order refusal.
The [retained bundle inventory](candidate-3fa477a-bundle.json) ties that original
evidence to the builder's existing output, with native bundle/report identities,
exact file SHA256 values (including the manifest), and host-local inspection paths.
The unchanged candidate's native loader accepted the retained bundle. The bundle
and logs remain in local `/tmp`, are not uploaded, and may be lost on host cleanup;
the inventory does not make those bytes remotely available. No acceptance was
regenerated for this inventory.

This depends on the candidate Lab report expectation extension; it is not yet a
claim about merged Lab main. Existing `study report` already verifies the archived
report, but previously had no fixed mode/ordered-digest expectation option or
candidate-bound acceptance output.

## Candidate after provenance fix

[Candidate 1329c52 evidence](candidate-1329c52.json) records a separate explicit
acceptance at `1329c520de0609817af1feae51555b8ad9e77e30`, including its actual
retained bundle identities, file hashes, invocation and reversed-order refusal.
This candidate requires every file in the native package source inventory to be
clean and committed at the claimed revision. Its native bundle loader passed.
The original 3fa477a evidence and bundle inventory remain unchanged as historical
records; that candidate's incomplete provenance check cannot establish acceptance
of this fixed candidate. The new bundle has the same host-local `/tmp` availability
limitations. Neither acceptance is scientific qualification or review clearance.

## Coverage boundary

This pass is one candidate's evidence, not perpetual regression coverage.
Ordinary Lab CI remains self-contained and offline with neutral fixtures; it does
not fetch Workshop or silently skip this personal guarantee. Future candidates
require an explicit new acceptance run against the unchanged expectations and
review of its result. No scheduler or recurring infrastructure is introduced.

All twelve pending Lab assets and the original historical assertion remain in
place. Retirement must wait for replacement acceptance and external review of the
guarantee mapping. Historical data/tokenizer paths and scientific results are
not made executable or qualified by this metadata check. Missing prepared payloads
remain unavailable. No historical hashes, results, budgets or approvals are edited.
