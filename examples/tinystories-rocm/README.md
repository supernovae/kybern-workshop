# TinyStories: bounded ROCm validation on WSL

**Prepared, not executed. Launch remains blocked on approved input transfer,
external review, whole-job supervision and writable-container qualification.**
RUN-13 established enumeration of one RX 7900 XTX, not training or VRAM monitoring.
This is the small two-arm validation requested for chief/Grok's runner. The later
2000/100-story, 120-main-update experiment is outside this recipe.

## Pins and supported path

`pins.json` binds Lab `2d5ba0fd66b6087101ad152fdbfe17b44ce194a5`, the already-cached
ROCm image digest `0842874b5eea67c0766b48f052335570e725145915d05df2ac568ed5365d70a5`,
Python 3.14.4 and Torch 2.14.0+rocm10.1.0 (HIP 7.16.26385). The image label and
RUN-13 source fingerprint were inspected; no image/model/corpus was downloaded.

The portable `experiment recipe workflow apply/resume` admission is CPU-only at
this pin. This separate recipe uses public native `campaign` commands, an explicit
ROCm runtime-acceptance profile, and runtime-bound ROCm evaluation. It does not
change Lab or the existing CPU recipe. The plan and Campaign both carry the exact
artifact identities from reviewed CPU workflow commit
`3659786f9506c25d4d13088d0726cd990be7f0cc`, used by `LAB80-cpu-20261015f`.

## Aggregate limits

| Item | Exact declaration |
| --- | --- |
| Source | TinyStories `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`; 64 train / 16 validation stories |
| Model | seed 7; vocab 512; hidden 32; 1 layer; 2 heads; FP32 ROCm device 0 |
| Pair | baseline FFN 64; candidate FFN 96; serial execution |
| Training | each arm smoke 2 + warmup 5 + main 1; **16 aggregate updates**, 512 target positions |
| Evaluation | one batch per pass; conservative **24 aggregate batch ceiling**, 768 targets |
| Whole job | **1800 seconds**, including copying, checks, operator waits, commands, reporting and cleanup |
| Container resources | 4 GiB memory; memory+swap total 4 GiB; 2 CPUs; 256 PIDs |
| Observation | 4 GiB tree RSS; 2 GiB added state; optional qualified 8 GiB whole-device VRAM stop threshold |
| Downloads/retries | no fresh corpus or model downloads; no automatic retries |

The 24 evaluation batches are an upper bound from the pinned schedule, not a
measurement or a native aggregate counter. CPUf directly evidenced six batches.
Retain and audit actual counts; do not add `try`, probes, extra evaluations or arms.
The native run wait of 1740 seconds is subordinate to the original whole-job clock;
it is not permission to start a new 30-minute clock at each command.

## Retained inputs and writable cache

Chief must arrange an approved transfer of the following retained CPUf artifacts
into one immutable input directory. They were not accessible in this workspace;
The owner explicitly approved copying these retained inputs in Sentinel_cf76ba978d588191bac9548724438197 at 2026-10-16T00:14:42Z. No transfer or data acquisition was performed here; chief resolves the actual CPUf source root.

```text
inputs/
  source.lock.json
  parquet/train-00000-of-00004-2d5a1467fff1081b.parquet
  parquet/validation-00000-of-00001-869c898b519ad725.parquet
  snapshot/{manifest.json,train.jsonl,validation.jsonl}
  tokenizer/{tokenizer.json,tokenizer_manifest.json}
  packed/b7af269e44c026cd6f7c0f0c0c9a1ab5334344d1e4c50b51327b10d70131636c/...
```

The Parquet files total 258720238 bytes; their exact sizes/SHA256 values are in
`first-files.json`. This path reuses the already prepared CPU snapshot/tokenizer
and packed artifact, rather than repeating source preparation. Both raw cached
files are authenticated as provenance. Do not fetch replacements if any retained
input is missing or invalid. Preserve native manifests; never repair their hashes.

Before transfer, chief produces the exact byte manifest outside the staged input root:

```sh
python3 examples/tinystories-rocm/handoff.py transfer-manifest \
  --inputs /absolute/approved-retained-cpuf-inputs \
  --output /absolute/evidence/transfer-manifest.json
```

The returned SHA256 seals that manifest; its entries give each relative destination
path, size and byte SHA256. Copy those files independently to the same relative
paths on the GPU runner, verify every destination against this manifest, and retain
both the manifest and returned hash. This operation only reads inputs and writes
new metadata. It neither transfers data nor replaces native identity validation.
Actual CPU source paths and their byte manifest cannot be asserted before chief
binds the retained root. `first-files.json` and the typed identities in
`campaign.json` are the exact pre-existing digest authorities, not invented hashes.

The inputs mount is read-only. `handoff.py stage` authenticates the source lock,
raw files and snapshot, copies only the packed artifact to a fresh writable
`/state/cache/<original-identifier>`, then uses native cold artifact verification.
It bounds traversal, rejects symlinks/nonregular files, refuses an existing cache,
and leaves partial evidence on failure. Copies have independent bytes; original
permissions/ownership are not changed. Snapshot and tokenizer remain read-only.
The cache parent must stay writable for `.cleanup.lock` and preparation receipts.
No old admissions, Campaign state, claims or attempt ledgers are copied.

