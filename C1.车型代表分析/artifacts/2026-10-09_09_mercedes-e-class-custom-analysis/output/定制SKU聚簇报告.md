# Mercedes-Benz E-Class 定制 SKU 聚簇分析

目标：在 L/W/H 包络阈值内，最少化 SKU 数量。未读取或引用自动尺码。

有效长度：A0 无单独字段，使用 L-MM 作为可获得的有效长度代理，并先满足其 150 mm 最大跨度。

阈值：L ≤ 150 mm；W ≤ 100 mm；H ≤ 80 mm。

结论：30 个 E-Class 原子记录压缩为 5 个 L/W/H SKU 聚簇。

## SKU 包络

| SKU | 车型数 | L 范围 | W 范围 | H 范围 | 包络建议 | 代表车型 |
|---|---:|---:|---:|---:|---|---|
| E-CLUSTER-01 | 6 | 4671–4755 | 1740–1786 | 1394–1430 | 4755×1786×1430 | Mercedes-Benz E-Class Sedan 1994-1995 US |
| E-CLUSTER-02 | 1 | 4780–4780 | 1740–1740 | 1519–1519 | 4780×1740×1519 | Mercedes-Benz E-Class Wagon 1994-1995 US |
| E-CLUSTER-03 | 5 | 4818–4839 | 1798–1859 | 1440–1506 | 4839×1859×1506 | Mercedes-Benz E-Class Wagon 1998-2003 US |
| E-CLUSTER-04 | 2 | 4836–4879 | 1859–1928 | 1440–1471 | 4879×1928×1471 | Mercedes-Benz E-Class Sedan 2010-2016 US |
| E-CLUSTER-05 | 16 | 4851–4989 | 1821–1908 | 1448–1506 | 4989×1908×1506 | Mercedes-Benz E-Class AMG Sedan 2020-2022 US |

## Sketchfab 检索

检索词、日期和选中链接见 `Sketchfab检索记录.csv`。链接仅用于外形核验，不参与 SKU 聚簇。
