# 全量生成 Agent（A 线：全量表 + TRIM 适配器）

`id: full-generation`。2026-09-22 由原 `A1.全量汇总`（`full-table-summary`）与 `B1.适配器-Trim生成`（`adapter-trim`）合并而成：一个节点内先做 Trim 匹配，再做三区域汇总与回填。人工映射与覆盖规则放在 `data/`，当前稳定交付物写入 `output/`，每次生成快照写入 `artifacts/`。历史批次分别保存在 `artifacts/legacy-adapter-trim/`（原 B1）与 `artifacts/legacy-full-table-summary/`（原 A1），只做了目录搬迁，内容未改动；合并后的新批次直接写在 `artifacts/<日期>_<序号>_<描述>/`，与两个历史前缀不会撞号。

上游：`A0.尺码计算/output/`（`全量表_US.csv`/`全量表_EU.csv`/`全量表_RU.csv`）。

## 两段职责

### 1. Trim 匹配（原 B1 逻辑）

把车型尺寸库中的每个 `DIMENSION-ID` 匹配到可信 Trim，产出 `output/TRIM适配器.csv` 与 `output/尺寸TRIM映射.csv`。

数据源：
- 逐年 `Year+Make+Model` 原子（"4A fitment"）：历史上来自仓库外 `source/4A全数据.csv`（该路径已不可用）。2026-09-22 找回一份快照 `data/4a_fitment_0722.tsv`（仅 `year/make/model` 三列，51826 行），现作为唯一可用的联网匹配基准。
- 当前不再单独维护 `车型尺寸库.csv`：dimension 库直接由 A0 `output/全量表_US.csv` 派生（`DIMENSION-ID` 去掉区域后缀 " US"），因为 `data/TrimList.csv` 的键本身就是无后缀的基础 ID。
- 原 `子车系维护表.csv`（`src/run.py`/`build_files` 全量重建所需的第三个输入）已不可用，**不得**再调用 `src/run.py` 对 `data/TrimList.csv` 做从零重建——那会丢失所有靠该表继承的"现有精确键"行。`data/TrimList.csv`/`TrimList_audit.csv` 现在本身就是被长期维护的状态，只做增量追加。

联网分析 dimension-id ↔ fitment 匹配的增量流程：

1. `python src/analyze_fitment_coverage.py --fitment <4a快照.csv> --dimensions <A0全量表_US派生.csv> --trim data/TrimList.csv --review data/TrimList_online_review.csv --data-dir <批次输出目录>`：离线生成 `FitmentCoverage.csv`/`FitmentCoverageCandidates.csv`/`FitmentCoverageSummary.json`，标出哪些 4A 原子还没有 `DIMENSION-ID` 映射、哪些有语义候选。
2. `python src/research_nhtsa.py --review <候选文件> --report <报告路径> --evidence data/online_evidence.csv --apply-safe-evidence`：对候选中满足安全子集条件的记录发起 NHTSA vPIC 联网查询，命中的按 `DIMENSION-ID+Year+Make+Model` 键合并进 `data/online_evidence.csv`（非破坏性，仅新增/更新键，不删除既有证据）。
3. 增量把新批准的证据转成 `TrimList.csv`/`TrimList_audit.csv` 新行（校验：候选版本/结构与证据一致、键不在现有 TrimList 中、DIMENSION-ID+Year 落在当年 4A 原子集合内）；审核状态记为"联网证据批准"。这一步目前没有独立脚本，按各批次 `reports/apply_new_evidence_report.json` 记录的口径手工/临时脚本执行，后续如需固化为常规工具再补充到本目录。
4. `python src/refresh_from_size_output.py`：重新用更新后的 `TrimList.csv`/`TrimList_audit.csv` 生成 `output/TRIM适配器.csv` 与 `output/尺寸TRIM映射.csv`；读取 A0 `output/全量表_US.csv`、本节点 `data/TrimList.csv`、`data/TrimList_audit.csv` 及 `data/trim_values.csv`（后者保留已审核的 TRIM 文本，补充 A0 表的空 `TRIM` 列）。已不在 US 尺寸库中的旧 TrimList 行先按 `data/TrimList_ID迁移.csv`（旧ID、Year、新ID、依据；新ID 留空表示按规则不映射）迁移到当前 ID，并同步 `trim_values.csv` 的 Trims；仍无对应的才从本批次输入中排除，迁移/排除数量记录于批次状态，原始 `data/TrimList*.csv` 不改动。上游尺寸库改名或拆分 ID 时必须补这张表。

详见 [README.md](README.md)（TrimList 生成、例外维护、联网证据字段的完整规则）。

### 2. 全量汇总与回填（原 A1 逻辑）

把 `A0.尺码计算/output/` 的 `全量表_US.csv`、`全量表_EU.csv`、`全量表_RU.csv` 汇总为 `output/全量表_汇总.csv`，并按 US `DIMENSION-ID` 去掉区域后缀 lookup 本节点刚生成的 `output/尺寸TRIM映射.csv` 的 `Trims` 列（同节点内部依赖，不再跨节点读取）。EU/RU 与未命中的 US 行留空，并在批次状态记录覆盖数。三张区域表都必须存在并带 `DIMENSION-CODE`，`DIMENSION-ID` 跨区域唯一；缺任一区域、缺码或映射键重复时失败，不改变 `output/`。

汇总列 = 各区域列的并集，`DIMENSION-CODE`、`DIMENSION-ID` 固定为最后两列。

```powershell
python src/build_consolidated_full_table.py
```

## 运行顺序

Trim 匹配（第 1 段第 4 步 `refresh_from_size_output.py`）产出新的 `output/尺寸TRIM映射.csv` 后，必须重跑 `python src/build_consolidated_full_table.py`（第 2 段）才能把新匹配到的 Trim 回填进 `output/全量表_汇总.csv`；两段共用同一个 `output/manifest.json`，由 `scripts/publish_release.py` 统一发布。

当前已可汇总三地区全量表；EU 覆盖版中的销量零值为占位，RU 销量为区域代理，汇总表必须保留该口径限制。遵守仓库根目录 `AGENTS.md`。
