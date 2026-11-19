# Blinded statistics for the 32k ROCm study (GR32K-S1)

This is a new study, based on Workshop commit 9939e29ba594bebe646ef983fbc605dc80a9699c.
Written 2026-11-18 at 15:59 UTC before inspecting treatment learning outcomes.
The numeric horizon, margin and elapsed cap remain unbound until their blind
receipts qualify. It adds to the [campaign runbook](CAMPAIGN-RUNBOOK.md) and
[campaign budget](CAMPAIGN-PROPOSAL.json) without changing the earlier results,
training declarations, admissions, or resource limits. The campaign has owner
approval; the device claim, source, timing, and resource gates still apply.
This document allocates no resources. Record its content hash in the campaign
before runs and bind the predeclared numerical fields below before reading
new treatment learning results.

## Design and staged freeze

C0 is the native dense, untied head. C4 starts at A=W0 and B=I, with both
factors trainable. The C4 contrast is **C4 minus C0** for every loss difference
in this protocol: negative favors C4. Use the same validated start function,
sampling order, mask, batch schedule, optimizer, ROCm BF16/chunk path, and
workstation policy. The frozen-identity head is a correctness gate, not an
efficacy arm. A missing valid same-start proof is an admission failure, not
a null result.

| Phase | Seeds and contrast | Use |
| --- | --- | --- |
| Shape/cost calibration | 13, C0 and C4, 40 updates each | Runtime and functional gates only. No learning effect or power claim. |
| Baseline-only precision | C0 seed 13 twice, independently launched | Measure one same-seed terminal repeat gap. Preserve a and b in planned launch order. Not counted as fresh efficacy seeds. |
| Screen | 17, paired C0 and C4 | Feasibility and descriptive effects. No t interval, retuning, horizon reselection, or promotion on a favorable curve. |
| Fresh confirmation | 101, 211, 307, each paired C0 and C4 | One planned fixed-token comparison and a separately labeled practical time endpoint. No substitutions, expanded n, or pooling prior seeds. |

Bind the same T for both arms, repeats, screen, and all fresh pairs before
reading any C4 learning results. Select 2,961 steps (388,104,192 committed
training targets) if the calibrated resource gate passes. The named
512-update post-warmup pilot (67,108,864 targets) is eligible only if explicitly
accepted as the alternative and recalculated to fit. Otherwise stop and report
the shortfall. Never shorten the model's 2,961-step LR schedule; use a native
absolute stop. A 512-step result describes that pilot, not a one-pass result.
The calibration has no comparable efficacy horizon. Full-horizon eval ticks
are 0, 370, 740, 1110, 1480, 1850, 2220, 2590, 2960, 2961; primary token
endpoint is 2961. The pilot ticks are 0, 256, 512; primary endpoint is 512.
Step 64 in the warmup is not a pilot endpoint. Intermediate curves and
milestones are descriptive.

The analyst setting thresholds may see C4's timing, resource and integrity
checks, including pass/refusal at the validated initial function. Keep C4
numeric development learning curves and outcome-bearing diagnostic plots
sealed until the numerical freeze is recorded. Do not hide safety, nonfinite
or integrity conditions. Bind the selected horizon, input identities, phase
and arm order, clock and cue definitions, and operational ceilings in a
timestamped quote receipt. Then enter the two eligible C0 repeat observations
and freeze the materiality margin and common measured-time cap below in a
second immutable receipt, still before inspecting C4 learning. Record who
had access and when; if blinding failed, mark the affected analysis
exploratory, not pre-outcome confirmation.

The screen has a path to confirmation even if the effect is small or adverse:
the planned contrast is fixed and the reserve tests a negative as well as
a positive. A failed gate, missing comparability, or insufficient resources
can block it. Record the obstruction and preserve already completed pairs.
Do not spend the fresh reserve on a different setting, seed, or metric.

## Adaptive quote: uses time and resource observations only

Measure both real 32k paths. The first 8 updates are startup; use all 32
post-startup update times (updates 9 through 40). For arm i let t_i be the
greater of nearest-rank p90 (29th of 32) and the slowest of four consecutive
8-update means, with the clocks and excluded phases listed. Keep the cold
setup time and any first-eight excess above T*t_i's per-update allowance
separate to avoid counting the same update twice. Charge actual startup,
both calibration evaluations, every planned native save, and all mandatory
checks that take device time. Where native timestamps show overlap, budget
unique elapsed intervals once; do not add overlapping phase clocks and call
the sum measured elapsed. If critical timings are absent, the calibration
has not earned a numerical quote.

