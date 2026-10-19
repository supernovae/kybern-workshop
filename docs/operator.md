# Container & Supervisor Helper Reference (`scripts/workshop.py`)

For standard local experiments, run recipes directly with the `sparselab` CLI as shown in the [Tiny Sparse Lab workflow guide](native-workflow.md) and each project's README.

This document covers `scripts/workshop.py`, an optional helper for running a pre-staged Tiny Sparse Lab Campaign inside a resource-bounded Linux/WSL Docker container.

## Overview

`scripts/workshop.py` binds a Campaign declaration (`campaign.json`) and runtime profile (`runtime.json`) into a seven-step supervised session (`copy-inputs`, `validate`, `apply`, `approve`, `run`, `status`, and `report`) using the templates in `examples/operator/`.

- **Single approval gate:** expects one `approval` stage in the campaign, one `experiment_plan` stage, and one `experiment_collect` stage.
- **Resource bounds:** the default template in `examples/operator/session-template.json` sets an 1,800-second wall-clock limit and a 12 GiB container RAM ceiling with zero swap. For longer runs, set `limits.wall_seconds` in the session template and pass `--approved-wall-seconds N` when binding.

## Running the Offline Adapter Tests

The repository includes unit tests for `scripts/workshop.py` and `scripts/handoff.py` using standard-library mocks and temporary filesystem fixtures:

```sh
python3 -B -m unittest discover -s tests -v
```

## Binding a Supervised Session

Place your `campaign.json`, referenced plan/run/suite files, and `runtime.json` in a clean Workshop checkout, with prepared dataset and tokenizer inputs staged in an external directory:

```sh
python3 -B scripts/workshop.py bind \
  --checkout /path/to/workshop --commit FULL_WORKSHOP_SHA \
  --harness /path/to/harness --harness-commit FULL_HARNESS_SHA \
  --campaign /path/to/workshop/studies/example/campaign.json \
  --profile /path/to/workshop/studies/example/runtime.json \
  --inputs /path/to/prepared-inputs \
  --state /path/to/attempt/state --receipts /path/to/attempt/receipts \
  --runtime /path/to/observed-runtime.json --python /opt/venv/bin/python \
  --session-template examples/operator/session-template.json \
  --job-template examples/operator/job-template.json \
  --experiment EXP-123 --attempt exp123-attempt01 \
  --owner OWNER --approval APPROVAL_REFERENCE --approval-stage approve-model
```

`bind` writes the session and job specifications into `--state` without launching a container. Initialize a Git repository in the state directory and commit the generated JSON specs before running.

## Executing and Inspecting a Session

```sh
python3 -B scripts/workshop.py run --state /path/to/attempt/state \
  --harness /path/to/harness --harness-commit FULL_HARNESS_SHA \
  --inputs /path/to/prepared-inputs --image IMAGE_DIGEST --gpu
```

To inspect session status and verified report outputs after completion (or if a step stops early):

```sh
python3 -B scripts/workshop.py status --state /path/to/attempt/state
python3 -B scripts/workshop.py results --state /path/to/attempt/state
```

Both commands return read-only JSON summaries of stage completion, exit statuses, and the captured `audit/report.json` artifact.
