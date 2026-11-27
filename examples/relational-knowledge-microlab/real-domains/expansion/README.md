# Software retention after astronomy expansion

Can a decoder acquire a second domain without losing performance on the
first? Train one software parent per seed and fork its terminal checkpoint
into two astronomy additions. Both additions contain the same 43 admitted
astronomy training assertions. One uses triples and the other uses
factorization. Both use the software parent’s tokenizer, weights, optimizer
state, and consumed update boundaries. One whole-document pass reaches all
selected records. The representations use different token and update counts.
The expansion keeps the CPython license and notices with the software data
and records Wikidata's CC0-1.0 provenance for the added material.

Score fixed software and astronomy development panels at initialization,
after software training, and after each astronomy addition. Improvement from
the software parent on the astronomy panel measures acquisition. The change
on the software panel measures retention. Both panels use triples, which
aligns with the triples arm’s representation. Report either improvement or
degradation. The parent and both children leave the final families held back.

The [replay follow-up](replay/README.md) revisits 16 software training records
and compares late and interleaved replay at equal exposure and update counts.
The [gradient follow-up](gradient-alignment/README.md) measures local loss
gradient agreement on the same saved checkpoints and development panels.

## Prepare the shared prefix and both additions

Set `PREP` to the output of the [real-domain preparation](../README.md). Set
`RECIPE` to this directory and use a fresh absolute `WORK` outside Git. The decoder uses
128 target tokens per update as a grouping goal, a constant learning rate of
0.002, and a 256-token bound on whole training documents. Use seeds 11, 23
and 37. The development panels use independent fixed 64-token windows.

```bash
set -euo pipefail
WORK="${WORK:-$HOME/.local/share/klab/relational-expansion}"
mkdir -p "$WORK"
cd "$WORK"
export KLAB_WORK_DIR="$WORK/state" OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1
mkdir -p receipts parents panels results
software=$(jq -er .path "$PREP/receipts/software-triples.json")
astronomy=$(jq -er .path "$PREP/receipts/astronomy-triples.json")
factorized=$(jq -er .path "$PREP/receipts/astronomy-factorized.json")
cmp "$PREP/receipts/astronomy-train-original-assertions.txt" \
    "$PREP/receipts/astronomy-train-factorized-assertions.txt"
old_docs=$(jq -er .partitions.train.sequences "$PREP/receipts/software-triples.json")
new_valid=$(jq -er .partitions.validation.sequences "$PREP/receipts/astronomy-triples.json")
klab config derive "$PREP/software-triples-run.yaml" \
  --set 'name="relational-expansion-microlab"' --set model.max_seq_len=256 \
  --set training.seq_len=256 --set training.micro_batch_size=1 \
  --set 'training.matched_stories={"layout":"story","targets_per_update":128,"unpadded_documents":true}' \
  --set optimizer.warmup_steps=0 --set optimizer.peak=0.002 --set optimizer.floor=0.002 \
  --set evaluation.batch_size=1 --set evaluation.text_documents=85 \
  --set "logging.root_dir=\"$WORK/parents\"" --output parent-plan.yaml
parent=$(klab data prepare parent-plan.yaml 2> receipts/parent-prepare.log | tail -n 1)
klab data budget --prepared-root "$parent" --config parent-plan.yaml \
  --passes 1 --no-require-full --output parent.yaml --json > receipts/parent-budget.json
old_tokens=$(jq -er .max_tokens receipts/parent-budget.json)
old_steps=$(jq -er .max_steps receipts/parent-budget.json)
jq -e --argjson count "$old_docs" '
  .coverage.splits.train as $train | $train.preparation.retained_documents == $count
  and $train.matched_groups.documents_per_pass == $count
  and $train.preparation.skipped_documents == 0 and $train.preparation.truncated_documents == 0
' receipts/parent-budget.json >/dev/null
for arm in triples factorized; do
  if [[ "$arm" == triples ]]; then stage="$astronomy"; else stage="$factorized"; fi
  added=$(jq -er .partitions.train.sequences "$PREP/receipts/astronomy-$arm.json")
  revision=$(jq -er .key "$PREP/receipts/astronomy-$arm.json")
  cat "$software/train.jsonl" "$stage/train.jsonl" > "$arm-expanded.jsonl"
  klab config derive parent.yaml --set "dataset.train_path=\"$WORK/$arm-expanded.jsonl\"" \
    --set "dataset.revision=\"software-then-$revision\"" \
    --set 'dataset.license="Software: PSF-2.0 with the pinned license and module notices. Astronomy: CC0-1.0."' \
    --set "dataset.train_max_documents=$((old_docs + added))" \
    --set "training.matched_stories.frozen_update_ends=[$old_tokens]" \
    --set "optimizer.decay_steps=$old_steps" --output "$arm-plan.yaml"
  data=$(klab data prepare "$arm-plan.yaml" 2> "receipts/$arm-prepare.log" | tail -n 1)
  klab data budget --prepared-root "$data" --config "$arm-plan.yaml" \
    --passes 1 --no-require-full --output "$arm.yaml" --json > "receipts/$arm-budget.json"
  jq -e --argjson count "$((old_docs + added))" '
    .coverage.splits.train as $train | $train.preparation.retained_documents == $count
    and $train.matched_groups.documents_per_pass == $count
    and $train.preparation.skipped_documents == 0 and $train.preparation.truncated_documents == 0
  ' "receipts/$arm-budget.json" >/dev/null
  cmp "$parent/validation.npy" "$data/validation.npy"
done
```

