# 发布报告

- 节点：`code-mapping`（`nodes/02.代码映射`）
- 版本：`20261102_10`
- 发布时间：`2026-11-02T18:25:24+08:00`
- 发布原因：交付物变化：尺寸编码映射.csv；上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261102_12`：运行批次实际读取，1 个文件。

## 身份承接

- `尺寸编码映射.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。

## 交付物与变更

### `车型编码映射.csv`

- 内容未变化；引用 `nodes/02.代码映射/artifacts/2026-11-02_06_code-mapping/output/车型编码映射-20261102_06.csv`，未复制。

### `尺寸编码映射.csv`

- 内容已变化：4837 行 → 4837 行；存于 `nodes/02.代码映射/artifacts/2026-11-02_09_code-mapping/output/尺寸编码映射-20261102_09.csv`。
- 行级差异：新增 11，删除 11，修改 0。
- 新增示例（最多 10 条）：`BMW X2 SUV 2027 US`；`Ford Transit Connect SWB Van 2014 US`；`Ford Transit Connect SWB Van 2015 US`；`Ford Transit Connect SWB Van 2016 US`；`Ford Transit Connect SWB Van 2017 US`；`Ford Transit Connect SWB Van 2018 US`；`Ford Transit Connect SWB Van 2019 US`；`Ford Transit Connect SWB Van 2020 US`；`Ford Transit Connect SWB Van 2021 US`；`Ford Transit Connect SWB Van 2022 US`。
- 删除示例（最多 10 条）：`BMW X2 Coupe 2027 US`；`Ford Transit Connect Van 2014 US`；`Ford Transit Connect Van 2015 US`；`Ford Transit Connect Van 2016 US`；`Ford Transit Connect Van 2017 US`；`Ford Transit Connect Van 2018 US`；`Ford Transit Connect Van 2019 US`；`Ford Transit Connect Van 2020 US`；`Ford Transit Connect Van 2021 US`；`Ford Transit Connect Van 2022 US`。
