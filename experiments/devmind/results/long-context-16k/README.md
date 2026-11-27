# Stage 2 at 16,384 tokens: YaRN against a larger RoPE base

Run notes for 26 November 2026. The question was which way of lengthening the
context to use for stage 2: YaRN RoPE scaling (`context-16k.yaml`) or a larger
RoPE base with no scaling (`long-context-abf.yaml`, base 1,000,000). Two short
arms were trained from the same pretraining checkpoint, the lower held-out loss
picked YaRN, and the full stage-2 budget was then spent on YaRN.

The result is mixed and the choice is open again. YaRN has the lower loss, but
it cannot retrieve a fact from about 10,000 tokens back, and ten times more
training did not change that. The larger base retrieves it after the short arm
alone.

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

- The larger base at the full stage-2 budget.
- Any base between 10,000 and 1,000,000. Gao et al. 2025 ("How to Train
  Long-Context Language Models (Effectively)", ACL) found the best base to be
  about twice the dynamic-NTK value for the new length; for a fourfold
  extension of this model that is on the order of 80,000, far below the
  1,000,000 used here.
- Short-context checks after stage 2 (does the 4,096-token behaviour survive).
- Stage 3.

## Next

Do not start stage 3 from `devmind-lc16k-yarn-500m` on the strength of its
loss. Before another full run, get a retrieval measurement that covers needle
depth as well as length and has enough items to separate the arms, and fix the
fp32 scorer so the standard probe produces the record.
