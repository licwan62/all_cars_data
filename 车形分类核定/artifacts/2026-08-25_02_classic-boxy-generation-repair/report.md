# 方正老爷车代际清单回归修复

本批次以 `D:\Licheng\Workflow\all_cars_data\车形分类核定\changes\2026-08-25_01_all-dimension-generation-review\correct.csv` 为变更对比基线，以分类结构审核最新规范快照为输入，将车形规则落实到全部 `4,354` 个 `DIMENSION-ID`。本轮未写入 `source` 目录。

## 核定规则

- `STRUCTURE` 只用于定位分支，不直接映射 `30/31/32`。
- 方形宽车头是 `32` 最高优先级特征；确认后不再与 `31` 比较。
- `31` 仅在排除方形宽车头后，按低矮、下宽上窄的实际比例核定。
- `20/21` 按车头收窄和前角轮廓逐代复核。
- 2000 年以前历史车型逐条审计，仅复用已独立核定的同代轮廓结论。

## 结果统计

- 全量结果：4,354 条，唯一 ID 4,354 个。
- 2000 年以前重点审计：2,042 条。
- 对比基线的增量记录：250 条；`RECLASSIFY` 250，`ADD` 0，`REMOVE` 0。
- 其中 239 条方正代际恢复为 `32`：`30→32` 227 条，`31→32` 12 条。
- Lincoln Continental 不再被整车系误当作 Low Sport；11 条非方正代际由 `31` 修正为 `30`。
- 方正老爷车注册表现有 102 个代际，全部通过 `classic_boxy_generation_coverage` 验收。
- 车形分布：0=230, 1=176, 10=20, 11=39, 20=342, 21=199, 25=63, 26=69, 30=814, 31=651, 32=816, 40=347, 41=431, 42=96, 50=61。
- 非独立代际的 3x 失败：0。
- 机器验收：PASS。

## 文件说明

- `correct.csv`：本批次完成时的全量 `DIMENSION-ID,车形` 快照。
- `changes.csv`：相对基线的实际新增、删除和改类。
- `all_dimension_audit.csv/json`：全 ID 逐条判定与摘要。
- `hatch_wagon_front_review.json`：`20/21` 前脸边界复核。
- `classic_shape_review.json`：历史车型轮廓复核。
- `generation_shape_review.json`：`30/31/32` 代际缓存和结构直映射清理审计。
- `classic_boxy_regression_audit.json`：旧 32 降级候选的机器回溯；216 条全部有明确去向，无未解释回归。
- `validation.json`：本批次机器验收结果。

## 保留风险

- 对旧快照中 216 条“原 32、重建后非 32”的同 ID 记录逐项回溯：188 条方正三厢分支已恢复 `32`，16 条 Bel Air Wagon 依固定类别保持 `21`，12 条圆化/收窄代际经显式复核保持 `30`。
- 显式排除的 12 条包含 Q45 gen1/gen2、XJ gen1、LS gen2、Continental gen8、Legacy gen1、Corolla gen5 和 Passat gen3；它们不再使用无证据的默认说明。
- 新证据如推翻已核代际，应追加新批次，不覆盖本快照。
