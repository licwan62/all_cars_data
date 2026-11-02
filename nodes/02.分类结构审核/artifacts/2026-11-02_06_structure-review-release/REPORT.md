# 发布报告

- 节点：`structure-review`（`nodes/02.分类结构审核`）
- 版本：`20261102_06`
- 发布时间：`2026-11-02T12:43:35+08:00`
- 发布原因：交付物变化：车型结构.csv、车型结构_US.csv；上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261102_10`：运行批次实际读取，3 个文件。

## 身份承接

- `车型结构.csv` ← `dimension-library` `尺寸库.csv`（equal）：通过。
- `车型结构_US.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `车型结构_EU.csv` ← `dimension-library` `尺寸库_EU.csv`（equal）：通过。
- `车型结构_RU.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。

## 交付物与变更

### `车型结构.csv`

- 内容已变化：47788 行 → 47815 行；存于 `nodes/02.分类结构审核/artifacts/2026-11-02_05_category-standard/output/车型结构-20261102_05.csv`。
- 行级差异：新增 27，删除 0，修改 0。
- 新增示例（最多 10 条）：`BYD e6 SUV 2012 US`；`BYD e6 SUV 2013 US`；`BYD e6 SUV 2014 US`；`BYD e6 SUV 2016 US`；`BYD e6 SUV 2017 US`；`BYD e6 SUV 2018 US`；`BYD e6 SUV 2020 US`；`Daewoo Lanos Sedan 2000 US`；`Daewoo Lanos Sedan 2001 US`；`Daewoo Lanos Sedan 2002 US`。

### `车型结构_US.csv`

- 内容已变化：4810 行 → 4837 行；存于 `nodes/02.分类结构审核/artifacts/2026-11-02_05_category-standard/output/车型结构_US-20261102_05.csv`。
- 行级差异：新增 27，删除 0，修改 0。
- 新增示例（最多 10 条）：`BYD e6 SUV 2012 US`；`BYD e6 SUV 2013 US`；`BYD e6 SUV 2014 US`；`BYD e6 SUV 2016 US`；`BYD e6 SUV 2017 US`；`BYD e6 SUV 2018 US`；`BYD e6 SUV 2020 US`；`Daewoo Lanos Sedan 2000 US`；`Daewoo Lanos Sedan 2001 US`；`Daewoo Lanos Sedan 2002 US`。

### `车型结构_EU.csv`

- 内容未变化；引用 `nodes/02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_EU-20261009_04.csv`，未复制。

### `车型结构_RU.csv`

- 内容未变化；引用 `nodes/02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_RU-20261009_04.csv`，未复制。
