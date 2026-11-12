# TinyStories CPU smoke run: first completed pair

[Workshop README](../../README.md) · [TinyStories worker recipe](../../examples/tinystories-worker/README.md)

On 2026-10-15 we ran a two-arm TinyStories smoke test on CPU (`FFN 64` vs. `FFN 96`) in [Kybern Model Lab](https://github.com/supernovae/model-lab). It tried out dataset preparation, cache reuse, paired training and held-out evaluation.

## Run summary

- Status: all 12 workflow stages exited with code `0`, with zero OOM events, and container cleanup checked out.
- Training: 16 updates across both arms (2 smoke + 5 warmup + 1 main update per arm), 512 training target positions in total.
- Evaluation: 6 batches of 32 targets (main steps 0 and 1 for both arms, plus 1 Campaign evaluation pass per arm).

## Pinned revisions and inputs

| Component | Value |
| --- | --- |
| **Kybern Model Lab commit** | `66ff9d71423e961ee15aed2267902164f04514c6` |
| **CPU container image** | `ghcr.io/supernovae/tiny-sparse-lab@sha256:553eefba27b7069ba17fb92c5734b2b53548ad3b40f868b1ad39dc3e3ad82ea4` |
| **Runtime** | Python 3.14.4, PyTorch 2.14.1+cpu |
| **Dataset** | `roneneldan/TinyStories` (`f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`) |
| **Subset & tokenizer** | 64 train / 16 validation stories, 512-token BPE vocabulary, 23,673 packed tokens |
| **Snapshot manifest SHA-256** | `efd5e6924cb04e0bad0d2bad50b1863f1630b5bb6d3c58eb93879d8c20003239` |
| **Prepared cache SHA-256** | `dfc008bd34c09fabf8ebc204f300277080735a49d5bedff7d0f8a99eb394d458` (`b7af269e44c026cd`) |

## Cache reuse

To reuse a prepared dataset cache in another run, copy it into a writable directory. A read-only mount won't work, because Kybern Model Lab writes `.cleanup.lock` and `<id>.preparation.json` into the cache's parent directory while verifying it.
