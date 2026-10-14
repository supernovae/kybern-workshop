# Executed command record

These are historical commands reconstructed from retained native monitor launch records.
`CPU_PYTHON`, `A`, `B` and `WORK` substitute the original absolute local paths.
They are audit records, not a script to rerun against an existing store.
Provisioning, baseline capture and analysis overhead are excluded from child-command monitor timings.
The root guide recommends native monitoring without strace; failed traced commands remain visible here.

All monitor policies use the committed 600-second / 4-GiB / 1-GiB limits except
`remaining-attempt-monitor.json`, a local copy with `max_wall_seconds: 328`.
The successful continuation used a 300-second Controller wait; its earlier traced continuation used 420.
The passive sampler ran separately, launching no lab commands. Its durations are sampled observations.

## preparation-1

```sh
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor-baseline "$WORK" \
  --output "$WORK/preparation-baseline.json" --json
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor \
  --policy "$A/examples/synthetic-cpu/monitor.json" \
  --baseline "$WORK/preparation-baseline.json" \
  --log-dir "$WORK/monitor/preparation-1" --workspace "$WORK" -- \
  "$CPU_PYTHON" -m sparselab experiment recipe preparation apply "$A/examples/synthetic-cpu/preparation.json" --bindings "$WORK/preparation-bindings.json" --admission "$WORK/preparation-admission-a.json" --work-dir "$WORK" --json \
  > "$WORK/preparation-monitor-1.json" 2> "$WORK/preparation-monitor-1.stderr"
```

## preparation-replay

```sh
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor-baseline "$WORK" \
  --output "$WORK/preparation-replay-baseline.json" --json
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor \
  --policy "$A/examples/synthetic-cpu/monitor.json" \
  --baseline "$WORK/preparation-replay-baseline.json" \
  --log-dir "$WORK/monitor/preparation-replay" --workspace "$WORK" -- \
  "$CPU_PYTHON" -m sparselab experiment recipe preparation resume "$A/examples/synthetic-cpu/preparation.json" --bindings "$WORK/preparation-bindings.json" --admission "$WORK/preparation-admission-a.json" --work-dir "$WORK" --json \
  > "$WORK/preparation-replay-monitor.json" 2> "$WORK/preparation-replay-monitor.stderr"
```

## workflow-resolve

```sh
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor-baseline "$WORK" \
  --output "$WORK/resolve-baseline.json" --json
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor \
  --policy "$B/examples/synthetic-cpu/monitor.json" \
  --baseline "$WORK/resolve-baseline.json" \
  --log-dir "$WORK/monitor/workflow-resolve" --workspace "$WORK" -- \
  "$CPU_PYTHON" -m sparselab experiment recipe workflow resolve "$B/examples/synthetic-cpu/workflow.json" --bindings "$WORK/workflow-bindings.json" --json \
  > "$WORK/workflow-resolve-monitor.json" 2> "$WORK/workflow-resolve-monitor.stderr"
```

## workflow-plan

```sh
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor-baseline "$WORK" \
  --output "$WORK/workflow-plan-baseline.json" --json
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor \
  --policy "$B/examples/synthetic-cpu/monitor.json" \
  --baseline "$WORK/workflow-plan-baseline.json" \
  --log-dir "$WORK/monitor/workflow-plan" --workspace "$WORK" -- \
  "$CPU_PYTHON" -m sparselab experiment recipe workflow apply "$B/examples/synthetic-cpu/workflow.json" --bindings "$WORK/workflow-bindings.json" --admission "$WORK/workflow-admission.json" --work-dir "$WORK" --json \
  > "$WORK/workflow-plan-monitor.json" 2> "$WORK/workflow-plan-monitor.stderr"
```

## workflow-approve

```sh
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor-baseline "$WORK" \
  --output "$WORK/workflow-approve-baseline.json" --json
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor \
  --policy "$B/examples/synthetic-cpu/monitor.json" \
  --baseline "$WORK/workflow-approve-baseline.json" \
  --log-dir "$WORK/monitor/workflow-approve" --workspace "$WORK" -- \
  "$CPU_PYTHON" -m sparselab experiment recipe workflow approve "$B/examples/synthetic-cpu/workflow.json" approve-model --bindings "$WORK/workflow-bindings.json" --admission "$WORK/workflow-admission.json" --work-dir "$WORK" --note 'Owner approved one bounded synthetic CPU attempt at reviewed B e8250556412bc8535c029d80af3fa735b82c1ffa' --json \
  > "$WORK/workflow-approve-monitor.json" 2> "$WORK/workflow-approve-monitor.stderr"
```

## workflow-run

```sh
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor-baseline "$WORK" \
  --output "$WORK/workflow-run-baseline.json" --json
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor \
  --policy "$B/examples/synthetic-cpu/monitor.json" \
  --baseline "$WORK/workflow-run-baseline.json" \
  --log-dir "$WORK/monitor/workflow-run" --workspace "$WORK" -- \
  strace -f -ttt -s 300 -e trace=process -o "$WORK/workflow-run-process.trace" "$CPU_PYTHON" -m sparselab experiment recipe workflow apply "$B/examples/synthetic-cpu/workflow.json" --bindings "$WORK/workflow-bindings.json" --admission "$WORK/workflow-admission.json" --work-dir "$WORK" --execute-runs --max-wait-seconds 540 --json \
  > "$WORK/workflow-run-monitor.json" 2> "$WORK/workflow-run-monitor.stderr"
```

