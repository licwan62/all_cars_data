# 发布报告

- 节点：`full-generation`（`A1.全量生成`）
- 版本：`20260923_08`
- 发布时间：`2026-09-23T19:17:46+08:00`
- 工作描述：full-generation 输出刷新。

## 交付物与变更

### `全量表_汇总.csv`

- 内容已变化：47926 行 → 47695 行。
- 行级差异：新增 18816，删除 19047，修改 10367。
- 变更字段计数：`OZON尺码` 166，`Trims` 19，`候选` 668，`分类` 4099，`前宽-MM` 1486，`原因` 418，`参考侧高` 1486，`发货尺码` 348，`后宽-MM` 1486，`插片指数` 1486，`相差数值` 565，`等效长` 1486，`自动尺码` 9636，`自动长度余量` 7425，`车形` 1505，`销量合计` 145。
- 新增示例（最多 10 条）：`212 T01 SUV 2024-2026 RU`；`AC Cobra iv 291F L4115 W1735 H1245 Convertible 1990-1997 EU`；`AC Cobra iv 291F L4155 W1745 H1230 Convertible 1990-1997 EU`；`AM General HMMWV (Humvee) SUV 1984-2006 RU`；`AMC Eagle 1980 Sedan 1979-1985 EU`；`AMC Eagle 1981 Sedan 1979-1985 EU`；`AMC Eagle 1982 Sedan 1979-1985 EU`；`AMC Eagle 1983 Sedan 1979-1985 EU`；`AMC Eagle 1984 Sedan 1979-1985 EU`；`AMC Eagle Wagon 1979-1987 RU`。
- 删除示例（最多 10 条）：`212 T01 SUV 5dr 2024-2026 RU`；`AC Cobra iv 291F Cobra IV Convertible 1990-1997 EU`；`AC Cobra iv 291F Cobra IV Lightweight Convertible 1990-1997 EU`；`AM General HMMWV (Humvee) SUV 5dr 1984-2006 RU`；`AMC Eagle Eagle I 1980 Sedan 1979-1985 EU`；`AMC Eagle Eagle I 1981 Sedan 1979-1985 EU`；`AMC Eagle Eagle I 1982 Sedan 1979-1985 EU`；`AMC Eagle Eagle I 1983 Sedan 1979-1985 EU`；`AMC Eagle Eagle I 1984 Sedan 1979-1985 EU`；`AMC Eagle Wagon 5dr 1979-1987 RU`。
- 修改示例（最多 20 条）：
  - `212 Explorer 01 Pickup 2026-2026 Double RU`：`自动尺码`
  - `212 T10 SUV 2026-2026 RU`：`自动尺码`
  - `AC 428 Convertible 1965-1974 EU`：`自动尺码`、`自动长度余量`
  - `AC Ace Convertible 1995-1998 EU`：`自动尺码`、`自动长度余量`
  - `AC Ace Convertible 1998-2026 EU`：`自动尺码`、`自动长度余量`
  - `AC Cobra iv 291N Convertible 1997-2026 EU`：`自动尺码`、`自动长度余量`
  - `AMC Eagle Hatchback 1979-1987 RU`：`自动尺码`
  - `AMC Gremlin Hatchback 1970-1978 RU`：`自动尺码`
  - `AMC Hornet Sedan 1969-1970 EU`：`自动尺码`、`自动长度余量`
  - `AMC Matador Coupe 1974-1978 RU`：`自动尺码`
  - `AMC Rambler Ambassador Sedan 1965-1972 RU`：`自动尺码`
  - `Acura CL Coupe 1997-1999 US`：`自动尺码`、`自动长度余量`
  - `Acura ILX Sedan 2013-2015 US`：`自动尺码`、`自动长度余量`
  - `Acura Integra Coupe 1994 US`：`自动尺码`、`自动长度余量`
  - `Acura Integra Coupe 1995-2001 US`：`自动尺码`、`自动长度余量`
  - `Acura Integra Hatchback 1989-1993 RU`：`自动尺码`
  - `Acura Integra Sedan 1990 US`：`自动尺码`、`自动长度余量`
  - `Acura Integra Sedan 1991-1993 US`：`自动尺码`、`自动长度余量`
  - `Acura Integra Sedan 1994 US`：`自动尺码`、`自动长度余量`
  - `Acura Integra Sedan 1995-2001 US`：`自动尺码`、`自动长度余量`

### `TRIM适配器.csv`

- 内容已变化：23231 行 → 23324 行。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺寸TRIM映射.csv`

- 内容已变化：4371 行 → 4371 行。
- 行级差异：新增 7，删除 7，修改 19。
- 变更字段计数：`Trims` 19。
- 新增示例（最多 10 条）：`Subaru Outback Sport Wagon 2001`；`Subaru Outback Sport Wagon 2002-2003`；`Subaru Outback Sport Wagon 2004`；`Subaru Outback Sport Wagon 2005`；`Subaru Outback Sport Wagon 2006`；`Subaru Outback Sport Wagon 2007`；`Subaru Outback Sport Wagon 2008-2011`。
- 删除示例（最多 10 条）：`Subaru Outback Sport Outback Sport Hatchback 2008-2011`；`Subaru Outback Sport Outback Sport Wagon 2001`；`Subaru Outback Sport Outback Sport Wagon 2002-2003`；`Subaru Outback Sport Outback Sport Wagon 2004`；`Subaru Outback Sport Outback Sport Wagon 2005`；`Subaru Outback Sport Outback Sport Wagon 2006`；`Subaru Outback Sport Outback Sport Wagon 2007`。
- 修改示例（最多 20 条）：
  - `Jeep Gladiator 4dr JT Mojave Pickup 2025-2026 Crew 5`：`Trims`
  - `Jeep Gladiator 4dr JT Pickup 2020-2024 Crew 5`：`Trims`
  - `Jeep Gladiator 4dr JT Pickup 2025-2026 Crew 5`：`Trims`
  - `Jeep Gladiator 4dr JT Rubicon Pickup 2020 Crew 5`：`Trims`
  - `Jeep Gladiator 4dr JT Rubicon Pickup 2025-2026 Crew 5`：`Trims`
  - `Jeep Gladiator 4dr JT Rubicon/Mojave Pickup 2021-2024 Crew 5`：`Trims`
  - `Jeep Wrangler 2dr JK SUV 2007-2018`：`Trims`
  - `Jeep Wrangler 2dr JL SUV 2018-2024`：`Trims`
  - `Jeep Wrangler 2dr JL SUV 2025-2026`：`Trims`
  - `Jeep Wrangler 2dr JL Xtreme SUV 2026`：`Trims`
  - `Jeep Wrangler 2dr LJ Unlimited SUV 2004-2006`：`Trims`
  - `Jeep Wrangler 2dr TJ Rubicon SUV 2004-2006`：`Trims`
  - `Jeep Wrangler 2dr TJ SUV 1997-2006`：`Trims`
  - `Jeep Wrangler 2dr YJ SUV 1987-1995`：`Trims`
  - `Jeep Wrangler 4dr JKU SUV 2007-2018`：`Trims`
  - `Jeep Wrangler 4dr JLU Rubicon 392 SUV 2021-2026`：`Trims`
  - `Jeep Wrangler 4dr JLU SUV 2018-2024`：`Trims`
  - `Jeep Wrangler 4dr JLU SUV 2025-2026`：`Trims`
  - `Jeep Wrangler 4dr JLU Xtreme SUV 2024-2026`：`Trims`
