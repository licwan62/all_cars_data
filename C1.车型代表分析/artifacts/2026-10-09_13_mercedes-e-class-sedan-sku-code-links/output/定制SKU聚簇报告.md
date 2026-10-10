# Mercedes-Benz E-Class 定制 SKU 聚簇分析

范围：Sedan。目标：在 L/W/H 包络阈值内，最少化 SKU 数量。未读取或引用自动尺码。

有效长度：A0 无单独字段，使用 L-MM 作为可获得的有效长度代理，并先满足其 150 mm 最大跨度。

阈值：L ≤ 150 mm；W ≤ 100 mm；H ≤ 80 mm。

结论：15 个 E-Class 原子记录压缩为 2 个 L/W/H SKU 聚簇。

## SKU 包络

| SKU | 车型数 | SKU车型代号（含年份） | L 范围 | W 范围 | H 范围 | 包络建议 | 代表车型 | Sketchfab |
|---|---:|---|---:|---:|---:|---|---|---|
| E-CLUSTER-01 | 6 | 23019409 | 4755–4851 | 1740–1821 | 1430–1483 | 4851×1821×1483 | Mercedes-Benz E-Class AMG Sedan 2007-2009 US | [查看模型](https://sketchfab.com/3d-models/mercedes-benz-klasy-e-iii-w211-2002-2009-eeec59df77404b7082498bbe63034ecf) |
| E-CLUSTER-02 | 9 | 23011026 | 4879–4989 | 1852–1928 | 1448–1471 | 4989×1928×1471 | Mercedes-Benz E-Class AMG Sedan 2020-2022 US | [查看模型](https://sketchfab.com/models/468fd13bf3d64d658b420497dcb5fa80/embed) |

## Sketchfab 检索

检索词、日期和选中链接见 `Sketchfab检索记录.csv`。链接仅用于外形核验，不参与 SKU 聚簇。
