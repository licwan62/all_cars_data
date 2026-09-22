# 适配器与 Trim 生成 Agent（并入 A1.全量生成 的 Trim 分支）

负责生成适配器、Trim 和覆盖率交付物。人工映射与覆盖规则放在 `data/`，当前稳定交付物写入 `output/`，每次生成快照写入 `artifacts/`。

上游：尺码计算和代码映射节点的 `output/`。

## 与 A1.全量汇总 的合并关系

本节点（`adapter-trim`）与下游 `A1.全量汇总`（`full-table-summary`）在职责上正在合并为一条统一叙事 **A1.全量生成**：本节点负责"用 4A fitment 原子把每个 `DIMENSION-ID` 匹配到可信 Trim"，A1 负责"把三区域全量表汇总并回填本节点产出的 Trim"。当前仍按 `pipeline.json` 维持两个物理节点（目录、`output/`、`artifacts/` 均不合并），只是文档上把两者作为同一条产物链描述；实际目录合并、`pipeline.json` 节点合并需由 `D2.链接分析` 另行决定并执行。

阅读顺序：本文件（Trim 匹配来源与规则）→ [B1 README.md](README.md)（TrimList 生成与联网审核细节）→ `A1.全量汇总/AGENTS.md`（汇总与回填规则）。

## Trim 匹配的数据源

- 逐年 `Year+Make+Model` 原子（"4A fitment"）：历史上来自仓库外 `source/4A全数据.csv`（该路径已不可用）。2026-09-22 找回一份快照 `4a_fitment_0722.tsv`（仅 `year/make/model` 三列，51826 行），现作为当前唯一可用的联网匹配基准，已转存为 `artifacts/2026-09-22_04_fitment-coverage-recovered-4a/input/4a_fitment_0722.csv`。
- 当前 dimension-id 库不再单独维护 `车型尺寸库.csv`：直接由 A0 `output/全量表_US.csv` 派生（`DIMENSION-ID` 去掉区域后缀 " US"），因为 `TrimList.csv` 的键本身就是无后缀的基础 ID。
- 原 `子车系维护表.csv`（`run.py`/`build_files` 全量重建所需的第三个输入）已不可用，**不得**再调用 `run.py` 对 `data/TrimList.csv` 做从零重建——那会丢失所有靠该表继承的"现有精确键"行。`data/TrimList.csv`/`TrimList_audit.csv` 现在本身就是被长期维护的状态，只做增量追加。

## 联网分析 dimension-id ↔ fitment 匹配（当前采用的增量流程）

1. `python analyze_fitment_coverage.py --fitment <4a快照.csv> --dimensions <A0全量表_US派生.csv> --trim data/TrimList.csv --review data/TrimList_online_review.csv --data-dir <批次输出目录>`：离线生成 `FitmentCoverage.csv`/`FitmentCoverageCandidates.csv`/`FitmentCoverageSummary.json`，标出哪些 4A 原子还没有 `DIMENSION-ID` 映射、哪些有语义候选。
2. `python research_nhtsa.py --review <候选文件> --report <报告路径> --evidence data/online_evidence.csv --apply-safe-evidence`：对候选中满足安全子集条件的记录发起 NHTSA vPIC 联网查询，命中的按 `DIMENSION-ID+Year+Make+Model` 键合并进 `data/online_evidence.csv`（非破坏性，仅新增/更新键，不删除既有证据）。
3. 增量把新批准的证据转成 `TrimList.csv`/`TrimList_audit.csv` 新行（校验：候选版本/结构与证据一致、键不在现有 TrimList 中、DIMENSION-ID+Year 落在当年 4A 原子集合内）；审核状态记为"联网证据批准"。这一步目前没有独立脚本，按 `artifacts/2026-09-22_04_fitment-coverage-recovered-4a/reports/apply_new_evidence_report.json` 记录的口径手工/临时脚本执行，后续如需固化为常规工具再补充到本目录。
4. `python refresh_from_size_output.py` 重新用更新后的 `TrimList.csv`/`TrimList_audit.csv` 生成 `output/TRIM适配器.csv` 与 `output/尺寸TRIM映射.csv`；读取 A0 `output/全量表_US.csv`、本节点 `data/TrimList.csv`、`data/TrimList_audit.csv` 及 `data/trim_values.csv`。后者保留已经审核的 TRIM 文本，以补充当前 A0 表的空 `TRIM` 列。已不在 US 尺寸库中的旧 TrimList 行只从本批次输入中排除，数量记录于批次状态，原始 `data/` 不改动。
5. 下游 `A1.全量汇总/build_consolidated_full_table.py` 用 `output/尺寸TRIM映射.csv` 回填汇总表的 `Trims` 列——完成"匹配→回填全量表"的整条链路。
