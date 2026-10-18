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

## Merge order and merged-source acceptance

Merge [Lab #185](https://github.com/supernovae/tiny-sparse-lab/pull/185) first.
Then run the native metadata acceptance below against the exact merged Lab SHA,
using that clean source checkout and passing its full SHA as `--candidate-commit`.
Retain a separate result and bundle inventory for the merged SHA, and have that
acceptance reviewed before merging Workshop #36. The existing branch-candidate
records do not establish acceptance of a different merge commit, even if its
package bytes match. Preserve them as historical evidence; do not rewrite them
with the merged SHA. Parent coordination owns review and both merges.

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

## Candidate after main integration

[Candidate a3ccbe8 evidence](candidate-a3ccbe8.json) records a separate native
metadata acceptance at `a3ccbe8ad0377d02ce6b37a97ea4aaad32d5e710`, after an
ordinary merge of main `48ef4d47673d5f21c15dfcac8f272337e6514e79` and extraction
of shared neutral test vectors. Native bundle verification passed and reversed
config order refused before output. Production source bytes are unchanged from
1329c52; the candidate commit and retained bundle are nevertheless recorded
separately. Earlier records remain unchanged. This branch-candidate acceptance
does not replace the required acceptance at the future merged Lab SHA.

## Candidate with hermetic provenance tests

[Candidate eadb19e evidence](candidate-eadb19e.json) records separate acceptance
at `eadb19e22ff6cc9a8bf52737c65ca85a0820a847` after isolating the public-command
tests in temporary committed package copies and covering the inventory/provenance
hash-mismatch refusal. The emitted status is now `candidate_package_status`, with
no compatibility alias; older records retain their original field unchanged.
Candidate commits belong to the repository containing the loaded package and do
not by themselves establish upstream origin; compare the package source hash.
Native bundle verification passed, and reversed config order refused before
output. The merged-SHA acceptance gate and local-artifact limitations still apply.

## Candidate with specific refusal assertions

[Candidate b28f69c evidence](candidate-b28f69c.json) records separate acceptance
at `b28f69c41b84b9b6ea86f2df1776c0c853800839` after tightening drift tests to
require their intended identity or schema errors. Six committed mutation controls
were caught for those reasons. Production package bytes are unchanged from
eadb19e. Native bundle verification passed; reversed order refused with the
identity-mismatch message before output. Earlier records remain unchanged, and
acceptance at the future merged Lab SHA is still required.

## Digest and location semantics

For these version-1 native bundles, manifest `report_sha256` (recorded as
`native_report_sha256` or inside `native_identities`) identifies the verified
collected report. It is independent of the archive's filesystem root; it is not
the byte hash of the newly emitted `report.json`. The fixed study, matrix and
ordered config identities likewise describe the unchanged inputs rather than
their checkout location.

The emitted report retains reproduction commands containing input locations.
Changing the absolute archive root can therefore change serialized `report.json`
and rendered file hashes, the manifest bytes and the full `bundle_sha256`, while
the native collected-report identity remains unchanged. Compare each file digest
against its own retained bundle, and compare the native identities and fixed
expectations when assessing relocated inputs. Do not expect full bundle digests
to match across different archive roots or candidate commits.

Recorded host paths document where the historical invocation read inputs and
wrote evidence. They are not portable invocation defaults, remotely accessible
artifact links, or a durability guarantee. Use the variable-based command above
with locally resolved paths for a new acceptance. The recorded local inventories
permit byte verification only where those original files are still available;
missing local files remain unavailable evidence, not permission to substitute
new output under an old record.

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
