# 圆角经典车俯视收缩速度复核

本批次以 `D:\Licheng\Workflow\all_cars_data\车形分类核定\changes\2026-08-25_02_classic-boxy-generation-repair\correct.csv` 为变更对比基线，以分类结构审核最新规范快照为输入，将车形规则落实到全部 `4,354` 个 `DIMENSION-ID`。本轮未写入 `source` 目录。

## 核定规则

- `STRUCTURE` 只用于定位分支，不直接映射 `30/31/32`。
- 方形宽车头是 `32` 最高优先级特征；确认后不再与 `31` 比较。
- `31` 仅在排除方形宽车头后，按低矮、下宽上窄的实际比例核定。
- `20/21` 按车头收窄和前角轮廓逐代复核。
- 2000 年以前历史车型逐条审计，仅复用已独立核定的同代轮廓结论。

## 结果统计

- 全量结果：4,354 条，唯一 ID 4,354 个。
- 2000 年以前重点审计：2,042 条。
- 对比基线的增量记录：70 条；`RECLASSIFY` 70，`ADD` 0，`REMOVE` 0。
- 共重核 29 个“多代 32 后圆角化”的连续代际：`30→32` 55 条，`31→32` 15 条。
- Cadillac DeVille `gen6` 1994–1999 与 `gen7` 2000–2005 的 3 条记录均已归 `32`；DeVille 现有 `gen0–gen7` 全系 68 条均为 `32`。
- 同类复核覆盖 LeSabre、Park Avenue、Regal、Riviera、Roadmaster、Eldorado、Seville、Impala、Crown Victoria、Continental、Town Car、Grand Marquis、Oldsmobile 88 和 Bonneville。
- 方正/宽肩历史代际注册总数现为 131，覆盖验收失败数为 0。
- 车形分布：0=230, 1=176, 10=20, 11=39, 20=342, 21=199, 25=63, 26=69, 30=759, 31=636, 32=886, 40=347, 41=431, 42=96, 50=61。
- 非独立代际的 3x 失败：0。
- 机器验收：PASS。

## 文件说明

- `correct.csv`：本批次完成时的全量 `DIMENSION-ID,车形` 快照。
- `changes.csv`：相对基线的实际新增、删除和改类。
- `all_dimension_audit.csv/json`：全 ID 逐条判定与摘要。
- `hatch_wagon_front_review.json`：`20/21` 前脸边界复核。
- `classic_shape_review.json`：历史车型轮廓复核。
- `generation_shape_review.json`：`30/31/32` 代际缓存和结构直映射清理审计。
- `classic_boxy_regression_audit.json`：旧 32 回归审计；216 条历史降级候选均有明确去向。
- `validation.json`：本批次机器验收结果。

## 保留风险

- 本轮只修改车形结论，没有 ID 新增、删除或上游年份重组。
- 俯视边界不清时向 `32` 倾斜仅适用于有连续方正血统，且肩部、机盖前缘和前轮至保险杠的横向收缩仍然缓慢的代际；不对一般现代轿车扩张使用。
- 新证据如推翻已核代际，应追加新批次，不覆盖本快照。
