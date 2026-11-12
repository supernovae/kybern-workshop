# TinyStories: ROCm Container Campaign Recipe

[Back to Workshop README](../../README.md)

This recipe runs the two-arm TinyStories smoke comparison (FFN width 64 vs. 96 on 64 training and 16 validation stories) in a container on AMD ROCm, under Linux or WSL2, using `klab campaign` commands.

## Workload & Resource Configuration

| Setting | Value |
| --- | --- |
| **Kybern Model Lab commit** | `2d5ba0fd66b6087101ad152fdbfe17b44ce194a5` (pinned in [`pins.json`](pins.json)) |
| **Dataset** | `roneneldan/TinyStories` (`f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`), 64 train / 16 validation stories |
| **Model arms** | Seed 7, vocab 512, hidden dim 32, 1 layer, 2 heads, FP32 on ROCm device 0; **FFN 64 vs. 96** |
| **Training budget** | 2 smoke + 5 warmup + 1 main update per arm (16 updates / 512 targets total) |
| **Evaluation** | 1 batch per pass (up to 24 evaluation batches / 768 targets total) |
| **Container limits** | 1,800-second wall limit, 12 GiB RAM (zero swap), 2 CPUs, 256 PIDs |

> **Pinned before the Lab rename:** this procedure uses a Kybern Model Lab commit from before the CLI was renamed `klab`. To replay it at that commit, use `sparselab` (and `SPARSELAB_*` variables) in place of `klab`; see [Records Pinned Before the Rename](../../docs/native-workflow.md#records-pinned-before-the-rename).

## Staging Prepared Inputs

The recipe reads an already prepared TinyStories snapshot, tokenizer, and packed cache from a read-only input directory:

```text
inputs/
  source.lock.json
  parquet/train-00000-of-00004-2d5a1467fff1081b.parquet
  parquet/validation-00000-of-00001-869c898b519ad725.parquet
  snapshot/{manifest.json,train.jsonl,validation.jsonl}
  tokenizer/{tokenizer.json,tokenizer_manifest.json}
  packed/b0892750f1d1206ca5ddfc4a47ed3257bed54651146d3b8558e0321d280498fb/...
```

Check these inputs with Lab before any GPU work. `klab tokenizer verify`
checks the tokenizer against its config, and
`klab data prepared-inputs verify` rechecks the packed inputs from scratch on
the machine that will run them.

## Running It

Run the campaign with `klab experiment recipe workflow inspect`, `resolve`,
`apply`, `approve` and `report`; see
[packaging and inspecting a recipe](../../docs/native-workflow.md#packaging-and-inspecting-a-recipe).
The recorded run used helper scripts for the container session, which have
since been removed; you can find them in Git history. The result is in
[`results/2026-10-31-tinystories-rocm`](../../results/2026-10-31-tinystories-rocm/README.md).
