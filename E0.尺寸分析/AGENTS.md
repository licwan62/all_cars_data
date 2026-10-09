# 尺寸分析 Agent（E 线：全量表尺寸分析，按需运行）

`id: size-analysis`（原 `full-generation`）。2026-10-09 起由 `A1.全量生成` 移出 A 线，改为 `E0.尺寸分析`，按需运行：A 线发布不会自动刷新本节点。2026-09-27 起只做全量表分析：读取 `A0.尺码计算` 发布的 US/EU/RU 全量表，按区域 + 自动尺码生成宽高统计。全量表本身、TRIM 匹配与 TRIM适配器 均由 A0 产出，本节点不再输出全量表（`全量表_汇总.csv`、`全量生成_<产线>.csv`、`尺寸TRIM映射.csv`、`TRIM适配器.csv` 已取消）；原 TRIM 代码与 `data/` 资料已迁至 `A0.尺码计算/src/trim/` 与 `A0.尺码计算/data/US/TRIM/`。

历史批次保存在 `artifacts/`；合并前的 `legacy-adapter-trim/`、`legacy-full-table-summary/` 与较旧批次已于 2026-10-09 原样归档到 NAS `\\NAS8824B4\Public\PQData\bak\all_cars_data\artifacts\E0.尺寸分析\`（索引见仓库根目录 `artifacts_archive.json`）。

上游：`A0.尺码计算/output/<国别>/全量/全量表.csv`（US、EU、RU；只有 US 带 TRIM）。

## 数据与输出

- `data/dimension_stats_config.json`：排除的尺码状态、IQR 倍数、z 分数阈值、方差口径（总体方差）。
- `output/尺码宽高统计.csv`：区域 × 自动尺码的车型数与宽、高的最小/最大/平均/中位数/方差。
- `output/尺码宽高极值车型.csv`：每组最宽、最高车型（并列全列）。
- `output/尺码尺寸异常.csv`：超出 IQR 或 |z| 阈值的车型及原因。
- `output/manifest.json`：`scripts/publish_release.py` 生成。

## 运行

```powershell
python src/build_dimension_statistics.py
```

校验通过后写入新的 `artifacts/<日期>_<序号>_dimension-statistics/`（`lib/artifact_batch.py`：`run.json` 引用三张已发布的 A0 区域全量表、记录 `data/` 规则 sha256 + git commit，不复制；`output/` 保存带版本后缀的交付物），再原子更新 `output/`。任一区域缺失或有效尺码行宽高非正时失败，不改变 `output/`。

遵守仓库根目录 `AGENTS.md`。
