# One synthetic CPU workflow, including its failed invocations

The admitted workflow completed one model attempt, normal ingestion, one diagnostic
heldout_lm suite, a verified report and completed replay without a second attempt.
This establishes wiring for this tiny synthetic example, not model quality.
No corpus/model downloads, GPU/provider resources or paid compute were used.

## Exact revisions

| Identity | Revision |
| --- | --- |
| Lab | `b155cdcc1462cfbcbd5f0cf5261eb8aa197ef9dc` |
| Reviewed lab PR128 head | `45230f446bde5d88b26857630c9b7a53eaaf602e` |
| Workshop bootstrap | `2b9bace19ab5d671acdf6cafcf90563411831bf7` |
| Preparation A | `28a01d69442c8b08e5ba78e4561ff4f69443e1e5` |
| Measured workflow B | `e8250556412bc8535c029d80af3fa735b82c1ffa` |
| Workshop PR1 merge | `e4d0fb16cde8c00a719fdee21e51ddd148f64991` |

Admission selected B, not the later merge commit. A and B were retained as clean
checkouts with their exact local bindings/admissions. Empty Git porcelain output
and the unchanged native installed-source identity were checked after execution.
No lab or website source was changed. This results branch does not change any
scientific declaration, preparation identity, historical admission or receipt.

Native source identity (`package-path-sha256-v2`, 372 files):
`1f947cce513952bef88f9397e12bb3661efe97ece604cab04330f197e0a44a26`.
Lab lock file SHA-256:
`2058fe5c126df074879648018c36288386190446b94b147b811671185958ac86`.
Runtime: CPython 3.14.8, PyTorch 2.14.0+cpu, tokenizers 0.22.2, NumPy 2.5.3,
datasets 4.8.5, PyArrow 25.0.1, Pydantic 2.13.5, PyYAML 6.0.3,
huggingface-hub 0.36.2 and psutil 7.2.2, provisioned from the lab's locked CPU extra.
Environment installation precedes these measurements and is not included in them.

## What ran

Seeds: integer 7 for run and synthetic data. Dense model: one layer, hidden 16,
FFN 32, two heads, context 32, vocabulary 260; 6,768 parameters. CPU FP32,
sequence 16, microbatch 1, accumulation 1, deterministic training. AdamW peak
0.0003, floor 0.00003, optimizer warmup 0; native smoke/warmup remain 2/5.
Dataset caps: eight/four train/validation documents and 256/128 tokens.
Tokenizer training caps at eight documents. Caps are not observed document counts.

Compared with the lab contract fixture, dimensions, seeds and batch/staging
settings stayed the same, but vocabulary changed from 512 (264 in the preparation
fixture), token caps from 129/81, optimizer peak/floor from 0.003/0.0003 and warmup
from 2, evaluation max batches from 4, and main budget from 20 steps/640 targets.
This independently authored example is not exact fixture reproduction; its token
caps are larger despite smaller vocabulary and main/evaluation budgets.

| Work | Actual verified updates | Targets | Native update timing |
| --- | ---: | ---: | ---: |
| Smoke | 2 | 32 | 0.402239 s total |
| Warmup | 5 | 80 | 0.088141 s total |
| Main | 1 | 16 | 0.047268 s |

All eight Campaign stages completed: both artifact references, lock, CPU
acceptance, explicit approval, training, collection and evaluation. The CPU
acceptance stage in this no-profile path checked storage/runtime declarations;
precision probes occurred during later execution. Stage states are native states,
not invented per-stage process exit codes. Successful CLI commands exited zero.

Not executed: a second model attempt, heavyweight suites, generation, comparisons,
accelerator work, corpus acquisition, scientific promotion or full-state training
resume. The historical 149.486-second/1.50-GiB lab proof is not this measurement.

## Measurements and failures

