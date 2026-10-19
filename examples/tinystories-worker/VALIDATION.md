# TinyStories Worker Helper Validation

The unit test suite in `examples/tinystories-worker/test_handoff.py` validates `handoff.py` using temporary filesystem fixtures and mocked source metadata (no network downloads or model training required):

```sh
python3 -B -m unittest discover -s examples/tinystories-worker -p test_handoff.py -v
```

## Covered Checks (16 Tests)

- CLI argument rendering for `data lock`, `experiment recipe preparation`, and `experiment recipe workflow` commands.
- Verification of dataset revision, shard count, byte limits (300 MiB), and SHA-256 digests against `first-files.json`.
- Refusal of incomplete preparation receipts, unsafe or relative paths, duplicate JSON keys, and existing output paths (no-clobber).
- Validation of the two-arm training and evaluation budget (16 total updates, 512 training targets, and 24 evaluation batches across both arms).
