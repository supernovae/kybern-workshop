# Stage 2 at 16,384 tokens: YaRN against a larger RoPE base

Run notes for 26 November 2026. The question was which way of lengthening the
context to use for stage 2: YaRN RoPE scaling (`context-16k.yaml`) or a larger
RoPE base with no scaling (`long-context-abf.yaml`, base 1,000,000). Two short
arms were trained from the same pretraining checkpoint, the lower held-out loss
picked YaRN, and the full stage-2 budget was then spent on YaRN.

The first result was mixed: YaRN had the lower loss but could not retrieve a
fact from about 10,000 tokens back, and ten times more training did not change
that. On 27 November the comparison was repeated over three paired seeds with a
retrieval probe that varies where the fact sits, and a third arm at base 80,000
was added. That settled the choice: base 1,000,000 retrieves everywhere on
every seed for 0.7% more held-out loss. See
[Paired seeds and the retrieval surface](#paired-seeds-and-the-retrieval-surface).
The full stage 2 was then rerun at base 1,000,000 and finished on 28 November:
it retrieves across the window and its held-out loss is 0.25% above the YaRN
full run. See [Full run at base 1,000,000](#full-run-at-base-1000000).
The sections after it are the 26 November record, kept as written.

## Paired seeds and the retrieval surface

Seven more short arms were trained on 27 November with the same shortened
config, changing only the seed and the position encoding: YaRN, RoPE base
80,000 and RoPE base 1,000,000 at seeds 42, 43 and 44 (seed 42 already had
YaRN and base 1,000,000). All seven completed at step 382 without
interruption. The base 80,000 and seed variants were derived from the short
configs with `klab config derive --set attention.rope_base=80000.0` and
`--set seed=N`. Within a seed the arms see the same rows in the same order.

| Seed | YaRN | Base 80,000 | Base 1,000,000 | Tokens seen |
| --- | --- | --- | --- | --- |
| 42 | `devmind-lc16k-yarn-50m-r2` | `devmind-lc16k-abf80k-50m` | `devmind-lc16k-abf-50m` | 38,970,527 |
| 43 | `devmind-lc16k-yarn-50m-s43` | `devmind-lc16k-abf80k-50m-s43` | `devmind-lc16k-abf-50m-s43` | 39,504,331 |
| 44 | `devmind-lc16k-yarn-50m-s44` | `devmind-lc16k-abf80k-50m-s44` | `devmind-lc16k-abf-50m-s44` | 39,193,605 |

They were probed with the standard `klab probe TARGET --vs BASE --config full`
at bf16, suite version 7, using the two Lab changes in
[model-lab#720](https://github.com/supernovae/model-lab/pull/720): scoring at
the run's precision, and `long_needle` as a grid of input length by fact depth
with 12 held-out items per cell. Each raised-base arm was compared with the
YaRN arm of its seed. Values for seeds 42 / 43 / 44
([paired-seeds.csv](paired-seeds.csv), [retrieval-surface.csv](retrieval-surface.csv)):

| | YaRN | Base 80,000 | Base 1,000,000 |
| --- | --- | --- | --- |
| Held-out loss | 1.9967 / 1.9996 / 1.9987 | 1.9979 / 2.0002 / 2.0014 | 2.0112 / 2.0123 / 2.0140 |
| Loss against YaRN, mean | | +0.07% | +0.71% |
| Long needle, all cells | 0.913 / 0.913 / 0.900 | 0.942 / 0.925 / 0.900 | 1.000 / 1.000 / 1.000 |
| Needle at the start, 10,026 tokens | 0.17 / 0.17 / 0.17 | 0.75 / 0.50 / 0.17 | 1.00 / 1.00 / 1.00 |
| Needle at the start, 15,037 tokens | 0.17 / 0.17 / 0.17 | 0.17 / 0.17 / 0.17 | 1.00 / 1.00 / 1.00 |
| KV recall, all cells | 0.225 / 0.273 / 0.229 | 0.200 / 0.246 / 0.242 | 0.204 / 0.302 / 0.242 |
| Fact recall | 0.75 / 0.94 / 0.81 | 0.75 / 0.94 / 0.81 | 0.75 / 0.88 / 0.88 |
| Short needle | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 |

What this shows:

- **YaRN fails in one place.** With the fact at the very start of a context of
  10,000 tokens or more it scores chance (one in six) and picks one answer for
  every item, on all three seeds. From 25% depth onward it scores 0.83 to 1.00
  in every cell.
- **More YaRN training does not fix it.** `devmind-lc16k-yarn-500m` scores
  0.908 on the same surface and is still at chance in both start cells.
- **Base 1,000,000 scores 1.00 in all 20 cells on all three seeds.** Its
  held-out loss is 0.0127 to 0.0153 above YaRN (standard error about 0.0015),
  which the probe marks `warn`; the fail threshold is 3%.
- **Base 80,000 is not a dependable middle.** It matches YaRN's loss, but the
  10,026-token start cell ranges from 0.75 to chance across seeds and the
  15,037-token start cell never recovers.
- **KV recall does not separate the arms.** Every arm is near chance except at
  the shortest length and at the end of the context.
- Cells of 65,536 and 98,304 characters are about 20,000 tokens, outside the
  16,384-token window, and are reported as out of window, not scored.

Limits of this evidence:

- Twelve items per cell and seed, six candidate answers, one haystack style.
- The probe verdict was `rerun` for every pair because the `lm_eval` probe was
  unavailable in the accelerator runtime. Every probe that ran passed or
  warned; repetition warned for both raised-base arms at seed 43 and moved the
  other way at seed 42. The seed 42 pair has since been probed with `lm_eval`
  ([below](#general-language-check)); the other six pairs have not.
- The held-out split has now been used to choose between arms twice. The
  held-back final split has not been read.
- Whether the 0.7% loss gap narrows at the full budget is not measured.

Decision, 27 November: run the full stage-2 budget at base 1,000,000
(`devmind-lc16k-abf-500m`, seed 42, same config as `devmind-lc16k-yarn-500m`
apart from the position encoding, same Lab commit `e0bbbb0c`). Its result is in
[Full run at base 1,000,000](#full-run-at-base-1000000).

### General-language check

After `lm-eval` 0.4.13 was installed next to the accelerator runtime, the seed
42 pair was probed again: `devmind-lc16k-abf-50m` against
`devmind-lc16k-yarn-50m-r2`, full tier, suite version 7, probe record
`probe-20261127T181144Z-5f16ac1e`. Nothing was missing this time, so the
verdict is a real one: `tweak`, for the held-out loss `warn` and no loss gain.
Every other row matches the earlier probe of this pair.

Accuracy on the first 50 items of each task, zero-shot
([lm-eval.csv](lm-eval.csv)):

| Task | YaRN | Base 1,000,000 |
| --- | --- | --- |
| arc_easy | 0.44 | 0.44 |
| hellaswag | 0.38 | 0.40 |
| lambada_openai | 0.38 | 0.34 |
| piqa | 0.56 | 0.60 |
| Mean | 0.440 | 0.445 |

The mean differs by 0.005 with a standard error of 0.015, and no task differs
by more than two items. Neither arm wins. The raised base did not measurably
change general-language ability at this budget, which is the most this check
can say: 200 items can only show a gap of about three points, and both
checkpoints sit close to chance (0.25 for arc_easy and hellaswag, 0.50 for
piqa).

## Full run at base 1,000,000

`devmind-lc16k-abf-500m` started from `devmind-pretrain-r3-a18` on
27 November and completed on 28 November: step 3,815, 392,953,439 tokens
seen, 13.1 hours, no interruptions, final checkpoint verified. It used the
same config, seed 42 and Lab commit `e0bbbb0c` as `devmind-lc16k-yarn-500m`,
with `attention.rope_base=1000000.0` and no RoPE scaling.

It was probed against the YaRN full run with the standard full tier, suite
version 7, `lm_eval` included (probe record
`probe-20261128T082047Z-0816534e`, [full-run.csv](full-run.csv), cells in
[retrieval-surface.csv](retrieval-surface.csv)). Nothing was missing. Every
probe passed and the verdict is `tweak`, because the held-out loss did not
improve.

| Probe | YaRN full | Base 1,000,000 full |
| --- | --- | --- |
| Held-out loss | 1.9920 | 1.9970 |
| Long needle, all cells | 0.908 | 0.996 |
| Needle at the start, 10,026 tokens | 0.17 | 0.92 |
| Needle at the start, 15,037 tokens | 0.17 | 1.00 |
| KV recall, all cells | 0.267 | 0.321 |
| Short needle, 31 to 120 tokens | 18 of 18 | 16 of 18 |
| Fact recall | 0.875 | 0.9375 |
| Repetition (seq-rep-4) | 0.466 | 0.509 |
| Calibration error | 0.0115 | 0.0120 |
| lm-eval, mean of four tasks | 0.430 | 0.440 |

What this shows:

- **The loss gap shrank with the full budget.** It is 0.0050 (standard error
  0.0011), or 0.25%, against 0.71% in the short arms. That is under the
  probe's 0.5% warning line, so held-out loss passes where the short arm
  warned.
- **Retrieval held.** 19 of 20 long-needle cells score 1.00. The one miss is
  a single item of twelve in the 10,026-token start cell, where YaRN is at
  chance and picks one answer throughout.
- **KV recall moved a little** (0.054, standard error 0.020), mostly at about
  10,000 tokens. Both models are still near chance at 15,000 tokens away from
  the end of the context.
- **General-language tasks are level.** lm-eval differs by 0.010 with a
  standard error of 0.014: arc_easy 0.48 against 0.44, the other three tasks
  identical.
- **Two short-needle items were missed**, both at the shortest length (about
  31 tokens), where the YaRN run and all three short base-1,000,000 arms
  scored 18 of 18. The difference is 1.5 standard errors and the probe passes
  it. It is the one sign of a short-context cost and has not been followed up.
- Repetition rose by 0.043, under the probe's warning line of 0.05.

Limits: one seed at this budget, twelve items per cell, 50 items per lm-eval
task, and the held-out split has now been read three times for this choice.
The held-back final split has not been read.

Outcome: `devmind-lc16k-abf-500m` is the stage 2 checkpoint to carry forward.
The stage 2 declarations in this recipe still describe YaRN.

## Lessons

- **Held-out loss alone picked the wrong arm.** YaRN's loss was 0.7% lower
  and it could not use the first tokens of a long context. Choose a context
  extension on retrieval across the window as well as on loss.
- **A retrieval probe needs depth as well as length.** Six items with the fact
  always at the start showed that something failed at 10,000 tokens. Only the
  length by depth grid showed that the failure was confined to the start of
  the context and that everything from 25% depth onward worked.
- **More training did not repair the encoding.** The 500 million token YaRN
  run finished with the same blind spot as the 39 million token arm. A short
  arm was enough to see it, and the full budget had been committed on the
  loss comparison alone.
- **One seed would have misled twice.** At seed 42 base 80,000 scored 0.75 in
  the 10,026-token start cell and looked like a cheap middle; seeds 43 and 44
  scored 0.50 and chance.
- **Check that the whole probe tier can run before training for it.** The
  full tier ends with `lm_eval`, the runtime did not have it, and every
  verdict came back `rerun` after the arms had trained. Lab now refuses a
  full-tier probe, try or sweep up front when the harness or a task's dataset
  cannot be loaded
  ([model-lab#722](https://github.com/supernovae/model-lab/pull/722),
  [#723](https://github.com/supernovae/model-lab/pull/723)).
- **Score at the precision the run trained in.** The fp32 scorer needed 24 GiB
  for one attention matrix at 16,384 tokens and the first probe numbers came
  from a patched scorer. Fixed in
  [model-lab#720](https://github.com/supernovae/model-lab/pull/720).

## What ran

All runs start from `devmind-pretrain-r3-a18` (final checkpoint, step 91,553),
use the 16,384-token long-context mixture (dataset revision `2bc68a80…decc7a`),
seed 42, bf16, four Arc Pro B70 cards under zero1 with SDPA attention and
recomputation, on Lab commit `e0bbbb0c` (a local branch carrying the change
tracked in Lab #650).

| Run ID | Arm | Status | Steps | Tokens seen |
| --- | --- | --- | --- | --- |
| `devmind-lc16k-yarn-50m` | YaRN, short | interrupted by a power cut near step 61 | | |
| `devmind-lc16k-yarn-50m-r1` | recovery of the above | stopped by hand at step 102 | | |
| `devmind-lc16k-yarn-50m-r2` | recovery of `-r1` | completed | 382 | 38,970,527 |
| `devmind-lc16k-abf-50m` | larger base, short | completed | 382 | 38,970,527 |
| `devmind-lc16k-yarn-500m` | YaRN, full stage 2 | completed | 3,815 | 392,953,439 |

The two short arms were launched as separate `klab train` runs with the same
shortened config, so there is no `klab try` record for the comparison. The
YaRN arm was interrupted twice and recovered; the larger-base arm ran straight
through.

## Results

Validation loss from the trainer (4 batches of 16,384 tokens):

| Run | Before training | At the end |
| --- | --- | --- |
| YaRN, short | 2.008 | 1.9967 |
| Larger base, short | 3.270 | 2.0112 |
| YaRN, full | 2.008 | 1.9920 |

The larger base starts far worse because it changes every rotation frequency
at once, and it had closed almost all of that gap by step 382. Its training
loss was still above YaRN's at every logged step, with the gap narrowing from
0.018 to 0.013.

Probe battery, suite version 6, full tier, held-out split
([probes.csv](probes.csv)):

| Probe | YaRN short | Larger base short | YaRN full |
| --- | --- | --- | --- |
| Held-out loss | 1.9967 | 2.0112 | 1.9920 |
| Long needle, about 5,000 tokens | 6 of 6 | 6 of 6 | 6 of 6 |
| Long needle, about 10,000 tokens | 1 of 6 | 6 of 6 | 1 of 6 |
| Short needle, 31 to 120 tokens | 18 of 18 | 18 of 18 | 18 of 18 |
| Fact recall | 0.75 | 0.75 | 0.875 |
| Calibration error | 0.0147 | 0.0142 | 0.0115 |

Against the short YaRN arm, the larger base is 0.0145 worse on held-out loss
(standard error 0.0015) and the full YaRN run is 0.0046 better (standard
error 0.0013).

At about 10,000 tokens both YaRN checkpoints pick the same answer, "kite", for
all six items, which is why they score one of six: chance. Every item is in
[long-needle.csv](long-needle.csv). The battery also has items of about 20,000
and 40,000 tokens. Those are longer than the model's context, every checkpoint
scores chance on them, and they say nothing about these arms.

## How far to trust this

- **The probe numbers come from a patched scorer.** `klab probe` scores in
  fp32, and at 16,384 tokens one attention matrix needs 24 GiB, so the standard
  command runs out of memory on a 32 GiB card (Lab #669). These numbers were
  produced with the model's forward pass wrapped in bf16 autocast, the
  precision the runs trained in. The records are diagnostic and were kept out
  of the lab directory. Rerun with the standard command once #669 is fixed.
- **The probe verdict is `rerun`** for both comparisons, because the `lm_eval`
  probe was unavailable. Every probe that ran passed, except that held-out loss
  for the larger base was marked `warn`.
- **One seed.** The loss gap between the arms is within-run noise until paired
  seeds confirm it.
- **Six items per length**, with the needle always at the start of the input
  and one fixed set of six answers. This measures one position at two usable
  lengths. It does not show whether either arm retrieves from the middle of
  the context, or anything beyond single-fact lookup.
- **The arms are not symmetric.** The larger base moved every frequency and
  had 39 million tokens to recover; whether its loss gap closes with the full
  budget is not measured.
- Fact recall has few items; its change is about 1.5 standard errors.

## Not run

- Any base between 80,000 and 1,000,000. Gao et al. 2025 ("How to Train
  Long-Context Language Models (Effectively)", ACL) found the best base to be
  about twice the dynamic-NTK value for the new length; for a fourfold
  extension of this model that is on the order of 80,000, far below the
  1,000,000 used here.
- `lm_eval` for the seed 43 and 44 pairs.
- A second seed of the full run, and a closer look at the short-needle misses.
- Short-context checks after stage 2 (does the 4,096-token behaviour survive).
- Stage 3.

## Next (as of 26 November; both items are done above)

Do not start stage 3 from `devmind-lc16k-yarn-500m` on the strength of its
loss. Before another full run, get a retrieval measurement that covers needle
depth as well as length and has enough items to separate the arms, and fix the
fp32 scorer so the standard probe produces the record.
