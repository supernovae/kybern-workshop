# Kybern Workshop: instructions for agents

Workshop holds **declarations and records**. [Kybern Model Lab](https://github.com/supernovae/model-lab)
(`klab`) does all the work. Read Lab's own `AGENTS.md` before running anything;
its rules on lab mode, resources, evidence and spending apply here too.

## 1. What belongs here

- **Declarations:** run configs, tokenizer configs, model and optimizer
  sections, dataset sources, `try` deltas, probe and evaluation declarations,
  campaign and plan documents. YAML or JSON.
- **Documentation:** a README per recipe, protocols, and the commands to run.
- **Records:** compact results under `results/` and dated campaign notes.
  Never weights, token arrays, corpora or downloads.
- **Component packages:** a model part or training objective Lab does not ship
  lives in a small Python package under `components/` that registers it
  through Lab's `klab.components` or `klab.objectives` entry points. This is
  the only Python in the repository.

## 2. What does not belong here

No helper scripts, launchers, binders, validators, per-recipe tests or CI
programs. CI rejects any `.py` or `.sh` file outside `components/`.

When a task seems to need a script, the capability is either already in Lab or
missing from it:

1. Look for it: `klab --help`, `klab COMMAND --help`, and Lab's `docs/`.
2. If it exists, write the command into the recipe's documentation.
3. If it does not, stop and say so. Open a Lab issue stating the inputs, the
   expected output and how to tell it failed, or implement it in Lab with a
   neutral test. Do not write a local stand-in "to make it work"; a stand-in
   hides the gap and outlives the reason for it.

## 3. Use Lab for each job

| Need | Command |
| --- | --- |
| Check every declaration in a recipe or the whole repository | `klab config validate DIR` |
| Check one declaration | `klab config validate FILE --kind run\|tokenizer\|model\|optimizer` |
| Assemble a run config from sections and local paths | `klab config compose run.json model=model.json optimizer=optimizer.json bindings.json --output OUT.yaml` |
| Change fields of a complete config | `klab config derive BASE --set field=value --output OUT.yaml` |
| Pick an architecture by name and size | `klab architecture derive PRESET --params N --base BASE --output OUT.yaml` |
| See whether a model fits before training | `klab inspect CONFIG` |
| Pin and materialize a dataset | `klab data lock`, `klab data snapshot` |
| Fit a tokenizer, pack data | `klab tokenizer train`, `klab data prepare` |
| Train, continue, or start from a parent | `klab train CONFIG`, `--resume`, `training.parent_checkpoint` |
| Test one change against a baseline | `klab try DELTA.yaml --vs BASELINE.yaml`, then `klab report TRY_ID` |
| Probe, explore, generate, chat | `klab probe`, `klab explore`, `klab generate`, `klab chat` |
| Distill, tune on preferences, export | Lab's `docs/post-training.md` |
| Inventory and inspect a release recipe | `klab experiment recipe create`, `inspect`, `preparation inspect/apply`, `workflow inspect/resolve/apply/approve/report` |
| Verify inputs and checkpoints | `klab tokenizer verify`, `klab data prepared-inputs verify`, `klab checkpoint verify` |

## 4. Writing a recipe

- **One directory per recipe**, readable on its own: declarations plus a README
  that states the question, the settings, and the exact commands.
- **Paths are relative to the declaration** that names them, or are bound from
  a local file outside Git with `klab config compose`. Never commit a host
  path, a credential or a machine name.
- **Outputs stay outside Git**, under `$KLAB_WORK_DIR` or an ignored `work/`.
- **Never write a value that was not measured.** A hash, token count or
  checkpoint digest comes from a Lab receipt, or the field stays unbound.
- **Changing a published recipe makes a new recipe.** Do not edit the
  declarations behind a recorded result; add a variant and link the baseline.
- **Write documentation like a person explaining their own recipe:** say what
  something is and what to do with it, not where it isn't; avoid reflexive
  "X, not Y" contrasts, repeated hedges, and audit words (sealed, identity,
  provenance, admission) in prose.

## 5. Recording results

- Say what ran, on what, and what you skipped. A schema check or a dry run
  does not count as a trained model.
- Keep negative, interrupted and inconclusive results.
- One seed is within-run noise only; say so.
- Name the Lab commit, backend, dataset revision, run ID and status for
  anything described as trained.

## 6. Before you finish

```sh
klab config validate .          # every declaration loads with the installed Lab
git ls-files '*.py' '*.sh'      # nothing outside components/
```

Report what you ran and what you did not.
