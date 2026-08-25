# 身份、重叠区间与缺年候选区分

本批次以 `2026-08-25_02_year-generation-audit/correct.csv` 为输入，继续保持 `source` 只读。

## 已应用结果

- 输入：4,400 行。
- VERSION 身份补全：54 条。
- 年份边界收窄：24 条。
- 身份或年份拆分：4 条。
- 删除旧聚合残留：6 条。
- 新形成的安全连续合并：8 组。
- 输出：4,390 行、4,390 个唯一且字段一致的 `DIMENSION-ID`。

## 身份区分

以下原本共用空 VERSION、但参考车型和备注已经明确不同车身的记录已分键：

- Chevrolet S-10 Blazer / Blazer、GMC Jimmy / Yukon、Chevrolet Tracker：`2dr` 与 `4dr`。
- Mitsubishi Montero：`2dr SWB` 与 `4dr LWB`。
- MINI Cooper、Kia Sportage：`2dr` 与 `4dr`。
- Jeep Wrangler：普通 Rubicon 与 `2dr Unlimited Rubicon`。
- Audi e-tron、Q5：常规 SUV 与 `Sportback`。
- Nissan Sentra：B11 `2dr` 与 `4dr`，并把 gen1 宽区间收窄到 1982-1986。
- Nissan Pathfinder：资料不足以稳妥断言门数，因此只按已有参考车型和三维区分为 `Wide-body` / `Narrow-body`。

## 聚合残留和边界修复

- 删除 Infiniti G、Pontiac Sunfire 中由旧 `Coupe/Convertible` 压缩记录派生、且已被原子记录完整覆盖的行。
- 删除 Mitsubishi Eclipse 已被逐段 Coupe 数据完整覆盖的人工聚合行。
- 删除 BMW 1 Series 中参考车型实际为 Coupe 的错误 Convertible 派生行。
- 对 BMW Z3、Plymouth Fury、Pontiac Bonneville/LeMans、Oldsmobile Cutlass、Suzuki SX4、350Z、Solstice、Mustang、S-Class、SL-Class、Golf GTI 等宽年份段，扣除已有独立年款，收窄或拆成互不重叠的区间。

## 重叠冲突结论

上一批的 80 个未解决同代重叠冲突已经降为 0。当前 `interval_conflicts.csv` 只剩 4 个已确认合法的跨代并行边界：Jaguar XJ、2018 Wrangler 2dr/4dr、1963 SL；状态均为 `VALID_PARALLEL`。

## 缺年候选进一步区分

`gap_candidates.csv` 的 391 个信号已按“整车型是否由其他分支覆盖该年”重新分类：

- `VALID_HIATUS`：13 个已确认的跳年或市场空档，不补年。
- `RESEARCH_MODEL_YEAR_GAP`：19 个整车型层面缺年，优先查证。
- `RESEARCH_BRANCH_GAP`：81 个车型仍有其他结构/版本覆盖，仅当前分支缺年。
- `REVIEW_BRANCH_OR_GENERATION_BOUNDARY`：145 个跨代或分支边界，车型本身并未缺年。
- `REVIEW_GENERATION_BOUNDARY`：80 个短换代空档。
- `REVIEW_NAMEPLATE_HIATUS`：53 个长时间停产或名称复用候选。

这些候选仍不会仅凭左右年份自动补齐。配置分支、车身停售和跳过美国 model year 都可能形成合法空档。

## 复现

身份决策位于 `../../review_rules/identity_decisions_2026-08-25.json`；处理逻辑位于 `../../code/review_year_generation.py`。
