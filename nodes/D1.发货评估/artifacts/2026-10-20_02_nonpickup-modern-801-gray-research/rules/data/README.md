# Agent 维护资料

存放 SKU 聚类、合并和人工例外规则。

`非皮卡非W上架分析.json` 是 US 非皮卡、非 W 范围的研究方案：默认以2020–2025年度销量估值排序、2010–2025累计值参考，取24个精确车型/版本/结构/SHAPE/物理尺码簇，组合总配额800件。W范围、质量暂缓、结构分配提醒和组合规模均在此维护；800件为条件分配试算，不是订单预测。

在D1目录运行 `python src/mainstream_listing_analysis.py`（可选 `--budget 800`），测试为 `python -m pytest tests/test_mainstream_listing_analysis.py`。每次运行使用RunBatch，只生成不可变研究批次，不更新正式output、流水线状态或NAS；不属于pipeline正式run，不启用灰区升码。

`指定车型追加900.json` 在上述24簇基线上追加用户点名的21条车型需求，综合总配额900件。Bronco/Wrangler按门数、Corvette按代际分细分，每细分首轮选一个代表簇；Model Y/Model 3与原组合去重，Challenger/Model X为本轮范围例外。保底6件是可调试销假设，剩余按近期销量分配；Outback等原质量暂缓仍保留，旧款不代表新款覆盖。运行 `python src/expanded_listing_analysis.py`，仍只生成RunBatch研究批次。

`非皮卡非老车801上架分析.json` 是直接读取 A1 US 压缩尺码表的801件研究方案。非老车按2010年及以后建议适配定义，指定清单强制排除；同车型、版本、结构的连续年代若跨相邻尺码且整组长宽高跨度均不超过50mm，可在重新校验目标长度余量后统一到较大尺码。运行 `python src/nonpickup_modern_801_analysis.py`，生成新RunBatch研究批次，不更新正式output或NAS。
