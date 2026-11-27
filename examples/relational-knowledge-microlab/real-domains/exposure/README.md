# Matched relational exposure

Do the same assertions train a small decoder differently as triples and as
factorized relationships? This study pairs seeds 11, 23 and 37 for each of the
[astronomy and software corpora](../README.md). Each domain uses its own
TRAIN-fitted tokenizer. Within a pair, tokenizer bytes, decoder, validation
bytes, scoring window, optimizer and precision are shared.

- **Equal assertion exposure.** Every selected assertion is presented 16
  times in each representation. The lossless compiler already checked the
  assertion IDs with multiplicity. The EOS-delimited loader applies every
  serialized target and records its exact completion cursor.
- **Matched compute.** Compare against the same 16-pass baseline. Make a
  separate seed-101 timing run for each representation and choose the whole
  number of factorized passes nearest to the baseline's recorded optimizer
  update time. The match is accepted when the median paired
  factorized-to-triples update-time ratio lies within 15% of one. Preparation,
  checkpoint writes and evaluation are outside the update timer.

Use contiguous EOS groups targeting 256 tokens per update, 64-token rows, four
rows per microbatch, and a constant 0.002 learning rate. Group sizes can differ
across representations. Each development panel supplies context for
unseen families. Score both panels on each model to compare same-domain and
cross-domain context performance. The panels use exact four-choice answers.
They do not score knowledge of unprovided facts. Keep the final split held
back. Tiny per-family panels provide a pilot measure with limited independence.

## Verify full passes and calibrate compute

Set `PREP` to the work directory from the parent recipe and `RECIPE` to this
directory. Start a fresh run directory. Use Lab with `data budget` support for
EOS groups. Use two CPU threads and run the calibration jobs serially.

```bash
set -euo pipefail
WORK="${WORK:-$HOME/.local/share/klab/real-domain-exposure}"
mkdir -p "$WORK"
cd "$WORK"
export KLAB_WORK_DIR="$WORK/state" OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1
mkdir -p receipts calibration
for domain in astronomy software; do
  val_docs=$(jq -er '.partitions.validation.sequences' "$PREP/receipts/$domain-triples.json")
  for arm in triples factorized; do
    name="$domain-$arm"
    klab config derive "$PREP/$name-run.yaml" \
      --set "name=\"$domain-relation-exposure\"" --set seed=101 \
      --set 'training.matched_stories={"layout":"contiguous","targets_per_update":256}' \
      --set optimizer.warmup_steps=0 --set optimizer.peak=0.002 --set optimizer.floor=0.002 \
      --set "logging.root_dir=\"$WORK/calibration\"" --set logging.every_steps=256 \
      --set "evaluation.text_documents=$val_docs" --set evaluation.every_steps=4096 \
      --set checkpoint.every_steps=4096 --output "$name-unbudgeted.yaml" \
      > "receipts/$name-derive.json"
    prepared=$(klab data prepare "$name-unbudgeted.yaml" \
      2> "receipts/$name-prepare.log" | tail -n 1)
    printf '%s\n' "$prepared" > "receipts/$name-prepared.txt"
    klab data budget --prepared-root "$prepared" --config "$name-unbudgeted.yaml" \
      --passes 16 --no-require-full --output "$name-equal-exposure.yaml" \
      --json > "receipts/$name-equal-exposure.json"
    rows=$(jq -er '.partitions.train.sequences' "$PREP/receipts/$name.json")
    tokens=$(jq -er --arg arm "$arm" '.representations[] |
      select(.options.target == $arm) | .partitions.train.tokens' "$PREP/receipts/$domain-compare.json")
    jq -e --argjson rows "$rows" --argjson tokens "$tokens" '
      .coverage.splits.train as $train |
      $train.preparation.retained_documents == $rows and $train.preparation.skipped_documents == 0
      and $train.preparation.truncated_documents == 0
      and $train.matched_groups.documents_per_pass == $rows
      and $train.matched_groups.supervised_targets == $tokens
      and .max_tokens == .passes * $tokens
    ' "receipts/$name-equal-exposure.json" >/dev/null
    klab train "$name-equal-exposure.yaml" --run-id "$name" --require-prepared \
      > "receipts/$name-calibration.out" 2> "receipts/$name-calibration.log"
    run="$WORK/calibration/$name"
    generation=$(jq -er .relative_path "$run/checkpoints/latest.json")
    klab checkpoint verify "$run/checkpoints/$generation" > "receipts/$name-calibration-verification.txt"
    jq -e --arg name "$name" '{
      name:$name, step, tokens_seen, passes:.exposure.cursor.completed_loader_passes,
      update_seconds:.exposure.timing.optimizer_update_seconds, sha256
    } | select(.passes == 16 and .update_seconds > 0)' \
      "$run/checkpoints/$generation/manifest.json" > "receipts/$name-calibration.json"
  done
done
```

## Run the paired sweeps and score both development panels

