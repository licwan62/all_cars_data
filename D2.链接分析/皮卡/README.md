# 皮卡链接分析

本项目审核 `D2.链接分析/data/发货单明细.xlsx` 中的既成皮卡发货事实，与 W 型车项目的规则、批次和输出目录完全分开。

```powershell
python run.py --publish-public
```

运行批次写入 `皮卡/artifacts/`，通过校验的稳定结果写入 `皮卡/output/`。`SKU发货数量.csv` 以 `data/发货事实.csv` 的 `SKU_NAME` 为唯一键，发货数量与 `CLUSTER_ID` 无关；只输出 SKU、当前尺码、带 CAB/BED 的适配车型、适配年份和发货数量。指定 `--publish-public` 后，四张 CSV 原子发布到 `pub_all_cars_data/sku_cluster/皮卡`；Markdown 报告只保留在仓库内。