## Train paired continuations

Lab checks the old token prefix byte for byte and requires the old terminal
update boundary in both children. The try uses the common terminal parent,
including its optimizer moments. Scoring the old and new domain separately
uses the fixed-panel commands below. The try disables generic prose probes
for this structured development comparison.

```bash
klab config validate factorized.yaml --kind run --json > receipts/factorized-config.json
jq '{
  kind:"delta",
  question:"How does the astronomy addition format change software retention and astronomy acquisition?",
  set:{"dataset.train_path":.config.dataset.train_path,
       "dataset.train_max_documents":.config.dataset.train_max_documents,
       "dataset.revision":.config.dataset.revision,
       "training.max_tokens":.config.training.max_tokens,
       "training.max_steps":.config.training.max_steps}
}' receipts/factorized-config.json > factorized-delta.json
for seed in 11 23 37; do
  run="software-parent-$seed"
  klab config derive parent.yaml --set "seed=$seed" --output "parent-$seed.yaml"
  klab train "parent-$seed.yaml" --run-id "$run" --require-prepared \
    > "receipts/$run.out" 2> "receipts/$run.log"
  parent_run="$WORK/parents/$run"
  generation=$(jq -er .relative_path "$parent_run/checkpoints/latest.json")
  checkpoint="$parent_run/checkpoints/$generation"
  klab checkpoint verify "$checkpoint" --json > "receipts/$run-verify.json"
  jq -n --arg checkpoint "$checkpoint" --argjson seed "$seed" '
    {seed:$seed,probe_tier:"none",continuation:{checkpoint:$checkpoint,append_data:true}}
  ' > "try-$seed.json"
  klab try factorized-delta.json --vs triples.yaml --config "./try-$seed.json" --json \
    > "receipts/try-$seed.json" 2> "receipts/try-$seed.log"
done
```

## Score both domains at every boundary

The panel in each domain uses its complete 64-token validation blocks.
All stages score the same bytes, tokenizer and block selection. The
publication records the number of targets scored and the comparison group.

