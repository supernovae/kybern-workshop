# DevMind340MBase scientific protocol

Proposed, awaiting review and measured inputs.

Sources: [EXP-1 science card](https://app.notion.com/p/3f63b68cca2281cc8659d12bd8aa9d2c)
and its [design revision](https://app.notion.com/p/3fb3b68cca2281ca8275d2733b1aaa65),
read 2026-10-17. The source explicitly labels training hyperparameters, cadence
and thresholds provisional. Software authoring approval does not approve them
scientifically or authorize execution.

## Architecture and parameter convention

`model.json` declares 24 layers, hidden width 1024, 16 full attention heads,
SwiGLU intermediate width 2816, RMSNorm, RoPE, vocabulary 32768 with tied
embeddings, dense causal attention and context 2048. No lexical memory or MoE.
The bias-free native tensor inventory convention counts shared embeddings once:
33,554,432 embeddings + 100,663,296 attention + 207,618,048 FFN + 50,176 norms
= **341,885,952 parameters**. This matches the existing native shape-only `named_tensor_inventory` result
(219 tensor specifications, one tied alias); no model or tensor was allocated.
Tied output-head aliases must not be counted twice.

## Fresh preparation

The latest approved fresh preparation supersedes DevMind reuse and the old six
semantic quotas: 60% educational web, 20% synthetic, 20% code by usable TRAIN
targets; conditional 12B unique usable-target goal, no silent repetition.
Source declarations and rights quarantine are in `preparation/lab86/`.
Fresh BPE vocabulary 32768, at most 512 MiB TRAIN fit with matching 60/20/20 byte
sampling; source-family split 98/1/1; heldout tokenizer audit; context 2048,
int32 packing; maximum exposure one in the prepared unique mixture.
Measured yields, family counts, deduplication, English coverage and rights may
still block release. Preserve Cosmopedia's coarse seed family until reviewed;
never replace it with invented per-prompt families just to pass split checks.
The initial 4 GiB transfer gate requires an explicit report-bound review before
continuation. Transfer retries do not create fresh budgets. Private quarantine
is not publication permission.

## Training proposal

Seed 42, BF16 on a separately qualified supported runtime; FP32 optimizer state,
transformer-block activation checkpointing, no offload initially. AdamW parameters
are in `optimizer.json`: peak 0.0006, floor 0.00006, betas 0.9/0.95, epsilon 1e-8,
weight decay 0.1; gradient clip 1.0; dropout zero. The inspected native `training.optimizer.make_optimizer` excludes nontrainable
and duplicate parameter identities, applies decay to tensors with rank at least
two, and zero decay to lower ranks (including RMSNorm). Pin that implementation
with the eventual reviewed runtime.
Nominal microbatch 2, accumulation 32, context 2048 gives 131072 targets/update
only when masks/packing actually produce all targets. Preserve effective batch
if changing microbatch for fit. Warm up for 1000 updates, then native cosine to
the reviewed 30x endpoint. A later approved extension preserves full state at
the floor without restarting warmup; it is not included in this allocation.

Scientific milestones at 5/10/15/20/25/30 targets per parameter correspond to
1,709,429,760 / 3,418,859,520 / 5,128,289,280 / 6,837,719,040 /
8,547,148,800 / 10,256,578,560 targets. These are arithmetic boundaries, not
measured committed targets or automatically executable whole-update caps.
Freeze rounding and actual masks using native committed-target accounting.
5x and 10x are intermediate diagnostics; 20–30x is the substantive initial
planning region. 50x/100x are forecasts for possible separately approved
extensions, not authorized endpoints or claims of saturation.

Proposed fast validation every 256 updates: fixed English and technical panels,
262144 targets each. Full lane validation and public benchmarks at scientific
milestones. Proposed full-state recovery every 1024 updates; retain scientific
milestones, latest, previous, validation-best and terminal. Bind native retention
byte caps from real measured checkpoint size and permitted storage, including
write headroom. Preserve optimizer, scheduler, RNG, cursor and committed targets.
Do not invent caps to make a configuration parse.

## Evaluation and decisions

Proposed upstream lm-evaluation-harness revision:
`d6de81643928d653435c431bae19945d41d32520`. Full official splits, zero-shot,
no chat template or generative-answer substitute. Primary metrics separately:
LAMBADA OpenAI accuracy, HellaSwag acc_norm, ARC-Easy acc_norm. Supporting:
PIQA and SciQ acc/acc_norm; SciQ uses the upstream support-passage prompt.
No invented aggregate mean. Freeze dataset revisions, item counts, prompt and
scoring identities, context and per-item records before execution. SciQ access
and intended license use need review; a task definition is not data permission.
Evaluation seed 42; proposed paired-bootstrap seed 1234. Preserve official
standard errors and report incomplete items. Public repeated looks are
developmental evidence; final private holdout stays closed.

Proposed completion diagnostic: fixed 64 prompts covering English, technical,
code and incidents, greedy decoding, at most 128 new tokens. Actual prompt set
is missing. Bespoke sensemaking tasks are also not yet frozen. Same-size external
models SmolLM2-360M and Pythia-410M are possible capability references, not local
artifacts or approved downloads. Align evaluation settings and disclose unequal
pretraining budgets. Causal variant claims require matched internal controls.

For review: worthwhile gain 0.005 nats/token per additional billion targets on
English or technical heldout objective, or 0.5 percentage point per billion on
a preregistered primary capability. Two successive sufficiently precise intervals
below frozen thresholds may support diminishing returns under this recipe.
Imprecision is inconclusive; useful gains at 30x mean saturation was not
established within budget. Stop for invalid lineage/evaluation, instability,
material regression or exhausted budget. Thresholds must be reviewed before
outcomes, not selected retrospectively.

Record targets and measured device-hours/compute/cost to each observed capability
threshold, crossing brackets, fixed-token/fixed-compute curves, and separate
training versus end-to-end overhead. Unknown cost remains unknown. Local MODEL-0
throughput is not a 340M forecast. No seed sweep, SFT or memory variant is silently
included. Optional SFT is a separate later recipe with base-retention evaluation.

## Still required

Scientific approval of proposals; measured source/English/token supply; immutable
release, tokenizer and packed input receipts; evaluation datasets/prompts/rights;
exact update and scheduler horizon; finite
runtime and retention budget from actual capacity; explicit execution approval.
These are concrete missing decisions/artifacts, not evidence of failed science.