Use the runbook quote Q_i(T): round up to the next 300 seconds after applying
1.25 to the sum of charged setup/startup, T*t_i, planned eval time, planned
save time, and charged checks. Use the slower observed compatible eval/save
service time rather than declaring the startup delay typical of all later
operations. Count all 10 full-horizon ticks, or all 3 pilot ticks, including
initial and final measurements. Record the native save count used and
transient protected generations. Keep BPB or sparse standalone probes out of
the efficacy endpoint; any elected measurement has its own charged slot.
Do not treat the 4k ROCm qualifier or old Intel times as a 32k quote.

The initial bound is actual calibration/claim time already used plus
2*Q0 for the baseline repeats, Q0+Q4 for the screen, 3*(Q0+Q4) for the six fresh
arms, and 3,240 seconds (0.9 h) for recovery/shutdown. Stamp real UTC deadlines.
At each phase transition substitute elapsed claim time spent for completed
quotes and keep all unspent required reservations. Check the 18-hour device
claim, 30-hour overall elapsed time, two-hour per-arm cap, 64 GiB new storage,
and invocation/disposable-update caps from the proposal. Charge wait and
cleanup under claim. Do not sum per-arm and whole-claim clocks twice, reset
spent time, add a retry, or convert unspent confirmation into another screen.
If the full plan becomes unaffordable after a horizon is bound, report the
shortfall; do not switch horizon on outcome information or silently compare
partial arms.

## Primary scientific endpoint: fixed committed training targets

The endpoint for seed s is d_s = dev_CE(C4,s,T) - dev_CE(C0,s,T) in nats per valid
development target. Keep both signed arm values, their checkpoint identities,
step and committed valid target counts. Require the exact same terminal
training target count and registered evaluation slice, with no extra
optimization on either arm. Compare raw CE, not perplexity, training
cross-entropy, an exponential average, or CE at an earlier step substituted
for a missing terminal measurement. Exp(d_s) is the paired perplexity ratio.

### Minimum practically material effect

Use three quantities before any new C4 learning result is exposed:

1. **Intended utility.** A change smaller than a 1% multiplicative perplexity
   difference does not by itself justify preferring a parameterization with
   extra optimizer state and potentially different training costs. Its
   symmetric log margin is ln(1.01) nats/target.
2. **Historical scale.** Use one quarter of the [old full-width penalty](results/historical-full-width.json):
   H = 0.04340055646995703 nats/target, old random factorization minus dense on
   Intel. A quarter (about 0.01085014 nats/target) is a minimum worth pursuing
   relative to that practical question, not a predicted AMD effect or a
   measured C4 recovery. H's historical between-seed variability is separate.
3. **Observed endpoint repeat gap.** For the two eligible C0 seed-13 terminal
   values a and b at the locked T, report the arm scores and signed r=b-a.
   Use R=abs(r) as the observed one-pair jitter, and 2R as a conservative
   resolution guard. This is not a variance, a prediction bound, or evidence
   of equivalence. Never substitute the 40-update baseline, the screen, or
   historical between-seed variation for this paired C0 repeat.

Freeze delta = round-up-to-0.001(max(ln(1.01), H/4, 2R)) nats/target.
For compatible repeats with 2R no larger than H/4, the rule gives 0.011,
as a rule consequence, not a measured margin. Use unrounded receipt losses
and record which term binds. If R is large, disclose by how much the guard
exceeds the intended-utility threshold; increasing delta does not improve
precision. A missing/incompatible repeat leaves delta unbound; mark the
materiality question unavailable while honoring the existing budget/gates.
The same formula in a pilot remains only a pilot margin. No post-outcome
search for a smaller margin.

## Primary practical endpoint: CE as of one common elapsed cap

The resource question is the available development CE at the same capped
**monitored arm elapsed time**. For each arm, capture a start monotonic
timestamp and UTC correlation under the native physical claim, at the
per-arm owned monitor/runner boundary before arm-specific setup or launch.
Use the same boundary for all arms. Include per-arm authorization/load,
input staging required by that arm, compilation if ever within the fixed
path, warmup, optimization, validation, checkpoint/report waits and owned
recovery before each score becomes available. Shared offline acquisition,
shared one-time preparation, inter-arm scheduling and time between arms
are not spent progressing either arm; report separately and charge them to
the applicable campaign clocks. This is elapsed time under ownership, not
GPU kernel busy time. Record optimizer-update-only time and native trainer
elapsed separately as diagnostic clocks. Neither can replace this endpoint.

