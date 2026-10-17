# Historical offline sample guides

This supplement preserves three exact Lab guides before any later sample
retirement or tutorial rewrite:

- [Experiment programs](../provenance/lab/docs/experiment-programs.md)
- [Experiments](../provenance/lab/docs/experiments.md)
- [Sample directory guide](../provenance/lab/experiments/samples/README.md)

The [scoped manifest](../provenance/lab-sample-guides-manifest.json) records Lab
source commit `faf415e3754f4018674a734547c66df7ddca8333`, original paths, destination
paths, Git blob identities, byte lengths and SHA-256 values. No exact or partial
same-path copy existed in Workshop main
`1aa84218a95fabafc96f2cc7d667c0c969eb8d5e` before this supplement.

The three training-program YAML files, corpus-shape-fraction.yaml and
heldout-suite.yaml were already preserved in the stage-two manifest. All five
current Lab files were compared again with those archived bytes and hashes;
none are copied again or changed here.

Archived commands, resource budgets and host paths describe historical examples.
They are not current Lab guarantees, executable recipe delivery or authority to
run anything. Internal links retain the original Lab-relative layout and may
refer to files outside the preserved subset. Original bytes remain unchanged;
current authoring follows [the contribution policy](../CONTRIBUTING.md).

## Static consumer audit at the source pin

The five YAML paths and sample IDs are referenced by these three guides and by
the two sample plans that share the held-out suite. No direct path or ID consumers
were found in src/, tests/ or .github/. The workspace-hygiene test explicitly
reads the sample README and requires its external-resource authoring guidance;
a later rewrite must retain that generic contract.

The experiment-plan, direct-input and comparison-phase tests construct temporary
neutral declarations rather than discovering these samples. The reviewed research
lint discovery is scoped to experiments/research, not experiments/samples. Runtime
experiment-directory references belong to run stores, not repository sample
loading. This is a static source audit, not an execution or exhaustive runtime
proof.

A later coordinated Lab change can retire the five declarations together and
replace sample-specific guide commands with explicit external current inputs,
while retaining the workspace-hygiene contract and generic native API guidance.
That change is blocked until this preservation lands. This PR makes no Lab edits,
current recipe adaptations, schema changes or runtime calls.
