# TinyStories recipes

Start with the [native TinyStories microlab](../tinystories-microlab/README.md):
pinned declarations, train-only tokenizer, FFN-width comparison, native report
and explicit metadata validation. It uses Lab directly, with no Workshop Python
or internal runner prerequisite. The 40-update teaching run is not a useful-story
quality claim; see the separate [usable-story proposal](../tinystories-microlab/usable-story-proposal.md).

The earlier [PR17 GPU walkthrough](https://github.com/supernovae/kybern-workshop/blob/521f7c72cc1f17a6285696106a6f1af5a02788a0/examples/tinystories/README.md)
remains in Git history. It described a different 64/16-story, width-32 smoke,
including old runtime pins and an inline config-copy snippet. Those historical
operator steps are not the new declarative recipe or a current GPU qualification.
The [recorded CPU smoke](../../results/2026-10-15-tinystories-smoke/README.md)
remains evidence of that specific execution, not of the new recipe or story quality.
