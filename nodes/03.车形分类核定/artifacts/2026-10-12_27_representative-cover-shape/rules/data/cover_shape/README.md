# COVER_SHAPE 规则与参考资料

2026-10-12 研究队列改为车型族：`research_queue.yaml`（v3）以 市场/品牌/车型/结构 为研究单元，每代际只抽少数年份；研究结论写入 `family_cache.csv`（车型族研究缓存，参照旧 `cache/model_shape_cache.csv`），按代际/年份/模式规则覆盖整族，EU/RU 可按年份重叠复用 US 结论。用 `code/shape_family_research.py` 领取与写入，详见节点 `COVER_SHAPE.md`。下文中「按代表分支」「不向其他分支广播」的描述为旧规则，已由车型族缓存取代。

研究推进规则在 `research_queue.yaml`，队列稳定接口为 `output/shape_research_queue.jsonl`。队列按代表分支覆盖，显式 online 批次保留失败、重试与进度，不把已有原型推断当成已研究。全量表只投影 SHAPE；本节点维护完整状态、代表年、方法、备选、来源和研究进度。合格的新几何证据进入本目录，保留源年款与事实限制，禁止把 target_scope 当作源身份已验证。

2026-10-12 自动化更新：`pipeline.yaml` 已启用 `automatic.yaml`，用户无需准备图片、关键点或人工原型。online 自动读取初始来源索引中的原厂/历史资料，提取明确的车顶、尾部、座舱几何描述，再动态调用 Wikimedia Commons 正式 API 搜索有许可的照片，运行本地 U2netp 背景分割、双轮与椭圆门禁、64 点轮廓和几何规则。索引仅记录来源与身份范围，不记录车型对应标签；BODY_TYPE 只参与身份消歧，候选规则仅读取几何观测及尺寸。新车型没有初始文本索引时也会动态搜索照片。

自动路径使用试验阈值，候选最高 INFERRED；冲突仍为 CONFLICT，资料不足仍为 UNKNOWN。原厂文本是定性证据，不能伪造 64 点轮廓；若使用本节点输入已声明的同一分支年份内资料，保留 source_model_year 与 inference_chain，注明改款几何未独立验证，不伪装为当前年款实测。源未知的代际/市场保留空值，variant_key 表示研究目标，不代表图片身份已经验证。

自动依赖用 `python -m pip install -e ".[automatic,dev]"` 安装。分割模型仅做背景分离，无车型标签分类；从固定 URL 自动下载并验证 SHA-256，记录权重哈希和 CPU 依赖版本。同域 HTTPS 正常重定向最多 3 次且逐次计入配额/日志，跨域重定向须配置明确来源；HTML 遵守 robots 与 Crawl-delay，正式 API 和 API 返回的有许可媒体不进行 HTML 爬取。未配置密钥也能运行当前自动路径。照片、模型和响应在后续批次引用已有相同哈希文件，避免重复归档。

下列人工原型/关键点说明保留为可选验证路径；不会阻塞自动取证与候选判断。

`column_map.yaml` 为实际上游字段映射（英寸 × 25.4 → mm）。市场来自显式字段或明确配置的 DIMENSION-ID 后缀；缺失时不默认美国。原始字段原样保留。`pilot_cases.csv` 选择已有库的 8 个精确分支/年款，expected_candidate 仅为 STARTUP 测试假设，全部 PENDING，未参与分类。

`taxonomy_v1.yaml` 暂无人工确认原型；分类器因此保持 UNKNOWN。试验图像门禁/冲突容差尚未完成真实样本标定，不代表正确概率或已达上线标准。要加入原型须提供 id、label、reviewed=true、reviewer、reviewed_at_utc、calibration_evidence_ids、features、scales、max_distance；features 至少三项且含 roof_start_x / roof_end_x。不得添加车型名或 body_type 分类规则。

证据通过 `evidence.jsonl` 或 CLI `--evidence` 显式导入。必需字段见 `code/cover_shape/evidence.py`。variant_claim 包含 make/model/generation/body_type/trim；model_year_claim / market_claim 必须精确对应 variant_key。side_profile 的 data_payload 提供 quality（identity_confirmed/full_vehicle/unoccluded/low_perspective/stock_vehicle/real_image 全为布尔 true）、annotation、missing_intervals、independent_source_id。annotation 的 x 由车头向车尾递增、y 向下，包含 front_x/rear_x/ground_y、wheel_centers（两轮）、wheel_radii、top_points（有序上缘点）、hood_end_x/roof_start_x/roof_end_x/rear_deck_start_x。本地资料需 sha256。不能将合成测试几何作为真实车型证据。

64 点曲线以车长归一 x、地面至最高轮廓归一 y；不输出毫米轮廓。hood_ratio 为车头到机盖末端距离/车长；roof_start_x / roof_end_x 为车顶起止位置；roof_plateau_ratio 为两者差；rear_deck_ratio 为尾箱起点到车尾距离/车长；rear_slope_index 为车顶末端到尾箱起点的归一高度下降量/归一水平距离（无尾箱区间时为 null）；height_length_ratio / wb_length_ratio 为已知实际尺寸比。位置/长度比在 [0,1]，斜率是有限实数；缺失值为 null，轮廓缺失区间不得外推，不合格图不生成可信曲线。

独立核验要求两个合格侧面来源的域名、原始素材 ID 和内容 sha256 均不同。VERIFIED 还需精确身份、无重大矛盾、权威原厂/尺寸信息、已审原型、无多候选；任何状态 fit_tested=false / fit_status=NOT_TESTED。继承推断当前未启用，不输出未经证明的 INFERRED。

NHTSA CVS 参考：[官方 API 定义](https://vpic.nhtsa.dot.gov/api/Home/Index)。Metric 的 OL/OW/OH/WB/F/G 单位为 cm，MYR 是资料编制年末两位，B 随车身类型改变。响应实际为 Results[].Specs[].Name/Value。适配器保留原始值，不把加拿大资料默认为 US/EU/RU，也不猜测具体代际/版本。未核实的 API 响应仅作待审线索，不能使车型 VERIFIED。

规则变更需要同步测试，新运行通过 RunBatch 自动记录规则 sha256 + git commit，并快照未提交规则。研究模式不更新正式 output/manifest.json；需要正式接入时由 pipeline.json 维护节点增加契约，再走 publish_release。