| Monitored command | Status | Seconds | Peak tree RSS bytes | Added workspace bytes | Samples |
| --- | --- | ---: | ---: | ---: | ---: |
| Preparation | COMPLETE | 9.587894 | 437280768 | 73736 | 10 |
| Preparation replay | COMPLETE | 6.452063 | 430981120 | 23824 | 7 |
| Cold workflow resolution | COMPLETE | 6.515828 | 430206976 | 11540 | 7 |
| Plan/acceptance | COMPLETE | 14.273060 | 445087744 | 127667 | 13 |
| Explicit approval | COMPLETE | 8.426039 | 436744192 | 47329 | 9 |
| First traced invocation | MONITOR_ERROR after stop | 140.834523 | 1090207744 | 1015803 | 138 |
| Traced continuation | MONITOR_ERROR after stop | 121.038262 | 1172439040 | 655900 | 115 |
| Untraced continuation | COMPLETE | 291.320703 | 1984081920 | 3213741 | 275 |
| Verified report | COMPLETE | 9.558889 | 440287232 | 21702 | 10 |
| Completed replay | COMPLETE | 8.947403 | 444030976 | 56586 | 9 |

Each command used a persisted baseline and native operational monitor, with
600-second / 4-GiB tree-RSS / 1-GiB workspace-growth ceilings and one-second
sampling, five-second termination grace. These are sampled stop ceilings, not
instantaneous kernel quotas or expected performance. The final continuation's
wall ceiling was narrowed to 328 seconds (Controller wait 300) to keep cumulative
attempt commands below 600 seconds. It finished at 291.321 seconds; no resource
ceiling was reached. Tracing overhead is included in the failed measurements.

Attempt commands including both stops total **553.193487 seconds**. All workflow
commands total **594.398878 seconds**. Including preparation, its replay and cold
resolution, measured commands total **616.954663 seconds / 593 samples**. This
last total spans separately bounded operations; it is not a single attempt time.
Peak tree RSS was **1984081920 bytes**. Summed per-command growth was 5247828 bytes;
a separate scan recorded **5400089 bytes net growth**, including inter-command
logs/metadata, before the last small summary/cleanup records were written. These
are different accounting bases, not interchangeable totals or training time.

The initial monitor launch before preparation failed before spawning its child:
the default work directory was read-only. It has no native preparation attempt or
successful timing receipt. Its record and empty stdout were retained. Global
`--work-dir "$WORK"` and a persisted baseline corrected the invocation.

The first traced workflow invocation stayed queued because the default worker
lease directory was read-only. The supported per-command correction was
`SPARSELAB_WORKER_LEASE_DIR="$WORK/worker-leases"`. The next traced continuation
hit worker transport timeouts; two precision probe output pipes broke after the
worker was killed. It was stopped and diagnosed, then continued without strace,
using the same queued attempt. No tracing software was installed and no timeout
or runtime implementation was patched. Passive process sampling replaced tracing.

Both stopped monitor CLIs exited 1, retaining command return code 254 and
`owned shutdown unverified: invalid owned shutdown receipt`. Traced SIGINT exit
mapping disagreed with the owned receipt's -2. These records remain MONITOR_ERROR,
not relabeled success. Both owned receipts reported zero living descendants.
After each stop, every recorded PID was independently checked: no non-zombie
survivors. The two trace-identified orphan probe PIDs were separately checked
with `psutil.Process`; both raised `NoSuchProcess`. The final lab-process scan was
empty. See [cleanup evidence](cleanup-excerpt.json); PIDs and host details are omitted.

## Probe observations

Six precision probe processes were observed on the successful path, and native
qualification passed. Their sampled lifetimes were 3.984, 8.187, 6.064, 5.489,
12.720 and 5.968 seconds (42.414 seconds summed). Passive sampling targeted 100 ms;
maximum observed gap was 0.543 seconds. These are observed process lifetimes,
not exact start-to-exit, optimizer-only timings, or an exhaustive syscall trace.
They corroborate the six source-predicted validation sites; predictions alone
would not count as measured success. Each dense precision probe separately tests
one update of a 4-by-4 parameter, not a 16-target training update.

