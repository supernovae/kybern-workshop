# Native authoring and execution path

These are staged instructions, not an executable launch script. Use an existing
provisioned environment and a new persistent work root outside Git. Set `RECIPE`
to this package, `WORKSHOP` to its repository, and `V2` to a new work directory.
Paths below must be absolute. No command installs dependencies. Preparation and
workload commands require their own resource and execution authorization.

## 1. Bind previously verified inputs

After code qualification, use the existing native corpus preparation interface
and the shared phase map at `../devmind/preparation/preparation.json`. Render its
bindings for this new v2 corpus, not the historical three-pillar acquisition
project. Inspect a phase without executing it with `sparselab attempt phase-command`.
Native steps cover admission inspection, split inventory, family freezing, build,
release audit, tokenizer fitting/verification, measured unique-token floors,
mixture materialization/verification and prepared-input publication. Source IDs
and release identities in the v2 mixture/floor templates are intentionally unbound.
Map every chosen source ID to a pillar; multiple source IDs can map to one pillar.
Keep a complete frozen feasible mixture, not a succession of exhausted shards.

Copy `binding.example.json` to `$V2/bindings.json` and bind all fields from verified
native outputs. Five heldout panels must share the model tokenizer and 4K context;
fill their *measured* supervised-target counts and independently verified manifest
hashes. Template panel sizes (64 blocks each) are a proposal. The example does not
claim those blocks already exist. Choose a backend and device explicitly.

```sh
python "$WORKSHOP/scripts/bind-experiment.py" "$RECIPE/experiment.json" \
  --bindings "$V2/bindings.json" --output "$V2/packing.json"
sparselab tokenizer verify "$V2/packing.json" --json
sparselab tokenizer memory-map "$TOKENIZER" --mode identity \
  --output "$V2/memory-map.json" --bind-config "$V2/packing.json" \
  --config-output "$V2/mapped.yaml"
```

`TOKENIZER` must be the same file as the bound tokenizer. The map binds its bytes;
identity mode preserves case, whitespace and code spelling. The binder itself
performs schema validation only. It does not prove paths exist or admit a corpus.
The five panel declarations are checked by the native prepared/evaluation path.

Optional runtime optimization uses native derivation, before publishing inputs:

```sh
sparselab config derive "$V2/mapped.yaml" \
  --set 'runtime.backend="xpu"' --set 'runtime.device_index=0' \
  --set 'runtime.secondary_device_indices=[1]' --set 'runtime.precision="bf16"' \
  --set 'runtime.compile_dynamic_shapes=true' \
  --set 'runtime.compile_output_head_loss=true' \
  --set 'runtime.compile_transformer_blocks=true' --output "$V2/runtime.yaml"
```

For the remaining commands, `CONFIG` names mapped.yaml or the explicitly derived
runtime.yaml. Do not infer device availability or multi-GPU execution from a backend
string. Select a registered native runtime/profile and owned devices separately.
The native secondary-device setting replaces dependency on the previous external
two-GPU launcher. Verify both selected physical devices and replica behavior before
actual work; the example does not claim they are available.

## 2. Pack, measure schedule, rebind and cold-verify

```sh
sparselab data prepared-inputs publish "$CONFIG" --output "$V2/bootstrap-inputs" \
  --resource-envelope "$ENVELOPE"
sparselab data prepared-inputs verify "$CONFIG" "$V2/bootstrap-inputs"
sparselab config schedule "$CONFIG" --prepared-inputs "$V2/bootstrap-inputs" \
  --output "$V2/final.yaml"
sparselab data prepared-inputs publish "$V2/final.yaml" --output "$V2/final-inputs" \
  --resource-envelope "$ENVELOPE"
sparselab data prepared-inputs verify "$V2/final.yaml" "$V2/final-inputs"
```

The schedule command derives the terminal update and cosine-decay horizon from
actual authenticated packed groups, rather than dividing targets by nominal batch
size. It binds the checkpoint terminal boundary consistently and refuses missing
supply. Inspect its receipt, including actual committed targets and partial final
update semantics. A schedule change changes RunConfig identity: do not feed the
bootstrap bundle to the final config. Republish with native cache reuse, then
cold-verify the final bundle. No private grouping or identity bypass is permitted.

The optimizer warmup is a deliberate 1,000-step proposal. If the measured horizon
cannot support it, revise the experiment explicitly instead of silently clipping
warmup. Final schedule derivation is not evidence that the learning rate is stable.

## 3. Qualify and launch only when separately authorized

```sh
sparselab inspect "$V2/final.yaml" --json
sparselab stage "$V2/final.yaml" --through validate --prepared-inputs "$V2/final-inputs" \
  --cold-verify --output "$V2/validated-stage" --resource-envelope "$ENVELOPE"
```

Schema and data validation are not a finite-gradient or accelerator test. When
runtime qualification is authorized, native `stage --through smoke` or `warmup`
executes real work. Use a new stage output and the selected runtime profile; do
not label it training-free. Reuse applicable prior runtime verification only when
code, dimensions, backend and ownership have not changed.

After reviewing data, schedule, qualification, storage and behavior criteria:

```sh
sparselab train "$V2/final.yaml" --run-id "$FRESH_RUN_ID" \
  --stage-bundle "$V2/validated-stage" --resource-envelope "$ENVELOPE"
```

Do not add `--resume`, `--promote`, `--add-ngram-memory`, `--append-data`, historical
cursors or old frozen boundaries to the fresh command. Select the native runtime
explicitly where needed. A resource envelope is a bound, not a spend approval.

## 4. Evaluate, recover and report exact generations

```sh
sparselab checkpoint verify "$GENERATION" --config "$V2/final.yaml" --json
sparselab probe "$GENERATION" --config "$RECIPE/probe-standard.json" --json
sparselab probe "$GENERATION" --config "$RECIPE/probe-full.json" --json
sparselab report "$FRESH_RUN_ID" --kind run --json
```

Probes execute inference; the full tier additionally needs an already provisioned
lm-eval dependency and task data. Missing task data or results remain missing, not
passes. Bind the correct runtime before inference. Use exact checkpoint paths,
not an unverified latest generation. Keep per-pillar losses separate from aggregate
loss and probe verdicts. Run `probe-final.json` only once on the already chosen
candidate; never use its held-back split for tuning.

Recovery is a separate native full-state operation after checkpoint verification:

```sh
sparselab train "$V2/final.yaml" --resume "$GENERATION" --run-id "$RECOVERY_RUN_ID" \
  --resource-envelope "$ENVELOPE"
```

Resume only a matching v2 generation, preserving optimizer/RNG/counters and data
identity. Do not use drift or budget-extension overrides to hide mismatches. Retain
the native cancellation/failure record if a run stops. Back up full state,
tokenizer, config, prepared/source closure and environment/code pins independently
before any destructive cleanup. Checkpoints alone are not a recovery closure.
