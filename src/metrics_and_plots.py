import argparse, warnings, pandas as pd, numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
warnings.filterwarnings("ignore")

def mape(y_true, y_pred):
    y_true = np.array(y_true, dtype=float); y_pred = np.array(y_pred, dtype=float)
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask]-y_pred[mask]) / y_true[mask]))*100 if mask.any() else np.nan

def compute_mape_per_region(demand_csv, horizon=8):
    df = pd.read_csv(demand_csv, parse_dates=["date"])
    regions = sorted(df["region"].unique())
    rec = []
    for r in regions:
        sub = df[df.region==r].sort_values("date")
        ts = sub.set_index("date")["demand"].asfreq("7D")
        train, test = ts.iloc[:-horizon], ts.iloc[-horizon:]
        model = SARIMAX(train, order=(1,1,1), enforce_stationarity=False, enforce_invertibility=False)
        res = model.fit(disp=False); fc = res.forecast(horizon)
        rec.append({"region": r, "mape_last8": round(float(mape(test.values, fc.values)),2)})
    met = pd.DataFrame(rec).sort_values("mape_last8")
    return met

def plot_mape_bar(met, out_png):
    plt.figure(figsize=(8,4))
    plt.bar(met["region"], met["mape_last8"])
    plt.title("Forecast error by region (MAPE last 8 weeks)")
    plt.xlabel("Region"); plt.ylabel("MAPE (%)")
    plt.tight_layout(); plt.savefig(out_png, dpi=160)

def compute_fill_rate(allocation_csv):
    alloc = pd.read_csv(allocation_csv, parse_dates=["date"])
    summary = alloc.groupby("region").agg(demand=("demand","sum"), alloc=("alloc","sum"))
    summary["fill_rate_%"] = (summary["alloc"]/summary["demand"]*100).round(2)
    return summary.reset_index().sort_values("fill_rate_%", ascending=False)

def plot_fillrate_bar(fr, out_png, min_service=0.85):
    plt.figure(figsize=(8,4))
    plt.bar(fr["region"], fr["fill_rate_%"])
    plt.axhline(min_service*100, linestyle="--")
    plt.title("Service level by region (Fill Rate)")
    plt.xlabel("Region"); plt.ylabel("Fill Rate (%)")
    plt.tight_layout(); plt.savefig(out_png, dpi=160)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demand_csv", default="data/demand.csv")
    ap.add_argument("--allocation_csv", default="reports/allocation.csv")
    ap.add_argument("--horizon", type=int, default=8)
    ap.add_argument("--min_service", type=float, default=0.85)
    ap.add_argument("--out_mape_png", default="reports/mape_bar.png")
    ap.add_argument("--out_fill_png", default="reports/fillrate_bar.png")
    ap.add_argument("--out_mape_csv", default="reports/mape.csv")
    ap.add_argument("--out_fill_csv", default="reports/fillrate.csv")
    args = ap.parse_args()

    met = compute_mape_per_region(args.demand_csv, args.horizon)
    fr = compute_fill_rate(args.allocation_csv)

    met.to_csv(args.out_mape_csv, index=False)
    fr.to_csv(args.out_fill_csv, index=False)
    plot_mape_bar(met, args.out_mape_png)
    plot_fillrate_bar(fr, args.out_fill_png, args.min_service)

    print(f"Wrote {args.out_mape_csv}, {args.out_fill_csv}")
    print(f"Wrote {args.out_mape_png}, {args.out_fill_png}")
    print("MAPE:", met.to_dict(orient="records"))
    print("FillRate:", fr[["region","fill_rate_%"]].to_dict(orient="records"))

if __name__ == "__main__":
    main()
