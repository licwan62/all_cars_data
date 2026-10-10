# Mercedes-Benz E-Class 定制 SKU 聚簇分析

范围：Sedan。目标：在 L/W/H 包络阈值内，最少化 SKU 数量。未读取或引用自动尺码。

有效长度：A0 无单独字段，使用 L-MM 作为可获得的有效长度代理，并先满足其 250 mm 最大跨度。

阈值：L ≤ 250 mm；W ≤ 150 mm；H ≤ 100 mm。

方法：先按有效长度代理（L-MM）从大到小分配，再选择产生最紧 L/W/H 包络的可行 SKU。结构、自动尺码、销量与 Sketchfab 链接均不参与聚簇。

结论：15 个 E-Class 原子记录压缩为 2 个 L/W/H SKU 聚簇。

## SKU 包络

| SKU | 车型数 | SKU车型代号（含年份） | L 范围 | W 范围 | H 范围 | 包络建议 | 代表车型 | 核验链接数 |
|---|---:|---|---:|---:|---:|---|---|---:|
| E-CLUSTER-01 | 1 | 23019495 | 4755–4755 | 1740–1740 | 1430–1430 | 4755×1740×1430 | Mercedes-Benz E-Class Sedan 1994-1995 US | 2 |
| E-CLUSTER-02 | 14 | 23019626 | 4818–4989 | 1798–1928 | 1440–1483 | 4989×1928×1483 | Mercedes-Benz E-Class AMG Sedan 2020-2022 US | 7 |

## Sketchfab 外形核验链接

链接仅用于外形核验，不参与 L/W/H 聚簇。W214 暂未找到可可靠核验的 Sketchfab Sedan 模型。

### E-CLUSTER-01

- W124 · [E-Class Mk2 W124](https://sketchfab.com/3d-models/mercedes-benz-e-class-mk2w124-81b317899e9641d9ac08f0be4fd09fac)
- W124 · [W124 220E](https://sketchfab.com/3d-models/mercedes-benz-w124-220e-eab4f77956a245fcad7bf5404440f31a)

### E-CLUSTER-02

- W210 · [E-Class W210 Sedan](https://sketchfab.com/3d-models/mercedes-benz-e-class-w210-sedan-ca4387f139da4dc8a51c1abd2edd01c1)
- W210 · [2002 E320 W210 4Matic Sedan](https://sketchfab.com/3d-models/2002-mercedes-benz-e320-w210-4matic-sedan-5ddd3b440cf0496782948d765b8ef0c4)
- W211 · [E-Class W211 2002-2009](https://sketchfab.com/3d-models/mercedes-benz-klasy-e-iii-w211-2002-2009-eeec59df77404b7082498bbe63034ecf)
- W211 · [E200 Kompressor W211](https://sketchfab.com/3d-models/mercedes-benz-e-class-w211-e200-kompressor-c0e4910155f44e2fb298c5692000d262)
- W212 · [E-Class W212](https://sketchfab.com/3d-models/mercedes-benz-e-class-w212-9b70707fd2304f578175158564719c5d)
- W212 · [Mercedes E-Class W212](https://sketchfab.com/3d-models/mercedes-e-class-w212-e86ac95cbfa1448b8246950450757a0d)
- W213 · [E-Class W213 2016-2021](https://sketchfab.com/models/468fd13bf3d64d658b420497dcb5fa80/embed)
- W214 · 未发现可可靠核验模型

## 设计边界

包络建议是 L/W/H 外廓聚簇结果，不等于成品罩的放量、松量、镜袋、天线位或面料收缩量；这些工艺参数需要在打样阶段另行定义。
