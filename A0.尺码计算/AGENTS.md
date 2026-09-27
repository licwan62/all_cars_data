# 尺码计算 Agent

负责把尺寸库、车形和销量合成为各国全量尺码结果，并在同一节点内完成 US 的 TRIM 匹配。尺码规则、参数、店铺货架和 TRIM 资料由本 agent 在 `data/` 维护；当前正式结果写入 `output/`，每次计算完整快照写入 `artifacts/`。规则变更必须新增测试和 artifact，不得改写历史批次。

## 上游（第 4 层）

上游 `output/`：`01.整理尺寸库/尺寸库*.csv`、`02.分类结构审核/车型结构*.csv`、`03.车形分类核定/车形分类.csv` 与 `参考尺寸计算.csv`（车身号→系数）、`02.销量评估/原子销量.csv`。全量表不再带 `DIMENSION-CODE`，本节点不依赖 `02.代码映射`。

## data/ 结构（`src/data_layout.py`）

```
data/
├─ 当前规则.yaml  各国别当前生效的规则文件、尺码字段、参数文件（换版本只改这里）
├─ US/
│  ├─ 规则/  各版本尺码规则
│  ├─ 参数/  尺码匹配参数.csv
│  ├─ 店铺/  货架.yaml（店铺匹配尺码 → 发货尺码）
│  └─ TRIM/  TrimList、TrimList_audit、trim_values、TrimList_ID迁移、联网证据与研究产物
├─ EU/  规则/尺码匹配规则.csv、参数/尺码匹配参数.csv、研究/当前已审核全量.csv
├─ RU/  规则/、参数/（各版本）、参考/ozon映射.csv
└─ 参考/ powerquery.md、新旧尺码对应/
```

## output/ 结构（`src/output_layout.py`，与 `pipeline.json` 的 `outputs` 一致）

```
output/
├─ US/
│  ├─ 尺码匹配报告.md   所用规则全文、参数、匹配概况与尺码分布、店铺货架与店铺分布、TRIM 概况
│  ├─ 全量/全量表.csv   带 TRIM（TRIM 匹配回填）
│  ├─ 店铺/店铺全量_<店铺>.csv（HNT、TM、TM_拆分；与 US 全量同行同序，自动尺码为发货尺码，带 TRIM）
│  └─ TRIM/TRIM适配器.csv
├─ EU/  尺码匹配报告.md、全量/全量表.csv（无 TRIM 列）
└─ RU/  尺码匹配报告.md、全量/全量表.csv（无 TRIM 列）
```

文件名不带区域后缀，区域由目录表示。规则与店铺货架不再单独输出 CSV，以 md 报告中的表格为准；各生成脚本的 JSON 状态只留在对应 artifact。

## 运行（`pipeline.json` 的 `run`，在节点目录执行）

1. `python src/generate_store_outputs.py`：US 尺码计算 → `trim.matching.match_trims` 做 TRIM 匹配（`data/US/TRIM`，含 ID 迁移）→ 回填 US 与店铺全量表 `TRIM` → 输出 TRIM适配器。
2. `python src/generate_ru_full_table.py`：RU 全量表。
3. `python src/build_regional_coverage_full.py`：EU 覆盖版全量表，RU 车形候选回填。
4. `python src/build_match_report.py`：读取上述结果与 data/ 规则，生成三份 `尺码匹配报告.md`。

只有 US 有 TRIM 环节；EU/RU 全量表不带 `TRIM` 列。TRIM 资料维护与离线工具见 [src/trim/README.md](src/trim/README.md)。

下游：`A1.全量生成`（宽高统计）、`A2.压缩尺寸信息`（国别线/店铺线全量表）、`B1.压缩定制评分`（评分键）、`C1`/`D*`/`X*`，以及网站流水线（读取全量表、店铺表与报告中的规则/货架表格）。

EU 覆盖版销量为零占位，RU 销量为 Auto.ru 代理，报告与下游必须保留该口径限制。
