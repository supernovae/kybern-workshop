# DevMind v2: fresh-start planning checklist

This is a planning-only follow-up to [campaign PR #73](https://github.com/supernovae/kybern-workshop/pull/73).
It contains no runnable recipe, trained model, admitted dataset or launch approval.
No training, downloads, backup, deletion or drive reset is performed by this PR.

## Scope of this public starting point

This deliberately reduced public document omits recovered configurations, proposed
run parameters and budgets, source revisions, engine/tokenizer hashes, local paths,
archive locations and identifying provenance. Those artifacts are not preserved by
this PR. It is not a substitute for the complete v2 configuration or a backup.

## Fresh initialization contract

- Create a new run identity and new output directories.
- Initialize model weights, optimizer state, random state and counters from the
  chosen fresh-run recipe. Do not bind a v1 checkpoint or continuation cursor.
- Validate the configuration against an explicitly selected compatible engine.
- Bind and verify the tokenizer before constructing vocabulary-dependent mappings.
  If the tokenizer changes, regenerate mappings and validate special-token IDs.
- Derive the schedule from actual frozen packed groups, not historical step counts.
- Keep all launch inputs unbound until the checks below have independent evidence.

## Data admission checklist

For every proposed pillar, retain a reviewable inventory containing:

- Exact immutable source revisions, shard hashes and source-quality decisions.
- Retained document identities and duplicate clusters across the full mixture.
- Train, validation and test separation, including benchmark contamination checks.
- Tokenizer identity and measured unique usable targets, with an explicit EOS rule.
- Packed artifact hashes, group boundaries and the resulting full-run schedule.

Historical screened totals are not admitted capacity. Keep missing capacity visible;
do not quietly rebalance an exhausted pillar. Prior training consumption alone is
not a permanent exclusion for fresh initialization, but heldout and benchmark
protections remain necessary. Freeze the complete feasible mixture before launch.

## Acceptance gates

Before any separately authorized training, define a fixed behavioral evaluation
rubric and numerical pass/stop criteria. Verify the native artifact/schema binding,
fresh initialization, restart equivalence, finite loss and gradients, physical
accelerator ownership, sustainable throughput and storage headroom. A passing
planning checklist does not certify runtime readiness or model quality.

## Reset and recovery gate

A repository PR does not make drives safe to wipe. Before any destructive action:

1. Identify the exact physical devices to be reset and all dependent storage pools.
2. Inventory the desired final checkpoint and complete training state, tokenizer,
   resolved configuration, source code including local changes, dependency/environment
   manifests, selection/split manifests and all data required for recovery.
3. Copy that recovery set to storage independent of every device being reset.
4. Verify destination checksums and perform a recovery test from that copy.
5. Record missing dependencies and obtain explicit authorization for the concrete
   destructive action only after those gaps are resolved.

A different mountpoint or filesystem does not establish physical independence.
This checklist supplies no deletion commands and makes no claim that any existing
backup or recovery set is complete.
