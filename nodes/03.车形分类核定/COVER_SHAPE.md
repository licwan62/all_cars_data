# COVER_SHAPE 自动判断

## 全量表接口

当前接口：A0 全量表仅保留 `SHAPE` 一列；`SHAPE_STATUS`、`SHAPE_YEAR`、`SHAPE_METHOD`、`SHAPE_ALTERNATES`、`SHAPE_SOURCE` 均在 03 的 `output/COVER_SHAPE.csv` 维护。

### 研究队列（2026-10-12 起按车型族 + 研究缓存推进）

旧队列以「代表分支」为单位（US 2,814 项、每项一个尺寸分支/年份），成功结论也不覆盖同族其他分支，推进过慢。现参照旧车身号研究缓存（`cache/model_shape_cache.csv` + `shape_project.py claim/batch-update`）改为：

- **研究单元 = 市场 + 品牌 + 车型 + 结构（车型族）**。结构不同（Coupe/Convertible/Hatchback…）分开研究；代际、年份、尺寸、trim、CAB/BED 不再拆任务。US 997 族，EU 4,456 族，RU 6,147 族。
- **只研究少数年份**：每个代际跨度 < 9 年取中位年；更长的代际按分位取 2 个年份（前期/后期，覆盖改款）。多个代际外形相同时，一条不带代际的规则即可覆盖。
- **结论写入研究缓存** `data/cover_shape/family_cache.csv`：`market, make, model, body_type` 必填，可选 `generation / year_start / year_end / match_pattern` 细分，`shape / alternates / sample_years / source_url / note` 记录结论与实际研究年份。最具体规则优先（模式 > 代际 > 年份），同级冲突报错。
- **全族继承**：含抽样年份的记录 `PROBABLE`（`family_cache_sampled`），同族其余年份/尺寸/trim `INFERRED`（`family_cache_inherited`）；EU/RU 无本市场结论时，按年份重叠复用 US 同车型/结构结论（`family_cache_cross_market`，INFERRED）。精确分支的冻结几何证据仍优先于缓存；没有规则的记录维持原型推断。
- `output/shape_research_queue.jsonl` 每行一个车型族：各代际年份跨度、记录数、已覆盖数、建议抽样年、状态（PENDING/PARTIAL/CACHED/BLOCKED_INPUT/NO_EVIDENCE/DEFERRED_LIMIT/CONFLICT）和自动研究进度。状态由缓存覆盖情况重建；成员变化时进度失效。队列 JSONL 不发布到 NAS。

人工/Agent 研究（推荐，参照旧车身缓存流程）：

```powershell
# 节点目录
python code/shape_family_research.py claim --limit 10 --worker <名字> [--market US]
python code/shape_family_research.py records --worker <名字>     # 只列未覆盖记录
python code/shape_family_research.py apply --file <规则.json> --worker <名字>
python code/shape_family_research.py status
python code/build_cover_shape_output.py                            # 重建 COVER_SHAPE 与队列
# 或循环调用 codex：每批领取、研究、apply，每 5 批重建一次
pwsh -File code/run_shape_family_research.ps1 -BatchSize 10 -Market US
```

千问 API 研究（不经智能体，直接调用接口，可与 codex worker 并行）：

```powershell
Copy-Item research_queue/qwen_config.example.yaml research_queue/qwen_config.yaml   # 本地配置，已 gitignore
setx DASHSCOPE_API_KEY "sk-..."                                                     # 或在本地配置写 api_key
python code/qwen_family_research.py --dry-run --families <family_id> ...           # 对照试跑，不写入
python code/qwen_family_research.py --limit 50                                     # 研究 50 个族；省略则跑到没有可领取的族
```

检索来源用 `search_provider` 选择：`tavily`（推荐）先调 Tavily 英文网页搜索（每族 1 条整族 + 按代际抽样年补充，最多 `queries_per_family` 次），结果编号连同摘要附在提示中，千问只做判断；`dashscope` 用百炼内置联网搜索（偏中文网页）。推理模型须保持 `enable_thinking: false`，否则单族可达 5 分钟并超时。配置可选 `api_style: dashscope`（百炼原生接口，联网搜索并返回来源，推荐）或 `openai`（任意 OpenAI 兼容接口），以及 base_url、model、并发、重试、检索策略等。每路并发用独立 worker 名 `qwen-family-N`；来源 URL 只取检索结果编号映射，不接受模型编造；校验不过把错误反馈给模型修正（`max_fix_attempts`），仍失败的族记入 `work/qwen_runner/skipped.jsonl` 不再领取（`--retry-skipped` 重试）。逐族请求/回复/来源记录在 `work/qwen_runner/log-YYYYMMDD.jsonl`。`run_shape_family_release.ps1` 发布前会等待千问研究进程结束。

`apply` 校验：提交的族与领取一致；每条规则至少匹配一条记录，`sample_years` 必须落在规则覆盖的年份内；整族所有记录都被规则覆盖，否则拒绝写入。提交的族整族重写旧规则。

