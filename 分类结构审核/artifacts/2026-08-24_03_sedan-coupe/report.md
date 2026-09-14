# Sedan / Coupe 同尺寸修复

> 本目录为历史修复的补充归档。`correct.csv` 以上一阶段 year reference/美国市场修复结果为基线；`changes.csv` 只包含本阶段新增的 6 条变化。

## 结果

- 输入累计结果：4,791 行。
- 实际应用：6 条变化。
- 删除误分类重复记录：3 条。
- 年份身份重键：1 条。
- 三维修正：2 条。
- 阶段原始输出：4,788 行。
- 车形核定前唯一性规范化后：4,786 行（见下方补充）。

## 具体处置

- 删除 BMW 3 Series E30 的 Coupe 重复项，保留官方 2-door sedan/saloon 对应的 Sedan 记录。
- 删除 Nissan Sentra B13 的 Coupe 重复项，保留 2-door sedan 对应的 Sedan 记录。
- 删除 Toyota Tercel 1995-1999 Coupe 重复项，并将保留的 Sedan 年份修正为 1995-1998。
- Chevrolet Cobalt Sedan 修正为 `180.3 × 67.9 × 57.1 in`。
- Chevrolet Cobalt SS Coupe 修正为 `180.5 × 67.9 × 55.5 in`。

## 车形核定前补充规范化

在按新版车形规则生成一对一 `DIMENSION-ID,车形` 映射时，发现原阶段输出仍有 6 个重复键和 1 个字段/键不一致项：

- 4 个 Audi Sportback 行补充 `VERSION=Sportback`，与同期普通 SUV 分键，避免同一 ID 同时映射到 Conventional SUV 与 Fastback SUV。
- 删除 Mercedes-Benz S-Class 2010-2013 与 Toyota Land Cruiser 20/40 Series Van/Hardtop 各 1 条冗余同键行。
- Dodge Viper 2008-2010 的字段为 `Roadster`，将旧 `STRUCTURE=Convertible` 键同步改为 `STRUCTURE=Roadster`。

当前 `correct.csv` 为 4,786 行、4,786 个唯一且字段一致的 `DIMENSION-ID`。

## 判断规则

只有同期美国厂商资料明确写作 `Coupe` 或 `Sport Coupe` 才归为 Coupe/跑车；`2-door sedan`、`2-door saloon` 仍属于 Sedan/三厢车。相同三维只作为风险信号，不能单独证明分类错误。

## 文件

- `correct.csv`：完成本阶段后的累计全量结果。
- `changes.csv`：本阶段 6 条实际变化。
- `review.csv`：逐行结论、原因和来源链接。
