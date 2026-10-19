# Running the 4 GiB Preparation Pilot

[Back to Package Overview](README.md)

This guide covers the four-step initial pilot session defined by `pilot-session.template.json`, `pilot-contract.template.json`, `pilot-content.json`, and the templates in `pilot-jobs/`.

## Pilot Workflow Steps

1. **Prepare Environment & Runtime:**
   Use a Linux `amd64` container environment with Tiny Sparse Lab (`0af1683188edacecf0856baa3520354363358f0d` or newer, which includes ISO-8601 Parquet timestamp serialization). Verify at least 24 GiB available RAM, 310 GiB free disk space, and 100,000 free inodes.
2. **Prepare Receipt Parent & Capture Workspace Baseline:**
   In the fresh private workspace, create the native phase receipt parent before the baseline. Validate that `$WORK` and its parents are real directories, not symlinks. Do not precreate harness session receipt roots.
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
   - `attempt-init` — initializes the zero-model preparation attempt contract.
   - `transport-init` — initializes the 4 GiB / 100 GiB transport budget ledger.
   - `pilot-acquire` — uses `project-pilot-acquire.json`, which selects only the three unchanged pilot declarations (`000-web.yaml`, `001-synthetic.yaml`, `002-code.yaml`, totaling 3,771,713,555 compressed bytes). It completes after those three sources if metadata and retries fit the cumulative 4 GiB initial gate; otherwise it refuses earlier. No fourth source is selected.
   - `pilot-budget-status` — records the transport ledger status and retained snapshot hashes for pilot review.

The native projected disk bound for this three-source project is 28,021,704,695 bytes (three 8 GiB expanded-output limits, the largest compressed shard, and 65,536 bytes of metadata). The 300 GiB workspace ceiling and approved deadline still apply. The remaining 523,253,741 bytes under the initial transfer gate cover metadata and any retries; they are not additional source allowance.

A changed project binding cannot reuse or reset an existing transport ledger. These templates do not authorize another attempt, refund failed reservations, extend a deadline, or release the gate. Keep prior histories and unfinished reservations intact; any future attempt needs its own explicit approval and cumulative accounting.

## Reference Pins

- **Tiny Sparse Lab commit:** `0af1683188edacecf0856baa3520354363358f0d`
- **Container image:** `ghcr.io/supernovae/tiny-sparse-lab@sha256:b56dc5b447503fd6f7e4aff7a208e8b225f102000da1b180d2586a732deffcd2`
- **Package manifest:** [`package-sha256.json`](package-sha256.json)

## Direct offline preview of the acquired pilot

After acquisition and budget reconciliation, use the `pilot-preview` phase in
`../preparation.json` with `PILOT_PREVIEW_DECLARATION` and
`PILOT_PREVIEW_INPUT_ROOT`. Render `preview.template.json` with independently
recorded exact manifest hashes/sizes. It pins the three retained data files and
snapshot IDs; input root is the existing acquisition work root, mounted read-only.
This route explicitly **defers pilot-reuse**: preview reads original snapshots
without creating the separate pilot view. Existing admission/draft phases still
use that view and are not implied by this route.

The declaration allows at most 16 GiB of aggregate input reads, 8 MiB per physical
record, 12 deterministic excerpts/source, 1 KiB/excerpt, 2 MiB total receipt bytes
and 530 seconds of cooperative work. Supervise it offline with a 600-second total
window including cleanup, 2 GiB sampled RSS stopping, and 64 MiB for all new job
files/logs/receipts. RSS is observed, not a hard cap. Preserve prior cumulative
charges and any earlier campaign deadline. Keep the declaration and job approval
bound to reviewed revisions; an example template does not authorize execution.

A successful preview verifies the pinned file bytes and row envelopes, with
bounded excerpts for human review. It does not make rights/admission decisions or
unlock tokenizer/training. Original snapshots and prior receipts remain untouched.
Use a Lab revision containing `corpus preview`; verify the actual imported module
and complete rendered job before launching. An older installed Lab must refuse
rather than silently falling back to admission inspection.

The companion `preview-session.template.json` and `preview-job.template.json`
provide one direct native command under the existing Harness CPU profile; they do
not initialize or reset a native attempt ledger. Use fresh session/job identities,
commit rendered jobs, and pass the retained acquisition work root with the existing
Docker supervisor `--inputs` mount (read-only at `/inputs`). The job deliberately
selects the reviewed Lab `src` working directory, so Python imports that exact
source revision while using dependencies from the immutable image. Validate the
wheel-distribution CLI on a tiny fixture in that image before real execution.
Pass the earlier inherited deadline and its boot ID to the outer supervisor;
600 seconds is an upper bound, never a deadline extension. The 64 MiB session cap
includes an 8 MiB shared receipt reserve; track any preparation files outside the
session separately against the same approved total and cumulative campaign budget.

The 600-second outer window reserves 30 seconds for cleanup and leaves startup
headroom around the 540-second job allowance (530 seconds cooperative preview).
This prevents an exact-fit slot from refusing after ordinary startup time.
