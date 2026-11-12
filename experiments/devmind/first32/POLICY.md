# First-run private attribution policy

Apply Lab's record-attribution overlay for private training on the three
retained sources. Keep each record's original row, shard and revision, any
license labels and notice pointers, and note unknowns and conflicting evidence.
An unknown label is neither a restriction nor a legal clearance. Where a source
explicitly restricts our intended use, keep the pinned restricted-row evidence
and exclude those rows. This policy covers private training only; it doesn't
cover redistribution or publishing a model.

Run quality and family checks separately from attribution. Quarantine records
with missing source information, empty or non-text content, or credentials; keep
Lab's language and code-quality rules. Freeze the reviewed family and
exact-content groups before fitting the TRAIN-only tokenizer. Never move held-out
families into training to fill a quota.

This first-run profile tests implementation changes; you don't need to rerun it
before every later run. Once it passes, the approved larger run can go ahead if
its data, measured capacity and remaining resource budget fit. The historical
84-source/12B-token plan still can't run on this profile.
