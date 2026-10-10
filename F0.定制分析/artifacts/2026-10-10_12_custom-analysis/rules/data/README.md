# 定制分析配置

每个 *_custom_analysis.json 定义车型（`model` 或 `models`）、区域、结构（`structure` 或 `structures`）筛选、L/W/H 最大跨度和 Sketchfab 参考链接。跨子车系聚簇时必须设置 `sku_family_code`，不得把单一 MODEL 的映射代号误标为家族 SKU。
当前仅支持 US；长度使用 A0 的 L-MM 代理，包络不是成品裁剪尺寸。
保留原配置的 250/150/100 mm 阈值和聚簇顺序，自动尺码不参与聚簇。
算法是确定性的贪心分配，不保证所有输入上的全局最少 SKU。

迁移来源：C1.车型代表分析/src/analyze_mercedes_e_class_custom.py 与其两套车型配置。
参考批次：C1.车型代表分析/artifacts/2026-10-09_16_mini-countryman-custom-analysis。
历史 artifact 保持原位。search_date 是人工参考链接的检索日期；重跑不会把旧链接标为当天已核验。

运行全部配置：`python src/run.py`。运行单一配置：
`python src/run.py --case mini_countryman`。
新增车型配置时同时登记 pipeline.json 的交付物，并补充自动测试。
Sketchfab 外形核验与实际尺寸测量在打样阶段完成，脚本只生成参考任务，不自动宣称模型已验证。

2026-10-10：交付改为每车型单份完整 Markdown，成员和任务表嵌入文档；取消 CSV 生成和稳定交付。新增 Prius，两厢范围精确筛选；差评读取 B0 output，本节点仍归属独立 F 产线。sampling_groups 为人工打样方案，独立于尺寸算法候选结果。
