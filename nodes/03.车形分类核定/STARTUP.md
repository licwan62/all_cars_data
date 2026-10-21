# Vehicle COVER_SHAPE Research — Codex Startup

版本：1.0 ｜ 日期：2026-10-12 ｜ 项目性质：现有车型库的只读增强与可审计几何分类

## 0. 项目使命与不可妥协原则

输入已有车型数据库，在**不改写原始数据**的前提下，使用可合法访问的网络来源、官方参数和真实正侧面几何证据，为每条车型记录生成可追溯的 `COVER_SHAPE` 候选分类，并导出审查报告。**BODY_TYPE 不可被直接映射为 COVER_SHAPE；COVER_SHAPE 不可直接映射为 COVER_FIT/SKU。**

项目第一阶段不做车罩 SKU 分配、不训练黑箱分类模型、不尝试为证据不足的车型强行填值。允许 `UNKNOWN`、`CONFLICT`、`REVIEW_REQUIRED`。`VERIFIED` 仅指车型几何分类证据通过规则验证，不代表实际车罩打样通过。

## 1. 给 Codex 的首轮执行指令（复制到 Codex）

> 你是本仓库的高级数据工程师、汽车几何研究员和测试工程师。先阅读 `STARTUP.md`、`AGENTS.md`，以及现有数据库说明。先执行**只读盘点**，输出数据库字段、车系/年份覆盖、现有重复记录和可能的结构映射风险。不要修改现有数据库、不要重构现有项目、不要假设现有列名、不要在没有证据时生成可信标签。请按 `STARTUP.md` 的阶段 0→1→2 执行，先建立可运行的最小闭环：从 8 个已知测试车型载入→检索/导入证据→输出候选分类与来源→运行验证测试。任何外部 API 若无凭证应实现适配器和可复现的离线 fixture 测试，不要假装已经联网成功。只在工作目录创建新文件，阶段完成后给出变更清单、运行命令、测试结果、阻塞项和下一阶段计划。

## 2. 范围定义

### 本期必做（MVP）
1. 读取 CSV/XLSX/Parquet 中的一种或多种，自动发现列名并生成显式映射配置；支持主键或稳定合成 ID。
2. 车型标准化：品牌、车系、年款、代际、车身版本（如 Coupe/Hatchback）、市场、长宽高和单位；保留原始字段。
3. 来源采集：制造商原厂规格/宣传册、政府车辆尺寸数据、可信汽车媒体实拍的可信侧面照；可选 NHTSA CVS API。
4. 证据归档：记录 URL、来源站点、访问时间、车型匹配键、原始尺寸/图片标识、许可证/使用限制、哈希、字段级来源。
5. 几何特征：尺寸比、前后悬/轴距比（有数据时）；可信侧面图合格后估计轮廓采样及车顶相关特征。
6. 规则明确、可配置的 `COVER_SHAPE` 分类器；输出多候选和原因而不是只输出标签。
7. 证据质量门禁与人工复核；结果导出、单元测试、端到端 fixture 测试。

### 非目标（本期禁止自动承诺）
- 直接推导真实 3D 曲面/精确裁片尺寸；从单张侧视图不能确定车身横截面。
- 根据车身结构直接分配 SKU；自动改写用户已有车罩匹配、尺寸表或产品数据。
- 无授权批量抓取/再分发受版权保护图片，绕过网站访问控制。
- 使用视觉模型生成的自信分数冒充客观的正确概率。

## 3. 关键输入和模式

配置 `config/column_map.yaml` 负责将用户库的实际列名映射到：

| 逻辑字段 | 必需 | 规则 |
|---|---|---|
| `source_row_id` | 是 | 保留原始主键；缺失时基于文件标识+原始行号生成稳定 ID |
| `make`, `model` | 是 | 不得覆盖原值；另存标准化值 |
| `year_start`, `year_end` 或 `model_year` | 是 | 展开用于查询，导出时可回聚，**跨代禁止自动合并** |
| `body_type` | 否 | 只用于车型身份消歧、异常检查；**不得作为唯一分类特征** |
| `trim`, `generation`, `market` | 否 | 尽可能保留；缺失则标注身份歧义 |
| `length_mm`, `width_mm`, `height_mm` | 否 | 统一为 mm；宽度默认要求明确不含后视镜，来源定义不清时注明 |
| `wheelbase_mm`, `front_overhang_mm`, `rear_overhang_mm` | 否 | 非必需，不可补猜 |

