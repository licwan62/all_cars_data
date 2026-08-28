# TrimList 与自动尺码关联分析

## 结论

- Trim 映射行：23,382
- 关联成功行：23,382
- 唯一 `Year + Make + Model`：12,659
- 单 Size 键：8,485
- 多 Size 正常展开键：3,855
- 其中多结构展开键：2,570
- 无可发布 Size 键：319

多 Size 占有效尺码车型键的 **31.24%**；
多 Size 本身不是冲突，全部按 `DIMENSION-ID + Size` 保留。

## 唯一性与展开

| 指标 | 数量 |
|---|---:|
| 过滤状态值后可发布行 | 22,568 |
| 唯一 DIMENSION-ID + Size | 4,099 |
| 完整适配原子行 | 22,568 |
| 可删除完整重复行 | 0 |
| 多 Size 正常展开 | 3,855 |

## 非尺码状态

| 状态 | 映射行 |
|---|---:|
| 无可用尺码 | 814 |
| 数据不全 | 0 |

这些状态不应作为正式 `Size` 发布。

## 发布规则

1. 排除 `无可用尺码` 和 `数据不全`。
2. `DimensionSizeMap.csv` 以 `DIMENSION-ID + Size` 为唯一键。
3. 多结构或多版本导致多个 Size 时，保留并展开全部已核实分支。
4. 完整发布原子键为 `DIMENSION-ID + Size + Year + Make + Model`。
5. 无有效 Size 进入 `NoPublishableSizeReport.csv`。
