# TrimList 与自动尺码关联分析

## 结论

- Trim 映射行：23,209
- 关联成功行：23,209
- 唯一 `Year + Make + Model`：12,580
- 单 Size 键：9,022
- 多 Size 正常展开键：3,503
- 其中多结构展开键：2,214
- 无可发布 Size 键：55

多 Size 占有效尺码车型键的 **27.97%**；
多 Size 本身不是冲突，全部按 `DIMENSION-ID + Size` 保留。

## 唯一性与展开

| 指标 | 数量 |
|---|---:|
| 过滤状态值后可发布行 | 22,875 |
| 最终TRIM适配器回填行 | 23,209 |
| 最终TRIM适配器保留状态行 | 334 |
| 唯一 DIMENSION-ID + Size | 4,232 |
| DIMENSION-ID + Trims 映射 | 4,371 |
| Trims 为空 | 4,371 |
| 完整适配原子行 | 22,875 |
| 可删除完整重复行 | 0 |
| 多 Size 正常展开 | 3,503 |

## 非尺码状态

| 状态 | 映射行 |
|---|---:|
| 无可用尺码 | 334 |
| 数据不全 | 0 |

这些状态不应作为正式 `Size` 发布。

## 发布规则

1. `TRIM适配器.csv` 对 `TrimList.csv` 全量回填，不丢弃 `无可用尺码` 和 `数据不全` 状态行。
2. 可发布尺码分析继续排除 `无可用尺码` 和 `数据不全`。
3. `DimensionSizeMap.csv` 以 `DIMENSION-ID + Size` 为唯一键。
4. `尺寸TRIM映射.csv` 每个 `DIMENSION-ID` 一行，`Trims` 仅来自尺码分析的 `TRIM` 列。
5. 多结构或多版本导致多个 Size 时，保留并展开全部已核实分支。
6. 完整发布原子键为 `DIMENSION-ID + Size + Year + Make + Model`。
7. 无有效 Size 进入 `NoPublishableSizeReport.csv`。
