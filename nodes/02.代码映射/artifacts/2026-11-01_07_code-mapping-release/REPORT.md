# 发布报告

- 节点：`code-mapping`（`nodes/02.代码映射`）
- 版本：`20261101_07`
- 发布时间：`2026-11-01T12:47:55+08:00`
- 发布原因：交付物变化：尺寸编码映射.csv；上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261101_16`：运行批次实际读取，1 个文件。

## 身份承接

- `尺寸编码映射.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。

## 交付物与变更

### `车型编码映射.csv`

- 内容未变化；引用 `nodes/02.代码映射/artifacts/2026-11-01_03_code-mapping/output/车型编码映射-20261101_03.csv`，未复制。

### `尺寸编码映射.csv`

- 内容已变化：4471 行 → 4474 行；存于 `nodes/02.代码映射/artifacts/2026-11-01_06_code-mapping/output/尺寸编码映射-20261101_06.csv`。
- 行级差异：新增 3，删除 0，修改 0。
- 新增示例（最多 10 条）：`Mazda 2 Hatchback 2016 US`；`Mazda 2 Hatchback 2017 US`；`Mazda 2 Hatchback 2018 US`。
