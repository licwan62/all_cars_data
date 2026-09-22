# 全量汇总 Agent（A 线：全量表，与 B1 合称 A1.全量生成）

把 `A0.尺码计算/output/` 的 `全量表_US.csv`、`全量表_EU.csv`、`全量表_RU.csv` 汇总为 `output/全量表_汇总.csv`，并按 US `DIMENSION-ID` 去掉区域后缀 lookup `B1.适配器-Trim生成/output/尺寸TRIM映射.csv` 的 `Trims` 列。EU/RU 与未命中的 US 行留空，并在批次状态记录覆盖数。三张区域表都必须存在并带 `DIMENSION-CODE`，`DIMENSION-ID` 跨区域唯一；缺任一区域、缺码或映射键重复时失败，不改变 `output/`。

## 与 B1.适配器-Trim生成 的合并关系

本节点（`full-table-summary`）与上游 `B1.适配器-Trim生成`（`adapter-trim`）职责上正在合并为一条统一叙事 **A1.全量生成**：B1 负责"用 4A fitment 原子联网分析把每个 `DIMENSION-ID` 匹配到可信 Trim"（详见 `B1.适配器-Trim生成/AGENTS.md`），本节点负责"汇总三区域全量表并回填 B1 产出的 Trim"。当前仍按 `pipeline.json` 维持两个物理节点（目录、`output/`、`artifacts/` 均不合并），只是文档上把两者作为同一条产物链描述；实际目录合并、`pipeline.json` 节点合并需由 `D2.链接分析` 另行决定并执行。

数据链路：`4a_fitment_0722.tsv`（找回的 4A 原子快照）→ B1 联网匹配/审核 → `B1/output/尺寸TRIM映射.csv` → 本节点回填 → `output/全量表_汇总.csv`。B1 侧每次更新 Trim 映射后，本节点需重跑 `python build_consolidated_full_table.py` 才能把新匹配到的 Trim 回填进全量表。

汇总列 = 各区域列的并集，`DIMENSION-CODE`、`DIMENSION-ID` 固定为最后两列。

```powershell
python build_consolidated_full_table.py
```

当前已可汇总三地区全量表；EU 覆盖版中的销量零值为占位，RU 销量为区域代理，汇总表必须保留该口径限制。遵守仓库根目录 `AGENTS.md`。
