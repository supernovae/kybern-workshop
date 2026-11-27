# Astronomy and software relations

These two bounded corpora exercise the same Corpus indexes and compilers on
real sources. The astronomy families are ten planetary or dwarf-planet systems.
The software families are thirteen CPython standard-library packages. Each
family stays in one split. The two domains have separate indexes and
tokenizers. The recipes compare representations within a domain.

- Astronomy uses revision-pinned [Wikidata](https://www.wikidata.org/wiki/Wikidata:Licensing)
  structured records (CC0-1.0). The capture keeps the full P397 (parent body) and
  P398 (child body) statement arrays, including their qualifiers, references
  and ranks. The scope admits only the selected bodies. The projections omit
  all other properties, and the downloaded item files retain the originals.
  Treat the graph as recorded Wikidata assertions.
- Software uses [CPython v3.14.0](https://github.com/python/cpython/tree/ebf955df7a89ed0c7968f79faec1de49f61ed7cb/Lib).
  Keep the pinned [PSF license and notices](https://github.com/python/cpython/blob/ebf955df7a89ed0c7968f79faec1de49f61ed7cb/LICENSE)
  and additional module notices with the sources. Corpus reads import syntax
  from module ASTs, so conditional and nested imports can appear. Dynamic
  resolution and transitive dependencies have no edge of their own. Upstream
  authoring provenance is recorded as unknown.

Both sources retain their physical evidence locators. An absent or cross-split
endpoint is recorded as unresolved. The source and scope pins live in
[`astronomy.json`](astronomy.json) and [`software.json`](software.json).
See [item revisions](astronomy-items.tsv) and [package splits](software-families.tsv).

## Acquire pinned inputs

Use Lab with the `python-ast` relation adapter, Bash, curl, jq, and GNU tar.
Set `RECIPE` to this directory. Run the commands in a fresh directory outside
Git. Keep the downloaded files under that directory. The extraction commands
verify the exact SHA-256 of every projected payload before publishing an index.

```bash
set -euo pipefail
WORK="${WORK:-$HOME/.local/share/klab/real-domain-relations}"
mkdir -p "$WORK"
cd "$WORK"
export KLAB_WORK_DIR="$WORK/state"
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1
mkdir astronomy software cpython wiki receipts

while IFS=$'\t' read -r family split item revision; do
  curl -fsSL --retry 2 --max-time 30 --max-filesize 4000000 \
    -A 'Kybern Workshop research (github.com/supernovae/kybern-workshop)' \
    "https://www.wikidata.org/wiki/Special:EntityData/$item.json?revision=$revision" \
    -o "wiki/$item.json"
  jq -ceS --arg item "$item" --argjson revision "$revision" '
    .entities[$item] |
    if .id != $item or .lastrevid != $revision then error("Wikidata revision mismatch")
    else {id,type,claims:(.claims | with_entries(select(.key == "P397" or .key == "P398")))}
    end' "wiki/$item.json" >> "astronomy/$family.jsonl"
done < "$RECIPE/astronomy-items.tsv"
jq -RceS 'split("\t") | {family:("astronomy:"+.[0]),split:.[1],id:("wikidata:"+.[2])}' \
  "$RECIPE/astronomy-items.tsv" > astronomy/scope.jsonl

cpython_revision=ebf955df7a89ed0c7968f79faec1de49f61ed7cb
curl -fsSL --retry 2 --max-time 60 --max-filesize 52000000 \
  "https://codeload.github.com/python/cpython/tar.gz/$cpython_revision" -o cpython.tar.gz
tar -xOf cpython.tar.gz "cpython-$cpython_revision/LICENSE" > cpython/LICENSE
mapfile -t patterns < <(cut -f1 "$RECIPE/software-families.tsv" | sed "s|.*|cpython-$cpython_revision/Lib/&/*.py|")
tar -xzf cpython.tar.gz -C cpython --strip-components=2 --wildcards "${patterns[@]}"
while IFS=$'\t' read -r family split; do
  LC_ALL=C find "cpython/$family" -type f -name '*.py' | LC_ALL=C sort | while read -r file; do
    path=${file#cpython/}
    jq -RscS --arg path "Lib/$path" --arg relative "$path" '
      . as $source | {
        module: ($relative | sub("(^|/)__init__\\.py$"; "") | sub("\\.py$"; "") | gsub("/"; ".")),
        path: $path, is_package: ($relative | endswith("/__init__.py")), source: $source
      }' "$file"
  done > "software/$family.jsonl"
  jq -ceS --arg family "$family" --arg split "$split" '
    {id:("python:"+.module),family:("software:"+$family),split:$split}
  ' "software/$family.jsonl"
done < "$RECIPE/software-families.tsv" > software/scope.jsonl
cp "$RECIPE"/{astronomy,software}.json .
```

## Extract, compare and prepare

The first pass builds and cold-verifies both indexes, then compiles triples,
factorized relationships and seeded walks. Astronomy also compiles a hierarchy
on the declared parent predicate. For each domain, fit a 320-token BPE on TRAIN
triples and measure every representation with that tokenizer. Triples and
factorization preserve the same admitted assertion set. The astronomy
hierarchy preserves it too. Walks select and revisit edges.

```bash
jq '.hierarchy_predicate = "wikidata:P397"' "$RECIPE/../compilers/hierarchy.json" > astronomy-hierarchy.json
for domain in astronomy software; do
  klab corpus relations extract "$domain.json" --workers 2 \
    > "receipts/$domain-index.json" 2> "receipts/$domain-extract.log"
  index=$(jq -er .key "receipts/$domain-index.json")
  klab corpus relations inspect "$index" --cold > "receipts/$domain-audit.json"
  for arm in triples factorized walks; do
    klab corpus relations compile "$index" "$RECIPE/../compilers/$arm.json" \
      > "receipts/$domain-$arm.json"
  done
  if [[ "$domain" == astronomy ]]; then
    klab corpus relations compile "$index" astronomy-hierarchy.json > receipts/astronomy-hierarchy.json
  fi
  triples=$(jq -er .path "receipts/$domain-triples.json")
  if [[ "$domain" == astronomy ]]; then
    license="CC0-1.0"
    arms=(triples factorized walks hierarchy)
  else
    license="PSF-2.0; retain the pinned LICENSE and package or module notices"
    arms=(triples factorized walks)
  fi
  keys=()
  for arm in "${arms[@]}"; do
    artifact="receipts/$domain-$arm.json"
    keys+=("$(jq -er .key "$artifact")")
    jq -n --slurpfile input "$artifact" --slurpfile baseline "receipts/$domain-triples.json" \
      --arg license "$license" --arg cache "$WORK/$domain-prepared" \
      '$input[0] as $arm | $baseline[0] as $base | {dataset:{
        source:"local_text", revision:$arm.key, license:$license, cache_dir:$cache,
        train_path:($arm.path+"/train.jsonl"), validation_path:($base.path+"/validation.jsonl"),
        train_max_documents:$arm.partitions.train.sequences,
        validation_max_documents:$base.partitions.validation.sequences,
        train_max_tokens:100000,validation_max_tokens:100000}}' > "$domain-$arm-dataset.json"
  done
  jq -s --arg output "$WORK/$domain-tokenizer" 'add | .output_dir = $output | .vocab_size = 320' \
    "$RECIPE/../tokenizer-options.json" "$domain-triples-dataset.json" > "$domain-fit.json"
  klab tokenizer train "$domain-fit.json" > "receipts/$domain-tokenizer.txt"
  klab corpus relations compare "${keys[@]}" \
    --tokenizer "$domain-tokenizer/tokenizer.json" --max-bytes 8388608 > "receipts/$domain-compare.json"
  tokenizer="$WORK/$domain-tokenizer/tokenizer.json"
  manifest="$WORK/$domain-tokenizer/tokenizer_manifest.json"
  jq -n --arg path "$tokenizer" --arg sha256 "$(jq -er .sha256 "$manifest")" \
    --arg manifest_sha256 "$(sha256sum "$manifest" | cut -d ' ' -f1)" \
    --arg train_sha256 "$(jq -er '.files["train.jsonl"].sha256' "receipts/$domain-triples.json")" \
    --slurpfile source "$domain-triples-dataset.json" \
    '{model:{vocab_size:320},tokenizer:{path:$path,origin:{
      sha256:$sha256,manifest_sha256:$manifest_sha256,train_sha256:$train_sha256,
      dataset:$source[0].dataset}}}' > "$domain-tokenizer-path.json"
  for arm in "${arms[@]}"; do
    run="$domain-$arm-run.yaml"
    klab config compose "$RECIPE/../model.yaml" "$domain-$arm-dataset.json" "$domain-tokenizer-path.json" --output "$run" \
      > "receipts/$domain-$arm-compose.txt"
    klab data prepare "$run" > "receipts/$domain-$arm-prepared.txt"
    prepared=$(tail -n 1 "receipts/$domain-$arm-prepared.txt")
    klab data coverage --prepared-root "$prepared" --config "$run" --json \
      > "receipts/$domain-$arm-coverage.json"
  done
done
```

Keep the test split out of training and development evaluation. The commands
use one development file for all prepared arms in each domain. The comparison
counts serialized tokens including one EOS per row, before sequence-block
packing. Coverage separately reports dropped tails and repeated rows removed
during preparation.

## Check assertion coverage and shared validation

Compare sorted assertion IDs with multiplicity across the lossless compiler
outputs. Check the actual packed development array separately.

```bash
for domain in astronomy software; do
  triples=$(jq -er .path "receipts/$domain-triples.json")
  baseline=$(tail -n 1 "receipts/$domain-triples-prepared.txt")
  for arm in factorized hierarchy walks; do
    [[ "$domain" != software || "$arm" != hierarchy ]] || continue
    candidate=$(tail -n 1 "receipts/$domain-$arm-prepared.txt")
    cmp "$baseline/validation.npy" "$candidate/validation.npy"
    [[ "$arm" != walks ]] || continue
    output=$(jq -er .path "receipts/$domain-$arm.json")
    for split in train validation test; do
      jq -r '.assertions[]' "$triples/$split.lineage.jsonl" | LC_ALL=C sort \
        > "receipts/$domain-$split-original-assertions.txt"
      jq -r '.assertions[]' "$output/$split.lineage.jsonl" | LC_ALL=C sort \
        > "receipts/$domain-$split-$arm-assertions.txt"
      cmp "receipts/$domain-$split-original-assertions.txt" "receipts/$domain-$split-$arm-assertions.txt"
    done
  done
done
```

## Measured preparation

The [record](results/2026-11-27.json) binds the capture to Lab
`591ef2bc` and includes index, representation and tokenizer digests.
Astronomy admitted 99 assertions from 60 items, and software admitted 283
from 282 modules. Astronomy had 410 statements outside the scope. Software
reported 845 out-of-scope import sites and 21 sites crossing split boundaries.

| TRAIN representation | Astronomy serialized tokens | Software serialized tokens |
| --- | ---: | ---: |
| Triples | 1,043 | 5,027 |
| Factorized | 779 | 3,272 |
| Hierarchy | 815 | — |
| Seeded walks | 3,948 | 9,925 |

Factorization saved 25% and 35% respectively. Its assertion IDs matched the
triples with multiplicity for every split, as did the astronomy hierarchy.
The seven prepared bundles retained every compiled TRAIN row and matched
validation bytes within each domain. Complete blocks left different
unsupervised target tails, which the record shows for each arm. The token
savings measure serialization. Learning and cross-domain transfer require
separate training and evaluation.

The [matched exposure study](exposure/README.md) trains triples and
factorization with whole assertion passes and separately matched update
time, then scores context questions over development families from both
domains.

On local NVMe, cold astronomy extraction took 0.49 s at 82 MiB peak RSS.
Software took 0.81 s at 93 MiB. After a fault at the fourth software shard,
the retry reused four of 13 shards and took 0.61 s with the same index bytes.
Verified warm software open took 0.59 s. These are single bounded runs with
warm OS caches, including CLI startup.
