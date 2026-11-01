# 发布报告

- 节点：`structure-review`（`nodes/02.分类结构审核`）
- 版本：`20261101_05`
- 发布时间：`2026-11-01T12:34:58+08:00`
- 发布原因：交付物变化：车型结构.csv、车型结构_US.csv；上游输入变化；pending/发布说明变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261101_04`：运行批次实际读取，3 个文件。

## 身份承接

- `车型结构.csv` ← `dimension-library` `尺寸库.csv`（equal）：通过。
- `车型结构_US.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `车型结构_EU.csv` ← `dimension-library` `尺寸库_EU.csv`（equal）：通过。
- `车型结构_RU.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。

## 交付物与变更

### `车型结构.csv`

- 内容已变化：47361 行 → 47449 行；存于 `nodes/02.分类结构审核/artifacts/2026-11-01_04_category-standard/output/车型结构-20261101_04.csv`。
- 行级差异：新增 88，删除 0，修改 1。
- 变更字段计数：`H-IN` 1，`备注` 1。
- 新增示例（最多 10 条）：`Acura RL Sedan 2005 US`；`Acura RL Sedan 2006 US`；`Acura RL Sedan 2007 US`；`Acura RL Sedan 2008 US`；`Acura RL Sedan 2009 US`；`Acura RL Sedan 2010 US`；`Acura RL Sedan 2011 US`；`Acura RL Sedan 2012 US`；`Audi 90 Sedan 1990 US`；`Audi 90 Sedan 1993 US`。
- 修改示例（最多 20 条）：
  - `Pontiac Solstice Convertible 2009 US`：`H-IN`、`备注`

### `车型结构_US.csv`

- 内容已变化：4383 行 → 4471 行；存于 `nodes/02.分类结构审核/artifacts/2026-11-01_04_category-standard/output/车型结构_US-20261101_04.csv`。
- 行级差异：新增 88，删除 0，修改 1。
- 变更字段计数：`H-IN` 1，`备注` 1。
- 新增示例（最多 10 条）：`Acura RL Sedan 2005 US`；`Acura RL Sedan 2006 US`；`Acura RL Sedan 2007 US`；`Acura RL Sedan 2008 US`；`Acura RL Sedan 2009 US`；`Acura RL Sedan 2010 US`；`Acura RL Sedan 2011 US`；`Acura RL Sedan 2012 US`；`Audi 90 Sedan 1990 US`；`Audi 90 Sedan 1993 US`。
- 修改示例（最多 20 条）：
  - `Pontiac Solstice Convertible 2009 US`：`H-IN`、`备注`

### `车型结构_EU.csv`

- 内容未变化；引用 `nodes/02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_EU-20261009_04.csv`，未复制。

### `车型结构_RU.csv`

- 内容未变化；引用 `nodes/02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_RU-20261009_04.csv`，未复制。
