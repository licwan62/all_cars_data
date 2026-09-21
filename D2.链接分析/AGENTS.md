# 链接分析 Agent

除本节点自身交付物外，本节点维护仓库根目录的 `pipeline.json`：新增、移除或调整节点、依赖、交付物和 `pending` 时须同步更新该文件，并运行 `python scripts/validate_pipeline_structure.py`。

负责 SKU、发货和车型链接关系分析。人工匹配规则放在 `data/`，当前分析结果写入 `output/`，运行历史写入 `artifacts/`。

上游：尺码计算、聚类 SKU 和销量评估节点的 `output/`。
