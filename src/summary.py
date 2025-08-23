import pandas as pd, pathlib as p
mape = pd.read_csv("reports/mape.csv")
fill = pd.read_csv("reports/fillrate.csv")
alloc = pd.read_csv("reports/allocation.csv", parse_dates=["date"])
overall_fill = (alloc["alloc"].sum()/alloc["demand"].sum()*100)

lines = []
lines += ["# Project Summary", ""]
lines += ["**Forecast → Constrained Allocation → KPIs** pipeline for SEA iPhone launch.", ""]
lines += ["## Forecast quality (MAPE, last 8 weeks)", mape.to_markdown(index=False), ""]
lines += ["## Service level by region (Fill Rate %)", fill.to_markdown(index=False), ""]
lines += [f"**Overall Fill Rate:** {overall_fill:.2f}%", ""]
lines += ["## Artifacts",
          "- reports/mape_bar.png",
          "- reports/fillrate_bar.png",
          "- reports/allocation_heatmap.png",
          "- reports/forecast_demo.png", ""]
p.Path("reports/summary.md").write_text("\n".join(lines), encoding="utf-8")
print("Wrote reports/summary.md")
