# 定制分析配置

2026-10-19：新增 F-150 SuperCrew 2008–2026、F-350 Crew 1999–2026、F-250 Crew 2001–2026、Ram 1500 Crew 2009–2026、Silverado 2500 Crew 2020–2026 五份短斗分析。配置用 `cabs`、`beds` 精确匹配 A0 字段，`year_range` 取年款交集并保留 `SOURCE_YEAR` 和原 DIMENSION-ID；`excluded_versions` 排除 Lightning。F-150 短斗 5.5 ft、Super Duty 6.8 ft、Ram 5.6 ft、Silverado HD 6.8 ft。保留特殊性能版供独立核验，Ram 含独立 Classic；合并车型尺寸不能冒充各子车型独立测量，年款缺口不补造。五份新报告仅登记内部交付，不新增公开发布。Sketchfab 仅登记候选线索，尚无核验过的首选模型。

每个 *_custom_analysis.json 定义车型（`model` 或 `models`）、区域、结构（`structure` 或 `structures`）筛选、L/W/H 最大跨度和 Sketchfab 参考链接。跨子车系聚簇时必须设置 `sku_family_code`；候选 SKU 只含一个车系时仍使用数字尺寸编码（4 位车型码 + 起止年 YY，如 01036973），家族代号只用于真正跨车系的候选。

`sketchfab_sku_searches` 的每个模型用 `dimension_id` 登记对应的全量表车型，报告据此写出车长及与 SKU 车长上限的差。`representative_url`（首选）对应车型的车长不得比 SKU 上限短超过 `reference_length_tolerance_mm`（默认 50 mm），否则运行失败；找不到接近上限的模型时留空首选，模型只作轮廓对照，状态为“待补上限参考模型”。
`universal_size_risk_by_sku: true` 时，通用尺码适配风险按候选 SKU 对照成员的 A0 自动尺码，自动写出尺码分布、与其他候选共用的尺码、长度余量松紧差（超过 `risk_margin_span_mm`，默认 100）和偏紧车型（余量低于 `risk_tight_margin_mm`，默认 50）；`universal_size_risk_notes` 只补数据推不出的人工结论。未开启时仍按自动尺码分组。
使用 `sketchfab_sku_searches` 时，“Sketchfab 参考”先给总览表（代表车型及车长上限、首选模型与上限差、状态），再按 SKU 列“覆盖车型”（年份、版本、结构、车长；SKU 内混合车系时加车系列）和“参考模型”（角色、链接、对应年份、版本、结构、车长、与上限差、说明）。模型标题中“｜”前的角色前缀和“（…）”说明由脚本拆分。
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

2026-10-16：新增 MINI Cooper Hatchback（2002–2026）分析；仅选 MODEL=Cooper，避免与独立 MODEL=Cooper SE 记录重复。差评品牌匹配改为不区分大小写，以兼容 A0 的 MINI 与 B0 的 Mini。
