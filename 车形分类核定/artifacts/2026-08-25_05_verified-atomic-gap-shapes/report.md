# 已核实原子缺口车形同步

本批次以 `D:\Licheng\Workflow\all_cars_data\车形分类核定\changes\2026-08-25_04_confirmed-branch-gap-shapes\correct.csv` 为变更对比基线，以分类结构审核最新规范快照为输入，将车形规则落实到全部 `4,442` 个 `DIMENSION-ID`。本轮未写入 `source` 目录。

## 核定规则

- `STRUCTURE` 只用于定位分支，不直接映射 `30/31/32`。
- 方形宽车头是 `32` 最高优先级特征；确认后不再与 `31` 比较。
- `31` 仅在排除方形宽车头后，按低矮、下宽上窄的实际比例核定。
- `20/21` 按车头收窄和前角轮廓逐代复核。
- 2000 年以前历史车型逐条审计，仅复用已独立核定的同代轮廓结论。

## 结果统计

- 全量结果：4,442 条，唯一 ID 4,442 个。
- 2000 年以前重点审计：2,095 条。
- 对比基线的增量记录：7 条；`RECLASSIFY` 0，`ADD` 6，`REMOVE` 1。
- 其中 5 个 `ADD` 是确证缺年原子；另 1 个 `ADD` 与 1 个 `REMOVE` 是 2008–2010 Scion xB 从 `Wagon` 纠正为 `Hatchback` 后的 ID 迁移，车形保持 `21`，并未新增平行车型。
- 新增车形按已核定同代轮廓复用：RDX/Explorer/HR-V 为 `41`，Crown Victoria 为 `32`，Thunderbird 为 `31`。
- 车形分布：0=239, 1=181, 10=20, 11=39, 20=350, 21=206, 25=63, 26=71, 30=765, 31=648, 32=913, 40=352, 41=436, 42=97, 50=62。
- 非独立代际的 3x 失败：0。
- 机器验收：PASS。

## 文件说明

- `correct.csv`：本批次完成时的全量 `DIMENSION-ID,车形` 快照。
- `changes.csv`：相对基线的实际新增、删除和改类。
- `all_dimension_audit.csv/json`：全 ID 逐条判定与摘要。
- `hatch_wagon_front_review.json`：`20/21` 前脸边界复核。
- `classic_shape_review.json`：历史车型轮廓复核。
- `generation_shape_review.json`：`30/31/32` 代际缓存和结构直映射清理审计。
- `validation.json`：本批次机器验收结果。

## 保留风险

- `ADD/REMOVE` 中包含上游年份合并、结构原子化和 `DIMENSION-ID` 重组，不应解读为单纯车形改类。
- 新证据如推翻已核代际，应追加新批次，不覆盖本快照。
