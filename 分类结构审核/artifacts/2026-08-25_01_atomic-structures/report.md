# 车身结构原子化

本变更包以 `2026-08-24_03_sedan-coupe/correct.csv` 为累计基线，不读取后再回写 `source`，也不修改 `source` 中的任何文件。

## 结果

- 输入：4,786 行。
- 删除旧复合结构压缩行：21 行。
- 输出：4,765 行。
- 输出中含 `/` 的复合结构：0 行。
- 输出 `DIMENSION-ID`：4,765 个，全部唯一。
- 新增或复制尺寸：0 行。

## 处置原则

这些行不能一律机械拆分。复核发现，它们属于以下三类：

1. 同年同代已经存在 Coupe、Convertible 等原子记录，复合行只是重复压缩结果。
2. 原子记录已按更准确的年份区间或结构名称存在，例如 Dodge Viper 的 `Coupe` 与 `Roadster`、Mitsubishi Eclipse 的分代 Coupe/Spyder、Pontiac LeMans 的逐年 Coupe/Convertible。
3. 复合结构列入了当年不存在的车身，例如部分 Porsche 911 Targa、C-Class Convertible；或者把 S-Class PHEV 版本错误附在 Coupe/Convertible 上。此类记录只能删除，不能生成虚构原子行。

因此，本阶段删除全部 21 条旧复合行，并保留现有、尺寸更具体的单结构记录。旧行中的“最大尺寸”没有复制给 Coupe 与 Convertible，避免再次制造跨车身尺寸污染。

## 维护模型

- 普通车与老爷车可由人工分别维护为两个同表头 CSV。
- 使用 `分类结构审核/code/build_maintenance_union.py` 做严格追加，规范结果写到 `artifacts/maintenance_union/`。
- 主表不增加数据源字段；来源保存在 `.provenance.csv` 旁表。
- 不建立代际分区登记表。
- 合并遇到重复 ID、跨文件同身份年份重叠、复合结构或表头差异时直接停止，不采用“后文件覆盖前文件”。

详见 `分类结构审核/doc/维护分源与原子结构.md`。
