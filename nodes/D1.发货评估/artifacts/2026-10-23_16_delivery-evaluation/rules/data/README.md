# Agent 维护资料

存放 SKU 聚类、合并和人工例外规则。

`发货评估.json` 是当前正式发货评估口径。运行 `python code/build_delivery_evaluation.py`，从 A0 US 全量表覆盖全部车型，按 W 型车、皮卡、普通车分别做灰度聚合和市场潜力排序，并关联 B0 差评分析；不计算发货量。成功运行通过 RunBatch 更新稳定 `output/`。

正式业务输出以 SKU 为主键，一行对应一个 `MAKE + MODEL + 连续 YEAR 年份区间 + 供货尺码`；版本、结构、CAB、BED 只作汇总核对字段，不再拆分 SKU。业务输出不展示 `DIMENSION-ID`；差评模糊与推理依据合并到 `差评备注`。W 型车和普通车分类表不输出皮卡专用的 `CAB`、`BED`，混合明细中的非皮卡行将这两列留空。`发货评估身份映射.csv` 仅用于流水线身份追踪，将上游全部 `DIMENSION-ID` 映射到 SKU，不作为业务查看表。

业务表的 `差评备注` 使用短句：移除“车型已匹配全量表”和语义归并来源等清洗流水账，保留实际分析结论；模糊匹配原因压缩为 `匹配：缺年份/年份不符/缺尺码/尺码不符/结构不符/仅车型`，推理匹配仅保留同尺寸结论和来源 SKU。

`定制预定车型.csv` 是正式定制标记清单，内容参考仓库 `global/定制预定车型.csv` 维护；运行时只读取本节点 `data/` 副本。匹配以规范化后的 `MAKE + MODEL` 为准，并在当前车型中采用最长前缀匹配；清单尾部的 `2dr/4dr`、`C3-C8` 等视为车型细分说明，因此同一车型的对应 SKU 统一标记为定制，其他 MODEL（如 Bronco Sport、Range Rover）不会被更长车型名误标。

`非皮卡非W上架分析.json` 是 US 非皮卡、非 W 范围的研究方案：默认以2020–2025年度销量估值排序、2010–2025累计值参考，取24个精确车型/版本/结构/SHAPE/物理尺码簇，组合总配额800件。W范围、质量暂缓、结构分配提醒和组合规模均在此维护；800件为条件分配试算，不是订单预测。

在D1目录运行 `python src/mainstream_listing_analysis.py`（可选 `--budget 800`），测试为 `python -m pytest tests/test_mainstream_listing_analysis.py`。每次运行使用RunBatch，只生成不可变研究批次，不更新正式output、流水线状态或NAS；不属于pipeline正式run，不启用灰区升码。

`指定车型追加900.json` 在上述24簇基线上追加用户点名的21条车型需求，综合总配额900件。Bronco/Wrangler按门数、Corvette按代际分细分，每细分首轮选一个代表簇；Model Y/Model 3与原组合去重，Challenger/Model X为本轮范围例外。保底6件是可调试销假设，剩余按近期销量分配；Outback等原质量暂缓仍保留，旧款不代表新款覆盖。运行 `python src/expanded_listing_analysis.py`，仍只生成RunBatch研究批次。

`非皮卡非老车801上架分析.json` 是直接读取 A1 US 压缩尺码表的801件研究方案。非老车按2010年及以后建议适配且排除4*老车/W尺码系列定义，指定清单强制排除；同车型、版本、结构的连续年代若跨相邻尺码且整组长宽高跨度均不超过50mm，可在重新校验目标长度余量后统一到较大尺码。运行 `python src/nonpickup_modern_801_analysis.py`，生成新RunBatch研究批次，不更新正式output或NAS。

`普通车2000件150SKU灰度聚类.json` 用于普通车池的2000件、150 SKU研究：排除皮卡和W型车范围，启用上述灰度匹配，SKU按 `MAKE + MODEL + YEAR年份区间 + 供货尺码` 聚类，按销量权重分配件数；单SKU最多25件，封顶后的余量按未封顶SKU销量继续分配。运行 `python src/mainstream_2000_150_gray_analysis.py`，仅生成研究RunBatch，不更新稳定output或NAS。
