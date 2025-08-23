import argparse, numpy as np, pandas as pd
from datetime import datetime, timedelta
np.random.seed(42)

def gen(weeks=60, regions=None, seed=42):
    if regions is None:
        regions = ["SG","MY","TH","VN","ID","PH"]
    np.random.seed(seed)
    start = datetime(2024,1,1)
    dates = [start + timedelta(days=7*i) for i in range(weeks)]
    rows = []
    for r in regions:
        base = np.random.randint(800, 1800)     # 区域基准需求
        trend = np.random.uniform(-2, 6)        # 线性趋势
        seasonal_amp = np.random.uniform(0.05, 0.25) * base
        noise_sigma = 0.10 * base
        for t, d in enumerate(dates):
            season = seasonal_amp * np.sin(2*np.pi*t/52)
            uplift = 1.25 if t >= weeks-8 else 1.0  # 最近8周“新品发布”提振
            mean = (base + trend*t + season) * uplift
            demand = max(0, int(np.random.normal(mean, noise_sigma)))
            rows.append((d, t+1, r, demand))
    df = pd.DataFrame(rows, columns=["date","week","region","demand"])
    return df

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weeks", type=int, default=60)
    ap.add_argument("--regions", nargs="*", default=None)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="data/demand.csv")
    args = ap.parse_args()
    df = gen(args.weeks, args.regions, args.seed)
    df.to_csv(args.out, index=False)
    print(f"Wrote {args.out} with shape {df.shape} and regions {sorted(df.region.unique())}")

if __name__ == "__main__":
    main()
