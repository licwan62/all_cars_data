# 链接分析 Agent

除本节点自身交付物外，本节点维护仓库根目录的 `pipeline.json`：新增、移除或调整节点、依赖、交付物和 `pending` 时须同步更新该文件，并运行 `python scripts/validate_pipeline_structure.py`。

负责 SKU、发货和车型链接关系分析。人工匹配规则放在 `data/`，当前分析结果写入 `output/`，运行历史写入 `artifacts/`。

上游：尺码计算、发货评估和销量评估节点的 `output/`。

## 子项目登记

D2 根目录同时是业务容器：已形成稳定交付的子项目在 `pipeline.json` 单独登记为节点，自带 `AGENTS.md`、`data/`、`output/`、`artifacts/`、代码与测试，正式资料归其自身 `data/`，本节点不再承载其运行、测试与发布。

| 子项目 | 节点 id | 状态 |
| --- | --- | --- |
| `皮卡/` | `link-analysis-pickup` | 已登记（2026-10-19） |
| `W型车/` | 本节点 | 待接入：历史流程等待 D1 的 W型车聚类接口；D1 当前发布发货评估表 |
| `sku_shipment_analysis/` | 本节点 | 共享引擎与回归测试，无独立交付 |
