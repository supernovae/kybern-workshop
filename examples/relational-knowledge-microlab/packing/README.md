# Matched basin prose packing

This variant of the [Relational Knowledge Microlab](../README.md) tests
whether neighboring passages from the same basin improve learning. The
frozen release splits each world into six link sentences and one rule
paragraph. Each basin is both a source and a split family. The 12 training
families yield 84 passages. Four development families supply 28 validation
passages, and four final families stay held out.

The random arm uses the mixture's seeded order. The coherent arm groups
the exact same records by basin with Corpus source ordering. Both use the
same BPE fitted on TRAIN, reference schedule format, contiguous prepared
loader, 64-token attention windows, causal supervision and four blocks
per update. The recipe checks all record memberships, the segment
inventory, the packed loss mask and the validation array before training.
The runs apply 16 complete passes over the selected mixture. Compare
model seeds 11, 23 and 37 for each of two independently seeded orders,
29 and 53.

## Build and measure the release

Set `RECIPE` to the absolute path of the parent microlab directory.
Use Lab with whole-pass budgeting for Corpus mixtures, `jq`, and a fresh
work directory outside Git. The authored worlds are pinned in
[`sources/worlds.json`](../sources/worlds.json). The shell projects their
already-declared prose into local passages and Lab does acquisition,
family assignment and release construction.

```bash
WORK="$HOME/.local/share/klab/coherent-prose-study"
mkdir -p "$WORK"
cd "$WORK"
export KLAB_WORK_DIR="$WORK/state"
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=1

project="$KLAB_WORK_DIR/project"
mkdir -p receipts "$project"/{sources,text,transforms}
cp "$RECIPE/packing/release.yaml" "$project/release.yaml"
worlds="$RECIPE/sources/worlds.jsonl"
expected=$(jq -er '.sources[0].sha256' "$RECIPE/sources/worlds.json")
printf '%s  %s\n' "$expected" "$worlds" | sha256sum --check > receipts/input-pin.txt
while IFS= read -r world; do
  basin=$(jq -er '.id | sub("^basin:";"")' <<< "$world")
  mkdir -p "$project/text/$basin"
  jq -ce '.prose | split(". ") | if length == 10 then (.[0:6][] + "."), (.[6:] | join(". ")) else error("unexpected basin passage count") end' <<< "$world" |
    jq -rs 'to_entries[] | [.key,.value] | @tsv' |
    while IFS=$'\t' read -r index passage; do
      printf '%s\n' "$passage" > "$project/text/$basin/$index.txt"
    done
  klab corpus render-declaration --template "$RECIPE/packing/source.template.yaml" \
    --values-json "$(jq -cn --arg BASIN "$basin" '$ARGS.named')" \
    --output "$project/sources/$basin.yaml" > "receipts/source-$basin.json"
done < "$worlds"
jq -s '{schema_version:1,id:"coherent-basin-prose",sources:(map("sources/"+(.id|sub("^basin:";""))+".yaml")|sort),transforms:["transforms/lm.yaml"],splits:"splits.yaml",release:"release.yaml"}' "$worlds" > "$project/corpus.yaml"
jq -s '{id:"basin-lm",version:"1",kind:"lm_text",parameters:{},inputs:map(.id|sub("^basin:";"basin-"))}' "$worlds" > "$project/transforms/lm.yaml"
jq -s '{schema_version:1,unit:"source_document_family",family_key:"source_family",assignments:(map({key:(.family|sub("^basin:";"basin-")),value:.split})|from_entries)}' "$worlds" > "$project/splits.yaml"
klab corpus acquire "$project/corpus.yaml" > receipts/acquire.json 2> receipts/acquire.log
klab corpus build "$project/corpus.yaml" --offline > receipts/build.txt 2> receipts/build.log
klab corpus freeze "$(cat receipts/build.txt)" > receipts/release.txt 2> receipts/freeze.log
cp "$RECIPE"/{model.yaml,dataset.json} .
klab config compose model.yaml dataset.json --output export-base.yaml > receipts/export-base.log
klab corpus export "$(cat receipts/release.txt)" --view lm --base-run-config export-base.yaml --vocab-size 384 --min-frequency 1 > receipts/export.txt 2> receipts/export.log
release=$(cat receipts/release.txt)
exported=$(cat receipts/export.txt)
fit="$exported/tokenizer.yaml"
klab tokenizer train "$fit" > receipts/tokenizer.txt 2> receipts/tokenizer.log
tokenizer="$exported/tokenizer/tokenizer.json"
klab corpus describe "$release" --tokenizer "$tokenizer" --workers 2 > receipts/describe.json 2> receipts/describe.log
klab config validate "$exported/run.yaml" --kind run --json > receipts/exported-run.json
```

