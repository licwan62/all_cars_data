# 发布报告

- 节点：`code-mapping`（`nodes/02.代码映射`）
- 版本：`20261101_02`
- 发布时间：`2026-11-01T02:46:46+08:00`
- 发布原因：上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261101_02`：运行批次实际读取，1 个文件。

## 身份承接

- `尺寸编码映射.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。

## 交付物与变更

### `车型编码映射.csv`

- 内容未变化；引用 `nodes/02.代码映射/artifacts/2026-10-09_04_code-mapping-release/output/车型编码映射-20261009_04.csv`，未复制。

### `尺寸编码映射.csv`

- 内容未变化；引用 `nodes/02.代码映射/artifacts/2026-10-19_02_code-mapping-release/output/尺寸编码映射-20261019_02.csv`，未复制。