自动联网研究（可选）：`research_cover_shape.py` 也按车型族消费队列，每族研究最多 2 个未覆盖代际的抽样年份；合格几何结论写成该代际的缓存规则（worker=automatic），失败 48 小时后重试，最多 3 次。

```powershell
python code/research_cover_shape.py --mode online --market US --limit 8 --max-requests 120 --plan-only
python code/research_cover_shape.py --mode online --market US --limit 8 --max-requests 120
```

在线研究保存所有成功、无数据、来源拒绝和图片门禁失败记录；只有真正提取的几何事实进入 data/evidence.jsonl，失败不会被当作覆盖，也不会提升为 VERIFIED。缓存结论最高 PROBABLE，不代表车罩适配（fit_status 始终 NOT_TESTED）。

正式流程新增 `python code/build_cover_shape_output.py`，生成 `output/COVER_SHAPE.csv` 和 `cover_shape_summary.json`。所有 47,356 条结构记录已有 SHAPE 分类；37,042 个精确分支各选一个代表年，优先已有几何证据源年款，否则选覆盖年份下中位数，选出的年份一定属于该分支。分支区分市场、代际、车身版本、trim、CAB/BED、尺寸和旧几何原型；代际缺失时按源行隔离。

按照用户确认的全覆盖口径，车型级冻结几何证据优先，其余以 `data/cover_shape/full_table.yaml` 的旧几何原型先验加尺寸推断，状态为 INFERRED，后部形态未解决时保留备选。原型是先验假设，不伪装为该车型实际轮廓；20 条尺寸缺失/无效的特殊车辆分类为 OTHER，不补猜尺寸。代表分支可能覆盖多行，同组某行的 SHAPE_YEAR 可能在该行年份区间外，其来源是同代、同版本、同尺寸的组内代表记录，详见批次代表年审计。

A0 正式流程新增 `src/add_cover_shape.py`，三国全量与三个 US 店铺全量表紧跟原有 `车形` 列加入 SHAPE。原有年份、尺寸、销量、尺码、行序及 TRIM 不变。SHAPE 不参与尺码匹配；不得把这些推断说成车型级 VERIFIED 或实际车罩适配。

全量正式生成离线运行，不对 47,356 条记录默认无限联网。更新车型级证据时，可显式通过 `code/import_cover_shape_evidence.py --evidence <冻结研究输出>` 维护 data/ 的必要参考，保留来源/源年款/哈希，再重跑全量接口。下游只读 output 稳定文件名，不依赖研究批次日期。

当前版本 0.2.0 已启用自动研究，不要求用户提供侧视图、关键点或人工标定样本。联网运行自动读取已发现的原厂/历史文档，提取明确的车顶、尾部和座舱几何描述；同时通过 Commons 正式 API 动态搜索有许可照片，用 CPU 分割、轮心与椭圆门禁提取合格轮廓，再由几何特征与长高比例生成类别及备选。初始来源索引只存来源和身份范围，不存车型对应标签；新车型也会执行动态照片搜索。

从本节点目录运行：

```powershell
python -m pip install -e ".[automatic,dev]"
cover-shape run --input "../02.分类结构审核/output/车型结构.csv" --mode online --sample data/cover_shape/pilot_cases.csv --limit 8 --max-requests 200
# 冻结证据可离线重分类，不访问网络。替换批次/版本为命令返回值。
cover-shape reclassify --evidence "artifacts/<批次>/output/evidence-<版本>.jsonl" --taxonomy data/cover_shape/taxonomy_v1.yaml --automatic data/cover_shape/automatic.yaml
python -m pytest tests -q
```

当前自动路径不需要付费密钥。分割模型首次联网下载并校验固定 SHA-256，依赖/权重/来源和失败请求均留档。默认 offline 仍关闭网络；开启 online 必须有明确 limit，配额涵盖 robots、重试和同域重定向。HTML 遵守 robots/Crawl-delay，正常同域 HTTPS 重定向最多 3 次并记录；跨域不会隐式跟随。公开 JSON API 和其返回的有许可媒体按正式 API 使用，不爬取 HTML 搜索页。

自动路径采用未标定的可解释试验规则，候选最高 INFERRED，保留复核选项；程序不等待人工提供资料。冲突为 CONFLICT，未找到足够依据为 UNKNOWN。没有实测侧视几何的文本结果仅为 qualitative，top_profile_64 留空。源资料的真实年款/市场/代际与目标 variant_key 分开记录，跨年使用仅限上游已声明的同一车型分支年份区间，并保留推断链与未验证改款的限制。所有结果仍 fit_status=NOT_TESTED，不分配 SKU，不更新正式旧车形接口。

照片门禁会拒绝拍摄日期冒充年款、明确标题与描述车型矛盾、Coupe/Hatchback 混用、普通版混入 Type R 等外形版本、改装/AI 图/模型车、裁切车体、无法识别相近双轮及不合格轮胎椭圆。先前探索批次 06 含宽松过滤下的错误候选且规则曾在运行中调整，不能作为质量成绩；批次 07 展示收紧门禁后的拒绝情况。最终实现已增加代码/规则运行前后哈希检查，变化时整个批次失败。

