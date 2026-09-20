# 链接分析 Agent

负责 SKU、发货和车型链接关系分析。人工匹配规则放在 `data/`，当前分析结果写入 `output/`，运行历史写入 `artifacts/`。

上游：尺码计算、聚类 SKU 和销量评估节点的 `output/`。
