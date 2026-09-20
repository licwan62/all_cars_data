# 已确认分支缺口推进

输入为 `分类结构审核\changes\2026-08-25_05_final-review-progression\correct.csv`。本轮不跨代合并记录；对已确认存在的缺失分支新建独立 `DIMENSION-ID`，对停产年和证据不足项继续保留。

## 结果

- 输入 4,354 条，输出 4,437 条，新建 83 条已确认分支。
- 新建类型：同代分支连续缺口 49 条；整车型缺失 6 条；跨代但已确认的分支 28 条。
- 1975 Chevrolet Nova Coupe 已按原厂目录新建为 `gen4 / Coupe / 1975`，不与 Hatchback 合并。
- 已确认停产空档继续保留；证据不足的跨代候选不自动补齐。
- 剩余缺口候选 273 条；本轮已应用缺口的未解决数为 0。
- 机器验收：PASS。

## 文件

- `correct.csv`：本轮全量快照。
- `changes.csv`：新建的已确认分支。
- `branch_gap_decisions.csv`：上一轮全部缺口的推进/保留决定。
- `gap_candidates.csv`：按新快照重算的剩余缺口。
- `generation_findings.csv`、`interval_conflicts.csv`：代际和年份区间验收。
- `validation.json`：机器验收结果。

本轮未写入 `source` 目录。
