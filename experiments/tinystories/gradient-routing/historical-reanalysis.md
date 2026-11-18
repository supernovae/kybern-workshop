# Recompute the historical full-width contrast
This procedure reads the three single-seed series already shipped by Workshop and produces a local comparison JSON and SVG. It reads no development/test stories. These are Intel historical observations under the old factor initialization, not measured ROCm trajectories or C4 identity-initialized results. The source only includes final values here, so no loss-vs-time or retention-over-training curve can be reconstructed.

From the new study directory:

```sh
python3 - <<'PY'
import csv, hashlib, json, math, statistics
from pathlib import Path
base=Path("../lm-head-bottleneck/results")
out=Path("results"); out.mkdir(exist_ok=True)
rows=[]
for seed,suffix in enumerate(["8c046567","a2a5f28f","be6c7739"],1):
    series=base/f"sweep-20261113T230505Z-{suffix}"/"series.csv"
    with series.open(newline="") as f:
        arm,=[r for r in csv.DictReader(f) if r["label"]=="model.output_head_rank=512"]
    assert int(arm["comparable"])==1 and arm["metric"]=="loss"
    rows.append(dict(seed=seed,series=str(series),source_sha256=hashlib.sha256(series.read_bytes()).hexdigest(),candidate_minus_dense_nats=float(arm["heldout_delta_mean"]),nominal_tokens=int(arm["tokens_seen"]),candidate_parameters=int(arm["parameters"]),source_recorded_wall_seconds=float(arm["wall_seconds_mean"]),candidate_raw_residual_norm=float(arm["kernel_norm_fraction_mean"])))
v=[r["candidate_minus_dense_nats"] for r in rows]
mean=statistics.mean(v);sd=statistics.stdev(v);se=sd/math.sqrt(len(v))
t=4.302652729911275
lo,hi=mean-t*se,mean+t*se
result=dict(observation_class="historical_reanalysis_not_current_training",contrast="rank512_old_factor_minus_dense",n=len(v),mean=mean,sample_sd=sd,se=se,t_critical_95_df2=t,ci95_paired_t=[lo,hi],units="nats_per_token",rows=rows,assumption="independent approximately normal between-seed differences; conditional on published task/budget")
(out/"historical-full-width.json").write_text(json.dumps(result,indent=2)+"\n")
x=lambda a:82+820*a/.065
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="316" viewBox="0 0 960 316"><rect width="960" height="316" fill="white"/><g font-family="sans-serif" fill="#182c40"><text x="24" y="35" font-size="23">Historical full-width factorization penalty</text><text x="24" y="61" font-size="15">Intel B70, 388.1M positions; candidate minus dense validation NLL (nats/token).</text>']
for seed,val in enumerate(v,1):
    y=70+seed*31
    svg.append(f'<text x="24" y="{y+5}">s{seed}</text><circle cx="{x(val):.2f}" cy="{y}" r="6" fill="#197873"/><text x="{x(val)+12:.1f}" y="{y+5}">{val:+.4f}</text>')
svg.append(f'<text x="24" y="213">mean</text><path d="M{x(lo):.2f} 208 H{x(hi):.2f}" stroke="#2f477a" stroke-width="4"/><circle cx="{x(mean):.2f}" cy="208" r="6" fill="#2f477a"/><path d="M82 235 H902" stroke="#697c8d"/>')
for i in range(7):
    a=.01*i
    svg.append(f'<path d="M{x(a):.1f} 231v9" stroke="#697c8d"/><text x="{x(a):.1f}" y="258" text-anchor="middle">{a:.2f}</text>')
svg.append(f'<text x="24" y="291" font-size="14">Mean {mean:+.4f}; paired 95% t interval [{lo:+.4f}, {hi:+.4f}] (3 seed pairs, df=2). Not a new ROCm run.</text></g></svg>')
(out/"historical-full-width.svg").write_text("".join(svg)+"\n")
print(json.dumps({k:v for k,v in result.items() if k!="rows"}))
PY
```

