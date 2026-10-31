# 发布报告

- 节点：`size-analysis`（`nodes/E0.尺寸分析`）
- 版本：`20261101_02`
- 发布时间：`2026-11-01T02:37:37+08:00`
- 发布原因：交付物变化：尺码宽高极值车型.csv、尺码宽高统计.csv、尺码尺寸异常.csv；上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `size-calculation` `20261101_07`：运行批次实际读取，3 个文件。

## 交付物与变更

### `尺码宽高统计.csv`

- 内容已变化：106 行 → 105 行；存于 `nodes/E0.尺寸分析/artifacts/2026-11-01_01_dimension-statistics/output/尺码宽高统计-20261101_01.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺码宽高极值车型.csv`

- 内容已变化：464 行 → 462 行；存于 `nodes/E0.尺寸分析/artifacts/2026-11-01_01_dimension-statistics/output/尺码宽高极值车型-20261101_01.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺码尺寸异常.csv`

- 内容已变化：3177 行 → 3176 行；存于 `nodes/E0.尺寸分析/artifacts/2026-11-01_01_dimension-statistics/output/尺码尺寸异常-20261101_01.csv`。
- 行级差异：新增 2，删除 3，修改 559。
- 变更字段计数：`宽IQR上界-MM` 23，`宽IQR下界-MM` 23，`宽Z分数` 69，`异常原因` 4，`自动尺码` 502，`高IQR上界-MM` 23，`高IQR下界-MM` 23，`高Z分数` 70。
- 新增示例（最多 10 条）：`Cadillac V12 Convertible 1931-1935 RU`；`Deco Rides Zephyr Coupe 1999-2026 RU`。
- 删除示例（最多 10 条）：`Buick Roadmaster Sedan 1938-1939 RU`；`Buick Roadmaster Sedan 1942-1948 RU`；`ГАЗ 12 ЗИМ Sedan 1948-1960 RU`。
- 修改示例（最多 20 条）：
  - `212 T10 SUV 2026-2026 RU`：`自动尺码`
  - `Adler Diplomat Pullman Sedan 1934-1940 RU`：`自动尺码`
  - `Adler Diplomat Sedan 1934-1940 RU`：`自动尺码`
  - `Alpine A290 Hatchback 2024-2026 RU`：`自动尺码`
  - `Arcfox Alpha S Liftback 2021-2025 RU`：`自动尺码`
  - `Arcfox Alpha S6 Liftback 2025-2026 RU`：`自动尺码`
  - `Asia Topic MPV 1987-1999 RU`：`自动尺码`
  - `Aston Martin Lagonda Wagon 1976-1997 RU`：`自动尺码`
  - `Aston Martin Virage Sedan 1988-2000 RU`：`自动尺码`
  - `Audi 920 Sedan 1938-1940 RU`：`自动尺码`
  - `Audi A6 allroad Wagon 2026-2026 RU`：`自动尺码`
  - `Avatr 12 Fastback 2023-2026 RU`：`自动尺码`
  - `BAIC BJ2020 SUV 1989-2005 RU`：`自动尺码`
  - `BAIC BJ2030 SUV 1993-2012 RU`：`自动尺码`
  - `BAIC BJ212 SUV 2020-2024 RU`：`自动尺码`
  - `BAIC BJ40 L171.3 W75.8 H73.4 SUV 2013-2019 RU`：`自动尺码`
  - `BAIC BJ40 L171.3 W75.8 H73.4 SUV 2019-2026 RU`：`自动尺码`
  - `BAW 212 SUV 2020-2023 RU`：`自动尺码`
  - `BMW 3 серии Wagon 2008-2013 RU`：`自动尺码`
  - `BMW M5 Sedan 2011-2013 RU`：`自动尺码`
