# COVER_SHAPE 规则与参考资料

`column_map.yaml` 为实际上游字段映射（英寸 × 25.4 → mm）。市场来自显式字段或明确配置的 DIMENSION-ID 后缀；缺失时不默认美国。原始字段原样保留。`pilot_cases.csv` 选择已有库的 8 个精确分支/年款，expected_candidate 仅为 STARTUP 测试假设，全部 PENDING，未参与分类。

`taxonomy_v1.yaml` 暂无人工确认原型；分类器因此保持 UNKNOWN。试验图像门禁/冲突容差尚未完成真实样本标定，不代表正确概率或已达上线标准。要加入原型须提供 id、label、reviewed=true、reviewer、reviewed_at_utc、calibration_evidence_ids、features、scales、max_distance；features 至少三项且含 roof_start_x / roof_end_x。不得添加车型名或 body_type 分类规则。

证据通过 `evidence.jsonl` 或 CLI `--evidence` 显式导入。必需字段见 `code/cover_shape/evidence.py`。variant_claim 包含 make/model/generation/body_type/trim；model_year_claim / market_claim 必须精确对应 variant_key。side_profile 的 data_payload 提供 quality（identity_confirmed/full_vehicle/unoccluded/low_perspective/stock_vehicle/real_image 全为布尔 true）、annotation、missing_intervals、independent_source_id。annotation 的 x 由车头向车尾递增、y 向下，包含 front_x/rear_x/ground_y、wheel_centers（两轮）、wheel_radii、top_points（有序上缘点）、hood_end_x/roof_start_x/roof_end_x/rear_deck_start_x。本地资料需 sha256。不能将合成测试几何作为真实车型证据。

64 点曲线以车长归一 x、地面至最高轮廓归一 y；不输出毫米轮廓。hood_ratio 为车头到机盖末端距离/车长；roof_start_x / roof_end_x 为车顶起止位置；roof_plateau_ratio 为两者差；rear_deck_ratio 为尾箱起点到车尾距离/车长；rear_slope_index 为车顶末端到尾箱起点的归一高度下降量/归一水平距离（无尾箱区间时为 null）；height_length_ratio / wb_length_ratio 为已知实际尺寸比。位置/长度比在 [0,1]，斜率是有限实数；缺失值为 null，轮廓缺失区间不得外推，不合格图不生成可信曲线。

独立核验要求两个合格侧面来源的域名、原始素材 ID 和内容 sha256 均不同。VERIFIED 还需精确身份、无重大矛盾、权威原厂/尺寸信息、已审原型、无多候选；任何状态 fit_tested=false / fit_status=NOT_TESTED。继承推断当前未启用，不输出未经证明的 INFERRED。

NHTSA CVS 参考：[官方 API 定义](https://vpic.nhtsa.dot.gov/api/Home/Index)。Metric 的 OL/OW/OH/WB/F/G 单位为 cm，MYR 是资料编制年末两位，B 随车身类型改变。响应实际为 Results[].Specs[].Name/Value。适配器保留原始值，不把加拿大资料默认为 US/EU/RU，也不猜测具体代际/版本。未核实的 API 响应仅作待审线索，不能使车型 VERIFIED。

规则变更需要同步测试，新运行通过 RunBatch 自动记录规则 sha256 + git commit，并快照未提交规则。研究模式不更新正式 output/manifest.json；需要正式接入时由 pipeline.json 维护节点增加契约，再走 publish_release。
