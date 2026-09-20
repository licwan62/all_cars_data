# 皮卡链接分析

本项目只处理 `D1.聚类SKU/artifacts/皮卡`，与 W 型车项目的输入、聚类规则和输出目录完全分开。

```powershell
python run.py
```

流程使用 `A0.尺码计算/output/全量表_US.csv` 和 `02.销量评估/output/原子销量.csv` 重建皮卡聚类候选，再生成本项目独立的版本化 artifact；通过校验的当前结果写入本 agent 的 `output/`。
