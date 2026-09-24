# 尺码计算 Agent

负责把尺寸库、车形和销量合成为全量尺码结果。尺码规则、参数、参考尺寸和店铺货架配置由本 agent 在 `data/` 维护；当前正式结果写入 `output/`，每次计算完整快照写入 `artifacts/`。

上游：`01.整理尺寸库`、`03.车形分类核定`、`02.销量评估`。规则变更必须新增测试和 artifact，不得改写历史批次。

## 上游与交付物（第 4 层）

上游 `output/`：`01.整理尺寸库/尺寸库.csv`、`03.车形分类核定/车形分类.csv`、`03.车形分类核定/参考尺寸计算.csv`（车身号→系数）、`02.销量评估/原子销量.csv`、`02.代码映射/尺寸编码映射.csv`。

全量表带 `DIMENSION-CODE` 列（在 `DIMENSION-ID` 之前），由 `full_table_schema.attach_dimension_code` 按 `DIMENSION-ID` 关联；任何 ID 缺少编码都会报错，不写空值。

稳定交付物：`全量表_US.csv`、`全量表_EU.csv`、`全量表_RU.csv`、`全量表_汇总.csv`（`build_consolidated_full_table.py` 合并三国，缺任一区域或缺 `DIMENSION-CODE` 时失败）、`尺寸分析表_US.csv`、`店铺全量_<店铺>.csv`、`尺码匹配报告*.json`、`尺码匹配规则.csv`。

EU 全量表由 `publish_eu_current_research.py` 发布当前已审核研究覆盖；报告必须明确覆盖行数、当前 EU 尺寸库行数和被排除的过时 ID，不得把部分研究覆盖表述为全库完成。