## WSL invocation and current qualification blocker

The rendered argv retains RUN-13's `/dev/dxg` and read-only
`/usr/lib/wsl/lib/libdxcore.so` to `/usr/lib/libdxcore.so` mapping. It does not mount
host ROCm libraries, `/dev/kfd`, `/dev/dri`, or add privileged/security overrides.
It uses `--pull=never`, `--network=none`, and explicit device visibility `0`.

The image defaults to UID 10001. The candidate writable mapping uses rootless
`--userns=keep-id --user=<host-uid>:<host-gid>`, without host permission changes.
**This mapping is not qualified:** one bounded, GPU-free stdlib file-write fixture
on the cached image timed out during Podman startup before a container ID existed.
A follow-up query reported no such container and an incomplete storage layer;
further `podman info` stalled. Saved `argv.json` shows a direct Python subprocess argument array (`shell=False`), and binary resolution is `/usr/bin/podman`; a separate metadata-only query also stalled. Evidence points to Podman startup/storage handling, not command quoting or shell interception. The exact storage cause remains unconfirmed. Only this task's identified diagnostic processes
were stopped. No GPU devices were exposed, and no container-write success or
verified full storage cleanup is claimed. No further container probes were run.
Chief must resolve/qualify this through the existing runner before launch; do not
change device permissions, security policy, or WSL settings to bypass the blocker.

The repository mount must be a **clean standalone checkout** of the externally
reviewed Workshop commit, with its own `.git` directory and no external Git
alternates. Mounting a linked worktree alone breaks native declaration provenance.
Use an existing qualified whole-job supervisor, not independent per-step timeouts.
It must own a fresh job/claim and output directory, preserve holds and history,
retain stdout/stderr/real outcomes, inspect each owned container and verify cleanup.
`handoff.py` is a renderer/copy helper, not an executor, scheduler or claim manager.

## Render and execute only after qualification

Run the renderer with the real reviewed SHA and actual approval reference:

```sh
python3 examples/tinystories-rocm/handoff.py render \
  --checkout /absolute/standalone-reviewed-workshop \
  --inputs /absolute/approved-retained-cpuf-inputs \
  --state /absolute/fresh-job-output --job-id fresh-chief-assigned-id \
  --reviewed-commit ACTUAL_REVIEWED_40_HEX_SHA \
  --approval-reference ACTUAL_OWNER_APPROVAL_REFERENCE
```

It returns exact argument arrays with `execution_enabled: false`; never join them
into shell text. The supervisor checks checkout/image/source pins and existing
claims, creates the fresh state root after admission, and keeps one origin/deadline.
The sequence is copy-inputs, Campaign validate, apply (without execution), approve
`approve-model`, resume with `--execute-runs`, then status. Approve only the actual
pending gate with the owner-approved assignment. Every native state must be checked,
not just the process exit. After resume require all 12 stages COMPLETE. Any failure,
interruption, timeout or still-running state stops the job; no automatic resume/retry.

After the final collection, use the real lock/workspace/index from native receipts
with the same supervised container prefix and a fresh owned `JOB-report` name:

```json
["sparselab", "experiment", "recipe", "workflow", "report", "LOCK_FROM_RECEIPT", "--workspace", "WORKSPACE_FROM_RECEIPT", "--index", "INDEX_FROM_RECEIPT", "--output", "/state/report.json", "--json"]
```

This report command is read-only native evidence handling and does not use CPU-only
execution admission. Report paths cannot be known before their native receipts.
Keep reports, both arm outcomes, actual budgets and supervisor evidence locally;
this recipe posts nothing to GitHub/Notion and does not schedule the larger run.

## Memory semantics and VRAM qualification

Podman cgroup memory/swap/CPU/PID settings apply to the container; external runner
helpers still need the supervisor's own resource accounting. Inspect actual applied
limits and OOM state. `monitor.json` is a native observation policy, not an OS quota
or a multi-command supervisor. RSS/storage sampling can overshoot between samples.

The 8 GiB VRAM threshold is conditional on a working **UUID-bound AMD SMI sensor**.
Torch enumeration is insufficient; PyTorch allocator statistics are not whole-device
VRAM. No sensor probe/install was performed here. If chief qualifies the existing
sensor, bind `max_device_memory_bytes: 8589934592` and the actual
`expected_device_uuid` into a fresh native policy and require its prelaunch read.
The policy refuses a missing/failed sensor; never silently remove a requested field.
If unavailable, record VRAM observation unavailable and the optional threshold
unenforced. No cgroup, driver, permission or security settings are changed here.

## Validation

`python3 -m unittest discover -s examples/tinystories-rocm -p test_handoff.py -v`
uses only tiny filesystem fixtures and argument rendering. `check_native.py`, run
with the existing Lab environment and `PYTHONPATH` pointing to source `2d5ba0f`,
validates actual native schemas, exact two-arm budgets, evaluation authorization and
all five public CLI argument arrays; it never calls a parsed handler or probes GPUs.
RuntimeProfile validation substitutes the existing local Python path only for that
metadata fixture. Real CPUf payload verification and GPU execution remain unrun.
