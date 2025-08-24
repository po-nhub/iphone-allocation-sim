# iPhone Allocation Simulator
[![CI](https://github.com/po-nhub/iphone-allocation-sim/actions/workflows/ci.yml/badge.svg)](https://github.com/po-nhub/iphone-allocation-sim/actions)
![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
Demand forecasting (ARIMA) + allocation optimization (LP via PuLP) for regional iPhone launch.

## 🔥 TL;DR (Screenshots)
<p float="left">
  <img src="reports/mape_bar.png" width="32%" />
  <img src="reports/fillrate_bar.png" width="32%" />
  <img src="reports/allocation_heatmap.png" width="32%" />
</p>

## Quickstart
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
./run.sh
```


## Recruiter summary
See: reports/summary.md

## Forecast panels (per region)
<img src="reports/forecast_demo.png" width="100%" />

![CI](https://github.com/po-nhub/iphone-allocation-sim/actions/workflows/ci.yml/badge.svg)
