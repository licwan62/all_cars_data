# 发布报告

- 节点：`structure-review`（`nodes/02.分类结构审核`）
- 版本：`20261102_02`
- 发布时间：`2026-11-02T09:05:45+08:00`
- 发布原因：交付物变化：车型结构.csv、车型结构_US.csv；上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261102_02`：运行批次实际读取，3 个文件。

## 身份承接

- `车型结构.csv` ← `dimension-library` `尺寸库.csv`（equal）：通过。
- `车型结构_US.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `车型结构_EU.csv` ← `dimension-library` `尺寸库_EU.csv`（equal）：通过。
- `车型结构_RU.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。

## 交付物与变更

### `车型结构.csv`

- 内容已变化：47453 行 → 47718 行；存于 `nodes/02.分类结构审核/artifacts/2026-11-02_01_category-standard/output/车型结构-20261102_01.csv`。
- 行级差异：新增 265，删除 0，修改 0。
- 新增示例（最多 10 条）：`Acura RDX SUV 2019 US`；`Audi A3 Hatchback 2027 US`；`Audi A5 Sedan 2027 US`；`Audi A6 e-tron Sedan 2027 US`；`Audi A8 Sedan 2027 US`；`Audi Q3 SUV 2027 US`；`Audi Q6 e-tron SUV 2025 US`；`Audi Q6 e-tron SUV 2027 US`；`Audi Q8 SUV 2027 US`；`Audi RS Q8 SUV 2027 US`。

### `车型结构_US.csv`

- 内容已变化：4475 行 → 4740 行；存于 `nodes/02.分类结构审核/artifacts/2026-11-02_01_category-standard/output/车型结构_US-20261102_01.csv`。
- 行级差异：新增 265，删除 0，修改 0。
- 新增示例（最多 10 条）：`Acura RDX SUV 2019 US`；`Audi A3 Hatchback 2027 US`；`Audi A5 Sedan 2027 US`；`Audi A6 e-tron Sedan 2027 US`；`Audi A8 Sedan 2027 US`；`Audi Q3 SUV 2027 US`；`Audi Q6 e-tron SUV 2025 US`；`Audi Q6 e-tron SUV 2027 US`；`Audi Q8 SUV 2027 US`；`Audi RS Q8 SUV 2027 US`。

### `车型结构_EU.csv`

- 内容未变化；引用 `nodes/02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_EU-20261009_04.csv`，未复制。

### `车型结构_RU.csv`

- 内容未变化；引用 `nodes/02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_RU-20261009_04.csv`，未复制。
