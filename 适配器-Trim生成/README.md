# TrimList v2 生成器

本项目将车型尺寸库中的 `DIMENSION-ID` 直接映射到 4A 的逐年
`Make + Model` 原子，用于取代原来依赖
`Year + 主车型 + 结构 + 版本 + 分号候选字符串`
的中间维护表。

共享输入统一来自仓库 `source`；项目只在 `input` 中维护 Trim 例外和联网证据，`input` 内的共享大表副本不再由主入口读取。正式输出遵守两层门禁：

1. 候选必须存在于当年 `source/4afitment_data.csv` 的 `Year + Make + Model`。
2. 除“继承现有精确键”外，必须在 `input/online_evidence.csv` 提供联网证据，
   且证据的年份、版本、结构必须与 `DIMENSION-ID` 源记录一致。

## 输出

`output/TrimList.csv`

```csv
DIMENSION-ID,Year,Make,Model
MAKE=Acura|MODEL=ADX|VERSION=|STRUCTURE=SUV|YEAR=2025-2026,2025,Acura,ADX
MAKE=Acura|MODEL=ADX|VERSION=|STRUCTURE=SUV|YEAR=2025-2026,2026,Acura,ADX
```

每行只有一个候选，不使用分号合并。主键为：

```text
DIMENSION-ID + Year + Make + Model
```

运行时还会生成：

- `output/TrimList_audit.csv`：每条映射的来源、置信度及尺寸库身份字段。
- `output/TrimList_unmapped.csv`：没有可验证 4A 候选的 DIMENSION-ID 年份。
- `output/TrimList_online_review.csv`：非精确键候选的联网审核队列和建议搜索词。
- `output/TrimList_online_review_groups.csv`：按源车型/版本/结构/候选汇总的批量检索清单。
- `output/TrimList_multi_dimension.csv`：同一车型的多 DIMENSION-ID 正常展开关系。
- `output/validation_report.json`：输入、输出数量和强校验结果。
- `output/FitmentCoverage.csv`：每个唯一 4A `Year + Make + Model` 的尝试状态。
- `output/FitmentCoverageCandidates.csv`：尚无正式映射的 DIMENSION-ID 语义候选。
- `output/FitmentCoverageSummary.json`：4A 全覆盖计数及“未尝试为零”校验。

默认还会将 `TrimList.csv` 按 `DIMENSION-ID` 关联
`source/尺码分析.csv` 的“自动尺码”，生成：

- `output/DimensionSizeMap.csv`：以 `DIMENSION-ID + Size` 为唯一键的尺码映射。
- `output/AdapterSizeList.csv`：保留 DIMENSION-ID 的完整适配器尺码原子表。
- `output/SizeAnalysis.csv`：每个 `Year + Make + Model` 的尺码展开判定。
- `output/MultipleSizeReport.csv`：多 Size 正常展开汇总，不再将多 Size 视为冲突。
- `output/MultipleSizeDetail.csv`：展开到每个 `DIMENSION-ID + Size` 的明细。
- `output/NoPublishableSizeReport.csv`：只有“无可用尺码/数据不全”的车型键。
- `output/SizeAnalysisSummary.md` 和 `.json`：可读总结与机器可读指标。

## 运行

在当前目录执行：

```powershell
python run.py
```

如只需重新分析已生成的 TrimList：

```powershell
python analyze_sizes.py
```

如只生成 TrimList：

```powershell
python run.py --skip-size-analysis
```

默认读取：

- `../source/车型尺寸库.csv`
- `../source/4afitment_data.csv`
- `../source/子车系维护表.csv`
- `../source/尺码分析.csv`
- `input/trim_overrides.csv`（项目专属）
- `input/online_evidence.csv`（项目专属）

也可指定路径：

```powershell
python run.py `
  --dimensions ..\source\车型尺寸库.csv `
  --fitment ..\source\4afitment_data.csv `
  --maintenance ..\source\子车系维护表.csv `
  --size-source ..\source\尺码分析.csv `
  --online-evidence .\input\online_evidence.csv `
  --output-dir .\output
```

如果需要将未匹配或待联网审核候选视为构建失败：

```powershell
python run.py --fail-on-unmapped --fail-on-unreviewed
```

## 例外维护

`input/trim_overrides.csv` 只维护例外，不复制全量映射。

```csv
DIMENSION-ID,Year,Action,Make,Model,Note
...,2025,ADD,Acura,ADX,手工确认
...,2025,REMOVE,Acura,ADX,排除错误候选
...,2025,CLEAR,,,当年不发布
```

支持的 `Action` 为 `ADD` / `REMOVE` / `CLEAR`。`ADD` 仍必须通过当年 4A
校验；如果新增候选不属于现有精确键，也必须提供联网证据。

## 联网证据

`input/online_evidence.csv` 每行审核一个原子候选：

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
python research_nhtsa.py --apply-safe-evidence
python run.py
```

该命令仅自动批准：1996 年以后、源/候选 Make+Model 同名、版本为空，且
NHTSA 在同年对应车辆类型中返回该 Model 的记录。详细查询结果写入
`output/NHTSAResearchReport.csv`。无法证明具体版本或 Sedan/Coupe/Convertible
等细分结构的记录仍保留在联网审核队列。

对全量 4A 新发现的候选可继续运行：

```powershell
python research_nhtsa.py `
  --review .\output\FitmentCoverageCandidates.csv `
  --report .\output\NHTSAFitmentCoverageResearch.csv `
  --apply-safe-evidence
python run.py
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
python -m unittest discover -s tests -v
```
