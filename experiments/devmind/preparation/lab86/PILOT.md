# Running the 4 GiB Preparation Pilot

[Back to Package Overview](README.md)

This guide walks through the four-step pilot session set up by `pilot-session.template.json`, `pilot-contract.template.json`, `pilot-content.json`, and the templates in `pilot-jobs/`.

## Pilot Workflow Steps

1. **Prepare Environment & Runtime:**
   Use a Linux `amd64` container environment with Tiny Sparse Lab (`0af1683188edacecf0856baa3520354363358f0d` or newer, which includes ISO-8601 Parquet timestamp serialization). Verify at least 24 GiB available RAM, 310 GiB free disk space, and 100,000 free inodes.
2. **Prepare Receipt Parent & Capture Workspace Baseline:**
   In a fresh private workspace, create the phase receipt directory before taking the baseline. Make sure `$WORK` and its parent directories are real directories rather than symlinks. Leave the harness session receipt directories for the harness to create.
   ```sh
   mkdir -m 700 -p "$WORK/phases/receipts"
   python -m sparselab monitor-baseline "$WORK" --output "$WORK/baseline.json" --json
   ```
   Bind the resulting baseline SHA-256 into `pilot-contract.template.json` alongside the SHA-256 of `pilot-content.json`.
3. **Render Session & Job Templates:**
   Substitute all `HOST_*` and `PACKAGE_ROOT` placeholders in `pilot-session.template.json` and `pilot-jobs/*.template.json`. Because `runtime` and `required_files` are JSON objects, materialize them from their JSON files before committing the rendered specs:
   ```python
   import json
   from pathlib import Path

   job = json.loads(rendered_job.read_text())
   for field in ("runtime", "required_files"):
       value = json.loads(Path(job[field]).read_text())
       if not isinstance(value, dict) or not value:
           raise ValueError(f"{field} requires a nonempty JSON object")
       job[field] = value
   with final_job.open("x") as stream:
       json.dump(job, stream, indent=2)
       stream.write("\n")
   ```
4. **Execute the Four Pilot Slots:**
   Run the four slots in sequence:
   - `attempt-init` — sets up the preparation attempt (no model runs).
   - `transport-init` — sets up the 4 GiB / 100 GiB download budget ledger.
   - `pilot-acquire` — uses `project-pilot-acquire.json`, which selects only the three unchanged pilot shard files (`000-web.yaml`, `001-synthetic.yaml`, `002-code.yaml`, 3,771,713,555 compressed bytes in total). It finishes after those three if metadata and retries fit inside the cumulative 4 GiB gate, and refuses earlier if they don't. It never selects a fourth source.
   - `pilot-budget-status` — records the ledger status and the snapshot hashes for the pilot review.

Lab projects at most 28,021,704,695 bytes of disk for this three-source project: three 8 GiB expanded-output limits, the largest compressed shard, and 65,536 bytes of metadata. The 300 GiB workspace ceiling and the approved deadline still apply. The remaining 523,253,741 bytes under the initial gate are for metadata and retries, not more source data.

If the project binding changes, it can't reuse or reset an existing ledger. Running these templates again needs a new approval: they don't refund failed reservations, extend a deadline or release the gate. Keep earlier histories and unfinished reservations as they are. Each future attempt needs its own approval and keeps counting against the same running total.

## Reference Pins

- **Tiny Sparse Lab commit:** `0af1683188edacecf0856baa3520354363358f0d`
- **Container image:** `ghcr.io/supernovae/tiny-sparse-lab@sha256:b56dc5b447503fd6f7e4aff7a208e8b225f102000da1b180d2586a732deffcd2`
- **Package manifest:** [`package-sha256.json`](package-sha256.json)

## Direct offline preview of the acquired pilot

After acquisition and budget reconciliation, use the `pilot-preview` phase in
`../preparation.json` with `PILOT_PREVIEW_DECLARATION` and
`PILOT_PREVIEW_INPUT_ROOT`. Fill `preview.template.json` with the exact manifest
hashes and sizes you recorded separately. It pins the three retained data files
and snapshot IDs. Each source names its text field: `text` for web and
synthetic, `code` for code. Preview has to support this per-source field and
hash the original row as-is, so don't rename or copy the acquired data. The
connected fixture loads these fields from the production acquisition project.
The input root is the existing acquisition work root, mounted read-only.
This route **skips pilot-reuse**: preview reads the original snapshots without
creating the separate pilot view. The existing admission and draft phases still
use that view, and this route doesn't run them.

The preview config allows at most 16 GiB of total input reads, 8 MiB per physical
record, 12 fixed excerpts per source, 1 KiB per excerpt, 2 MiB of receipts in
total and 530 seconds of cooperative work. Supervise it offline with a 600-second
total window including cleanup, a 2 GiB sampled RSS stop, and 64 MiB for all new
job files, logs and receipts. RSS is sampled, not a hard cap. Keep earlier
cumulative charges and any earlier campaign deadline. Tie the config and the job
approval to reviewed revisions; filling in the example template doesn't approve
a run.

A successful preview checks the pinned file bytes and row structure and gives you
short excerpts to review by hand. It makes no rights or admission decisions and
doesn't unlock tokenizer fitting or training. The original snapshots and earlier
receipts are left untouched. Use a Lab revision that has `corpus preview`, and
check the module that actually gets imported and the complete rendered job before
launching. An older Lab must refuse rather than fall back to admission inspection.

The companion `preview-session.template.json` and `preview-job.template.json`
run one Lab command under the existing Harness CPU profile. They don't create or
reset an attempt ledger. Use fresh session and job IDs, commit the rendered jobs,
and pass the retained acquisition work root with the existing Docker supervisor
`--inputs` mount (read-only at `/inputs`). The job runs from the reviewed Lab
`src` directory on purpose, so Python imports that exact source revision while
using the dependencies in the fixed image. Test the wheel-distribution CLI on a
tiny fixture in that image before the real run.
Pass the earlier inherited deadline and its boot ID to the outer supervisor. The
600 seconds is an upper limit and never extends that deadline. The 64 MiB session
cap includes an 8 MiB shared receipt reserve. Track any preparation files outside
the session separately, against the same approved total and the cumulative
campaign budget.

The 600-second outer window reserves 30 seconds for cleanup and leaves startup
headroom around the 540-second job allowance (530 seconds of cooperative
preview). That way an ordinary startup delay doesn't push an exactly sized slot
over its limit.