## Seal equivalent schedules and derive both budgets

The release measures 1,641 TRAIN text tokens and 84 documents for this
tokenizer. Each scheduled document also contributes one EOS. Use the
measured count to take the entire TRAIN release with one exposure.
Independent mixture audits check selection and reordering. The
`--no-require-full` budget flag derives whole passes over the selected,
verified mixture.

```bash
cp "$RECIPE/packing/try-policy.yaml" "$KLAB_WORK_DIR/try-policy.yaml"
release=$(cat receipts/release.txt)
exported=$(cat receipts/export.txt)
fit="$exported/tokenizer.yaml"
tokenizer="$exported/tokenizer/tokenizer.json"
inventory="$WORK/families.jsonl"
worlds="$RECIPE/sources/worlds.jsonl"
targets=$(jq -er '.measurement.views.lm.train | .actual_tokens + .records' receipts/describe.json)
sources=$(jq -sc 'map({key:(.id|sub("^basin:";"basin-")),value:"basins"})|from_entries' "$worlds")
for seed in 29 53; do
  case_dir="$WORK/order-$seed"
  mkdir -p "$case_dir"
  jq -n --arg release "$release" --arg fit "$fit" --arg inventory "$inventory" \
    --argjson sources "$sources" --argjson quota "$targets" --argjson seed "$seed" \
    '{schema_version:1,release_path:$release,tokenizer_config:$fit,family_inventory:$inventory,
      source_strata:$sources,target_quotas:{basins:$quota},seed:$seed,max_exposures:1,
      token_cache:"sealed",token_output:"references"}' > "$case_dir/random.json"
  random="$case_dir/random"
  coherent="$case_dir/coherent"
  if [[ $seed == 29 ]]; then
    klab corpus describe "$release" --tokenizer "$tokenizer" --mixture "$case_dir/random.json" --workers 2 \
      > receipts/quota-check.json 2> receipts/quota-check.log
    if [[ ! -e $inventory ]]; then
      klab corpus derive-family-inventory "$case_dir/random.json" > receipts/families.json 2> receipts/families.log
    fi
  fi
  jq --arg declaration "$case_dir/random.json" --arg output "$random" \
    '. + {sequence_order:{kind:"source",base_declaration:$declaration,base_output:$output}}' \
    "$case_dir/random.json" > "$case_dir/coherent.json"
  for arm in random coherent; do
    /usr/bin/time -f %e -o "$case_dir/$arm.materialization-seconds" \
      klab corpus materialize-mixture "$case_dir/$arm.json" --output "$case_dir/$arm" --workers 2 \
      > "$case_dir/$arm.receipt.json" 2> "$case_dir/$arm.materialize.log"
    klab corpus verify-mixture "$case_dir/$arm.json" --output "$case_dir/$arm" --workers 2 --audit \
      > "$case_dir/$arm.audit.json" 2> "$case_dir/$arm.audit.log"
    jq -csS 'sort_by(.document_id,.exposure)' "$case_dir/$arm/train.records.jsonl" \
      > "$case_dir/$arm.membership.json"
    jq -n --slurpfile exported receipts/exported-run.json --slurpfile schedule "$case_dir/$arm.receipt.json" \
      --arg tokenizer "$tokenizer" --arg cache "$case_dir/prepared" --arg declaration "$case_dir/$arm.json" \
      --arg output "$case_dir/$arm" --arg runs "$case_dir/runs" \
      '$exported[0].config.dataset as $d | $schedule[0] as $m | {
        name:"coherent-prose-microlab",tokenizer:{path:$tokenizer},logging:{root_dir:$runs},
        evaluation:{text_documents:$d.validation_max_documents},
        dataset:{source:"local_token_mixture",revision:$d.revision,license:$d.license,
          cache_dir:$cache,train_path:$m.train_schedule_path,validation_path:$d.validation_path,
          train_max_tokens:($m.actual_target_tokens|[.[]]|add),train_max_documents:$m.records,
          validation_max_tokens:$d.validation_max_tokens,validation_max_documents:$d.validation_max_documents,
          mixture_declaration_path:$declaration,mixture_output_path:$output}}' > "$case_dir/$arm.inputs.json"
    klab config compose model.yaml "$case_dir/$arm.inputs.json" --output "$case_dir/$arm-unbudgeted.yaml" \
      > "$case_dir/$arm.compose.log"
    klab data prepare "$case_dir/$arm-unbudgeted.yaml" > "$case_dir/$arm.prepared.txt" 2> "$case_dir/$arm.prepare.log"
    prepared=$(tail -n 1 "$case_dir/$arm.prepared.txt")
    klab data budget --prepared-root "$prepared" --config "$case_dir/$arm-unbudgeted.yaml" \
      --no-require-full --passes 16 --output "$case_dir/$arm-run.yaml" --json > "$case_dir/$arm.budget.json"
  done
  cmp "$case_dir/random.membership.json" "$case_dir/coherent.membership.json"
  jq -es '.[0].records == 84 and .[1].records == 84 and
    .[0].actual_target_tokens == .[1].actual_target_tokens and
    (.[0].token_schedule.segments|sort) == (.[1].token_schedule.segments|sort) and
    .[0].token_schedule.sha256 != .[1].token_schedule.sha256' \
    "$random/receipt.json" "$coherent/receipt.json" > "$case_dir/shared-schedule-check.json"
  random_prepared=$(tail -n 1 "$case_dir/random.prepared.txt")
  coherent_prepared=$(tail -n 1 "$case_dir/coherent.prepared.txt")
  cmp "$random_prepared/train_supervision.npy" "$coherent_prepared/train_supervision.npy"
  cmp "$random_prepared/validation.npy" "$coherent_prepared/validation.npy"
  jq -cn --arg RANDOM_RUN "$case_dir/random-run.yaml" --arg COHERENT_DIR "$coherent" \
    --arg COHERENT_DECLARATION "$case_dir/coherent.json" '$ARGS.named' > "$case_dir/sweep-bindings.json"
  klab corpus render-declaration --template "$RECIPE/packing/sweep.template.yaml" \
    --values-json "$(cat "$case_dir/sweep-bindings.json")" --output "$KLAB_WORK_DIR/sweep-$seed.yaml" \
    > "$case_dir/sweep-render.json"
  printf 'Verified content, masks and validation for packing seed %s\n' "$seed"
done
```

