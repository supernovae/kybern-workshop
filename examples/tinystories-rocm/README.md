# TinyStories: bounded ROCm validation on WSL

**Prepared, not executed. Launch remains blocked on approved input transfer,
external review, whole-job supervision and writable-container qualification.**
RUN-13 established enumeration of one RX 7900 XTX, not training or VRAM monitoring.
This is the small two-arm validation requested for chief/Grok's runner. The later
2000/100-story, 120-main-update experiment is outside this recipe.

## Pins and supported path

`pins.json` binds Lab `2d5ba0fd66b6087101ad152fdbfe17b44ce194a5`, the already-cached
ROCm image digest `0842874b5eea67c0766b48f052335570e725145915d05df2ac568ed5365d70a5`,
Python 3.14.4 and Torch 2.14.0+rocm10.1.0 (HIP 7.16.26385). The image label and RUN-13 source fingerprint bind the installed source.
Provisioning or pulling an image requires separate authority.

The portable `experiment recipe workflow apply/resume` admission is CPU-only at
this pin. This separate recipe uses public native `campaign` commands, an explicit
ROCm runtime-acceptance profile, and runtime-bound ROCm evaluation. It does not
change Lab or the existing CPU recipe. The snapshot and tokenizer retain the CPUf identities from workflow commit
`3659786f9506c25d4d13088d0726cd990be7f0cc`. The packed cache was rebuilt offline
using this exact image after RUN15 exposed a source-identity mismatch; the plan
and Campaign bind the new identity recorded in `cache-rebuild/validation.json`.

## Aggregate limits

| Item | Exact declaration |
| --- | --- |
| Source | TinyStories `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`; 64 train / 16 validation stories |
| Model | seed 7; vocab 512; hidden 32; 1 layer; 2 heads; FP32 ROCm device 0 |
| Pair | baseline FFN 64; candidate FFN 96; serial execution |
| Training | each arm smoke 2 + warmup 5 + main 1; **16 aggregate updates**, 512 target positions |
| Evaluation | one batch per pass; conservative **24 aggregate batch ceiling**, 768 targets |
| Whole job | **1800 seconds**, including copying, checks, operator waits, commands, reporting and cleanup |
| Container resources | 12 GiB memory; zero swap; 2 CPUs; 256 PIDs |
| Observation | Tree RSS recorded without a kill threshold; 2 GiB added state; VRAM remains separate and unqualified |
| Downloads/retries | no fresh corpus or model downloads; no automatic retries |

The 24 evaluation batches are an upper bound from the pinned schedule, not a
measurement or a native aggregate counter. CPUf directly evidenced six batches.
Retain and audit actual counts; do not add `try`, probes, extra evaluations or arms.
The explicit schema-3 `command_policy: "observe_stages"` makes per-stage
`allowance_seconds`/job `wall_seconds` timing estimates observational. An overrun
is recorded in each job receipt and does not stop a healthy stage. Apply and
resume use a native wait of 1800 seconds, subordinate to the original whole-job clock;
it is not permission to start a new 30-minute clock at each command.

## Retained inputs and writable cache

Chief must bind the following retained inputs, including the newly prepared
source-compatible packed cache, in one immutable input directory. Keep the transfer manifest and source/destination verification receipts outside
the input root; chief binds the actual CPUf source root.

```text
inputs/
  source.lock.json
  parquet/train-00000-of-00004-2d5a1467fff1081b.parquet
  parquet/validation-00000-of-00001-869c898b519ad725.parquet
  snapshot/{manifest.json,train.jsonl,validation.jsonl}
  tokenizer/{tokenizer.json,tokenizer_manifest.json}
  packed/b0892750f1d1206ca5ddfc4a47ed3257bed54651146d3b8558e0321d280498fb/...
```

The Parquet files total 258720238 bytes; their exact sizes/SHA256 values are in
`first-files.json`. This path reuses the CPU snapshot/tokenizer and the separately rebuilt packed
artifact. It does not repeat source acquisition or tokenizer training. Both raw cached
files are authenticated as provenance. Do not fetch replacements if any retained
input is missing or invalid. Preserve native manifests; never repair their hashes.

Before binding or claiming a future GPU attempt, run the read-only check:

```sh
python3 examples/tinystories-rocm/handoff.py preflight --inputs /absolute/retained-inputs
```

The binder also runs this check before creating state/receipts. It authenticates
the bounded manifest bytes and both source identity fields against reviewed pins;
it does not replace cold native artifact verification. Staging additionally
compares the actual installed package identity before copying the cache. The
package-path-sha256-v2 identity is distinct from the Python-only runtime probe hash.
Neither a cache relabel nor an unauthenticated compatibility mapping is accepted.

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

## Docker supervision and binding

Use the reviewed lab-harness `docker_session.py` on an existing local Linux Docker
daemon with cgroup v2. It checks hard container limits, runs as the invoking
nonroot UID/GID and verifies owned-container cleanup. No user namespace, settings,
permission, service or security changes are needed. The offline image must already
be cached; there is no implicit pull. WSL GPU mapping is explicit `/dev/dxg` plus
read-only libdxcore, and remains blocked until separate real-job approval.