明确区分 `source_record_id`（原始行）与 `variant_key`（品牌+车型+年款+代际+车身版本+市场）；任何查证都绑定 `variant_key`。1973/1974 Mustang 不得跨代共享侧面证据；1974 Mustang II Coupe 与 Hatchback 不得共享未经证实的侧面图。

## 4. COVER_SHAPE 分类标签 V1（可版本化，不是既定 SKU）

- `LOW_FASTBACK`：整体低矮，长而连续的后部下降曲线。
- `LOW_NOTCHBACK`：整体低矮，明显独立尾箱台阶。
- `SPORT_LIFTBACK`：运动型乘员舱，后部倾斜掀背。
- `STANDARD_SEDAN`：常规三厢比例，明显后备厢。
- `COMPACT_HATCH`：车长较短、车头较短、乘员舱较高，尾部较短。
- `TALL_BOX`：较高且长的车顶，尾部趋向直立。
- `WAGON`：较长车顶，载物舱连续延伸，尾部较直立。
- `SLOPED_CROSSOVER`：较高车体且向尾部倾斜的跨界轮廓。
- `BOXY_SUV`：较高车体、较直立车尾和较长的高车顶。
- `PICKUP`：独立驾驶室与开放货箱；Cab/Bed 作为额外特征。
- `OTHER`, `UNKNOWN`：不适合现有类或资料不足。

标签必须与 `taxonomy_version` 绑定。分类阈值先由“人工标注的金标准样本”标定，不得凭空把高长比 `0.32` 等数值当成普适正确阈值。允许输出 `primary_shape`, `alternate_shapes`, `classification_rationale`, `review_required`。不能用 `body_type` 单字段直通标签；可在身份核对阶段辅助筛选。

## 5. 网络取证的优先级与适配器

| 级别 | 渠道 | 可用于验证哪些内容 | 注意 |
|---|---|---|---|
| A | 原厂规格表、官方宣传册、工程侧视资料 | 身份、原厂尺寸、侧面轮廓 | 验证年份/市场/车身版本；记录文档页码 |
| A/B | NHTSA Canadian Vehicle Specifications | OL/OW/OH/WB、A/B/C/D/F/G 等 | **覆盖不保证**；B 字段定义依车身类型变化，不能无条件跨类比较 |
| B | 可靠汽车媒体/历史资料正侧实拍 | 侧面轮廓辅助证据 | 必须核实图中型号和拍摄角度 |
| C | Sketchfab/其他 3D 资源 | 辅助人工验证 | 无尺寸校准及身份确认不可作为权威依据 |
| D | 搜索缩略图、论坛帖 | 检索线索 | 不足以使结果变为 VERIFIED |

NHTSA CVS 参考端点：`https://vpic.nhtsa.dot.gov/api/vehicles/GetCanadianVehicleSpecifications/?year=2011&make=Acura&format=json`。实现时确认 API 实际字段、返回状态、车型歧义和单位后再解析；不存在结果时为缺失，不能拿同车系其他版本填充。使用礼貌请求（默认 1 req/s/域名，可配置）、超时、重试指数退避、缓存、失败日志及域名白名单；遵守 robots、服务条款及授权。图片优先仅保存元数据、URL、许可标注和本地许可副本；不得在公开产物中再分发未经许可图片。

**每个证据对象必须有** `evidence_id`, `variant_key`, `evidence_type`, `source_url`, `publisher`, `retrieved_at_utc`, `model_year_claim`, `variant_claim`, `market_claim`, `source_rank`, `sha256`（有本地内容时）, `extraction_method`, `license_note`, `data_payload`, `validation_flags`。若来源断链，应通过缓存快照或档案索引复核；不可悄悄换源。

## 6. 侧面几何流水线

