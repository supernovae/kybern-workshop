# TinyStories lifecycle and operations

[Recipes and commands](README.md)

Use the two recipes to prepare shared inputs, train and resume each model, and
check operational portability to another machine. The checked-in runtime is an
example PyTorch/ROCm FP32 configuration. Bind local storage paths and select the
supported runtime for your hardware before staging.

The [versioned validation note](README.md#versioned-validation) records successful
declaration, source-loader, shape and separate CPU parameter checks on Lab
`1b9fed431f7257007e2bdb931de05f63b8c19109` and the intended workflow reference,
`b3a1630ec09dbddae36301b0acef4122623ed939`, with unchanged Workshop declarations.
Metadata-only dataset locking and native lock verification also passed on the
reference pin; this did not download corpus bodies. GPU fit, source acquisition,
data preparation/reuse, training, performance, recovery and remote/Colab handoffs
remain unvalidated.

## Workflow

1. **Prepare shared inputs.** Choose an external working directory, check available
   storage and use the bounded source declaration. Fit the tokenizer on training
   documents only, pack once, and inspect coverage. Record usable supervised
   targets per pass separately from total training exposure.
2. **Stage each model.** Bind both run configs to the same tokenizer and prepared
   data. Use a separate stage bundle for each full run configuration. Measure cold
   verification and staging copies as well as device memory use.
3. **Measure and train.** Run the first 256 updates with the full budget unchanged.
   Measure throughput, memory, I/O and checkpoint costs, then forecast remaining
   work. Verify the checkpoint, resume, exercise an orderly interruption and finish
   the declared exposure. Calibrate the 50M model independently of the 5M model.
4. **Evaluate.** Verify the final generation, evaluate the held-out split and save
   the fixed prompt-panel outputs. Record quality separately from operational
   completion; completed training alone does not establish useful story quality.
5. **Check portability.** On each receiving system, verify transferred inputs and
   checkpoint dependencies before device staging. The separate 320-update segments
   test operational handoff and resume, not scientific completion of the full
   100M/1B exposure recipes. See the transfer limitations below.

## Storage and reusable inputs

Keep source snapshots, tokenizers, prepared data and checkpoints outside Git.
Use native manifests and immutable identities to identify artifacts; use local
bindings to locate them on each machine. A path change alone does not establish
that an artifact has been transferred completely or is compatible with a run.

| Component | Identity and reuse | Storage lifetime |
| --- | --- | --- |
| Source snapshot | Pinned revision, selection/dedup policy and content inventory | Retain completed snapshot for preparation and verification |
| Tokenizer | Training-input identity, fitting settings and tokenizer bytes | Reuse exact bytes across both tiers |
| Prepared data | Snapshot, tokenizer, objective/masks and packing semantics | Retain completed arrays and inventory; compatible width/depth, seed and budget changes should not require refitting/repacking |
| Run | Scientific settings, input identities, runtime provenance and native run ID | Durable run directory with reports and checkpoint dependencies |
| Checkpoint | Immutable native generation and required recovery dependencies | Retain verified generations and necessary ancestry |
| Attempt scratch | In-progress acquisition, packing or transfer state | Remove only after completion or after confirming it is unnecessary for recovery |

Names such as `tinystories-shared`, `tinystories-5m` and `tinystories-50m` describe
purpose; native IDs distinguish runs and revisions. Local artifact, run, scratch
and incoming-transfer directories can use different filesystems. Cross-filesystem
publication requires a completed verified copy; an atomic rename on the source
filesystem does not make a remote copy complete.

Changes to source selection, dedup policy, tokenizer, objective/masks or packing
semantics require new dependent artifacts. A context-length change requires a
fresh coverage calculation for usable blocks and tails, even when packed token
streams can be reused. A backend change requires fresh device readiness checks.

The current `stage --prepared-inputs` contract binds the full config and may copy
assets. Do not use a 5M stage bundle as a 50M stage bundle. Compatible-input binding
and full-config staging are distinct operations; consult the Lab
[dataset guide](https://github.com/supernovae/tiny-sparse-lab/blob/b3a1630ec09dbddae36301b0acef4122623ed939/docs/datasets.md).
If a reuse request reports a mismatch, preserve the diagnostic and inspect which
identity changed before repeating expensive preparation.

## Scaling shared data

Model parameter count does not define prepared-data identity. The 5M and 50M
recipes, and a future 100M model, can reuse the same completed data when tokenizer,
objective, packing and input semantics remain compatible. Increasing supervised
exposure or repeating more epochs does not require more unique data or another
preparation pass. Report corpus supply and repeated exposure separately.

To increase unique supply, create a new versioned additive shard inventory that
references unchanged completed shards alongside new shards. Reuse completed
tokenization for unchanged content only when tokenizer bytes and tokenization
semantics match; fit changes invalidate affected tokenization. Preserve stable
train/validation assignments and validation-first global deduplication across both
retained and new content. Resolve overlap before publishing the new inventory.
If new validation content excludes previously retained training records, record
the exclusions and resulting inventory change rather than claiming every old
training shard remains eligible unchanged.

Check packing boundaries, document order, usable blocks and tails when extending
an inventory. Appending can change boundary packing or coverage even when tokenized
content is reusable. Repack affected boundaries or invalidate dependent artifacts
when required by their semantics, with an explicit reason; arbitrary append-only
compatibility is not guaranteed. Preserve prior versions for reproducible runs.

This is a data-scaling contract, not a third 100M training recipe. A larger model
needs its own explicit configuration and run; data reuse does not enlarge model
weights or make an existing checkpoint compatible with a different architecture.

## Physical placement and concurrency

The following placement options are planned generic Lab capabilities to validate
through Workshop; they are not tested support or additional CLI commands. Keep one
logical dataset identity across locations. A separate placement manifest maps its
immutable shard IDs to verified physical replicas. Worker count, device topology
and transfer location are execution settings, not scientific identity. Preserve
canonical record/block order, shuffle algorithm/seed and committed restart cursor;
changing placement must not silently change training order or exposure.

| Storage layout | Placement and concurrency plan |
| --- | --- |
| One storage pool | Share the verified shard inventory; measure aggregate bandwidth and contention before increasing reader/writer concurrency. A pool can conceal several physical devices. |
| Four NVMes | Distribute shards by measured bytes and processing cost; place workers near local shards and maintain separate byte queues and concurrency limits per device. Do not assume fourfold throughput. |
| Eight independent disks | Assign explicit shard replicas to each disk; use device-specific concurrency and sequential access where beneficial. Measure seek/contention costs and avoid treating all disks as one uniformly fast queue. |
| Four machines | Schedule work near verified local shards, transfer only required dependencies, and bound inter-machine traffic. Merge inventories and global operations deterministically; completion order must not become dataset order. |

Bound in-flight bytes, worker memory, prefetch depth and concurrent reads/writes
per device and machine. Apply backpressure before queues consume the memory budget.
Measure shard-size and processing-cost skew; use those observations to assign work
or rebalance replicas without changing shard contents or logical ordering. Tune
scheduling against end-to-end throughput and tail latency, not worker count alone.
Restart from committed logical work and verify reusable outputs; a changed worker
assignment must not duplicate or omit records, blocks or committed training targets.

For cloud execution, choose direct reads, staging/preloading or a bounded cache
from measured throughput, latency, contention, capacity and cost for the required
working set. Local storage is not necessarily faster than NFS or object-backed
access; compare the actual paths. Verify required artifacts and the chosen access
path before GPU reservation where possible; device readiness still requires the
allocated hardware. Bound network concurrency and prefetch in every mode. For
staging or cache refill, resume by fetching only missing or invalid members after
verifying retained ones. Validate content checksums rather than assuming an object
ETag is a content digest. Incomplete uploads or downloads are never ready inputs.

On S3-compatible storage, publish immutable object keys and a completion manifest
only after all required objects verify; do not model publication as POSIX rename.
For POSIX storage, atomic rename is a same-filesystem publication operation, not
a guarantee that a remote replica is complete. NFS needs separate validation of
shared-filesystem locking, client caches, visibility/durability and network failure
behavior; do not assume local-disk performance or coordination semantics. Record
which replicas and dependencies support recovery if the original location disappears.
These placement and replication contracts apply to new-format artifacts; legacy
import, if needed, is a separate disposable script outside the core workflow.

## Capacity and calibration

The source declaration uses supported bounds: 3M source records per split, 1GiB
selected text, 1MiB serialized record and 8GiB snapshot work. Packing caps are
160M train tokens and 2,097,152 validation tokens. These are configurable recipe
ceilings, not measured requirements or evidence of unique token supply. Reaching
a bound leaves incomplete work; revise the declaration explicitly rather than
presenting partial input as complete.

Snapshot work limits exclude Hub cache traffic and decoded-library transients.
A small document selection can still fetch a large shard. Measure cache growth,
network traffic and retries separately; use supported cache controls where
available. Observe the first real preparation segment to estimate remaining growth.

The source template's `min_free_bytes: 0` avoids prescribing a universal reserve.
Before locking a local source copy, choose a margin based on actual availability,
concurrent use and estimated remaining growth. Record the chosen margin. Check
both output and cache filesystems. Zero is not a statement of unlimited capacity.

| Phase | Access and working set | Coexisting storage |
| --- | --- | --- |
| Acquire/snapshot | Sequential transfer/decode; potentially random dedup-index I/O; decoder transient RAM | Cache + journal/index + in-progress and completed snapshot |
| Fit/pack | Sequential reads/writes; tokenizer host working set | Source + tokenizer + resumable chunks + final arrays |
| Stage/verify | Explicit cold full reads; possible full input copies | Immutable inputs + tier stage copies + incoming copy |
| Train/eval | Loader block access/page faults; cold/warm cache; model, optimizer, activations and evaluation buffers | Run-owned inputs, evaluation scratch and checkpoint ancestry |
| Checkpoint/transfer | Sequential writes/reads, save stalls and slowest-link throughput | Previous durable generation + temporary replacement + incoming replica |

Record phase wall/CPU time, useful targets/sec, records/sec, I/O rates, host RSS,
GPU allocated/reserved peaks, disk/inode peaks, cache growth and retained bytes.
Keep unavailable readings explicit. Int32 token IDs alone use 4 bytes/token
(~640MB at the training cap). FP32 AdamW weights, gradients and two moments use
roughly 16 bytes/parameter (~85MB / ~809MB for the two models). These estimates
exclude masks, indexes, copies, activations and framework workspaces; measure the
additional use on the actual workload.

Compare estimated peak plus a site-specific margin to available capacity. Unknown
peaks call for a short observed segment. Actual exhaustion, unmanageable growth or
insufficient room for a durable checkpoint are stop conditions. Preserve fit
failures and explicitly declare any batch/precision change as a new configuration.

For each model, separate initial overhead from steady throughput within the first
256 updates; aim to observe at least 128 updates after the initial 16. If unstable,
extend observation within the existing budget. Forecast remaining targets divided
by measured rate, adding evaluation, checkpoint, restart, verification, transfer
and finalization costs. Report variation and forecast-versus-observed error.
Revise estimates as measurements improve. The initial checkpoint cadence is 256
updates; measure save stalls and rollback exposure before changing it.

## Choosing a pipeline approach

Compare existing Lab preparation/staging with established libraries before adding
an execution layer. The options below are candidates, not validated integrations.
Workshop defines recipes and acceptance; Lab owns generic implementation. Evaluate
an option against an observed bottleneck within performance acceptance, without
making adoption of another library a prerequisite for useful runs.

| Approach | Useful capability and tradeoff |
| --- | --- |
| Native Lab | Start with `data snapshot`, `tokenizer train`, `data prepare`, coverage and prepared-input verification. Preserve their artifact and recovery contracts when changing execution. |
| Hugging Face Datasets | Batched `map` with bounded `num_proc` can parallelize independent transforms; Arrow supports reusable local outputs. Index-based shuffle sacrifices contiguous reads; rewriting flattened indices costs another full write, while buffered iterable shuffle changes shuffle semantics. [Processing guide](https://huggingface.co/docs/datasets/en/process) |
| Mosaic Streaming | Shard retrieval exposes prefetch and cache limits; too-small caches can cause eviction/redownload churn. Consider when measured remote-read stalls justify conversion and integration costs. [Shard retrieval](https://docs.mosaicml.com/projects/streaming/en/stable/dataset_configuration/shard_retrieval.html) |
| DataTrove / FineWeb | DataTrove provides reusable processing blocks and bounded local workers over shard tasks; a single file is not automatically split. FineWeb documents filtering/deduplication ablations, not a requirement to copy web-scale fuzzy dedup into TinyStories. [DataTrove](https://github.com/huggingface/datatrove), [FineWeb](https://arxiv.org/abs/2406.17557) |
| PyTorch asynchronous checkpoints | CPU staging buffers can overlap saving with work but add host-memory pressure; start with at most one outstanding save. Measure actual ROCm compatibility and preserve verified publication/recovery before adopting. The tutorial alone does not establish Lab support. [DCP recipe](https://docs.pytorch.org/tutorials/recipes/distributed_async_checkpoint_recipe.html) |

A candidate execution pattern is a bounded shard pipeline: parallel independent
decode/transform work, then tokenize with the frozen tokenizer and pack under an
explicit boundary policy. Coordinate only necessary global operations, such as
exact deduplication and split/order inventories. For exact dedup, compare the
existing disk-backed index with hash partitioning plus external sort/merge;
verify collisions against content and preserve validation-first selection. This is
a design comparison, not a claim that those alternatives are implemented here.

Keep record/shard IDs and output order independent of worker completion order.
Specify shuffle seed, algorithm, buffer/shard policy and resume cursor explicitly;
approximate shuffle is not interchangeable with a full permutation. Bound queues
for backpressure, cap worker/prefetch memory, account for skewed shard sizes and
spill disk, and publish verified reusable binary outputs only after completion.
Packing boundaries and supervised-target coverage must remain comparable.

Use portable CPU dispatch and fallback rather than assuming one SIMD target;
benchmark AVX2-compatible paths on Zen 3, without requiring AVX-512. AMD's
[optimization guidance](https://gpuopen.com/gdc-presentations/2024/GDC2024_AMD_Ryzen_Processor_Software_Optimization.pdf)
discusses ISA requirements and SIMD transition costs. The
[TinyStories paper](https://arxiv.org/abs/2305.07759) motivates meaningful small-model
experiments; it does not forecast throughput for these recipes or hardware.

## Performance acceptance

Before calling the workflow ready, audit each stage for serial work, CPU/GPU
utilization, I/O wait, transfer bandwidth and repeated reads or copies. Separate
compute-bound work from storage, decoding, tokenization and synchronization stalls.
Use the real workload and record stage timings alongside end-to-end throughput.

Where concurrency can address an observed bottleneck, compare a serial baseline
with a small bounded range of worker counts, batch sizes or prefetch depths. Change
one control at a time within available RAM/VRAM and storage capacity. Record actual
throughput, latency, utilization and peak resource use; include contention and
setup overhead. Retain serial execution where it is faster or more predictable.
Do not assume every stage benefits from parallel execution.

Accept a faster configuration only when artifact verification, deterministic
ordering where required, supervised-target accounting, preparation reuse and
checkpoint recovery still pass. A batch or scientific-setting change requires an
explicitly separate configuration; it is not an equivalent execution comparison.

A material bottleneck is one that dominates elapsed time or prevents the declared
resource/throughput objective from being met. Record that objective before comparing
alternatives. Resolve a material avoidable bottleneck and remeasure the complete
workflow before declaring performance acceptance. If it remains unresolved, report
the measured limitation and leave performance acceptance incomplete. Report observed
improvement or regression; do not infer speedups from worker count or utilization.
Setup trials and bounded operational segments provide performance and recovery
evidence, not completion of the full scientific training budgets.

## Checkpoint recovery and transfer

A verified native full-state generation supports resume under compatible settings.
Full resume requires the same engine/backend, architecture, tokenizer/data,
optimizer, schedule horizon, budget, batch, sequence length and deterministic
settings. It creates a child run and preserves the parent. See the Lab
[checkpoint guide](https://github.com/supernovae/tiny-sparse-lab/blob/b3a1630ec09dbddae36301b0acef4122623ed939/docs/checkpointing.md).

Runtime/device drift may require explicit `--allow-runtime-drift` and records
best-effort continuation, not bitwise equivalence. ROCm-to-CUDA is not strict
resume. Supported `train --promote` uses compatible weights with fresh optimizer,
schedule, scaler, RNG, cursor and counters. Track its exposure as a separate run.

Request orderly interruption with Ctrl-C/SIGTERM and wait for exit. Abrupt loss
recovers only to the last durable generation. Record that step and observed lost
work; do not assume zero loss. Retain the previous good generation until its
replacement verifies. Explicit selection of a corrupt generation must fail;
`--recover` selection must remain visible in the run record.

Recipe export transfers declarations; it does not by itself transfer the entire
prepared-data and full-state checkpoint dependency set. This study does not yet
provide a validated end-to-end relocation command sequence. Remote and Colab
handoffs require verification on the receiving system with original paths
unavailable; treat them as unvalidated until that evidence exists.

For a transfer, retain incoming data separately until the inventory, member
lengths/digests and all recovery dependencies verify. Publish completion only
then. Partial uploads must not become ready inputs. Exercise corrupt/partial-copy
refusal on a disposable replica, never the sole retained copy. Perform data
transfer and verification before reserving paid GPU time; actual device readiness
still requires the target hardware.

Colab ephemeral storage is scratch. Persist and independently verify checkpoint
exports before relying on them after disconnect. The recovery point is the last
verified exported generation, which may lag local saves. Measure export latency
when choosing cadence. Metadata listing should remain separate from explicit cold
corpus verification; use a metadata-only path for browsing large inventories.
