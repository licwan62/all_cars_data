# 发布报告

- 节点：`code-mapping`（`nodes/02.代码映射`）
- 版本：`20261108_02`
- 发布时间：`2026-11-08T17:02:32+08:00`
- 发布原因：交付物变化：尺寸编码映射.csv；上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261108_02`：运行批次实际读取，1 个文件。

## 身份承接

- `尺寸编码映射.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。

## 交付物与变更

### `车型编码映射.csv`

- 内容未变化；引用 `nodes/02.代码映射/artifacts/2026-11-02_13_code-mapping/output/车型编码映射-20261102_13.csv`，未复制。

### `尺寸编码映射.csv`

- 内容已变化：6335 行 → 6352 行；存于 `nodes/02.代码映射/artifacts/2026-11-08_01_code-mapping/output/尺寸编码映射-20261108_01.csv`。
- 行级差异：新增 20，删除 3，修改 0。
- 新增示例（最多 10 条）：`Ford Ranger Pickup 1998-2000 Regular 6 US`；`Ford Ranger Pickup 1998-2000 Regular 7 US`；`Ford Ranger Pickup 1998-2000 SuperCab 6 US`；`Ford Ranger Pickup 2001-2002 Regular 7 US`；`Ford Ranger Pickup 2001-2002 SuperCab 6 US`；`Ford Ranger Pickup 2001-2003 Regular 6 US`；`Ford Ranger Pickup 2003 Regular 7 US`；`Ford Ranger Pickup 2003 SuperCab 6 US`；`Ford Ranger Pickup 2004 Regular 6 US`；`Ford Ranger Pickup 2004 Regular 7 US`。
- 删除示例（最多 10 条）：`Ford Ranger Pickup 1998-2011 Regular 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 7 US`。
