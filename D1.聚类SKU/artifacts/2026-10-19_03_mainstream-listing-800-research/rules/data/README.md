# Agent 维护资料

存放 SKU 聚类、合并和人工例外规则。

`非皮卡非W上架分析.json` 是 US 非皮卡、非 W 范围的研究方案：默认以2020–2025年度销量估值排序、2010–2025累计值参考，取24个精确车型/版本/结构/SHAPE/物理尺码簇，组合总配额800件。W范围、质量暂缓、结构分配提醒和组合规模均在此维护；800件为条件分配试算，不是订单预测。

在D1目录运行 `python src/mainstream_listing_analysis.py`（可选 `--budget 800`），测试为 `python -m pytest tests/test_mainstream_listing_analysis.py`。每次运行使用RunBatch，只生成不可变研究批次，不更新正式output、流水线状态或NAS；不属于pipeline正式run，不启用灰区升码。
