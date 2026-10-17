# Native metadata validation

Validated on 2026-10-17 using existing WSL Ubuntu-26.04 Python 3.14.4 and Lab commit `3dc40ab91afce4004b273b42e9a6ff349eeaf8a4` from [PR164](https://github.com/supernovae/tiny-sparse-lab/pull/164). That dependency was unmerged and under review at validation time; this is an immutable tested development pin, not a merged-release claim.

The exact invocation, stdout, stderr, nine generated configuration identities and resolved paths are in [metadata-validation.json](metadata-validation.json). Native `research scaffold` exited 0, and native configuration loading plus study planning confirmed nine distinct seed/architecture configurations and nine matched pairs. Only offline/smoke/CPU metadata was checked. Other scales remain unvalidated.

All nine main configurations retain the 32-update/4,096-target caps and explicit seeds 17/41/73. Their tokenizer and dataset paths resolve below the generated study, and their run root resolves below the explicit work directory. No tokenizer/data payload directory or run workspace was created. There was no acquisition, model loading, runtime probe, training, generation, capability evaluation or submission. The command may create native scratch metadata, which is not a run.

An initial metadata inspection without `--work-dir` exposed Lab's default user-data run-root binding. The public command was corrected to set the work root explicitly, then repeated successfully; neither invocation ran a model. Absolute paths in the retained evidence describe that inspection only and must not be reused as portable execution bindings.

Resource provenance checks confirm the only recipe semantic change is making the original implicit seed axis explicit at all four scales. The dataset selection is restricted to the unchanged offline profile; base, profiles, card and historical lifecycle registry retain original bytes. All archives remain unchanged. Lifecycle registry parsing is diagnostics only; referenced evidence closure, promotion and runtime permission are unverified.

This validates metadata authoring, not current execution readiness or useful-model quality. Runtime requires reviewed native dependency, generated and verified tokenizer/prepared data, full per-stage resource accounting, applicable lifecycle evidence and explicit approval.
