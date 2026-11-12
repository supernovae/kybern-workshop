# Devmind corpus

Thirty-three pinned sources in ten strata, 12 billion tokens. Every Hugging Face
shard is named with its SHA-256 and size as the Hub reported them on
2026-11-12; every git source is pinned to that day's default-branch commit.
Nothing has been downloaded or counted. Token figures below are estimates from
dataset cards and file sizes.

## Mixture

| Stratum | Share | Tokens | Sources |
| --- | --- | --- | --- |
| `web` | 32.95% | 3.954B | FineWeb-Edu (deduplicated), 5 shards |
| `python` | 18% | 2.16B | Stack-Edu, permissive licenses only, Python shards |
| `web_code` | 12% | 1.44B | Stack-Edu JavaScript and TypeScript shards |
| `collaboration` | 12% | 1.44B | GitHub issues and pull-request threads |
| `math` | 8% | 0.96B | FineMath 4+ |
| `systems_code` | 6% | 0.72B | Stack-Edu Go, Rust, Shell and Markdown shards |
| `wiki` | 6% | 0.72B | FineWiki English |
| `notebooks` | 3% | 0.36B | Kaggle notebooks |
| `reference` | 2% | 0.24B | Python docs and PEPs, Node.js API, MDN, TypeScript handbook, React, Express, Kubernetes, GitHub docs, the Rust book, tldr pages |
| `practice` | 0.05% | 6M | OWASP cheat sheets and testing guide, Microsoft's engineering playbook, Google's code review guide |

About 48% code and collaboration, 39% prose, 8% math, 2% reference. The mixture
allows a document to be used twice (`max_exposures: 2`), which only the small
`reference` and `practice` strata are expected to need.

The `*_heldout` sources take one row in 200 from a shard no training source
uses, and go to the validation split.

## Why these sources

- **Code:** `common-pile/stackv2_edu_filtered` carries the file text of
  Stack-Edu for openly licensed repositories, with a license, repository and
  path on every row. Its shards are sorted by language, which is how the Python
  (73 to 84), JavaScript (50 to 64) and TypeScript (91 to 94) shards are chosen.
  Rows with a license outside MIT, Apache-2.0, BSD and ISC, or with several
  licenses, are set aside by Lab's code qualification. Many rows have an
  educational score of 2 (most of the first rows of one JavaScript shard);
  Lab cannot filter on that field yet.
- **Issues and pull requests:** `common-pile/github_archive_filtered` has a
  license and repository per thread.
- **Wikipedia:** `HuggingFaceFW/finewiki` is a 2025 extraction that keeps tables,
  math and code.
- **Web:** the deduplicated FineWeb-Edu in `HuggingFaceTB/smollm-corpus`.

## Left out on purpose

| Source | Reason |
| --- | --- |
| Cosmopedia v2, smol-summarize | Our own screening found truncation, factual errors and instruction violations |
| `codeparrot/github-code-clean`, `github-code`, The Stack v1 | Stale 2022 snapshots without quality filtering; superseded |
| The Stack v2, `HuggingFaceTB/stack-edu` | File contents need a Software Heritage bulk agreement and S3 access |
| OpenHermes, OpenOrca, Alpaca family, Magicoder, CodeFeedback | Generated with models whose terms restrict this use, or unknown origin |
| Google SRE books, DORA report PDFs, the STPA handbook, ISO and IEEE standards | Non-commercial, no-derivatives or not open |
| HumanEval, MBPP, MultiPL-E, DS-1000, CRUXEval, BigCodeBench, SWE-bench | Held out for evaluation |

Before acquiring `collaboration`, exclude the SWE-bench repositories at
admission (astropy, django, matplotlib, seaborn, flask, requests, xarray,
pylint, pytest, scikit-learn, sphinx, sympy), so the model can be said not to
have seen their issues.

## Not here yet

- **RFCs, NIST and NASA handbooks, accident investigation reports, the Cynefin
  wiki.** They are openly licensed and wanted, and Lab has no source kind for
  archives, PDFs or other wikis
  ([Lab #419](https://github.com/supernovae/model-lab/issues/419)). Safety and
  resilience engineering, Cynefin and SDLC material reaches the model today
  only through Wikipedia and the small `practice` stratum.
- **Commits and diffs, instruction pairs.** Their rows spread text over several
  fields ([Lab #416](https://github.com/supernovae/model-lab/issues/416)).
- **Whole repositories as single documents.** Each file is its own document.

## Unchecked

- `notebooks_kaggle` names `file_id` as its family field from the dataset card.
  Run `klab corpus preview` on that source before acquiring it.
- The include patterns of the git sources were written from each repository's
  layout as remembered, not listed. `corpus acquire --source-id ID` fails
  cleanly if a pattern matches nothing or the selection exceeds `max_bytes`.
- Share-alike sources (Wikipedia, MDN, OWASP) are in their own strata or
  sources so they can be dropped. Whether trained weights are a derivative of
  share-alike text is unsettled; every source is marked
  `weight_license_status: separate_analysis_required`.
