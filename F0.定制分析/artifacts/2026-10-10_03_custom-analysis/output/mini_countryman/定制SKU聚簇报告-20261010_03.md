# MINI Countryman 定制 SKU 聚簇分析

## 结论与范围

区域：US；精确车型：MINI Countryman；结构：SUV。
4 条尺寸记录形成 2 个尺寸候选 SKU。跨代际共版须完成外形核验和实车打样。


## 差评依据

B0 当前输出未命中本范围的差评记录；不推定没有适配问题，也不计算差评比例。

## 方法与尺寸候选 SKU

L/W/H 跨度阈值：250/150/100 mm。L-MM 作为长度代理。按长度降序贪心分配，保持原分析算法；不保证所有输入上的全局最优。自动尺码、销量和参考链接不参与聚簇。

| 候选 SKU | 车型代号 | 记录数 | L/mm | W/mm | H/mm | 最大包络/mm | 代表车型 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SKU-01 | 32031116 | 2 | 4110–4143（跨度 33） | 1788–1788（跨度 0） | 1562–1562（跨度 0） | 4143 × 1788 × 1562 | MINI Countryman JCW SUV 2016 US |
| SKU-02 | 32031726 | 2 | 4313–4448（跨度 135） | 1821–1844（跨度 23） | 1557–1656（跨度 99） | 4448 × 1844 × 1656 | MINI Countryman SUV 2025-2026 US |

各维度最大值可能来自不同车型，代表车型不一定达到三项最大值。包络是车辆外廓，不是成品车衣的放量或裁片尺寸。

## 完整成员明细

| 候选 SKU | DIMENSION-ID | 原子代号 | 年款 | 代际 | 版本 | 结构 | L/mm | W/mm | H/mm | 尺寸组销量 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SKU-01 | MINI Countryman SUV 2011-2015 US | 32031115 | 2011-2015 | gen1 | — | SUV | 4110 | 1788 | 1562 | 90205 |
| SKU-01 | MINI Countryman JCW SUV 2016 US | 32031616 | 2016 | gen1 | JCW | SUV | 4143 | 1788 | 1562 | 12706 |
| SKU-02 | MINI Countryman SUV 2017-2024 US | 32031724 | 2017-2024 | gen2 | — | SUV | 4313 | 1821 | 1557 | 109639 |
| SKU-02 | MINI Countryman SUV 2025-2026 US | 32032526 | 2025-2026 | gen3 | — | SUV | 4448 | 1844 | 1656 | 26500 |

## Sketchfab 参考任务

链接检索登记日期：2026-10-09。链接已找到表示参考候选，尚未完成外形与真实比例验证。

| 候选 SKU | 代际 | 覆盖车型 | 状态 | 核验项目 |
| --- | --- | --- | --- | --- |
| SKU-01 | R60 | MINI Countryman JCW SUV 2016 US；MINI Countryman SUV 2011-2015 US | 待外形核验 | 车顶弧线；前后轮廓；后视镜位置；尾门及扰流板；跨代际共版可行性 |
| SKU-02 | F60 | MINI Countryman SUV 2017-2024 US | 待外形核验 | 车顶弧线；前后轮廓；后视镜位置；尾门及扰流板；跨代际共版可行性 |
| SKU-02 | U25 | MINI Countryman SUV 2025-2026 US | 待补参考模型 | 车顶弧线；前后轮廓；后视镜位置；尾门及扰流板；跨代际共版可行性 |

## Sketchfab 检索与完整参考链接


### R60

检索式：`site:sketchfab.com/3d-models MINI Countryman R60`

- [MINI Cooper Countryman 2016](https://sketchfab.com/3d-models/mini-cooper-countryman-2016-ef1dd8c383cb4a98a626236b4fe3aa15)
- [MINI Cooper Countryman lidar scan](https://sketchfab.com/3d-models/mini-cooper-countryman-lidar-scan-6ac9fdf2b07842efb4ac9e2fd9990f45)

### F60

检索式：`site:sketchfab.com/3d-models MINI Countryman F60`

- [2017 Countryman John Cooper Works](https://sketchfab.com/3d-models/2017-mini-countryman-john-cooper-works-2b3e8afed5d64ffea7d91f477636ef30)
- [Countryman S 2021](https://sketchfab.com/3d-models/mini-countryman-s-2021-3dce3429baeb4eb198993adc313c86e0)

### U25

检索式：`site:sketchfab.com/3d-models MINI Countryman U25 2025`

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
