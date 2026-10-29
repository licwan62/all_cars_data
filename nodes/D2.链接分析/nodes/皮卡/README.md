# 皮卡链接分析

本项目审核 `data/发货单明细.xlsx` 中的既成皮卡发货事实，与 W 型车项目的规则、批次和输出目录完全分开。
在 `pipeline.json` 登记为节点 `link-analysis-pickup`。

```powershell
python scripts/run.py                                                   # 在本目录执行
python scripts/publish_release.py --nodes link-analysis-pickup          # 在仓库根执行
python scripts/publish_public.py                                        # 在仓库根执行，对外发布
```

运行批次写入 `皮卡/artifacts/`，通过校验的稳定结果写入 `皮卡/output/`，`output/manifest.json` 由发布脚本生成。`SKU发货数量.csv` 以 `review/发货事实.csv` 的 `SKU_NAME` + `发货日期` 为唯一键，发货数量与 `CLUSTER_ID` 无关；只输出 `SKU_NAME`、`发货数量`、`发货日期`；上架明细标题字段使用 `TITLE_NAME`，标题年份单列为 `TITLE_YEAR`。四张 CSV 按 `public_outputs` 发布到 `pub_all_cars_data/sku_cluster/皮卡`；Markdown 报告只保留在仓库内。
