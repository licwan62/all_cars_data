# Mercedes-Benz E-Class 定制分析

## 结论与范围

区域：US；精确车型：Mercedes-Benz E-Class；结构：Sedan。
15 条尺寸记录形成 2 个尺寸候选 SKU。跨代际共版须完成外形核验和实车打样。


## 差评依据

B0 当前输出未命中本范围的差评记录；不推定没有适配问题，也不计算差评比例。

## 方法与尺寸候选 SKU

L/W/H 跨度阈值：250/150/100 mm。L-MM 作为长度代理。按长度降序贪心分配，保持原分析算法；不保证所有输入上的全局最优。自动尺码、销量和参考链接不参与聚簇。

| 候选 SKU | 车型代号 | 记录数 | L/mm | W/mm | H/mm | 最大包络/mm | 代表车型 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SKU-01 | 23019495 | 1 | 4755–4755（跨度 0） | 1740–1740（跨度 0） | 1430–1430（跨度 0） | 4755 × 1740 × 1430 | Mercedes-Benz E-Class Sedan 1994-1995 US |
| SKU-02 | 23019626 | 14 | 4818–4989（跨度 171） | 1798–1928（跨度 130） | 1440–1483（跨度 43） | 4989 × 1928 × 1483 | Mercedes-Benz E-Class AMG Sedan 2020-2022 US |

各维度最大值可能来自不同车型，代表车型不一定达到三项最大值。包络是车辆外廓，不是成品车衣的放量或裁片尺寸。

## 完整成员明细

| 候选 SKU | DIMENSION-ID | 原子代号 | 年款 | 代际 | 版本 | 结构 | L/mm | W/mm | H/mm | 尺寸组销量 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SKU-01 | Mercedes-Benz E-Class Sedan 1994-1995 US | 23019495 | 1994-1995 | gen1 | — | Sedan | 4755 | 1740 | 1430 | 20500 |
| SKU-02 | Mercedes-Benz E-Class AMG Sedan 1999-2002 US | 23019902 | 1999-2002 | gen2 | AMG | Sedan | 4818 | 1798 | 1440 | 18681 |
| SKU-02 | Mercedes-Benz E-Class AMG Sedan 2003-2006 US | 23010306 | 2003-2006 | gen3 | AMG | Sedan | 4818 | 1811 | 1453 | 20827 |
| SKU-02 | Mercedes-Benz E-Class Sedan 1996-2002 US | 23019602 | 1996-2002 | gen2 | — | Sedan | 4836 | 1798 | 1463 | 205181 |
| SKU-02 | Mercedes-Benz E-Class AMG Sedan 2007-2009 US | 23010709 | 2007-2009 | gen3 | AMG | Sedan | 4851 | 1821 | 1483 | 9264 |
| SKU-02 | Mercedes-Benz E-Class Sedan 2003-2009 US | 23010309 | 2003-2009 | gen3 | — | Sedan | 4851 | 1821 | 1483 | 140427 |
| SKU-02 | Mercedes-Benz E-Class Sedan 2010-2016 US | 23011016 | 2010-2016 | gen4 | — | Sedan | 4879 | 1928 | 1471 | 111262 |
| SKU-02 | Mercedes-Benz E-Class AMG Sedan 2010-2016 US | 23011016 | 2010-2016 | gen4 | AMG | Sedan | 4900 | 1872 | 1466 | 23844 |
| SKU-02 | Mercedes-Benz E-Class Sedan 2017-2023 US | 23011723 | 2017-2023 | gen5 | — | Sedan | 4935 | 1872 | 1468 | 55333 |
| SKU-02 | Mercedes-Benz E-Class AMG Sedan 2017-2018 US | 23011718 | 2017-2018 | gen5 | AMG | Sedan | 4943 | 1852 | 1448 | 4844 |
| SKU-02 | Mercedes-Benz E-Class PHEV Sedan 2024-2026 US | 23012426 | 2024-2026 | gen6 | PHEV | Sedan | 4950 | 1880 | 1471 | 11779 |
| SKU-02 | Mercedes-Benz E-Class Sedan 2025-2026 US | 23012526 | 2025-2026 | gen6 | — | Sedan | 4950 | 1902 | 1471 | 13813 |
| SKU-02 | Mercedes-Benz E-Class AMG Sedan 2019 US | 23011919 | 2019 | gen5 | AMG | Sedan | 4958 | 1859 | 1448 | 2040 |
| SKU-02 | Mercedes-Benz E-Class AMG Sedan 2023 US | 23012323 | 2023 | gen5 | AMG | Sedan | 4983 | 1908 | 1458 | 1111 |
| SKU-02 | Mercedes-Benz E-Class AMG Sedan 2020-2022 US | 23012022 | 2020-2022 | gen5 | AMG | Sedan | 4989 | 1908 | 1448 | 3863 |

## Sketchfab 参考任务

链接检索登记日期：2026-10-09。链接已找到表示参考候选，尚未完成外形与真实比例验证。

