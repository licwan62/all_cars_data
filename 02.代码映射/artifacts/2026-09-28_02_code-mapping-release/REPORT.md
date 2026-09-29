# 发布报告

- 节点：`code-mapping`（`02.代码映射`）
- 版本：`20260928_02`
- 发布时间：`2026-09-28T09:25:17+08:00`
- 工作描述：code-mapping 输出刷新。

## 规则（data/）

- 相对上一版本：修改 data/config.yaml。

## 交付物与变更

### `车型编码映射.csv`

- 内容已变化：8846 行 → 704 行。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺寸编码映射.csv`

- 内容已变化：47355 行 → 4377 行。
- 行级差异：新增 0，删除 42978，修改 0。
- 删除示例（最多 10 条）：`212 Explorer 01 Pickup 2026-2026 Double RU`；`212 T01 SUV 2024-2026 RU`；`212 T10 SUV 2026-2026 RU`；`AC 378 GT Zagato Coupe 2012-2012 RU`；`AC 428 Convertible 1965-1974 EU`；`AC Ace Convertible 1995-1998 EU`；`AC Ace Convertible 1998-2026 EU`；`AC Ace Roadster 1992-2000 RU`；`AC Aceca Coupe 1993-1997 EU`；`AC Aceca Coupe 1998-2000 RU`。
