# 依据 reference.csv 的全量车身号重核

本批次以 `D:\Licheng\Workflow\all_cars_data\车形分类核定\changes\2026-09-02_01_reference-suv-id-migration\correct.csv` 为变更对比基线，以 `doc/reference.csv` 为车形定义唯一真源，将新版车身号落实到全部 `4,354` 个 `DIMENSION-ID`。本轮未写入 `source` 目录。

## 核定规则

- 只允许输出 `reference.csv` 的 18 个车身号，旧数字编号全部废止。
- `H0/H1/H2/H3` 按低斜两厢、高方两厢、现代流线 Wagon、经典方正 Estate 重新拆分，不沿用旧 `20/21` 边界。
- Dodge Challenger 全系使用专用 `dodge-challenger`。
- Pickup 按 `DUAL > P2 > P1 > P0` 的例外优先级；SUV 按 `JP/SU2/SU0/SU1` 的真实轮廓核定。
- `STRUCTURE` 只用于定位真实分支，不能代替轮廓证据。
- 同车型同代际同外壳复用结论；源数据代际粒度不足且轮廓确有变化时细化到年份分支。

## 结果统计

- 全量结果：4,354 条，唯一 ID 4,354 个。
- 2000 年以前重点审计：2,042 条。
- 对比基线的增量记录：4,354 条；`RECLASSIFY` 4,354，`ADD` 0，`REMOVE` 0。
- 车形分布：dodge-challenger=6, H0=230, H1=32, H2=132, H3=151, JP=61, P0=230, P1=176, P2=20, DUAL=39, SD0=629, SD1=756, SD2=884, SU0=104, SU1=425, SU2=347, V0=63, V1=69。
- 历史编号残留：0。
- 机器验收：PASS。

## 文件说明

- `correct.csv`：本批次完成时的全量 `DIMENSION-ID,车形` 快照。
- `changes.csv`：相对基线的实际新增、删除和改类。
- `all_dimension_audit.csv/json`：全 ID 逐条判定与摘要。
- `reference.csv`：本批次实际使用的规则源快照。
- `validation.json`：本批次机器验收结果。

## 保留风险

- 本轮 `RECLASSIFY` 同时包含定义等价的编号迁移和 `H*` 等边界重判；逐条原因以 `all_dimension_audit.csv` 为准。
- 新证据如推翻已核代际，应追加新批次，不覆盖本快照。
