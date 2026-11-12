# DevMind v2: native fresh-start scaffold

This package authors a complete fresh Engram recipe for Kybern Model Lab. It is
not a trained model or launch approval. Code qualification comes first; usable
data counts and source inventory come afterward. Nothing here downloads data,
starts training, copies private archives, or deletes anything.

## Contents

- `experiment.json`, `run.json`, `model.json`, `optimizer.json`: full 24-layer, 1,024-wide,
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

## Compatibility

Use the engine revision recorded in `compatibility.json`, not an older checkout
that silently lacks Engram, dynamic document batching, retention or scheduling.
Workshop remains declarative; engine implementations and behavioral tests belong
in Kybern Model Lab. There is no second training loop or packing implementation.

The recorded SHA identifies the tested source, not a required merge strategy.
Record the SHA of the Lab you actually run in run provenance. To check these
declarations against it, in an already provisioned environment:

```sh
klab config validate experiments/devmind-v2
```

That validates the model and optimizer sections against the installed schema
and installs nothing. The composed config in
[native commands](native-commands.md) is validated when it is written.

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
