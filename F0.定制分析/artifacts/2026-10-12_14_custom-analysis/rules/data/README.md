# 定制分析配置

每个 *_custom_analysis.json 定义车型（`model` 或 `models`）、区域、结构（`structure` 或 `structures`）筛选、L/W/H 最大跨度和 Sketchfab 参考链接。跨子车系聚簇时必须设置 `sku_family_code`；候选 SKU 只含一个车系时仍使用数字尺寸编码（4 位车型码 + 起止年 YY，如 01036973），家族代号只用于真正跨车系的候选。

`sketchfab_sku_searches` 的每个模型用 `dimension_id` 登记对应的全量表车型，报告据此写出车长及与 SKU 车长上限的差。`representative_url`（首选）对应车型的车长不得比 SKU 上限短超过 `reference_length_tolerance_mm`（默认 50 mm），否则运行失败；找不到接近上限的模型时留空首选，模型只作轮廓对照，状态为“待补上限参考模型”。
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
Sketchfab 参考优先选择页面明确提供下载的模型，便于后续量测和打样；不可下载模型降低优先级，仅在缺少同代可下载替代时保留。SQUIR3D 的模型通常不可下载，不作为首选；若必须引用，需在备注中说明不可下载及用途限制。

2026-10-10：交付改为每车型单份完整 Markdown，成员和任务表嵌入文档；取消 CSV 生成和稳定交付。新增 Prius，两厢范围精确筛选；差评读取 B0 output，本节点仍归属独立 F 产线。sampling_groups 为人工打样方案，独立于尺寸算法候选结果。
