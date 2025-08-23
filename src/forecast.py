import argparse, warnings, pandas as pd, numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")

def fit_and_forecast(ts, horizon=8):
    model = SARIMAX(ts, order=(1,1,1), enforce_stationarity=False, enforce_invertibility=False)
    res = model.fit(disp=False)
    fc = res.forecast(steps=horizon)
    return res, fc

def mape(y_true, y_pred):
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask]-y_pred[mask]) / y_true[mask])) * 100 if mask.any() else np.nan

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/demand.csv")
    ap.add_argument("--horizon", type=int, default=8)
    ap.add_argument("--out_csv", default="reports/forecast.csv")
    ap.add_argument("--out_png", default="reports/forecast_demo.png")
    args = ap.parse_args()

    df = pd.read_csv(args.data, parse_dates=["date"])
    regions = sorted(df["region"].unique())
    all_fc, metrics = [], []

    fig_rows = int(np.ceil(len(regions)/3))
    plt.figure(figsize=(16, 4*fig_rows))

    for i, r in enumerate(regions, 1):
        sub = df[df.region==r].sort_values("date")
        ts = sub.set_index("date")["demand"].asfreq("7D")
        # 回测：最后8周
        train, test = ts.iloc[:-args.horizon], ts.iloc[-args.horizon:]
        _, fc = fit_and_forecast(train, args.horizon)
        metrics.append({"region": r, "mape_last8": round(float(mape(test.values, fc.values)),2)})

        # 全量拟合得到未来预测
        _, fc_full = fit_and_forecast(ts, args.horizon)
        future_idx = pd.date_range(ts.index[-1] + pd.Timedelta(days=7), periods=args.horizon, freq="7D")
        all_fc.append(pd.DataFrame({"region": r, "date": future_idx, "yhat": fc_full.values}))

        # 近30周 + 预测
        plt.subplot(fig_rows, 3, i)
        plt.plot(ts.iloc[-30:].index, ts.iloc[-30:].values, label="Actual")
        plt.plot(future_idx, fc_full.values, marker="o", label="Forecast")
        plt.title(f"{r} (MAPE last 8w: {metrics[-1]['mape_last8']}%)")
        plt.xlabel("Week"); plt.ylabel("Units"); plt.legend()

    out = pd.concat(all_fc, ignore_index=True)
    out.to_csv(args.out_csv, index=False)
    plt.tight_layout(); plt.savefig(args.out_png, dpi=160)
    print(f"Wrote {args.out_csv} ({len(out)} rows) & {args.out_png}")
    print("Per-region MAPE (last 8 weeks):", metrics)

if __name__ == "__main__":
    main()
