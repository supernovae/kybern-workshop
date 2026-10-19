# TinyStories: Paired CPU Campaign & Worker Recipe

[Back to Workshop README](../../README.md)

For the interactive TinyStories walkthrough and local `sparselab try` comparison, start with the [TinyStories microlab guide](../tinystories-microlab/README.md) or [kybern.dev/models/tinystories-training](https://kybern.dev/models/tinystories-training/).

This directory contains a smaller, self-contained two-arm CPU Campaign recipe (64 train / 16 validation stories, FFN width 64 vs. 96) and a standard-library helper (`handoff.py`) for binding preparation and workflow stages on a CPU worker.

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

## Handoff Helper Commands (`handoff.py`)

`handoff.py` generates native `sparselab` CLI argument lists and binds artifact hashes between preparation and workflow stages without launching workloads itself.

1. **Render the command sequence:**
   ```sh
   python3 -B examples/tinystories-worker/handoff.py commands \
     --python /path/to/venv/bin/python \
     --recipe /path/to/examples/tinystories-worker \
     --work /path/to/work
   ```
2. **Lock source metadata and bind preparation:**
   After running `sparselab data lock` to produce `source.lock.json`, verify the lock against `first-files.json` and generate the preparation recipe:
   ```sh
   python3 -B examples/tinystories-worker/handoff.py bind-preparation \
     --recipe /path/to/examples/tinystories-worker \
     --source-lock /path/to/work/source.lock.json \
     --destination /path/to/work/preparation-recipe \
     --work /path/to/work \
     --bindings /path/to/work/preparation-bindings.json
   ```
3. **Generate preparation admission:**
   ```sh
   python3 -B examples/tinystories-worker/handoff.py admission \
     --phase preparation \
     --recipe /path/to/work/preparation-recipe \
     --reviewed-commit COMMIT_SHA \
     --bindings /path/to/work/preparation-bindings.json \
     --output /path/to/work/preparation-admission.json
   ```
4. **Seal the paired workflow after preparation completes:**
   ```sh
   python3 -B examples/tinystories-worker/handoff.py seal-workflow \
     --recipe /path/to/work/preparation-recipe \
     --receipt /path/to/work/preparation-result.json \
     --destination /path/to/work/workflow-recipe \
     --work /path/to/work \
     --bindings /path/to/work/workflow-bindings.json
   ```

## Running the Unit Tests

```sh
python3 -B -m unittest discover -s examples/tinystories-worker -p test_handoff.py -v
```
