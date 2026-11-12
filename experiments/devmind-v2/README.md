# DevMind v2: native fresh-start scaffold

This package is a complete recipe for training DevMind with Engram memory from
scratch in Kybern Model Lab. Nothing has been trained from it yet, and it isn't
approved to launch. Code qualification comes first; usable data counts and the
source inventory come after. Nothing here downloads data, starts training,
copies private archives or deletes anything.

## Contents

- `experiment.json`, `run.json`, `model.json`, `optimizer.json`: the full
  24-layer, 1,024-wide, 4K-context backbone at full size. Engram memory is tied
  to the tokenizer and sits at blocks 1 and 14 from initialization, with
  prime-XOR tables, context-key gates, a causal convolution and its own memory
  initialization.
- `binding.example.json`: the artifact locations, runtime choice and five fixed
  validation panels you need to fill in, each checked on its own. The Workshop
  binder refuses nulls and validates the result as a `RunConfig`.
- `mixture.template.json`, `token-floors.template.json`: proposed unique-target
  quotas for the whole run across web, notebooks, math, instruction and
  reference. Source revisions, inventory receipts and available capacity are
  left blank until we have real values.
- `probe-standard.json`, `probe-full.json`, `probe-final.json`: evaluation
  configs. Everyday iteration uses the first two; the final probes are held back.
- `runtime-xpu.delta.json`: optional `config derive --set` settings for an XPU
  runtime you have chosen. The optional two-device example uses Lab's
  secondary-device support.
- [Native commands](native-commands.md): binding, mapping, packing, deriving the
  schedule from measured data, re-checking, staging, training, recovery and
  reporting.
- [Protocol](protocol.md): scientific settings, evaluation, acceptance and recovery.

## Compatibility

Use the engine revision recorded in `compatibility.json`. Older checkouts may be
missing Engram, dynamic document batching, retention or scheduling. Workshop holds
the recipe; the engine code and its behavioral tests are in Kybern Model Lab,
which does all the training and packing.

The recorded SHA is the source we tested; you don't have to merge it a particular
way. Record the SHA of the Lab you actually run with each run. To check these
configs against it, in an environment that is already set up:

```sh
klab config validate experiments/devmind-v2
```

That validates the model and optimizer sections against the installed schema
and installs nothing. The composed config in
[native commands](native-commands.md) is validated when it is written.

## Limits

The 10,256,578,560-target budget and 50/15/20/10/5 mixture are proposals. We
haven't measured that much supply, and hitting them says nothing about quality.
The 78,252-update horizon only gets packing started; replace it with Lab's
measured schedule before training. The five panel hashes and paths stay blank
until the panels are produced. Filling in JSON fields or passing a schema check
doesn't confirm the artifacts behind them.

This recipe is meant to be portable, so we left out historical configs, machine
paths, raw data, tokenizer hashes and archive records. The memory-map command
rebuilds an identity mapping from the 32,768-token tokenizer you actually pick.
If you swap the tokenizer, rebuild the mapping and check every special ID,
especially the configured padding ID 3.

The v1 source, data and checkpoints stay as they are. Full-state resume is only
for recovering a v2 run; never start v2 from a v1 checkpoint. Before resetting
any drive, copy and checksum everything needed for recovery on its own and test
a restore. Nothing in this scaffold shows that a drive is safe to wipe.
