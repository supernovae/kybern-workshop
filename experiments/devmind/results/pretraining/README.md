# Pretraining on four cards: what it took to finish

Run notes for 18 to 25 November 2026. The pretraining stage in
[pretrain.yaml](../../pretrain.yaml) finished: 12 billion tokens, 91,553
steps, final checkpoint `devmind-pretrain-r3-a18` at step 91,553 with
validation loss 2.019. It took three starts and nineteen attempts over a
week. This page records why each attempt stopped and what was changed, so the
next long run starts from the working setup.

Every attempt and its stop is in [attempts.csv](attempts.csv).

## What ran

| | |
| --- | --- |
| Model | 1.247 billion parameters (845 million active), 28 layers, hidden 1,536, 4,096-token rows, 2x Engram tables |
| Settings | bf16, flex attention, fused AdamW, micro-batch 1 with 32 accumulation steps, seed 42 |
| Hardware | four Arc Pro B70 (32 GiB), one process per card, 98 GB host RAM, headless |
| Software | PyTorch 2.15.0+xpu, Python 3.14.8, Linux 7.3.0-10 |
| Lab commit | `8385b689` for every attempt through `-a17`; `9331304c` for `-a18` |
| Checkpoints | every 120 minutes or 250 million tokens, 15 GB each, only the newest kept |
| Result | `devmind-pretrain-r3-a18`, status `completed`, step 91,553, 12,000,000,000 tokens, checkpoint verified |

Validation loss along the way, from the trainer's inline evaluation on the
held-out split: 3.542 at step 1,823, 2.310 at step 25,775, 2.304 at step
26,984, 2.150 at step 51,828 and 2.019 at the end. Four strata (notebooks,
practice, reference, systems code) have no validation documents, so this
number does not see them.

Time and speed:

| Span | Layout | Steps | Speed |
| --- | --- | --- | --- |
| `-r3-a0` | `zero1` | 0 to 1,823 | about 31,000 tokens/s including startup (preflight warmup 34,829) |
| `-r3-a1` to `-a17` | `replicated` | 1,823 to 51,828 | about 21,400 tokens/s over the 40-hour `-a17` |
| `-r3-a18` | `zero1`, resumed | 51,828 to 91,553 | 34,000 tokens/s end to end over 42.5 hours |

The run held 128.6 hours of training wall time. From the third start to the
end was 6 days 5 hours on the calendar; the difference is recoveries, a
nine-hour halt on a full disk and seven hours validating the `zero1` resume.

## What stopped it, in order

**Two power cuts (18 November).** The first two starts, `devmind-pretrain-a0`
and `devmind-pretrain-r2-a0`, lost power at steps 136 and 311, before any
checkpoint. Both are still marked `running` in the run store because nothing
was alive to mark them. Nothing was recoverable, and the third start began
from step 0.

