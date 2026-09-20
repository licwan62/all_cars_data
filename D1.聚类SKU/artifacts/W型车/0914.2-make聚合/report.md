# W 型车 MAKE 聚合实验

- 输入：`../0914/car_cluster_detail.csv`（811 条记录）
- 聚类主键：`逻辑尺码 + MAKE`；MODEL 不再参与聚类主键。
- 原 MODEL 聚类数：83
- MAKE 聚类数：45
- 减少聚类数：38
- 跨 MODEL 的 MAKE 聚类：23

## 审核重点

跨 MODEL 聚合只代表同品牌链接合并候选，不自动证明版型相同。优先检查长宽高跨度较大、年代跨度较大以及不同车形混合的聚合。

## 输出

- `make_cluster_summary.csv`：每个 `逻辑尺码 + MAKE` 一行。
- `make_cluster_detail.csv`：保留全部源记录及原 MODEL 聚类 ID。
- `model_to_make_cluster_mapping.csv`：原 MODEL 聚类到 MAKE 聚类的映射。
- `跨MODEL聚合审核.csv`：只保留 MODEL_COUNT > 1 的审核对象。
