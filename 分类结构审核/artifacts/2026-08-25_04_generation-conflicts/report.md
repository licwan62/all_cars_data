# 代际 conflict 修复

本批次以 `2026-08-25_03_identity-gap-distinction/correct.csv` 为输入，不写入 `source`。

## 已应用结果

- 输入：4,390 行。
- 修正代际字段：50 条。
- 修正后新增安全连续合并：1 组。
- 输出：4,389 行。
- 非标准组合代际标签：0。
- 未解决代际 conflict：0。
- 未解决同 key 年份重叠 conflict：0。
- `DIMENSION-ID` 唯一且与身份字段一致。

## 主要修复

- Audi A3/S3/RS3、A4/S4/RS4、A6/S6/RS6：原 `A4-gen3/S4-gen3/RS4-gen1` 一类组合标签统一按主车型平台记录为单一 `genN`。MODEL 仍保留组合车型含义。
- Chevrolet Bel Air：1958 保持单年 gen3，1959-1960 所有结构统一为 gen4。
- Ford Expedition：2001-2002 统一为第一代；第二代从 2003 开始。
- Mercury Tracer：1990-1996 Sedan/Wagon 统一为 gen2，并合并连续 Sedan 年段。
- Pontiac Bonneville：1957 前身记为 gen0；1958、1959-1960、1961-1964 分别统一为 gen1、gen2、gen3，1965 起原有顺序保持不变。
- Toyota Corolla：2014-2019 Sedan 改为 gen10；2019+ Hatchback、2020+ Sedan 及 GR Corolla 改为 gen11。

## 合法代际重叠

`generation_findings.csv` 仍列出 17 个模型级跨度重叠，但全部标为 `VALID_PARALLEL_OR_LINEAGE`，主要包括：

- 新一代 Sedan 上市、上一代 Coupe/Convertible 继续销售；
- Wagon、Sport Trac、Gran Coupe 等衍生分支换代不同步；
- C/K 与 R/V、Land Cruiser 40/60 Series 等并行产品线；
- Blazer、Yaris 等名称复用或不同产品线共用 MODEL。

这些记录不是待修复冲突，不会被强行截断年份。

## 复现

- 决策：`../../review_rules/generation_conflict_decisions_2026-08-25.json`
- 处理程序：`../../code/review_year_generation.py`