| 候选 SKU | 代际 | 覆盖车型 | 状态 | 核验项目 |
| --- | --- | --- | --- | --- |
| SKU-01 | W124 | Mercedes-Benz E-Class Sedan 1994-1995 US | 待外形核验 | 车顶弧线；前后轮廓；后视镜位置；尾门及扰流板；跨代际共版可行性 |
| SKU-02 | W210 | Mercedes-Benz E-Class Sedan 1996-2002 US；Mercedes-Benz E-Class AMG Sedan 1999-2002 US | 待外形核验 | 车顶弧线；前后轮廓；后视镜位置；尾门及扰流板；跨代际共版可行性 |
| SKU-02 | W211 | Mercedes-Benz E-Class AMG Sedan 2007-2009 US；Mercedes-Benz E-Class Sedan 2003-2009 US；Mercedes-Benz E-Class AMG Sedan 2003-2006 US | 待外形核验 | 车顶弧线；前后轮廓；后视镜位置；尾门及扰流板；跨代际共版可行性 |
| SKU-02 | W212 | Mercedes-Benz E-Class AMG Sedan 2010-2016 US；Mercedes-Benz E-Class Sedan 2010-2016 US | 待外形核验 | 车顶弧线；前后轮廓；后视镜位置；尾门及扰流板；跨代际共版可行性 |
| SKU-02 | W213 | Mercedes-Benz E-Class AMG Sedan 2020-2022 US；Mercedes-Benz E-Class AMG Sedan 2023 US；Mercedes-Benz E-Class AMG Sedan 2019 US；Mercedes-Benz E-Class AMG Sedan 2017-2018 US；Mercedes-Benz E-Class Sedan 2017-2023 US | 待外形核验 | 车顶弧线；前后轮廓；后视镜位置；尾门及扰流板；跨代际共版可行性 |
| SKU-02 | W214 | Mercedes-Benz E-Class Sedan 2025-2026 US；Mercedes-Benz E-Class PHEV Sedan 2024-2026 US | 待补参考模型 | 车顶弧线；前后轮廓；后视镜位置；尾门及扰流板；跨代际共版可行性 |

## Sketchfab 检索与完整参考链接


### W124

检索式：`site:sketchfab.com/3d-models Mercedes-Benz E-Class W124 sedan`

- [E-Class Mk2 W124](https://sketchfab.com/3d-models/mercedes-benz-e-class-mk2w124-81b317899e9641d9ac08f0be4fd09fac)
- [W124 220E](https://sketchfab.com/3d-models/mercedes-benz-w124-220e-eab4f77956a245fcad7bf5404440f31a)

### W210

检索式：`site:sketchfab.com/3d-models Mercedes-Benz E-Class W210 sedan`

- [E-Class W210 Sedan](https://sketchfab.com/3d-models/mercedes-benz-e-class-w210-sedan-ca4387f139da4dc8a51c1abd2edd01c1)
- [2002 E320 W210 4Matic Sedan](https://sketchfab.com/3d-models/2002-mercedes-benz-e320-w210-4matic-sedan-5ddd3b440cf0496782948d765b8ef0c4)

### W211

检索式：`site:sketchfab.com/3d-models Mercedes-Benz E-Class W211 sedan`

- [E-Class W211 2002-2009](https://sketchfab.com/3d-models/mercedes-benz-klasy-e-iii-w211-2002-2009-eeec59df77404b7082498bbe63034ecf)
- [E200 Kompressor W211](https://sketchfab.com/3d-models/mercedes-benz-e-class-w211-e200-kompressor-c0e4910155f44e2fb298c5692000d262)

### W212

检索式：`site:sketchfab.com/3d-models Mercedes-Benz E-Class W212 sedan`

- [E-Class W212](https://sketchfab.com/3d-models/mercedes-benz-e-class-w212-9b70707fd2304f578175158564719c5d)
- [Mercedes E-Class W212](https://sketchfab.com/3d-models/mercedes-e-class-w212-e86ac95cbfa1448b8246950450757a0d)

### W213

检索式：`site:sketchfab.com/3d-models Mercedes-Benz E-Class W213 sedan`

- [E-Class W213 2016-2021](https://sketchfab.com/models/468fd13bf3d64d658b420497dcb5fa80/embed)

### W214

检索式：`site:sketchfab.com/3d-models Mercedes-Benz E-Class W214 sedan`

- 待补可靠参考模型。

## 打样验收与待确认事项

1. 每个拟共版 SKU 验证 L/W/H 极值车型，拍摄前、侧、后与镜耳位置；记录偏大、偏小、偏长、偏短及下摆覆盖。
2. 核对车顶弧线、尾门、扰流板和镜耳位置；跨代际外形差异无法通过放量解决时拆分 SKU。
3. 记录样品重量、安装用时及前后方向辨识；镜耳位置通过实车测量确认，不依据缺失的耳位反馈指定靠前或靠后。
4. 补充购买年款、实际尺码、偏差部位与照片，并回填差评人工台账。


## 输入来源与追踪

规则位于本节点 data/；规则 sha256、Git 版本及输入引用详见批次 run.json。

| 节点 | 输入 | 上游版本 | sha256 | 来源 artifact |
| --- | --- | --- | --- | --- |
| size-calculation | US/全量/全量表.csv | 20261009_04 | d6472a71893a8ee6a70b53fc1a5eda25e3d158ae3ddd95094c0e863251724965 | A0.尺码计算/artifacts/2026-10-09_04_size-calculation-release/output/US/全量/全量表-20261009_04.csv |
| code-mapping | 尺寸编码映射.csv | 20261009_04 | e9312b10b0589293e6ebeea0b169f09ec9578baa0a290215ed74b48706bde445 | 02.代码映射/artifacts/2026-10-09_04_code-mapping-release/output/尺寸编码映射-20261009_04.csv |
| negative-review-analysis | 差评分析表.csv | 20261009_04 | df162b43a6c7daf208d15ba08089022422cb9d256f0cf2089027d8659593189c | B0.差评分析/artifacts/2026-10-09_04_negative-review-analysis-release/output/差评分析表-20261009_04.csv |