1. 搜索关键词：`{year} {make} {model} {trim} side profile official`、`factory brochure side view`、`side elevation`；同名跨代或多版本时加消歧词。
2. 身份核对：图片与具体年份、代际、Coupe/Hatchback、市场、车型版本对应；不确定则拒绝定量分析。
3. 侧视质量门禁：前后轮中心接近同一水平线、两轮视觉半径接近、车体无遮挡、整车入镜、低透视畸变、无严重改装；阈值在 fixtures 中校准。
4. 识别车辆前后端、轮心、车辆上缘轮廓；保存人工可检查的带关键点可视化。先实现人工关键点标注回退，自动分割算法作为第二阶段增强。
5. 使用整体车长归一化 `x ∈ [0,1]`，高度以地面基准/已知高度归一化；生成固定 64 点 `top_profile_64`，并记录轮廓缺失区间和质量分数。若缺少车高数据只能输出形状归一化的相对值，不可伪装为厘米级测量。
6. 派生可解释指标：`hood_ratio`, `roof_start_x`, `roof_end_x`, `roof_plateau_ratio`, `rear_slope_index`, `rear_deck_ratio`, `height_length_ratio`, `wb_length_ratio`。每个指标应有计算定义、合法范围、缺失处理和来源。
7. 多张独立图像交叉比较；差异大时标记 `CONFLICT`，不要简单平均消除冲突。

**严禁** 将 AI 生成图片、明显 3/4 视角、改装/压低底盘车型用作未经说明的定量依据；先做可信侧面图的“人工关键点+可复现计算”闭环，再做自动化。

## 7. 分类、可信度与状态机

决策流程：车型身份核实 → 证据一致性 → 几何可测程度 → 与人工标定的类别原型比较 → 输出候选及理由 → 审核状态。

分类依据主要是连续几何特征与视觉轮廓；长宽高为约束和辅助。可以用可解释的规则/最近原型距离分类，不应直接让语言模型回答“它是 Hatchback，所以分类为 COMPACT_HATCH”。

审核状态（独立于分类标签）：
- `VERIFIED`：具体车型身份匹配；权威尺寸来源或有据可查的原厂信息；至少一份合格侧面几何证据及独立交叉验证；关键特征没有未解决的重大矛盾；规则校验通过。
- `PROBABLE`：车型身份明确且至少有可信侧面证据，但独立验证/关键数据不全。
- `INFERRED`：同代、邻近年份或关联版本推断；必须说明推断链，不得自动用于正式版型决策。
- `CONFLICT`：年份/版本/尺寸/轮廓之间存在未解决实质冲突。
- `UNKNOWN`：缺少足够数据或图像不合格。

`review_required=true` 对 `INFERRED|CONFLICT|UNKNOWN` 强制开启，`PROBABLE` 默认开启；`VERIFIED` 可抽检。另设 `fit_tested=false` 和 `fit_status=NOT_TESTED`，永不与分类证据状态混淆。

## 8. 输出数据契约

### `outputs/cover_shape_results.csv`（每个 variant_key 一行）
字段至少：`source_record_id, variant_key, make, model, model_year, generation, body_type, market, length_mm, width_mm, height_mm, cover_shape, alternate_shapes, taxonomy_version, status, review_required, fit_status, reason_codes, evidence_ids, pipeline_version, processed_at_utc`。

### `outputs/cover_shape_features.jsonl`
每行：`variant_key`, `measurement_units`, `hood_ratio`, `roof_start_x`, `roof_end_x`, `rear_slope_index`, `rear_deck_ratio`, `top_profile_64`（可空）, `image_quality`, `uncertainty`, `feature_version`。

### `outputs/evidence.jsonl`
原始取证清单，不丢失搜索失败和来源冲突信息；URL、采集时间、版本关联及原始值可审计。

### `outputs/review_queue.csv`
按优先级排序：冲突、高风险错误（低掀背被识别为高箱式）、缺失侧视图、代际不明。包含 `why_review`, `evidence_ids`, `suggested_action`。

### `outputs/run_manifest.json`
记录输入文件哈希、运行时间、分类配置版本、依赖版本、使用的网络适配器、成功/失败计数与耗时；相同输入+冻结证据+相同版本应复现相同分类。

**先写临时文件并校验，成功后原子替换**。保留历史运行目录，不覆盖旧结果；禁止把输出直接写回原始数据库。

