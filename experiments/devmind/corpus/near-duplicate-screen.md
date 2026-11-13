# Cross-split near-duplicate screen: record

Complete this before pretraining on a release. Leave nothing blank; write
"none" or "not covered" where that is the answer. A release with no completed
record is not cleared for training.

Why it exists: a validation document with a near-copy in training makes
validation loss look better than the model deserves, and exact-match checks do
not see it. `klab corpus near-duplicates` is a lexical screen (three-word
shingles, Jaccard 0.65 or more). It can miss pairs and does not catch
paraphrases, so a clean result means "no lexical near-copies found", nothing
more. MinHash banding finds a pair at Jaccard 0.65 about 96% of the time, at
0.7 about 99%, and above 0.8 almost always.

The screen covers every document or stops with no report (Lab
[#433](https://github.com/supernovae/model-lab/pull/433)). Run it as shown in
the [recipe](../README.md#1-corpus) and fill this record from its JSON report.

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
| Command and every flag passed | |
| Documents screened (train / validation), from `coverage` | |
| Text bytes screened (train / validation), from `coverage` | |
| Documents without words (matched by identical text only) | |
| Outcome | `complete` · `stopped at a bound` · `not run` |
| Cross-split pairs reported (`candidate_count`) | |
| Identical-text pairs reported (`identical_text_count`) | |
| `candidates_truncated` | must be `false` |

Screened counts must equal the release counts above. If the command stopped
at a held-out bound, it wrote no report: say which bound and rerun with it
raised. If `candidates_truncated` is `true`, rerun with `--max-candidates`
raised until every pair is listed.

## Review of reported pairs

Every reported pair needs a decision before training. Merging a pair into one
family and re-freezing the splits is the default.

| Pair (document IDs) | Jaccard | Decision (`merged` · `dropped` · `kept, because ...`) |
| --- | --- | --- |
| | | |

## Acceptance

Every document in the release was screened, `candidates_truncated` is `false`,
and every reported pair is decided above.

Accepted by: ______ on ______.
