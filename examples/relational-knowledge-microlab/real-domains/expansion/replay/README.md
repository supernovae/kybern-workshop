# Software replay during astronomy expansion

Does revisiting old training records protect software performance while the
same model learns astronomy? Reuse the three terminal software checkpoints
from the [expansion study](../README.md). The earlier astronomy-triples run is
the no-replay control. This variant adds 16 software triples copied from the
original 151 training records. Select the midpoint of each of 16 equal
ordinal intervals in the pinned source order before training or scoring.
The replay records come entirely from TRAIN.

- **Late replay** appends all 43 astronomy triples, followed by the 16 replay
  records.
- **Interleaved replay** spreads the same 16 records through the astronomy
  stream. It preserves each domain's original relative order.

Both replay arms start from the same software checkpoint in each seed,
including optimizer state. They use exactly the same added records. The
comparison against no replay measures the effect of adding old exposures and
their extra compute. The comparison between the replay arms holds exposure
fixed and measures ordering. Measure the actual optimizer update counts
before training and require them to match for the ordering comparison.

## Prepare the two replay orders

Set `PREP` to the [real-domain preparation](../../README.md) output and
`EXPANSION` to the completed [expansion run directory](../README.md). Set
`RECIPE` to this directory. Use a fresh absolute work directory. The commands
keep the previously prepared data and native checkpoints in their original
directories.

```bash
set -euo pipefail
WORK="${WORK:-$HOME/.local/share/klab/relational-expansion-replay}"
mkdir -p "$WORK"
cd "$WORK"
export KLAB_WORK_DIR="$WORK/state" OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1
mkdir -p receipts results panels

software=$(jq -er .path "$PREP/receipts/software-triples.json")
astronomy=$(jq -er .path "$PREP/receipts/astronomy-triples.json")
old_docs=$(jq -er .partitions.train.sequences "$PREP/receipts/software-triples.json")
new_docs=$(jq -er .partitions.train.sequences "$PREP/receipts/astronomy-triples.json")
count=16
jq -s -c --argjson n "$count" '
  . as $records | length as $total |
  if $total < $n then error("insufficient replay records") else
    range(0; $n) as $i | $records[((2*$i+1)*$total/(2*$n)|floor)]
  end
' "$software/train.jsonl" > software-replay.jsonl
cat "$astronomy/train.jsonl" software-replay.jsonl > late-suffix.jsonl
jq -s -c --slurpfile replay software-replay.jsonl '
  . as $astro | length as $total | ($replay|length) as $n |
  range(0;$total) as $i |
  $astro[$i], $replay[($i*$n/$total|floor):(($i+1)*$n/$total|floor)][]
' "$astronomy/train.jsonl" > interleaved-suffix.jsonl
for arm in late interleaved; do
  jq -sS 'sort_by(.text)' "$arm-suffix.jsonl" > "receipts/$arm-membership.json"
done
cmp receipts/late-membership.json receipts/interleaved-membership.json
if cmp -s late-suffix.jsonl interleaved-suffix.jsonl; then
  printf '%s\n' 'Expected different replay orders' >&2
  exit 1
fi

for arm in late interleaved; do
  cat "$software/train.jsonl" "$arm-suffix.jsonl" > "$arm-expanded.jsonl"
  klab config derive "$EXPANSION/triples.yaml" \
    --set "dataset.train_path=\"$WORK/$arm-expanded.jsonl\"" \
    --set "dataset.revision=\"astronomy-software-replay-$arm\"" \
    --set "dataset.train_max_documents=$((old_docs + new_docs + count))" \
    --output "$arm-plan.yaml"
  prepared=$(klab data prepare "$arm-plan.yaml" 2> "receipts/$arm-prepare.log" | tail -n 1)
  klab data budget --prepared-root "$prepared" --config "$arm-plan.yaml" \
    --passes 1 --no-require-full --output "$arm.yaml" --json > "receipts/$arm-budget.json"
  jq -e --argjson count "$((old_docs + new_docs + count))" '
    .coverage.splits.train as $train | $train.preparation.retained_documents == $count
    and $train.matched_groups.documents_per_pass == $count
    and $train.preparation.skipped_documents == 0 and $train.preparation.truncated_documents == 0
  ' "receipts/$arm-budget.json" >/dev/null
done
jq -es '
  .[0].max_tokens == .[1].max_tokens
  and .[0].max_steps == .[1].max_steps
  and .[0].coverage.splits.train.matched_groups.rows_per_pass ==
      .[1].coverage.splits.train.matched_groups.rows_per_pass
  and .[0].coverage.splits.validation.preparation.sha256 ==
      .[1].coverage.splits.validation.preparation.sha256
' receipts/{late,interleaved}-budget.json >/dev/null
```