## 9. 建议仓库目录

```text
cover-shape-research/
├── STARTUP.md
├── AGENTS.md
├── README.md
├── pyproject.toml
├── .env.example              # 无真实凭证
├── config/
│   ├── column_map.example.yaml
│   ├── sources.yaml
│   ├── taxonomy_v1.yaml
│   └── pipeline.yaml
├── src/cover_shape/
│   ├── cli.py
│   ├── ingest.py
│   ├── normalize.py
│   ├── identity.py
│   ├── fetchers/             # cvs.py, official.py, image_search.py
│   ├── evidence.py
│   ├── image_quality.py
│   ├── keypoints.py
│   ├── geometry.py
│   ├── classifier.py
│   ├── review.py
│   └── export.py
├── tests/
│   ├── fixtures/            # 少量可合法使用的数据/标注
│   ├── test_identity.py
│   ├── test_geometry.py
│   ├── test_classifier.py
│   ├── test_provenance.py
│   └── test_end_to_end.py
├── data/input/               # gitignore 用户私有原始数据库
├── cache/                    # gitignore 网络缓存及图片
└── outputs/                  # gitignore 运行成果
```

## 10. 计划命令行接口（Codex 应实现，而非假定已存在）

```powershell
# 1. 创建环境，安装项目
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"

# 2. 只读检测输入列名、长度单位、重复和代际风险
cover-shape inspect --input "data/input/vehicles.xlsx" --out outputs/inspection.json

# 3. 检查并填写 config/column_map.yaml 后离线试运行
cover-shape run --input "data/input/vehicles.xlsx" --config config/pipeline.yaml --mode offline --sample tests/fixtures/pilot_variants.csv

# 4. 联网试运行：仅已允许的来源，限制批量条数和请求额度
cover-shape run --input "data/input/vehicles.xlsx" --config config/pipeline.yaml --mode online --limit 8

# 5. 批处理已缓存证据、重复运行检查
cover-shape reclassify --evidence outputs/evidence.jsonl --taxonomy config/taxonomy_v1.yaml
pytest -q
```

CLI 的参数名称以此作为开发契约；首次执行前应确保 Codex 已完成实现。接口不能默认开启无限量联网，需显式 `--mode online` 并提供费用及配额预估。

## 11. 第一批人工金标准测试案例

至少包含下列**待人工审定**的案例（年份与市场应具体确认）。这些期望类别是测试假设，**不是无证据的最终数据库事实**。

| 案例 | 期望区分点 | 候选标签 |
|---|---|---|
| 1974 Ford Mustang II Hatchback | 低矮长斜背，非高掀背 | LOW_FASTBACK |
| 1974 Ford Mustang II Coupe | 三厢尾部台阶 | LOW_NOTCHBACK |
| 2025 Honda Civic Hatchback（指定市场） | 运动化斜背 | SPORT_LIFTBACK |
| Toyota Yaris Hatchback（明确年份/市场） | 紧凑高舱短尾 | COMPACT_HATCH |
| 2025 Kia Soul | 较高、近直立后尾 | TALL_BOX |
| Tesla Model Y（明确年份） | 较高斜背跨界 | SLOPED_CROSSOVER |
| Toyota Prius（明确年份） | 低矮 Liftback，不直接等于普通 Hatch | SPORT_LIFTBACK（待审定） |
| BMW 3 Series GT F34 | 长斜背与较高座舱混合 | 待人工定标 |

增加反例回归测试：`BODY_TYPE=Hatchback` 的所有车型不能被强制同类；1973/1974 Mustang 换代不得自动合并；Coupe 与 Hatchback 的同年份图片不得互用；尺寸全缺失或图像角度失败时不能输出 VERIFIED。

## 12. 里程碑和验收标准

### 阶段 0 — 只读数据库审计
产物：`inspection.json`、字段映射草案、重复/缺失/车型代际报告。验收：**原始文件字节哈希不变**；不能识别的数据列明确记录，而非偷偷丢弃。

### 阶段 1 — 离线可信闭环（优先）
产物：8 个案例的 fixture、人工金标准表、来源 schema、分类器初版与测试。验收：全部端到端用例可离线复现；证据不足必然 UNKNOWN；不能发生 `Hatchback→COMPACT_HATCH` 的直接映射。

