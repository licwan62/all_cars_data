# 全量表宽高统计

读取 `A0.尺码计算/output/<国别>/全量/全量表.csv`（US、EU、RU），按 区域 + 自动尺码 生成：

- `output/尺码宽高统计.csv`
- `output/尺码宽高极值车型.csv`
- `output/尺码尺寸异常.csv`

```powershell
python src/build_dimension_statistics.py
```

口径与阈值见 `data/dimension_stats_config.json`，节点职责见 [AGENTS.md](AGENTS.md)。TRIM 匹配与 TRIM适配器 已迁至 `A0.尺码计算`。
