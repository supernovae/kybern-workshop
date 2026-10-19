# Running the 4 GiB Preparation Pilot

[Back to Package Overview](README.md)

This guide covers the four-step initial pilot session defined by `pilot-session.template.json`, `pilot-contract.template.json`, `pilot-content.json`, and the templates in `pilot-jobs/`.

## Pilot Workflow Steps

1. **Prepare Environment & Runtime:**
   Use a Linux `amd64` container environment with Tiny Sparse Lab (`0af1683188edacecf0856baa3520354363358f0d` or newer, which includes ISO-8601 Parquet timestamp serialization). Verify at least 24 GiB available RAM, 310 GiB free disk space, and 100,000 free inodes.
2. **Capture Workspace Baseline:**
   ```sh
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
   - `pilot-acquire` — downloads the three pilot shards (`000-web.yaml`, `001-synthetic.yaml`, `002-code.yaml`, totaling 3.51 GiB) and stops when the fourth shard reservation exceeds the 4 GiB initial gate.
   - `pilot-budget-status` — records the transport ledger status and retained snapshot hashes for pilot review.

## Reference Pins

- **Tiny Sparse Lab commit:** `0af1683188edacecf0856baa3520354363358f0d`
- **Container image:** `ghcr.io/supernovae/tiny-sparse-lab@sha256:b56dc5b447503fd6f7e4aff7a208e8b225f102000da1b180d2586a732deffcd2`
- **Package manifest:** [`package-sha256.json`](package-sha256.json)
