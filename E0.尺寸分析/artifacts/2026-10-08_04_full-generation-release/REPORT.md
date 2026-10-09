# 发布报告

- 节点：`full-generation`（`A1.全量生成`）
- 版本：`20261008_04`
- 发布时间：`2026-10-08T22:21:40+08:00`
- 工作描述：full-generation 输出刷新。

## 规则（data/）

- 与上一版本相同。

## 交付物与变更

### `尺码宽高统计.csv`

- 内容已变化：106 行 → 106 行。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺码宽高极值车型.csv`

- 内容已变化：464 行 → 464 行。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺码尺寸异常.csv`

- 内容已变化：3177 行 → 3177 行。
- 行级差异：新增 1，删除 1，修改 5。
- 变更字段计数：`宽Z分数` 5，`高IQR上界-MM` 5，`高IQR下界-MM` 5，`高Z分数` 5。
- 新增示例（最多 10 条）：`Mercedes-Benz GLE-Class Coupe 2021-2027 US`。
- 删除示例（最多 10 条）：`Mercedes-Benz GLE-Class Coupe 2021-2026 US`。
- 修改示例（最多 20 条）：
  - `Dodge Durango SUV 1998 US`：`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Dodge Durango SUV 1999-2001 US`：`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Dodge Durango SUV 2002-2003 US`：`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Ford Bronco 4dr Raptor SUV 2022-2026 US`：`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Ineos Automotive Grenadier SUV 2024-2026 US`：`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