```bash
klab config derive parent.yaml --set training.matched_stories=null \
  --set training.seq_len=64 --output software-panel.yaml
klab config derive triples.yaml --set training.matched_stories=null \
  --set training.seq_len=64 --set "dataset.validation_path=\"$astronomy/validation.jsonl\"" \
  --set "dataset.validation_max_documents=$new_valid" --output astronomy-panel.yaml
tokenizer="$PREP/software-tokenizer/tokenizer.json"
tokenizer_sha=$(jq -er .sha256 "$PREP/software-tokenizer/tokenizer_manifest.json")
for domain in software astronomy; do
  prepared=$(klab data prepare "$domain-panel.yaml" 2> "receipts/$domain-panel-prepare.log" | tail -n 1)
  klab data coverage --prepared-root "$prepared" --config "$domain-panel.yaml" \
    --json > "receipts/$domain-panel-coverage.json"
  jq -n --arg domain "$domain" --arg path "$prepared" --arg tokenizer "$tokenizer_sha" \
    --slurpfile coverage "receipts/$domain-panel-coverage.json" --slurpfile manifest "$prepared/manifest.json" '
    $coverage[0].splits.validation.blocks as $v |
    {schema_version:1,name:$domain,purpose:"development",prepared_path:$path,
     prepared_manifest_sha256:$manifest[0].manifest_sha256,tokenizer_file_sha256:$tokenizer,
     tokenizer_canonical_sha256:$manifest[0].cache_identity.tokenizer_sha256,
     split:"validation",sampling:"first_eligible_blocks",sequence_length:64,
     blocks:$v.usable_blocks,supervised_targets:$v.supervised_targets,
     batch_size:4,max_forward_positions:$v.complete_block_target_positions}
  ' > "panels/$domain.json"
done

for seed in 11 23 37; do
  parent_run="$WORK/parents/software-parent-$seed"
  start=("$parent_run"/checkpoints/step_00000000_gen_*)
  parent_end="$parent_run/checkpoints/$(jq -er .relative_path "$parent_run/checkpoints/latest.json")"
  [[ ${#start[@]} == 1 && -d ${start[0]} ]]
  for stage in initial parent triples factorized; do
    case "$stage" in
      initial) root="$parent_run"; checkpoint=${start[0]} ;;
      parent) root="$parent_run"; checkpoint="$parent_end" ;;
      *)
        if [[ "$stage" == triples ]]; then arm=baseline; else arm=candidate; fi
        root=$(jq -er --arg arm "$arm" '.arms[$arm].run_dir' "receipts/try-$seed.json")
        checkpoint="$root/$(jq -er --arg arm "$arm" '.arms[$arm].checkpoint' "receipts/try-$seed.json")"
        ;;
    esac
    checkpoint_sha=$(jq -er .sha256 "$checkpoint/manifest.json")
    for domain in software astronomy; do
      spec="panels/$seed-$stage-$domain.json"
      jq --arg sha "$checkpoint_sha" '. + {checkpoint_sha256:$sha}' "panels/$domain.json" > "$spec"
      klab eval "$(basename "$root")" --runs-dir "$(dirname "$root")" --checkpoint "$checkpoint" \
        --panel "$spec" --output "$WORK/results/$seed-$stage-$domain.json" \
        > "receipts/$seed-$stage-$domain.out" 2> "receipts/$seed-$stage-$domain.log"
    done
  done
done
```

## CPU result

Three parent runs and six continuations completed at 102,720 parameters.
Every parent used 5,027 software targets over 35 updates. Each new astronomy
branch passed the token-prefix, validation, and update-boundary checks and
consumed exactly its one-pass budget. The [run record](results/2026-11-27.json)
includes all 24 development scores, source keys, exact checkpoints and
comparison groups. A fresh run with the combined license statement reproduced
all 24 loss values exactly.

| Boundary | Added targets | Added updates | Software loss | Astronomy loss |
| --- | ---: | ---: | ---: | ---: |
| Initialization | 0 | 0 | 5.733 | 5.768 |
| After software | 5,027 | 35 | 3.194 | 4.822 |
| After astronomy triples | 2,109 | 15 | 3.819 | 2.893 |
| After astronomy factorization | 1,586 | 11 | 3.547 | 3.297 |

Both astronomy additions improved astronomy loss and worsened software
loss in every seed. Relative to triples, the factorized branch ended
**0.272 ± 0.131 nats lower** on software and **0.404 ± 0.028 nats higher**
on astronomy. These are paired means and standard errors over three
seeds. The shorter factorized stream also uses fewer targets and updates,
so the comparison captures the combined effect of representation and
exposure. The astronomy score uses a triples panel.
