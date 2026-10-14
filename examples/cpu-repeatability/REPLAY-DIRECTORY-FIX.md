# Exact replay audit directory allowance

Native monitor creates its log directory exclusively. A before/after whole-root
inventory therefore gains `logs/replay` as well as the explicitly named files
inside it. The prior checker allowed the file prefix but rejected that directory.

Pass `--new-audit-path logs/replay` alongside one `--new-audit-path` for each
new replay log and report. The directory must be new and captured as a directory.
This is an exact entry allowance, never a recursive exclusion: an unlisted child,
changed existing file, changed raw database rows, unrelated path, symlink, or
special entry still refuses. Existing capture symlink refusal remains unchanged.

Validation used Python 3.14.4 on Ubuntu 26.04 under WSL2, with installed tools.
Seven focused inventory tests passed; the complete bounded suite passed 50 tests
in 1.951 seconds. No Lab execution, installation, or evidence modification occurred.
See replay-directory-test-evidence.txt and replay-directory-validation.json.

Read-only reproduction against retained A inventories: old checker refuses both
the original eight audit files and the nine-entry list including the directory.
New checker still refuses the eight-file list, and accepts only the exact nine
entries. Existing files and database rows are identical. All 509 retained file
hashes matched before and after validation. This post-stop check does not rewrite
the failed session outcome, prove absence of transient work, or establish B repeat
success. A fresh authorized iteration remains gated on external review and merge.

## Review follow-up

Review 5526075626 identified that the original lookalike probes were rejected by
presence checks rather than directory exactness. New filesystem cases create
after-only `logs/replay-other` and `logs` (with no logs directory before), name
each explicitly, and require `invalid new audit path`.

The suite now passes 53 tests in 1.704 seconds (10 inventory tests). Disposable-copy
mutations broadening to the replay prefix or adding the parent logs directory both
fail assertion checks. Crafted present-after traversal and noncanonical keys
independently kill removal of those guards. Absolute-path removal still survives:
the allowed relative prefixes already refuse absolute names on this platform.
The absolute refusal is tested, but no independent mutation coverage is claimed.
Non-dictionary audit entries now refuse cleanly with ValueError.

Reproduce using the existing interpreter with
`python -B examples/cpu-repeatability/tests/mutation_replay_directory.py`.
It mutates disposable copies only, caps each mutant at 15 seconds and the full
suite at 60 seconds, and refreshes the two test/mutation evidence files. No Lab
workload, native verification or retained attempt evidence access is performed.
