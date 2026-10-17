# Experiment portfolio

[The catalog](experiments.json) provides stable experiment IDs and local repository pointers for the active research portfolio. It is a discovery index, not an execution DSL. Read original scientific cards and receipts through each entry; no external account is required to browse these tracked records.

The owner asked on 2026-10-17 to keep prior experiments active for resumption or rebuilding. Active intent is separate from historical execution and current readiness. `preserved_unassessed` means original evidence has been copied, not that every execution claim has been verified. `metadata_validated` records only the linked metadata checks. An `actually_executed` claim must cite the exact run, pins, scope and receipt; it does not establish present-day reproducibility or model quality.

Stable IDs retain original scientific slugs. Historical and current kernel-memory-lab material share one ID with separate origin paths. Historical DevMind v0–v5 remain distinct from the fresh DevMind 340M Base proposal. That proposal is only a potential future retest base, not a selected model or authority to train.

## Resume or rebuild

Each entry lists blockers and links to original declarations. Resume requires verified retained artifact closure, compatible runtime, permissions and resource approval. Rebuild requires supported native declarations, resolved scientific choices and bindings, metadata checks, then execution approval. Missing checkpoints or datasets are not silently replaced by fresh training or downloads. Existing TinyStories and DevMind guides remain at their published paths.

## Preservation and later adaptation

[The manifest](../provenance/lab-manifest.json) records source commit/path, destination, Git blob, byte length and SHA-256 for all 1,077 stage-one files. Shared corpora, reports and packaged resource declarations keep original relative paths in `provenance/lab/`; report digest directories remain intact. This stage does not delete Lab sources.

Original bytes are immutable evidence. Relative links inside historical files may refer to their original Lab workspace and are not rewritten. The catalog and manifest are the relocation map. Packaged cards/resources are provenance only: do not assume their old package-relative bindings work here. Future native adaptations belong in separate reviewed files, using existing Lab schemas and explicit local resource roots.

The corpus fixture `checks.py` is archived as `checks.py.txt`, with exactly the same bytes. Historical HTML/SVG reports are retained source artifacts; this PR does not render or execute embedded content. No new executable Python or notebooks are added. Existing Workshop helpers and tests are unchanged; their native replacements and eventual retirement need a separate capability audit.

Stage one does not claim the entire Lab migration is complete. Mixed acceptance/configs/docs/samples/examples are awaiting selective mapping. Execution, useful-story validation, and native recipe adaptation are separate deliverables.

The key `devmind-340m-base` is a catalog discovery key only, not an immutable model or artifact identity. [Stage two](STAGE2.md) preserves additional configs, acceptance evidence, examples, samples and research documentation.

Historical absolute host paths in archived evidence are provenance only. They require new explicit local bindings and verified artifact identities before use; they are not current execution locations or access authority.
