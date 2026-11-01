# 发布报告

- 节点：`code-mapping`（`nodes/02.代码映射`）
- 版本：`20261101_05`
- 发布时间：`2026-11-01T12:36:00+08:00`
- 发布原因：交付物变化：尺寸编码映射.csv、车型编码映射.csv；上游输入变化；规则变化（修改 data/mapping/us/model_mapping.csv；新增 data/mapping/us/backups/20261101_122506_976623_make_mapping.csv, data/mapping/us/backups/20261101_122506_976623_model_mapping.csv）。

## 规则（data/）

- 相对上一版本：修改 data/mapping/us/model_mapping.csv；新增 data/mapping/us/backups/20261101_122506_976623_make_mapping.csv, data/mapping/us/backups/20261101_122506_976623_model_mapping.csv。

## 上游输入依据

- `dimension-library` `20261101_12`：运行批次实际读取，1 个文件。

## 身份承接

- `尺寸编码映射.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。

## 交付物与变更

### `车型编码映射.csv`

- 内容已变化：704 行 → 705 行；存于 `nodes/02.代码映射/artifacts/2026-11-01_03_code-mapping/output/车型编码映射-20261101_03.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺寸编码映射.csv`

- 内容已变化：4383 行 → 4471 行；存于 `nodes/02.代码映射/artifacts/2026-11-01_04_code-mapping/output/尺寸编码映射-20261101_04.csv`。
- 行级差异：新增 88，删除 0，修改 0。
- 新增示例（最多 10 条）：`Acura RL Sedan 2005 US`；`Acura RL Sedan 2006 US`；`Acura RL Sedan 2007 US`；`Acura RL Sedan 2008 US`；`Acura RL Sedan 2009 US`；`Acura RL Sedan 2010 US`；`Acura RL Sedan 2011 US`；`Acura RL Sedan 2012 US`；`Audi 90 Sedan 1990 US`；`Audi 90 Sedan 1993 US`。
