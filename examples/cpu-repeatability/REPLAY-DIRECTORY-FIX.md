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