**Resuming a four-card `zero1` run stalled.** Found in rehearsal before the
real run: a fresh `zero1` run was fine, but a resumed one finished one slow
update and then made no progress, with the three worker cards full
(31.89 of 31.89 GiB) and host RAM draining. Running headless did not change
it. The plan became: start fresh in `zero1`, and recover in `replicated`,
which resumed cleanly at about two thirds of the speed
([model-lab#534](https://github.com/supernovae/model-lab/issues/534),
[#533](https://github.com/supernovae/model-lab/pull/533)).

**Seven stops by the host memory guard (19 to 21 November).** Lab's spill
guard ends a run when available host memory falls by more than half after the
first update. It ended `-a1` to `-a6` and `-a16`. Each recovery picked up from
the last checkpoint, so little work was lost: between 1 and 48 steps in six of
the seven, and 334 in `-a1`. The cause was outside training. A
checkpoint archiver copied and checksummed each new 15 GB checkpoint, the ZFS
cache was uncapped and grew to 24 to 36 GiB of host RAM while it read, and
the replicated layout already needed about 66 GB. Six of seven stops came
0.6 to 5.4 minutes after a checkpoint was written. The archiver was stopped
and the ZFS cache capped at 8 GiB after `-a16`; `-a17` then
ran 40 hours and 23,644 steps without a stop.

**A full disk (21 November, 06:36 to 15:48).** Every attempt copied the 48 GB
of prepared data into its own run directory. After seven attempts the disk
had 72 GB free, Lab's storage check refused `-a7`, `-a8` and `-a9`, and the
supervisor gave up after three restarts with no newer checkpoint. The run sat
idle for nine hours overnight. The copies of dead attempts were deleted once
checked byte-identical to the prepared data. Lab now does this with
`klab workspace cleanup`.

**Damaged optimizer state from a sharded resume (21 November).** Two trials
of resuming in `zero1` (`-a11`, `-a14`) stalled and were stopped by hand.
The second one saved its restored state as a checkpoint first. The next recovery, `-a15`, read it
and failed on its first update with a non-finite loss. The optimizer
statistics of the four largest Engram tables had exactly a quarter of their
elements wrong: one rank's shard never arrived during the restore and stale
memory was kept. The weights were bit-identical. Those tables have row counts
that do not divide by four. `-a16` recovered from `-a13`, the last good
checkpoint, and the checkpoints of `-a14` and `-a15` were set aside. No
damaged state entered the finished model's lineage.

**Two refusals for changed code identity.** `-a10` and `-a12` were refused
because the code identity differed from the parent run's; they were
relaunched with `--allow-runtime-drift`. Why the identity differed while the
checkout stayed on `8385b689` was not investigated.

## What was changed to finish

- **The cause of the `zero1` resume stall, part one.** Each worker rank kept
  a second, unsharded copy of the weights on its card, 4.65 GiB per card.
  [model-lab#554](https://github.com/supernovae/model-lab/pull/554) frees it.
- **Part two.** The sharded optimizer restore went through collectives, which
  is where a shard was lost.
  [model-lab#559](https://github.com/supernovae/model-lab/pull/559) restores
  it without them.
- **A driver regression.** Level Zero driver `libze-intel-gpu1` 26.40.40196.8
  hangs every collective above about 1 MiB; 26.27.39122.14 works. The host is
  pinned to 26.27 (reported upstream as intel/compute-runtime#1062).
- **Back to `zero1`.** With those in place `-a17` was stopped by hand at a
  checkpoint on 23 November, the resume was rehearsed on the real checkpoint,
  and `-a18` resumed in `zero1` at step 51,828. It held about 27.7 GiB per card in rehearsal and
  ran to the end without a stop, 60% faster than `replicated`.
- **Host memory.** The ZFS cache is capped at 8 GiB and nothing copies
  checkpoints while training.
- **Lab changes the run prompted.** A recovery that changes the device layout
  now warns ([#536](https://github.com/supernovae/model-lab/pull/536)), and
  the prepared-data identity depending on checkpoint cadence and logging,
  which forced three restages and a 90-minute re-prepare before the run, was
  tracked and closed as [#528](https://github.com/supernovae/model-lab/issues/528).

## Lessons

- **Rehearse the resume, not only the start.** A fresh four-card run passed
  its warmup and a 100-step burn-in. Every serious problem was in resuming.
- **Watch host RAM as closely as card memory.** No stop in this run was a
  card running out. Seven were the host, and the cause was a helper process
  and a filesystem cache.
- **Run nothing else that reads checkpoints during training.** Archive during
  a pause.
- **Size the disk for attempts, not for one run.** Each attempt cost 48 GB
  until dead copies were cleaned.
- **Stop with SIGTERM at a checkpoint and check each card before relaunching.**
  A killed rank can leave its card's copy engine wedged, and the next run
  hangs loading weights.
- **A checkpoint written after a bad restore is bad.** Recover from the last
  checkpoint written by an attempt that trained normally.
- **A power cut loses everything since the last checkpoint.** The first two
  starts had none. A UPS, or an early first checkpoint, would have kept them.
- **Supervisor-stopped attempts keep the status `running`.** Read the newest
  attempt with a live heartbeat, not the stored status.

## Not checked

- Loss continuity across each recovery step was not examined beyond the
  validation values above.
- The four strata without validation documents, memorization on the repeated
  `practice` and `reference` strata, and whether the Engram tables help. Order
  3 tables were about 70% collided at the preflight estimate.
- The supervisor was an interim shell wrapper around `klab train --recover`,
  tested against a stub before the run. A supervised long run in Lab itself
  is open as [model-lab#516](https://github.com/supernovae/model-lab/issues/516).

What came next is in [long-context-16k](../long-context-16k/README.md).