Join each native validation phase's monotonic COMPLETE/finished timestamp
to the native validation_completed result by run, invocation, logical
evaluation occurrence, committed step and committed targets. Use the actual
recorded completion point (result measured, not necessarily durably saved).
Keep corresponding UTC, source hashes, native event/record identities, and
chronological checkpoint publication or absence. Reject ambiguity, clock
resets without a receipt-proven bridge, non-monotone sequences, duplicate
steps with conflicting results, and unrelated standalone rescoring. Join
only same-host same-boot monotonic time and record the launch/claim identity.
The current monitor completion reports elapsed duration, and process
create_time is wall clock; the stock MonitorLaunch need not carry an absolute
monotonic anchor. Confirm the admitted runner or native monitor emits the
anchor and release records **during calibration**. If not, add tested native
timing support before efficacy where possible; do not fabricate it from
trainer wall_time (which starts after startup) or backward from UTC/mtime.
Missing anchors or joins mean this endpoint is unavailable for that arm;
they do not invalidate a separately verified token endpoint.

Freeze a single numeric C for the selected T using only the two baseline
repeat terminal evaluation completion times E_a and E_b on that joined
clock, and the bracketed official per-arm quotes:

    C = min(E_a, E_b, Q0(T), Q4(T), 7200 seconds)

Use native precision (no rounded-down step/timestamp). This anchors the
cap to the earlier observed C0 terminal evaluation, instead of selecting
the time of largest opportunistic C4 separation. If the baseline timing
join is absent, the practical endpoint remains missing; no replacement
cap based on treatment outcomes. C is an analysis cutoff; it is not a new
operational stop or permission to idle/spend beyond actual runs.

In each arm select the last comparable scheduled development evaluation
actually completed at elapsed time <= C. Use no future, interpolated or
carried-back score. If a valid terminal score was measured before C, it is
the last available score (record arm already complete and terminal slack;
do not charge fictitious continued device time). If only initial score
qualifies, show the as-of score as initial-only and omit that pair from the
fresh time-endpoint interval. If the arm failed before C, preserve and
report an eligible last score as a failed-arm observation, not a valid
confirmatory pair. If no eligible observation or archival time evidence is
available, censor with a reason. Report d_time,s = C4_asof(C) - C0_asof(C)
only for eligible pairs; also report score completion, target counts, step,
C minus completion (evaluation age), newest saved checkpoint step and
publication delay if actually measured, and whether an exact sibling
checkpoint exists for that score. Sparse development ticks can make CE
appear stale: steps 2960/2961 can lie close together, and pilot 256/512 is
much coarser. Do not substitute progress/cursor state for a measured CE or
call an old checkpoint an exact score binding.

Optional secondary time to a baseline quality: freeze in the same pre-reveal
receipt whether enabled, and if enabled set CE goal to max(a,b) from the
eligible C0 terminal values. Use the first observed eligible scheduled score
<= goal by C. Report the measurement bracket (previous observed above-goal
score time, observed hit time]; left-censor at first observed hit if there
is no prior measured failure. If not observed, right-censor at the last
verified measurement time and give C separately. A bracket is a detection
interval between measurements, not a guarantee of where a nonmonotonic
unobserved curve first crossed; never interpolate. Show clock source and
censoring, not a ratio of unmatched terminal times.

## Fresh paired analysis and attainable precision

Only the three complete, verified fresh seed pairs count for confirmatory
fixed-token inference. Preserve signed d_101, d_211, d_307, their mean,
sample SD (denominator n-1), SE=s_d/sqrt(3), and the two-sided 95% Student-t
interval mean +/- 4.302652729911275*SE (df=2). State the independent-seed and
approximately normal paired-difference assumption; three pairs cannot
diagnose distribution or give robust equivalence. The fixed-token decision
is: upper CI endpoint strictly below -delta = practically material C4
benefit; lower strictly above +delta = material harm; CI excluding zero
without clearing a margin = directional at observed precision, practical
effect unresolved. Otherwise inconclusive. Even an interval wholly inside
[-delta,+delta] is not a registered equivalence test. Make no null/equivalence
claim from nonsignificance, matched initial functions or jitter alone.
If any registered pair is missing, give available paired values with reasons,
not a rebranded smaller confirmatory analysis.

Show matched-elapsed per-seed differences in a separate table and the same
three-pair t calculation only if all three pairs have eligible joined clocks
and scores. Label this practical endpoint's interval separately, with
evaluation age and unmatched committed tokens; it is not pooled with the
fixed-token comparison and is not an additional corrected efficacy test.
Do not claim practical learning efficiency when token and time data disagree
or useful time comparisons are missing. C0 repeats, calibration, old Intel
pairs, bounded 4k results, exploratory seed 17, intermediate horizons,
projection and optional quality-crossing comparisons never enter the paired
inference. Treat repeated evaluations on one run as repeated measurements,
not independent units; neither the dev targets nor checkpoint count is n.

