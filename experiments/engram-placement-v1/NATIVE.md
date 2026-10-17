# Native placement-study authoring

This port preserves the original educational comparison: no lexical memory, final injection, and embedding injection, matched across seeds 17, 41 and 73. It does not establish useful language-model quality, unseen-fact transfer, semantic retrieval, architecture speed or cross-tokenizer equivalence. The original card explicitly permits smoke as a minimum useful scale; finite repeated synthetic data and construction-RNG differences remain confounders.

## Author metadata only

The six-file resource closure lives in `native/`. It uses Lab's existing ResearchEntry, ResearchRecipe, RunConfig, profile, dataset and lifecycle schemas. The recipe makes the old scaffold's three implicit seeds explicit; the dataset catalog exposes only the unchanged offline profile. The preserved card still describes TinyStories applicability, but this port intentionally offers only offline data. All four scale declarations remain because the existing schema requires them. Only smoke is intended for validation here; nano, micro and tiny are not validated or approved.

Use the exact Lab interface revision recorded in VALIDATION.md. With that installed existing environment, choose a fresh absolute output path and an external working directory, then run:

```sh
cd /absolute/external/work
sparselab --work-dir /absolute/external/work/state research scaffold engram-placement-v1 --resource-root /absolute/workshop/experiments/engram-placement-v1/native --scale smoke --data offline --backend cpu --output /absolute/external/work/placement-study
```

This command writes study/configuration metadata. It does not fit a tokenizer, prepare data, probe hardware, train, generate, register workers or execute the study. Do not treat commands in its generated README as approval to run. The destination must be new. The explicit `--work-dir` binds run storage under `/absolute/external/work/state/experiments/engram-placement-v1/runs`. Tokenizer and data paths resolve under the generated study directory. Without this flag, Lab uses its configured environment/XDG/user-data default; changing directory alone does not bind run storage. Inspect all emitted paths before any authorized runtime work.

## Frozen smoke settings

Nine configurations cross three architectures with three seeds. The three comparisons are final-minus-none, embedding-minus-none and embedding-minus-final, each seed-matched. All use a two-layer, width-64, four-head dense backbone, FFN 256, tied 512-token vocabulary, maximum context 256 and training sequence length 64. The two memory arms use 257 trigram table entries, dimension 8 and one hash head; only injection location differs between those arms.

Each configuration declares 32 main updates or 4,096 target tokens, microbatch 2 and accumulation 1. Thus the nine main-run caps sum to 288 updates and 36,864 targets. These are configuration limits, not a measured whole-job resource envelope: separate staging declares two smoke and five warmup steps, and tokenization, preparation, validation and capability evaluation add work. No CPU time/RAM or runtime approval is supplied.

CPU FP32, deterministic mode and AdamW are preserved: peak 0.003, floor 0.0003, four warmup steps, weight decay 0.1, betas 0.9/0.95, epsilon 1e-8, clipping 1. Validation and checkpoint cadence are eight updates, with six evaluation batches in the base configuration. Native scale overlays are part of this result and must be checked, not inferred from base.yaml alone.

The offline chat_recall curriculum has dataset seed 42, finite cyclic training transcripts, 768/12 train/validation document caps and 131,072/4,096 token caps. Tokenizer fitting is training-only, capped at 384 documents and 65,536 tokens, vocabulary 512 and minimum frequency 1. Tokenizer/data payloads have not been generated. The three builtin chat capability card IDs remain references to the pinned Lab implementation: retention, held-out wording and context override. These are not general chat-quality gates.

## Evidence and bindings

The current native lifecycle registry is intentionally empty. It claims no historical evidence, baselines, entries, findings or promotions. No lifecycle promotion, prior finding authorization or resumable artifact closure is claimed. Actual evidence views require separately verified files and explicit `--evidence-root` bindings.

Historical absolute host paths in preserved documents, manifests or registries are provenance, not portable destinations or current access grants. New execution requires explicit local bindings and verified tokenizer, data, run and checkpoint identities. Never edit archived bytes to make a path appear current. [The adaptation map](native-provenance.json) records original and adapted hashes; [the archive](../../provenance/lab/src/sparselab/research/resources/) remains unchanged.

Before runtime work, review generated configs, native study plan, all stage budgets, full artifact closure and an approved resource envelope. Metadata validation does not fulfill those requirements. Future DevMind 340M Base retesting remains a separate proposed scientific choice.
