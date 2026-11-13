# Cross-split near-duplicate screen: record

Complete this before pretraining on a release. Leave nothing blank; write
"none" or "not covered" where that is the answer. A release with no completed
record is not cleared for training.

Why it exists: a validation document with a near-copy in training makes
validation loss look better than the model deserves, and exact-match checks do
not see it. `klab corpus near-duplicates` is a lexical screen (three-word
shingles, Jaccard 0.65 or more). It can miss pairs and does not catch
paraphrases, so a clean result means "no lexical near-copies found in the
covered documents", nothing more.

## Release

| Field | Value |
| --- | --- |
| Release ID | |
| Lab commit | |
| Date | |
| Documents in release (train / validation) | |
| Text bytes in release (train / validation) | |

## Screen run

| Field | Value |
| --- | --- |
| Command and every bound passed | |
| Documents screened (train / validation) | |
| Share of release covered | |
| Strata or sources not covered | |
| Outcome | `complete` · `stopped at a bound` · `not run` |
| Cross-split pairs reported | |
| Identical-text pairs reported | |

If the command stopped at a bound, it wrote no report. Say which bound, then
either rerun with it raised or record the gap under Acceptance.

## Review of reported pairs

Every reported pair needs a decision before training. Merging a pair into one
family and re-freezing the splits is the default.

| Pair (document IDs) | Jaccard | Decision (`merged` · `dropped` · `kept, because ...`) |
| --- | --- | --- |
| | | |

## Acceptance

Choose one and delete the other.

- **Full coverage:** every document in the release was screened and every
  reported pair is decided above.
- **Partial coverage, accepted by the owner:** the uncovered documents are
  listed above, the reason they could not be screened is stated, and the
  owner accepts that training proceeds without screening them.
  Accepted by: ______ on ______.

## Gap to close in Lab

Full coverage needs a screen that does not hold the whole corpus in memory, for
example one that indexes the (small) validation side and streams the training
side past it, or one that shards by band. Until Lab has that, partial coverage
with an owner's acceptance is the only way to proceed on a full-size release.
Tracked in [model-lab#432](https://github.com/supernovae/model-lab/issues/432).
