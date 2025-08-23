#!/usr/bin/env bash
set -e
# 1) 合成数据
python -m src.sim_data --weeks 60 --seed 7
# 2) 预测
python -m src.forecast --horizon 8
# 3) 配额优化
python -m src.allocation --supply_ratio 0.9 --min_service 0.85 --max_share 0.6
# 4) KPI 图
python -m src.metrics_and_plots --horizon 8 --min_service 0.85
echo "✅ Pipeline finished. See reports/ for outputs."