## Train and score

The [try policy](try-policy.yaml) records the preflight waiver for this
audited, 108-step CPU workload in each try and run. The two schedules
still go through the ordinary mixture and prepared-data verifiers.

```bash
for seed in 29 53; do
  klab sweep "$KLAB_WORK_DIR/sweep-$seed.yaml" --backend cpu --json \
    > "$WORK/order-$seed/sweep.json"
done
```

Use `klab report SWEEP_ID` for the paired prose-loss results. Score the
same [development choices](../evaluation/development.json) at each try's
recorded checkpoint. Seen-family relation questions are recall diagnostics.
The 16 context questions use four development families. Keep the
separate [final declaration](../evaluation/final.json) for a chosen
representation after independent development evidence.

```bash
klab eval RUN_ID --runs-dir RUNS --checkpoint GENERATION \
  --ranking "$RECIPE/evaluation/development.json"
```

## Paired CPU results

Lab `ae5ee18d` trained all 12 runs with 106,816 parameters, 27,600
supervised targets and 108 optimizer updates per run. The [run record](results/2026-11-27.json)
links the release, schedules, prepared arrays, masks, checkpoints and
ranking results. Each row averages three paired model seeds.

| Packing seed | Source transitions | Multi-basin blocks of 27 | Coherent minus random prose loss | Context choices, random → coherent |
| --- | ---: | ---: | ---: | ---: |
| 29 | 79 → 11 | 27 → 11 | −0.0349 ± 0.0248 nats | 33.3% → 39.6% |
| 53 | 75 → 11 | 25 → 11 | −0.0012 ± 0.0272 nats | 29.2% → 35.4% |

The loss uncertainty is the standard error across the three model seeds
within each packing seed. Both loss differences were within seed noise.
Context accuracy improved by three correct choices across the 48 scored
responses to 16 questions per packing seed. Both orders reuse the same
four development families, so this leaves open whether the gain transfers.
The final panel stayed held back.

Three fast probe reruns still lacked enough generated text for a repetition
score. Two seed-23 pairs advanced to the standard tier. Their full repeats
recorded missing `lm-eval` in this environment. No representation advanced
on the strength of the development scores.

The tiny schedule commands took 1.43–1.62 s with warm segments, including
CLI startup and verification. Median training wall times were 2.00–2.02 s
per arm. A fresh preparation replay reproduced all four schedule digests
and the tokenizer digest. These measurements describe the local pilot.
