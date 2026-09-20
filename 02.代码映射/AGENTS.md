# 代码映射 Agent

负责维护不可变的 MAKE/MODEL 编码，并为每条尺寸记录生成 `DIMENSION-CODE`。位于流水线第 2 层，是 `A0.尺码计算` 的上游之一。

- 上游：`01.整理尺寸库/output/尺寸库.csv`（US/EU/RU 合并库）。
- 交付物（`output/`）：`车型编码映射.csv`（REGION, MAKE, MODEL, MAKE_CODE, MODEL_CODE）、`尺寸编码映射.csv`（DIMENSION-ID, DIMENSION-CODE）。
- 三个区域独立编码，持久映射在 `data/mapping/{us,eu,ru}/`：US 用 2 位码；EU、RU 用 3 位码，DIMENSION-CODE 分别加 `E`、`R` 前缀。
- `DIMENSION-CODE = 前缀 + MAKECODE + MODELCODE + YEARCODE`，YEARCODE 为年份区间两端后两位拼接（`1956-2012` → `5612`，单年 `1994` → `9494`）。
- 编码只追加、不重排、不复用；尺寸库无销量，新增项按标准化名称升序分配。详细规则见 `data/编码规则.md`（其中销量排序仅适用于 US 首次初始化的历史口径）。
- 该码不含结构信息，同车型同年份的不同结构共码；`DIMENSION-ID` 才是唯一主键。运行时报告共码行数。

```powershell
python src/main.py --dry-run
python src/main.py
```

遵守仓库根目录 `AGENTS.md`。
