# 发布报告

- 节点：`code-mapping`（`nodes/02.代码映射`）
- 版本：`20261102_14`
- 发布时间：`2026-11-02T19:47:25+08:00`
- 发布原因：交付物变化：尺寸编码映射.csv、车型编码映射.csv；上游输入变化；规则变化（修改 data/mapping/us/make_mapping.csv, data/mapping/us/model_mapping.csv；新增 data/mapping/us/backups/20261102_194714_649865_make_mapping.csv, data/mapping/us/backups/20261102_194714_649865_model_mapping.csv）。

## 规则（data/）

- 相对上一版本：修改 data/mapping/us/make_mapping.csv, data/mapping/us/model_mapping.csv；新增 data/mapping/us/backups/20261102_194714_649865_make_mapping.csv, data/mapping/us/backups/20261102_194714_649865_model_mapping.csv。

## 上游输入依据

- `dimension-library` `20261102_17`：运行批次实际读取，1 个文件。

## 身份承接

- `尺寸编码映射.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。

## 交付物与变更

### `车型编码映射.csv`

- 内容已变化：764 行 → 970 行；存于 `nodes/02.代码映射/artifacts/2026-11-02_13_code-mapping/output/车型编码映射-20261102_13.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺寸编码映射.csv`

- 内容已变化：4837 行 → 6335 行；存于 `nodes/02.代码映射/artifacts/2026-11-02_13_code-mapping/output/尺寸编码映射-20261102_13.csv`。
- 行级差异：新增 1498，删除 0，修改 0。
- 新增示例（最多 10 条）：`AMC Alliance Sedan 1983 US`；`AMC Alliance Sedan 1984 US`；`AMC Alliance Sedan 1985 US`；`AMC Alliance Sedan 1986 US`；`AMC Alliance Sedan 1987 US`；`AMC Ambassador Sedan 1963 US`；`AMC Ambassador Sedan 1964 US`；`AMC Ambassador Sedan 1967 US`；`AMC Ambassador Sedan 1968 US`；`AMC Eagle Hatchback 1980 US`。
