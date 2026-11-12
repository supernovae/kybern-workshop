# TinyStories sample configs

Start with the [lab walkthrough](https://github.com/supernovae/model-lab/blob/main/docs/tinystories-microlab.md).
Copy just `source.yaml`, `tokenizer.yaml` and `run.yaml` into the `inputs/`
directory of a fresh workspace outside the repository. Prepare the snapshot and
tokenizer, then use `try` for the width comparison. Relative paths resolve from
the copied YAML files. Lab keeps its runs in `WORK_DIR/lab/runs`; configs for
direct training write to `../runs`.

The sample pins one TinyStories revision and drops duplicate stories and any
story that appears in both training and validation. Each baseline arm trains
for 40 updates (10,240 targets). Getting the source needs network access. The
training is a small teaching exercise, too short to say much about quality.
Keep earlier data and any negative or interrupted results.

## Advanced configs

Use these when an exercise calls for them. Each one starts on its own and
doesn't pick up an earlier lab baseline automatically.

| File | Purpose | Native guide |
| --- | --- | --- |
| `continued.yaml` | PyTorch AdamW child: 80 cumulative updates / 20,480 targets, original 40-update decay horizon | [Checkpointing](https://github.com/supernovae/model-lab/blob/main/docs/checkpointing.md) |
| `matrix.yaml` | Two fresh FFN widths at the baseline budget | [Experiments](https://github.com/supernovae/model-lab/blob/main/docs/experiments.md) |
| `plan.yaml` | Width comparison with checkpoint-bound child phases | [Training programs](https://github.com/supernovae/model-lab/blob/main/docs/experiment-programs.md) |
| `campaign.yaml` | Acquisition through evaluation for three selected cells; optional wider child unselected | [Campaigns](https://github.com/supernovae/model-lab/blob/main/docs/campaigns.md) |

Copy the configs each one needs into a separate workspace. Put
`campaign.yaml` at the workspace root, with the other YAML files in `inputs/`.
Before locking, make sure the settings you are comparing and the backend
choices match across files. For exercises on a larger slice of the source, see
[dataset coverage and budgets](https://github.com/supernovae/model-lab/blob/main/docs/datasets.md).
The [acceptance record](acceptance.md) describes the original Campaign run of
these configs: its hashes, measured results and limitations. It's a record of
that run, separate from the beginner walkthrough.
