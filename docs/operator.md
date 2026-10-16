# Run an approved Workshop experiment

Notion owns experiment planning, ordering and assignment. Workshop owns the
committed scientific recipe, runtime configuration, operator commands and output
links. Installed Lab supplies Campaign execution, scientific components and native
evidence/report verification. Harness supervises the single bounded process tree.
There is no Notion client, polling, scheduler, credential setup or automatic retry.

Use `scripts/workshop.py` for a native Campaign with already prepared local inputs.
This is the existing Linux/WSL local Docker schema-3 path: one root, seven outer
steps, one explicitly selected approval gate, one experiment plan and one terminal
collection. Native Campaign owns all scientific dependencies inside those steps.
The Docker supervisor still supports its existing pinned ROCm image, CPU quota of
2 and PID limit of 256. The template defaults to an 1800-second overall deadline.
With the companion Harness finite-deadline change, an explicitly approved longer
`limits.wall_seconds` is passed through unchanged, including the cleanup reserve.
Older Harness revisions refuse extended durations; the companion
[Harness PR19](https://github.com/supernovae/lab-harness/pull/19) supplies this
capability. Use its reviewed final revision for longer runs. This does not add
portable GPU admission, another backend, unbounded durations or automatic preparation.
The existing local CLI guides and TinyStories-specific binder remain available.

## Author and bind

Put `campaign.json`, its referenced plan/run/suite files and runtime profile in the
Workshop checkout. Change supported model settings, comparison cells, training
budgets and dependencies in those declarations; the adapter has no width, seed,
update-count or cell-count constants. Native validators decide supported science.
Keep the single approval gate and terminal collection explicit. Multiple plans,
multiple approval gates and ambiguous terminal evidence are outside this slice.

Use existing prepared inputs. The generic `copy-inputs` step copies the mounted
input directory to `<state>/inputs`, preserving its relative layout. Author native
artifact locations accordingly (`/state/inputs/...` inside this Docker profile),
or reference read-only `/inputs/...` when the native component supports it. It does
not infer or rewrite artifact identities, rebuild caches or download missing data.
The TinyStories-specific `/state/cache` staging convention is unchanged in its
original binder; do not feed that recipe unchanged to this generic staging layout.

The templates under `examples/operator` reuse Harness's existing session/job
shapes. Their placeholder identities are not runnable specs or authority. Bind
copies only session limits/slots/policies and job limits; all identity, approval,
source, runtime and command fields are freshly supplied/generated. Edit resource
budgets explicitly before binding; unsupported values are refused by Harness.
The provided memory profile enforces 12 GiB cgroup RAM with zero swap, requires
24 GiB effective host RAM and 20 GiB available, and records aggregate RSS without
a separate RSS stop. No hard disk or VRAM limit is implied.

The following is an unexecuted command pattern. Replace paths, full commit hashes,
observed runtime identity, interpreter and actual approval reference. Record a
stable Notion experiment ID separately from this fresh attempt ID. The Notion ID
is provenance, not permission; approvals cover the exact reviewed recipe/budget.

```sh
python3 -B scripts/workshop.py bind \
  --checkout /absolute/workshop --commit FULL_WORKSHOP_SHA \
  --harness /absolute/harness --harness-commit FULL_HARNESS_SHA \
  --campaign /absolute/workshop/studies/example/campaign.json \
  --profile /absolute/workshop/studies/example/runtime.json \
  --inputs /absolute/prepared-inputs \
  --state /absolute/attempt/state --receipts /absolute/attempt/receipts \
  --runtime /absolute/observed-runtime.json --python /opt/venv/bin/python \
  --session-template examples/operator/session-template.json \
  --job-template examples/operator/job-template.json \
  --experiment EXP-123 --attempt exp123-attempt01 \
  --owner OWNER --approval ACTUAL_APPROVAL_REFERENCE --approval-stage approve-model
```

The parent of fresh state/receipt directories must exist. The adapter requires
clean pinned checkouts; neither it nor its imported staging helper is hot-loaded
from an unreviewed location. Binding writes specs only. Review them, initialize a
Git repository in state and commit the generated JSON files using your configured
Git identity. Runtime identity must be an existing observed identity for the
cached image. Do not manufacture it from the example placeholders.

## Execute exactly once

After assignment and approval, invoke the pinned adapter from its clean checkout:

```sh
python3 -B scripts/workshop.py run --state /absolute/attempt/state \
  --harness /absolute/harness --harness-commit FULL_HARNESS_SHA \
  --inputs /absolute/prepared-inputs --image EXISTING_SUPPORTED_IMAGE_DIGEST --gpu
```

The adapter records a permanent `.workshop-driver` marker, starts one Harness
wrapper and drives copy, validate, apply, the selected approval, resume, status,
report and finish on that same live deadline. It approves only the declared gate
when native apply reports `AWAITING_APPROVAL`, using the supplied actual owner
reference. Exit zero with incomplete native stages stops the sequence. There is no
retry or fresh deadline. Native errors and interruption request stop, then terminate a stuck wrapper.
A wrapper that still ignores shutdown is killed and reaped; the result explicitly
marks container cleanup unverified in that exceptional case. Inspect host/receipts
before further work; no claim is stolen or automatically retried. The wrapper
normally owns container cleanup and its retained evidence remains authoritative.

The report lock/workspace/index come from the actual complete native status,
not guessed filenames. The adapter writes and commits `report.json` in the state
repository (configured Git identity required), then captures the native report at
`<state>/audit/report.json`. It uses the same declared path in the command and
capture, fixing the former `/state` versus host-path envelope mismatch.

## Inspect outputs even when the session fails

```sh
python3 -B scripts/workshop.py status --state /absolute/attempt/state
python3 -B scripts/workshop.py results --state /absolute/attempt/state
```

Both are read-only JSON views over existing files. They expose the experiment and
attempt IDs, individual exit/signal outcomes, native completion, session evidence
limitations, verified captured-report path/hash and the report's scientific assessment.
Science is shown only after a successful report slot and matching capture bytes,
size and SHA256; a file left in the live work root is not trusted as final output.
Native completion is labeled native-reported, separate from supervisor outcomes. The native
`sparselab-publication-report` and evidence indexes
remain authoritative formats; no parallel result database is introduced.
An unassessed, negative or inconclusive scientific result never blocks final report
capture. A failed command or incomplete capture stays visible separately. A local
report is not an external publication; post its link through the existing human
Board workflow. Historical reports and claims are never rewritten by these views.

Validation uses stdlib fake subprocesses and filesystem fixtures only. No GPU,
Docker daemon or real workload has been exercised by this entrypoint's tests.
Actual-host use and larger experiments still need their own approved resources.
