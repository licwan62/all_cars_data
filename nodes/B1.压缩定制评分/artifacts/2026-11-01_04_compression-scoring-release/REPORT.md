# 发布报告

- 节点：`compression-scoring`（`nodes/B1.压缩定制评分`）
- 版本：`20261101_04`
- 发布时间：`2026-11-01T02:46:50+08:00`
- 发布原因：上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `size-calculation` `20261101_07`：运行批次实际读取，3 个文件。
- `negative-review-analysis` `20261009_04`：运行批次实际读取，3 个文件。

## 交付物与变更

### `定制需求度评分.csv`

- 内容未变化；引用 `nodes/B1.压缩定制评分/artifacts/2026-10-09_04_compression-scoring-release/output/定制需求度评分-20261009_04.csv`，未复制。
