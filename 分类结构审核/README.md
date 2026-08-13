# 分类结构审核

本项目审核 `../source/车型尺寸库.csv` 的结构与五类车衣分类，并通过 `DIMENSION-ID` 回查源表身份字段。

## 产物

- `artifacts/corrected.csv`：与源表结构一致的最终修正版。
- `artifacts/audit_table*.csv`：仅包含 `DIMENSION-ID` 与对应审核结论/证据的过程表。
- `artifacts/audit_full_inventory.csv`：每个尺寸组一行的全库审核结论。
- `artifacts/validation_report.json`：机器验收结果。
- `research_queue/queue.csv`：审核研究状态源。

## 标准重建

在工作区根目录运行：

```powershell
python 分类结构审核/code/research_queue.py init
python 分类结构审核/code/regenerate_artifacts.py
python 分类结构审核/code/generate_report.py
python 分类结构审核/code/validate_project.py
```

`corrected.csv` 保留源表的 4,801 行；过程表按 `DIMENSION-ID` 聚合，因此当前为 4,796 个尺寸组。