Precision warning: the n=3 half-width is 2.48414 times the **new** paired SD.
For hypothetical paired SD of 0.003, 0.006 or 0.010 nats/target, half-widths
are about 0.00745, 0.01491 or 0.02484. The historical old-factor SD (~0.00556)
would imply about 0.01382 half-width if it applied here; no reason to assume
that. To clear a practical margin, the observed mean must exceed delta plus
the actual half-width in the claimed direction. These are sensitivity
calculations, not power or a forecast. Report realized precision or its
absence; two same-seed repeats cannot estimate between-seed precision.

## Data, leakage and compact native analysis handoff

Before scoring, bind published source revision and all five raw shard
digests, lock/dedup rules, document-ID and overlap checks, tokenizer and
origin bytes, prepared split digests, packed counts, supervision policy and
the actual development slice ordering. Published cleaned counts are
1,792,647 train and 21,990 development stories, with 388,198,157 and
4,647,305 prepared tokens; counts alone cannot authenticate the bytes.
Use **byte-identical published assets** only if authoritative original
digests match in full. Otherwise label the locked and verified
**exact-settings reconstruction with newly bound data digests**; do not
silently claim historical array equivalence from hash prefixes. AMD/SDPA
eager/chunk adaptations remain separate even if data bytes agree. Overlap,
target-mask, CE path, replay/dedup, and manifest mismatches must be resolved
before classifying pairs. The original validation split informed earlier
work and is development, not untouched test. Fresh seeds add replication,
not a new evaluation population. An untouched independent test is not
established or authorized as part of this study; do not introduce one
post-hoc.

The future neutral analyzer needs only compact native manifests/observations
and indices, not text, token IDs, tensors, full stdout, or an extra scoring
run. Have the native collector export the following (original evidence stays
in the authorized run store; published artifacts use relative identifiers):

- Freeze records: amendment/checkpointed declaration hashes, selected T,
  quote inputs, actual cap C, delta, timestamp, planned arms and counter
  ceilings, score visibility, and data/split/CE-matching identities. Hash the
  native-data derivations and each normalized compact export separately.
- Attempt registry: planned index/phase, phase/seed/arm and run/attempt IDs,
  source/git/runtime/config/dataset/evaluator and start/draw-order IDs, all
  admission, timing, terminal, abort and verified release receipts. Include
  blocked, failed, censored, never-launched and nonfinite outcomes. Record
  partial committed labels and time, exit state and reason, device/host/disk
  peaks, raw clock scope, external monotonic arm start and terminal/release.
  A planned stop receipt differs from failure even if the native run's state
  string says interrupted. A parse failure is explicit missingness, never
  a deleted row.
- Evaluation index: for each scheduled tick keep exact step, committed
  training targets, protocol/split/order/mask, dev CE and count, eval end
  monotonic/UTC and native metric payload hash. Record nll_sum when native
  provides it. Default native validation_completed often stores only
  loss and count; if count is verified exact 2^20 (64*32*512 unmasked
  labels) and CE was a finite normal binary64 sum divided by that count,
  binary power-of-two rescaling can recover the numerator from the
  round-tripped loss. Label it recovered, not separately logged. For
  other counts label CE*count derived or keep numerator missing; exact
  numerator requirements need planned native support rather than a second
  score. All paired arms must agree on exact sampled targets/valid count.
  Store checkpoint IDs and publish clocks only when a verified generation
  binds the event. Evaluation and save cadences differ; unsaved milestones
  can be event-bound, never falsely checkpoint-bound.
- Neutral calculation: verify hashes, exact arm factor and frozen phases;
  normalize rows once, audit time/entity joins and refusals without selecting
  on magnitudes; take the exact T rows or cap-eligible last rows using the
  registered rules; build signed paired rows and registered intervals only
  for eligible fresh sets. Report baseline repeat gap, each arm score and
  uncertainty, with explicit reasons for missing values. Retain separate
  screen and confirmation outputs, along with precision sensitivities and
  any protocol deviations made before or after reveal.

Specify a native neutral analyzer or report extension in Model Lab if the
existing commands do not expose this record/clock join; add tests with small
synthetic compact fixtures, including a missed cap, duplicate/conflicting
tick, a missing fresh pair and C4-minus-C0 sign. Workshop stores this protocol
and small receipts only; do not add a helper script or rerun models for the
analysis. Match native open/close claim timestamps to attempted work and
verify no descendants remain before declaring accounting complete.
