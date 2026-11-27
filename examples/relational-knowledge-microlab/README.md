# Relational Knowledge Microlab

Twenty miniature drainage basins give the model a known set of links and
transfer rules. This CPU pilot asks how the same decoder responds to prose,
triples, seeded walks, hierarchies, factorized relationships, procedural
examples, and a mixed curriculum. The inputs are authored rule and graph
declarations licensed Apache-2.0. Lab generates the training text and
simulation traces locally.

Twelve basin families are reserved for training, four for development and four
for final evaluation. All nodes of a basin stay in its assigned split.
Every arm starts from the same initialization for a given seed and applies
32,768 training targets. A single 384-token BPE is fitted on TRAIN prose.
Every arm scores the same four development prose documents. The procedural
arms add realized examples derived from the rules, and seeded walks repeat
selected links. This pilot fixes the token budget while allowing exposure
and source-information coverage to differ.

The development ranking declaration separates recall of facts from trained
basins from questions over new basin families. The latter supply the necessary
context for two-hop composition, overrides, legal transfer limits and failed
transfers. Uniform four-choice performance earns 25% credit. Leave the
[final declaration](evaluation/final.json) for a representation chosen
after development, with its own run and recorded protocol.

The [paired counterfactual study](counterfactuals/README.md) reuses the
21 fixed-token checkpoints on 24 new simulated families and measures whether
answers follow a change in the request. It tests both ranking and
[free-response generation](counterfactuals/README.md#generate-answers-without-choices).

## Build the representations

Use Lab with local tokenizer-origin verification and
`klab eval --ranking`. Set `RECIPE` to this directory in a Workshop checkout
and start in a fresh work directory. The commands use `jq` to read receipts.

```bash
WORK="$HOME/.local/share/klab/relational-microlab"
mkdir -p "$WORK"
cd "$WORK"
export KLAB_WORK_DIR="$WORK/state"
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=1
mkdir receipts views

klab corpus relations extract "$RECIPE/sources/relations.json" --workers 2 > receipts/relations.json
klab corpus mechanisms simulate "$RECIPE/sources/worlds.json" --workers 2 > receipts/worlds.json
INDEX=$(jq -er .key receipts/relations.json)
WORLDS=$(jq -er .key receipts/worlds.json)
klab corpus mechanisms audit "$WORLDS" --samples 20 --seed 29 > receipts/oracle-audit.json

for arm in triples walks hierarchy factorized; do
  klab corpus relations compile "$INDEX" "$RECIPE/compilers/$arm.json" > "receipts/$arm.json"
done
jq -n --arg HIERARCHY "$(jq -er .key receipts/hierarchy.json)" \
  --arg FACTORIZED "$(jq -er .key receipts/factorized.json)" \
  '$ARGS.named' > receipts/compiler-values.json
klab corpus render-declaration --template "$RECIPE/compilers/mixed.template.json" \
  --values-json "$(cat receipts/compiler-values.json)" \
  --output "$KLAB_WORK_DIR/mixed.json" > receipts/render.json
for arm in prose procedural; do
  klab corpus mechanisms compile "$WORLDS" "$RECIPE/compilers/$arm.json" > "receipts/$arm.json"
done
klab corpus mechanisms compile "$WORLDS" "$KLAB_WORK_DIR/mixed.json" > receipts/mixed.json
for arm in prose triples walks hierarchy factorized procedural mixed; do
  ln -s "$(jq -er .path "receipts/$arm.json")" "views/$arm"
done
```

## Fit once and run paired seeds

```bash
cp "$RECIPE"/{model.yaml,dataset.json,sweep.yaml} .
jq -s add "$RECIPE/tokenizer-options.json" dataset.json > tokenizer.json
klab tokenizer train tokenizer.json
klab config compose model.yaml dataset.json --output baseline.yaml
ORIGIN=$(jq -cn --arg sha256 "$(jq -er .sha256 tokenizer/tokenizer_manifest.json)" \
  --arg manifest_sha256 "$(sha256sum tokenizer/tokenizer_manifest.json | cut -d ' ' -f1)" \
  --arg train_sha256 "$(jq -er '.files["train.jsonl"].sha256' receipts/prose.json)" \
  --slurpfile source dataset.json \
  '{sha256:$sha256,manifest_sha256:$manifest_sha256,train_sha256:$train_sha256,dataset:$source[0].dataset}')
klab config derive baseline.yaml --set "tokenizer.origin=$ORIGIN" --output run.yaml
klab tokenizer verify run.yaml --json > receipts/tokenizer.json

klab corpus relations compare "$(jq -er .key receipts/triples.json)" \
  "$(jq -er .key receipts/hierarchy.json)" "$(jq -er .key receipts/factorized.json)" \
  --tokenizer tokenizer/tokenizer.json --max-bytes 8388608 > receipts/representations.json
klab sweep sweep.yaml --backend cpu --json > receipts/sweep.json
klab report SWEEP_ID
```

Lab prepares every arm through its regular local-text loader. The walk
declaration emits 168 training rows and the preparation deduplicates them
to 119 distinct documents. Other training document counts are written in
the sweep. All arms keep the original prose validation bytes.

For each selected run, use the run directory and checkpoint named in the
try record. The same command works for the prose baseline.

```bash
klab eval RUN_ID --runs-dir RUNS --checkpoint GENERATION \
  --ranking "$RECIPE/evaluation/development.json"
```

Keep the compiled artifact receipts, sweep ID, paired run IDs, training
targets and wall times with any result. Model rankings and held-out
prose loss answer different questions.

## CPU pilot results

Lab `8b07f3c1e60bbb7cc6960c70d520ce7ea94b9d38`, sweep
`sweep-20261127T181949Z-1acba96a`. All 21 runs completed on CPU and
applied 32,768 targets with a 106,816-parameter decoder. The
[run record](results/2026-11-27.json) lists the artifact and checkpoint
digests, run IDs and per-seed scores.

| Training view | Prose loss (nats) | Seen relationship choices | Held-out context choices | Median training wall time |
| --- | ---: | ---: | ---: | ---: |
| Prose | 3.604 | 16.7% | 33.3% | 1.98 s |
| Triples | 6.708 | 15.3% | 25.0% | 1.96 s |
| Walks | 6.734 | 23.6% | 22.9% | 1.98 s |
| Hierarchy | 6.559 | 33.3% | 37.5% | 2.03 s |
| Factorized | 6.834 | 40.3% | 29.2% | 1.98 s |
| Procedural | 4.440 | 26.4% | 33.3% | 2.00 s |
| Mixed | 4.476 | 36.1% | 45.8% | 2.02 s |

Loss and choice columns average the three seeds. Each seed scores 24 seen
relationship choices and 16 context questions drawn from four development
families. All 18 paired tries failed the held-out prose-loss gate, so
the current recipe advances no alternative and leaves the final panel held
back. The mixed arm answered more development context questions despite
the prose regression. Sixteen questions over four families leave substantial
uncertainty about transfer to a new family.

With the same tokenizer, the TRAIN graph took 6,864 tokens as triples,
5,244 as hierarchy and 2,580 as factorization before packing. The latter
two round-tripped the canonical assertions. Lab also replayed all 20 rule
worlds against their pinned sources. Fresh prepared directories on the
same host took 58–91 ms per arm with the files already warm. The measured
cell sizes are for validating the workflow and do not estimate production
preparation throughput.

The [matched random-versus-coherent study](packing/README.md) holds the
passages, tokenizer, token exposure and update shape fixed. The
[real-domain recipe](real-domains/README.md) prepares pinned astronomy and
software data and checks assertion coverage across representations. The
[exposure study](real-domains/exposure/README.md) compares factorization under
equal assertion exposure and separately matched update time. Broader
representation and transfer comparisons remain in
[Workshop #118](https://github.com/supernovae/kybern-workshop/issues/118).
