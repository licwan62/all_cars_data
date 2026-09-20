# 皮卡 SKU 聚类

本目录发布皮卡车型的消费者适配聚类。一个 `PHYSICAL_SKU` 可以对应多个消费者 `CLUSTER_ID`，每条有效明细只归属于一个 Cluster。

## 文件

- `pickup_cluster_summary.csv`：聚类主表，每行一个消费者适配簇，`CLUSTER_ID` 唯一。
- `pickup_cluster_detail.csv`：通过校验的车型明细及其 Cluster、物理 SKU。
- `pickup_cluster_exceptions.csv`：未进入正式聚类、需要人工复核的记录。

## 发布统计

- Cluster：132
- 有效明细：598
- 异常记录：36
- 物理 SKU：8
- 真实原子事实：2,077
- 标题推断原子：2,201
- 物理 SKU 冲突原子：0
- 重复真实原子：0
- `SAFETY_PASS=False` 的 Cluster：60

## 聚类口径

- 物理 SKU、DRW/SRW、车型级别、CAB 和 BED 构成主要约束。
- `CLUSTER_ID` 使用持久化 `LINK-*` 标识，不由本次运行序号临时生成。
- `VALIDATION_STATUS=ACCEPT` 的 Cluster 才进入发布主表。
- `VALIDATION_STATUS=ACCEPT` 表示原子归属门禁通过，不等同于尺寸安全检查通过；使用方必须同时读取 `SAFETY_PASS`。
- `pickup_cluster_exceptions.csv` 保留无可用尺码、关键字段缺失等异常，不能视为正式适配关系。

候选生成代码、配置和研究资料保存在 `05.聚类SKU/artifacts/皮卡/`。
