# DevMind 340M Base: Scientific Protocol

[Back to DevMind Overview](README.md) · [DevMind Pilot Status (kybern.dev)](https://kybern.dev/models/devmind/)

This document defines the architecture, corpus preparation mixture, training schedule, and evaluation protocol for **DevMind 340M Base**.

## 1. Model Architecture

[`model.json`](model.json) specifies a dense causal transformer decoder:

- **Dimensions:** 24 layers, hidden dimension 1,024, 16 attention heads, SwiGLU intermediate width 2,816, RMSNorm, RoPE, context length 2,048.
- **Vocabulary:** 32,768 tokens with tied input/output embeddings.
- **Parameter count:** **341,885,952 parameters** (33,554,432 embeddings + 100,663,296 attention + 207,618,048 FFN + 50,176 norms across 219 tensors, counting tied embeddings once).

## 2. Corpus Mixture & Preparation

Source declarations and filtering policies live in [`preparation/lab86/`](preparation/lab86/README.md):

- **Target training mixture:** 60% educational web (`HuggingFaceTB/smollm-corpus` FineWeb-Edu), 20% synthetic textbooks/stories (`cosmopedia-v2`), and 20% permissively licensed code (`codeparrot/github-code-clean`).
- **Deduplication & splitting:** exact and canonical deduplication plus family clustering (grouping repositories and seed families) prior to a frozen **98% train / 1% validation / 1% test** split, requiring at least 100 distinct families per stratum.
- **Tokenizer:** byte-level BPE with 32,768 vocabulary trained on up to 512 MiB of `TRAIN` text sampled at 60/20/20 across the three streams, audited on at least 1,000 unseen `TRAIN` documents per stream.
- **Packing & exposure:** sequences packed to length 2,048 (`int32` tokens) with `max_exposures: 1` (up to 12B unique training tokens without silent repetition).
- **Pilot gate:** acquisition starts with a 4 GiB pilot across three candidate shards (one web, one synthetic, one code) to verify schema, license filtering, family counts, and token yield before full corpus acquisition.

## 3. Training Schedule & Optimizer

- **Precision & runtime:** Seed 42, BF16 training with FP32 optimizer state and transformer-block activation checkpointing.
- **Optimizer ([`optimizer.json`](optimizer.json)):** AdamW with peak learning rate `6e-4`, cosine decay to `6e-5` floor, $\beta_1 = 0.9$, $\beta_2 = 0.95$, $\epsilon = 10^{-8}$, weight decay `0.1` on rank $\ge 2$ tensors (zero weight decay on norms/biases), gradient clipping `1.0`, dropout `0.0`.
- **Batching:** Microbatch 2 × gradient accumulation 32 × sequence length 2,048 = **131,072 target tokens per update**, with 1,000 warmup updates.
- **Token-to-parameter milestones:** Evaluated at 5×, 10×, 15×, 20×, 25×, and 30× tokens per parameter (`1.71B` to `10.26B` target tokens), with fast validation every 256 updates (262,144 targets each on fixed English and technical validation panels) and full-state checkpoints every 1,024 updates.

## 4. Evaluation Protocol

- **Zero-shot benchmarks (`lm-evaluation-harness` `d6de81643928d653435c431bae19945d41d32520`):**
  - **Primary metrics (reported separately):** LAMBADA OpenAI (`acc`), HellaSwag (`acc_norm`), ARC-Easy (`acc_norm`).
  - **Supporting metrics:** PIQA (`acc` / `acc_norm`) and SciQ (`acc` / `acc_norm`).
- **Completion diagnostics:** Fixed 64-prompt panel spanning general English, technical explanations, code completion, and incident debugging (greedy decoding, up to 128 new tokens).
- **Reference comparisons:** Compare capability curves against similarly sized open models (such as SmolLM2-360M and Pythia-410M) with pretraining token budgets explicitly noted.
- **Stopping & scaling rule:** Track held-out NLL improvement (target $\ge 0.005$ nats/token per additional billion tokens) and primary benchmark gains ($\ge 0.5$ percentage points per billion tokens) across milestones.
