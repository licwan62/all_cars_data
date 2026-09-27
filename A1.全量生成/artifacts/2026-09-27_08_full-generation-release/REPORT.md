# 发布报告

- 节点：`full-generation`（`A1.全量生成`）
- 版本：`20260927_08`
- 发布时间：`2026-09-27T14:09:40+08:00`
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

- 内容已变化：3150 行 → 3152 行。
- 行级差异：新增 2，删除 0，修改 44。
- 变更字段计数：`宽Z分数` 44，`异常原因` 1，`高Z分数` 44。
- 新增示例（最多 10 条）：`GMC Jimmy 4dr SUV 2001 US`；`Toyota RAV4 Convertible 1998-1999 US`。
- 修改示例（最多 20 条）：
  - `Chevrolet Blazer 4dr SUV 1998-2001 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet Blazer 4dr SUV 2002 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet Blazer 4dr SUV 2003-2005 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet Blazer SUV 1969-1970 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet Blazer SUV 1971 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet Blazer SUV 1972 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet K5 Blazer SUV 1969-1970 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet K5 Blazer SUV 1971-1972 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet S-10 Blazer 2dr 2WD SUV 1992-1993 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet S-10 Blazer 2dr 4WD SUV 1991-1994 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet S-10 Blazer 4dr 2WD SUV 1991-1994 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet S-10 Blazer 4dr SUV 1995-2003 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet S-10 Blazer 4dr SUV 2004 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet S-10 Blazer SUV 1983-1984 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet S-10 Blazer SUV 1985-1986 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet S-10 Blazer SUV 1987 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet S-10 Blazer SUV 1988 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet S-10 Blazer SUV 1989 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet S-10 Blazer SUV 1990 US`：`宽Z分数`、`高Z分数`
  - `Chevrolet Suburban SUV 1935-1940 US`：`宽Z分数`、`高Z分数`
