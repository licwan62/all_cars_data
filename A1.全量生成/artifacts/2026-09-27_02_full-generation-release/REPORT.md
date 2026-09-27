# 发布报告

- 节点：`full-generation`（`A1.全量生成`）
- 版本：`20260927_02`
- 发布时间：`2026-09-27T02:02:25+08:00`
- 工作描述：full-generation 输出刷新。

## 规则（data/）

- 相对上一版本：删除 data/4a_fitment_0722.tsv, data/AdapterSizeList.csv, data/DimensionSizeMap.csv, data/FitmentCoverage.csv, data/FitmentCoverageCandidates.csv, data/FitmentCoverageSummary.json, data/MultipleSizeDetail.csv, data/MultipleSizeReport.csv, data/NHTSAFitmentCoverageResearch.csv, data/NHTSAResearchReport.csv, data/NoPublishableSizeReport.csv, data/SizeAnalysis.csv, data/SizeAnalysisSummary.json, data/SizeAnalysisSummary.md, data/TrimList.csv, data/TrimList_ID迁移.csv, data/TrimList_audit.csv, data/TrimList_conflicts.csv, data/TrimList_multi_dimension.csv, data/TrimList_online_review.csv, data/TrimList_online_review_groups.csv, data/TrimList_unmapped.csv, data/online_evidence.csv, data/trim_overrides.csv, data/trim_values.csv, data/validation_report.json。

## 交付物与变更

### `尺码宽高统计.csv`

- 内容未变化；仅产生新的发布版本。

### `尺码宽高极值车型.csv`

- 内容已变化：481 行 → 481 行。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺码尺寸异常.csv`

- 内容已变化：3115 行 → 3115 行。
- 行级差异：新增 0，删除 0，修改 3115。
- 变更字段计数：`DIMENSION-CODE` 3115，`TRIM` 335。
- 修改示例（最多 20 条）：
  - `212 T01 SUV 2024-2026 RU`：`DIMENSION-CODE`
  - `212 T10 SUV 2026-2026 RU`：`DIMENSION-CODE`
  - `AM General HMMWV (Humvee) SUV 1984-2006 RU`：`DIMENSION-CODE`
  - `ARO 10 10.1 Convertible 1984-1999 EU`：`DIMENSION-CODE`
  - `ARO 240-244 243 3dr facelift SUV 1978-1998 EU`：`DIMENSION-CODE`
  - `ARO 240-244 243 3dr facelift SUV 1985-1998 EU`：`DIMENSION-CODE`
  - `ARO 240-244 243 3dr prefl SUV 1978-1998 EU`：`DIMENSION-CODE`
  - `ARO 240-244 243 3dr prefl SUV 1985-1998 EU`：`DIMENSION-CODE`
  - `ARO 240-244 243 SUV 1989-1998 EU`：`DIMENSION-CODE`
  - `ARO 240-244 244 5dr facelift SUV 1978-1998 EU`：`DIMENSION-CODE`
  - `ARO 240-244 244 5dr facelift SUV 1985-1998 EU`：`DIMENSION-CODE`
  - `ARO 240-244 244 5dr prefl SUV 1978-1998 EU`：`DIMENSION-CODE`
  - `ARO 240-244 244 5dr prefl SUV 1985-1998 EU`：`DIMENSION-CODE`
  - `ARO 240-244 244 SUV 1989-1998 EU`：`DIMENSION-CODE`
  - `ARO Spartana pick up Convertible 1997-2003 EU`：`DIMENSION-CODE`
  - `Acura ILX Sedan 2013-2015 US`：`DIMENSION-CODE`、`TRIM`
  - `Acura NSX Coupe 1991-1994 US`：`DIMENSION-CODE`、`TRIM`
  - `Acura NSX Coupe 1995 US`：`DIMENSION-CODE`、`TRIM`
  - `Acura NSX Coupe 1996-2005 US`：`DIMENSION-CODE`、`TRIM`
  - `Adler Diplomat Pullman Sedan 1934-1940 RU`：`DIMENSION-CODE`
