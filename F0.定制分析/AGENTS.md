# 定制分析 Agent

负责按车型生成定制 SKU 包络、成员明细、Sketchfab 外形参考任务和分析报告。
遵守根目录 AGENTS.md；配置和人工核验的参考链接维护在 data/。

正式上游：A0.尺码计算/output/US/全量/全量表.csv、02.代码映射/output/尺寸编码映射.csv、B0.差评分析/output/差评分析表.csv。
按需运行 `python src/run.py`，再从仓库根目录执行
`python scripts/publish_release.py --nodes custom-analysis`。
各配置独立输出到 output/<配置名>/；历史 C1 批次保留原位，不能作为默认输入。

每个车型仅交付完整的 定制SKU聚簇报告.md，包含结论、差评依据、SKU 包络、完整成员、打样建议、Sketchfab 检索和参考任务及输入追踪。
新运行批次只生成 Markdown 数据交付物（保留约定的 run.json/manifest.json 与规则快照）；不生成 CSV。历史 CSV 不回写或删除，撤下的 output CSV 可从历史 artifact 恢复。
