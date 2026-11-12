# Native authoring and execution path

These steps are meant to be read and run one at a time; this is not a launch
script. Use an environment that is already set up and a new persistent work root
outside Git. Set `RECIPE` to this package, `WORKSHOP` to its repository, and `V2`
to a new work directory. All paths below must be absolute. None of the commands
install dependencies. Preparation and training each need their own resource and
run approval.

## 1. Bind previously verified inputs

After code qualification, prepare the corpus with Lab's corpus preparation
commands and the shared phase map at `../devmind/preparation/preparation.json`.
Fill in its bindings for the new v2 corpus; the historical three-pillar
acquisition project doesn't apply. To see a phase's command without running it,
use `klab attempt phase-command`. The Lab steps cover admission inspection, split
inventory, family freezing, build, release audit, tokenizer fitting and checks,
measured unique-token floors, mixture materialization and checks, and
prepared-input publication. Source IDs and release IDs in the v2 mixture and
floor templates are left blank on purpose. Map every source ID you choose to a
pillar; several source IDs can share one pillar. Freeze one complete mixture that
can actually be filled, rather than moving from one exhausted shard to the next.

Copy `binding.example.json` to `$V2/bindings.json` and fill every field from
checked Lab outputs. The five held-out panels must use the model's tokenizer and
4K context. Enter their *measured* supervised-target counts and their manifest
hashes, checked separately. The 64 blocks per panel in the template is a
proposal; those blocks don't exist yet. Choose a backend and device explicitly.

```sh
klab config compose "$RECIPE/run.json" model="$RECIPE/model.json" \
  optimizer="$RECIPE/optimizer.json" "$V2/bindings.json" \
  --output "$V2/packing.yaml"
klab tokenizer verify "$V2/packing.yaml" --json
klab tokenizer memory-map "$TOKENIZER" --mode identity \
  --output "$V2/memory-map.json" --bind-config "$V2/packing.yaml" \
  --config-output "$V2/mapped.yaml"
```

`TOKENIZER` must be the same file as the bound tokenizer; the map is tied to its
bytes. Identity mode keeps case, whitespace and code spelling. `config compose`
checks the schema and names any field still unbound. It doesn't check that paths
exist or that the corpus has been admitted. Lab's prepared-input and evaluation
steps check the five panel configs.

To tune the runtime, derive a new config before publishing inputs:

```sh
klab config derive "$V2/mapped.yaml" \
  --set 'runtime.backend="xpu"' --set 'runtime.device_index=0' \
  --set 'runtime.secondary_device_indices=[1]' --set 'runtime.precision="bf16"' \
  --set 'runtime.compile_dynamic_shapes=true' \
  --set 'runtime.compile_output_head_loss=true' \
  --set 'runtime.compile_transformer_blocks=true' --output "$V2/runtime.yaml"
```

For the remaining commands, `CONFIG` is mapped.yaml or the derived runtime.yaml.
A backend string doesn't tell you which devices exist or whether multi-GPU works.
Pick a registered runtime/profile and the devices you own separately. Lab's
secondary-device setting replaces the old external two-GPU launcher. Check both
physical devices and the replica behavior before real work; the example assumes
nothing about what hardware you have.

## 2. Pack, measure schedule, rebind and cold-verify

```sh
klab data prepared-inputs publish "$CONFIG" --output "$V2/bootstrap-inputs" \
  --resource-envelope "$ENVELOPE"
klab data prepared-inputs verify "$CONFIG" "$V2/bootstrap-inputs"
klab config schedule "$CONFIG" --prepared-inputs "$V2/bootstrap-inputs" \
  --output "$V2/final.yaml"
klab data prepared-inputs publish "$V2/final.yaml" --output "$V2/final-inputs" \
  --resource-envelope "$ENVELOPE"
klab data prepared-inputs verify "$V2/final.yaml" "$V2/final-inputs"
```

The schedule command works out the final update and the cosine-decay horizon from
the actual packed groups, instead of dividing targets by the nominal batch size.
It sets the terminal checkpoint boundary to match, and refuses if supply is
missing. Read its receipt, including the actual committed targets and how the
partial final update is handled. A new schedule makes a new RunConfig, so don't
use the bootstrap bundle with the final config. Republish with Lab's cache reuse,
then cold-check the final bundle. Don't regroup data by hand or work around the
hash checks.

The 1,000-step warmup is a deliberate choice. If the measured horizon is too
short for it, revise the experiment openly instead of quietly shortening warmup.
Deriving the schedule doesn't tell you whether the learning rate is stable.

## 3. Qualify and launch only when separately authorized

```sh
klab inspect "$V2/final.yaml" --json
klab stage "$V2/final.yaml" --through validate --prepared-inputs "$V2/final-inputs" \
  --cold-verify --output "$V2/validated-stage" --resource-envelope "$ENVELOPE"
```

Schema and data validation don't test gradients or the accelerator. Once runtime
qualification is approved, `stage --through smoke` or `warmup` does real work on
the device. Give it a new stage output and the chosen runtime profile, and record
it as real work. Reuse an earlier runtime check only if the code, dimensions,
backend and device ownership are all unchanged.

After you have reviewed the data, schedule, qualification, storage and behavior
criteria:

```sh
klab train "$V2/final.yaml" --run-id "$FRESH_RUN_ID" \
  --stage-bundle "$V2/validated-stage" --resource-envelope "$ENVELOPE"
```

Keep `--resume`, `--promote`, `--add-ngram-memory`, `--append-data`, historical
cursors and old frozen boundaries out of the fresh command. Choose the runtime
explicitly where needed. A resource envelope sets limits; it doesn't approve
spending.

## 4. Evaluate, recover and report exact generations

```sh
klab checkpoint verify "$GENERATION" --config "$V2/final.yaml" --json
klab probe "$GENERATION" --config "$RECIPE/probe-standard.json" --json
klab probe "$GENERATION" --config "$RECIPE/probe-full.json" --json
klab report "$FRESH_RUN_ID" --kind run --json
```

Probes run inference. The full tier also needs lm-eval and its task data already
installed. If task data or results are missing, record them as missing, not as
passes. Bind the right runtime before inference. Use exact checkpoint paths
rather than whatever the latest generation happens to be. Report per-pillar
losses separately from the aggregate loss and the probe verdicts. Run
`probe-final.json` only once, on the candidate you've already chosen, and never
tune on its held-back split.

Recovery is a separate full-state operation, after the checkpoint check:

```sh
klab train "$V2/final.yaml" --resume "$GENERATION" --run-id "$RECOVERY_RUN_ID" \
  --resource-envelope "$ENVELOPE"
```

Resume only a matching v2 generation, keeping optimizer, RNG, counters and data
unchanged. Don't use drift or budget-extension overrides to paper over a
mismatch. If a run stops, keep Lab's cancellation or failure record. Before any
destructive cleanup, back up the full state, tokenizer, config, prepared and
source data, and environment and code pins to separate storage. Checkpoints
alone aren't enough to recover a run.