The failed traced continuation launched two precision probes, exiting 120 after
17.961 and 22.813 seconds. They did not produce successful native qualification;
optimizer completion inside those failed processes cannot be certified. Do not
add them to the six successful probes or claim zero optimizer work in them.
Nine read-only runtime-identity probes were observed across the attempt commands:
three in the first stop, two in the second, four in the successful continuation.
They are neither precision probes nor model updates. Completed replay sampled none.

## Immutable result and replay

The [native report](report.json) contains the exact attempt, manifest and checkpoint
identities and was copied byte-for-byte. Its file SHA-256 is
`95fb40744a653b3bde13af9dd078239ddb9b7d4357be0ac1fdc4e0f6aef2a4c8`.

- Attempt: `00b3938a-611f-4af8-bb4b-411e1b44e9d6`.
- Run: `1632259c-9aa4-45bc-965f-de87d7fadb2c`.
- Terminal attempt receipt: `1aeee4aaa985e214817819e339ab3a6b69d40e6ec133db7ac01962aa46d02d7f`.
- Terminal checkpoint: `010d3d137dd6943b2dc7317223d36fffd60ca1a3ded0680e86a62bf8f76ec81f`, generation `step_00000001_gen_000002`.
- Collected evidence index: `68a13e4526d842148a00374318982896185b0d2063da3787d55cd534ac9d1888`.
- Later evaluation index: `658de3edf804b4ab227c25df8a0692163006d15388db4003c25d5d0aefcd1a0c`.

The separate diagnostic evaluation completed one batch / 16 targets on that
terminal checkpoint: loss 5.441391468048096, perplexity 230.76305958852774.
Its result digest is `5eabd09ec684ed0272f63ca6ccb09b1dc0c64f5b91d465a892c29a56eb5c34e2`.
See the [evaluation excerpt](evaluation-excerpt.json). The report selects the
collect-stage snapshot made before this evaluation; it does not silently replace
that snapshot with the later suite index. The report also retains the native
training validation observations at steps zero and one.

Report readiness: `verified_snapshot`, execution coverage `complete`, scientific
result `not_assessed`, decision `no_automatic_promotion`. Checkpoint verification
is `weights_only`; full-state training resume is not established. Licensing,
redistribution and distributed weights availability remain unknown in the report
contract. These synthetic observations do not establish untouched held-out
separation, general model quality, a comparison win or across-seed uncertainty.

Completed replay used `resume` without `--execute-runs`. All eight stages remained
COMPLETE. Read-only before/after comparison showed exactly one unchanged Controller
attempt row, COMPLETE ingestion, and byte-identical Campaign stage receipts.
No additional attempt was created. See [replay evidence](replay-excerpt.json).

## Public evidence and reproduction

[Evidence index](evidence-index.json) hashes every distributed JSON file. Native
artifact/receipt/index/checkpoint digests retain their original semantics.
`original_byte_sha256` identifies retained unsanitized bytes; `sanitized_file_sha256`
identifies the published projection. They are not interchangeable. Excerpts are
not original signed/verified receipt bytes and cannot re-verify withheld payloads.
The native public report is the exception: it already omits local paths and is
copied unchanged. No checkpoints, bindings, admissions, raw traces, process IDs,
credentials or personal data are distributed here.

[Monitor excerpts](monitor-excerpts.json) retain exact sanitized child argv,
policy, baseline/source identities, exits, samples, resource measurements and
cleanup outcome. [Receipt excerpts](receipt-excerpts.json) retain all preparation
and workflow stage identities. [Summary](summary.json) includes precise timings,
probe samples, pilot identities, main metrics and preserved failure explanations.
[Executed commands](commands.md) reconstruct the outer monitor/baseline commands
with symbolic paths and retain all historical invocations, including the failures.

Use the project [reproduction guide](../../examples/synthetic-cpu/README.md) with ordinary Git clone and
pinned checkouts. Use the writable lease directory and native monitor, not strace.
Fresh bindings/admissions and payloads belong outside Git; a fresh preparation
requires its own committed workflow identities and review. This published result
is evidence of the measured A/B revisions, not an automatic grant to rerun work.
