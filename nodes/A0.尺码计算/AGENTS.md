# 尺码计算 Agent

负责把尺寸库、车形和销量合成为各国全量尺码结果，并在同一节点内完成 US 的 TRIM 匹配。尺码规则、参数、店铺货架和 TRIM 资料由本 agent 在 `data/` 维护；当前正式结果写入 `output/`，每次计算完整快照写入 `artifacts/`。规则变更必须新增测试和 artifact，不得改写历史批次。

## 上游（第 4 层）

上游 `output/`：`01.整理尺寸库/尺寸库*.csv`、`02.分类结构审核/车型结构*.csv`、`03.车形分类核定/车形分类.csv` 与 `参考尺寸计算.csv`（车身号→系数）、`02.销量评估/原子销量.csv` 与 `RU代理销量.csv`（RU 全量表销量）。只读上游 `output/`，不读上游 `data/`。全量表不再带 `DIMENSION-CODE`，本节点不依赖 `02.代码映射`。

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
└─ 参考/ powerquery.md、插片必要性.md、新旧尺码对应/、车衣数据/（us/ru 车衣尺寸，供半周长分析）
```

## output/ 结构（`src/output_layout.py`，与 `pipeline.json` 的 `outputs` 一致）

```
output/
├─ US/
│  ├─ 尺码匹配报告.md   所用规则全文、参数、匹配概况与尺码分布、店铺货架与店铺分布、TRIM 概况
│  ├─ 尺码规则.json     报告规则表+参数的机器接口（含 规则ID、余量长容差 mm、规则/参数文件与 sha256）
│  ├─ 店铺货架.json     店铺 匹配尺码 → 发货尺码（data/US/店铺/货架.yaml 的结构化发布）
│  ├─ 新旧尺码对应.csv  新通用尺码 → 尺码代码（data/参考/新旧尺码对应/新旧尺码对应2.csv，LF）
│  ├─ 全量/全量表.csv   带 TRIM（TRIM 匹配回填）
│  ├─ 店铺/店铺全量_<店铺>.csv（HNT、TM、TM_拆分；与 US 全量同行同序，自动尺码为发货尺码，带 TRIM）
│  └─ TRIM/TRIM适配器.csv
├─ EU/  尺码匹配报告.md、尺码规则.json、全量/全量表.csv（无 TRIM 列）
└─ RU/  尺码匹配报告.md、尺码规则.json、全量/全量表.csv（无 TRIM 列）
```

文件名不带区域后缀，区域由目录表示。规则与店铺货架不再单独输出 CSV：md 报告中的表格供人阅读，机器读取用同源的 `尺码规则.json`、`店铺货架.json`（2026-10-14 起；下游不得解析 md 表格或读取本节点 `data/`）；各生成脚本的 JSON 状态只留在对应 artifact。

## 运行（`pipeline.json` 的 `run`，在节点目录执行）

1. `python src/generate_store_outputs.py`：US 基础尺码计算 → `data/US/规则/SHAPE调整.yaml` 对低矮掀背／溜背候选尝试普通3X规则（保留基础分类与白名单，仍检查原数值约束与店铺货架）→ `trim.matching.match_trims` 做 TRIM 匹配（`data/US/TRIM`，含 ID 迁移）→ 回填 US 与店铺全量表 `TRIM` → 输出 TRIM适配器。运行通过 RunBatch 保存上游引用与规则快照。
2. `python src/generate_ru_full_table.py`：RU 全量表。
3. `python src/build_regional_coverage_full.py`：EU 覆盖版全量表，RU 车形候选回填。
4. `python src/add_cover_shape.py`：只读 03 `output/COVER_SHAPE.csv`，按精确地区 DIMENSION-ID 仅回填国别与 US 店铺全量表的 SHAPE。状态/代表年/方法/备选/来源由 03 节点维护，不带入全量表。配置在 `data/全量SHAPE.yaml`；字段紧跟旧车形，本回填步骤保持其他原列值及行序不变。US生成阶段单独消费SHAPE与状态执行调整；EU/RU未启用。
5. `python src/build_match_report.py`：读取上述结果与 data/ 规则，生成三份 `尺码匹配报告.md` 及机器接口 `<国别>/尺码规则.json`、`US/店铺货架.json`、`US/新旧尺码对应.csv`；US报告包含SHAPE调整条件、证据提醒、基础→调整尺码与跳过原因，重算核对最终尺码。

只有 US 有 TRIM 环节；EU/RU 全量表不带 `TRIM` 列。TRIM 资料维护与离线工具见 [src/trim/README.md](src/trim/README.md)。

下游：`A1.压缩尺寸信息`（国别线/店铺线全量表）、`E0.尺寸分析`（宽高统计）、`B1.压缩定制评分`（评分键）、`C1`/`D*`/`X*`，以及网站流水线（读取全量表、店铺表、`尺码规则.json`、`店铺货架.json` 与 `US/新旧尺码对应.csv`）。

EU 覆盖版销量为零占位，RU 销量为 Auto.ru 代理，报告与下游必须保留该口径限制。
