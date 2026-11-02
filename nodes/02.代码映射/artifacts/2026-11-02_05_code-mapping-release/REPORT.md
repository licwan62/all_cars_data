# 发布报告

- 节点：`code-mapping`（`nodes/02.代码映射`）
- 版本：`20261102_05`
- 发布时间：`2026-11-02T12:38:43+08:00`
- 发布原因：交付物变化：尺寸编码映射.csv、车型编码映射.csv；上游输入变化；规则变化（修改 data/mapping/us/make_mapping.csv, data/mapping/us/model_mapping.csv；新增 data/mapping/us/backups/20261102_123828_259924_make_mapping.csv, data/mapping/us/backups/20261102_123828_259924_model_mapping.csv）。

## 规则（data/）

- 相对上一版本：修改 data/mapping/us/make_mapping.csv, data/mapping/us/model_mapping.csv；新增 data/mapping/us/backups/20261102_123828_259924_make_mapping.csv, data/mapping/us/backups/20261102_123828_259924_model_mapping.csv。

## 上游输入依据

- `dimension-library` `20261102_04`：运行批次实际读取，1 个文件。

## 身份承接

- `尺寸编码映射.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。

## 交付物与变更

### `车型编码映射.csv`

- 内容已变化：750 行 → 757 行；存于 `nodes/02.代码映射/artifacts/2026-11-02_03_code-mapping/output/车型编码映射-20261102_03.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺寸编码映射.csv`

- 内容已变化：4740 行 → 4810 行；存于 `nodes/02.代码映射/artifacts/2026-11-02_03_code-mapping/output/尺寸编码映射-20261102_03.csv`。
- 行级差异：新增 70，删除 0，修改 0。
- 新增示例（最多 10 条）：`Buick Terraza MPV 2005 US`；`Buick Terraza MPV 2006 US`；`Buick Terraza MPV 2007 US`；`Buick Terraza MPV 2008 US`；`Hummer H3 SUV 2006 US`；`Hummer H3 SUV 2007 US`；`Hummer H3 SUV 2008 US`；`Hummer H3 SUV 2009 US`；`Hummer H3 SUV 2010 US`；`Isuzu Ascender SUV 2003 US`。
