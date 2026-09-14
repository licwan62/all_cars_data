# 单次修改包

本目录按修改批次保存可独立交付和回溯的快照。每个批次必须至少包含 `correct.csv`、`changes.csv` 和 `report.md`。

## 当前批次

- `2026-08-24_01_version-normalization`：SUV 门数 VERSION 规范化及同外廓冗余版本合并。
- `2026-08-24_02_year-reference-us-market`：补归档原 year_reference 与美国市场尺寸修复；该阶段快照为 4,791 行。
- `2026-08-24_03_sedan-coupe`：补归档原 Sedan/Coupe 分类与尺寸修复；该阶段快照为 4,788 行。
- `2026-08-25_01_atomic-structures`：删除 21 条旧复合结构压缩行；原子化快照为 4,765 行。
- `2026-08-25_02_year-generation-audit`：修正明确代际错标并合并连续同外廓记录；规范快照为 4,400 行。
- `2026-08-25_03_identity-gap-distinction`：区分门数/轴距/Sportback，清理聚合残留并细分缺年候选；规范快照为 4,390 行。
- `2026-08-25_04_generation-conflicts`：归一组合代际标签，修复明确错代并登记合法并行；规范快照为 4,389 行。
- `2026-08-25_05_final-review-progression`：按宽松终核规则补齐同代同分支短缺口；35 个缺口并入 31 组，规范快照为 4,354 行。
- `2026-08-25_06_confirmed-branch-gaps`：推进已确认的同代、整车型及跨代分支缺口；新建 83 条独立记录，其中包含 1975 Chevrolet Nova Coupe，规范快照为 4,437 行。
- `2026-08-25_07_verified-atomic-gaps`：仅补建已确认存在的 5 个原子记录，纠正 1 条结构别名，并将 15 个停产/跳年候选登记为禁止补建；规范快照为 4,442 行。

`02`、`03` 是补建修改包的目录序号；实际数据处理顺序为 year/美规 → Sedan/Coupe → VERSION 规范化。

## 约定

- 目录名：`YYYY-MM-DD_NN_short-description`。
- `correct.csv` 是该批次完成时的全量结果，不是增量补丁。
- `changes.csv` 只记录该批次实际执行的修改。
- `candidates.csv` 记录未自动应用、仍需审核的候选。
- `report.md` 说明规则、统计、例外和风险。
- `validation.json` 保存该批次机器验收结果。
- 已交付批次不得被下一次修改覆盖；下一次使用新的顺序号和目录。
