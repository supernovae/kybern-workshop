# Use native Lab from any recipe directory

Lab owns authoring, parsing, planning, execution and verification. Your experiment
repository owns DSL/configuration, cards, documentation and artifact references.
Ordinary Git can version that directory; no Workshop account, Harness checkout,
Notion integration or per-recipe Python is required.

Use an already installed, reviewed Lab runtime. These commands describe interfaces,
not permission to install packages or run a workload. Current metadata evidence
and its exact source pin are in [the acceptance record](native-acceptance-2026-10-18.md).

## Choose the existing route

| Need | Native route | Boundary |
| --- | --- | --- |
| Simple controlled comparison | `config validate`, `config derive`, then `try` and `report` | `try` performs model work; use the recipe’s actual input and runtime limits |
| Author a shareable inventory | `experiment recipe create` with explicit files and profile | Copies selected metadata; no scientific design or future hashes |
| Relocate an existing inventory | `experiment recipe export` then the profile’s `inspect` | Local artifact bindings remain explicit and separate |
| Prepare inputs | `experiment recipe preparation inspect`, then admitted `apply`/`resume` | Inspection creates no tokenizer/data; execution retains native receipts and limits |
| Prepared-input workflow | `experiment recipe workflow inspect`, verified `resolve`/`publish`, admitted `apply`/`approve`/`resume`, then `report` | Supported CPU profiles only; publication is not execution authority |
| Inspect a declared derivative | Matrix `recipe inspect` checkpoint-phase projection | Missing payloads stay unavailable; inherited settings and compatibility require native verification |

The [TinyStories microlab](../examples/tinystories-microlab/README.md) uses the
simple comparison route. Its advanced Campaign is not interchangeable with the
bounded matrix preview. [DevMind](../experiments/devmind/README.md) still lacks a
full RunConfig and real generated identities; validate its sections and compile
its declared preparation argv without claiming the whole experiment is ready.

## Author and inspect without execution

From any working directory, let `INPUT` be the absolute directory containing the
`examples/synthetic-cpu` declarations in your Workshop checkout (or a byte-identical
copy), and `DEST` an unused absolute directory whose parent already exists:

```sh
sparselab experiment recipe create "$INPUT" --profile preparation \
  --id workshop-synthetic-cpu-preparation --entrypoint preparation-campaign.json \
  --file campaign:preparation-campaign.json --file run_config:run.json \
  --file tokenizer_config:tokenizer-config.json --file metadata:monitor.json \
  --output "$DEST"
sparselab experiment recipe preparation inspect "$DEST/recipe.json" \
  --bindings /absolute/local-bindings.json --json
```

The current local bindings use native field names, without an obsolete bindings
version field. Choose output locations under your eventual external work root;
inspection does not create them:

```json
{
  "artifacts": {},
  "config_paths": {
    "tokenizer-config.json": {
      "output_dir": "/absolute/work/tokenizer",
      "dataset.cache_dir": "/absolute/work/cache"
    },
    "run.json": {
      "tokenizer.path": "/absolute/work/tokenizer/tokenizer.json",
      "dataset.cache_dir": "/absolute/work/cache",
      "logging.root_dir": "/absolute/work/runs"
    }
  }
}
```

Creation uses the selected declarations unchanged. It does not choose scientific
settings, fabricate artifact identities or grant approval. Commit the resulting
metadata with ordinary Git if desired. Later execution needs a separately reviewed
admission containing the actual inspected recipe/binding identities, supported
runtime and finite limits. Generated outputs must be verified before binding them
into later workflow declarations; preserve original preparation provenance and
accounting through review and resume.

For exact supported operations and admission fields, use the pinned Lab
[portable authoring](https://github.com/supernovae/tiny-sparse-lab/blob/7e306a96bcc617468d2a06493dab4562bff6beb0/docs/portable-recipes.md),
[preparation](https://github.com/supernovae/tiny-sparse-lab/blob/7e306a96bcc617468d2a06493dab4562bff6beb0/docs/preparation-recipes.md)
and [workflow](https://github.com/supernovae/tiny-sparse-lab/blob/7e306a96bcc617468d2a06493dab4562bff6beb0/docs/workflow-recipes.md)
contracts. Existing example result pins remain historical evidence, not current
runtime qualification. New reproductions use current interfaces and new identities;
no compatibility adapter is provided.
