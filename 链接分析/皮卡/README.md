# 皮卡链接分析

本项目只处理 `聚类SKU/changes/皮卡`，与 W 型车项目的输入、聚类规则和输出目录完全分开。

```powershell
python run.py
```

流程使用 `public/全量数据.csv` 和 `销量评估/artifacts/atom_sales.csv` 重建皮卡聚类候选，再生成本项目独立的 `output/`。W 型车专用的年份/尺码合并脚本不会在本项目运行。
