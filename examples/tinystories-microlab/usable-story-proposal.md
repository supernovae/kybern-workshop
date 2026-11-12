# Story Generation Prompt Panels

The completed 8,192-update TinyStories baseline and its 27 generated stories are here:

- **Walkthrough & improvement exercises:** [`examples/tinystories-useful/README.md`](../tinystories-useful/README.md)
- **Recorded outputs & quality review:** [`results/2026-10-19-tinystories-cpu/README.md`](../../results/2026-10-19-tinystories-cpu/README.md)
- **Interactive reader on kybern.dev:** [TinyStories: build, read and improve a small story model](https://kybern.dev/models/tinystories-training/)

## Prompt Panel Declarations in This Directory

This folder has three prompt-panel files. Point them at any Kybern Model Lab checkpoint to compare stories side by side:

| File | Decoding settings | Purpose |
| --- | --- | --- |
| [`story-greedy.json`](story-greedy.json) | `temperature: 0.0`, `top_k: 0`, `max_new_tokens: 192`, `seed: 42` | Deterministic continuations across 6 development story prefixes |
| [`story-sampled.json`](story-sampled.json) | `temperature: 0.7`, `top_k: 40`, `max_new_tokens: 192`, `seed: 42` | Sampled continuations across the same 6 prefixes |
| [`story-website-baseline.json`](story-website-baseline.json) | `temperature: 0.0`, `top_k: 0`, `max_new_tokens: 48`, `seed: 42` | Short 48-token continuations on the first 3 prefixes |

## Evaluation Rubric

To score a new TinyStories checkpoint, use the full 12-prompt panel: 6 development and 6 held-out prefixes, each decoded greedy and sampled, for 24 continuations of 192 tokens.

- **Target:** at least 20 of 24 continuations that are relevant, readable, and consistent (with at least 10 of 12 on the held-out prefixes), and at least 18 of 24 that reach a complete ending.
- **Failures to look for:** sentences repeating in loops, characters or objects swapping (a red ball turning into a blue box), the prompt's setup getting dropped, and stories cut off mid-sentence.
- **Reporting:** keep all 24 outputs, failures included, next to the validation loss and perplexity, so readers see what the model really writes.
