# TinyStories: does a wider FFN help at the same training budget?

Run a small paired experiment on your GPU, inspect the evidence, then change one
thing. The baseline uses FFN width 64; the candidate uses 96. Both use the same
seed, train-only tokenizer, story selection, sequence length and training budget.
The question is whether the extra FFN capacity changes held-out loss under those
conditions—not whether this tiny model is a useful storyteller.

Start small: 64 training stories, 16 validation stories, vocabulary 512, one
transformer layer, hidden width 32, two heads, sequence length 32, seed 7 and fp32.
The checked-in configuration has one main training update, with smoke/warmup
settings of 2/5. This is a starting point for learning the workflow. Increase the
budget for both arms together before investigating model quality.

**Status:** the [CPU container smoke](../../results/2026-10-15-tinystories-smoke/README.md)
completed the native paired workflow. The GPU walkthrough below uses supported
Lab commands and published CUDA/ROCm images, but has **not been executed on a GPU**.
Image publication and CLI checks do not establish hardware or experiment correctness.

## Choose an existing GPU runtime

These Bash commands target an already configured Linux Docker host, an ordinary
non-root user, Git and Python 3 for copying/editing JSON. No host package or driver
setup is part of the experiment. Run from the Workshop checkout root.

All images below contain Lab `66ff9d71423e961ee15aed2267902164f04514c6`.
They are application images, not dependency-layer images. Publication evidence:
[accelerator images](https://github.com/supernovae/tiny-sparse-lab/actions/runs/38784066593)
and [CPU image](https://github.com/supernovae/tiny-sparse-lab/actions/runs/38784066479).

For an NVIDIA GPU with existing Docker GPU integration:

```sh
BACKEND=cuda
IMAGE=ghcr.io/supernovae/tiny-sparse-lab@sha256:517c53689e48a4f93f226015b76bf314cb4a51cd411fa3c3924281d23093fb9e
DEVICES=(--gpus device=0)
```

For an AMD RX 7900 XTX (gfx1100) on an existing native Linux ROCm host:

```sh
BACKEND=rocm
IMAGE=ghcr.io/supernovae/tiny-sparse-lab@sha256:0d30947f05873ad17b5ba10fcf431f94d297f2350c2a7a35d21785b0f9e435b8
DEVICES=(--device=/dev/kfd --device=/dev/dri
  --group-add "$(stat -c %g /dev/kfd)"
  --group-add "$(stat -c %g /dev/dri/renderD128)")
```

Select the render node for your GPU. This ROCm example is not a WSL command;
WSL's device path and runtime integration differ and are unverified here. Use
Lab's pinned [CUDA guide](https://github.com/supernovae/tiny-sparse-lab/blob/66ff9d71423e961ee15aed2267902164f04514c6/docs/containers-cuda.md)
or [ROCm guide](https://github.com/supernovae/tiny-sparse-lab/blob/66ff9d71423e961ee15aed2267902164f04514c6/docs/containers-rocm.md)
for host prerequisites. An unavailable explicit backend must fail, not fall back
to CPU. Podman users should use those guides' existing device integration and
rootless user mapping; Docker GPU flags are not interchangeable with Podman CDI.

For a CPU-only supporting check, choose instead:

```sh
BACKEND=cpu
IMAGE=ghcr.io/supernovae/tiny-sparse-lab@sha256:553eefba27b7069ba17fb92c5734b2b53548ad3b40f868b1ad39dc3e3ad82ea4
DEVICES=()
```

## Make a fresh local experiment

Choose an unused directory outside Git. The image pull downloads runtime layers;
the later snapshot step downloads dataset content. Neither is performed by
reading this guide or inspecting its declarations.

```sh
set -euo pipefail
STATE="$HOME/sparselab-experiments/tinystories-ffn-001"
mkdir -p "$(dirname "$STATE")"
mkdir "$STATE"
mkdir "$STATE/inputs" "$STATE/evidence"
cp examples/tinystories-worker/{source,run,tokenizer-config}.json "$STATE/inputs/"
python3 - "$STATE" "$BACKEND" <<'PY'
import json, sys
from pathlib import Path
root, backend = Path(sys.argv[1]), sys.argv[2]
assert backend in {'cuda', 'rocm', 'cpu'}
for name in ('run.json', 'tokenizer-config.json'):
    path = root / 'inputs' / name
    doc = json.loads(path.read_text())
    doc['dataset'].update(cache_dir='/state/payload/cache',
        train_path='/state/snapshot/train.jsonl',
        validation_path='/state/snapshot/validation.jsonl',
        source_manifest_path='/state/snapshot/manifest.json')
    if name == 'run.json':
        doc['runtime'].update(backend=backend, device_index=0)
        doc['tokenizer']['path'] = '/state/payload/tokenizer/tokenizer.json'
        doc['logging']['root_dir'] = '/state/payload/runs'
    else:
        doc['output_dir'] = '/state/payload/tokenizer'
    path.write_text(json.dumps(doc, indent=2) + '\n')
PY
docker pull "$IMAGE"
RUN=(docker run --rm --pull=never --user "$(id -u):$(id -g)"
  --read-only --cap-drop=ALL --security-opt=no-new-privileges
  --memory=4g --memory-swap=4g --cpus=2 --pids-limit=256
  --mount "type=bind,src=$STATE,dst=/state" "${DEVICES[@]}")
lab() { "${RUN[@]}" --network=none "$IMAGE" sparselab "$@"; }
lab --help
printf '%s\n' "$IMAGE" > "$STATE/evidence/image.txt"
git rev-parse HEAD > "$STATE/evidence/workshop-commit.txt"
```

Four GiB is a container host-memory limit, not a GPU VRAM limit. Choose runtime
resources for your own experiment; this example does not claim that every GPU
fits. The container's home, temporary files, caches and native work root remain
under the writable `/state` mount. Native records go to `/state/work/lab`.
Keep the same container paths across commands.

## Prepare once, then compare offline

The source declaration pins `roneneldan/TinyStories` at
`f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`. Validation stories are selected first;
overlap and within-split duplicates are excluded. Tokenizer fitting uses training
text only. No pretrained model is downloaded.

Check disk space before acquisition. Selecting 80 stories does not limit upstream
Parquet downloads to 80 stories' text size. This simple local path does not inherit
the separate CPU worker campaign's two-transfer/300 MiB acquisition envelope.
For that bounded acquisition path, see the [CPU workflow reference](../tinystories-worker/README.md).

```sh
df -h "$STATE"
df -i "$STATE"
"${RUN[@]}" --network=bridge -e HF_HUB_OFFLINE=0 -e HF_DATASETS_OFFLINE=0   "$IMAGE" sparselab data lock /state/inputs/source.json   --output /state/inputs/source.lock.json --cache-dir /state/source-cache   2>&1 | tee "$STATE/evidence/source-lock.log"
"${RUN[@]}" --network=bridge -e HF_HUB_OFFLINE=0 -e HF_DATASETS_OFFLINE=0   "$IMAGE" sparselab data snapshot /state/inputs/source.lock.json   --output /state/snapshot --cache-dir /state/source-cache   2>&1 | tee "$STATE/evidence/snapshot.log"
lab tokenizer train /state/inputs/tokenizer-config.json   2>&1 | tee "$STATE/evidence/tokenizer.log"
cat > "$STATE/wider-ffn.yaml" <<'YAML'
question: Does FFN width 96 improve held-out loss over width 64 at the same budget?
set:
  model.ffn_dim: 96
YAML
lab try /state/wider-ffn.yaml --vs /state/inputs/run.json   2>&1 | tee "$STATE/evidence/try.log"
```

`try` performs model work: both arms, held-out scoring and the fast probe battery.
It handles native data preparation and records actual work. It is a new lab
experiment, not a replay of the CPU campaign's 16-update/24-evaluation-batch
allocation. The portable Campaign workflow in `tinystories-worker` is CPU-only;
changing its admission's backend is not a GPU execution path.

The command prints a try ID and two run IDs. Read the sealed try record:

```sh
lab report TRY_ID
lab compare TRY_ID --references
```

Replace `TRY_ID` with the emitted ID. Missing reference evidence or an incomparable
result is not a win or a reason to fetch reference models. Keep the source lock,
input configuration, image digest, Workshop commit, logs and sealed record with
your experiment directory. A fixed seed does not promise bitwise equivalence
across devices or runtime versions.

## Reuse inputs without changing an earlier experiment

Within the same experiment, keep its cache writable even when all data is already
prepared. Native cache reuse opens `cache/.cleanup.lock` and atomically writes
`cache/<id>.preparation.json`; the work root also needs its cleanup lock. A read-only
cache can pass inspect/resolve and then fail at resume before any model updates.

For a fresh experiment, copy the completed snapshot and tokenizer (including
`tokenizer_manifest.json`) into the corresponding fresh locations above. Copy the
verified prepared-data artifact directory into the new cache **with its original
basename**. For example, after setting `PACKED` to the old artifact's absolute path:

```sh
mkdir -p "$STATE/payload/cache"
test ! -e "$STATE/payload/cache/$(basename "$PACKED")"
cp -R --no-preserve=mode,ownership -- "$PACKED" "$STATE/payload/cache/"
chmod -R u+rwX -- "$STATE/payload/cache/$(basename "$PACKED")"
```

Use independent copies, not symlinks or hardlinks to retained evidence. Skip the
acquisition/tokenizer commands when reusing verified completed inputs. Do not copy
old campaign/controller state, temporary packing directories or admissions.
Native validation must still accept the copied inputs; changed source/runtime or
preparation settings may require new preparation. Keep the original untouched and
account for both copies in disk usage.

For portable workflow reuse, point `artifacts.packed` to the copied artifact and
`logging_root` to the fresh output root; keep matching tokenizer/snapshot bindings.
Regenerate admission after changing bindings. The portable artifact identities and
reviewed recipe can remain unchanged when bytes are identical. This correction
was tested through native apply/approve/resume dispatch-bundle preparation with
worker execution disabled, then used in the completed CPU smoke.

## Interpret the result and build the next experiment

One main update and one seed cannot establish an architecture advantage. Start by
checking that both arms used the intended data/tokenizer, backend, seed and actual
training/evaluation counts. Read probe failures and missing evidence alongside
loss; a successful process exit alone does not establish scientific comparability.

Then increase the shared training budget, repeat paired seeds and use a larger
fixed validation sample. Change one intervention at a time: FFN width first,
then a separate experiment for learning rate or another architecture choice.
Do not change tokenizer or evaluation settings between arms. Preserve unsuccessful
results and keep an untouched final evaluation split instead of repeatedly
selecting against the same held-out stories.

Use a fresh directory for a changed preparation protocol, and record its new
identities. Use Lab's [try declarations](https://github.com/supernovae/tiny-sparse-lab/blob/66ff9d71423e961ee15aed2267902164f04514c6/docs/try-config.md)
for paired seeds and resource envelopes. Larger training, extra probes and GPU
runs are new work to budget, not conclusions implied by the CPU smoke.
