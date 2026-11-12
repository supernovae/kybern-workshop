# TinyStories: Paired CPU Campaign & Worker Recipe

[Back to Workshop README](../../README.md)

For the interactive TinyStories walkthrough and local `klab try` comparison, start with the [TinyStories microlab guide](../tinystories-microlab/README.md) or [kybern.dev/models/tinystories-training](https://kybern.dev/models/tinystories-training/).

This directory contains a smaller, self-contained two-arm CPU Campaign recipe (64 train / 16 validation stories, FFN width 64 vs. 96): its preparation campaign, run config, plan, campaign and evaluation suite.

- **Recorded smoke result:** [`results/2026-10-15-tinystories-smoke/README.md`](../../results/2026-10-15-tinystories-smoke/README.md)

## Workload Summary

| Setting | Value |
| --- | --- |
| **Dataset** | `roneneldan/TinyStories` (`f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`) |
| **Selected stories** | 64 train, 16 validation (deduplicated; up to 300 MiB shard cache) |
| **Tokenizer** | 512-token BPE trained on up to 64 stories |
| **Model arms** | Seed 7, CPU FP32, 1 layer, hidden dim 32, 2 heads, **FFN 64 vs. 96** |
| **Training budget** | Sequence 32, batch 1, accumulation 1; 2 smoke + 5 warmup + 1 main update per arm (16 updates / 512 targets total) |
| **Evaluation** | 1 batch per evaluation pass (up to 24 batches / 768 targets across both arms) |
| **Resource bounds** | 3,600-second wall limit, 4 GiB observed process-tree RSS, 2 GiB retained output |

## Running It

The declarations run through Lab's own recipe commands; nothing here launches
work. Lock the source with `klab data lock source.json`, then follow
[packaging and inspecting a recipe](../../docs/native-workflow.md#packaging-and-inspecting-a-recipe):
`klab experiment recipe create` inventories the declarations,
`klab experiment recipe preparation inspect` and `apply` prepare the inputs, and
`klab experiment recipe workflow inspect`, `resolve`, `apply`, `approve` and
`report` run the paired campaign. Local paths go in a bindings file outside Git.

The recorded smoke result used a helper script that has since been removed;
its commands are preserved in Git history.