## Fork the same checkpoints and score the fixed panels

The paired try uses late replay as its baseline. The no-replay branch and the
parent scores come from the original expansion study. Keep the held-out
panels byte-identical to that study. Both new arms disable the generic prose
probes and score the fixed development panels separately.

```bash
klab config validate interleaved.yaml --kind run --json > receipts/interleaved-config.json
jq '{
  kind:"delta",
  question:"Does interleaving the same software replay records change retention or astronomy acquisition?",
  set:{"dataset.train_path":.config.dataset.train_path,
       "dataset.revision":.config.dataset.revision}
}' receipts/interleaved-config.json > interleaved-delta.json
for seed in 11 23 37; do
  parent=$(jq -er .continuation.checkpoint "$EXPANSION/receipts/try-$seed.json")
  expected=$(jq -er .continuation.sha256 "$EXPANSION/receipts/try-$seed.json")
  klab checkpoint verify "$parent" --json > "receipts/parent-$seed-verify.json"
  jq -e --arg sha "$expected" '.sha256 == $sha' "$parent/manifest.json" >/dev/null
  jq -n --arg checkpoint "$parent" --argjson seed "$seed" '
    {seed:$seed,probe_tier:"none",continuation:{checkpoint:$checkpoint,append_data:true}}
  ' > "try-$seed.json"
  klab try interleaved-delta.json --vs late.yaml --config "./try-$seed.json" --json \
    > "receipts/try-$seed.json" 2> "receipts/try-$seed.log"
  for term in late:baseline interleaved:candidate; do
    name=${term%:*}
    role=${term#*:}
    run=$(jq -er --arg role "$role" '.arms[$role].run_dir' "receipts/try-$seed.json")
    checkpoint=$(jq -er --arg role "$role" '.arms[$role].checkpoint' "receipts/try-$seed.json")
    sha=$(jq -er --arg role "$role" '.arms[$role].checkpoint_sha256' "receipts/try-$seed.json")
    for domain in software astronomy; do
      spec="panels/$seed-$name-$domain.json"
      jq --arg sha "$sha" '. + {checkpoint_sha256:$sha}' "$EXPANSION/panels/$domain.json" > "$spec"
      klab eval "$(basename "$run")" --runs-dir "$(dirname "$run")" --checkpoint "$run/$checkpoint" \
        --panel "$spec" --output "$WORK/results/$seed-$name-$domain.json" \
        > "receipts/$seed-$name-$domain.out" 2> "receipts/$seed-$name-$domain.log"
      group=$(jq -er .comparison_group "$EXPANSION/results/$seed-triples-$domain.json")
      jq -e --arg group "$group" '.status == "complete" and .comparison_group == $group' \
        "results/$seed-$name-$domain.json" >/dev/null
    done
  done
done
```

## CPU result

All six continuations completed. Each replay arm used 2,651 added targets
over 19 updates, including 542 software replay targets. The earlier
astronomy-only control used 2,109 targets over 15 updates. Both replay
orders used the same tokenizer, document inventory, and development
panels. A fresh preparation reproduced the exact source files and
prepared arrays.

| After the software parent | Added targets | Added updates | Software loss | Astronomy loss |
| --- | ---: | ---: | ---: | ---: |
| Parent | 0 | 0 | 3.194 | 4.822 |
| Astronomy, no replay | 2,109 | 15 | 3.819 | 2.893 |
| Astronomy, late software replay | 2,651 | 19 | 3.117 | 2.804 |
| Astronomy, interleaved software replay | 2,651 | 19 | 3.176 | 2.549 |

Both replay orders improved software loss relative to the no-replay
control in every seed. The extra replay exposure brought average software
loss back near the parent. At matched exposure and update counts,
interleaving lowered astronomy loss by **0.255 ± 0.040 nats** and
raised software loss by **0.059 ± 0.029 nats** relative to late replay.
Both directions held across the three seeds. Differences are paired
means and standard errors. The sample covers one replay selection and
one domain sequence. Final families remained held back.

The [run record](results/2026-11-27.json) retains the parent, control and
child checkpoint identities, source projections, and panel scores.
