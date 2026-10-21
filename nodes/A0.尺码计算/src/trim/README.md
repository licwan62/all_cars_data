# TrimList v2 生成器

> **2026-09-27 迁移**：TRIM 匹配已从 `A1.全量生成`（现 `E0.尺寸分析`）迁入 `A0.尺码计算`：代码在 `src/trim/`，维护资料在 `data/US/TRIM/`。正式流程由 `src/generate_store_outputs.py` 在计算 US 尺码后调用 `trim.matching.match_trims`，回填 US/店铺全量表的 `TRIM` 列并输出 `output/US/TRIM/TRIM适配器.csv`；下文中的 `rebuild_trimlist.py`（原 `src/run.py`）、`analyze_sizes.py` 等为离线维护工具，默认写入 `work/trim/`，不直接改 `output/`。只有 US 有 TRIM 环节。


本项目将车型尺寸库中的 `DIMENSION-ID` 直接映射到 4A 的逐年
`Make + Model` 原子，用于取代原来依赖
`Year + 主车型 + 结构 + 版本 + 分号候选字符串`
的中间维护表。所属节点见 [A0 AGENTS.md](../../AGENTS.md)。

> **当前状态（2026-09-22）**：本节README下方描述的 `source/4A全数据.csv`、`source/车型尺寸库.csv`、`source/子车系维护表.csv`（仓库外 `source` 目录）均已不可用，`src/run.py` 的全量重建路径**不可再运行**（会因缺少子车系维护表丢失所有"现有精确键"行）。找回的 4A 原子快照 `data/US/TRIM/4a_fitment_0722.tsv`（仅 `year/make/model`）现作为联网匹配的唯一基准；`data/US/TRIM/TrimList.csv`/`TrimList_audit.csv` 是被长期维护的状态，只做增量追加，不再从零重建。当前实际使用的命令是 `analyze_fitment_coverage.py`（离线匹配分析）→ `research_nhtsa.py --apply-safe-evidence`（联网审核）→ 增量写入 TrimList → `refresh_from_size_output.py`（生成 Trim 交付物）→ `build_consolidated_full_table.py`（回填全量表）。详见 [AGENTS.md](AGENTS.md) 的完整流程。以下为历史设计文档，作为字段与门禁规则的参考。

共享输入统一来自仓库 `source`；项目在 `data` 中维护 Trim 例外、联网证据以及全部研究/校验中间产物。正式输出遵守两层门禁：

1. 候选必须存在于当年 `source/4A全数据.csv` 的 `Year + Make + Model`。
2. 除“继承现有精确键”外，必须在 `data/US/TRIM/online_evidence.csv` 提供联网证据，
   且证据的年份、版本、结构必须与 `DIMENSION-ID` 源记录一致。

## 输出

`output` 只保留两个最终交付文件：

- `output/US/TRIM/TRIM适配器.csv`：为 `TrimList` 的每一行回填 `Size`，包括“无可用尺码/数据不全”等状态值，不丢行。
- US 全量表与店铺全量表的 `TRIM` 列：每个 `DIMENSION-ID` 由已审核 TRIM 值规范化得到，多个名称以 ` | ` 分隔（原 `尺寸TRIM映射.csv` 已不再单独输出）。

## Data 与研究产物

`data/US/TRIM/TrimList.csv` 是适配器生成所用的 DIMENSION-ID 到逐年车型映射：

```csv
DIMENSION-ID,Year,Make,Model
Acura ADX SUV 2025-2026,2025,Acura,ADX
Acura ADX SUV 2025-2026,2026,Acura,ADX
```

每行只有一个候选，不使用分号合并。主键为：

```text
DIMENSION-ID + Year + Make + Model
```

其余中间结果和所有研究产物统一写入 `data`：

- Trim 映射与审核：`TrimList*.csv`、`validation_report.json`
- 4A 覆盖研究：`FitmentCoverage*.csv/json`
- 尺码关联分析：`DimensionSizeMap.csv`、`AdapterSizeList.csv`、`SizeAnalysis*`、`MultipleSize*`、`NoPublishableSizeReport.csv`
- NHTSA 研究：`NHTSAResearchReport.csv`、`NHTSAFitmentCoverageResearch.csv`
- 研究输入：`online_evidence.csv`、`trim_overrides.csv`

