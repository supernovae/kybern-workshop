# DevMind v2: native fresh-start scaffold

This package authors a complete fresh Engram recipe for Kybern Model Lab. It is
not a trained model or launch approval. Code qualification comes first; usable
data counts and source inventory come afterward. Nothing here downloads data,
starts training, copies private archives, or deletes anything.

## Contents

- `experiment.json`, `model.json`, `optimizer.json`: full 24-layer, 1,024-wide,
  4K-context backbone; tokenizer-bound Engram at blocks 1/14 from initialization;
  prime-XOR tables, context-key gates, causal convolution and independent memory
  initialization. This is not a reduced smoke model.
- `binding.example.json`: explicit unbound artifact locations, runtime selection
  and five individually authenticated fixed validation panels. The existing
  Workshop binder refuses nulls and validates with native `RunConfig`.
- `mixture.template.json`, `token-floors.template.json`: proposed whole-run unique
  quotas for web, notebooks, math, instruction and reference, without invented
  source revisions, inventory receipts or admitted capacity.
- `probe-standard.json`, `probe-full.json`, `probe-final.json`: native evaluation
  declarations, keeping ordinary iteration separate from held-back final probes.
- `runtime-xpu.delta.json`: optional native `config derive --set` settings
  for an explicitly selected XPU runtime. The optional two-device example uses native secondary-device support.
- [Native commands](native-commands.md): binding, mapping, packing, measured
  schedule derivation, re-verification, staging, training, recovery and reporting.
- [Protocol](protocol.md): scientific settings, evaluation, acceptance and recovery.
- `tests/test_devmind_v2.py`: offline contracts plus opt-in connected native schema,
  mapping, derivation and command-parser tests. These never train or download.

## Compatibility and tests

Use the engine revision recorded in `compatibility.json`, not an older checkout
that silently lacks Engram, dynamic document batching, retention or scheduling.
Workshop remains declarative; engine implementations and behavioral tests belong
in Kybern Model Lab. There is no second training loop or packing implementation.

The recorded SHA identifies the tested PR source, not a required merge strategy.
A squash merge produces a different main SHA. Either check out the recorded source
revision or verify the resulting merged diff and rerun the connected tests against
that main checkout; record its actual SHA in run provenance. The connected tests
exercise native contracts and do not impose an ancestor-only or exact-SHA gate.

From Workshop, in an already provisioned compatible environment:

```sh
python -B -m unittest discover -s tests -p 'test_devmind_v2.py' -v
WORKSHOP_LAB_CHECKOUT=/absolute/compatible/lab \
  python -B -m unittest discover -s tests -p 'test_devmind_v2.py' -v
```

The first command deliberately skips connected tests. A skipped test is not a
compatibility pass. The second imports the selected Lab source into the existing
interpreter; it installs nothing. Run the complete offline Workshop test suite
and the Lab feature tests before calling the pair merge-ready.

## Honest boundaries

The 10,256,578,560-target budget and 50/15/20/10/5 mixture are proposals, not
measured supply or a quality guarantee. The 78,252-update authoring horizon is a
packing bootstrap only. It must be replaced by native measured scheduling before
training. Five panel hashes and paths are unbound until independently produced.
Neither filling JSON fields nor passing a schema check authenticates artifacts.

Historical configurations, machine paths, raw data, tokenizer hashes and archive
provenance are deliberately not copied into this portable recipe. The native
memory-map command regenerates an identity mapping from the actual chosen
32,768-token tokenizer. Do not substitute a tokenizer without regenerating the
mapping and checking all special IDs, especially the configured padding ID 3.

Existing v1 source, data and checkpoints remain untouched. Full-state resume is
for recovery of a new v2 run only, never initialization from v1. Before resetting
any drives, independently copy and checksum the complete recovery closure and
test restoration. This scaffold does not establish that any drive is safe to wipe.
