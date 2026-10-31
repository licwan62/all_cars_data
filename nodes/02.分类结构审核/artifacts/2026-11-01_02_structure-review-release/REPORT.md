# 发布报告

- 节点：`structure-review`（`nodes/02.分类结构审核`）
- 版本：`20261101_02`
- 发布时间：`2026-11-01T02:46:34+08:00`
- 发布原因：上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261101_02`：运行批次实际读取，3 个文件。

## 身份承接

- `车型结构.csv` ← `dimension-library` `尺寸库.csv`（equal）：通过。
- `车型结构_US.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `车型结构_EU.csv` ← `dimension-library` `尺寸库_EU.csv`（equal）：通过。
- `车型结构_RU.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。

## 交付物与变更

### `车型结构.csv`

- 内容未变化；引用 `nodes/02.分类结构审核/artifacts/2026-10-19_02_structure-review-release/output/车型结构-20261019_02.csv`，未复制。

### `车型结构_US.csv`

- 内容未变化；引用 `nodes/02.分类结构审核/artifacts/2026-10-19_02_structure-review-release/output/车型结构_US-20261019_02.csv`，未复制。

### `车型结构_EU.csv`

- 内容未变化；引用 `nodes/02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_EU-20261009_04.csv`，未复制。

### `车型结构_RU.csv`

- 内容未变化；引用 `nodes/02.分类结构审核/artifacts/2026-10-09_04_structure-review-release/output/车型结构_RU-20261009_04.csv`，未复制。