The two points reuse the identical triples baseline for each seed. Compute
calibration chooses the factorized pass count before evaluating any outcome.
The ranking declarations carry the objective evaluation for this pilot.
The generic prose probe battery is disabled.

```bash
for domain in astronomy software; do
  base="$domain-triples"
  candidate="$domain-factorized"
  passes=$(jq -ers '
    (16 * .[0].update_seconds / .[1].update_seconds) | round |
    if . >= 1 and . <= 64 then . else error("compute match exceeds the pilot pass bound") end
  ' "receipts/$base-calibration.json" "receipts/$candidate-calibration.json")
  klab data budget --prepared-root "$(cat "receipts/$candidate-prepared.txt")" \
    --config "$candidate-unbudgeted.yaml" --passes "$passes" --no-require-full \
    --output "receipts/$candidate-matched-compute.yaml" --json > "receipts/$candidate-matched-compute.json"
  for budget in equal-exposure matched-compute; do
    configuration="$candidate-$budget.yaml"
    if [[ "$budget" == matched-compute ]]; then configuration="receipts/$configuration"; fi
    klab config validate "$configuration" --kind run --json \
      > "receipts/$candidate-$budget-config.json"
  done
  jq -n --arg baseline "$WORK/$base-equal-exposure.yaml" \
    --slurpfile whole "receipts/$candidate-equal-exposure-config.json" \
    --slurpfile compute "receipts/$candidate-matched-compute-config.json" '
    def point: {"dataset.revision":.dataset.revision,"dataset.train_path":.dataset.train_path,
      "dataset.train_max_documents":.dataset.train_max_documents,"training.max_tokens":.training.max_tokens,
      "training.max_steps":.training.max_steps};
    {baseline:$baseline, question:"How does factorization change development performance at equal assertion exposure or matched optimizer update time?",
      points:([$whole[0].config,$compute[0].config] | map(point) | unique),
      seeds:[11,23,37], config:"no-probes"}' > "$domain-sweep.json"
  klab sweep "$domain-sweep.json" --backend cpu --json > "receipts/$domain-sweep.json"
done
```

For each distinct run ID in the sweep records, score the terminal checkpoint
selected by the try. Use both development panels and keep their scores
separate. They contain 8 astronomy questions over two families and 12 software
questions over three families, with the correct option positions balanced
within each family. The supplied facts are development assertions from the
pinned indexes.

```bash
mkdir -p receipts/rankings
for domain in astronomy software; do
  jq -er '.tries[].record' "receipts/$domain-sweep.json" | while IFS= read -r trial; do
    jq -r '.arms[] | [.run_id,.checkpoint] | @tsv' "$trial"
  done | LC_ALL=C sort -u | while IFS=$'\t' read -r run_id generation; do
    for task in astronomy software; do
      klab eval "$run_id" --runs-dir "$KLAB_WORK_DIR/lab/runs" \
        --checkpoint "$generation" --ranking "$RECIPE/evaluation/$task-development.json" \
        > "receipts/rankings/$run_id-$task.json"
    done
  done
done
```

The terminal checkpoint also records the number of completed loader passes
and cumulative optimizer update seconds. Use the paired median timing ratio
to check the prospective compute match. Compare held-out triple loss within
each domain. Read the two context scores independently since the panels and
tokenizers differ.

## CPU result

The [record](results/2026-11-27.json) includes 18 completed runs, 12 paired
comparisons, and two development panels scored at every terminal checkpoint.
Each CPU model had 102,720 parameters. The sealed checkpoint cursor confirmed
the full planned number of passes in every arm. The unbudgeted preparations
reused all four existing prepared arrays.

| Domain and budget | Factorized passes | Factorized targets | Update time ratio | Held-out loss delta, nats |
| --- | ---: | ---: | ---: | ---: |
| Astronomy, equal exposure | 16 | 12,464 | 0.73 | +0.304 ± 0.097 |
| Astronomy, matched compute | 23 | 17,917 | 1.05 | +0.296 ± 0.041 |
| Software, equal exposure | 16 | 52,352 | 0.59 | −0.010 ± 0.068 |
| Software, matched compute | 27 | 88,344 | 0.99 | +0.591 ± 0.056 |

Both baselines used 16 passes, with 16,688 astronomy targets and 80,432
software targets. Ratios are the median paired factorized-to-triples optimizer
update time. Loss deltas are paired means and standard errors over three
seeds. Loss uses the same held-out triple encoding for both arms. The results
measure how well each representation predicts previously unseen triples in
that encoding.

Astronomy models scored 25% on the astronomy context panel in every arm.
Software models scored 25% as triples and 19.4% or 27.8% as factorization
under equal exposure or matched compute. Across domains, factorization
brought software models from 16.7% to 25% on the astronomy questions,
while astronomy models moved from 30.6% to 25% on the software questions.
Uniform four-choice accuracy is 25%. These small panels show no consistent
transfer gain, and the final split stayed held back.
