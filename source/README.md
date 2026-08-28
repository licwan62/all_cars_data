# source 数据真源

本目录是跨项目共享数据的唯一真源。文件只能由人手工维护或在审核项目候选后手工覆盖；研究脚本不得直接写入本目录。

`catalog.json` 记录每个正式数据集的格式、主键、生产项目和候选路径。执行以下命令可检查缺失文件、字段、空主键、重复主键和候选同步状态：

```powershell
python data_workflow.py check
```

发布前使用 `python data_workflow.py publish-plan <数据集名称>`。命令只校验并打印人工复制步骤，不会写入 `source`。

`尺码分析.csv` 是 pandas 尺码计算经人工审核后发布的统一接口，SKU、Trim 和尺码簇分析都默认读取它。`车型数据尺码.xlsx` 以及 `fx_size_match.pq`、`q_dim_sales.pq`、`q_全量.pq` 仅保留用于历史回归，不再是新项目的数据输入契约。`pk-cluster/` 是人工确认后发布的派生真源快照，因此仍由 `source` 统一对外提供。
