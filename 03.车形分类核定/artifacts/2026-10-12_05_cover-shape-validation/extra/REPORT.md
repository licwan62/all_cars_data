# 03 节点 COVER_SHAPE 实装验收（2026-10-12）

已实现阶段 0–2 的可运行研究 MVP，并提供人工关键点/64 点轮廓计算与可审计分类门禁。原型和真实侧面资料尚待人工核定，不宣称阶段 3–5 的真实数据验收已完成。

## 变更清单

- code/cover_shape/：ingest、evidence、geometry、classifier、fetchers、cli，新增 code/cover_shape_cli.py。
- data/cover_shape/：实际字段映射、taxonomy、来源与网络策略、pipeline、8 案例待审核表、证据导入入口及规则说明。
- tests/test_cover_shape_research.py：身份分支、单位、保留原值、合成几何、质量门禁、候选/冲突、VERIFIED 条件、API 形状、缓存/robots/配额、离线闭环、重分类与失败保护。
- pyproject.toml：可安装 cover-shape 命令；COVER_SHAPE.md：运行说明；.gitignore：仅排除新增的缓存、工作副本与打包文件。
- 未改用户已有 AGENTS.md/STARTUP.md、旧业务实现、pipeline.json、正式 output、流水线状态.md、NAS 发布目录。

## 运行与证据

在仓库根目录执行：

```powershell
python 03.车形分类核定/code/cover_shape_cli.py inspect --input 02.分类结构审核/output/车型结构.csv
python 03.车形分类核定/code/cover_shape_cli.py run --input 02.分类结构审核/output/车型结构.csv --sample 03.车形分类核定/data/cover_shape/pilot_cases.csv --mode offline
python 03.车形分类核定/code/cover_shape_cli.py run --input 02.分类结构审核/output/车型结构.csv --sample 03.车形分类核定/data/cover_shape/pilot_cases.csv --mode online --limit 8 --max-requests 20
python 03.车形分类核定/code/cover_shape_cli.py reclassify --evidence 03.车形分类核定/artifacts/2026-10-12_03_cover-shape-online/output/evidence-20261012_03.jsonl --taxonomy 03.车形分类核定/data/cover_shape/taxonomy_v1.yaml
python -m pytest 03.车形分类核定/tests -q
python scripts/validate_pipeline_structure.py
python scripts/verify_pipeline.py --rebuild shape-classification
```

批次 01 为只读盘点（47,356 行、主键无重复、缺失代际 3,248 行）；02 为真实 8 案例离线输出；03 为真实限量联网报告；04 为冻结联网证据离线重分类。03/04 除 processed_at_utc 外的结果 CSV 所有字段逐项相同。

8 案例均收到 NHTSA 响应，共 9 个 HTTP 请求、1 次缓存命中，耗时 25.789 秒。具体车身版本/代际与目标市场未确认，保留 CVS_VARIANT_AMBIGUOUS、CANADIAN_MARKET_UNCONFIRMED 等标记，不能由加拿大数据默认继承为美国等市场的原厂尺寸。全部 8 个输出 UNKNOWN，均进入复核队列，无 fitment/SKU 宣称。旧 03 批次 manifest 的 evidence_outcomes 将响应归入 IMPORTED；最终实现已细分 NO_DATA / VARIANT_AMBIGUOUS / UNCONFIRMED_MATCH，历史批次保持不可变。

图片检索未配置授权供应商：8 个 NOT_ATTEMPTED 检索计划，非联网图片检索成功记录。官方 URL 适配器已实装，但本次未配置车型官方资料；支持人工导入证据与关键点，未伪造来源 URL、图片许可或金标准。

## 验证结果与边界

- 03 节点：46 项测试通过；安装与 cover-shape --help 成功。
- 结构校验通过（17 节点）；03 正式 run 在只读沙箱重建，当前两张正式交付物逐字节一致。
- 原尺寸库、结构库、03 正式分类表 sha256 与执行前一致，详见 validation.json。
- 全仓 verify 已执行：仓库级测试 45 项通过，03 测试通过；A0 有 1 个失败（测试期待 4,378 行，实际 4,383 行），X1 有 4 个错误（旧批次 correct.csv 缺失）。与本次仅新增 03 研究文件无关，未修改这些节点。
- 追踪提示 03 新研究规则尚未发布；D2 另有已有规则变动和历史 artifact 引用提示。不得将静态验证“全部节点打通”解释为全仓测试通过。

## 规则与下一阶段

所有研究运行使用 RunBatch，已发布上游只记来源引用；data 全量规则记录 sha256 + git commit，未提交规则留快照。冻结重分类显式引用本节点已登记的历史输出，不复制上游数据库。

需要人工确认 8 个案例的年份/市场/代际与真实正侧面标注、独立原厂资料，随后在 data/cover_shape 标定原型和质量门禁，再使用未参与标定的保留集评估准确率/VERIFIED precision。当前无此数据，不能承诺 ≥98% 或批量正式推广。邻年/跨代推断、自动分割、审核决策应用、Parquet 与付费图片搜索尚未启用。正式接入须先由 pipeline.json 维护节点登记新增交付物，再经 publish_release 发布。
