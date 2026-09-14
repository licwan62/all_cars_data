# 待终核短缺口推进

输入为 `../2026-08-25_04_generation-conflicts/correct.csv`。本轮采用“宽松但不盲补”的终核口径：

- 同代、同版本/CAB/BED/结构且分类一致；
- 单年缺口：两侧长宽高各自差值不超过 `1.0 in`；
- 两年缺口：两侧长宽高各自差值不超过 `0.3 in`；
- 三年以上缺口、换代边界、分类变化与明显尺寸变化继续保留；
- Dodge Viper 2007、Porsche 911 GT3 RS 2017-2018 作为已知衍生线空档明确保留。

结果：35 个短缺口并入 31 个合并组，记录数由 4,389 降至 4,354。复核后仍有 51 个分支缺口、14 个整车型年份缺口等待证据或人工判断；没有未解决代际冲突、区间冲突、重复 `DIMENSION-ID` 或 ID 计算错误。

文件说明：

- `correct.csv`：本轮规范快照；
- `applied_gap_repairs.csv`：已补齐并合并的缺口；
- `retained_gap_reviews.csv`：未自动处理的上一轮记录及保留原因；
- `gap_candidates.csv`：基于新快照重算的全部年份缺口；
- `changes.csv`：31 个实际合并组；
- `validation.json`：机器验收结果。

本轮未写入 `source` 目录。
