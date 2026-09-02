# TrimList v2 生成器

本项目将车型尺寸库中的 `DIMENSION-ID` 直接映射到 4A 的逐年
`Make + Model` 原子，用于取代原来依赖
`Year + 主车型 + 结构 + 版本 + 分号候选字符串`
的中间维护表。

共享输入统一来自仓库 `source`；项目在 `data` 中维护 Trim 例外、联网证据以及全部研究/校验中间产物。正式输出遵守两层门禁：

1. 候选必须存在于当年 `source/4A全数据.csv` 的 `Year + Make + Model`。
2. 除“继承现有精确键”外，必须在 `data/online_evidence.csv` 提供联网证据，
   且证据的年份、版本、结构必须与 `DIMENSION-ID` 源记录一致。

## 输出

`output` 只保留两个最终交付文件：

- `output/适配器.csv`：为 `TrimList` 的每一行回填 `Size`，包括“无可用尺码/数据不全”等状态值，不丢行。
- `output/DimensionTrimMap.csv`：每个 `DIMENSION-ID` 一行，从 `source/尺码分析.csv` 的 `TRIM` 列生成 `Trims`，多个名称以 ` | ` 分隔。

## Data 与研究产物

`data/TrimList.csv` 是适配器生成所用的 DIMENSION-ID 到逐年车型映射：

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
- `../source/4A全数据.csv`
- `../source/子车系维护表.csv`
- `../source/尺码分析.csv`
- `data/trim_overrides.csv`（项目专属）
- `data/online_evidence.csv`（项目专属）

也可指定路径：

```powershell
python run.py `
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
python run.py --fail-on-unmapped --fail-on-unreviewed
```

## 例外维护

`data/trim_overrides.csv` 只维护例外，不复制全量映射。

```csv
DIMENSION-ID,Year,Action,Make,Model,Note
...,2025,ADD,Acura,ADX,手工确认
...,2025,REMOVE,Acura,ADX,排除错误候选
...,2025,CLEAR,,,当年不发布
```

支持的 `Action` 为 `ADD` / `REMOVE` / `CLEAR`。`ADD` 仍必须通过当年 4A
校验；如果新增候选不属于现有精确键，也必须提供联网证据。

## 联网证据

`data/online_evidence.csv` 每行审核一个原子候选：

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
`data/NHTSAResearchReport.csv`。无法证明具体版本或 Sedan/Coupe/Convertible
等细分结构的记录仍保留在联网审核队列。

对全量 4A 新发现的候选可继续运行：

```powershell
python research_nhtsa.py `
  --review .\data\FitmentCoverageCandidates.csv `
  --report .\data\NHTSAFitmentCoverageResearch.csv `
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
