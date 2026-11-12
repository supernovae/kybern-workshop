# TinyStories lifecycle and operations

[Recipes and commands](README.md)

Use the two recipes to prepare shared inputs, train and resume each model, and
move a run to another machine. The checked-in runtime is an example PyTorch/ROCm
FP32 setup. Set local storage paths and pick the supported runtime for your
hardware before staging.

The [versioned validation note](README.md#versioned-validation) records config,
source-loader, shape and separate CPU parameter checks that passed on Lab
`1b9fed431f7257007e2bdb931de05f63b8c19109` and on the workflow reference,
`b3a1630ec09dbddae36301b0acef4122623ed939`, with the Workshop configs unchanged.
The metadata-only dataset lock and its native verification also passed on the
reference pin, without downloading the stories. The later
[local ROCm results](../../results/2026-10-31-tinystories-rocm/README.md) record the
download, preparation and reuse, GPU pilots, the full 5M run with signal and resume
checks, short 50M calibration runs, and a full 50M BF16 run to 1,000,001,536
targets. The original FP32 50M recipe (`run-50m.json`) has not run in full, and
the remote/Colab handoffs are still untested. Moving to a new source pin
also caused an unexpected rebuild of the packed cache; the record lists it as a
rebuild rather than as reuse.

## Workflow

1. **Prepare shared inputs.** Choose a working directory outside the repo, check
   free space and use the bounded source config. Fit the tokenizer on training
   documents only, pack once, and inspect coverage. Record usable supervised
   targets per pass separately from total training exposure.
2. **Stage each model.** Point both run configs at the same tokenizer and prepared
   data. Give each full run config its own stage bundle. Measure cold verification,
   staging copies and device memory.
3. **Measure and train.** Run the first 256 updates with the full budget unchanged.
   Measure throughput, memory, I/O and checkpoint costs, then forecast the rest.
   Verify the checkpoint, resume, try an orderly interruption, and finish the
   planned exposure. Calibrate the 50M model on its own, separately from 5M.
4. **Evaluate.** Verify the final generation, evaluate the held-out split and save
   the fixed prompt-panel outputs. Judge story quality separately: a finished run
   can still write poor stories.
5. **Check portability.** On each receiving machine, verify the copied inputs and
   checkpoint files before staging on the device. The separate 320-update segments
   test the handoff and resume; they don't replace the full 100M/1B recipes. See
   the transfer notes below.

## Storage and reusable inputs

Keep source snapshots, tokenizers, prepared data and checkpoints out of Git. Use
native manifests and their hashes to tell artifacts apart, and local path settings
to find them on each machine. A new path only tells Lab where to look; it doesn't
show that an artifact was copied completely or fits the run.

| Component | What defines it and how to reuse it | Storage lifetime |
| --- | --- | --- |
| Source snapshot | Pinned revision, selection/dedup policy and content inventory | Retain completed snapshot for preparation and verification |
| Tokenizer | Training inputs, fitting settings and tokenizer bytes | Reuse exact bytes across both tiers |
| Prepared data | Snapshot, tokenizer, objective/masks and packing semantics | Retain completed arrays and inventory; compatible width/depth, seed and budget changes should not require refitting/repacking |
| Run | Training settings, input hashes, runtime details and native run ID | Durable run directory with reports and checkpoint dependencies |
| Checkpoint | Immutable native generation and required recovery dependencies | Retain verified generations and necessary ancestry |
| Attempt scratch | In-progress acquisition, packing or transfer state | Remove only after completion or after confirming it is unnecessary for recovery |

Names such as `tinystories-shared`, `tinystories-5m` and `tinystories-50m` say what
a directory is for; native IDs tell runs and revisions apart. Artifact, run,
scratch and incoming-transfer directories can sit on different filesystems. When
you publish across filesystems, finish and verify the copy first; an atomic rename
on the source filesystem says nothing about whether a remote copy is complete.

If you change source selection, dedup policy, tokenizer, objective or masks, or
packing, build new downstream artifacts. If you change context length, recompute
coverage for usable blocks and tails, even when the packed token streams can be
reused. If you change backend, check device readiness again.

`stage --prepared-inputs` currently binds the full config and may copy data, so
don't use a 5M stage bundle for 50M. Binding compatible inputs and staging a full
config are separate steps; see the Lab
[dataset guide](https://github.com/supernovae/model-lab/blob/b3a1630ec09dbddae36301b0acef4122623ed939/docs/datasets.md).
If a reuse request reports a mismatch, keep the message and check which input
changed before rerunning expensive preparation.

## Scaling shared data

Prepared data doesn't depend on model size. The 5M and 50M recipes, and a future
100M model, can reuse the same finished data as long as the tokenizer, objective,
packing and inputs stay compatible. Training on more targets or for more epochs
needs no new data and no new preparation pass. Report corpus supply and repeated
exposure separately.

To add more unique data, create a new versioned shard inventory that lists the
unchanged finished shards alongside the new ones. You can reuse existing
tokenization for unchanged content only when the tokenizer bytes and tokenization
rules match; refitting the tokenizer means retokenizing what it affects. Keep
train/validation assignments stable, and dedup globally with validation taking
priority across old and new content. Resolve overlap before you publish the new
inventory. If new validation content knocks out training records you used before,
record those exclusions and the resulting inventory change.

When you extend an inventory, check packing boundaries, document order, usable
blocks and tails. Appending can change boundary packing or coverage even when the
tokenized content is reusable, so appending is not automatically safe. Repack the
affected boundaries, or rebuild dependent artifacts where needed, and write down
why. Keep earlier versions so past runs stay reproducible.

This section is about growing the data; there is no 100M training recipe yet. A
larger model needs its own config and run. Reusing data doesn't make a model bigger or
let an existing checkpoint load into a different architecture.

## Physical placement and concurrency

The placement options below are planned Lab features that we want to test through
Workshop. They are not supported yet and have no CLI commands. The plan: one
logical dataset across all locations, with a separate placement manifest that maps
its immutable shard IDs to verified physical copies. Worker count, device layout
and transfer location are execution settings and should not change the experiment.
Keep record and block order, the shuffle algorithm and seed, and the committed
restart cursor fixed, so that moving data around never quietly changes training
order or exposure.

| Storage layout | Placement and concurrency plan |
| --- | --- |
| One storage pool | Share the verified shard inventory; measure aggregate bandwidth and contention before increasing reader/writer concurrency. A pool can conceal several physical devices. |
| Four NVMes | Distribute shards by measured bytes and processing cost; place workers near local shards and maintain separate byte queues and concurrency limits per device. Do not assume fourfold throughput. |
| Eight independent disks | Assign explicit shard replicas to each disk; use device-specific concurrency and sequential access where beneficial. Measure seek/contention costs and avoid treating all disks as one uniformly fast queue. |
| Four machines | Schedule work near verified local shards, transfer only required dependencies, and bound inter-machine traffic. Merge inventories and global operations deterministically; completion order must not become dataset order. |

Limit in-flight bytes, worker memory, prefetch depth and concurrent reads and
writes per device and per machine. Apply backpressure before queues eat the memory
budget. Measure how unevenly shard sizes and processing costs are spread, and use
that to assign work or rebalance copies without changing shard contents or
logical order. Tune for end-to-end throughput and tail latency rather than worker
count. Restart from committed work and verify outputs you plan to reuse; a new
worker assignment must not duplicate or drop records, blocks or committed training
targets.

In the cloud, choose between direct reads, staging or preloading, and a bounded
cache based on measured throughput, latency, contention, capacity and cost for the
data you need. Local disk is not always faster than NFS or object storage, so
compare the actual paths. Where you can, verify the needed artifacts and the access
path before reserving a GPU; checking device readiness still needs the allocated
hardware. Limit network concurrency and prefetch in every mode. When resuming a
stage or refilling a cache, verify what you already have and fetch only what is
missing or bad. Check content checksums; an object ETag is not necessarily a
content digest. An incomplete upload or download is never a ready input.

On S3-compatible storage, write immutable object keys and publish a completion
manifest only after every required object checks out; there is no POSIX rename to
lean on. On POSIX storage, atomic rename publishes within one filesystem and says
nothing about a remote copy. NFS needs its own testing of shared-filesystem
locking, client caches, visibility, durability and network failures; don't expect
local-disk speed or behavior. Record which copies and files you would recover from
if the original location disappeared. These placement and replication rules apply
to new-format artifacts. Importing old artifacts, if ever needed, belongs in a
separate throwaway script outside the core workflow.

## Capacity and calibration

The source config uses the supported bounds: 3M source records per split, 1GiB
selected text, 1MiB per serialized record and 8GiB of snapshot work. Packing caps
are 160M train tokens and 2,097,152 validation tokens. These are adjustable
ceilings in the recipe; measure what you actually need and get. If you hit a bound,
the work is incomplete; change the config on purpose rather than treating partial
input as complete.

The snapshot work limit leaves out Hub cache traffic and temporary decoding
memory. A small selection of documents can still download a large shard. Measure
cache growth, network traffic and retries separately, and use the supported cache
controls where they exist. Watch the first real stretch of preparation to estimate
how much more it will grow.

The source template sets `min_free_bytes: 0` because no single reserve fits every
machine. Before you lock a local copy of the source config, choose a margin from
the space you actually have, what else is using the disk, and the growth you still
expect. Write down the margin you chose. Check both the output and cache
filesystems. Zero just means no reserve was set.

| Phase | Access and working set | Coexisting storage |
| --- | --- | --- |
| Acquire/snapshot | Sequential transfer/decode; potentially random dedup-index I/O; decoder transient RAM | Cache + journal/index + in-progress and completed snapshot |
| Fit/pack | Sequential reads/writes; tokenizer host working set | Source + tokenizer + resumable chunks + final arrays |
| Stage/verify | Explicit cold full reads; possible full input copies | Immutable inputs + tier stage copies + incoming copy |
| Train/eval | Loader block access/page faults; cold/warm cache; model, optimizer, activations and evaluation buffers | Run-owned inputs, evaluation scratch and checkpoint ancestry |
| Checkpoint/transfer | Sequential writes/reads, save stalls and slowest-link throughput | Previous durable generation + temporary replacement + incoming replica |

For each phase, record wall and CPU time, useful targets/sec, records/sec, I/O
rates, host RSS, GPU allocated and reserved peaks, disk and inode peaks, cache
growth and retained bytes. Mark any reading you couldn't get. Int32 token IDs
alone take 4 bytes/token (~640MB at the training cap). FP32 AdamW weights,
gradients and two moments take roughly 16 bytes/parameter (~85MB / ~809MB for the
two models). These estimates leave out masks, indexes, copies, activations and
framework workspaces, so measure the rest on the real workload.

Compare the estimated peak plus your own safety margin with the space you have. If
you don't know the peak, run a short segment and watch it. Stop if you actually
run out, if growth gets out of hand, or if there isn't room for a durable
checkpoint. Keep fit failures, and treat any batch or precision change as a new
config.

For each model, separate startup overhead from steady throughput within the first
256 updates; try to observe at least 128 updates after the first 16. If the rate
is unstable, watch longer within the same budget. Forecast the remaining time as
remaining targets divided by the measured rate, plus evaluation, checkpoint,
restart, verification, transfer and wrap-up costs. Report the spread and how far
the forecast was off, and update the forecast as measurements improve. Checkpoints
start every 256 updates; measure save stalls and how much work a rollback would
lose before changing that.

## Choosing a pipeline approach

Before adding a new execution layer, compare Lab's existing preparation and
staging with established libraries. The options below are candidates we haven't
integrated. Workshop holds the recipes and acceptance checks; Lab holds the
general code. Try an option only against a bottleneck you've actually seen, and
don't make another library a requirement for useful runs.

| Approach | Useful capability and tradeoff |
| --- | --- |
| Native Lab | Start with `data snapshot`, `tokenizer train`, `data prepare`, coverage and prepared-input verification. Preserve their artifact and recovery contracts when changing execution. |
| Hugging Face Datasets | Batched `map` with bounded `num_proc` can parallelize independent transforms; Arrow supports reusable local outputs. Index-based shuffle sacrifices contiguous reads; rewriting flattened indices costs another full write, while buffered iterable shuffle changes shuffle semantics. [Processing guide](https://huggingface.co/docs/datasets/en/process) |
| Mosaic Streaming | Shard retrieval exposes prefetch and cache limits; too-small caches can cause eviction/redownload churn. Consider when measured remote-read stalls justify conversion and integration costs. [Shard retrieval](https://docs.mosaicml.com/projects/streaming/en/stable/dataset_configuration/shard_retrieval.html) |
| DataTrove / FineWeb | DataTrove provides reusable processing blocks and bounded local workers over shard tasks; a single file is not automatically split. FineWeb documents filtering/deduplication ablations, not a requirement to copy web-scale fuzzy dedup into TinyStories. [DataTrove](https://github.com/huggingface/datatrove), [FineWeb](https://arxiv.org/abs/2406.17557) |
| PyTorch asynchronous checkpoints | CPU staging buffers can overlap saving with work but add host-memory pressure; start with at most one outstanding save. Measure actual ROCm compatibility and preserve verified publication/recovery before adopting. The tutorial alone does not establish Lab support. [DCP recipe](https://docs.pytorch.org/tutorials/recipes/distributed_async_checkpoint_recipe.html) |

One pattern worth trying is a bounded shard pipeline: decode and transform shards
in parallel, then tokenize with the frozen tokenizer and pack with a clear
boundary rule. Coordinate only the steps that need a global view, such as exact
dedup and the split and order inventories. For exact dedup, compare the current
disk-backed index with hash partitioning plus an external sort and merge; check
hash collisions against the content and keep validation priority. None of these
alternatives is implemented here yet.

Keep record and shard IDs, and output order, independent of which worker finishes
first. Spell out the shuffle seed, algorithm, buffer or shard policy and resume
cursor; an approximate shuffle is not a drop-in for a full permutation. Bound the
queues for backpressure, cap worker and prefetch memory, plan for uneven shard
sizes and disk spill, and publish reusable binary outputs only after they are
complete and verified. Packing boundaries and supervised-target coverage must stay
comparable.

Use portable CPU dispatch with a fallback instead of assuming one SIMD target;
benchmark AVX2-compatible paths on Zen 3 without requiring AVX-512. AMD's
[optimization guidance](https://gpuopen.com/gdc-presentations/2024/GDC2024_AMD_Ryzen_Processor_Software_Optimization.pdf)
covers ISA requirements and SIMD transition costs. The
[TinyStories paper](https://arxiv.org/abs/2305.07759) is why small-model
experiments like these are worth running; it doesn't predict throughput for these
recipes or this hardware.

## Performance acceptance

Before calling the workflow ready, go through each stage looking for serial work,
CPU and GPU utilization, I/O wait, transfer bandwidth, and repeated reads or
copies. Separate compute-bound work from storage, decoding, tokenization and
synchronization stalls. Use the real workload and record per-stage timings
alongside end-to-end throughput.

Where more concurrency could fix a bottleneck you've seen, compare a serial
baseline with a small range of worker counts, batch sizes or prefetch depths.
Change one setting at a time and stay within available RAM, VRAM and storage.
Record throughput, latency, utilization and peak resource use, including
contention and setup overhead. Keep serial execution where it is faster or more
predictable; not every stage gains from parallelism.

Adopt a faster setup only if artifact verification, deterministic ordering where
needed, supervised-target accounting, preparation reuse and checkpoint recovery
all still pass. Changing the batch or a training setting makes a separate config,
so compare it as a different experiment.

A material bottleneck is one that dominates elapsed time or stops you from
reaching the resource or throughput goal. Write that goal down before comparing
options. Fix a material bottleneck that can be avoided, then remeasure the whole
workflow before you accept performance. If it stays unfixed, report the measured
limit and leave performance acceptance open. Report the improvement or regression
you measured; worker count or utilization alone doesn't show a speedup. Setup
trials and short operational segments give performance and recovery data; they
don't count toward the full training budgets.

## Checkpoint recovery and transfer

A verified native full-state generation can be resumed under compatible settings.
A full resume needs the same engine and backend, architecture, tokenizer and data,
optimizer, schedule horizon, budget, batch, sequence length and deterministic
settings. Resuming creates a child run and leaves the parent intact. See the Lab
[checkpoint guide](https://github.com/supernovae/model-lab/blob/b3a1630ec09dbddae36301b0acef4122623ed939/docs/checkpointing.md).

If the runtime or device changed, you may need `--allow-runtime-drift`; the run is
then recorded as a best-effort continuation that may not match bit for bit.
ROCm-to-CUDA can't be a strict resume. `train --promote` takes compatible weights
and starts fresh optimizer, schedule, scaler, RNG, cursor and counters. Track its
exposure as a separate run.

To stop a run, press Ctrl-C or send SIGTERM and wait for it to exit. If the
process dies abruptly, you can recover only to the last saved generation, so
record that step and how much work was lost. Keep the previous good generation
until its replacement verifies. Explicitly selecting a corrupt generation should
fail, and the generation `--recover` picks should show up in the run record.

Recipe export copies the configs only; it doesn't move the full set of prepared
data and checkpoint files. This study has no tested command sequence for moving a
run end to end yet. Remote and Colab handoffs need checking on the receiving
machine with the original paths unavailable; until that's done, treat them as
untested.

When transferring, keep incoming data separate until the inventory, file lengths
and digests, and all recovery files check out. Only then mark it complete.
Partial uploads must never become ready inputs. Test the refusal of corrupt or
partial copies on a throwaway copy, never on your only copy. Transfer and verify
data before you reserve paid GPU time; checking device readiness still needs the
target hardware.

Treat Colab's local storage as scratch. Save checkpoint exports somewhere
persistent and verify them before you rely on them after a disconnect. You can
recover only to the last verified export, which may be behind your local saves.
Measure export time when you choose how often to export. Keep metadata listing
separate from full cold verification of the corpus, and use the metadata-only path
to browse large inventories.