Run `bind_session.py bind --help` for required concrete inputs: clean reviewed
Workshop and harness checkouts, immutable inputs, fresh state and receipt roots,
the image's observed Python runtime identity JSON, boot ID, fresh job ID and real
owner approval provenance. The helper must run from the selected Workshop checkout.
Device mapping is opt-in via `bind --gpu`; omit it for GPU-free qualification.
The rendered `container_profile` is documentary: the harness fixes and verifies
its cgroup controls, including zero additional swap. The exact harness commit is
pinned at binding time and must be separately reviewed; PR #15 supplies this
implementation until merged.
It emits unexecuted schema-3 session/jobs and host wrapper argv with an exact
harness commit pin. Commit the generated files in the fresh state repository
before invoking the wrapper. Do not run the native argv independently.

The seven ordered slots share one 1800-second clock, including preflight and
operator waits. Submit copy-inputs, validate, apply, approve, run and status
individually using requests.json after inspecting each native result. Approve
only the actual pending gate under owner authority; a saved approval string is
not new authority. Require all 12 native stages COMPLETE after resume.

Bind report paths from actual native receipts during that same live session:

```sh
python3 examples/tinystories-rocm/bind_session.py report \
  --state /absolute/fresh-state --lock /actual/state/lock.json \
  --workspace /actual/state/workspace --index /actual/state/index.json
```

All three native paths must exist within the selected state root. This writes an
exclusive report.json job using the same pins/environment and hashes lock/index;
commit it, submit the returned report request, inspect the result, then submit
`{"finish":true}`. The public report command is `experiment recipe workflow report`,
with output `/state/audit/report.json`, captured by the session. No fresh container,
deadline or retry is created. Outputs, failures, immutable inputs and claims stay
local. Timeout/interruption stops the job and records partial evidence.

Before actual TinyStories execution, qualify tiny success, cancellation and
deadline fixtures on each intended host using the cached image, no GPU devices,
and the reviewed wrapper. A fake-engine unit test is not daemon qualification.

## Memory semantics and VRAM qualification

Docker cgroup memory/swap/CPU/PID settings apply to the container; external runner
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

`python3 -m unittest discover -s examples/tinystories-rocm -p 'test_*.py' -v`
uses only tiny filesystem fixtures and argument rendering. `check_native.py`, run
with the existing Lab environment and `PYTHONPATH` pointing to source `2d5ba0f`,
validates actual native schemas, exact two-arm budgets, evaluation authorization and
all five public CLI argument arrays; it never calls a parsed handler or probes GPUs.
RuntimeProfile validation substitutes the existing local Python path only for that
metadata fixture. GPU execution remains unrun; transfer and daemon qualification evidence is recorded separately by the runner.

## RUN15 cache correction

The native lock-input guard correctly rejected the CPUf packed cache because its
source identity differed from the execution image. Dataset, tokenizer and packing
settings matched. The approved remedy rebuilt only the small packed cache with
`sparselab data prepare` in the cached image, without GPU devices, training,
downloads or installations. Array bytes remained identical; source-bound cache
and manifest identities changed. Original caches, failed attempts and claims were
preserved. See `cache-rebuild/validation.json` for exact identities and outcomes.

Preparation used a 300-second outer ceiling (30 seconds reserved for cleanup),
hard container limits of 4 GiB memory including swap, 2 CPUs and 256 PIDs, and
network-none/read-only/nonroot execution. Retained-output observation was bounded
at 64 MiB (sampled, not a disk quota); harness logs/artifacts had finite limits.
Telemetry reported four tokenizer threads under the hard two-CPU quota. The first
read-only verification helper omitted required artifact metadata and failed after
preparation succeeded; that failure is retained. Corrected read-only verification
and staging checks passed without rebuilding or training. No new GPU attempt is
authorized by preparation, these checks, a PR or a merge.

Diagnostic stdout/stderr retention and artifact hashing stay bounded. In this
profile, exhausting their byte/entry/time budgets records incomplete evidence
without converting a successful process into an execution failure. Retained cache
files remain charged to the aggregate storage ledger, even if not fully hashed.
Unsafe paths, read/integrity errors, native nonzero exits, cancellation and the
whole-job deadline still stop the session. The final native report capture is
mandatory and must be complete. Older Harness versions refuse this explicit
policy field; unrelated recipes and standalone jobs retain strict limits.
No retry or new run is authorized by rendering or binding these specs.

The binder selects `memory_policy: "container_12g_observe_rss"`. Admission requires
24 GiB effective host RAM and 20 GiB available, leaving at least 8 GiB headroom.
The 12 GiB allocation is below half the observed 31.3 GiB WSL RAM; GPU capacity
is not counted as host RAM. The native monitor omits its duplicate tree-RSS stop.
Actual OOM/nonzero/signal outcomes and the original 1800-second deadline remain
fatal. Runtime readiness also requires Lab's native host-RAM detector to respect
cgroup total/headroom; the existing pinned image alone does not establish that
correction. Do not launch until the coordinated runtime is reviewed and pinned.
