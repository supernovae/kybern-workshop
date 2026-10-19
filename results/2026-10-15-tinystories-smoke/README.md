# TinyStories CPU Smoke Run: First Completed Pair

[Back to Workshop README](../../README.md) · [TinyStories Worker Recipe](../../examples/tinystories-worker/README.md)

This record summarizes the 2026-10-15 two-arm TinyStories CPU smoke run (`FFN 64` vs. `FFN 96`), exercising dataset preparation, cache reuse, paired training, and held-out evaluation in [Tiny Sparse Lab](https://github.com/supernovae/tiny-sparse-lab).

## Run Summary

- **Completion status:** All 12 workflow stages completed with exit code `0`, zero OOM events, and verified container cleanup.
- **Training budget:** 16 total updates across both arms (2 smoke + 5 warmup + 1 main update per arm = 512 total training target positions).
- **Evaluation:** 6 evaluation batches executed (main step 0 and 1 for both arms plus 1 Campaign evaluation pass per arm, 32 targets per batch).

## Pinned Revisions & Inputs

| Component | Value |
| --- | --- |
| **Tiny Sparse Lab commit** | `66ff9d71423e961ee15aed2267902164f04514c6` |
| **CPU container image** | `ghcr.io/supernovae/tiny-sparse-lab@sha256:553eefba27b7069ba17fb92c5734b2b53548ad3b40f868b1ad39dc3e3ad82ea4` |
| **Runtime** | Python 3.14.4, PyTorch 2.14.1+cpu |
| **Dataset** | `roneneldan/TinyStories` (`f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`) |
| **Subset & tokenizer** | 64 train / 16 validation stories, 512-token BPE vocabulary, 23,673 packed tokens |
| **Snapshot manifest SHA-256** | `efd5e6924cb04e0bad0d2bad50b1863f1630b5bb6d3c58eb93879d8c20003239` |
| **Prepared cache SHA-256** | `dfc008bd34c09fabf8ebc204f300277080735a49d5bedff7d0f8a99eb394d458` (`b7af269e44c026cd`) |

## Cache Reuse Notes

When reusing a prepared dataset cache across runs, copy the prepared cache into a writable directory rather than mounting it read-only: Tiny Sparse Lab writes `.cleanup.lock` and `<id>.preparation.json` receipts in the cache parent directory during verification.
