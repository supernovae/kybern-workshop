# TinyStories: ROCm Container Campaign Recipe

[Back to Workshop README](../../README.md)

This recipe adapts the two-arm TinyStories smoke comparison (FFN width 64 vs. 96 on 64 train / 16 validation stories) for containerized AMD ROCm execution on Linux/WSL2 using `sparselab campaign` commands.

## Workload & Resource Configuration

| Setting | Value |
| --- | --- |
| **Tiny Sparse Lab commit** | `2d5ba0fd66b6087101ad152fdbfe17b44ce194a5` (pinned in [`pins.json`](pins.json)) |
| **Dataset** | `roneneldan/TinyStories` (`f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`), 64 train / 16 validation stories |
| **Model arms** | Seed 7, vocab 512, hidden dim 32, 1 layer, 2 heads, FP32 on ROCm device 0; **FFN 64 vs. 96** |
| **Training budget** | 2 smoke + 5 warmup + 1 main update per arm (16 updates / 512 targets total) |
| **Evaluation** | 1 batch per pass (up to 24 evaluation batches / 768 targets total) |
| **Container limits** | 1,800-second wall limit, 12 GiB RAM (zero swap), 2 CPUs, 256 PIDs |

## Staging Prepared Inputs

This recipe reuses pre-staged TinyStories snapshot, tokenizer, and packed cache inputs from an immutable input directory:

```text
inputs/
  source.lock.json
  parquet/train-00000-of-00004-2d5a1467fff1081b.parquet
  parquet/validation-00000-of-00001-869c898b519ad725.parquet
  snapshot/{manifest.json,train.jsonl,validation.jsonl}
  tokenizer/{tokenizer.json,tokenizer_manifest.json}
  packed/b0892750f1d1206ca5ddfc4a47ed3257bed54651146d3b8558e0321d280498fb/...
```

Run the read-only preflight check or generate a transfer manifest with `handoff.py`:

```sh
python3 examples/tinystories-rocm/handoff.py preflight --inputs /path/to/retained-inputs
python3 examples/tinystories-rocm/handoff.py transfer-manifest \
  --inputs /path/to/retained-inputs \
  --output /path/to/evidence/transfer-manifest.json
```

During container execution, `handoff.py stage` verifies the read-only input manifests and copies the packed cache into a writable `/state/cache/<identifier>` directory before running cold artifact verification.

## Binding a Container Session

Use `bind_session.py` to generate the seven-slot session specification (`copy-inputs`, `validate`, `apply`, `approve`, `run`, `status`, and `report`):

```sh
python3 examples/tinystories-rocm/bind_session.py bind --help
```

After training completes, bind the report job from the campaign's lock, workspace, and evidence index paths:

```sh
python3 examples/tinystories-rocm/bind_session.py report \
  --state /path/to/state --lock /path/to/state/lock.json \
  --workspace /path/to/state/workspace --index /path/to/state/index.json
```

## Running Offline Tests

The stdlib test suite exercises input preflight, manifest generation, staging guards, and session binding without requiring a GPU or Docker daemon:

```sh
python3 -m unittest discover -s examples/tinystories-rocm -p 'test_*.py' -v
```
