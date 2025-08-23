import argparse, pandas as pd, numpy as np
import pulp
import matplotlib.pyplot as plt
from pathlib import Path

def build_model(df, horizon=8, supply=None, supply_ratio=0.9,
                unmet_cost=3.0, extra_cost=1.0,
                min_service=0.85, max_share=0.6):
    df = df.copy(); df["date"] = pd.to_datetime(df["date"])
    regions = sorted(df["region"].unique())
    weeks = sorted(df["date"].unique())
    if len(weeks) > horizon: weeks = weeks[:horizon]

    demand = {(r,w): float(df[(df.region==r)&(df.date==w)]["yhat"].iloc[0])
              for r in regions for w in weeks}
    total_w = {w: sum(demand[(r,w)] for r in regions) for w in weeks}
    supply_w = {w: (float(supply) if supply is not None else float(supply_ratio)*total_w[w]) for w in weeks}

    m = pulp.LpProblem("iphone_allocation", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("alloc", [(r,w) for r in regions for w in weeks], lowBound=0, cat="Integer")
    unmet = pulp.LpVariable.dicts("unmet", [(r,w) for r in regions for w in weeks], lowBound=0)
    extra = pulp.LpVariable.dicts("extra", [(r,w) for r in regions for w in weeks], lowBound=0)

    m += pulp.lpSum(unmet_cost*unmet[(r,w)] + extra_cost*extra[(r,w)] for r in regions for w in weeks)
    for w in weeks: m += pulp.lpSum(x[(r,w)] for r in regions) <= supply_w[w]
    for r in regions:
        for w in weeks:
            d = demand[(r,w)]
            m += unmet[(r,w)] >= d - x[(r,w)]
            m += extra[(r,w)] >= x[(r,w)] - d
    for r in regions:
        m += pulp.lpSum(x[(r,w)] for w in weeks) >= min_service * pulp.lpSum(demand[(r,w)] for w in weeks)
    if max_share < 1.0:
        for w in weeks:
            for r in regions:
                m += x[(r,w)] <= max_share * supply_w[w]

    m.solve(pulp.PULP_CBC_CMD(msg=False))

    rows = []
    for r in regions:
        for w in weeks:
            d = demand[(r,w)]
            rows.append({"region": r, "date": pd.to_datetime(w),
                         "demand": d,
                         "alloc": x[(r,w)].value(),
                         "unmet": unmet[(r,w)].value(),
                         "extra": extra[(r,w)].value()})
    res = pd.DataFrame(rows).sort_values(["date","region"])
    summary = res.groupby("region").agg(demand=("demand","sum"),
                                        alloc=("alloc","sum"),
                                        unmet=("unmet","sum"),
                                        extra=("extra","sum"))
    summary["fill_rate_%"] = (summary["alloc"]/summary["demand"]*100).round(2)
    return res, summary, regions, weeks, supply_w

def plot_heatmap(res, regions, weeks, out_png):
    ratio = (res.pivot(index="region", columns="date", values="alloc") /
             res.pivot(index="region", columns="date", values="demand")).fillna(0.0)
    fig, ax = plt.subplots(figsize=(1.6*len(weeks)+3, 0.6*len(regions)+3))
    im = ax.imshow(ratio.values, aspect="auto")
    ax.set_xticks(range(len(weeks))); ax.set_yticks(range(len(regions)))
    ax.set_xticklabels([pd.to_datetime(w).strftime("%Y-%m-%d") for w in weeks], rotation=45, ha="right")
    ax.set_yticklabels(res.index.unique(level=0) if hasattr(res.index, "levels") else regions)
    ax.set_title("Allocation / Forecast Demand (heatmap)")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout(); fig.savefig(out_png, dpi=160)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="reports/forecast.csv")
    ap.add_argument("--horizon", type=int, default=8)
    ap.add_argument("--supply", type=float, default=None)
    ap.add_argument("--supply_ratio", type=float, default=0.9)
    ap.add_argument("--min_service", type=float, default=0.85)
    ap.add_argument("--max_share", type=float, default=0.6)
    ap.add_argument("--unmet_cost", type=float, default=3.0)
    ap.add_argument("--extra_cost", type=float, default=1.0)
    ap.add_argument("--out_csv", default="reports/allocation.csv")
    ap.add_argument("--out_png", default="reports/allocation_heatmap.png")
    args = ap.parse_args()

    df = pd.read_csv(args.data)
    res, summary, regions, weeks, supply_w = build_model(
        df, args.horizon, args.supply, args.supply_ratio,
        args.unmet_cost, args.extra_cost, args.min_service, args.max_share
    )
    Path("reports").mkdir(exist_ok=True, parents=True)
    res.to_csv(args.out_csv, index=False)
    plot_heatmap(res, regions, weeks, args.out_png)

    print(f"Wrote {args.out_csv} ({len(res)} rows) & {args.out_png}")
    print("Weekly supply plan (first 3):", {str(k.date()): round(v,1) for k,v in list(supply_w.items())[:3]})
    print("Fill rate by region (%):", summary["fill_rate_%"].to_dict())

if __name__ == "__main__":
    main()
