# MINI Countryman 定制 SKU 聚簇分析

范围：SUV。目标：在 L/W/H 包络阈值内，最少化 SKU 数量。未读取或引用自动尺码。

有效长度：A0 无单独字段，使用 L-MM 作为可获得的有效长度代理，并先满足其 250 mm 最大跨度。

阈值：L ≤ 250 mm；W ≤ 150 mm；H ≤ 100 mm。

方法：先按有效长度代理（L-MM）从大到小分配，再选择产生最紧 L/W/H 包络的可行 SKU。结构、自动尺码、销量与 Sketchfab 链接均不参与聚簇。

结论：4 个 E-Class 原子记录压缩为 2 个 L/W/H SKU 聚簇。

## SKU 包络

| SKU | 车型数 | SKU车型代号（含年份） | L 范围 | W 范围 | H 范围 | 包络建议 | 代表车型 | 核验链接数 |
|---|---:|---|---:|---:|---:|---|---|---:|
| E-CLUSTER-01 | 2 | 32031116 | 4110–4143 | 1788–1788 | 1562–1562 | 4143×1788×1562 | MINI Countryman JCW SUV 2016 US | 2 |
| E-CLUSTER-02 | 2 | 32031726 | 4313–4448 | 1821–1844 | 1557–1656 | 4448×1844×1656 | MINI Countryman SUV 2025-2026 US | 2 |

## Sketchfab 外形核验链接

链接仅用于外形核验，不参与 L/W/H 聚簇。W214 暂未找到可可靠核验的 Sketchfab Sedan 模型。

### E-CLUSTER-01

- R60 · [MINI Cooper Countryman 2016](https://sketchfab.com/3d-models/mini-cooper-countryman-2016-ef1dd8c383cb4a98a626236b4fe3aa15)
- R60 · [MINI Cooper Countryman lidar scan](https://sketchfab.com/3d-models/mini-cooper-countryman-lidar-scan-6ac9fdf2b07842efb4ac9e2fd9990f45)

### E-CLUSTER-02

- F60 · [2017 Countryman John Cooper Works](https://sketchfab.com/3d-models/2017-mini-countryman-john-cooper-works-2b3e8afed5d64ffea7d91f477636ef30)
- F60 · [Countryman S 2021](https://sketchfab.com/3d-models/mini-countryman-s-2021-3dce3429baeb4eb198993adc313c86e0)
- U25 · 未发现可可靠核验模型

## 设计边界

包络建议是 L/W/H 外廓聚簇结果，不等于成品罩的放量、松量、镜袋、天线位或面料收缩量；这些工艺参数需要在打样阶段另行定义。
