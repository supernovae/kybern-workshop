# Preparation evidence

Validated on 2026-10-15 using existing Python 3.14.4 on Ubuntu 26.04 WSL2.
The imported Lab package was
`/home/byron/src/lab-pinned-d96b0aaf/src/sparselab/__init__.py`, at pinned source
`d96b0aafda56c3a263a3be83d88e07839e17c3e6`; its checkout was clean.

Command (no installs):

```text
/home/byron/src/lab-runtime-d96b0aaf/bin/python -B -m unittest discover -s /home/byron/src/workshop-tinystories-worker/examples/tinystories-worker -p test_handoff.py -v
```

All ten tests passed in 2.759 seconds:

- commands accepted by the native public CLI parser (handlers never invoked)
- literal argv and exit 0/7 preserved by bounded fake Python children
- dataset revision, first-file count, content-digest and 300 MiB guard refusals
- native unsupported hard-memory/disk/expanded-byte requests refuse
- incomplete preparation, unsafe paths and duplicate JSON fields refuse
- source-lock fixture, native preparation inspection and admission model validation
- partial report bindings refuse
- mismatched review commit and dirty checkout refuse
- native configuration models and 16-update/24-evaluation-batch derivation
- sealed serial pair passes native metadata inspection; repeated output refuses

Source discovery was mocked; no network payload, tokenizer fit, runtime probe,
model training or model evaluation ran. A read-only web attempt to inspect the
real Hub file inventory was unavailable, so real lock availability/content/size
remains unverified. Fake artifacts support metadata inspection only and were
confined to temporary test directories. The worker must cold-verify actual native
artifacts before admission.

The existing supervisor's fixed 26-slot requirement was verified in
`lab-harness/session.py` at `ac45e7aea69169cc6854bc14745ac57ffeca1391`,
particularly the minimum slot count and exact ordered A/B step validation.
The adapter's fixed argv/offline requirements were inspected in
`workshop_argv.py`. This PR makes no supervisor change or execution-clearance claim.
