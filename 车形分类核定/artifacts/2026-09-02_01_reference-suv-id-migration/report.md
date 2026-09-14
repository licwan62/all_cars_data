# 依据 reference.csv 的新版 SUV 车形编号迁移

本批次以 `D:\Licheng\Workflow\all_cars_data\车形分类核定\changes\2026-08-25_05_verified-atomic-gap-shapes\correct.csv` 为变更对比基线，以分类结构审核最新规范快照为输入，将车形规则落实到全部 `4,354` 个 `DIMENSION-ID`。本轮未写入 `source` 目录。

## 核定规则

- `STRUCTURE` 只用于定位分支，不直接映射 `30/31/32`。
- 方形宽车头是 `32` 最高优先级特征；确认后不再与 `31` 比较。
- `31` 仅在排除方形宽车头后，按低矮、下宽上窄的实际比例核定。
- `20/21` 按车头收窄和前角轮廓逐代复核。
- SUV 编号按 `reference.csv` 的结构细分迁移：旧 `40 Boxy` → 新 `42 Boxy`，旧 `41 Conventional` → 新 `40 Conventional`，旧 `42 Fastback` → 新 `41 Fastback`。
- 2000 年以前历史车型逐条审计，仅复用已独立核定的同代轮廓结论。

## 结果统计

- 全量结果：4,354 条，唯一 ID 4,354 个。
- 2000 年以前重点审计：2,042 条。
- 对比基线的增量记录：8,796 条；`RECLASSIFY` 0，`ADD` 4,354，`REMOVE` 4,442。
- 共迁移 288 条 SUV 缓存规则；当前结果中 874 条 SUV 记录按新版 `40/41/42` 语义输出。
- 车形分布：0=230, 1=176, 10=20, 11=39, 20=342, 21=199, 25=63, 26=69, 30=759, 31=636, 32=886, 40=431, 41=96, 42=347, 50=61。
- 非独立代际的 3x 失败：0。
- 机器验收：PASS。

## 文件说明

- `correct.csv`：本批次完成时的全量 `DIMENSION-ID,车形` 快照。
- `changes.csv`：相对基线的实际新增、删除和改类。
- `all_dimension_audit.csv/json`：全 ID 逐条判定与摘要。
- `hatch_wagon_front_review.json`：`20/21` 前脸边界复核。
- `classic_shape_review.json`：历史车型轮廓复核。
- `generation_shape_review.json`：`30/31/32` 代际缓存和结构直映射清理审计。
- `suv_shape_id_migration.json`：依据 `reference.csv` 将旧 SUV 编号语义迁移至新版 `40/41/42` 的审计。
- `validation.json`：本批次机器验收结果。

## 保留风险

- `ADD/REMOVE` 中包含上游年份合并、结构原子化和 `DIMENSION-ID` 重组，不应解读为单纯车形改类。
- 本批次与上一批次之间的 `DIMENSION-ID` 展示格式已整体重组，因此 `changes.csv` 呈现为 4,354 条 `ADD` 和 4,442 条 `REMOVE`；SUV 语义迁移的可审计明细以 `suv_shape_id_migration.json` 为准。
- 新证据如推翻已核代际，应追加新批次，不覆盖本快照。
