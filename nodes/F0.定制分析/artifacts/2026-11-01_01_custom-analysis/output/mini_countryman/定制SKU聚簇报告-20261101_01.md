# MINI Countryman 定制 SKU 聚簇分析

## 结论与范围

区域：US；车系范围：MINI Countryman；结构：SUV。
5 条尺寸记录形成 2 个尺寸候选 SKU。跨代际共版须完成外形核验和实测适配验证。


## 差评依据

| 结构 | 记录尺码 | 差评数量 | 主要原因 | 严重度 | 评价总数 | 差评占比 | 年份 | 更新时间 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SUV | YM+ | 2 | 太薄(1)；尺寸太大(1) | 低 | 未提供 | 未提供 | 未提供 | 2026-09-22 |

同一评价可能涉及多个原因，原因次数不能相加当作独立差评数。缺少年款和偏差方向时，不能直接归因至具体 SKU，也不能决定整体加大或缩小。

## 方法与尺寸候选 SKU

L/W/H 跨度阈值：250/150/100 mm。L-MM 作为长度代理。按长度降序贪心分配，保持原分析算法；不保证所有输入上的全局最优。自动尺码、销量和参考链接不参与聚簇。

| 候选 SKU | 车型代号 | 记录数 | L/mm | W/mm | H/mm | 最大包络/mm | 代表车型 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SKU-01 | 32031116 | 2 | 4110–4143（跨度 33） | 1788–1788（跨度 0） | 1562–1562（跨度 0） | 4143 × 1788 × 1562 | MINI Countryman JCW SUV 2016 US |
| SKU-02 | 32031726 | 3 | 4313–4448（跨度 135） | 1821–1844（跨度 23） | 1557–1656（跨度 99） | 4448 × 1844 × 1656 | MINI Countryman SUV 2025-2026 US |

各维度最大值可能来自不同车型，代表车型不一定达到三项最大值。包络是车辆外廓，不是成品车衣的放量或裁片尺寸。

## 完整成员明细

| 候选 SKU | DIMENSION-ID | 原子代号 | 年款 | 代际 | 版本 | 结构 | L/mm | W/mm | H/mm | 尺寸组销量 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SKU-01 | MINI Countryman SUV 2011-2015 US | 32031115 | 2011-2015 | gen1 | — | SUV | 4110 | 1788 | 1562 | 90205 |
| SKU-01 | MINI Countryman JCW SUV 2016 US | 32031616 | 2016 | gen1 | JCW | SUV | 4143 | 1788 | 1562 | 12706 |
| SKU-02 | MINI Countryman JCW SUV 2018 US | 32031818 | 2018 | gen2 | JCW | SUV | 4313 | 1821 | 1557 | 8783 |
| SKU-02 | MINI Countryman SUV 2017-2024 US | 32031724 | 2017-2024 | gen2 | — | SUV | 4313 | 1821 | 1557 | 100856 |
| SKU-02 | MINI Countryman SUV 2025-2026 US | 32032526 | 2025-2026 | gen3 | — | SUV | 4448 | 1844 | 1656 | 26500 |

## 通用尺码适配风险

按候选 SKU 对照成员在 A0 中的自动尺码；“自动长度余量”与“参考侧高”是现有计算字段，不是实测镜耳或发动机舱坐标。

| 候选 SKU | 车型代号 | 记录数 | 自动尺码×条数 | 自动长度余量/mm | 参考侧高/mm |
| --- | --- | --- | --- | --- | --- |
| SKU-01 | 32031116 | 2 | YM×2 | 487–520（跨度 33） | 1183–1183（跨度 0） |
| SKU-02 | 32031726 | 3 | YM×3 | 182–317（跨度 135） | 1192–1279（跨度 87） |

### 风险解读

- SKU-01：YM 与 SKU-02 共用，现行尺码区分不了这些候选。
- SKU-02：YM 与 SKU-01 共用，现行尺码区分不了这些候选；长度余量相差 135 mm，同一版型松紧不一。

全量表缺少镜耳位置和车顶/尾门曲线坐标，镜耳前后与外伸须按代际实测，不能由总宽或发动机布局推定。

## Sketchfab 参考任务

链接检索登记日期：2026-10-09。链接已找到表示参考候选，尚未完成外形与真实比例验证。

| 候选 SKU | 代际 | 覆盖车型 | 状态 | 核验项目 |
| --- | --- | --- | --- | --- |
| SKU-01 | R60 | MINI Countryman JCW SUV 2016 US；MINI Countryman SUV 2011-2015 US | 待外形核验 | 车顶弧线；前后轮廓；后视镜位置；尾门及扰流板；跨代际共版可行性 |
| SKU-02 | F60 | MINI Countryman JCW SUV 2018 US；MINI Countryman SUV 2017-2024 US | 待外形核验 | 车顶弧线；前后轮廓；后视镜位置；尾门及扰流板；跨代际共版可行性 |
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

## 适配核验与待确认事项

1. 每个拟共版 SKU 验证 L/W/H 极值车型，拍摄前、侧、后与镜耳位置；记录偏大、偏小、偏长、偏短及下摆覆盖。
2. 核对车顶弧线、尾门、扰流板和镜耳位置；跨代际外形差异无法通过放量解决时拆分 SKU。
3. 记录样品重量、安装用时及前后方向辨识；镜耳位置通过实车测量确认，不依据缺失的耳位反馈指定靠前或靠后。
4. 补充购买年款、实际尺码、偏差部位与照片，并回填差评人工台账。


## 输入来源与追踪

规则位于本节点 data/；规则 sha256、Git 版本及输入引用详见批次 run.json。

| 节点 | 输入 | 上游版本 | sha256 | 来源 artifact |
| --- | --- | --- | --- | --- |
| size-calculation | US/全量/全量表.csv | 20261101_07 | 563ef622ff706624b5eff237648b8601039002345ac41b246aa5bfcfd389bdc4 | nodes/A0.尺码计算/artifacts/2026-10-28_01_us-market-potential/output/US/全量/全量表-20261028_01.csv |
| code-mapping | 尺寸编码映射.csv | 20261019_02 | cc8c22d408a4a09098db1833a87dc523fbdef2c1c0051a50c3a252661c5e51d8 | nodes/02.代码映射/artifacts/2026-10-19_02_code-mapping-release/output/尺寸编码映射-20261019_02.csv |
| negative-review-analysis | 差评分析表.csv | 20261009_04 | df162b43a6c7daf208d15ba08089022422cb9d256f0cf2089027d8659593189c | nodes/B0.差评分析/artifacts/2026-10-09_04_negative-review-analysis-release/output/差评分析表-20261009_04.csv |
