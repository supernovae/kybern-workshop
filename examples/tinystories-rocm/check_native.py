"""Metadata-only check against the exact Lab source; never invoke parsed handlers."""

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

from sparselab.campaign.plan import load_campaign
from sparselab.cli.main import build_parser
from sparselab.config.loading import load_config
from sparselab.experiments.compiler import expand_axes
from sparselab.experiments.plan import load_plan
from sparselab.operational_monitor import MonitorPolicy
from sparselab.runtime_profile import RuntimeProfile

root = Path(__file__).resolve().parent
config = load_config(root / "run.json")
plan = load_plan(root / "plan.json")
campaign = load_campaign(root / "campaign.json")
cells = expand_axes(config, plan.axes, max_runs=2, base_dir=root)
assert len(cells) == 2
assert sorted(c.model.ffn_dim for c, _ in cells) == [64, 96]
assert all(
    c.runtime.backend == "rocm" and c.runtime.precision == "fp32" for c, _ in cells
)
assert (
    sum(
        c.staging.smoke_steps + c.staging.warmup_steps + c.training.max_steps
        for c, _ in cells
    )
    == 16
)
assert (
    sum(
        (c.staging.smoke_steps + c.staging.warmup_steps + c.training.max_steps + 4)
        * c.evaluation.max_batches
        for c, _ in cells
    )
    == 24
)
assert all(
    (
        c.seed,
        c.model.vocab_size,
        c.model.hidden_dim,
        c.model.num_layers,
        c.model.num_heads,
        c.training.seq_len,
        c.training.micro_batch_size,
        c.training.gradient_accumulation,
    )
    == (7, 512, 32, 1, 2, 32, 1, 1)
    for c, _ in cells
)
profile = json.loads((root / "runtime.json").read_text())
profile["python"] = sys.executable
RuntimeProfile.model_validate(
    profile
)  # Fixture interpreter substitution only; no probe.
MonitorPolicy.model_validate_json((root / "monitor.json").read_text())
assert len(campaign.stages) == 12
assert all(
    s.runtime == "accept-rocm" and s.backend == "rocm"
    for s in campaign.stages
    if s.kind == "evaluation"
)
spec = importlib.util.spec_from_file_location("recipe_handoff", root / "handoff.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory() as tmp:
    t = Path(tmp)
    doc = module.render(
        t / "checkout",
        t / "inputs",
        t / "state",
        "fixture-native",
        "a" * 40,
        "fixture provenance",
        1000,
        1000,
    )
    parser = build_parser(work_dir=t / "work")
    for step in doc["steps"][1:]:
        argv = step["argv"]
        assert argv[:4] == ["/opt/venv/bin/python", "-B", "-m", "sparselab"]
        argv = argv[4:]
        parser.parse_args(
            argv
        )  # Only parsing; no native handler or model function called.
print(
    "Native schemas, two-cell aggregate budget, GPU evaluation authorization, and all five public CLI argv parsed successfully; no handlers executed."
)
