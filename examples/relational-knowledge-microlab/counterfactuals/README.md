# Counterfactual transfer cases

Do the fixed-token Microlab models change their answers when a single request
amount crosses a known rule boundary? This development-only comparison uses
the 21 terminal checkpoints from the [seven-view CPU pilot](../README.md).
The previous question panel scored items individually. This one also scores
whether the same model answers both sides of each contrast correctly.

The 24 new families each have one two-tank world. Eight families each isolate
the action limit, the source minimum, or the destination capacity. Each
family yields an allowed and a blocked amount with the same state, rule and
direction. Lab's simulator supplies both outcomes. We ask whether the
request succeeds and how much remains in the source, presenting each as prose
and as a compact record. Each question has two choices and identical wording
and choice order in both contexts. Both contexts supply the rule. The original
final families remain held back.

## Generate the panel from audited cases

Set `RECIPE` to this directory and `RUNS` to the original pilot's run store.
Use Lab with paired ranking and a fresh work directory outside Git.

```bash
set -euo pipefail
WORK="${WORK:-$HOME/.local/share/klab/counterfactual-microlab}"
mkdir -p "$WORK"
cd "$WORK"
export KLAB_WORK_DIR="$WORK/state" OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1
mkdir -p receipts
klab corpus mechanisms simulate "$RECIPE/worlds.json" --workers 2 > receipts/worlds.json
key=$(jq -er .key receipts/worlds.json)
klab corpus mechanisms audit "$key" --samples 24 --seed 83 > receipts/oracle.json
klab corpus mechanisms compile "$key" "$RECIPE/compile.json" > receipts/compiled.json
source="$(jq -er .path receipts/compiled.json)/validation.jsonl"
jq -es '
  def approval($outcome):
    if ($outcome.violations|length) == 0 then "yes" else "no" end;
  def context($format; $rule; $event; $amount):
    ["A","B"] as $labels |
    $labels[$event.source] as $sender | $labels[1-$event.source] as $receiver |
    if $format == "prose" then
      "A holds \($event.before[0]) units (min \($rule.minimum[0]), cap \($rule.capacity[0])). " +
      "B holds \($event.before[1]) (min \($rule.minimum[1]), cap \($rule.capacity[1])). " +
      "Limit \($rule.request_limit). A request above the limit or outside tank bounds leaves both unchanged. " +
      "Request: move \($amount) from \($sender) to \($receiver)."
    else
      "Tanks A,B. State \($event.before). Min \($rule.minimum). Cap \($rule.capacity). Limit \($rule.request_limit). " +
      "Reject above limit or outside bounds. Keep state on rejection. Request \($sender)>\($receiver): \($amount)."
    end;
  [ .[] | .text | fromjson |
    .world as $world | .rule as $rule | .events[0] as $event |
    $event.actual as $left | $event.counterfactual as $right |
    ($left.violations + $right.violations) as $violations |
    if (.events|length)!=1 or ($violations|length)!=1 or approval($left)==approval($right)
       or $left.after[$event.source]==$right.after[$event.source]
    then error("expected a single-boundary contrast") else . end |
    ("How many units remain in tank " + ["A","B"][$event.source] + "? Answer:") as $state_question |
    ("prose","record") as $format |
    ("approval","state") as $task |
    (if $task=="approval" then
      {question:"Does the request succeed? Answer:",left:approval($left),right:approval($right)}
     else
      {question:$state_question,left:($left.after[$event.source]|tostring),
       right:($right.after[$event.source]|tostring)}
     end) as $answer |
    "\($world):\($format):\($task)" as $id |
    {pair:{id:$id,left:($id+":observed"),right:($id+":alternative"),question:$answer.question},
     items:[("observed","alternative") as $side |
       (if $side=="observed" then [$left.amount,$answer.left] else [$right.amount,$answer.right] end) as $case |
       {id:($id+":"+$side),category:("\($format)_\($task)_\($violations[0])"),
        prefix:(context($format;$rule;$event;$case[0])+"\n"+$answer.question),
        candidates:([$answer.left,$answer.right]|sort),answer:$case[1]}]}
  ] |
  if length != 96 then error("expected 96 contrast pairs") else . end |
  {schema_version:1,name:"transfer-context-contrasts",items:map(.items[]),pairs:map(.pair)}
' "$source" > receipts/panel.json
```

## Score the retained checkpoints

The prior result pins each terminal checkpoint digest. Compare the digest
returned by `klab eval` before aggregating any score. The paired margin
measures how far the model shifts toward each context's correct answer
relative to the other context's answer. Independent uniform binary choices
give 50% single-item and 25% joint accuracy. A fixed answer earns zero joint
credit even if half the items are correct.

```bash
mkdir -p receipts/ranking
jq -r '.runs[] | [.run_id,.try_id,.checkpoint_sha256] | @tsv' "$RECIPE/../results/2026-11-27.json" |
  while IFS=$'\t' read -r run trial digest; do
    generation=$(klab report "$trial" --lab-dir "$(dirname "$RUNS")" --json |
      jq -er --arg run "$run" --arg digest "$digest" '
        .arms[] | select(.run_id==$run and .checkpoint_sha256==$digest) | .checkpoint')
    klab eval "$run" --runs-dir "$RUNS" --checkpoint "$generation" \
      --ranking receipts/panel.json > "receipts/ranking/$run.json"
    jq -e --arg digest "$digest" '.identity.checkpoint_sha256 == $digest' \
      "receipts/ranking/$run.json" >/dev/null
  done
```

## Result on the fixed-token pilot

Lab scored all 21 terminal checkpoints on 192 items covering 96 pairs from
24 audited development families. Each cell averages three paired seeds.

| Training view | Item accuracy | Joint accuracy |
| --- | ---: | ---: |
| Prose | 50.0% | 0.0% |
| Triples | 50.2% | 0.3% |
| Walks | 50.7% | 1.4% |
| Hierarchy | 49.7% | 0.0% |
| Factorized | 50.2% | 0.3% |
| Procedural | 50.0% | 1.0% |
| Mixed | 50.0% | 0.0% |
| Independent uniform choice | 50.0% | 25.0% |

Near-chance item accuracy coexisted with very low pair accuracy. The
procedural and mixed arms rarely changed to the correct answer when the
request crossed a rule boundary. Mean answer margins were near zero across
all seven views. This is evidence from small models on one simulated rule
system, with the same 24 families reused across question types and formats.
The [run record](results/2026-11-27.json) keeps the audited artifact keys,
checkpoint digests, and scores by seed, presentation, question, and boundary.
