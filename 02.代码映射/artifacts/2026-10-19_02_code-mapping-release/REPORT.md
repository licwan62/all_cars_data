# 发布报告

- 节点：`code-mapping`（`02.代码映射`）
- 版本：`20261019_02`
- 发布时间：`2026-10-19T02:04:36+08:00`
- 发布原因：交付物变化：尺寸编码映射.csv。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261009_08`：发布时上游版本（未经运行记录核实），7 个文件。
- 无运行记录可核实的交付物：`车型编码映射.csv`、`尺寸编码映射.csv`。

## 身份承接

- `尺寸编码映射.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。

## 交付物与变更

### `车型编码映射.csv`

- 内容未变化；引用 `02.代码映射/artifacts/2026-10-09_04_code-mapping-release/output/车型编码映射-20261009_04.csv`，未复制。

### `尺寸编码映射.csv`

- 内容已变化：4378 行 → 4383 行；存于 `02.代码映射/artifacts/2026-10-19_02_code-mapping-release/output/尺寸编码映射-20261019_02.csv`。
- 行级差异：新增 9，删除 4，修改 0。
- 新增示例（最多 10 条）：`Chevrolet Cavalier Coupe 1984-1985 US`；`Chevrolet Cavalier Sedan 1984-1985 US`；`Chevrolet Chevelle Convertible 1966-1967 US`；`Chevrolet Chevelle Coupe 1969-1970 US`；`Chevrolet Chevelle Coupe 1972 US`；`Chevrolet Chevelle Wagon 1965-1967 US`；`Chevrolet Nova Coupe 1975 US`；`Ford Mustang Coupe 1970 US`；`MINI Countryman JCW SUV 2018 US`。
- 删除示例（最多 10 条）：`Chevrolet Cavalier Coupe 1985 US`；`Chevrolet Cavalier Sedan 1984 US`；`Chevrolet Chevelle Convertible 1966 US`；`Chevrolet Chevelle Wagon 1967 US`。