## workflow-run-resume

```sh
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor-baseline "$WORK" \
  --output "$WORK/workflow-run-resume-baseline.json" --json
SPARSELAB_WORKER_LEASE_DIR="$WORK/worker-leases" "$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor \
  --policy "$B/examples/synthetic-cpu/monitor.json" \
  --baseline "$WORK/workflow-run-resume-baseline.json" \
  --log-dir "$WORK/monitor/workflow-run-resume" --workspace "$WORK" -- \
  strace -f -ttt -s 300 -e trace=process -o "$WORK/workflow-run-resume-process.trace" "$CPU_PYTHON" -m sparselab experiment recipe workflow resume "$B/examples/synthetic-cpu/workflow.json" --bindings "$WORK/workflow-bindings.json" --admission "$WORK/workflow-admission.json" --work-dir "$WORK" --execute-runs --max-wait-seconds 420 --json \
  > "$WORK/workflow-run-resume-monitor.json" 2> "$WORK/workflow-run-resume-monitor.stderr"
```

## workflow-run-untraced

```sh
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor-baseline "$WORK" \
  --output "$WORK/workflow-run-untraced-baseline.json" --json
SPARSELAB_WORKER_LEASE_DIR="$WORK/worker-leases" "$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor \
  --policy "$WORK/remaining-attempt-monitor.json" \
  --baseline "$WORK/workflow-run-untraced-baseline.json" \
  --log-dir "$WORK/monitor/workflow-run-untraced" --workspace "$WORK" -- \
  "$CPU_PYTHON" -m sparselab experiment recipe workflow resume "$B/examples/synthetic-cpu/workflow.json" --bindings "$WORK/workflow-bindings.json" --admission "$WORK/workflow-admission.json" --work-dir "$WORK" --execute-runs --max-wait-seconds 300 --json \
  > "$WORK/workflow-run-untraced-monitor.json" 2> "$WORK/workflow-run-untraced-monitor.stderr"
```

## workflow-report

```sh
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor-baseline "$WORK" \
  --output "$WORK/workflow-report-baseline.json" --json
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor \
  --policy "$B/examples/synthetic-cpu/monitor.json" \
  --baseline "$WORK/workflow-report-baseline.json" \
  --log-dir "$WORK/monitor/workflow-report" --workspace "$WORK" -- \
  "$CPU_PYTHON" -m sparselab experiment recipe workflow report "$WORK/campaigns/workshop-synthetic-cpu/ac2b8dcf392783f4013ee32314b4d3d1aac8fa34a0159135ba91f180d72ae6fe/experiments/lock-plan-workshop-synthetic-cpu/locks/9b460b8eed339211362fb6fbdfd795e4c43d93af4c173f76b49a9149ffb7c240.json" --workspace "$WORK/campaigns/workshop-synthetic-cpu/ac2b8dcf392783f4013ee32314b4d3d1aac8fa34a0159135ba91f180d72ae6fe/experiments/lock-plan-workshop-synthetic-cpu" --index "$WORK/campaigns/workshop-synthetic-cpu/ac2b8dcf392783f4013ee32314b4d3d1aac8fa34a0159135ba91f180d72ae6fe/experiments/lock-plan-workshop-synthetic-cpu/evidence/68a13e4526d842148a00374318982896185b0d2063da3787d55cd534ac9d1888.json" --output "$WORK/report.json" --json \
  > "$WORK/workflow-report-monitor.json" 2> "$WORK/workflow-report-monitor.stderr"
```

## workflow-completed-replay

```sh
"$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor-baseline "$WORK" \
  --output "$WORK/workflow-completed-replay-baseline.json" --json
SPARSELAB_WORKER_LEASE_DIR="$WORK/worker-leases" "$CPU_PYTHON" -m sparselab --work-dir "$WORK" monitor \
  --policy "$B/examples/synthetic-cpu/monitor.json" \
  --baseline "$WORK/workflow-completed-replay-baseline.json" \
  --log-dir "$WORK/monitor/workflow-completed-replay" --workspace "$WORK" -- \
  "$CPU_PYTHON" -m sparselab experiment recipe workflow resume "$B/examples/synthetic-cpu/workflow.json" --bindings "$WORK/workflow-bindings.json" --admission "$WORK/workflow-admission.json" --work-dir "$WORK" --json \
  > "$WORK/workflow-completed-replay-monitor.json" 2> "$WORK/workflow-completed-replay-monitor.stderr"
```

The first pre-preparation launch omitted global `--work-dir` and the growth baseline.
It exited before child launch because the default work root was read-only; its empty
stdout and failure note are retained privately. It has no native attempt or timing receipt.
Both stopped traced invocations received SIGINT on their owned workflow process; native
and independent cleanup checks are recorded in [cleanup-excerpt.json](cleanup-excerpt.json).
No new attempt was created by either continuation.
