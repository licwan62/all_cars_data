# 聚类 SKU Agent

负责按车型、尺码和销量生成 SKU 聚类结果。自身合并规则放在 `data/`，当前交付物写入 `output/`，每轮聚类留存在 `artifacts/`。

上游：尺码计算和销量评估节点的 `output/`。
