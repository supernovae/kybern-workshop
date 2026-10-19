# Story Generation Prompt Panels

For the completed 8,192-update TinyStories baseline and all 27 generated story outputs, see:

- **Walkthrough & improvement exercises:** [`examples/tinystories-useful/README.md`](../tinystories-useful/README.md)
- **Recorded outputs & quality review:** [`results/2026-10-19-tinystories-cpu/README.md`](../../results/2026-10-19-tinystories-cpu/README.md)
- **Interactive reader on kybern.dev:** [TinyStories: build, read and improve a small story model](https://kybern.dev/models/tinystories-training/)

## Prompt Panel Declarations in This Directory

This folder retains three declarative prompt-panel definitions that can be rebound to any verified Tiny Sparse Lab checkpoint for side-by-side story evaluation:

| File | Decoding settings | Purpose |
| --- | --- | --- |
| [`story-greedy.json`](story-greedy.json) | `temperature: 0.0`, `top_k: 0`, `max_new_tokens: 192`, `seed: 42` | Deterministic continuations across 6 development story prefixes |
| [`story-sampled.json`](story-sampled.json) | `temperature: 0.7`, `top_k: 40`, `max_new_tokens: 192`, `seed: 42` | Sampled continuations across the same 6 prefixes |
| [`story-website-baseline.json`](story-website-baseline.json) | `temperature: 0.0`, `top_k: 0`, `max_new_tokens: 48`, `seed: 42` | Short 48-token continuations on the first 3 prefixes |

## Evaluation Rubric

When evaluating a new TinyStories checkpoint on the full 12-prompt panel (6 development + 6 held-out prefixes, greedy and sampled = 24 continuations at 192 tokens):

- **Target quality threshold:** at least 20/24 relevant, readable, and internally consistent story continuations (including at least 10/12 on the held-out prefixes) and 18/24 complete story endings.
- **Failure modes to check:** sentence-level repetition loops, character/object identity swaps (e.g., a red ball turning into a blue box), dropped prompt premises, and abrupt mid-sentence cutoffs.
- **Honest reporting:** retain all 24 outputs—including failures—alongside validation loss and perplexity so readers can compare actual generation behavior rather than cherry-picked samples.
