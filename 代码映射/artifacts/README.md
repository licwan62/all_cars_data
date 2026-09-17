# 代码映射迭代留痕

本目录保存不可覆盖的代码映射运行批次，所有内容均应纳入 Git。

- 批次目录命名为 `YYYY-MM-DD_NN_code-mapping-publish`。
- `output/vehicle_mapping.csv` 是该批次的最终有效映射。
- `mapping/` 保存该批次使用的完整持久映射快照，包括历史停用项。
- `run_report.json` 记录源文件路径、SHA-256、数量和新增统计。
- `validation.json` 保存不可变性、容量与数量校验结果。
- 新运行必须创建新顺序号，不得覆盖或删除已归档批次。
- 下游项目只读取 `../../public/code/_mapping/vehicle_mapping.csv`，不直接依赖历史批次。

