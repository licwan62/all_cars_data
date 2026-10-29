# 销量评估 Agent

负责生成车型原子销量。稳定交付物是 `output/原子销量.csv`（US，`python scripts/run_pipeline.py`）与 `output/RU代理销量.csv`（`python scripts/build_ru_proxy_sales.py`：`data/ru/auto_ru_model_sales_with_match_key.csv` 的 Auto.ru 在售样本按 match_key 汇总，经 01 `output/来源映射_RU.csv` 落到 RU DIMENSION-ID，无样本的为 0）；流水线配置在 `data/config.json`；分配规则和人工证据属于 `data/`，缓存、队列与工作表不供下游读取。

上游：`01.整理尺寸库`。遵守仓库根目录 `AGENTS.md`。


市场潜力由 `python scripts/build_market_potential.py` 从01 `output/尺寸库_US.csv` 和自身 `output/原子销量.csv` 生成，内部稳定接口 `output/市场潜力.csv`（DIMENSION-ID、市场潜力、销量潜力调整）。参数、销售来源CSV、来源元数据与算法维护说明统一在 `data/商业潜力调整/`；每次运行用 RunBatch 保留追溯及明细，不读 A0 数据或代码。