## 初始阶段说明（历史）

在现有 03 节点中新增独立 Python CLI：只读车型库、显式列映射、逐年身份分支、证据导入/审计、人工关键点计算、已审原型候选分类、证据状态门禁、复核队列和冻结证据重分类。实现位于 `code/cover_shape/`；维护资料位于 `data/cover_shape/`。沿用当前节点目录和 pipeline.json 登记的 code_dir，不重构旧流程。

研究产物通过共享 `lib/artifact_batch.py` 创建不可变批次，输出带 `-YYYYMMDD_NN` 后缀，输入使用已发布上游引用，规则按 sha256 + git commit 留档；未提交规则自动快照。此研究 CLI 不发布正式 output/，因此不改变现有车形号及 A0 尺码匹配。正式流程仍是 pipeline.json 登记的 build/validate 命令。研究规则新增后 trace_pipeline 会提示 03 规则变化，待明确接入正式交付时由 pipeline.json 维护节点登记并通过 publish_release 发布。

从 **03 节点目录** 执行（不安装也可使用 `python code/cover_shape_cli.py` 代替 `cover-shape`）：

```powershell
python -m pip install -e ".[dev]"

cover-shape inspect --input "../02.分类结构审核/output/车型结构.csv"

cover-shape run --input "../02.分类结构审核/output/车型结构.csv" --config data/cover_shape/pipeline.yaml --mode offline --sample data/cover_shape/pilot_cases.csv

cover-shape run --input "../02.分类结构审核/output/车型结构.csv" --config data/cover_shape/pipeline.yaml --mode online --sample data/cover_shape/pilot_cases.csv --limit 8 --max-requests 20

# 将 <批次>、<版本> 替换为命令返回的实际目录/文件版本。
cover-shape reclassify --evidence "artifacts/<批次>/output/evidence-<版本>.jsonl" --taxonomy data/cover_shape/taxonomy_v1.yaml

python -m pytest tests -q
```

inspect 支持 `--out work/inspection.json` 生成可重建工作副本，且默认生成 inspection artifact 和映射草案，不覆写任何输入。CSV/TSV/XLSX 均只读；未启用 Parquet。默认 offline，不进行任何网络访问。online 必须显式指定正数 limit，max-requests 包括 robots 和重试。默认 1 请求/秒/域名，15 秒超时、一次指数退避重试、白名单、robots、禁止隐式重定向与秘密 URL 参数。当前只有免费 NHTSA CVS 自动请求；官方来源须在 data/cover_shape/sources.yaml 配置精确 URL；无图片检索供应商时生成明确 NOT_ATTEMPTED 检索计划，通过 --evidence 导入人工来源/标注。

每次研究生成 cover_shape_results.csv、cover_shape_features.jsonl、evidence.jsonl、review_queue.csv、cover_shape_records.jsonl、run_manifest.json 和 run.json。CSV 中保留原始行 ID、原始字段及多个来源行；variant_key 分开品牌/车型/年款/代际/车身版本/trim/市场。相同身份但不同尺寸不会静默覆盖，进入 CONFLICT。reclassify 自动读取同批次 records 文件，保留无证据的 UNKNOWN 分支；也可显式 --records 指定。

人工标注的 64 点曲线仅表示相对侧面形状，缺失区间不外推，不合格角度/AI 图/改装图不参与分类；可输出 SVG 关键点示意，未自动下载或公开再分发来源照片。分类只使用几何特征和经审核原型，不读取 MODEL/BODY_TYPE 作标签捷径。所有状态均 fit_tested=false / fit_status=NOT_TESTED。

本次 8 案例来自真实上游记录，期望类别全部 PENDING；侧面证据及金标准尚未人工核定，因此 taxonomy 原型为空，真实输出如实 UNKNOWN。自动化测试中的合成几何仅验证算法与门禁，不是车型证据。尚不能报告总体准确率、VERIFIED precision 或宣称全库可推广。

2026-10-12 联网批次 `2026-10-12_03_cover-shape-online`：7 次 HTTP 成功、1 次缓存命中，覆盖全部 8 案例；另有 2 次失败请求，分别为 robots.txt 的 HTTP 404 和 Prius 查询的 URLError（约 15 秒后失败，重试成功）。所有逐请求记录在该批次 extra/network_requests.jsonl；不能将最终收到响应解释为所有请求首次成功。8 个响应均待核实具体版本及市场，未提升分类状态。冻结证据重分类批次 04 与联网批次结果除处理时间外所有 CSV 字段一致。

下一阶段依次补充：真实侧面图的身份/许可/关键点审核、独立原厂交叉证据、人工金标准与类别原型、保留集质量评估，再决定批量运行和正式流水线接入。人工审核必须留单独决策记录，不能改写原始库。当前不执行邻年/跨代继承，不将研究分类变成 fitment/SKU。