### 阶段 2 — 联网取证 MVP
产物：NHTSA CVS 适配器、网页/官方来源适配器、缓存、限速、数据溯源、请求失败报告。验收：能对至少 8 案例尝试联网检索，分别报告真实成功/无数据/超时/限制；API 返回不完整不补猜；无凭证时有明确错误或离线降级。

### 阶段 3 — 半自动侧面轮廓
产物：图片角度质量门禁、人工关键点回退、归一化轮廓、64 点采样和可视化叠加。验收：给同一 fixture 图片重复运行得到一致几何结果；不合格的 3/4 视角被拒绝，不得产生精确曲线。

### 阶段 4 — 批量分类与审核
产物：批处理、去重缓存、人工审核队列、覆盖率报表和审计日志。验收：每条非 UNKNOWN 分类拥有证据引用；每个 VERIFIED 满足门禁；每个冲突被标记；支持从缓存重跑且结果可复现。

### 阶段 5 — 推广前质量评估
在不用于模型标定的人工测试集上报告：总体分类准确率、每类混淆矩阵、VERIFIED 子集精确率、UNKNOWN 比率、关键误判案例。建议上线门槛作为**项目目标而非既有成绩**：`VERIFIED precision ≥ 98%`、关键错误（低矮斜背误识别为高箱式）为 0、每个 VERIFIED 均可追溯证据；不足则保持人工审核，不全库自动推广。

## 13. 人工审核与更新规则

人工审核只能通过单独的 `review_decisions.csv` 或数据库审核表实现，不得直接改写原始资料。审核记录至少包括 `variant_key`, `decision`, `reviewer`, `reviewed_at_utc`, `evidence_ids`, `reason`。审核前后的标签、几何特征和来源必须保留。增加新年份时先找同代证据，但继承前应验证前后保险杠、车顶、尾门和重大改款未改变轮廓。

## 14. 错误处理、安全与可运维

- 默认联网关闭；API key 使用环境变量，永不提交 `.env`，日志屏蔽凭证。
- 来源请求失败必须带错误码，不可静默返回空标签为“成功”。
- 记录请求频率、缓存命中率、模型/规则版本、处理单车成本及异常。
- 数据采集遵守 robots、API 配额、使用条款和版权；不依赖绕过验证码或反爬。
- 所有源的年份、市场和结构冲突产生 review 记录；任何自动标准化均保存前后值。
- 同一模型与同一 年份，如果不同 trim 造成车身外形变更，必须保留分支。
- 量化计算用 `pytest` 和手工标注 fixture 校验，不以“Codex 说像”替代几何验证。

## 15. 完工定义（Definition of Done）

- 有明确输入字段映射、缺失策略、证据模式及可运行 CLI。
- 8 个首批车型全部有输出行（允许 UNKNOWN），具备状态与来源；不存在虚构证据链接。
- 至少有一次联网真实测试报告和一次离线可复现测试报告，并区分成功与失败。
- 分类器不含 `BODY_TYPE→COVER_SHAPE` 硬编码映射。
- 结果与证据可以按 `variant_key` 追溯，原始车型数据库字节级不变。
- 清楚标记 `COVER_SHAPE` 与 `COVER_FIT` 的边界。

## 16. 开始前用户只需提供

1. 将现有车型文件放入 `data/input/`（CSV/XLSX/Parquet）；如果数据已在项目中，则由 Codex 只读定位。
2. 确认使用美国市场优先还是混合市场（默认沿用每条记录的 `market`，缺失时不得默认为美国原厂版本）。
3. 若有付费图片搜索 API 或特定数据权限，将令牌填入环境变量；没有亦可先完成离线 MVP 与免费来源适配器。

## 17. 官方参考

- Codex 项目级 `AGENTS.md`：https://github.com/openai/codex/blob/main/docs/agents_md.md
- NHTSA Vehicle API / 加拿大车辆规格查询：https://vpic.nhtsa.dot.gov/api/Home/Index

**实施顺序：先审计→离线可复现→联网取证→半自动轮廓→批处理；以审计与准确率而非分类填充率为主指标。**