## 运行

在当前目录执行：

```powershell
python src/trim/rebuild_trimlist.py
```

如只需重新分析已生成的 TrimList：

```powershell
python src/trim/analyze_sizes.py
```

如只生成 TrimList：

```powershell
python src/trim/rebuild_trimlist.py --skip-size-analysis
```

默认读取：

- `../source/车型尺寸库.csv`
- `../source/4A全数据.csv`
- `../source/子车系维护表.csv`
- `../source/尺码分析.csv`
- `data/US/TRIM/trim_overrides.csv`（项目专属）
- `data/US/TRIM/online_evidence.csv`（项目专属）

也可指定路径：

```powershell
python src/trim/rebuild_trimlist.py `
  --dimensions ..\source\车型尺寸库.csv `
  --fitment ..\source\4A全数据.csv `
  --maintenance ..\source\子车系维护表.csv `
  --size-source ..\source\尺码分析.csv `
  --online-evidence .\data\online_evidence.csv `
  --data-dir .\data `
  --output-dir .\output
```

如果需要将未匹配或待联网审核候选视为构建失败：

```powershell
python src/trim/rebuild_trimlist.py --fail-on-unmapped --fail-on-unreviewed
```

## 例外维护

`data/US/TRIM/trim_overrides.csv` 只维护例外，不复制全量映射。

```csv
DIMENSION-ID,Year,Action,Make,Model,Note
...,2025,ADD,Acura,ADX,手工确认
...,2025,REMOVE,Acura,ADX,排除错误候选
...,2025,CLEAR,,,当年不发布
```

支持的 `Action` 为 `ADD` / `REMOVE` / `CLEAR`。`ADD` 仍必须通过当年 4A
校验；如果新增候选不属于现有精确键，也必须提供联网证据。

## 联网证据

`data/US/TRIM/online_evidence.csv` 每行审核一个原子候选：

```csv
DIMENSION-ID,Year,Make,Model,版本,结构,Decision,SourceURL,SourceTitle,EvidenceNote,ReviewedAt
...,2025,Acura,ADX,,SUV,APPROVE,https://...,官方车型资料,年份及SUV结构一致,2026-08-27
```

- `Decision` 只能为 `APPROVE` 或 `REJECT`。
- `APPROVE` 必须填写 HTTP(S) 来源。
- `版本`、`结构` 必须原样匹配车型尺寸库；不匹配时构建直接失败。
- 联网检索以厂商资料、NHTSA/vPIC 等可追溯来源为优先。

可先运行 NHTSA 安全子集审核：

```powershell
python src/trim/research_nhtsa.py --apply-safe-evidence
python src/trim/rebuild_trimlist.py
```

该命令仅自动批准：1996 年以后、源/候选 Make+Model 同名、版本为空，且
NHTSA 在同年对应车辆类型中返回该 Model 的记录。详细查询结果写入
`data/US/TRIM/NHTSAResearchReport.csv`。无法证明具体版本或 Sedan/Coupe/Convertible
等细分结构的记录仍保留在联网审核队列。

对全量 4A 新发现的候选可继续运行：

```powershell
python src/trim/research_nhtsa.py `
  --review .\data\FitmentCoverageCandidates.csv `
  --report .\data\NHTSAFitmentCoverageResearch.csv `
  --apply-safe-evidence
python src/trim/rebuild_trimlist.py
```

## 匹配顺序

1. 继承当前子车系表的精确年份、主车型、结构、版本。
2. 其余算法候选仅用于生成联网审核队列，不直接发布。
3. 联网证据必须同时证明年份、Make、Model、版本和结构的语义关系。
4. 通过审核后仍须再次校验候选存在于当年 4A。
5. 多结构确实存在时，保留所有对应 `DIMENSION-ID + Size` 分支。
6. 其余记录输出到 `TrimList_online_review.csv` 或 `TrimList_unmapped.csv`。

## 测试

```powershell
python -m pytest A0.尺码计算/tests/test_trimlist.py A0.尺码计算/tests/test_size_analysis.py A0.尺码计算/tests/test_fitment_coverage.py A0.尺码计算/tests/test_trim_matching.py
```
