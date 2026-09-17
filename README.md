# 车型数据研究工作区

当前已发布的 `public/全量数据.csv` 各计算列的来源、公式、取整与空值处理，以及尺码匹配规则，见 [全量表计算列说明](尺码计算/README.md#当前全量表计算列)。

本仓库采用一条明确的数据流：`source` 是唯一人工维护真源；研究项目只读 `source`，只向各自的 `output/`、`artifacts/`、`work/` 或 `cache/` 写结果；通过校验后，再由人手工覆盖对应的 `source` 文件。任何项目都不得在运行时自动回写 `source`。

区域尺寸数据的统一发布链为：`尺寸库 → 尺寸分析表 → 全量表`。尺寸分析表包含完成尺寸换算与车形派生后的 21 列，不包含 `自动尺码`、`自动长度余量`、`候选`、`原因`、`相差数值`；全量表在此基础上增加这 5 个尺码匹配结果列。

## 项目与数据流

| 项目 | 默认读取 | 项目候选输出 | 可人工发布到 |
|---|---|---|---|
| `自动化尺寸抓取器` | 原始 Ktype TSV、已审计映射与尺寸组 TSV | 标准区域 source 候选及 `尺寸库 → 尺寸分析表 → 全量表` 候选 | 审核后人工并入对应区域批次 |
| `分类结构审核` | `source/尺寸库.csv` | `artifacts/corrected.csv` | `source/尺寸库.csv` |
| `车形分类核定` | `source/尺寸库.csv` | `artifacts/record_shape.csv` | `source/车身分类.csv` |
| `销量评估` | `source/尺寸库.csv` | `artifacts/atom_sales.csv` | `source/销量明细.csv` |
| `尺码计算` | 尺寸库、车形、销量、子车系、参考尺寸 | `output/pandas_output.csv` | `source/全量数据.csv` |
| `尺码簇分析` | `source/全量数据.csv`、尺码匹配规则 | `output/*` | 分析结果，不直接发布 |
| `SKU 聚类/pickup-cluster` | `source/全量数据.csv`、销量明细 | `output/pickup_cluster_*.csv` | `source/pk-cluster/*` |
| `适配器-Trim生成` | 尺寸库、4A、子车系、`source/全量数据.csv` | `output/*` | 当前为下游交付，不直接替换真源 |

项目自己的规则、人工例外和研究证据留在项目目录，例如 `config/`、`data/`、`review_rules/`；它们不属于跨项目共享真源。

## 标准运行顺序

1. 在 `source` 中维护或确认上游数据。
2. 运行研究项目，结果只生成到该项目目录。
3. 检查真源和所有已生成候选：

   ```powershell
   python data_workflow.py status
   python data_workflow.py check
   ```

4. 查看某个数据集的人工发布计划，例如：

   ```powershell
   python data_workflow.py publish-plan 尺寸库
   python data_workflow.py publish-plan 车身分类
   python data_workflow.py publish-plan 原子销量
   python data_workflow.py publish-plan 全量数据
   ```

5. 审阅差异、关闭占用文件的程序并备份后，人工执行工具打印的 `Copy-Item`。工具本身永远不会覆盖 `source`。覆盖后再次运行 `check`，再启动下游项目。

数据文件、主键、生产项目和候选路径统一登记在 [`source/catalog.json`](source/catalog.json)。

## 目录约定

- `source/`：唯一共享真源及其数据清单。
- `项目/config/`、`项目/data/`：项目专属规则、例外、证据。
- `项目/cache/`、`项目/work/`：可重建的中间状态。
- `项目/output/`、`项目/artifacts/`：候选和审计产物。
- `项目/artifacts/`：版本化候选、审计产物和历史批次快照，不作为下游默认输入；其中所有文件均须纳入 Git。

`车形分类核定`、`车型代表分析`、`尺码簇分析`、`尺码计算`、`分类结构审核`、`适配器-Trim生成`、`销量评估` 统一使用 `artifacts/` 保存版本化迭代留痕。每次迭代创建 `YYYY-MM-DD_NN_short-description/` 批次目录，保留当次结果、差异、报告、验证和研究证据；已归档批次不得覆盖或删除。

旧 `input/` 中的重复大表暂时保留用于历史回归，但主入口已不再默认读取。确认新流程稳定后，可由人工归档；不要在项目运行过程中双向同步这些副本。

## DIMENSION-ID 格式

尺寸库中的基础 `DIMENSION-ID` 只保留非空业务值，依次为 `MAKE MODEL 版本 结构 YEAR`；皮卡继续在末尾追加 `CAB BED`。各值以单个空格连接，不再包含字段名或竖线。`data/us/US全量.csv`、`data/eu/EU全量.csv`、`data/ru/RU全量.csv` 的发布 ID 再在基础 ID 末尾追加国家代号 `US`、`EU`、`RU`。例如：

```text
Acura ADX SUV 2025-2026
Cadillac Escalade EXT Pickup 2002-2006 Crew 5.3
Acura ADX SUV 2025-2026 US
```

原子销量的 `atom_record_id` 仍在该 ID 后追加 `|ATOM_YEAR=YYYY`，供逐年销量聚合时稳定拆分。
